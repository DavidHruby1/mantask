from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.task import Task
from backend.app.models.enums import TaskStatus
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


def get_all_team_tasks(db: Session, team_id: int) -> list[Task]:
    return list(db.scalars(select(Task).where(Task.team_id == team_id)).all())


def get_all_team_tasks_by_status(db: Session, team_id: int, status: TaskStatus) -> list[Task]:
    return list(db.scalars(
        select(Task)
        .where(Task.team_id == team_id)
        .where(Task.status == status)
    ).all())


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


def update_task(task: Task, updates: dict[str, object]) -> Task:
    for field, value in updates.items():
        setattr(task, field, value)

    return task
