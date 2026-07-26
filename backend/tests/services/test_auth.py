from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from argon2.exceptions import (
    InvalidHashError,
    VerificationError,
    VerifyMismatchError,
)
from sqlalchemy.orm import Session

from backend.app.error import (
    AuthenticationFailedError,
    InvalidSessionError,
    NoActiveTeamSelectedError,
    TeamNotFoundError,
)
from backend.app.services import auth as auth_service
from backend.app.services.auth import (
    DUMMY_PASSWORD_HASH,
    LoginService,
    SESSION_TOKEN_BYTES,
    SessionAuthService,
    ensure_active_team_id,
    get_last_active_team_id,
    hash_session_token,
)


def test_hash_session_token_returns_sha256_hash():
    assert hash_session_token("session-token") == (
        "c101e911469c969171040b50d70543313cf968fdef5bacc780776f8fb399ab36"
    )


def test_create_session_stores_hash_and_returns_plain_token(monkeypatch):
    db = Mock(spec=Session)
    now = datetime(2026, 7, 25, 10, 30, tzinfo=timezone.utc)
    datetime_mock = Mock(wraps=datetime)
    datetime_mock.now.return_value = now
    create_session_record = Mock()
    monkeypatch.setattr(auth_service, "datetime", datetime_mock)
    monkeypatch.setattr(
        auth_service.secrets,
        "token_urlsafe",
        Mock(return_value="plain-session-token"),
    )
    monkeypatch.setattr(
        auth_service,
        "create_user_session_record",
        create_session_record,
    )

    result = LoginService().create_session(db, user_id=12)

    auth_service.secrets.token_urlsafe.assert_called_once_with(SESSION_TOKEN_BYTES)
    create_session_record.assert_called_once_with(
        db,
        12,
        hash_session_token("plain-session-token"),
        now + timedelta(days=auth_service.settings.SESSION_EXPIRE_DAYS),
    )
    assert result == "plain-session-token"
    db.commit.assert_not_called()
    db.rollback.assert_not_called()


def test_authenticate_user_returns_active_user_with_valid_password(monkeypatch):
    db = Mock(spec=Session)
    user = SimpleNamespace(password_hash="stored-hash", is_active=True)
    get_user = Mock(return_value=user)
    verify_password = Mock(return_value=True)
    monkeypatch.setattr(auth_service, "get_user_by_email", get_user)
    monkeypatch.setattr(
        auth_service,
        "ph",
        SimpleNamespace(verify=verify_password),
    )

    result = LoginService().authenticate_user(
        db,
        "david@example.com",
        "Valid-password123",
    )

    get_user.assert_called_once_with(db, "david@example.com")
    verify_password.assert_called_once_with("stored-hash", "Valid-password123")
    assert result is user


def test_authenticate_user_checks_dummy_hash_when_user_does_not_exist(monkeypatch):
    db = Mock(spec=Session)
    verify_password = Mock(return_value=True)
    monkeypatch.setattr(auth_service, "get_user_by_email", Mock(return_value=None))
    monkeypatch.setattr(
        auth_service,
        "ph",
        SimpleNamespace(verify=verify_password),
    )

    with pytest.raises(AuthenticationFailedError):
        LoginService().authenticate_user(
            db,
            "missing@example.com",
            "Invalid-password123",
        )

    verify_password.assert_called_once_with(
        DUMMY_PASSWORD_HASH,
        "Invalid-password123",
    )


def test_authenticate_user_rejects_inactive_user(monkeypatch):
    db = Mock(spec=Session)
    user = SimpleNamespace(password_hash="stored-hash", is_active=False)
    verify_password = Mock(return_value=True)
    monkeypatch.setattr(auth_service, "get_user_by_email", Mock(return_value=user))
    monkeypatch.setattr(
        auth_service,
        "ph",
        SimpleNamespace(verify=verify_password),
    )

    with pytest.raises(AuthenticationFailedError):
        LoginService().authenticate_user(
            db,
            "david@example.com",
            "Valid-password123",
        )

    verify_password.assert_called_once_with("stored-hash", "Valid-password123")


@pytest.mark.parametrize(
    "verification_error",
    [VerifyMismatchError(), VerificationError(), InvalidHashError()],
)
def test_authenticate_user_rejects_argon_verification_errors(
    monkeypatch,
    verification_error,
):
    db = Mock(spec=Session)
    user = SimpleNamespace(password_hash="stored-hash", is_active=True)
    monkeypatch.setattr(auth_service, "get_user_by_email", Mock(return_value=user))
    monkeypatch.setattr(
        auth_service,
        "ph",
        SimpleNamespace(verify=Mock(side_effect=verification_error)),
    )

    with pytest.raises(AuthenticationFailedError):
        LoginService().authenticate_user(
            db,
            "david@example.com",
            "Invalid-password123",
        )


def test_get_valid_session_by_token_renews_valid_session(monkeypatch):
    db = Mock(spec=Session)
    now = datetime(2026, 7, 25, 10, 30, tzinfo=timezone.utc)
    datetime_mock = Mock(wraps=datetime)
    datetime_mock.now.return_value = now
    session = SimpleNamespace(
        revoked_at=None,
        expires_at=now + timedelta(days=1),
    )
    get_session = Mock(return_value=session)
    monkeypatch.setattr(auth_service, "datetime", datetime_mock)
    monkeypatch.setattr(
        auth_service,
        "get_user_session_by_token_hash",
        get_session,
    )

    result = SessionAuthService().get_valid_session_by_token(
        db,
        "plain-session-token",
    )

    get_session.assert_called_once_with(
        db,
        hash_session_token("plain-session-token"),
    )
    assert session.expires_at == now + timedelta(
        days=auth_service.settings.SESSION_EXPIRE_DAYS
    )
    assert result is session


@pytest.mark.parametrize(
    "session",
    [
        None,
        SimpleNamespace(
            revoked_at=datetime(2026, 7, 25, 9, 30, tzinfo=timezone.utc),
            expires_at=datetime(2026, 7, 26, 10, 30, tzinfo=timezone.utc),
        ),
        SimpleNamespace(
            revoked_at=None,
            expires_at=datetime(2026, 7, 25, 10, 30, tzinfo=timezone.utc),
        ),
    ],
    ids=["missing", "revoked", "expired"],
)
def test_get_valid_session_by_token_rejects_invalid_session(
    monkeypatch,
    session,
):
    db = Mock(spec=Session)
    datetime_mock = Mock(wraps=datetime)
    datetime_mock.now.return_value = datetime(
        2026,
        7,
        25,
        10,
        30,
        tzinfo=timezone.utc,
    )
    monkeypatch.setattr(auth_service, "datetime", datetime_mock)
    monkeypatch.setattr(
        auth_service,
        "get_user_session_by_token_hash",
        Mock(return_value=session),
    )

    with pytest.raises(InvalidSessionError):
        SessionAuthService().get_valid_session_by_token(
            db,
            "plain-session-token",
        )


def test_revoke_session_by_token_returns_false_when_session_is_missing(monkeypatch):
    db = Mock(spec=Session)
    get_session = Mock(return_value=None)
    monkeypatch.setattr(
        auth_service,
        "get_user_session_by_token_hash",
        get_session,
    )

    result = SessionAuthService().revoke_session_by_token(
        db,
        "plain-session-token",
    )

    get_session.assert_called_once_with(
        db,
        hash_session_token("plain-session-token"),
    )
    assert result is False


def test_revoke_session_by_token_sets_revocation_time(monkeypatch):
    db = Mock(spec=Session)
    now = datetime(2026, 7, 25, 10, 30, tzinfo=timezone.utc)
    datetime_mock = Mock(wraps=datetime)
    datetime_mock.now.return_value = now
    session = SimpleNamespace(revoked_at=None)
    monkeypatch.setattr(auth_service, "datetime", datetime_mock)
    monkeypatch.setattr(
        auth_service,
        "get_user_session_by_token_hash",
        Mock(return_value=session),
    )

    result = SessionAuthService().revoke_session_by_token(
        db,
        "plain-session-token",
    )

    assert session.revoked_at == now
    assert result is True
    db.commit.assert_not_called()
    db.rollback.assert_not_called()


def test_revoke_session_by_token_keeps_existing_revocation_time(monkeypatch):
    db = Mock(spec=Session)
    revoked_at = datetime(2026, 7, 24, 10, 30, tzinfo=timezone.utc)
    session = SimpleNamespace(revoked_at=revoked_at)
    monkeypatch.setattr(
        auth_service,
        "get_user_session_by_token_hash",
        Mock(return_value=session),
    )

    result = SessionAuthService().revoke_session_by_token(
        db,
        "plain-session-token",
    )

    assert session.revoked_at == revoked_at
    assert result is True


def test_get_last_active_team_id_returns_active_member_team(monkeypatch):
    db = Mock(spec=Session)
    team = SimpleNamespace(id=20, is_active=True)
    user = SimpleNamespace(id=10, last_active_team_id=20)
    db.get.return_value = team
    is_member = Mock(return_value=True)
    monkeypatch.setattr(auth_service, "is_team_member", is_member)

    result = get_last_active_team_id(db, user)

    db.get.assert_called_once_with(auth_service.Team, 20)
    is_member.assert_called_once_with(db, 20, 10)
    assert result == 20


def test_get_last_active_team_id_rejects_missing_selection():
    db = Mock(spec=Session)
    user = SimpleNamespace(id=10, last_active_team_id=None)

    with pytest.raises(TeamNotFoundError):
        get_last_active_team_id(db, user)

    db.get.assert_not_called()


@pytest.mark.parametrize(
    ("team", "is_member"),
    [
        (None, True),
        (SimpleNamespace(id=20, is_active=False), True),
        (SimpleNamespace(id=20, is_active=True), False),
    ],
    ids=["missing-team", "inactive-team", "not-a-member"],
)
def test_get_last_active_team_id_rejects_unusable_team(
    monkeypatch,
    team,
    is_member,
):
    db = Mock(spec=Session)
    user = SimpleNamespace(id=10, last_active_team_id=20)
    db.get.return_value = team
    monkeypatch.setattr(
        auth_service,
        "is_team_member",
        Mock(return_value=is_member),
    )

    with pytest.raises(NoActiveTeamSelectedError):
        get_last_active_team_id(db, user)


def test_ensure_active_team_id_keeps_valid_selection(monkeypatch):
    db = Mock(spec=Session)
    user = SimpleNamespace(id=10, last_active_team_id=20)
    get_private_team = Mock()
    monkeypatch.setattr(
        auth_service,
        "get_last_active_team_id",
        Mock(return_value=20),
    )
    monkeypatch.setattr(
        auth_service,
        "get_private_team_id",
        get_private_team,
    )

    result = ensure_active_team_id(db, user)

    get_private_team.assert_not_called()
    assert user.last_active_team_id == 20
    assert result == 20


@pytest.mark.parametrize(
    "selection_error",
    [TeamNotFoundError(), NoActiveTeamSelectedError()],
    ids=["missing-selection", "unusable-selection"],
)
def test_ensure_active_team_id_falls_back_to_private_team(
    monkeypatch,
    selection_error,
):
    db = Mock(spec=Session)
    user = SimpleNamespace(id=10, last_active_team_id=20)
    get_private_team = Mock(return_value=30)
    monkeypatch.setattr(
        auth_service,
        "get_last_active_team_id",
        Mock(side_effect=selection_error),
    )
    monkeypatch.setattr(
        auth_service,
        "get_private_team_id",
        get_private_team,
    )

    result = ensure_active_team_id(db, user)

    get_private_team.assert_called_once_with(db, user)
    assert user.last_active_team_id == 30
    assert result == 30
    db.commit.assert_not_called()
    db.rollback.assert_not_called()
