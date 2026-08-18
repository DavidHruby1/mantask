from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from backend.app.api.endpoints import users
from backend.app.error import NotAuthenticatedError


def test_get_current_user_returns_authenticated_user(monkeypatch):
    now = datetime.now(timezone.utc)
    user = SimpleNamespace(
        id=7,
        username="alice",
        email="alice@example.com",
        is_active=True,
        profile_picture_path=None,
        last_active_team_id=3,
        created_at=now,
        updated_at=now,
    )
    monkeypatch.setattr(users, "get_user_by_id", lambda db, user_id: user)

    result = users.get_current_user(
        SimpleNamespace(), SimpleNamespace(user_id=7)
    )

    assert result.id == 7
    assert result.email == "alice@example.com"
    assert result.last_active_team_id == 3


def test_get_current_user_rejects_missing_session_user(monkeypatch):
    monkeypatch.setattr(users, "get_user_by_id", lambda db, user_id: None)

    with pytest.raises(NotAuthenticatedError):
        users.get_current_user(
            SimpleNamespace(), SimpleNamespace(user_id=7)
        )
