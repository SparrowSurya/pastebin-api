"""Main API module containing FastAPI endpoints, routers, and application lifespans."""

import asyncio
import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Request
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .background_tasks import delete_expired_paste_task
from .config import get_settings
from .database import SessionLocal, engine, get_db

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manages application startup and shutdown lifecycle events.

    Initializes the database session for periodic background tasks, triggers
    the task loop, and cancels/closes resources on application exit.
    """
    logger.info("Application lifespan started!")
    interval = float(get_settings().interval)
    db = SessionLocal()
    delete_task = asyncio.create_task(delete_expired_paste_task(interval, db))
    yield
    db.close()
    delete_task.cancel()
    logger.info("Application lifespan ended!")


# Initialize the FastAPI application and set up database tables
app = FastAPI(lifespan=lifespan)
models.Base.metadata.create_all(bind=engine)


@app.get("/")
def root() -> str:
    """Root endpoint welcoming users to the service."""
    return "Welcome to pastebin API."


@app.post("/")
def create_paste(paste: schemas.Paste, db: Session = Depends(get_db)) -> str:
    """Create a new paste containing one or more files.

    Args:
        paste: Body containing files list and expiry duration in seconds.
        db: Injected database session.

    Returns:
        The generated unique key of the created paste.

    Raises:
        HTTPException: 500 error if key generation fails.
    """
    try:
        db_paste = crud.create_db_paste(db, paste)
    except RuntimeError as error:
        logger.exception(error)
        raise HTTPException(status_code=500, detail=str(error))

    return db_paste.key


@app.get("/{key}", response_model=schemas.PasteInfo)
def get_paste(
    key: str, request: Request, db: Session = Depends(get_db)
) -> models.Paste:
    """Retrieve an active paste and its associated files by its unique key.

    Args:
        key: The unique identifier key of the paste.
        request: Request instance to build correct error URLs.
        db: Injected database session.

    Returns:
        The models.Paste database record.

    Raises:
        HTTPException: 404 error if paste does not exist.
    """
    if db_paste := crud.get_db_paste_by_key(db, key):
        return db_paste
    raise HTTPException(status_code=404, detail=f"{request.url} does not exist.")
