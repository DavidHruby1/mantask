from fastapi import APIRouter, HTTPException, Query

from sqlalchemy import select

from backend.app.api.dependencies import CurrentSessionDep, DbSessionDep
from backend.app.models.enums import TaskStatus
from backend.app.models.task import Task
from backend.app.models.team import Team
from backend.app.models.team_member import TeamMember
from backend.app.schemas.dashboard import DashboardColumnCounts, DashboardRead
from backend.app.schemas.task import TaskRead


router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/{team_id}", response_model=DashboardRead)
def get_dashboard(
    team_id: int,
    db: DbSessionDep,
    session: CurrentSessionDep,
    my_tasks_only: bool = Query(default=False),
) -> DashboardRead:
    current_team_member = db.scalar(
        select(TeamMember).where(
            TeamMember.team_id == team_id,
            TeamMember.user_id == session.user.id,
        )
    )
    if current_team_member is None:
        raise HTTPException(status_code=404, detail="Team not found")

    team = db.get(Team, team_id)
    if team is None or not team.is_active:
        raise HTTPException(status_code=404, detail="Team not found")

    stmt = select(Task).where(Task.team_id == team_id)
    if my_tasks_only:
        stmt = stmt.where(Task.assignee_member_id == current_team_member.id)

    tasks: list[Task] = list(db.scalars(stmt).all())

    column_counts: dict[TaskStatus, int] = {
        TaskStatus.TODO: 0,
        TaskStatus.IN_PROGRESS: 0,
        TaskStatus.REVIEW: 0,
        TaskStatus.DONE: 0,
    }
    kanban_data: dict[TaskStatus, list[TaskRead]] = {
        TaskStatus.TODO: [],
        TaskStatus.IN_PROGRESS: [],
        TaskStatus.REVIEW: [],
        TaskStatus.DONE: [],
    }

    for task in tasks:
        column_counts[task.status] += 1
        kanban_data[task.status].append(TaskRead.model_validate(task))

    return DashboardRead(
        counts=DashboardColumnCounts(
            todo=column_counts[TaskStatus.TODO],
            in_progress=column_counts[TaskStatus.IN_PROGRESS],
            review=column_counts[TaskStatus.REVIEW],
            done=column_counts[TaskStatus.DONE],
        ),
        todo=kanban_data[TaskStatus.TODO],
        in_progress=kanban_data[TaskStatus.IN_PROGRESS],
        review=kanban_data[TaskStatus.REVIEW],
        done=kanban_data[TaskStatus.DONE],
    )
