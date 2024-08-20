"""All helper functions are located here."""

import os
import tomllib
from pathlib import Path
from typing import Annotated, Any, Sequence

import tabulate
from dictalchemy import asdict
from starlette.requests import Request

from src.custom_types import AppEnvVariables


async def check_existence_of_moneybox_by_id(
    request: Request,
    moneybox_id: Annotated[
        int, Path(title="Moneybox ID", description="Moneybox ID to be processed.")  # type: ignore
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


def get_database_url(db_settings: AppEnvVariables) -> str:
    """Create a database connection string based on db_settings.

    :param db_settings: Includes the database credentials.
    :type db_settings: :class:`AppEnvVariables`
    :return: A database connection string
    :rtype: :class:`str`
    """

    if "postgres" in db_settings.db_driver:
        return f"{db_settings.db_driver}://{db_settings.db_user}:{db_settings.db_password.get_secret_value()}@{db_settings.db_host}:{db_settings.db_port}/{db_settings.db_name}"  # noqa: ignore  # pylint: disable=line-too-long

    raise ValueError(f"Not supported database driver: {db_settings.db_driver}")


def get_app_data() -> dict[str, Any]:
    """Extract app information from pyproject.toml.

    :return: The app data section from pyproject.toml as dict
    :rtype: :class:`dict[str, Any]`
    """

    pyproject_file_path = Path(__file__).resolve().parent.parent / "pyproject.toml"

    with pyproject_file_path.open(mode="rb") as pyproject_file:
        pyproject_data = tomllib.load(pyproject_file)

    return pyproject_data["tool"]["poetry"]


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
    exclude_keys: list[str] | None = None,
) -> bool:
    """Compare two dictionaries by excluding keys specified in exclude_keys.

    :param dict_1: The first dictionary.
    :type dict_1: :class:`dict`
    :param dict_2: The second dictionary.
    :type dict_2: :class:`dict`
    :param exclude_keys: List of keys to exclude from given dictionaries.
    :type exclude_keys: :class:`list[str]` | :class:`None`
    :return: True if the two dictionaries are equal, False otherwise.
    :rtype: :class:`bool`
    """

    if exclude_keys is None:
        exclude_keys = []

    # Create copies of the dictionaries to avoid modifying the originals
    dict_1_filtered = {k: v for k, v in dict_1.items() if k not in exclude_keys}
    dict_2_filtered = {k: v for k, v in dict_2.items() if k not in exclude_keys}

    return dict_1_filtered == dict_2_filtered


def as_dict(  # type: ignore  # pylint: disable=missing-function-docstring, too-many-arguments
    model: "SqlBase",  # type: ignore  # noqa: F821
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


def tabulate_str(headers: Sequence, rows: Sequence, showindex: bool = False) -> str:
    """Helper function to get a ascii table based on headers and rows.

    :param headers: The headers of the table.
    :type headers: :class:`Sequence`
    :param rows: The row data of the table.
    :type rows: :class:`Sequence`
    :param showindex: Flag to show indexes in table.
    :type showindex: :class:`bool`
    :return: The generated string table.
    :rtype: :class:`str`
    """

    tabulate.MIN_PADDING = 35
    return tabulate.tabulate(
        headers=headers,
        tabular_data=rows,
        tablefmt="plain",
        showindex=showindex,
    )
