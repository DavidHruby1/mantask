from datetime import datetime, timezone

from sqlalchemy.orm import Session

from backend.app.models.user_session import UserSession

from backend.app.repositories.bootstraps import get_in_progress_limit
from backend.app.repositories.teams import (
    get_team_by_id,
    get_team_member_by_id,
    is_team_member,
    get_team_member
)
from backend.app.repositories.tasks import (
    find_tasks,
    get_task_by_id,
    count_team_tasks_by_status,
    insert_task,
    get_last_task_position,
    update_task as update_task_repository,
    lock_task_positions,
    get_destination_neighbors,
    rebalance_task_column,
)
from backend.app.schemas.task import TaskFilters, TaskQuery, TaskCreate, TaskUpdate, TaskMove
from backend.app.models.task import Task
from backend.app.models.enums import TaskStatus

from backend.app.error import (
    ApiInternalServerError,
    ApiConflictError,
    InvalidTaskError,
    NoActiveTeamSelectedError,
    TeamInactiveError,
    TeamNotFoundError,
    TeamMembershipError,
    TaskNotFoundError,
    TaskAccessDeniedError
)

# Keep sparse ordering arithmetic within PostgreSQL's persisted INTEGER range.
TASK_POSITION_GAP = 1000
MAX_TASK_POSITION = 2_147_483_647


class TaskService:
    def get_all_tasks(
        self,
        db: Session,
        session: UserSession,
        query: TaskQuery
    ) -> list[Task]:
        filters = self._resolve_task_filters(db, session, query)
        return find_tasks(db, filters)

    def create_task(
        self,
        db: Session,
        active_team_id: int, 
        user_id: int,
        payload: TaskCreate
    ) -> Task:
        """Validate task membership, then serialize capacity and sparse append allocation.

        The team lock is acquired only after member checks and remains owned by the
        endpoint's transaction through commit or rollback.
        """
        # Ensure the creator is a member of the active team.
        creator_member = get_team_member(db, active_team_id, user_id)    
        if creator_member is None:
            raise TeamMembershipError()
        creator_member_id = creator_member.id

        if payload.assignee_member_id is None:
            payload = payload.model_copy(
                update={"assignee_member_id": creator_member_id}
            )
        else:
            assignee_member = get_team_member_by_id(db, active_team_id, payload.assignee_member_id)
            if assignee_member is None:
                raise TeamMembershipError("Invalid assignee")

        if payload.reviewer_member_id is not None:
            reviewer_member = get_team_member_by_id(db, active_team_id, payload.reviewer_member_id)
            if reviewer_member is None:
                raise TeamMembershipError("Invalid reviewer")

        # Capacity and append-position reads must observe one serialized team state.
        lock_task_positions(db, active_team_id)
        if payload.status == TaskStatus.IN_PROGRESS:
            if not self._can_create_in_progress_task(db, active_team_id):
                raise ApiConflictError("IN_PROGRESS limit reached")

        filters = TaskFilters(
            team_id=active_team_id, 
            statuses=[payload.status],
            assignee_member_id=None
        )

        last_task_position = get_last_task_position(db, filters)
        position = TASK_POSITION_GAP
        if last_task_position is not None:
            if last_task_position > MAX_TASK_POSITION - TASK_POSITION_GAP:
                raise ApiConflictError("No position is available in the destination column")
            position = last_task_position + TASK_POSITION_GAP

        started_working_at = None
        if payload.status == TaskStatus.IN_PROGRESS:
            started_working_at = datetime.now(tz=timezone.utc)

        return insert_task(
            db,
            active_team_id, 
            creator_member_id, 
            payload, 
            position, 
            started_working_at
        )

    def update_task(
        self,
        db: Session,
        task: Task,
        payload: TaskUpdate
    ) -> Task:
        """Validate and stage editable task fields while preserving review consistency.

        Resulting reviewer membership and ``should_review`` must agree, and a task
        already in REVIEW cannot be changed into a non-reviewable state.
        """
        updates = payload.model_dump(exclude_unset=True)

        if "assignee_member_id" in updates:
            assignee_member_id = updates["assignee_member_id"]
            if assignee_member_id is not None:
                assignee_member = get_team_member_by_id(db, task.team_id, assignee_member_id)
                if assignee_member is None:
                    raise InvalidTaskError("Invalid assignee_member_id")

        if "reviewer_member_id" in updates:
            reviewer_member_id = updates["reviewer_member_id"]
            if reviewer_member_id is not None:
                reviewer_member = get_team_member_by_id(db, task.team_id, reviewer_member_id)
                if reviewer_member is None:
                    raise InvalidTaskError("Invalid reviewer_member_id")
        else:
            reviewer_member_id = task.reviewer_member_id

        # Validates the business rule that you can't have should_review True if no reviewer is assigned and vice-versa
        should_review = updates.get("should_review", task.should_review)
        review_date = updates.get("review_date", task.review_date)
        if not should_review and review_date is not None:
            raise ApiConflictError("Task with no review cannot have a review date")
        if task.status == TaskStatus.REVIEW and not should_review:
            raise ApiConflictError("A task in REVIEW must remain reviewable")
        if should_review and reviewer_member_id is None:
            raise ApiConflictError("Can't review task with no reviewer")
        if not should_review and reviewer_member_id is not None:
            raise ApiConflictError("Can't assign reviewer to task that shouldn't be reviewed")

        return update_task_repository(task, updates)

    def get_accessible_task(self, db: Session, task_id: int, user_id: int) -> Task:
        task = get_task_by_id(db, task_id)                  
        if not task:
            raise TaskNotFoundError()

        team_id = task.team_id
        if not is_team_member(db, team_id, user_id):
            raise TeamMembershipError()

        team = get_team_by_id(db, team_id)
        if team is None:
            raise TeamNotFoundError()
        if not team.is_active:
            raise TeamInactiveError()

        return task 

    def _resolve_task_filters(
        self,
        db: Session,
        session: UserSession,
        query: TaskQuery,
    ) -> TaskFilters:
        team_id = query.team_id
        user_id = session.user_id

        if team_id is None:
            if not session.user.last_active_team_id:
                raise NoActiveTeamSelectedError()
            team_id = session.user.last_active_team_id

        team = get_team_by_id(db, team_id)
        if (
            team is None or
            not team.is_active or
            not is_team_member(db, team_id, user_id)
        ):
            raise TaskAccessDeniedError()

        assignee_member_id = query.assignee_member_id
        if assignee_member_id is not None:
            assignee_member = get_team_member_by_id(db, team_id, assignee_member_id)
            if assignee_member is None:
                raise InvalidTaskError("Invalid assignee_member_id")

        return TaskFilters(
            team_id=team_id,
            statuses=query.statuses,
            assignee_member_id=query.assignee_member_id,
        )

    def _can_create_in_progress_task(self, db: Session, team_id: int) -> bool:
        """Apply the configured count-based capacity rule shared by creation and movement."""
        team = get_team_by_id(db, team_id)
        if not team:
            raise TeamNotFoundError()
        if not team.is_active:
            raise TeamInactiveError()

        in_progress_limit: int | None = get_in_progress_limit(db)
        if in_progress_limit is None:
            raise ApiInternalServerError("App configuration is missing")

        status = TaskStatus.IN_PROGRESS
        in_progress_tasks_count: int = count_team_tasks_by_status(db, team_id, status)

        return in_progress_tasks_count < in_progress_limit

    def _validate_move(self, db: Session, task: Task, target_status: TaskStatus) -> None:
        """Reject a status change that violates the board's workflow policy.

        Enum declaration order defines the workflow: BACKLOG -> TODO -> IN_PROGRESS
        -> REVIEW -> DONE. A forward move may advance exactly one stage; tasks with
        ``should_review=False`` skip REVIEW and may advance directly from IN_PROGRESS
        to DONE. A task that does require review cannot skip REVIEW, and a task that
        does not require review cannot enter it. Backward moves may cross any number
        of stages.

        Entering IN_PROGRESS from another status is also rejected when the team's
        configured count limit is full. Reordering within IN_PROGRESS does not consume
        capacity and therefore does not run that check.
        """
        statuses = list(TaskStatus)
        source_index = statuses.index(task.status)
        target_index = statuses.index(target_status)

        if target_status == TaskStatus.REVIEW and not task.should_review:
            raise InvalidTaskError("A task without review cannot enter REVIEW")

        if target_index > source_index:
            next_index = source_index + 1
            # For work that does not require review, DONE is the next applicable stage.
            if task.status == TaskStatus.IN_PROGRESS and not task.should_review:
                next_index = statuses.index(TaskStatus.DONE)
            if target_index != next_index:
                raise InvalidTaskError("Task can only move one workflow step forward")

        if (
            target_status == TaskStatus.IN_PROGRESS
            and task.status != TaskStatus.IN_PROGRESS
            and not self._can_create_in_progress_task(db, task.team_id)
        ):
            raise ApiConflictError("IN_PROGRESS limit reached")

    def _movement_lifecycle_updates(
        self,
        task: Task,
        target_status: TaskStatus,
        moved_at: datetime,
    ) -> dict[str, object]:
        """Derive lifecycle timestamps and backward-event counters from one move instant.

        Each re-entry into active work or review records the supplied move instant.
        Later-stage timestamps are retained only where the destination still permits them.
        """
        updates: dict[str, object] = {
            "started_working_at": None,
            "submitted_for_review_at": None,
            "completed_at": None,
            "returned_count": task.returned_count,
            "reopened_count": task.reopened_count,
        }
        if target_status == TaskStatus.IN_PROGRESS:
            updates["started_working_at"] = moved_at
        elif target_status == TaskStatus.REVIEW:
            updates["started_working_at"] = task.started_working_at
            updates["submitted_for_review_at"] = moved_at
        elif target_status == TaskStatus.DONE:
            updates["started_working_at"] = task.started_working_at
            if task.should_review:
                updates["submitted_for_review_at"] = task.submitted_for_review_at
            updates["completed_at"] = moved_at

        statuses = list(TaskStatus)
        moving_backward = statuses.index(target_status) < statuses.index(task.status)
        if moving_backward and task.status == TaskStatus.REVIEW:
            updates["returned_count"] = task.returned_count + 1
        if moving_backward and task.status == TaskStatus.DONE:
            updates["reopened_count"] = task.reopened_count + 1
        return updates

    def _calculate_move_position(
        self,
        anchor: Task | None,
        successor: Task | None,
    ) -> int | None:
        """Allocate a positive distinct sparse position, or signal exhausted integer space."""
        if anchor is None and successor is None:
            return TASK_POSITION_GAP
        if anchor is None:
            position = successor.position // 2  # type: ignore[union-attr]
            return position if 0 < position < successor.position else None  # type: ignore[union-attr]
        if successor is None:
            if anchor.position > MAX_TASK_POSITION - TASK_POSITION_GAP:
                return None
            return anchor.position + TASK_POSITION_GAP

        position = (anchor.position + successor.position) // 2
        if position <= anchor.position or position >= successor.position:
            return None
        return position

    def move_task(self, db: Session, task: Task, payload: TaskMove) -> Task:
        """Coordinate one policy-complete move while leaving transaction completion to the endpoint.

        A team advisory lock and post-lock refresh make every decision use serialized,
        current state. Anchor validation, idempotence, sparse allocation, optional
        destination rebalance, lifecycle state, and counters are then resolved before
        one generic task update is staged.
        """
        lock_task_positions(db, task.team_id)
        db.refresh(task)

        # Anchoring a task to itself describes no change, so return before validating
        # transitions or capacity; retries of an already-applied request remain harmless.
        if payload.anchor_task_id == task.id:
            return task

        self._validate_move(db, task, payload.target_status)
        anchor, successor = get_destination_neighbors(
            db, task.team_id, payload.target_status, payload.anchor_task_id, task.id
        )
        if payload.anchor_task_id is not None and anchor is None:
            raise InvalidTaskError("Anchor is invalid or stale")

        # Dropping a task back onto its current place in the same column is a no-op.
        # The task is already there when it remains ordered between the requested
        # anchor and successor, which were resolved without the task itself.
        if task.status == payload.target_status:
            task_key = (task.position, task.id)
            is_already_at_destination = (
                (anchor is None or (anchor.position, anchor.id) < task_key)
                and (successor is None or task_key < (successor.position, successor.id))
            )
            if is_already_at_destination:
                return task

        position = self._calculate_move_position(anchor, successor)
        if position is None:
            # The neighboring positions are consecutive (or at the integer limit), so
            # no valid sparse position can be assigned. Renumber only the destination
            # column to restore gaps, then resolve the requested insertion point again
            # from the exact ordered list that was renumbered.
            rebalanced_tasks = rebalance_task_column(
                db, task.team_id, payload.target_status, task.id, TASK_POSITION_GAP
            )

            if payload.anchor_task_id is None:
                # No anchor means "place the moved task first". The first remaining
                # task therefore becomes its successor after the rebalance.
                anchor = None
                successor = rebalanced_tasks[0] if rebalanced_tasks else None
            else:
                # The request says "place the moved task after anchor_task_id".
                # Find that task in the rebalanced list so the next item can be
                # used as the moved task's successor.
                anchor_index = None
                for index, candidate in enumerate(rebalanced_tasks):
                    if candidate.id == payload.anchor_task_id:
                        anchor_index = index
                        break

                # Deletion does not use the task-position lock, so the anchor may
                # have disappeared after the earlier validation.
                if anchor_index is None:
                    raise InvalidTaskError("Anchor is invalid or stale")

                anchor = rebalanced_tasks[anchor_index]
                successor_index = anchor_index + 1
                successor = (
                    rebalanced_tasks[successor_index]
                    if successor_index < len(rebalanced_tasks)
                    else None
                )

            # Recalculate between the newly spaced neighbors. Failure now means the
            # destination column cannot fit another positive PostgreSQL INTEGER.
            position = self._calculate_move_position(anchor, successor)
            if position is None:
                raise ApiConflictError("No position is available in the destination column")

        # A same-column reorder changes only position. Timestamps and counters describe
        # workflow transitions, so changing them here would invent a lifecycle event.
        if task.status == payload.target_status:
            return update_task_repository(task, {"position": position})

        updates = self._movement_lifecycle_updates(
            task, payload.target_status, datetime.now(tz=timezone.utc)
        )
        updates.update(status=payload.target_status, position=position)
        return update_task_repository(task, updates)


task_service = TaskService()
