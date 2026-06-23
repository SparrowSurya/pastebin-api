"""Pydantic schemas representing request and response payloads for the API."""

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field


class File(BaseModel):
    """Data model representing a single text/code snippet inside a paste payload."""

    name: Annotated[str, Field(max_length=64)]
    """Name of the file."""

    text: Annotated[str, Field(min_length=1, max_length=1_000_000)]
    """Text contents of the file."""

    kind: Annotated[str, Field(max_length=64)]
    """Kind of raw file (syntax format, e.g. 'python', 'json')."""


class Paste(BaseModel):
    """Payload data model for creating a new paste."""

    files: Annotated[list[File], Field(min_length=1, max_length=10)]
    """List of files contained in this paste (must have at least one, max 10)."""

    expiry: Annotated[int, Field(gt=0)]
    """Expiration time limit relative to creation (in seconds)."""


class PasteInfo(BaseModel):
    """Detailed paste payload schema returned on retrieve queries."""

    files: Annotated[list[File], Field(min_length=1)]
    """List of files associated with this paste."""

    key: Annotated[str, Field(max_length=8)]
    """Unique 4-8 character public lookup key identifier."""

    expiry: datetime
    """Absolute expiration date and time."""
