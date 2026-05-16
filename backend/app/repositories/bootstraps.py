from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.app_config import AppConfig


def create_app_config(db: Session, organization_name: str) -> AppConfig:
    app_config = AppConfig(organization_name=organization_name)
    db.add(app_config)
    return app_config


def is_bootstrapped(db: Session) -> bool:
    return db.scalar(select(AppConfig.id).limit(1)) is not None
