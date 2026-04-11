from datetime import datetime

from sqlalchemy import (
    Integer,
    SmallInteger,
    DateTime,
    CheckConstraint,
    String,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.core.db import Base


class AppConfig(Base):
    __tablename__ = "app_config"

    __table_args__ = (
        CheckConstraint("id = 1", name="app_config_singleton"),
        CheckConstraint("in_progress_limit > 0", name="app_config_in_progress_limit"),
        CheckConstraint("btrim(organization_name) <> ''", name="app_config_name_not_blank"),
    )

    id: Mapped[int] = mapped_column(
        SmallInteger, 
        primary_key=True,
        server_default=text("1")
    )
    organization_name: Mapped[str] = mapped_column(String(200), nullable=False)
    initialized_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False, 
        server_default=text("now()")
    )
    in_progress_limit: Mapped[int] = mapped_column(
        Integer, 
        nullable=False,
        server_default=text("2")
    )
