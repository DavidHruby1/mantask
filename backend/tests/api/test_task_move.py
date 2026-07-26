from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError

from backend.app.api.dependencies import get_current_session
from backend.app.core.db import get_db
from backend.app.error import (
    ApiConflictError,
    InvalidTaskError,
    TaskNotFoundError,
    TeamInactiveError,
    TeamMembershipError,
    TeamNotFoundError,
)
from backend.app.main import app
from backend.app.models.enums import TaskStatus
from backend.app.services.tasks import task_service


@pytest.fixture
def db():
    return MagicMock()


@pytest.fixture
def client(db):
    """Provide authenticated HTTP access and always restore the app's global overrides."""
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_current_session] = lambda: SimpleNamespace(user_id=7)
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def task():
    """Return every persisted attribute required by the public TaskRead contract."""
    timestamp = datetime(2026, 7, 26, 12, 0, tzinfo=timezone.utc)
    return SimpleNamespace(
        id=41,
        team_id=3,
        creator_member_id=5,
        assignee_member_id=None,
        reviewer_member_id=6,
        title="Ship task movement",
        description="Move this task through the board",
        layer="backend",
        priority=None,
        review_date=None,
        due_date=None,
        effort=None,
        should_review=True,
        status=TaskStatus.TODO,
        position=1000,
        created_at=timestamp,
        updated_at=timestamp,
        started_working_at=None,
        submitted_for_review_at=None,
        completed_at=None,
        returned_count=0,
        reopened_count=0,
        blocked_count=0,
    )


@pytest.mark.parametrize("_scenario", [None], ids=["API-001"])
def test_self_anchor_returns_current_task_read(_scenario, client, monkeypatch, task):
    monkeypatch.setattr(task_service, "get_accessible_task", MagicMock(return_value=task))
    monkeypatch.setattr(task_service, "move_task", MagicMock(return_value=task))

    response = client.patch(
        f"/api/tasks/{task.id}/move",
        json={"target_status": "todo", "anchor_task_id": task.id},
    )

    assert response.status_code == 200
    assert response.json()["id"] == task.id
    assert response.json()["status"] == "todo"


@pytest.mark.parametrize("_scenario", [None], ids=["API-002"])
def test_invalid_transition_returns_400(_scenario, client, monkeypatch, task):
    monkeypatch.setattr(task_service, "get_accessible_task", MagicMock(return_value=task))
    monkeypatch.setattr(
        task_service,
        "move_task",
        MagicMock(side_effect=InvalidTaskError("Invalid transition")),
    )

    response = client.patch(
        f"/api/tasks/{task.id}/move", json={"target_status": "done"}
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid transition"}


@pytest.mark.parametrize("_scenario", [None], ids=["API-003"])
def test_invalid_anchor_returns_400(_scenario, client, monkeypatch, task):
    monkeypatch.setattr(task_service, "get_accessible_task", MagicMock(return_value=task))
    monkeypatch.setattr(
        task_service,
        "move_task",
        MagicMock(side_effect=InvalidTaskError("Anchor is invalid or stale")),
    )

    response = client.patch(
        f"/api/tasks/{task.id}/move",
        json={"target_status": "todo", "anchor_task_id": 999},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Anchor is invalid or stale"}


@pytest.mark.parametrize("_scenario", [None], ids=["API-004"])
def test_in_progress_capacity_conflict_returns_409(
    _scenario, client, monkeypatch, task
):
    monkeypatch.setattr(task_service, "get_accessible_task", MagicMock(return_value=task))
    monkeypatch.setattr(
        task_service,
        "move_task",
        MagicMock(side_effect=ApiConflictError("IN_PROGRESS limit reached")),
    )

    response = client.patch(
        f"/api/tasks/{task.id}/move", json={"target_status": "in_progress"}
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "IN_PROGRESS limit reached"}


@pytest.mark.parametrize("_scenario", [None], ids=["API-005"])
def test_commit_integrity_error_rolls_back_and_returns_409(
    _scenario, client, db, monkeypatch, task
):
    monkeypatch.setattr(task_service, "get_accessible_task", MagicMock(return_value=task))
    monkeypatch.setattr(task_service, "move_task", MagicMock(return_value=task))
    db.commit.side_effect = IntegrityError("statement", {}, Exception("collision"))

    response = client.patch(
        f"/api/tasks/{task.id}/move", json={"target_status": "in_progress"}
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": "Task movement conflicts with current board state"
    }
    db.rollback.assert_called_once_with()
    db.refresh.assert_not_called()


@pytest.mark.parametrize("_scenario", [None], ids=["API-006"])
def test_unauthenticated_request_returns_401(_scenario, db):
    app.dependency_overrides.clear()
    app.dependency_overrides[get_db] = lambda: db
    try:
        with TestClient(app) as unauthenticated_client:
            response = unauthenticated_client.patch(
                "/api/tasks/41/move", json={"target_status": "todo"}
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


@pytest.mark.parametrize(
    "error",
    [TaskNotFoundError(), TeamNotFoundError()],
    ids=["API-007-missing-task", "API-007-missing-team"],
)
def test_missing_resource_returns_404(error, client, monkeypatch):
    monkeypatch.setattr(
        task_service, "get_accessible_task", MagicMock(side_effect=error)
    )

    response = client.patch(
        "/api/tasks/41/move", json={"target_status": "todo"}
    )

    assert response.status_code == 404
    assert response.json() == {"detail": error.detail}


@pytest.mark.parametrize(
    "error",
    [TeamMembershipError(), TeamInactiveError()],
    ids=["API-008-membership", "API-008-inactive-team"],
)
def test_existing_access_failure_returns_409(error, client, monkeypatch):
    monkeypatch.setattr(
        task_service, "get_accessible_task", MagicMock(side_effect=error)
    )

    response = client.patch(
        "/api/tasks/41/move", json={"target_status": "todo"}
    )

    assert response.status_code == 409
    assert response.json() == {"detail": error.detail}


@pytest.mark.parametrize("_scenario", [None], ids=["API-009"])
def test_success_commits_once_refreshes_and_returns_task_read(
    _scenario, client, db, monkeypatch, task
):
    get_accessible_task = MagicMock(return_value=task)
    move_task = MagicMock(return_value=task)
    monkeypatch.setattr(task_service, "get_accessible_task", get_accessible_task)
    monkeypatch.setattr(task_service, "move_task", move_task)

    response = client.patch(
        f"/api/tasks/{task.id}/move", json={"target_status": "in_progress"}
    )

    assert response.status_code == 200
    assert response.json()["id"] == task.id
    assert response.json()["title"] == task.title
    get_accessible_task.assert_called_once_with(db, task.id, 7)
    move_task.assert_called_once()
    db.commit.assert_called_once_with()
    db.refresh.assert_called_once_with(task)
    db.rollback.assert_not_called()
