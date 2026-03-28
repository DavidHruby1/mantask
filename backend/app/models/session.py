from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Text,
    func,
    text
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from backend.app.core.db import Base


class Session(Base):
    __tablename__ = "sessions"

    __table_args__ = (
        CheckConstraint("expires_at > created_at", name="check_expires_at"),
        CheckConstraint("btrim(token_hash) <> ''", name="session_token_hash_not_blank"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("app_users.id", ondelete="RESTRICT"),
        nullable=False
    )
    token_hash: Mapped[str] = mapped_column(
        Text, 
        nullable=False, 
        unique=True
    )
    current_team_id: Mapped[int | None] = mapped_column( # backend will always set team
        Integer,
        ForeignKey("teams.id", ondelete="RESTRICT"),
        nullable=False
    )    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False, 
        server_default=text("now()")
    )
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False,
        server_default=text("now()"),
        onupdate=func.now() 
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False,
        server_default=text("now() + INTERVAL '30 days'")
    )
    revoked_at: Mapped[datetime | None] = mapped_column( # If user is_active is False, then revoked_at will be set to now()
        DateTime(timezone=True),
        nullable=True
    )
    
    user = relationship("User", back_populates="sessions")