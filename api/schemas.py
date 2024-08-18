from datetime import datetime
from pydantic import BaseModel, Field
from typing import Annotated, List


class File(BaseModel):
    """A single file paste schema."""

    name: Annotated[str, Field(max_length=64)]
    """Name of the file."""

    text: Annotated[str, Field(min_length=1)]
    """Text contents of the file."""

    kind: Annotated[str, Field(max_length=64)]
    """Kind of raw file."""


class Paste(BaseModel):
    """A single paste schema."""

    files: Annotated[List[File], Field(min_length=1)]
    """List of files."""

    expiry: Annotated[int, Field(gt=0)]
    """Expiration time (in seconds)."""


class PasteInfo(BaseModel):
    """A detailed paste schema."""


    files: Annotated[List[File], Field(min_length=1)]
    """List of files."""

    key: Annotated[str, Field(max_length=8)]
    """unique identifier for the paste."""

    expiry: datetime
    """expiry date of the paste."""
