import asyncio
import logging

import aiohttp
import discord
from discord.ext import commands

import bot
from bot.bot import Bot
from bot.settings import BOT, CONFIG, ROLES

log = logging.getLogger(__name__)


async def main() -> None:
    """Entry async method for starting the bot."""
    allowed_roles = list({discord.Object(id_) for id_ in ROLES.pingable_roles})
    intents = discord.Intents.all()
    intents.presences = False
    intents.invites = False
    intents.webhooks = False
    intents.integrations = False

    async with aiohttp.ClientSession() as session:
        bot.instance = Bot(
            guild_id=BOT.guild_id,
            http_session=session,
            command_prefix=commands.when_mentioned_or(BOT.command_prefix),
            activity=discord.Game(name=f"Version {CONFIG.version}"),
            case_insensitive=True,
            max_messages=10_000,
            allowed_mentions=discord.AllowedMentions(everyone=False, roles=allowed_roles),
            intents=intents,
            allowed_roles=allowed_roles,
        )
        async with bot.instance as _bot:
            await _bot.start(BOT.discord_token.get_secret_value())


asyncio.run(main())
