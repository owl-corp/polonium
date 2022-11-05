import asyncio
import os
import warnings
from typing import TYPE_CHECKING

from pydis_core.utils import apply_monkey_patches
from sqlalchemy.exc import RemovedIn20Warning
from sqlalchemy.util import deprecations

from bot import log

if TYPE_CHECKING:
    from bot.bot import Bot

# The project uses SQLAlchemy v1.4, which supports the upcoming 2.0 style
# Enabling warnings will allow a seamless transition to 2.0 once released
# See: https://docs.sqlalchemy.org/en/14/glossary.html#term-2.0-style
deprecations.SQLALCHEMY_WARN_20 = True
warnings.simplefilter("error", RemovedIn20Warning)

log.setup_logging()

# On Windows, the selector event loop is required for aiodns.
if os.name == "nt":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

apply_monkey_patches()

instance: "Bot" = None  # Global Bot instance.
