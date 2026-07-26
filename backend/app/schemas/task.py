from typing import Self
from datetime import (
    date,
    datetime
)

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from backend.app.models.enums import TaskEffort, TaskPriority, TaskStatus


class TaskCreate(BaseModel):
    """Validate task creation input, defaulting new work to the backlog column."""

    assignee_member_id: int | None = None
    reviewer_member_id: int | None = None

    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=32000)
    layer: str | None = Field(default=None, max_length=64)
    priority: TaskPriority | None = None
    review_date: date | None = None
    due_date: date | None = None
    effort: TaskEffort | None = None
    should_review: bool = True
    status: TaskStatus = TaskStatus.BACKLOG

    @field_validator("title")
    @classmethod
    def validate_title(cls, title: str) -> str:
        if title.strip() == "":
            raise ValueError("Title cannot be empty or whitespace")
        return title.strip()

    @field_validator("layer")
    @classmethod
    def normalize_layer(cls, layer: str | None) -> str | None:
        if layer is None:
            return None
        if layer.strip() == "":
            raise ValueError("Layer cannot be empty or whitespace")
        return layer.lower().strip()

    @field_validator("review_date", "due_date")
    @classmethod
    def validate_dates(cls, date_value: date | None) -> date | None:
        if date_value is not None and date_value < date.today():
            raise ValueError("Dates cannot be in the past")
        return date_value

    @field_validator("status")
    @classmethod
    def validate_status(cls, status: TaskStatus) -> TaskStatus:
        """Restrict creation to entry statuses; later lifecycle changes belong to task policy."""
        if status not in TaskStatus:
            raise ValueError("Invalid status")
        if status not in [TaskStatus.BACKLOG, TaskStatus.TODO, TaskStatus.IN_PROGRESS]:
            raise ValueError("Status must be BACKLOG, TODO or IN_PROGRESS")
        return status

    @model_validator(mode="after")
    def validate_review(self) -> Self:
        if not self.should_review and self.review_date is not None:
            raise ValueError("Task with no review cannot have a review date")
        if self.should_review and self.reviewer_member_id is None:
            raise ValueError("Review must have a reviewer")
        if not self.should_review and self.reviewer_member_id is not None:
            raise ValueError("Review cannot not have a reviewer")
        return self


class TaskUpdate(BaseModel):
    assignee_member_id: int | None = None 
    reviewer_member_id: int | None = None

    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=32000)
    layer: str | None = Field(default=None, max_length=64)
    priority: TaskPriority | None = None
    review_date: date | None = None
    due_date: date | None = None
    effort: TaskEffort | None = None
    should_review: bool | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, title: str | None) -> str | None:
        if title is None:
            return None
        if title.strip() == "":
            raise ValueError("Title cannot be empty or whitespace")
        return title.strip()

    @field_validator("layer")
    @classmethod
    def normalize_layer(cls, layer: str | None) -> str | None:
        if layer is None:
            return None
        if layer.strip() == "":
            raise ValueError("Layer cannot be empty or whitespace")
        return layer.lower().strip()

    @field_validator("review_date", "due_date")
    @classmethod
    def validate_dates(cls, date_value: date | None) -> date | None:
        if date_value is not None and date_value < date.today():
            raise ValueError("Dates cannot be in the past")
        return date_value

    @model_validator(mode="before")
    @classmethod
    def reject_null_required_fields(cls, data):
        """Reject explicit nulls that would violate required task columns."""
        if (not isinstance(data, dict)):
            return data
        if "title" in data and data["title"] is None:
            raise ValueError("Title cannot be null")
        if "should_review" in data and data["should_review"] is None:
            raise ValueError("Should review cannot be null")
        return data


class TaskMove(BaseModel):
    target_status: TaskStatus
    anchor_task_id: int | None = None


class TaskDelete(BaseModel):
    id: int


class TaskRead(BaseModel):
    """Expose persisted task state while matching the database's positive-position contract."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    team_id: int
    creator_member_id: int
    assignee_member_id: int | None = None
    reviewer_member_id: int | None = None

    title: str
    description: str | None = None
    layer: str | None = None
    priority: TaskPriority | None = None
    review_date: date | None = None
    due_date: date | None = None
    effort: TaskEffort | None = None
    should_review: bool
    status: TaskStatus
    position: int = Field(..., ge=1)
    created_at: datetime
    updated_at: datetime
    started_working_at: datetime | None = None
    submitted_for_review_at: datetime | None = None
    completed_at: datetime | None = None
    returned_count: int
    reopened_count: int
    blocked_count: int


class TaskFilterFields(BaseModel):
    statuses: list[TaskStatus] = Field(default_factory=list)
    assignee_member_id: int | None = None


class TaskQuery(TaskFilterFields):
    team_id: int | None = None


class TaskFilters(TaskFilterFields):
    team_id: int
