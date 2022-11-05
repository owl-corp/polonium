import logging
import os
import sys

import coloredlogs
from pydis_core.utils.logging import get_logger

from bot.settings import CONFIG


def setup_logging() -> None:
    """Setup logging for the bot."""
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
    if "COLOREDLOGS_LEVEL_STYLES" not in os.environ:
        coloredlogs.DEFAULT_LEVEL_STYLES = {
            **coloredlogs.DEFAULT_LEVEL_STYLES,
            "trace": {"color": 246},
            "critical": {"background": "red"},
            "debug": coloredlogs.DEFAULT_LEVEL_STYLES["info"],
        }

    if "COLOREDLOGS_LOG_FORMAT" not in os.environ:
        coloredlogs.DEFAULT_LOG_FORMAT = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"

    coloredlogs.install(logger=root, stream=sys.stdout)
    get_logger("discord").setLevel(logging.WARNING)
