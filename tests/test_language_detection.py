"""Test suite for programming language auto-detection."""

from sqlalchemy.orm import Session

from api import crud, schemas


def test_auto_detects_obvious_python(db_session: Session) -> None:
    """Verify that Python code is detected as Python despite incorrect input."""
    python_code = """
def greet(name: str) -> None:
    print(f"Hello, {name}!")

if __name__ == "__main__":
    greet("World")
"""
    paste = schemas.Paste(
        files=[schemas.File(name="hello.py", text=python_code, kind="dart")],
        expiry=3600,
    )

    db_paste = crud.create_db_paste(db_session, paste)
    assert db_paste.files[0].kind == "python"


def test_fallback_to_user_kind_on_plain_text(db_session: Session) -> None:
    """Verify that generic plain text falls back to the user's provided kind."""
    plain_text = "Just some standard non-code sentences written here."
    paste = schemas.Paste(
        files=[schemas.File(name="info.txt", text=plain_text, kind="custom-kind")],
        expiry=3600,
    )

    db_paste = crud.create_db_paste(db_session, paste)
    assert db_paste.files[0].kind == "custom-kind"


def test_auto_detects_obvious_json(db_session: Session) -> None:
    """Verify that obvious JSON is auto-detected correctly."""
    json_data = '{"name": "test", "active": true, "values": [1, 2, 3]}'
    paste = schemas.Paste(
        files=[schemas.File(name="config.json", text=json_data, kind="xml")],
        expiry=3600,
    )

    db_paste = crud.create_db_paste(db_session, paste)
    assert db_paste.files[0].kind == "json"


def test_empty_text_uses_fallback(db_session: Session) -> None:
    """Verify that empty text fallback logic returns user-provided kind or 'text'."""
    paste = schemas.Paste(
        files=[schemas.File(name="empty.txt", text=" ", kind="sql")],
        expiry=3600,
    )

    db_paste = crud.create_db_paste(db_session, paste)
    assert db_paste.files[0].kind == "sql"


def test_unrecognized_filename_extension(db_session: Session) -> None:
    """Verify that unrecognized extensions trigger catch block and fallback."""
    paste = schemas.Paste(
        files=[schemas.File(name="code.unrecognized", text="text", kind="custom")],
        expiry=3600,
    )

    db_paste = crud.create_db_paste(db_session, paste)
    assert db_paste.files[0].kind == "custom"


def test_content_guess_exception_falls_back(db_session: Session) -> None:
    """Verify that guess_lexer exceptions trigger catch block and fallback."""
    from unittest.mock import patch

    paste = schemas.Paste(
        files=[schemas.File(name="test", text="some text", kind="fallback-type")],
        expiry=3600,
    )

    with patch("api.language_detector.guess_lexer", side_effect=ValueError("Error")):
        db_paste = crud.create_db_paste(db_session, paste)
    assert db_paste.files[0].kind == "fallback-type"


def test_normalizes_mojo_to_python(db_session: Session) -> None:
    """Verify that auto-detected mojo language maps to python."""
    from unittest.mock import MagicMock, patch

    # Mock guess_lexer to return a lexer with "mojo" alias
    mock_lexer = MagicMock()
    mock_lexer.aliases = ["mojo"]

    paste = schemas.Paste(
        files=[schemas.File(name="test", text="print('hello')", kind="text")],
        expiry=3600,
    )

    # We patch guess_lexer and check if it maps to python
    with patch("api.language_detector.guess_lexer", return_value=mock_lexer):
        db_paste = crud.create_db_paste(db_session, paste)
    assert db_paste.files[0].kind == "python"
