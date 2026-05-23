from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.task import Task
from backend.app.schemas.task import TaskFilters


def find_tasks(db: Session, filters: TaskFilters) -> list[Task]:
    stmt = select(Task).where(Task.team_id == filters.team_id)

    if filters.statuses:
        stmt = stmt.where(Task.status.in_(filters.statuses))
    if filters.assignee_member_id is not None:
        stmt = stmt.where(Task.assignee_member_id == filters.assignee_member_id)

    stmt = stmt.order_by(Task.status, Task.position, Task.id)
    return list(db.scalars(stmt).all())
