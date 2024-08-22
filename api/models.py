import datetime

from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declared_attr, declarative_base
from sqlalchemy.orm import relationship


class _Base(object):
    """
    Base class which provides automated table names and a primary key column.
    """

    @declared_attr
    def __tablename__(cls) -> str:
        return str(cls.__name__.lower())

    id = Column(Integer, primary_key=True)


Base = declarative_base(cls=_Base)


class Paste(Base):
    """A single paste."""

    key = Column(String(8))
    pub_date = Column(DateTime)
    exp_date = Column(DateTime)
    files = relationship("File", cascade="all,delete", backref="paste")

    def __init__(self, key: str, expiry: int):
        self.key = key
        self.pub_date = datetime.datetime.now()
        self.exp_date = datetime.datetime.now() + datetime.timedelta(seconds=expiry)

    @property
    def expiry(self):
        return self.exp_date

    def __repr__(self) -> str:
        return f"<Paste: key={self.key}>"


class File(Base):
    """A file associated with single paste."""

    paste_id = Column(ForeignKey(Paste.id))
    name = Column(String(64), default="")
    kind = Column(String(64))
    text = Column(Text)

    def __init__(self, text: str, kind: str, name: str = ""):
        self.text = text
        self.kind = kind
        self.name = name

    def __repr__(self) -> str:
        return f"<File: paste_id={self.paste_id}>"