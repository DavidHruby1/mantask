from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    APP_NAME: str = "Mantask"
    DEBUG: bool = True
    DATABASE_URL: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/mantask"
    )
    SECRET_KEY: str = Field(
        default="change-me-in-production"
    )
    SESSION_COOKIE_NAME: str = "session_token"
    SESSION_EXPIRE_DAYS: int = 30
    DEFAULT_TIMEZONE: str = "UTC"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()