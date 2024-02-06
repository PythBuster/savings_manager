"""All helper functions are located here."""

from functools import cache

from src.data_classes.settings import Settings


@cache
def get_settings() -> Settings:
    """Read current env file and provide data as settings model."""

    return Settings()


@cache
def get_database_url() -> str:
    """Create a database url based on env credentials."""

    env = get_settings()
    return f"{env.db_driver}:///{env.db_name}"
