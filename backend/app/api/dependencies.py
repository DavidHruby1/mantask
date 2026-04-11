from typing import Annotated

from fastapi import Depends, Cookie, HTTPException
from sqlalchemy.orm import Session

from backend.app.core.db import get_db
from backend.app.models.user_session import UserSession
from backend.app.core.config import settings
from backend.app.services.auth import get_user_session_by_token, is_user_session_valid


DbSessionDep = Annotated[Session, Depends(get_db)]
SessionTokenDep = Annotated[
    str | None, Cookie(default=None, alias=settings.SESSION_COOKIE_NAME)
]


def get_current_session(
    db: DbSessionDep, session_token: SessionTokenDep
) -> UserSession:
    if not session_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    session = get_user_session_by_token(db, session_token)
    if not session or not is_user_session_valid(session):
        raise HTTPException(status_code=401, detail="Not authenticated")

    return session


CurrentSessionDep = Annotated[UserSession, Depends(get_current_session)]
