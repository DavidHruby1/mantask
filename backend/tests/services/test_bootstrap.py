from types import SimpleNamespace
from unittest.mock import Mock, call

from sqlalchemy.orm import Session

from backend.app.models.enums import UserRole
from backend.app.schemas.bootstrap import BootstrapSetup
from backend.app.services import bootstrap as bootstrap_service


def test_bootstrap_application_creates_initial_state(monkeypatch):
    input_data = BootstrapSetup(
        username="David123",
        email="david@example.com",
        password="Valid-password123",
        organization_name="Example Organization",
        team_name="Example Team",
        bootstrap_secret="a" * 32,
    )
    db = Mock(spec=Session)
    user = SimpleNamespace(id=10, last_active_team_id=None)
    private_team = SimpleNamespace(id=20)
    shared_team = SimpleNamespace(id=30)
    create_app_config = Mock()
    hash_password = Mock(return_value="password-hash")
    create_user = Mock(return_value=user)
    create_private_team = Mock(return_value=private_team)
    create_team = Mock(return_value=shared_team)
    create_team_member = Mock()

    monkeypatch.setattr(bootstrap_service, "create_app_config", create_app_config)
    monkeypatch.setattr(bootstrap_service, "create_user", create_user)
    monkeypatch.setattr(bootstrap_service, "create_private_team", create_private_team)
    monkeypatch.setattr(bootstrap_service, "create_team", create_team)
    monkeypatch.setattr(bootstrap_service, "create_team_member", create_team_member)
    monkeypatch.setattr(
        bootstrap_service,
        "ph",
        SimpleNamespace(hash=hash_password),
    )

    result = bootstrap_service.bootstrap_application(db, input_data)

    create_app_config.assert_called_once_with(db, input_data.organization_name)
    hash_password.assert_called_once_with(input_data.password)
    create_user.assert_called_once_with(
        db,
        username="David123",
        username_normalized="david123",
        email=input_data.email,
        password_hash="password-hash",
    )
    create_private_team.assert_called_once_with(db, owner_user_id=user.id)
    create_team.assert_called_once_with(db, name=input_data.team_name)
    assert create_team_member.call_args_list == [
        call(
            db,
            user_id=user.id,
            team_id=private_team.id,
            role=UserRole.OWNER,
        ),
        call(
            db,
            user_id=user.id,
            team_id=shared_team.id,
            role=UserRole.OWNER,
        ),
    ]
    assert db.flush.call_count == 2
    assert user.last_active_team_id == private_team.id
    assert result is user
    db.commit.assert_not_called()
    db.rollback.assert_not_called()
