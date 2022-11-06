import string
from dataclasses import dataclass, field

import discord
from sqlalchemy import select

from bot.orm_models import Post
from bot.settings import POSTS, Connections


@dataclass(frozen=True)
class MemberInfo:
    """Information about the user, and their interaction with the server & Polonium bot."""

    member: discord.Member
    previous_posts: list[int]  # List of forum post ids

    member_username: str = field(init=False)
    created_timestamp: str = field(init=False)
    joined_timestamp: str = field(init=False)
    default_post_title: str = field(init=False)

    def __post_init__(self) -> None:
        """Populate fields that are calculated after creation."""
        object.__setattr__(self, "member_username", f"{self.member.name}#{self.member.discriminator}")
        object.__setattr__(self, "created_timestamp", f"<t:{int(self.member.created_at.timestamp())}:R>")
        object.__setattr__(self, "joined_timestamp", f"<t:{int(self.member.joined_at.timestamp())}:R>")
        object.__setattr__(self, "default_post_title", self.get_channel_name_from_member(self.member))

    @staticmethod
    def get_channel_name_from_member(member: discord.Member) -> str:
        """
        Return a channel name that would pass Discord's basic channel name validation.

        The returned name may still not be suitable for a channel name, due to Discord not having
        and open source list of bad-words that they disallow in community servers.
        """
        channel_name = member.display_name.lower()
        channel_name = "".join(
            letter for letter in channel_name if letter.isprintable() and letter not in string.punctuation
        )
        if not channel_name:
            return "Name-unsuitable"

        return f"{channel_name}-{member.discriminator}"

    def get_base_member_embed(self) -> discord.Embed:
        """Return the embed that should be used for new posts opened by the member."""
        embed = discord.Embed(color=POSTS.user_embed_colour)
        embed.set_author(name=self.member_username, icon_url=self.member.display_avatar.url)
        embed.set_footer(text=f"User ID: {self.member.id}")
        return embed


async def get_member_info(member: discord.Member) -> MemberInfo:
    """Returns the info about this member and their interactions with the bot."""
    async with Connections.DB_SESSION.begin() as session:
        member_posts: list[Post] = await session.scalars(select(Post).where(Post.user_id == member.id))
        return MemberInfo(member=member, previous_posts=[post.post_id for post in member_posts])
