"""Database model definitions for SQLAlchemy ORM mapping.

Defines the base model structure and schema mappings for Paste and File entities.
"""

import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    declared_attr,
    mapped_column,
    relationship,
)


class Base(DeclarativeBase):
    """Abstract base model supplying automatic table names and an ID primary key."""

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """Generate table name based on lowercase representation of class name."""
        return cls.__name__.lower()

    id: Mapped[int] = mapped_column(primary_key=True)
    """Unique internal auto-incrementing identifier."""


class Paste(Base):
    """Database mapping representing a single Paste container with one or more files."""

    key: Mapped[str] = mapped_column(String(8))
    """Alphanumeric 4-8 character public unique key identifying the paste."""

    pub_date: Mapped[datetime.datetime] = mapped_column(DateTime)
    """Publication datetime when the paste was created."""

    exp_date: Mapped[datetime.datetime] = mapped_column(DateTime)
    """Expiration datetime after which the paste is deleted by the cleanup worker."""

    files: Mapped[list["File"]] = relationship(
        "File", cascade="all,delete", backref="paste"
    )
    """One-to-many relationship linking this paste to its associated file records."""

    def __init__(self, key: str, expiry: int) -> None:
        """Instantiate a Paste.

        Args:
            key: Public unique identifier key.
            expiry: Retention duration in seconds (relative to current time).
        """
        self.key = key
        self.pub_date = datetime.datetime.now()
        self.exp_date = datetime.datetime.now() + datetime.timedelta(seconds=expiry)

    @property
    def expiry(self) -> datetime.datetime:
        """Getter property returning the expiration datetime of the paste."""
        return self.exp_date

    def __repr__(self) -> str:
        return f"<Paste: key={self.key}>"


class File(Base):
    """Database mapping representing a single file snippet stored within a Paste."""

    paste_id: Mapped[int] = mapped_column(ForeignKey("paste.id"))
    """Foreign key linking to the parent Paste container."""

    name: Mapped[str] = mapped_column(String(64), default="")
    """Filename given to the code/text snippet (optional)."""

    kind: Mapped[str] = mapped_column(String(64))
    """Programming language or file type syntax (e.g. 'python', 'markdown', 'text')."""

    text: Mapped[str] = mapped_column(Text)
    """Raw text/source contents of the file snippet."""

    def __init__(self, text: str, kind: str, name: str = "") -> None:
        """Instantiate a File.

        Args:
            text: Raw contents.
            kind: Syntax format type descriptor.
            name: Filename.
        """
        self.text = text
        self.kind = kind
        self.name = name

    def __repr__(self) -> str:
        return f"<File: paste_id={self.paste_id}>"
