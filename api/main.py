from fastapi import Depends, FastAPI, HTTPException, Request
from sqlalchemy.orm import Session

from . import schemas, models, crud
from .config import get_settings
from .database import engine, SessionLocal


app = FastAPI()
models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return "Welcome to pastebin API."


@app.post("/")
def create_paste(paste: schemas.Paste, db: Session = Depends(get_db)):
    db_paste = crud.create_db_paste(db, paste)
    url =  get_settings().base_url + f"/{db_paste.key}"
    return url


@app.get("/{key}", response_model=schemas.PasteInfo)
def get_paste(key: str, request: Request, db: Session = Depends(get_db)) -> str:
    if db_paste := crud.get_db_paste_by_key(db, key):
        return db_paste
    else:
        raise HTTPException(status_code=404, detail=f"{request.url} does not exist.")
