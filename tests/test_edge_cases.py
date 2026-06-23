"""Test suite for edge cases and coverage gaps."""

import asyncio
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from api import keygen, models
from api.background_tasks import delete_expired_paste_task
from api.database import get_db


def test_models_repr(db_session: Session) -> None:
    """Verify __repr__ methods for Paste and File models."""
    paste = models.Paste(key="abcd", expiry=3600)
    file = models.File(text="content", kind="python", name="test.py")
    paste.files.append(file)

    db_session.add(paste)
    db_session.commit()
    db_session.refresh(paste)

    assert repr(paste) == "<Paste: key=abcd>"
    assert repr(file) == f"<File: paste_id={paste.id}>"


def test_key_exhaustion_raises_runtime_error(db_session: Session) -> None:
    """Verify that key generation raises RuntimeError after 10 collisions."""
    # Pre-populate a paste with key 'aaaa'
    paste = models.Paste(key="aaaa", expiry=3600)
    db_session.add(paste)
    db_session.commit()

    # Mock create_random_key to always return 'aaaa', triggering collisions
    with patch("api.keygen.create_random_key", return_value="aaaa"):
        with pytest.raises(RuntimeError) as exc_info:
            keygen.create_unique_random_key(db_session)
        assert "Failed to generate unique random key" in str(exc_info.value)


def test_api_handles_key_exhaustion(client: TestClient, db_session: Session) -> None:
    """Verify API handles key exhaustion and returns HTTP 500."""
    paste = models.Paste(key="aaaa", expiry=3600)
    db_session.add(paste)
    db_session.commit()

    # Mock create_random_key to trigger key exhaustion on POST
    json_request = {
        "files": [{"name": "test.txt", "text": "hello", "kind": "text"}],
        "expiry": 3600,
    }
    with patch("api.keygen.create_random_key", return_value="aaaa"):
        response = client.post("/", json=json_request)
        assert response.status_code == 500
        assert "Failed to generate unique random key" in response.json()["detail"]


@pytest.mark.anyio
async def test_delete_expired_paste_task_cancellation(
    db_session: Session,
) -> None:
    """Verify that delete_expired_paste_task loop cancels cleanly."""
    task = asyncio.create_task(delete_expired_paste_task(0.01, db_session))
    await asyncio.sleep(0.02)
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass  # expected cancellation


def test_get_db_generator() -> None:
    """Verify get_db generator yields a session and closes it on exit."""
    generator = get_db()
    db = next(generator)
    assert isinstance(db, Session)

    # Verify the session is active
    assert db.is_active

    # Close generator
    with pytest.raises(StopIteration):
        next(generator)
