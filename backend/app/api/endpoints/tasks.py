from typing import Annotated

from fastapi import APIRouter, Query
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from backend.app.api.dependencies import DbSessionDep, CurrentSessionDep
from backend.app.error import (
    ApiConflictError,
    ApiInternalServerError,
)
from backend.app.schemas.task import TaskQuery, TaskRead, TaskCreate, TaskUpdate, TaskMove
from backend.app.services.auth import get_last_active_team_id
from backend.app.services.tasks import task_service


router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/", response_model=list[TaskRead])
def get_tasks(
    db: DbSessionDep,
    session: CurrentSessionDep,
    query: Annotated[TaskQuery, Query()],
) -> list[TaskRead]:
    tasks = task_service.get_all_tasks(db, session, query)
    return [TaskRead.model_validate(task) for task in tasks]


@router.get("/{task_id}", response_model=TaskRead)
def get_task(
    db: DbSessionDep,
    session: CurrentSessionDep,
    task_id: int,
) -> TaskRead:
    user_id = session.user_id
    task = task_service.get_accessible_task(db, task_id, user_id)    
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
    user_id = user.id

    active_team_id = get_last_active_team_id(db, user)
    created_task = task_service.create_task(db, active_team_id, user_id, payload)

    try: 
        db.commit()
        db.refresh(created_task)
    except IntegrityError:
        db.rollback()
        raise ApiConflictError("Task creation conflicts with current board state")

    return TaskRead.model_validate(created_task)


@router.patch("/{task_id}", response_model=TaskRead)
def patch_task(
    db: DbSessionDep,
    session: CurrentSessionDep,
    task_id: int,
    payload: TaskUpdate
) -> TaskRead:
    # TODO: Store in database
    # TODO: Later add also role based access control
    user_id = session.user_id

    task = task_service.get_accessible_task(db, task_id, user_id)
    updated_task = task_service.update_task(db, task, payload)

    try: 
        db.commit()
        db.refresh(updated_task)
    except IntegrityError:
        db.rollback()
        raise ApiConflictError("Task update conflicts with existing records")

    return TaskRead.model_validate(updated_task)


@router.patch("/{task_id}/move", response_model=TaskRead, status_code=200)
def move_task(
    db: DbSessionDep,
    session: CurrentSessionDep,
    task_id: int,
    payload: TaskMove,
) -> TaskRead:
    """Move an accessible task and commit all board and lifecycle effects atomically."""
    task = task_service.get_accessible_task(db, task_id, session.user_id)
    try:
        moved_task = task_service.move_task(db, task, payload)
        db.commit()
        db.refresh(moved_task)
    except IntegrityError:
        db.rollback()
        raise ApiConflictError("Task movement conflicts with current board state")
    except SQLAlchemyError:
        db.rollback()
        raise ApiInternalServerError("Unable to move task right now. Please try again.")

    return TaskRead.model_validate(moved_task)


@router.delete("/{task_id}", status_code=204)
def delete_task(
    db: DbSessionDep,
    session: CurrentSessionDep,
    task_id: int,
) -> None:
    user_id = session.user_id
    task = task_service.get_accessible_task(db, task_id, user_id)

    db.delete(task)
    try: 
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ApiConflictError("Task cannot be deleted because it is still referenced by other records")
    except SQLAlchemyError:
        db.rollback()
        raise ApiInternalServerError("Unable to delete task right now. Please try again.")
