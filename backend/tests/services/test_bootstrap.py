from types import SimpleNamespace
from unittest.mock import Mock, call

import pytest
from sqlalchemy.orm import Session

from backend.app.models.enums import UserRole
from backend.app.schemas.bootstrap import BootstrapSetup
from backend.app.services import bootstrap as bootstrap_service


@pytest.fixture
def input_data() -> BootstrapSetup:
    return BootstrapSetup(
        username="David123",
        email="david@example.com",
        password="Valid-password123",
        organization_name="Example Organization",
        team_name="Example Team",
        bootstrap_secret="a" * 32,
    )


def mock_dependencies(monkeypatch):
    user = SimpleNamespace(id=10, last_active_team_id=None)
    private_team = SimpleNamespace(id=20)
    shared_team = SimpleNamespace(id=30)

    dependencies = SimpleNamespace(
        user=user,
        private_team=private_team,
        shared_team=shared_team,
        create_app_config=Mock(),
        hash_password=Mock(return_value="password-hash"),
        create_user=Mock(return_value=user),
        create_private_team=Mock(return_value=private_team),
        create_team=Mock(return_value=shared_team),
        create_team_member=Mock(),
    )

    monkeypatch.setattr(
        bootstrap_service, "create_app_config", dependencies.create_app_config
    )
    monkeypatch.setattr(bootstrap_service, "create_user", dependencies.create_user)
    monkeypatch.setattr(
        bootstrap_service, "create_private_team", dependencies.create_private_team
    )
    monkeypatch.setattr(bootstrap_service, "create_team", dependencies.create_team)
    monkeypatch.setattr(
        bootstrap_service, "create_team_member", dependencies.create_team_member
    )
    monkeypatch.setattr(
        bootstrap_service,
        "ph",
        SimpleNamespace(hash=dependencies.hash_password),
    )

    return dependencies


def test_bootstrap_application_creates_initial_state(monkeypatch, input_data):
    db = Mock(spec=Session)
    dependencies = mock_dependencies(monkeypatch)
    dependencies.user.id = None
    dependencies.private_team.id = None
    dependencies.shared_team.id = None

    def assign_generated_ids():
        if db.flush.call_count == 1:
            dependencies.user.id = 10
        else:
            dependencies.private_team.id = 20
            dependencies.shared_team.id = 30

    db.flush.side_effect = assign_generated_ids

    result = bootstrap_service.bootstrap_application(db, input_data)

    dependencies.create_app_config.assert_called_once_with(
        db, input_data.organization_name
    )
    dependencies.hash_password.assert_called_once_with(input_data.password)
    dependencies.create_user.assert_called_once_with(
        db,
        username="David123",
        username_normalized="david123",
        email=input_data.email,
        password_hash="password-hash",
    )
    dependencies.create_private_team.assert_called_once_with(
        db, owner_user_id=dependencies.user.id
    )
    dependencies.create_team.assert_called_once_with(db, name=input_data.team_name)
    assert dependencies.create_team_member.call_args_list == [
        call(
            db,
            user_id=dependencies.user.id,
            team_id=dependencies.private_team.id,
            role=UserRole.OWNER,
        ),
        call(
            db,
            user_id=dependencies.user.id,
            team_id=dependencies.shared_team.id,
            role=UserRole.OWNER,
        ),
    ]
    assert db.flush.call_count == 2
    assert dependencies.user.last_active_team_id == dependencies.private_team.id
    assert result is dependencies.user
    db.commit.assert_not_called()
    db.rollback.assert_not_called()


def test_bootstrap_application_propagates_repository_failure(
    monkeypatch, input_data
):
    db = Mock(spec=Session)
    dependencies = mock_dependencies(monkeypatch)
    failure = RuntimeError("Database failure")
    dependencies.create_team.side_effect = failure

    with pytest.raises(RuntimeError) as caught:
        bootstrap_service.bootstrap_application(db, input_data)

    assert caught.value is failure
    dependencies.create_team_member.assert_not_called()
    assert dependencies.user.last_active_team_id is None
    db.commit.assert_not_called()
    db.rollback.assert_not_called()
