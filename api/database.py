"""Database connection and session helper module.

Sets up the SQLAlchemy engine, configures options for SQLite/other databases,
and defines a context generator for managing database sessions.
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .config import get_settings

# Retrieve configuration database URL
db_url = get_settings().db_url

# Configure engine connection arguments.
# SQLite requires check_same_thread=False for FastAPI concurrency.
connect_args = {}
if db_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False

# Instantiate the SQLAlchemy database engine
engine = create_engine(db_url, connect_args=connect_args)

# Create a session maker factory linked to the engine
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Generator[Session, None, None]:
    """Dependency injection generator to supply a database session for a single request.

    Guarantees the connection is closed after the request is processed.

    Yields:
        An active SQLAlchemy database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
