from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.app.models.user_session import UserSession
from backend.app.repositories.teams import (
    get_team_by_id,
    get_team_member,
    get_team_member_by_id,
)
from backend.app.schemas.task import TaskFilters, TaskListQuery
from backend.app.models.enums import TaskView


def resolve_task_list_filters(
    db: Session,
    session: UserSession,
    query: TaskListQuery,
) -> TaskFilters:
    if query.view == TaskView.KANBAN and query.statuses is not None:
        raise HTTPException(status_code=400, detail="Invalid statuses for kanban view")

    team_id = query.team_id
    if team_id is None:
        if not session.user.last_active_team_id:
            raise HTTPException(status_code=409, detail="No active team selected")
        team_id = session.user.last_active_team_id

    team = get_team_by_id(db, team_id)
    if team is None:
        raise HTTPException(status_code=404, detail="Team not found")

    team_member = get_team_member(db, team_id, session.user.id)
    if team_member is None:
        raise HTTPException(status_code=404, detail="Team not found")

    if not team.is_active:
        raise HTTPException(status_code=409, detail="Team is inactive")

    assignee_member_id = query.assignee_member_id
    if assignee_member_id is not None:
        assignee_member = get_team_member_by_id(db, team_id, assignee_member_id)
        if assignee_member is None:
            raise HTTPException(status_code=400, detail="Invalid assignee_member_id")

    return TaskFilters(
        team_id=team_id,
        statuses=query.statuses,
        assignee_member_id=query.assignee_member_id,
    )


def can_view_task(db: Session, team_id: int, user_id: int) -> bool:
    team_member = get_team_member(db, team_id, user_id)
    if team_member is None:
        return False

    team = get_team_by_id(db, team_id)
    if not team.is_active:
        return False

    return True
    
