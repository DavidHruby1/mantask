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
)
from backend.app.schemas.task import TaskFilters, TaskQuery, TaskCreate, TaskUpdate
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
        if payload.status == TaskStatus.IN_PROGRESS:
            can_create_in_progress_task = self._can_create_in_progress_task(db, active_team_id)
            if not can_create_in_progress_task:
                raise ApiConflictError("IN_PROGRESS limit reached")

        # Ensure the creator is a member of the active team.
        creator_member = get_team_member(db, active_team_id, user_id)    
        if creator_member is None:
            raise TeamMembershipError()
        creator_member_id = creator_member.id

        if payload.assignee_member_id is not None:
            assignee_member = get_team_member_by_id(db, active_team_id, payload.assignee_member_id)
            if assignee_member is None:
                raise TeamMembershipError("Invalid assignee")

        if payload.reviewer_member_id is not None:
            reviewer_member = get_team_member_by_id(db, active_team_id, payload.reviewer_member_id)
            if reviewer_member is None:
                raise TeamMembershipError("Invalid reviewer")

        filters = TaskFilters(
            team_id=active_team_id, 
            statuses=[payload.status],
            assignee_member_id=None
        )

        last_task_position = get_last_task_position(db, filters)
        position = 1
        if last_task_position is not None:
            position = last_task_position + 1

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


task_service = TaskService()
