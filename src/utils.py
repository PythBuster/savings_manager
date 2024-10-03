"""All helper functions are located here."""

import os
import tomllib
from functools import cache
from pathlib import Path
from typing import Any, Sequence

import tabulate
from dictalchemy import asdict
from pydantic.alias_generators import to_camel

from src.constants import ENVIRONMENT_ENV_FILE_PATHS
from src.custom_types import AppEnvVariables, EnvironmentType


def get_app_env_variables(
    environment: EnvironmentType | None = None,
) -> tuple[EnvironmentType, AppEnvVariables]:
    """Helper function to get env settings.

    :param environment: Environment type or None, defaults to None.
    :type environment: :class:`EnvironmentType` | :class:`None`
    :return: A tuple of environment and app env settings.
    :rtype: :class:`tuple[EnvironmentType, AppEnvVariables]`
    """

    try:
        if environment is None:
            environment_str = os.getenv("ENVIRONMENT")

            if environment_str is None:
                raise ValueError("ENVIRONMENT environment variable not set.")

            environment = EnvironmentType(environment_str.lower())
    except:  # noqa: E722
        expected_values = [environment_type.value for environment_type in EnvironmentType]
        expected_values_str = ", ".join(expected_values)
        raise ValueError(  # pylint: disable=raise-missing-from
            f"ENVIRONMENT environment variable is invalid - expected: {expected_values_str}"
        )

    if environment is EnvironmentType.PROD:
        if environment in ENVIRONMENT_ENV_FILE_PATHS:
            app_env_variables = AppEnvVariables(
                _env_file=ENVIRONMENT_ENV_FILE_PATHS[environment],
            )
        else:
            app_env_variables = AppEnvVariables()
    else:
        app_env_variables = AppEnvVariables(
            _env_file=ENVIRONMENT_ENV_FILE_PATHS[environment],
        )

    return environment, app_env_variables


def to_camel_cleaned_suffix(field_name: str) -> str:
    """Remove suffix in field name and convert to camel case.

    :param field_name: The field name.
    :type field_name: :class:`str`
    :return: Converted field name.
    :rtype: :class:`str`
    """

    return to_camel(field_name.removesuffix("_"))


def get_database_url(db_settings: AppEnvVariables) -> str:
    """Create a database connection string based on db_settings.

    :param db_settings: Includes the database credentials.
    :type db_settings: :class:`AppEnvVariables`
    :return: A database connection string
    :rtype: :class:`str`

    :raises ValueError: if db_driver in settings is not supported.
    """

    if "postgres" in db_settings.db_driver:
        return f"{db_settings.db_driver}://{db_settings.db_user}:{db_settings.db_password.get_secret_value()}@{db_settings.db_host}:{db_settings.db_port}/{db_settings.db_name}"  # noqa: ignore  # pylint: disable=line-too-long

    raise ValueError(f"Not supported database driver: {db_settings.db_driver}")


@cache
def get_app_data() -> dict[str, Any]:
    """Extract app information from pyproject.toml.

    :return: The app data section from pyproject.toml as dict
    :rtype: :class:`dict[str, Any]`
    """

    pyproject_file_path: Path = Path(__file__).resolve().parent.parent / "pyproject.toml"

    with pyproject_file_path.open(mode="rb") as pyproject_file:
        pyproject_data: dict[str, Any] = tomllib.load(pyproject_file)

    return pyproject_data["tool"]["poetry"]


def equal_dict(
    dict_1: dict[str, Any],
    dict_2: dict[str, Any],
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
    dict_1_filtered: dict[str, Any] = {k: v for k, v in dict_1.items() if k not in exclude_keys}
    dict_2_filtered: dict[str, Any] = {k: v for k, v in dict_2.items() if k not in exclude_keys}

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


def tabulate_str(headers: Sequence, rows: Sequence, show_index: bool = False) -> str:
    """Helper function to get a ascii table based on headers and rows.

    :param headers: The headers of the table.
    :type headers: :class:`Sequence`
    :param rows: The row data of the table.
    :type rows: :class:`Sequence`
    :param show_index: Flag to show indexes in table.
    :type show_index: :class:`bool`
    :return: The generated string table.
    :rtype: :class:`str`
    """

    tabulate.MIN_PADDING = 35
    return tabulate.tabulate(
        headers=headers,
        tabular_data=rows,
        tablefmt="plain",
        showindex=show_index,
    )
