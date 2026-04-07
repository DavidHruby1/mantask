from sqlalchemy import (
    Integer,
    SmallInteger,
    CheckConstraint,
    Text,
    text,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

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
        server_default=text("1"))
    organization_name: Mapped[str] = mapped_column(Text, nullable=False)
    in_progress_limit: Mapped[int] = mapped_column(
        Integer, 
        nullable=False,
        server_default=text("2")
    )
