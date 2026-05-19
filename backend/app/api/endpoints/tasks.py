from typing import Annotated

from fastapi import APIRouter, Query

from backend.app.api.dependencies import DbSessionDep, CurrentSessionDep
from backend.app.schemas.task import TaskListQuery, TaskRead
from backend.app.services.tasks import get_tasks_for_user


router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/", response_model=list[TaskRead])
def get_tasks(
    db: DbSessionDep,
    session: CurrentSessionDep,
    query: Annotated[TaskListQuery, Query()],
) -> list[TaskRead]:
    return get_tasks_for_user(db, session, query)
