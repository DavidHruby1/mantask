import pytest

from backend.app.error import (
    ApiConflictError,
    ApiInternalServerError,
    InvalidTaskError,
    NoActiveTeamSelectedError,
    TaskAccessDeniedError,
    TaskNotFoundError,
    TeamInactiveError,
    TeamMembershipError,
    TeamNotFoundError,
)
from backend.app.models.enums import TaskStatus
from backend.app.schemas.task import TaskCreate, TaskFilters, TaskQuery, TaskUpdate
from backend.app.services.tasks import TaskService
