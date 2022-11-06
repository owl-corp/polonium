import discord

import bot
from bot.exts.post_manager import _strings


class PostOpenConfirmation(discord.ui.View):
    """Foo."""

    def __init__(self) -> None:
        super().__init__(timeout=60)
        self.confirmed = None
        self.message: discord.Message = None

    @staticmethod
    def get_base_confirmation_embed() -> discord.Embed:
        """A base embed for confirmation messages."""
        embed = discord.Embed(
            colour=discord.Colour.og_blurple(),
        )
        embed.set_author(name=bot.instance.user.name, icon_url=bot.instance.user.display_avatar.url)
        return embed

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.primary)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        """A button that confirms thread creation on click."""
        self.confirmed = True
        embed = self.get_base_confirmation_embed()
        embed.title = "**Thread opened**"
        embed.description = _strings.CONFIRMED_MESSAGE
        await interaction.message.edit(embed=embed, view=None)
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        """A button that cancelled thread creation on click."""
        self.confirmed = False
        embed = self.get_base_confirmation_embed()
        embed.title = "**Cancelled**"
        await interaction.message.edit(embed=embed, view=None)
        self.stop()

    async def on_timeout(self) -> None:
        """Cancel the thread creation on timeout."""
        embed = self.get_base_confirmation_embed()
        embed.title = "**Cancelled**"
        embed.description = "Timed out"
        await self.message.edit(embed=embed, view=None)
