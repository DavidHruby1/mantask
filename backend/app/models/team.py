from datetime import datetime

from sqlalchemy import (
    Boolean,
    Index,
    Integer,
    Text,
    DateTime,
    CheckConstraint,
    text
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from backend.app.core.db import Base


class Team(Base):
    __tablename__ = "team"

    __table_args__ = (
        CheckConstraint("btrim(name) <> ''", name="team_name_not_blank"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()")
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("TRUE")
    )

    members = relationship("TeamMember", back_populates="team")
    tasks = relationship("Task", back_populates="team")