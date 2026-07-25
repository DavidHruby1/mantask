from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from fastapi import Response
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.app.api import dependencies
from backend.app.error import ApiInternalServerError


def test_get_current_session_persists_expiry_and_renews_cookie(monkeypatch):
    db = Mock(spec=Session)
    response = Mock(spec=Response)
    session = SimpleNamespace(id=1)
    monkeypatch.setattr(
        dependencies.session_auth_service,
        "get_valid_session_by_token",
        Mock(return_value=session),
    )

    result = dependencies.get_current_session(
        db,
        "plain-session-token",
        response,
    )

    db.commit.assert_called_once_with()
    db.rollback.assert_not_called()
    response.set_cookie.assert_called_once_with(
        key=dependencies.settings.SESSION_COOKIE_NAME,
        value="plain-session-token",
        httponly=True,
        secure=not dependencies.settings.DEBUG,
        samesite="lax",
        max_age=60 * 60 * 24 * dependencies.settings.SESSION_EXPIRE_DAYS,
        path="/",
    )
    assert result is session


def test_get_current_session_rolls_back_failed_expiry_renewal(monkeypatch):
    db = Mock(spec=Session)
    db.commit.side_effect = SQLAlchemyError()
    response = Mock(spec=Response)
    monkeypatch.setattr(
        dependencies.session_auth_service,
        "get_valid_session_by_token",
        Mock(return_value=SimpleNamespace(id=1)),
    )

    with pytest.raises(ApiInternalServerError, match="Unable to renew the session"):
        dependencies.get_current_session(
            db,
            "plain-session-token",
            response,
        )

    db.rollback.assert_called_once_with()
    response.set_cookie.assert_not_called()
