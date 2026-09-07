from datetime import datetime, timezone
from types import SimpleNamespace

from backend.app.api.endpoints import teams


def test_get_current_user_teams_returns_repository_teams(monkeypatch):
    now = datetime.now(timezone.utc)
    team = SimpleNamespace(
        id=3,
        name="Engineering",
        created_at=now,
        updated_at=now,
        is_active=True,
    )
    monkeypatch.setattr(
        teams,
        "get_teams_by_user_id",
        lambda db, user_id: [team],
    )

    result = teams.get_current_user_teams(
        SimpleNamespace(), SimpleNamespace(user_id=7)
    )

    assert len(result) == 1
    assert result[0].id == 3
    assert result[0].name == "Engineering"
