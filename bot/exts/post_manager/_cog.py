"""Extension to manage posts to the mail forum."""

import datetime

import discord
from discord.ext import commands
from discord.ext.commands import Cog
from pydis_core.utils.logging import get_logger
from pydis_core.utils.members import get_or_fetch_member

from bot.bot import Bot
from bot.database import posts
from bot.exts.post_manager import _member, _message, _post
from bot.settings import CHANNELS

log = get_logger(__name__)


class PostManager(Cog):
    """Log that the bot started up in the log channel."""

    def __init__(self, bot: Bot):
        self.bot = bot
        self.mail_forum: discord.ForumChannel

    async def cog_load(self) -> None:
        """Announce our presence to the configured log channel."""
        await self.bot.wait_until_guild_available()
        self.mail_forum = self.bot.get_channel(CHANNELS.mail_forum)
        if not isinstance(self.mail_forum, discord.ForumChannel):
            raise TypeError("CHANNELS.mail_forum is not a forum channel!")

    @commands.command("reply", aliases=("r",))
    async def reply_to_post(self, ctx: commands.Context, *, content: str) -> None:
        """Allows mods to send a DM reply to a post opener."""
        if not getattr(ctx.channel, "parent", None) or ctx.channel.parent != self.mail_forum:
            return
        embed = _message.build_mod_message_embed(ctx.author, content)
        try:
            await _message.send_dm_from_post(ctx.channel, embed)
        except posts.PostNotFoundError:
            await ctx.send(":x: Could not find recipient for current post.")
            return
        await ctx.send(embed=embed)
        await ctx.message.delete()

    @Cog.listener()
    async def on_typing(
        self, channel: discord.abc.Messageable, user: discord.Member | discord.User, when: datetime.datetime
    ) -> None:
        """Forward typing events to posts if the user has an open post."""
        if not isinstance(channel, discord.DMChannel) or not isinstance(user, discord.User):
            # Early return for in-guild typing events, and fix typing for `user`.
            return
        post = await _post.get_active_post(self.mail_forum, user)
        if post:
            await post.typing()

    @Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """Forward on messages from members to the appropriate handler."""
        if message.guild or message.author.bot:
            return

        member = await get_or_fetch_member(self.mail_forum.guild, message.author.id)
        if not member:
            return
        member_info = await _member.get_member_info(member)

        post = await _post.get_active_post(self.mail_forum, member)
        if not post:
            post = await _post.maybe_create_post(self.mail_forum, member_info, message)
            if not post:
                return

        await _message.forward_dm_to_post(post, member_info, message)
