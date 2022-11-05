import asyncio
import logging
import os
import sys
from typing import TYPE_CHECKING

import coloredlogs
from pydis_core.utils import apply_monkey_patches
from pydis_core.utils.logging import get_logger

from bot.settings import CONFIG

if TYPE_CHECKING:
    from bot.bot import Bot

# Console handler prints to terminal
console_handler = logging.StreamHandler()
level = logging.DEBUG if CONFIG.debug else logging.INFO
console_handler.setLevel(level)

# Remove old loggers, if any
root = logging.getLogger()
if root.handlers:
    for handler in root.handlers:
        root.removeHandler(handler)

# Setup new logging configuration
format_string = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
log_format = logging.Formatter(format_string)
if "COLOREDLOGS_LEVEL_STYLES" not in os.environ:
    coloredlogs.DEFAULT_LEVEL_STYLES = {
        **coloredlogs.DEFAULT_LEVEL_STYLES,
        "trace": {"color": 246},
        "critical": {"background": "red"},
        "debug": coloredlogs.DEFAULT_LEVEL_STYLES["info"],
    }

if "COLOREDLOGS_LOG_FORMAT" not in os.environ:
    coloredlogs.DEFAULT_LOG_FORMAT = format_string

coloredlogs.install(logger=root, stream=sys.stdout)
get_logger("discord").setLevel(logging.WARNING)

# On Windows, the selector event loop is required for aiodns.
if os.name == "nt":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

apply_monkey_patches()

instance: "Bot" = None  # Global Bot instance.
