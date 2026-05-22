from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.task import Task
from backend.app.models.enums import TaskStatus


def find_tasks(
    db: Session,
    team_id: int,
    statuses: list[TaskStatus] | None = None,
    assignee_member_id: int | None = None,
) -> list[Task]:
    stmt = select(Task).where(Task.team_id == team_id)

    if statuses:
        stmt = stmt.where(Task.status.in_(statuses))
    if assignee_member_id is not None:
        stmt = stmt.where(Task.assignee_member_id == assignee_member_id)

    stmt = stmt.order_by(Task.status, Task.position, Task.id)
    return list(db.scalars(stmt).all())
