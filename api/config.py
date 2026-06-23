"""Configuration management module.

Handles environment-based application settings loading using Pydantic Settings.
Loads development settings from `.env.dev` and uses direct env variables on Vercel.
"""

import logging
import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

# Detect execution environment (Vercel sets VERCEL=1)
is_vercel = os.environ.get("VERCEL") == "1"
env_file_name = None if is_vercel else ".env.dev"


class Settings(BaseSettings):
    """Application settings schema and loader.

    Environment variables matching these field names (case-insensitive)
    will automatically override the default values.
    """

    env_name: str = "prod" if is_vercel else "dev"
    """Name of the active deployment environment (e.g. 'dev', 'prod')."""

    base_url: str = "127.0.0.1:8000"
    """Base URL of the running API service."""

    db_url: str = "sqlite:///./db.sqlite3"
    """SQLAlchemy-compatible database connection URL."""

    interval: float = 3600.0
    """Cleanup interval in seconds for deleting expired pastes."""

    model_config = SettingsConfigDict(env_file=env_file_name, extra="ignore")


@lru_cache
def get_settings() -> Settings:
    """Fetch the cached application settings singleton instance.

    Returns:
        The instantiated Settings object loaded with environment configs.
    """
    settings = Settings()
    logger.info(f"Loading settings for {settings.env_name}")
    return settings
