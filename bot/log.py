import os
import sys
from logging import INFO, WARNING, StreamHandler

import coloredlogs
from pydis_core.utils import logging

from bot.settings import CONFIG


def setup_logging() -> None:
    """Setup logging for the bot."""
    # Console handler prints to terminal
    console_handler = StreamHandler()
    level = logging.TRACE_LEVEL if CONFIG.debug else INFO
    console_handler.setLevel(level)

    # Remove old loggers, if any
    root = logging.get_logger()
    if root.handlers:
        for handler in root.handlers:
            root.removeHandler(handler)

    # Setup new logging configuration
    if "COLOREDLOGS_LEVEL_STYLES" not in os.environ:
        coloredlogs.DEFAULT_LEVEL_STYLES = {
            **coloredlogs.DEFAULT_LEVEL_STYLES,
            "trace": {"color": 246},
            "critical": {"background": "red"},
            "debug": coloredlogs.DEFAULT_LEVEL_STYLES["info"],
        }

    if "COLOREDLOGS_LOG_FORMAT" not in os.environ:
        coloredlogs.DEFAULT_LOG_FORMAT = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"

    coloredlogs.install(level=level, logger=root, stream=sys.stdout)
    logging.get_logger("discord").setLevel(WARNING)
    logging.get_logger("asyncio").setLevel(WARNING)
