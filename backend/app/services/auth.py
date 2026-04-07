import hashlib
import secrets

from sqlalchemy.orm import Session

from backend.app.models.auth_session import AuthSession


def generate_session_token() -> str:
    return secrets.token_urlsafe(32)

def hash_session_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()

def create_auth_session(
    db: Session, 
    user_id: int, 
    team_id: int
) -> str: 
    raw_token = generate_session_token()
    token_hash = hash_session_token(raw_token)

    auth_session = AuthSession(
        user_id=user_id,
        token_hash=token_hash,
        current_team_id=team_id
    )
    db.add(auth_session)

    return raw_token
