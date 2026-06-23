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

    Starts with a 4-character key. If it encounters collisions (every 5 failed
    attempts), it increases the key length by 1 to expand the key space.
    If it reaches a length of 8 and still fails (which is mathematically
    virtually impossible), it raises a RuntimeError.

    Args:
        db: Database session.

    Returns:
        A unique random alphanumeric key.

    Raises:
        RuntimeError: If unique key cannot be generated.
    """
    length = 4
    attempts = 0
    total_attempts = 0
    MAX_TOTAL_ATTEMPTS = 25

    while total_attempts < MAX_TOTAL_ATTEMPTS:
        key = create_random_key(length)
        if crud.get_db_paste_by_key(db, key) is None:
            return key
        attempts += 1
        total_attempts += 1
        if attempts >= 5:
            length += 1
            attempts = 0

    raise RuntimeError(
        "Failed to generate unique random key after expanding search space."
    )
