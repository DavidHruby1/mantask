from datetime import datetime

from sqlalchemy import select, func, text
from sqlalchemy.orm import Session

from backend.app.models.task import Task
from backend.app.models.enums import TaskStatus
from backend.app.schemas.task import TaskFilters, TaskCreate


# Serialize task position and IN_PROGRESS capacity decisions per team without
# coupling unrelated teams. Both values fit PostgreSQL's two-integer lock key.
TASK_POSITIONS_LOCK_NAMESPACE = 1_298_695_507


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


def lock_task_positions(db: Session, team_id: int) -> None:
    """Serialize one team's position allocation and IN_PROGRESS capacity checks.

    The PostgreSQL advisory lock belongs to the current transaction, so this
    repository operation never commits and endpoint commit/rollback releases it.
    The module-owned namespace keeps this lock independent from other advisory
    lock uses while allowing create and move to coordinate on the same team key.
    """
    db.execute(
        text(
            "SELECT pg_advisory_xact_lock("
            "CAST(:namespace AS INTEGER), CAST(:team_id AS INTEGER))"
        ),
        {"namespace": TASK_POSITIONS_LOCK_NAMESPACE, "team_id": team_id},
    )


def get_destination_neighbors(
    db: Session,
    team_id: int,
    target_status: TaskStatus,
    anchor_task_id: int | None,
    moved_task_id: int,
) -> tuple[Task | None, Task | None]:
    """Return the tasks immediately before and after the requested insertion point.

    ``anchor_task_id`` means "place the moved task directly after this task". The
    returned pair is therefore ``(anchor, anchor's successor)``. With no anchor,
    the request means "place the task first", so the pair is ``(None, first_task)``.

    Both lookups are restricted to the destination team and status and exclude the
    task being moved. If a supplied anchor is missing, belongs to another team or
    status, or is the moved task itself, ``(None, None)`` tells the service to reject
    it as invalid or stale. An empty destination also returns ``(None, None)``, but
    only when no anchor was supplied, which the service can distinguish from input.
    """
    scope = (
        Task.team_id == team_id,
        Task.status == target_status,
        Task.id != moved_task_id,
    )
    if anchor_task_id is None:
        first = db.scalar(select(Task).where(*scope).order_by(Task.position, Task.id).limit(1))
        return None, first

    anchor = db.scalar(
        select(Task).where(*scope, Task.id == anchor_task_id).limit(1)
    )
    if anchor is None:
        return None, None

    successor = db.scalar(
        select(Task)
        .where(
            *scope,
            (Task.position > anchor.position)
            | ((Task.position == anchor.position) & (Task.id > anchor.id)),
        )
        .order_by(Task.position, Task.id)
        .limit(1)
    )
    return anchor, successor


def rebalance_task_column(
    db: Session,
    team_id: int,
    status: TaskStatus,
    moved_task_id: int,
    position_gap: int,
) -> list[Task]:
    """Create fresh position gaps in one destination column when insertion space runs out.

    The moved task is excluded because the caller assigns its final position after
    this function returns. Every other task in the destination team/status keeps its
    current ``(position, id)`` order and is renumbered to ``position_gap``,
    ``2 * position_gap``, and so on. The returned list is that same stable order, so
    the caller can find the requested anchor and calculate the new insertion point.

    Renumbering can temporarily reuse positions still held by rows later in the
    update, so this function defers only ``uq_task_team_status_position`` until the
    transaction ends. It only stages ORM changes: the endpoint-owned transaction
    must commit them or roll them back together with the move.
    """
    db.execute(text("SET CONSTRAINTS uq_task_team_status_position DEFERRED"))
    tasks = list(
        db.scalars(
            select(Task)
            .where(
                Task.team_id == team_id,
                Task.status == status,
                Task.id != moved_task_id,
            )
            .order_by(Task.position, Task.id)
        ).all()
    )
    for index, task in enumerate(tasks, start=1):
        task.position = index * position_gap
    return tasks


def count_team_tasks_by_status(db: Session, team_id: int, status: TaskStatus) -> int:
    stmt = (
        select(func.count())
        .select_from(Task)
        .where(Task.team_id == team_id)
        .where(Task.status == status)
    )
    return db.scalar(stmt) or 0


def get_last_task_position(db: Session, filters: TaskFilters) -> int | None:
    """Return the append boundary for the requested team/status scope."""
    statuses = filters.statuses if filters.statuses is not None else [TaskStatus.BACKLOG]
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
