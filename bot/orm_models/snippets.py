"""Text snippets."""

from sqlalchemy import Column, Integer, Text

from .base import Base


class Snippet(Base):
    """A snippet in the database."""

    __tablename__ = "snippets"

    snippet_id: int = Column(Integer, primary_key=True)
    name: str = Column(Text, nullable=False, unique=True)
    text: str = Column(Text, nullable=False)
