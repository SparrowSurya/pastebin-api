from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .config import get_settings


db_url = get_settings().db_url
connect_args = {}
if db_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(db_url, connect_args=connect_args)

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
