from typing import Annotated

from fastapi import APIRouter, Query

from backend.app.api.dependencies import DbSessionDep, CurrentSessionDep
from backend.app.schemas.task import TaskBulkDeleteQuery, TaskListQuery, TaskRead
from backend.app.repositories.tasks import find_tasks
from backend.app.services.tasks import build_task_filters


router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/", response_model=list[TaskRead])
def get_tasks(
    db: DbSessionDep,
    session: CurrentSessionDep,
    query: Annotated[TaskListQuery, Query()],
) -> list[TaskRead]:
    filters = build_task_filters(db, session, query)
    tasks = find_tasks(db, filters)
    return [TaskRead.model_validate(task) for task in tasks]


@router.get("/{task_id}", response_model=TaskRead)
def get_task(
    db: DbSessionDep,
    session: CurrentSessionDep,
    task_id: int,
) -> TaskRead:
    pass


@router.post("/", response_model=TaskRead)
def create_task():
    pass


@router.patch("/{task_id}", response_model=TaskRead)
def update_task(
    db: DbSessionDep,
    session: CurrentSessionDep,
    task_id: int,
):
    pass


# Both deletes will return status code 204, nothing else
@router.delete("/")
def delete_column_tasks(
    db: DbSessionDep,
    session: CurrentSessionDep,
    query: Annotated[TaskBulkDeleteQuery, Query()],
):
    pass


@router.delete("/{task_id}")
def delete_task(
    db: DbSessionDep,
    session: CurrentSessionDep,
    task_id: int,
):
    pass
