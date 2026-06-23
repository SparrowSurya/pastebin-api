import logging
import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

# Detect execution environment
is_vercel = os.environ.get("VERCEL") == "1"
env_file_name = None if is_vercel else ".env.dev"


class Settings(BaseSettings):
    """Settings for the application."""

    env_name: str = "prod" if is_vercel else "dev"
    base_url: str = "127.0.0.1:8000"
    db_url: str = "sqlite:///./db.sqlite3"
    interval: float = 3600.0

    model_config = SettingsConfigDict(env_file=env_file_name, extra="ignore")


@lru_cache
def get_settings() -> Settings:
    """Get the application settings."""
    settings = Settings()
    logger.info(f"Loading settings for {settings.env_name}")
    return settings
