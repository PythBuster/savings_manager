"""All helper functions are located here."""

import argparse
import os
import tomllib
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from src.custom_types import DBSettings, EnvironmentType


def get_db_settings() -> DBSettings:
    """A :class:`DBSettings` spawner.

    :return: Creates a :class:`DBSettings` by loading os.environ settings
        and return a :class:`DBSettings` instance.
    :rtype: :class:`DBSettings`
    """

    return DBSettings(
        db_user=os.getenv("DB_USER", ""),
        db_password=os.getenv("DB_PASSWORD", ""),
        db_host=os.getenv("DB_HOST", ""),
        db_port=os.getenv("DB_PORT"),
        db_name=os.getenv("DB_NAME", ""),
        db_driver=os.getenv("DB_DRIVER"),
    )


def get_database_url(db_settings: DBSettings) -> str:
    """Create a database connection string based on db_settings.

    :param db_settings: Includes the database credentials.
    :type db_settings: :class:`DBSettings`
    :return: A database connection string
    :rtype: :class:`str`
    """

    if "sqlite" in db_settings.db_driver:
        return f"{db_settings.db_driver}:///{db_settings.db_name}"

    if "postgres" in db_settings.db_driver:
        return (
            f"{db_settings.db_driver}://"
            f"{db_settings.db_user}:{db_settings.db_password.get_secret_value()}"
            f"@{db_settings.db_host}:{db_settings.db_port}/{db_settings.db_name}"
        )

    raise ValueError("Not supported database driver.")


def get_app_data() -> dict[str, Any]:
    """Extract app information from pyproject.toml.

    :return: The app data section from pyproject.toml as dict
    :rtype: :class:`dict[str, Any]`
    """

    pyproject_file_path = Path(__file__).resolve().parent.parent / "pyproject.toml"

    with pyproject_file_path.open(mode="rb") as pyproject_file:
        pyproject_data = tomllib.load(pyproject_file)

    return pyproject_data["tool"]["poetry"]


def load_environment() -> EnvironmentType:
    """Helper function to load the current env file, depending on deploy environment.

    :return: The detected environment type.
    :rtype: :class:`EnvironmentType`
    """

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--environment",
        required=False,
        default=EnvironmentType.TEST,
        help="Loads environment variables depending on this flag",
        type=EnvironmentType,
    )
    args = parser.parse_args()

    if args.environment == EnvironmentType.DEV:
        dotenv_path = Path(__file__).resolve().parent.parent / "envs" / ".env"
        load_dotenv(dotenv_path=dotenv_path)
        print(f"Loaded {dotenv_path}")

    return args.environment
