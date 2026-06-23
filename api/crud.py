"""Database CRUD (Create, Read, Update, Delete) operations.

Manages DB operations for Pastes and associated Files.
"""

import datetime

from sqlalchemy.orm import Session

from . import keygen, models, schemas


def get_db_paste_by_key(db: Session, key: str) -> models.Paste | None:
    """Retrieve a single paste record from the database using its unique identifier key.

    Args:
        db: Database session.
        key: The 4-character unique key representing the paste.

    Returns:
        The models.Paste object if found, otherwise None.
    """
    return db.query(models.Paste).filter(models.Paste.key == key).first()


def create_db_paste(db: Session, paste: schemas.Paste) -> models.Paste:
    """Create a new paste record along with its associated files in the database.

    Generates a unique random key for the paste and calculates its expiry date.

    Args:
        db: Database session.
        paste: The Paste schema containing files list and expiry duration in seconds.

    Returns:
        The newly created models.Paste database record.
    """
    key = keygen.create_unique_random_key(db)

    db_paste = models.Paste(key=key, expiry=paste.expiry)
    db_files = [models.File(text=f.text, kind=f.kind, name=f.name) for f in paste.files]
    db_paste.files.extend(db_files)

    db.add(db_paste)
    db.commit()
    db.refresh(db_paste)
    return db_paste


def delete_expired_pastes(db: Session) -> None:
    """Query the database and delete all paste records whose expiration date has passed.

    Also cascades and deletes associated file records due to relation configurations.

    Args:
        db: Database session.
    """
    now = datetime.datetime.now()

    expired_pastes = db.query(models.Paste).filter(models.Paste.exp_date <= now).all()
    for paste in expired_pastes:
        db.delete(paste)
    db.commit()
