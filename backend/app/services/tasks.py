from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.app.models.user_session import UserSession
from backend.app.repositories.teams import (
    get_team_by_id,
    get_team_member,
    get_team_member_by_id,
)
from backend.app.schemas.task import TaskFilters, TaskListQuery


def build_task_filters(
    db: Session,
    session: UserSession,
    query: TaskListQuery,
) -> TaskFilters:
    team_id = query.team_id
    if team_id is None:
        if not session.user.last_active_team_id:
            raise HTTPException(status_code=403, detail="No active team")
        team_id = session.user.last_active_team_id

    team = get_team_by_id(db, team_id)
    if team is None or not team.is_active:
        raise HTTPException(status_code=403, detail="No active team")

    team_member = get_team_member(db, team_id, session.user.id)
    if team_member is None:
        raise HTTPException(status_code=403, detail="Not a team member")

    assignee_member_id = query.assignee_member_id
    if assignee_member_id is not None:
        assignee_member = get_team_member_by_id(db, team_id, assignee_member_id)
        if assignee_member is None:
            raise HTTPException(status_code=400, detail="Invalid assignee_member_id")

    return TaskFilters.model_validate(query.model_dump() | {"team_id": team_id})
