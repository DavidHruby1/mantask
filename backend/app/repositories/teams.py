from sqlalchemy import exists, select
from sqlalchemy.orm import Session

from backend.app.models.app_config import AppConfig
from backend.app.models.team import Team
from backend.app.models.enums import TeamType, UserRole
from backend.app.models.user import User
from backend.app.models.team_member import TeamMember


def create_team(db: Session, name: str) -> Team:
    team = Team(name=name)
    db.add(team)
    return team


def create_private_team(db: Session, owner_user_id: int) -> Team:
    team = Team(
        name="Private",
        type=TeamType.PRIVATE,
        private_owner_user_id=owner_user_id,
    )
    db.add(team)
    return team


def create_team_member(
    db: Session,
    user_id: int,
    team_id: int,
    role: UserRole,
) -> TeamMember:
    team_member = TeamMember(
        user_id=user_id,
        team_id=team_id,
        role=role,
    )
    db.add(team_member)
    return team_member


def get_private_team_id(db: Session, user: User) -> int | None:
    private_team = db.scalar(
        select(Team).where(
            Team.type == TeamType.PRIVATE,
            Team.private_owner_user_id == user.id,
            Team.is_active,
        )
    )
    return private_team.id if private_team is not None else None


def get_team_by_id(db: Session, team_id: int) -> Team | None:
    team = db.get(Team, team_id)
    return team


def get_team_member(db: Session, team_id: int, user_id: int) -> TeamMember | None:
    team_member = db.scalar(
        select(TeamMember).where(
            TeamMember.team_id == team_id,
            TeamMember.user_id == user_id,
        ).limit(1)
    )
    return team_member


def is_team_member(db: Session, team_id: int, user_id: int) -> bool:
    return bool(
        db.scalar(
            select(
                exists().where(
                    TeamMember.team_id == team_id,
                    TeamMember.user_id == user_id,
                )
            )
        )
    )


def get_team_member_by_id(db: Session, team_id: int, member_id: int) -> TeamMember | None:
    team_member = db.scalar(
        select(TeamMember).where(
            TeamMember.team_id == team_id,
            TeamMember.id == member_id,
        ).limit(1)
    )
    return team_member

def get_in_progress_limit(db: Session) -> int | None:
    app_config = db.get(AppConfig, 1)
    in_progress_limit = app_config.in_progress_limit if app_config is not None else None
    return in_progress_limit 
