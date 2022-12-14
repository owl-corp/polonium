import typing
from collections.abc import Sequence

import discord
import pydantic
import sqlalchemy.orm
import tomlkit
from pydantic.error_wrappers import ErrorWrapper
from pydis_core.utils.logging import get_logger
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

log = get_logger(__name__)

# This is available in pydantic as pydantic.error_wrappers.ErrorList
# but is type hinted as a Sequence[any], due to being a recursive type.
# This makes it harder to handle the types.
# For our purposes, a fully accurate representation is not necessary.
_PYDANTIC_ERROR_TYPE = Sequence[ErrorWrapper | Sequence[ErrorWrapper]]


class PoloniumBaseSettings(pydantic.BaseSettings):
    """Base class for settings with .env support and nicer error messages."""

    @staticmethod
    def __log_missing_errors(base_error: pydantic.ValidationError, errors: _PYDANTIC_ERROR_TYPE) -> bool:
        """
        Log out a nice representation for missing environment variables.

        Returns false if none of the errors were caused by missing variables.
        """
        found_relevant_errors = False
        for error in errors:
            if isinstance(error, Sequence):
                found_relevant_errors = (
                    PoloniumBaseSettings.__log_missing_errors(base_error, error) or found_relevant_errors
                )
            elif isinstance(error.exc, pydantic.MissingError):
                log.error(f"Missing environment variable {base_error.args[1].__name__}.{error.loc_tuple()[0]}")
                found_relevant_errors = True

        return found_relevant_errors

    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        """Try to instantiate the class, and print a nicer message for unset variables."""
        try:
            super().__init__(*args, **kwargs)
        except pydantic.ValidationError as error:
            if PoloniumBaseSettings.__log_missing_errors(error, error.raw_errors):
                exit(1)
            else:
                # The validation error is not due to an unset environment variable, propagate the error as normal
                raise error from None

    class Config:
        """Enable env files."""

        frozen = True

        env_file = ".env"
        env_file_encoding = "utf-8"


class _Config(PoloniumBaseSettings):
    """General configuration settings for the service."""

    @staticmethod
    def _get_project_version() -> str:
        with open("pyproject.toml") as pyproject:
            file_contents = pyproject.read()

        return tomlkit.parse(file_contents)["tool"]["poetry"]["version"]  # type: ignore[index, return-value]

    version: str = _get_project_version()

    debug: bool = False
    git_sha: str = "development"
    database_url: pydantic.SecretStr


CONFIG = _Config()


class Connections:
    """How to connect to other, internal services."""

    # Async engines only support future style
    DB_ENGINE = create_async_engine(CONFIG.database_url.get_secret_value(), future=True)
    DB_SESSION = sqlalchemy.orm.sessionmaker(DB_ENGINE, class_=AsyncSession)


class _Bot(PoloniumBaseSettings):
    """Configuration settings specific to the Bot itself."""

    guild_id: int = 1038469736612233317
    command_prefix: str = "&"
    discord_token: pydantic.SecretStr


class _Roles(PoloniumBaseSettings):
    """Settings for Discord roles required by the bot."""

    mod_team: int = 1038470644347699281

    pingable_roles: Sequence[int] = (mod_team,)


class _Channels(PoloniumBaseSettings):
    """Settings for Discord roles required by the bot."""

    dev_log: int = 1038469960537743460
    mail_forum: int = 1038592814751162378


class _Posts(PoloniumBaseSettings):
    """Settings specific to posts in the mail forum."""

    mod_embed_colour: int = discord.Colour.green().value
    user_embed_colour: int = discord.Colour.gold().value


BOT = _Bot()
ROLES = _Roles()
CHANNELS = _Channels()
POSTS = _Posts()
