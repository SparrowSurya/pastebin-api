import string
import secrets

from sqlalchemy.orm import Session

from . import crud


def create_random_key(length: int = 4) -> str:
    chars = string.ascii_lowercase + string.digits
    return "".join(secrets.choice(chars) for _ in range(length))


def create_unique_random_key(db: Session) -> str:
    ATTEMPTS = 10
    for _ in range(ATTEMPTS):
        key = create_random_key()
        if crud.get_db_paste_by_key(db, key) is None:
            return key
    raise RuntimeError(f"Failed to generate unique random key in {ATTEMPTS}attempts.")