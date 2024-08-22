import logging

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """Settings for the application."""

    env_name: str
    base_url: str
    db_url: str
    interval: float

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings() -> Settings:
    """Get the application settings."""
    settings = Settings()
    logging.info(f"Loading settings for {settings.env_name}")
    return settings
