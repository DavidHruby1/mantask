from __future__ import annotations
from datetime import datetime, date
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Enum,
    Text,
    func,
    text,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from backend.app.core.db import Base
from backend.app.models.enums import TaskStatus, TaskPriority, TaskEffort, IntEnumType

if TYPE_CHECKING:
    from backend.app.models.team_member import TeamMember
    from backend.app.models.team import Team


class Task(Base):
    __tablename__ = "task"

    __table_args__ = (
        CheckConstraint("position >= 1", name="task_position"),
        CheckConstraint("layer IS NULL OR btrim(layer) <> ''", name="task_layer_not_blank"),
        CheckConstraint("btrim(title) <> ''", name="task_title_not_blank"),
        CheckConstraint("returned_count >= 0", name="task_returned_count_non_negative"),
        CheckConstraint("reopened_count >= 0", name="task_reopened_count_non_negative"),
        CheckConstraint("blocked_count >= 0", name="task_blocked_count_non_negative"),
        CheckConstraint(
            "(status = 'done' AND completed_at IS NOT NULL) OR "
            "(status <> 'done' AND completed_at IS NULL)",
            name="task_completed_at_matches_status",
        ),
        CheckConstraint(
            "(submitted_for_review_at IS NULL) OR (status IN ('review', 'done'))",
            name="task_review_timestamp_only_after_review",
        ),
        CheckConstraint(
            "(should_review = FALSE) OR (reviewer_member_id IS NOT NULL)",
            name="should_review_must_have_reviewer",
        ), 
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    team_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("team.id", ondelete="RESTRICT"),
        nullable=False
    )
    creator_member_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("team_member.id", ondelete="RESTRICT"),
    )
    assignee_member_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("team_member.id", ondelete="RESTRICT"),
    )
    reviewer_member_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("team_member.id", ondelete="RESTRICT"),
    )

    layer: Mapped[str | None] = mapped_column(Text)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[TaskStatus] = mapped_column(
        Enum(
            TaskStatus,
            name="task_status",
            values_callable=lambda e: [item.value for item in e],
            validate_strings=True
        ),
        nullable=False,
        server_default=text("'todo'")
    )
    priority: Mapped[TaskPriority | None] = mapped_column(
        Enum(
            TaskPriority,
            name="task_priority",
            values_callable=lambda e: [item.value for item in e],
            validate_strings=True
        ),
        nullable=True
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    review_date: Mapped[date | None] = mapped_column(Date)
    due_date: Mapped[date | None] = mapped_column(Date)
    effort: Mapped[TaskEffort | None] = mapped_column(
        IntEnumType(TaskEffort),
        nullable=True
    )
    should_review: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
        onupdate=func.now()
    )
    started_working_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    submitted_for_review_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    returned_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("0")
    )
    reopened_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("0")
    )
    blocked_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("0")
    )

    creator: Mapped[TeamMember] = relationship(
        back_populates="created_tasks",
        foreign_keys=[creator_member_id],
    )
    assignee: Mapped[TeamMember] = relationship(
        back_populates="assigned_tasks",
        foreign_keys=[assignee_member_id],
    )
    reviewer: Mapped[TeamMember] = relationship(
        back_populates="reviewing_tasks",
        foreign_keys=[reviewer_member_id],
    )
    team: Mapped[Team] = relationship(back_populates="tasks")