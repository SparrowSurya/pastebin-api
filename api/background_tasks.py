"""Module for handling asynchronous background tasks.

Mainly handles cleaning up expired pastes.
"""

import asyncio
import logging

from sqlalchemy.orm import Session

from . import crud

logger = logging.getLogger(__name__)


async def delete_expired_paste_task(interval: float, db: Session) -> None:
    """Asynchronous loop task that periodically deletes expired database pastes.

    Args:
        interval: Time in seconds between cleanup runs.
        db: The SQLAlchemy database session to use for deletions.
    """
    run = 1
    logger.info(f"Task started: delete-expired-paste after each {interval}s.")
    while run:
        try:
            await asyncio.sleep(interval)
        except asyncio.CancelledError:
            run = False
        else:
            crud.delete_expired_pastes(db)

    logger.info("Task ended: delete-expired-paste.")
