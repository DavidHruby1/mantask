"""PostgreSQL integration coverage for serialized task placement and constraints."""

from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from threading import Barrier, Event
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool

from backend.app.core.config import settings
from backend.app.error import ApiConflictError
from backend.app.models.app_config import AppConfig
from backend.app.models.enums import TaskStatus, TeamType, UserRole
from backend.app.models.task import Task
from backend.app.models.team import Team
from backend.app.models.team_member import TeamMember
from backend.app.models.user import User
from backend.app.repositories.tasks import lock_task_positions
from backend.app.schemas.task import TaskCreate, TaskMove
from backend.app.services.tasks import TaskService


@pytest.fixture(scope="module")
def session_factory():
    """Migrate the explicitly disposable PostgreSQL URL and provide independent sessions."""
    database_url = os.getenv("TEST_DATABASE_URL")
    if not database_url:
        pytest.skip("TEST_DATABASE_URL is required for PostgreSQL integration tests")
    if not database_url.startswith(("postgresql://", "postgresql+")):
        pytest.skip("TEST_DATABASE_URL must identify PostgreSQL")

    settings.DATABASE_URL = database_url
    alembic_config = Config(os.path.join(os.path.dirname(__file__), "../../../alembic.ini"))
    command.upgrade(alembic_config, "head")

    engine = create_engine(database_url, poolclass=NullPool)
    factory = sessionmaker(engine, expire_on_commit=False)
    yield factory
    engine.dispose()


@pytest.fixture(autouse=True)
def isolated_database(session_factory):
    """Keep every scenario independent within the disposable migrated database."""
    with session_factory.begin() as db:
        db.execute(
            text(
                "TRUNCATE TABLE tasks, team_members, teams, app_users, app_config "
                "RESTART IDENTITY CASCADE"
            )
        )


def _seed_team(session_factory, *, in_progress_limit: int = 2) -> tuple[int, int, int]:
    """Create the minimum configuration, user, active team, and membership graph."""
    unique = uuid4().hex
    with session_factory.begin() as db:
        db.add(
            AppConfig(
                id=1,
                organization_name=f"org-{unique}",
                in_progress_limit=in_progress_limit,
            )
        )
        user = User(
            username=f"user-{unique}",
            username_normalized=f"user-{unique}",
            email=f"{unique}@example.test",
            password_hash="test-hash",
        )
        team = Team(name=f"team-{unique}", type=TeamType.TEAM, is_active=True)
        db.add_all([user, team])
        db.flush()
        member = TeamMember(team_id=team.id, user_id=user.id, role=UserRole.OWNER)
        db.add(member)
        db.flush()
        return team.id, user.id, member.id


def _seed_task(
    session_factory,
    team_id: int,
    member_id: int,
    *,
    status: TaskStatus,
    position: int,
    title: str | None = None,
) -> int:
    """Persist one review-free task with a caller-controlled board position."""
    with session_factory.begin() as db:
        task = Task(
            team_id=team_id,
            creator_member_id=member_id,
            title=title or f"task-{uuid4().hex}",
            status=status,
            position=position,
            should_review=False,
            started_working_at=(
                datetime.now(timezone.utc) if status == TaskStatus.IN_PROGRESS else None
            ),
        )
        db.add(task)
        db.flush()
        return task.id


def test_PG_001_concurrent_create_allocation(session_factory):
    team_id, user_id, _ = _seed_team(session_factory)
    barrier = Barrier(2)

    def create(title: str) -> None:
        with session_factory() as db:
            barrier.wait()
            TaskService().create_task(
                db,
                team_id,
                user_id,
                TaskCreate(title=title, should_review=False, status=TaskStatus.TODO),
            )
            db.commit()

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(create, f"concurrent-{index}") for index in range(2)]
        for future in futures:
            future.result()

    with session_factory() as db:
        positions = list(
            db.scalars(
                select(Task.position)
                .where(Task.team_id == team_id, Task.status == TaskStatus.TODO)
                .order_by(Task.position)
            )
        )
    assert positions == [1000, 2000]


def test_PG_002_concurrent_empty_column_movement(session_factory):
    team_id, _, member_id = _seed_team(session_factory)
    task_ids = [
        _seed_task(session_factory, team_id, member_id, status=TaskStatus.BACKLOG, position=position)
        for position in (1000, 2000)
    ]
    barrier = Barrier(2)

    def move(task_id: int) -> None:
        with session_factory() as db:
            task = db.get(Task, task_id)
            barrier.wait()
            TaskService().move_task(db, task, TaskMove(target_status=TaskStatus.TODO))
            db.commit()

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(move, task_id) for task_id in task_ids]
        for future in futures:
            future.result()

    with session_factory() as db:
        positions = list(
            db.scalars(
                select(Task.position)
                .where(Task.team_id == team_id, Task.status == TaskStatus.TODO)
                .order_by(Task.position)
            )
        )
    assert positions == [500, 1000]


def test_PG_003_concurrent_capacity_entry(session_factory):
    team_id, _, member_id = _seed_team(session_factory, in_progress_limit=2)
    _seed_task(session_factory, team_id, member_id, status=TaskStatus.IN_PROGRESS, position=1000)
    entrants = [
        _seed_task(session_factory, team_id, member_id, status=TaskStatus.TODO, position=position)
        for position in (1000, 2000)
    ]
    barrier = Barrier(2)

    def enter(task_id: int) -> str:
        with session_factory() as db:
            task = db.get(Task, task_id)
            barrier.wait()
            try:
                TaskService().move_task(
                    db, task, TaskMove(target_status=TaskStatus.IN_PROGRESS)
                )
                db.commit()
                return "entered"
            except ApiConflictError:
                db.rollback()
                return "rejected"

    with ThreadPoolExecutor(max_workers=2) as executor:
        outcomes = list(executor.map(enter, entrants))

    with session_factory() as db:
        count = len(
            list(
                db.scalars(
                    select(Task.id).where(
                        Task.team_id == team_id,
                        Task.status == TaskStatus.IN_PROGRESS,
                    )
                )
            )
        )
    assert sorted(outcomes) == ["entered", "rejected"]
    assert count == 2


def test_PG_004_waiting_move_refresh(session_factory):
    team_id, _, member_id = _seed_team(session_factory, in_progress_limit=1)
    task_id = _seed_task(
        session_factory, team_id, member_id, status=TaskStatus.TODO, position=1000
    )
    attempting_move = Event()

    def waiting_move() -> TaskStatus:
        with session_factory() as db:
            task = db.get(Task, task_id)
            attempting_move.set()
            TaskService().move_task(db, task, TaskMove(target_status=TaskStatus.IN_PROGRESS))
            db.commit()
            return task.status

    with session_factory() as locker:
        lock_task_positions(locker, team_id)
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(waiting_move)
            assert attempting_move.wait(timeout=5)
            locker.execute(
                text(
                    "UPDATE tasks SET status = 'in_progress', "
                    "started_working_at = now() WHERE id = :task_id"
                ),
                {"task_id": task_id},
            )
            locker.commit()
            observed_status = future.result()

    assert observed_status == TaskStatus.IN_PROGRESS


def test_PG_005_atomic_rebalance(session_factory):
    team_id, _, member_id = _seed_team(session_factory)
    first_id = _seed_task(
        session_factory, team_id, member_id, status=TaskStatus.TODO, position=1
    )
    second_id = _seed_task(
        session_factory, team_id, member_id, status=TaskStatus.TODO, position=2
    )
    moved_id = _seed_task(
        session_factory, team_id, member_id, status=TaskStatus.BACKLOG, position=1000
    )

    with session_factory() as db:
        moved = db.get(Task, moved_id)
        TaskService().move_task(
            db,
            moved,
            TaskMove(target_status=TaskStatus.TODO, anchor_task_id=first_id),
        )
        db.commit()

    with session_factory() as db:
        ordered = list(
            db.execute(
                select(Task.id, Task.position)
                .where(Task.team_id == team_id, Task.status == TaskStatus.TODO)
                .order_by(Task.position)
            )
        )
    assert [row.id for row in ordered] == [first_id, moved_id, second_id]
    assert [row.position for row in ordered] == [1000, 1500, 2000]
    assert len({row.position for row in ordered}) == 3


def test_PG_006_constraint_mode(session_factory):
    team_id, _, member_id = _seed_team(session_factory)
    first_id = _seed_task(
        session_factory, team_id, member_id, status=TaskStatus.TODO, position=1000
    )
    second_id = _seed_task(
        session_factory, team_id, member_id, status=TaskStatus.TODO, position=2000
    )

    with session_factory() as db:
        db.get(Task, second_id).position = 1000
        with pytest.raises(IntegrityError):
            db.flush()
        db.rollback()

    with session_factory() as db:
        db.execute(text("SET CONSTRAINTS uq_task_team_status_position DEFERRED"))
        db.execute(text("UPDATE tasks SET position = 2000 WHERE id = :id"), {"id": first_id})
        db.execute(text("UPDATE tasks SET position = 1000 WHERE id = :id"), {"id": second_id})
        db.commit()

    with session_factory() as db:
        db.execute(text("SET CONSTRAINTS uq_task_team_status_position DEFERRED"))
        db.execute(text("UPDATE tasks SET position = 1000 WHERE id = :id"), {"id": first_id})
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()

    with session_factory() as db:
        positions = list(
            db.scalars(
                select(Task.position)
                .where(Task.id.in_([first_id, second_id]))
                .order_by(Task.id)
            )
        )
    assert sorted(positions) == [1000, 2000]
