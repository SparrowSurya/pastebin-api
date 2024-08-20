from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .config import get_settings


engine = create_engine(get_settings().db_url)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
