"""Key generation utility module.

Generates random, unique strings used as lookup keys for pastes.
"""

import secrets
import string

from sqlalchemy.orm import Session

from . import crud


def create_random_key(length: int = 4) -> str:
    """Generate a random alphanumeric string of the specified length.

    Args:
        length: Number of characters in the generated key. Default is 4.

    Returns:
        A randomly generated string of lowercase letters and digits.
    """
    chars = string.ascii_lowercase + string.digits
    return "".join(secrets.choice(chars) for _ in range(length))


def create_unique_random_key(db: Session) -> str:
    """Generate a random alphanumeric key that is unique in the database.

    Tries up to 10 times to find an unused key.

    Args:
        db: Database session.

    Returns:
        A unique 4-character key.

    Raises:
        RuntimeError: If all generation attempts conflict with existing records.
    """
    ATTEMPTS = 10
    for _ in range(ATTEMPTS):
        key = create_random_key()
        if crud.get_db_paste_by_key(db, key) is None:
            return key
    raise RuntimeError(f"Failed to generate unique random key in {ATTEMPTS} attempts.")
