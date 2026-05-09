from datetime import datetime

from sqlalchemy import (
    Boolean,
    Integer,
    Text,
    DateTime,
    CheckConstraint,
    UniqueConstraint,
    ForeignKey,
    Enum,
    func,
    text
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from backend.app.core.db import Base
from backend.app.models.enums import TeamType


class Team(Base):
    __tablename__ = "teams"

    __table_args__ = (
        CheckConstraint("btrim(name) <> ''", name="team_name_not_blank"),
        CheckConstraint(
            "(\"type\" = 'private' AND private_owner_user_id IS NOT NULL) OR "
            "(\"type\" = 'team' AND private_owner_user_id IS NULL)",
            name="team_type_owner_consistency",
        ),
        UniqueConstraint("private_owner_user_id", name="uq_team_private_owner"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[TeamType] = mapped_column(
        Enum(
            TeamType,
            name="team_type",
            values_callable=lambda e: [item.value for item in e],
            validate_strings=True,
        ),
        nullable=False,
        server_default=text("'team'"),
    )
    private_owner_user_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("app_users.id", ondelete="RESTRICT"),
        nullable=True,
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
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("TRUE")
    )

    members = relationship("TeamMember", back_populates="team")
    tasks = relationship("Task", back_populates="team")
