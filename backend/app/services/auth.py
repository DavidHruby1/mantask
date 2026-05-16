from datetime import datetime, timedelta, timezone

import hashlib
import secrets
from argon2 import (
    PasswordHasher, 
    VerifyMismatchError, 
    VerificationError, 
    InvalidHashError
)

from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.models.user import User
from backend.app.models.user_session import UserSession

from backend.app.repositories.teams import get_active_team_id, get_private_team_id
from backend.app.repositories.users import get_user_by_email
from backend.app.repositories.users import (
    create_user_session_record,
    get_user_session_by_token_hash,
)


DUMMY_PASSWORD_HASH = "$argon2id$v=19$m=65536,t=3,p=4$Q2k2U05wOTdoZkVEMTZUUA$qyASxedh9bH8/a6Xr8Hg9fXR9zlqwvUb89LgqnLr4HY"
SESSION_TOKEN_BYTES = 32


ph = PasswordHasher()


class LoginService:
    def __init__(self, db: Session):
        self.db = db

    def create_session(self, user_id: int) -> str:
        session_token = secrets.token_urlsafe(SESSION_TOKEN_BYTES)
        session_token_hash = hash_session_token(session_token)
        expires_at = datetime.now(timezone.utc) + timedelta(
            days=settings.SESSION_EXPIRE_DAYS
        )
        create_user_session_record(
            self.db, user_id, session_token_hash, expires_at
        )
        return session_token

    def authenticate_user(self, email: str, password: str) -> User | None:
        user = get_user_by_email(self.db, email)
        password_hash = user.password_hash if user else DUMMY_PASSWORD_HASH
        password_ok = self._verify_password(password, password_hash)

        if not user:
            return None
        if not user.is_active:
            return None
        if not password_ok:
            return None

        return user

    def _verify_password(self, password: str, password_hash: str) -> bool:
        try:
            return ph.verify(password_hash, password)
        except (VerifyMismatchError, VerificationError, InvalidHashError):
            return False


class SessionAuthService:
    def __init__(self, db: Session):
        self.db = db

    def get_valid_session_by_token(self, session_token: str) -> UserSession | None:
        session_token_hash = hash_session_token(session_token)
        user_session = get_user_session_by_token_hash(self.db, session_token_hash)

        if user_session is None:
            return None
        if not self._is_valid_session(user_session):
            return None

        return user_session

    def revoke_session_by_token(self, session_token: str) -> bool:
        session_token_hash = hash_session_token(session_token)
        session = get_user_session_by_token_hash(self.db, session_token_hash)

        if session is None:
            return False
        if session.revoked_at is None:
            session.revoked_at = datetime.now(timezone.utc)

        return True

    def _is_valid_session(self, session: UserSession) -> bool:
        now = datetime.now(timezone.utc)

        if session.revoked_at:
            return False
        if session.expires_at <= now:
            return False

        return True


def ensure_active_team_id(db: Session, user: User) -> int | None:
    active_team_id = get_active_team_id(db, user)
    if active_team_id is None:
        active_team_id = get_private_team_id(db, user)

    if user.last_active_team_id != active_team_id:
        user.last_active_team_id = active_team_id

    return active_team_id


def hash_session_token(session_token: str) -> str:
    return hashlib.sha256(session_token.encode("utf-8")).hexdigest()
