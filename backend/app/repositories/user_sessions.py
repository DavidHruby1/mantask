from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.user_session import UserSession


def create_user_session_record(
    db: Session,
    user_id: int,
    session_token_hash: str,
    expires_at: datetime,
) -> UserSession:
    user_session = UserSession(
        user_id=user_id, 
        session_token_hash=session_token_hash, 
        expires_at=expires_at
    )

    db.add(user_session)

    return user_session


def get_user_session_by_token_hash(
    db: Session, session_token_hash: str
) -> UserSession | None:
    session = db.scalar(
        select(UserSession).filter_by(session_token_hash=session_token_hash)
    )

    if not session:
        return None

    return session
