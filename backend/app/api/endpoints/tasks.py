from fastapi import APIRouter, Query

from backend.app.api.dependencies import DbSessionDep, CurrentSessionDep
from backend.app.models.enums import TaskStatus
from backend.app.schemas.task import TaskListQuery, TaskRead
from backend.app.services.tasks import get_tasks_for_user


router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/", response_model=list[TaskRead])
def get_tasks(
    db: DbSessionDep,
    session: CurrentSessionDep,
    team_id: int | None = Query(default=None),
    statuses: list[TaskStatus] | None = Query(default=None),
    assignee_member_id: int | None = Query(default=None),
) -> list[TaskRead]:
    query = TaskListQuery(
        team_id=team_id,
        statuses=statuses,
        assignee_member_id=assignee_member_id,
    )
    return get_tasks_for_user(db, session, query)
