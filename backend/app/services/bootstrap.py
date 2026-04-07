from argon2 import PasswordHasher

from sqlalchemy.orm import Session

from backend.app.models.app_config import AppConfig
from backend.app.models.auth_session import AuthSession
from backend.app.models.enums import UserRole
from backend.app.models.team import Team
from backend.app.models.team_member import TeamMember
from backend.app.models.user import User
from backend.app.schemas.bootstrap import BootstrapSetup


ph = PasswordHasher()


def perform_bootstrap(
    db: Session,
    input_data: BootstrapSetup
) -> tuple[User, Team]:
    db.add(AppConfig(organization_name=input_data.organization_name))

    normalized_username: str = input_data.username.strip().lower()
    hashed_password: str = ph.hash(input_data.password)
    user = User(
        username=input_data.username,
        username_normalized=normalized_username,
        email=input_data.email,
        password_hash=hashed_password
    ) 
    db.add(user)

    team = Team(name=input_data.team_name)
    db.add(team)

    # Flush both user and team to enable team_member creation
    db.flush()

    team_member = TeamMember(
        user_id=user.id,
        team_id=team.id,
        role=UserRole.OWNER
    )
    db.add(team_member)

    return user, team
