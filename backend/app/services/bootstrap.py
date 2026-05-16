from argon2 import PasswordHasher

from sqlalchemy.orm import Session

from backend.app.models.enums import UserRole
from backend.app.models.user import User
from backend.app.repositories.bootstraps import create_app_config
from backend.app.repositories.teams import (
    create_private_team,
    create_team,
    create_team_member,
)
from backend.app.repositories.users import create_user
from backend.app.schemas.bootstrap import BootstrapSetup


ph = PasswordHasher()


def bootstrap_application(db: Session, input_data: BootstrapSetup) -> User:
    create_app_config(db, input_data.organization_name)

    normalized_username = input_data.username.strip().lower()
    hashed_password = ph.hash(input_data.password)
    user = create_user(
        db,
        username=input_data.username,
        username_normalized=normalized_username,
        email=input_data.email,
        password_hash=hashed_password,
    )

    db.flush()

    private_team = create_private_team(db, owner_user_id=user.id)
    shared_team = create_team(db, name=input_data.team_name)

    db.flush()

    create_team_member(
        db,
        user_id=user.id,
        team_id=private_team.id,
        role=UserRole.OWNER,
    )
    create_team_member(
        db,
        user_id=user.id,
        team_id=shared_team.id,
        role=UserRole.OWNER,
    )

    user.last_active_team_id = private_team.id
    return user
