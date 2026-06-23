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
    """
    Base class which provides automated table names and a primary key column.
    """

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    id: Mapped[int] = mapped_column(primary_key=True)


class Paste(Base):
    """A single paste."""

    key: Mapped[str] = mapped_column(String(8))
    pub_date: Mapped[datetime.datetime] = mapped_column(DateTime)
    exp_date: Mapped[datetime.datetime] = mapped_column(DateTime)
    files: Mapped[list["File"]] = relationship(
        "File", cascade="all,delete", backref="paste"
    )

    def __init__(self, key: str, expiry: int) -> None:
        self.key = key
        self.pub_date = datetime.datetime.now()
        self.exp_date = datetime.datetime.now() + datetime.timedelta(seconds=expiry)

    @property
    def expiry(self) -> datetime.datetime:
        return self.exp_date

    def __repr__(self) -> str:
        return f"<Paste: key={self.key}>"


class File(Base):
    """A file associated with single paste."""

    paste_id: Mapped[int] = mapped_column(ForeignKey("paste.id"))
    name: Mapped[str] = mapped_column(String(64), default="")
    kind: Mapped[str] = mapped_column(String(64))
    text: Mapped[str] = mapped_column(Text)

    def __init__(self, text: str, kind: str, name: str = "") -> None:
        self.text = text
        self.kind = kind
        self.name = name

    def __repr__(self) -> str:
        return f"<File: paste_id={self.paste_id}>"
