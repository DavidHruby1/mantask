from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.task import Task
from backend.app.models.enums import TaskStatus
from backend.app.models.app_config import AppConfig
from backend.app.schemas.task import TaskFilters, TaskCreate


def find_tasks(db: Session, filters: TaskFilters) -> list[Task]:
    stmt = select(Task).where(Task.team_id == filters.team_id)

    if filters.statuses is not None:
        stmt = stmt.where(Task.status.in_(filters.statuses))
    if filters.assignee_member_id is not None:
        stmt = stmt.where(Task.assignee_member_id == filters.assignee_member_id)

    stmt = stmt.order_by(Task.status, Task.position, Task.id)
    return list(db.scalars(stmt).all())


def get_task_by_id(db: Session, task_id: int) -> Task | None:
    return db.get(Task, task_id)


def get_last_task_position(db: Session, filters: TaskFilters) -> int | None:
    statuses = filters.statuses if filters.statuses is not None else [TaskStatus.TODO]
    stmt = (
        select(Task)
        .where(Task.team_id == filters.team_id)
        .where(Task.status.in_(statuses))
        .order_by(Task.position.desc())
        .limit(1)
    )
    task = db.scalar(stmt)
    return task.position if task is not None else None


def is_in_progress_free(db: Session, team_id: int) -> bool:
    stmt = select(Task).where(Task.team_id == team_id).where(Task.status == TaskStatus.IN_PROGRESS)
    in_progress_tasks = len(list(db.scalars(stmt).all()))

    app_config = db.get(AppConfig, 1)
    in_progress_limit = app_config.in_progress_limit if app_config is not None else None

    if in_progress_limit is None:
        return True

    return in_progress_tasks < in_progress_limit


def insert_task(
    db: Session,
    team_id: int,
    creator_member_id: int,
    payload: TaskCreate,
    position: int,
    started_working_at: datetime | None
) -> Task:
    task = Task(
        **payload.model_dump(),
        team_id=team_id,
        creator_member_id=creator_member_id,
        position=position,
        started_working_at=started_working_at
    )

    db.add(task)
    return task
