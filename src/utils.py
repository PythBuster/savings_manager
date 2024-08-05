"""All helper functions are located here."""

import argparse
import datetime
import os
import tomllib
from pathlib import Path
from typing import Annotated, Any, Hashable

from dictalchemy import asdict
from dotenv import load_dotenv
from starlette.requests import Request

from src.custom_types import DBSettings, EnvironmentType


async def check_existence_of_moneybox_by_id(
    request: Request,
    moneybox_id: Annotated[
        int, Path(title="Moneybox ID", description="Moneybox ID to be processed.")
    ],
) -> int:
    """FastAPI dependency for checking existence of moneybox by id.

    :param request: The fastapi request object.
    :type request: Request
    :param moneybox_id: The id of the moneybox to check.
    :type moneybox_id: int
    :return: The moneybox id.
    :rtype: int
    """

    _ = await request.app.state.db_manager.get_moneybox(moneybox_id=moneybox_id)
    return moneybox_id


def get_vanilla_datetime() -> datetime:
    """Get a datetime without TZinfo and without microseconds
    as isoformat"""

    return datetime.datetime.now(tz=datetime.timezone.utc).replace(tzinfo=None, microsecond=0)


def get_db_settings() -> DBSettings:
    """A :class:`DBSettings` spawner.

    :return: Creates a :class:`DBSettings` by loading os.environ settings
        and return a :class:`DBSettings` instance.
    :rtype: :class:`DBSettings`
    """

    return DBSettings(
        db_environment=os.getenv("DB_ENVIRONMENT", ""),
        db_driver=os.getenv("DB_DRIVER", ""),
        db_file=os.getenv("DB_FILE", ""),
    )


def get_database_url(db_settings: DBSettings) -> str:
    """Create a database connection string based on db_settings.

    :param db_settings: Includes the database credentials.
    :type db_settings: :class:`DBSettings`
    :return: A database connection string
    :rtype: :class:`str`
    """

    if "sqlite" in db_settings.db_driver:
        return f"{db_settings.db_driver}:///{db_settings.db_file}"

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
    dict_1: dict,
    dict_2: dict,
    exclude_keys: list[str],
) -> bool:
    """Compare two dictionaries by excluding keys specified in exclude_keys.

    :param dict_1: The first dictionary.
    :type dict_1: :class:`dict`
    :param dict_2: The second dictionary.
    :type dict_2: :class:`dict`
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


def as_dict(
    model: "SqlBase",
    exclude=None,
    exclude_underscore=None,
    exclude_pk=None,
    follow=None,
    include=None,
    only=None,
    **kwargs,
) -> dict[str, Any]:
    return asdict(
        model=model,
        exclude=exclude,
        exclude_underscore=exclude_underscore,
        exclude_pk=exclude_pk,
        follow=follow,
        include=include,
        only=only,
        **kwargs,
    )
