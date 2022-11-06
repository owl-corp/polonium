import discord
from pydis_core.utils.logging import get_logger
from sqlalchemy import select

from bot.exts.post_manager import _member, _strings, _views
from bot.orm_models import Post
from bot.settings import Connections

log = get_logger(__name__)


async def get_active_post(forum_channel: discord.ForumChannel, member: discord.Member) -> discord.Thread | None:
    """Returns the active post for a member, if they have one."""
    async with Connections.DB_SESSION.begin() as session:
        db_most_recent_post: Post | None = await session.scalar(
            select(Post).where(Post.user_id == member.id).order_by(Post.post_id.desc())
        )

        if db_most_recent_post:
            most_recent_post = forum_channel.guild.get_thread(db_most_recent_post.forum_post_id)
            if most_recent_post and not most_recent_post.archived:
                return most_recent_post
    return None


async def create_post(forum_channel: discord.ForumChannel, member_info: _member.MemberInfo) -> discord.Thread:
    """Creates a post in `forum_channel` for the `member`."""
    embed = member_info.get_base_member_embed()
    embed.description = (
        f"{member_info.member.mention} was created {member_info.created_timestamp}, "
        f"joined {member_info.joined_timestamp} and has **{len(member_info.previous_posts)}** past posts."
    )
    if roles := member_info.member.roles[1:]:
        embed.add_field(name="Roles", value=" ".join(role.mention for role in roles))

    try:
        thread_with_message = await forum_channel.create_thread(
            name=member_info.default_post_title, content="You've got mail!", embed=embed
        )
    except discord.HTTPException:
        # To handle users with names that trip Discord's bad name filter.
        thread_with_message = await forum_channel.create_thread(
            name="Name-unsuitable", content="You've got mail!", embed=embed
        )
    async with Connections.DB_SESSION.begin() as session:
        session.add(Post(user_id=member_info.member.id, forum_post_id=thread_with_message.thread.id))
    return thread_with_message.thread


async def maybe_create_post(
    forum_channel: discord.ForumChannel,
    member_info: _member.MemberInfo,
) -> discord.Thread | None:
    """Creates a post in `forum_channel` for the `member` after confirming with a button interaction."""
    view = _views.PostOpenConfirmation()
    embed = _views.PostOpenConfirmation.get_base_confirmation_embed()
    embed.description = _strings.CONFIRM_POST_CREATION_MESSAGE
    message = await member_info.member.send(embed=embed, view=view)
    view.message = message
    if await view.wait() or not view.confirmed:
        return None
    return await create_post(forum_channel, member_info)
