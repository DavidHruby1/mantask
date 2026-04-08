from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Integer,
    Text,
    Boolean,
    func,
    text,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from backend.app.core.db import Base


class User(Base):
    __tablename__ = "app_users"

    __table_args__ = (
        CheckConstraint("btrim(username) <> ''", name="user_username_not_blank"),
        CheckConstraint("btrim(username_normalized) <> ''", name="user_username_normalized_not_blank"),
        CheckConstraint("btrim(email) <> ''", name="user_email_not_blank"),
        CheckConstraint("btrim(password_hash) <> ''", name="user_password_hash_not_blank"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(Text, nullable=False)
    username_normalized: Mapped[str] = mapped_column(
        Text, 
        nullable=False,
        unique=True
    )
    email: Mapped[str] = mapped_column(
        Text, 
        nullable=False, 
        unique=True
    )
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("TRUE")
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
    profile_picture_path: Mapped[str | None] = mapped_column(Text)

    team_members = relationship("TeamMember", back_populates="user")
    sessions = relationship("AuthSession", back_populates="user")
