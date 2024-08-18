import os
import logging
from pydantic_settings import BaseSettings
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Settings for the application."""

    env_name: str = os.environ["ENV_NAME"]
    base_url: str = os.environ["BASE_URL"]
    db_url: str = os.environ["DB_URL"]

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    """Get the application settings."""
    settings = Settings()
    logging.info(f"Loading settings for {settings.env_name}")
    return settings
