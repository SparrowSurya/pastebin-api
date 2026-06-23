import logging

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Settings for the application."""

    env_name: str = "development"
    base_url: str = "127.0.0.1:8000"
    db_url: str = "sqlite:///./db.sqlite3"
    interval: float = 3600.0

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings() -> Settings:
    """Get the application settings."""
    settings = Settings()
    logger.info(f"Loading settings for {settings.env_name}")
    return settings
