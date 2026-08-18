from fastapi import APIRouter

from backend.app.api.dependencies import CurrentSessionDep, DbSessionDep
from backend.app.repositories.teams import get_teams_by_user_id
from backend.app.schemas.team import TeamRead


router = APIRouter(prefix="/teams", tags=["teams"])


@router.get("", response_model=list[TeamRead])
def get_current_user_teams(
    db: DbSessionDep, session: CurrentSessionDep
) -> list[TeamRead]:
    teams = get_teams_by_user_id(db, session.user_id)
    return [TeamRead.model_validate(team) for team in teams]
