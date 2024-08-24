import asyncio
import logging

from sqlalchemy.orm import Session

from . import crud


logger = logging.getLogger(__name__)


async def delete_expired_paste_task(interval: float, db: Session):
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