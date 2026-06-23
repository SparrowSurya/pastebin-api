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
    logger.info("Application lifespan started!")
    interval = float(get_settings().interval)
    db = SessionLocal()
    delete_task = asyncio.create_task(delete_expired_paste_task(interval, db))
    yield
    db.close()
    delete_task.cancel()
    logger.info("Application lifespan ended!")


app = FastAPI(lifespan=lifespan)
models.Base.metadata.create_all(bind=engine)


@app.get("/")
def root() -> str:
    return "Welcome to pastebin API."


@app.post("/")
def create_paste(paste: schemas.Paste, db: Session = Depends(get_db)) -> str:
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
    if db_paste := crud.get_db_paste_by_key(db, key):
        return db_paste
    raise HTTPException(status_code=404, detail=f"{request.url} does not exist.")
