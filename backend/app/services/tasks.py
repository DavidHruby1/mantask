from datetime import datetime, timezone

from sqlalchemy.orm import Session

from backend.app.models.user_session import UserSession
from backend.app.error import (
    InvalidTaskError,
    NoActiveTeamSelectedError,
    TeamInactiveError,
    TeamNotFoundError,
    TeamMembershipError
)
from backend.app.repositories.teams import (
    get_team_by_id,
    get_team_member_by_id,
    is_team_member,
)
from backend.app.repositories.tasks import (
    get_task_by_id,
    insert_task,
    get_last_task_position,
    update_task as update_task_repository,
)
from backend.app.schemas.task import TaskFilters, TaskQuery, TaskCreate, TaskUpdate
from backend.app.models.task import Task
from backend.app.models.enums import TaskStatus

from backend.app.error import TaskNotFoundError, TaskAccessDeniedError


# What is better? To check if not is, or to check if is None?
class TaskService:
    '''
    def _has_task_access(self, db: Session, team_id: int, user_id: int) -> bool:
        if not is_team_member(db, team_id, user_id):
            return False

        team = get_team_by_id(db, team_id)
        if team is None or not team.is_active:
            return False

        return True
    '''
    def create_task(
        self,
        db: Session,
        team_id: int, 
        creator_member_id: int, 
        payload: TaskCreate
    ) -> Task | None:
        if get_team_member_by_id(db, team_id, creator_member_id) is None:
            return None

        if payload.assignee_member_id is not None:
            assignee_member = get_team_member_by_id(db, team_id, payload.assignee_member_id)
            if assignee_member is None:
                return None

        if payload.reviewer_member_id is not None:
            reviewer_member = get_team_member_by_id(db, team_id, payload.reviewer_member_id)
            if reviewer_member is None:
                return None

        filters = TaskFilters(
            team_id=team_id, 
            statuses=[payload.status],
            assignee_member_id=None
        )

        last_task_position = get_last_task_position(db, filters)

        if last_task_position is None:
            position = 1
        else:
            position = last_task_position + 1

        started_working_at = None
        if payload.status == TaskStatus.IN_PROGRESS:
            started_working_at = datetime.now(tz=timezone.utc)

        task = insert_task(
            db,
            team_id, 
            creator_member_id, 
            payload, 
            position, 
            started_working_at
        )
        return task

    def update_task(
        self,
        db: Session,
        task: Task,
        payload: TaskUpdate
    ) -> Task | None:
        updates = payload.model_dump(exclude_unset=True)

        assignee_member_id = updates.get("assignee_member_id")
        if assignee_member_id is not None:
            assignee_member = get_team_member_by_id(db, task.team_id, assignee_member_id)
            if assignee_member is None:
                return None

        reviewer_member_id = updates.get("reviewer_member_id", task.reviewer_member_id)
        if reviewer_member_id is not None:
            reviewer_member = get_team_member_by_id(db, task.team_id, reviewer_member_id)
            if reviewer_member is None:
                return None

        should_review = updates.get("should_review", task.should_review)
        if should_review is None:
            return None

        if should_review and reviewer_member_id is None:
            return None
        if not should_review and reviewer_member_id is not None:
            return None

        return update_task_repository(task, updates)

    def resolve_task_filters(
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
