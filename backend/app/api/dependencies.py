from typing import Annotated

from fastapi import Depends, Cookie, Response
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.app.core.db import get_db
from backend.app.error import ApiInternalServerError, NotAuthenticatedError
from backend.app.models.user_session import UserSession
from backend.app.core.config import settings
from backend.app.services.auth import session_auth_service


DbSessionDep = Annotated[Session, Depends(get_db)]
SessionTokenDep = Annotated[
    str | None, Cookie(alias=settings.SESSION_COOKIE_NAME)
]


def get_current_session(
    db: DbSessionDep,
    session_token: SessionTokenDep,
    response: Response,
) -> UserSession:
    """Authenticate activity and persist the renewed server and browser expiry."""
    if not session_token:
        raise NotAuthenticatedError()

    session, extended = session_auth_service.get_valid_session_by_token(db, session_token)

    # in `get_valid_session_by_token`, expiry is extended only if older than one day and if so, extended is True
    # therefore commit is made and cookie is set. This is to make the amount of commits lower
    if extended:
        try:
            db.commit()
        except SQLAlchemyError:
            db.rollback()
            raise ApiInternalServerError("Unable to renew the session")

        response.set_cookie(
            key=settings.SESSION_COOKIE_NAME,
            value=session_token,
            httponly=True,
            secure=not settings.DEBUG,
            samesite="lax",
            max_age=60 * 60 * 24 * settings.SESSION_EXPIRE_DAYS,
            path="/",
        )

    return session


CurrentSessionDep = Annotated[UserSession, Depends(get_current_session)]
