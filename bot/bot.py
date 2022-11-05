from pydis_core import BotBase
from pydis_core.utils import scheduling

from bot import exts


class Bot(BotBase):
    """A subclass of `pydis_core.BotBase` that implements bot-specific functions."""

    async def setup_hook(self) -> None:
        """Perform async initialisation method for Discord.py."""
        await super().setup_hook()

        scheduling.create_task(self.load_extensions(exts))
