"""All helper functions are located here."""

import argparse
import os
import tomllib
from pathlib import Path
from typing import Any, Hashable

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


def create_envfile_from_envvars() -> None:
    """Helper function to create .env file for database credentials
    in /envs dir by reading environment variables."""

    envfile_path = Path(__file__).resolve().parent.parent / "envs" / ".env"

    with envfile_path.open(mode="w") as env_file:
        env_file.write(f"DB_DRIVER={os.getenv('DB_DRIVER')}\n")
        env_file.write(f"DB_NAME={os.getenv('DB_NAME')}\n")
        env_file.write(f"DB_HOST={os.getenv('DB_HOST')}\n")
        env_file.write(f"DB_PORT={os.getenv('DB_PORT')}\n")
        env_file.write(f"DB_USER={os.getenv('DB_USER')}\n")
        env_file.write(f"DB_PASSWORD={os.getenv('DB_PASSWORD')}\n")


def equal_dict(
    dict_1: dict[Hashable, Any],
    dict_2: dict[Hashable, Any],
    exclude_keys: list[str],
) -> bool:
    """Compare two dictionaries by excluding keys specified in exclude_keys.

    :param dict_1: The first dictionary.
    :type dict_1: :class:`dict[Hashable, Any]`
    :param dict_2: The second dictionary.
    :type dict_2: :class:`dict[Hashable, Any]`
    :param exclude_keys: List of keys to exclude from given dictionaries.
    :type exclude_keys: :class:`list[str]`
    :return: True if the two dictionaries are equal, False otherwise.
    :rtype: :class:`bool`
    """

    for key in exclude_keys:
        if key in dict_1:
            del dict_1[key]

        if key in dict_2:
            del dict_2[key]

    return dict_1 == dict_2


def equal_list_of_dict(
    list_dict_1: list[dict[Hashable, Any]],
    list_dict_2: list[dict[Hashable, Any]],
    exclude_keys: list[str],
) -> bool:
    """Compare two dictionaries by excluding keys specified in exclude_keys.

    :param list_dict_1: The first list of dictionaries.
    :type list_dict_1: :class:`list[dict[Hashable, Any]]`
    :param list_dict_2: The second list of dictionaries.
    :type list_dict_2: :class:`list[dict[Hashable, Any]]`
    :param exclude_keys: List of keys to exclude from given dictionaries.
    :type exclude_keys: :class:`list[str]`
    :return: True if the two list of dictionaries are equal, False otherwise.
    :rtype: :class:`bool`
    """

    for key in exclude_keys:
        for item in list_dict_1:
            if key in item:
                del item[key]

        for item in list_dict_2:
            if key in item:
                del item[key]

    return list_dict_1 == list_dict_2
