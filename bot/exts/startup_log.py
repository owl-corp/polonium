from discord import Embed
from discord.ext.commands import Cog
from pydis_core.utils.logging import get_logger

from bot.bot import Bot
from bot.settings import CHANNELS

log = get_logger(__name__)


class StartupLog(Cog):
    """Log that the bot started up in the log channel."""

    def __init__(self, bot: Bot):
        self.bot = bot

    async def cog_load(self) -> None:
        """Announce our presence to the configured log channel."""
        await self.bot.wait_until_guild_available()
        log.info("Bot connected!")

        embed = Embed(description="Connected!")
        embed.set_author(
            name=self.bot.user.name,
            url="https://github.com/owl-corp/polonium",
            icon_url=self.bot.user.display_avatar.url,
        )

        await self.bot.get_channel(CHANNELS.dev_log).send(embed=embed)


async def setup(bot: Bot) -> None:
    """Load the Logging cog."""
    await bot.add_cog(StartupLog(bot))
