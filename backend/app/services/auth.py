from datetime import (
    datetime,
    timedelta,
    timezone,
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
from backend.app.models.auth_session import AuthSession
from backend.app.models.user import User


ph = PasswordHasher()


def generate_session_token() -> str:
    return secrets.token_urlsafe(32)


def hash_session_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_auth_session(db: Session, user_id: int) -> str:
    raw_token = generate_session_token()
    token_hash = hash_session_token(raw_token)
    expires_at = datetime.now(timezone.utc) + timedelta(
        days=settings.SESSION_EXPIRE_DAYS
    )

    auth_session = AuthSession(
        user_id=user_id,
        token_hash=token_hash, 
        expires_at=expires_at
    )
    db.add(auth_session)

    return raw_token


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


def get_session_by_token(db: Session, raw_token: str) -> AuthSession | None:
    token_hash = hash_session_token(raw_token)
    session = db.scalar(select(AuthSession).filter_by(token_hash=token_hash))
    if not session:
        return None

    return session


def verify_session_token(session: AuthSession) -> bool:
    now = datetime.now(timezone.utc)
    if session.revoked_at:
        return False
    if session.expires_at <= now:
        return False

    return True
