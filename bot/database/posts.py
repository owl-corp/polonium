from pydis_core.utils.logging import get_logger
from sqlalchemy import select

from bot.database.orm_models import Post
from bot.settings import Connections

log = get_logger(__name__)


class PostNotFoundError(LookupError):
    """Raised when a post could not be found."""


async def get_posts_by_user_id(user_id: int) -> list[Post]:
    """Returns a list of the specified user_id's posts."""
    async with Connections.DB_SESSION.begin() as session:
        posts = await session.scalars(select(Post).where(Post.user_id == user_id))
        session.expunge_all()
        return posts


async def get_post_by_id(post_id: int) -> Post:
    """Returns a post by its ID."""
    async with Connections.DB_SESSION.begin() as session:
        post: Post | None = await session.scalar(select(Post).where(Post.forum_post_id == post_id))
        if not post:
            raise PostNotFoundError(f"Post {post_id} could not be found.")
        session.expunge(post)
        return post


async def get_user_most_recent_post(user_id: int) -> Post:
    """Returns the user's most recent post, if one exists."""
    async with Connections.DB_SESSION.begin() as session:
        most_recent_post: Post | None = await session.scalar(
            select(Post).where(Post.user_id == user_id).order_by(Post.post_id.desc())
        )
        if not most_recent_post:
            log.debug(f"A post could not be found for {user_id}.")
            raise PostNotFoundError(f"A post could not be found for {user_id}.")
        session.expunge(most_recent_post)
        return most_recent_post


async def create_post(user_id: int, post_id: int) -> None:
    """Inserts a new Post into the database."""
    async with Connections.DB_SESSION.begin() as session:
        new_post = Post(user_id=user_id, forum_post_id=post_id)
        session.add(new_post)
