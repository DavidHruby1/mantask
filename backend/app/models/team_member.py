from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Integer,
    ForeignKey,
    Enum,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from backend.app.core.db import Base
from backend.app.models.enums import UserRole

if TYPE_CHECKING:
    from backend.app.models.task import Task
    from backend.app.models.team import Team
    from backend.app.models.user import User


class TeamMember(Base):
    __tablename__ = "team_members"

    __table_args__ = (
        UniqueConstraint("team_id", "user_id", name="uq_team_member_team_user"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    team_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("teams.id", ondelete="RESTRICT"),
        nullable=False,
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("app_users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    role: Mapped[UserRole] = mapped_column(
        Enum(
            UserRole,
            name="team_member_role",
            values_callable=lambda e: [item.value for item in e],
            validate_strings=True
        ),
        nullable=False,
        server_default=text("'member'"),
    )
    joined_at: Mapped[datetime] = mapped_column(
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

    team: Mapped[Team] = relationship(back_populates="members")
    user: Mapped[User] = relationship(back_populates="team_members")
    created_tasks: Mapped[list["Task"]] = relationship(
        "Task",
        back_populates="creator",
        foreign_keys="Task.creator_member_id",
    )
    assigned_tasks: Mapped[list["Task"]] = relationship(
        "Task",
        back_populates="assignee",
        foreign_keys="Task.assignee_member_id",
    )
    reviewing_tasks: Mapped[list["Task"]] = relationship(
        "Task",
        back_populates="reviewer",
        foreign_keys="Task.reviewer_member_id",
    )
