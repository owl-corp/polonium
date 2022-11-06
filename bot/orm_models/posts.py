"""Posts by users."""

from sqlalchemy import BigInteger, Column, Integer

from .base import Base


class Post(Base):
    """A post in the database."""

    __tablename__ = "posts"

    post_id: int = Column(Integer, primary_key=True)
    user_id: int = Column(BigInteger, nullable=False)
    forum_post_id: int = Column(BigInteger, nullable=False, unique=True)
