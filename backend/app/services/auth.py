from datetime import (
    datetime,
    timedelta,
    timezone
)

import hashlib
import secrets
from argon2 import (
    PasswordHasher,
    VerifyMismatchError,
    VerificationError,
    InvalidHashError,
)

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.models.user_session import UserSession
from backend.app.models.user import User


ph = PasswordHasher()
DUMMY_PASSWORD_HASH = "$argon2id$v=19$m=65536,t=3,p=4$Q2k2U05wOTdoZkVEMTZUUA$qyASxedh9bH8/a6Xr8Hg9fXR9zlqwvUb89LgqnLr4HY"


def generate_session_token() -> str:
    return secrets.token_urlsafe(32)


def hash_session_token(session_token: str) -> str:
    return hashlib.sha256(session_token.encode("utf-8")).hexdigest()


def create_user_session(db: Session, user_id: int) -> str:
    session_token = generate_session_token()
    session_token_hash = hash_session_token(session_token)
    expires_at = datetime.now(timezone.utc) + timedelta(
        days=settings.SESSION_EXPIRE_DAYS
    )

    auth_session = UserSession(
        user_id=user_id, 
        session_token_hash=session_token_hash, 
        expires_at=expires_at
    )
    db.add(auth_session)

    return session_token


def get_user_by_email(db: Session, email: str) -> User | None:
    user = db.scalar(select(User).filter_by(email=email))
    if not user:
        return None

    return user


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return ph.verify(password_hash, password)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(db, email)
    password_hash = user.password_hash if user else DUMMY_PASSWORD_HASH
    password_ok = verify_password(password, password_hash)

    if not user:
        return None
    if not user.is_active:
        return None
    if not password_ok:
        return None

    return user


def get_user_session_by_token(db: Session, session_token: str) -> UserSession | None:
    session_token_hash = hash_session_token(session_token)
    session = db.scalar(
        select(UserSession).filter_by(session_token_hash=session_token_hash)
    )
    if not session:
        return None

    return session


def is_user_session_valid(session: UserSession) -> bool:
    now = datetime.now(timezone.utc)
    if session.revoked_at:
        return False
    if session.expires_at <= now:
        return False

    return True
