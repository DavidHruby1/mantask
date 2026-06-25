from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.app_config import AppConfig


def create_app_config(db: Session, organization_name: str) -> AppConfig:
    app_config = AppConfig(organization_name=organization_name)
    db.add(app_config)
    return app_config


def is_bootstrapped(db: Session) -> bool:
    return db.scalar(select(AppConfig.id).limit(1)) is not None


def get_in_progress_limit(db: Session) -> int | None:
    app_config = db.get(AppConfig, 1)
    in_progress_limit = app_config.in_progress_limit if app_config is not None else None
    return in_progress_limit 
