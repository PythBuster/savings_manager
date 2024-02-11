"""All helper functions are located here."""

import os

from src.custom_types import DBSettings


def get_db_settings() -> DBSettings:
    """A DBSettings spawner.

    :return: Creates a DBSettings by loading os.environ settings
        and return a DBSettings instance.
    :rtype: DBSettings
    """

    return DBSettings(
        db_user=os.getenv("DB_USER", ""),
        db_password=os.getenv("DB_PASSWORD", ""),
        db_host=os.getenv("DB_HOST", ""),
        db_port=os.getenv("DB_PORT"),
        db_name=os.getenv("DB_NAME", ""),
        db_driver=os.getenv("DB_DRIVER"),
        in_memory=os.getenv("IN_MEMORY"),
    )


def get_database_url(db_settings: DBSettings) -> str:
    """Create a database connection string based on db_settings.

    :param db_settings: Includes the database credentials.
    :type db_settings: DBSettings
    :return: A database connection string
    :rtype: str
    """

    if "sqlite" in db_settings.db_driver:
        if db_settings.in_memory:
            return f"{db_settings.db_driver}://"

        return f"{db_settings.db_driver}:///{db_settings.db_name}"

    if "postgres" in db_settings.db_driver:
        return (
            f"{db_settings.db_driver}://"
            f"{db_settings.db_user}:{db_settings.db_password.get_secret_value()}"
            f"@{db_settings.db_host}:{db_settings.db_port}/{db_settings.db_name}"
        )

    raise ValueError("Not supported database driver.")
