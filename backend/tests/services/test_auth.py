import pytest

from backend.app.error import (
    AuthenticationFailedError,
    InvalidSessionError,
    NoActiveTeamSelectedError,
    TeamNotFoundError,
)
from backend.app.services.auth import (
    LoginService,
    SessionAuthService,
    ensure_active_team_id,
    get_last_active_team_id,
    hash_session_token,
)
