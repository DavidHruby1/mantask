from datetime import datetime

from sqlalchemy import (
    CheckConstraint, 
    DateTime, 
    ForeignKey, 
    Integer, 
    Text, 
    text
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from backend.app.core.db import Base


class UserSession(Base):
    __tablename__ = "user_sessions"

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
    session_token_hash: Mapped[str] = mapped_column(
        Text, 
        nullable=False, 
        unique=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False, 
        server_default=text("now()")
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), 
        nullable=True
    )

    user = relationship("User", back_populates="sessions")
