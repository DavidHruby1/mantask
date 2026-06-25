from typing import Annotated

from fastapi import APIRouter, Query
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from backend.app.api.dependencies import DbSessionDep, CurrentSessionDep
from backend.app.error import (
    ApiConflictError,
    ApiInternalServerError,
    InvalidTaskError,
    NoActiveTeamSelectedError,
    TaskAccessDeniedError,
    TaskNotFoundError,
    TeamMembershipError,
)
from backend.app.repositories.teams import get_last_active_team_id, get_team_member
from backend.app.schemas.task import TaskQuery, TaskRead, TaskCreate, TaskUpdate
from backend.app.models.enums import TaskStatus
from backend.app.repositories.tasks import find_tasks, get_task_by_id, is_in_progress_free
from backend.app.services.tasks import (
    resolve_task_filters,
    can_view_task,
    create_task,
    update_task,
)


router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/", response_model=list[TaskRead])
def get_tasks(
    db: DbSessionDep,
    session: CurrentSessionDep,
    query: Annotated[TaskQuery, Query()],
) -> list[TaskRead]:
    filters = resolve_task_filters(db, session, query)
    tasks = find_tasks(db, filters)
    return [TaskRead.model_validate(task) for task in tasks]


@router.get("/{task_id}", response_model=TaskRead)
def get_task(
    db: DbSessionDep,
    session: CurrentSessionDep,
    task_id: int,
) -> TaskRead:
    task = get_task_by_id(db, task_id)
    if task is None:
        raise TaskNotFoundError()

    task_team_id = task.team_id
    if not can_view_task(db, task_team_id, session.user_id):
        raise TaskAccessDeniedError()

    return TaskRead.model_validate(task)


@router.post("/", response_model=TaskRead)
def post_task(
    db: DbSessionDep,
    session: CurrentSessionDep,
    payload: TaskCreate
) -> TaskRead:
    # TODO: Task doesn't have to have assignee, it can be picked up by anyone if nobody is assigned
    # TODO: Should I prevent duplicate titles of tasks?
    user = session.user
    active_team_id = get_last_active_team_id(db, user)
    if active_team_id is None:
        raise NoActiveTeamSelectedError()

    team_member = get_team_member(db, active_team_id, user.id)    
    if team_member is None:
        raise TeamMembershipError()

    if payload.status == TaskStatus.IN_PROGRESS and not is_in_progress_free(db, active_team_id):
        raise ApiConflictError("IN_PROGRESS limit reached")

    created_task = create_task(db, active_team_id, team_member.id, payload)
    if not created_task:
        raise InvalidTaskError()

    try: 
        db.commit()
        db.refresh(created_task)
    except IntegrityError:
        db.rollback()
        raise ApiConflictError("Bootstrap data conflicts with existing records")

    return TaskRead.model_validate(created_task)


@router.patch("/{task_id}", response_model=TaskRead)
def patch_task(
    db: DbSessionDep,
    session: CurrentSessionDep,
    task_id: int,
    payload: TaskUpdate
) -> TaskRead:
# TODO: store in database
# TODO: later add also role based access control
    task = get_task_by_id(db, task_id)
    if task is None:
        raise TaskNotFoundError()

    task_team_id = task.team_id
    if not can_view_task(db, task_team_id, session.user_id):
        raise TaskAccessDeniedError()

    updated_task = update_task(db, task, payload)
    if not updated_task:
        raise InvalidTaskError()

    try: 
        db.commit()
        db.refresh(updated_task)
    except IntegrityError:
        db.rollback()
        raise ApiConflictError("Task update conflicts with existing records")

    return TaskRead.model_validate(updated_task)


@router.delete("/{task_id}", status_code=204)
def delete_task(
    db: DbSessionDep,
    session: CurrentSessionDep,
    task_id: int,
) -> None:
    task = get_task_by_id(db, task_id)
    if task is None:
        raise TaskNotFoundError()

    task_team_id = task.team_id
    if not can_view_task(db, task_team_id, session.user_id):
        raise TaskAccessDeniedError()

    db.delete(task)
    try: 
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ApiConflictError("Task cannot be deleted because it is still referenced by other records")
    except SQLAlchemyError:
        db.rollback()
        raise ApiInternalServerError("Unable to delete task right now. Please try again.")
