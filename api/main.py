import asyncio
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Request
from sqlalchemy.orm import Session

from . import schemas, models, crud
from .config import get_settings
from .database import SessionLocal, engine, get_db
from .background_tasks import delete_expired_paste_task


@asynccontextmanager
async def lifespan(app: FastAPI):
    interval = float(get_settings().interval)
    db = SessionLocal()
    asyncio.create_task(delete_expired_paste_task(interval, db))
    yield
    db.close()


app = FastAPI(lifespan=lifespan)
models.Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return "Welcome to pastebin API."


@app.post("/")
def create_paste(paste: schemas.Paste, db: Session = Depends(get_db)):
    try:
        db_paste = crud.create_db_paste(db, paste)
    except RuntimeError as error:
        raise HTTPException(status_code=500, detail=str(error))

    url =  get_settings().base_url + f"/{db_paste.key}"
    return url


@app.get("/{key}", response_model=schemas.PasteInfo)
def get_paste(key: str, request: Request, db: Session = Depends(get_db)) -> models.Paste:
    if db_paste := crud.get_db_paste_by_key(db, key):
        return db_paste
    raise HTTPException(status_code=404, detail=f"{request.url} does not exist.")
