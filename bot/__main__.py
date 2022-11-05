import logging

from bot.settings import SETTINGS

log = logging.getLogger(__name__)
log.info(f"Hello world {SETTINGS.git_sha = }")
