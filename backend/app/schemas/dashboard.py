from pydantic import BaseModel

from backend.app.schemas.task import TaskRead


class CurrentTeamInfo(BaseModel):
    id: int
    name: str


class DashboardColumnCounts(BaseModel):
    todo: int
    in_progress: int
    review: int
    done: int


class DashboardRead(BaseModel):
    current_team: CurrentTeamInfo
    my_tasks_only: bool
    in_progress_limit: int
    counts: DashboardColumnCounts

    todo: list[TaskRead]
    in_progress: list[TaskRead]
    review: list[TaskRead]
    done: list[TaskRead]