from bot.bot import Bot
from bot.exts.post_manager._cog import PostManager


async def setup(bot: Bot) -> None:
    """Load the PostManager cog."""
    await bot.add_cog(PostManager(bot))
