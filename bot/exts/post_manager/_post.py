import discord
from pydis_core.utils.logging import get_logger

from bot.database import posts
from bot.exts.post_manager import _member, _strings, _views

log = get_logger(__name__)


async def get_active_post(
    forum_channel: discord.ForumChannel, member: discord.Member | discord.User
) -> discord.Thread | None:
    """Returns the active post for a member/user, if they have one."""
    try:
        db_most_recent_post = await posts.get_user_most_recent_post(member.id)
    except posts.PostNotFoundError:
        return None

    most_recent_post = forum_channel.guild.get_thread(db_most_recent_post.forum_post_id)
    if most_recent_post and not most_recent_post.archived:
        return most_recent_post


async def create_post(
    forum_channel: discord.ForumChannel, post_title: str, opener_message: discord.Message
) -> discord.Thread:
    """Creates a post in `forum_channel` for the `member`."""
    opener_message_content = f"{opener_message.author.mention}:\n\n{opener_message.content}"[:1500]
    try:
        thread_with_message = await forum_channel.create_thread(name=post_title, content=opener_message_content)
    except discord.HTTPException as e:
        # To handle users with names that trip Discord's bad name filter.
        log.info(str(e))
        thread_with_message = await forum_channel.create_thread(name="Name-unsuitable", content=opener_message_content)
    await posts.create_post(opener_message.author.id, thread_with_message.thread.id)
    return thread_with_message.thread


async def maybe_create_post(
    forum_channel: discord.ForumChannel, member_info: _member.MemberInfo, opening_message: discord.message
) -> discord.Thread | None:
    """Creates a post in `forum_channel` for the `member` after confirming with a button interaction."""
    view = _views.PostOpenConfirmation()
    embed = _views.PostOpenConfirmation.get_base_confirmation_embed()
    embed.description = _strings.CONFIRM_POST_CREATION_MESSAGE
    message = await member_info.member.send(embed=embed, view=view)
    view.message = message
    if await view.wait() or not view.confirmed:
        return None
    post = await create_post(forum_channel, member_info.default_post_title, opening_message)
    embed = member_info.get_base_member_embed()
    embed.description = (
        f"{member_info.member.mention} was created {member_info.created_timestamp}, "
        f"joined {member_info.joined_timestamp} and has **{len(member_info.previous_posts)}** past posts."
    )
    if roles := member_info.member.roles[1:]:
        embed.add_field(name="Roles", value=" ".join(role.mention for role in roles))
    await post.send(embed=embed)
    return post
