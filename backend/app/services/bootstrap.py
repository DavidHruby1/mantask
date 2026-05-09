from argon2 import PasswordHasher

from sqlalchemy.orm import Session

from backend.app.models.app_config import AppConfig
from backend.app.models.enums import TeamType, UserRole
from backend.app.models.team import Team
from backend.app.models.team_member import TeamMember
from backend.app.models.user import User
from backend.app.schemas.bootstrap import BootstrapSetup


ph = PasswordHasher()


def bootstrap_application(db: Session, input_data: BootstrapSetup) -> User:
    db.add(AppConfig(organization_name=input_data.organization_name))

    normalized_username: str = input_data.username.strip().lower()
    hashed_password: str = ph.hash(input_data.password)
    user = User(
        username=input_data.username,
        username_normalized=normalized_username,
        email=input_data.email,
        password_hash=hashed_password,
    )
    db.add(user)

    db.flush()

    private_team = Team(
        name="Private",
        type=TeamType.PRIVATE,
        private_owner_user_id=user.id,
    )
    db.add(private_team)

    shared_team = Team(name=input_data.team_name)
    db.add(shared_team)

    db.flush()

    private_team_member = TeamMember(
        user_id=user.id,
        team_id=private_team.id,
        role=UserRole.OWNER,
    )
    db.add(private_team_member)

    shared_team_member = TeamMember(
        user_id=user.id,
        team_id=shared_team.id,
        role=UserRole.OWNER,
    )
    db.add(shared_team_member)

    user.last_active_team_id = private_team.id

    return user
