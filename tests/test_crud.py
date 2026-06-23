"""Database CRUD operations test suite."""

import time

from sqlalchemy.orm import Session

from api import crud, schemas


def test_deletes_expired_paste(db_session: Session) -> None:
    """Verify that expired pastes are cleaned up while non-expired ones persist."""
    paste1 = schemas.Paste(
        files=[
            schemas.File(name="name1.txt", text="123", kind="text"),
            schemas.File(name="name2.txt", text="246", kind="text"),
        ],
        expiry=1,
    )
    paste2 = schemas.Paste(
        files=[
            schemas.File(name="name3.txt", text="987", kind="text"),
            schemas.File(name="name4.txt", text="321", kind="text"),
        ],
        expiry=3600,
    )

    pasteinfo1 = crud.create_db_paste(db_session, paste1)
    pasteinfo2 = crud.create_db_paste(db_session, paste2)

    assert crud.get_db_paste_by_key(db_session, pasteinfo1.key) is not None
    assert crud.get_db_paste_by_key(db_session, pasteinfo2.key) is not None

    time.sleep(1)  # wait for paste1 to expire

    crud.delete_expired_pastes(db_session)

    assert crud.get_db_paste_by_key(db_session, pasteinfo1.key) is None
    assert crud.get_db_paste_by_key(db_session, pasteinfo2.key) is not None
