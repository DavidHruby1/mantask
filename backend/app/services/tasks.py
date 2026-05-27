from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.app.models.user_session import UserSession
from backend.app.repositories.teams import (
    get_team_by_id,
    get_team_member_by_id,
    is_team_member,
)
from backend.app.repositories.tasks import insert_task, get_last_task_position
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

    if not is_team_member(db, team_id, session.user.id):
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
    if not is_team_member(db, team_id, user_id):
        return False

    team = get_team_by_id(db, team_id)
    if team is None:
        return False
    if not team.is_active:
        return False

    return True
    

def create_task(db, team_id, creator_member_id, payload):
    if get_team_member_by_id(db, team_id, creator_member_id) is None:
        raise HTTPException(status_code=400, detail="Invalid creator_member_id")

    if payload.assignee_member_id is not None:
        assignee_member = get_team_member_by_id(db, team_id, payload.assignee_member_id)
        if assignee_member is None:
            raise HTTPException(status_code=400, detail="Invalid assignee_member_id")

    if payload.reviewer_member_id is not None:
        reviewer_member = get_team_member_by_id(db, team_id, payload.reviewer_member_id)
        if reviewer_member is None:
            raise HTTPException(status_code=400, detail="Invalid reviewer_member_id")

    filters = TaskFilters(
        team_id=team_id, 
        statuses=[payload.status],
        assignee_member_id=None
    )

    last_task_position = get_last_task_position(db, filters)

    if last_task_position is None:
        position = 0
    else:
        position = last_task_position + 1

    task = insert_task(db, team_id, creator_member_id, payload, position)
    return task
