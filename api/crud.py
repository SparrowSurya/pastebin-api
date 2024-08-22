import datetime
from typing import optional

from sqlalchemy.orm import Session

from . import keygen, models, schemas


def create_unique_random_key(db: Session) -> str:
    key = keygen.create_random_key()
    while get_db_paste_by_key(db, key):
        key = keygen.create_random_key()
    return key


def get_db_paste_by_key(db: Session, key: str) -> optional[schemas.PasteInfo]:
    return db.query(models.Paste).filter(models.Paste.key==key).first()


def create_db_paste(db: Session, paste: schemas.Paste) -> schemas.PasteInfo:
    key = create_unique_random_key(db)

    db_paste = models.Paste(key=key, expiry=paste.expiry)
    db_files = [models.File(text=f.text, kind=f.kind, name=f.name) for f in paste.files]
    db_paste.files.extend(db_files)

    db.add(db_paste)
    db.commit()
    db.refresh(db_paste)
    return db_paste


def delete_expired_pastes(db: Session):
    now = datetime.datetime.now()

    expired_pastes = db.query(models.Paste).filter(models.Paste.exp_date <= now).all()
    for paste in expired_pastes:
        db.delete(paste)
    db.commit()
