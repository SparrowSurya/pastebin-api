import asyncio
from sqlalchemy.orm import Session

from . import crud


async def delete_expired_paste_task(interval: float, db: Session):
    while True:
        try:
            await asyncio.sleep(interval)
        except asyncio.CancelledError:
            return
        else:
            crud.delete_expired_pastes(db)
