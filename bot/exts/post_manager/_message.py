import discord
from pydis_core.utils.logging import get_logger
from pydis_core.utils.members import get_or_fetch_member

from bot.database import posts
from bot.exts.post_manager._member import MemberInfo
from bot.settings import POSTS

log = get_logger(__name__)


async def forward_dm_to_post(post: discord.Thread, member_info: MemberInfo, message: discord.Message) -> None:
    """Forwards the members DM `message` to the given post."""
    embed = member_info.get_base_member_embed()
    embed.description = message.content
    await post.send(embed=embed)
    await message.add_reaction("✅")


def build_mod_message_embed(mod: discord.Member, content: str) -> discord.Embed:
    """Return an embed based on the mod's details and given content."""
    embed = discord.Embed(colour=POSTS.mod_embed_colour)
    embed.description = content
    embed.set_author(name=mod.display_name, icon_url=mod.display_avatar.url)
    return embed


async def send_dm_from_post(post: discord.Thread, embed: discord.Embed) -> None:
    """Sends the given embed as a DM to the post opener."""
    try:
        db_post = await posts.get_post_by_id(post.id)
    except posts.PostNotFoundError as e:
        log.error(f"Post {post.id} could not be found.", exc_info=e)
        return

    member = await get_or_fetch_member(post.guild, db_post.user_id)

    await member.send(embed=embed)
