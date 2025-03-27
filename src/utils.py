"""All helper functions are located here."""

import os
import tomllib
from collections import defaultdict
from functools import cache
from pathlib import Path
from typing import Any, Sequence

import tabulate
from dictalchemy import asdict
from pydantic.alias_generators import to_camel

from src.constants import ENVIRONMENT_ENV_FILE_PATHS
from src.custom_types import (
    AppEnvVariables,
    DBViolationErrorType,
    EnvironmentType,
    MoneyboxSavingsMonthData,
    OverflowMoneyboxAutomatedSavingsModeType,
)


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


def as_dict(  # type: ignore  # noqa: ignore  # pylint: disable=missing-function-docstring, too-many-arguments, too-many-positional-arguments
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
    """Helper function to get an ascii table based on headers and rows.

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


def calculate_savings_forecast(  # noqa: E501  # pylint: disable=line-too-long, too-many-locals, too-many-branches, too-many-statements
    moneyboxes: list[dict[str, Any]],
    app_settings: dict[str, Any],
    overflow_moneybox_mode: OverflowMoneyboxAutomatedSavingsModeType,
) -> dict[int, list[MoneyboxSavingsMonthData]]:
    """Calculates a forecast for each moneybox, including the estimated month the savings target
    will be reached and the monthly allocated amounts over the next months.

    :param moneyboxes: The moneyboxes the calculation will be work with.
    :param app_settings: The settings data of the app.
    :param overflow_moneybox_mode: The current overflow moneybox mode.
    :return: The calculated months for reaching savings amount. The Overflow Moneybox
        is not a part of the results.
    :raises: ValueError: if overflow mode is unknown.
    """

    if not moneyboxes or not app_settings["is_automated_saving_active"]:
        return {}

    def _get_active_moneyboxes_with_targets(
        _moneyboxes: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        return [
            mb
            for mb in _moneyboxes
            if mb["savings_target"] is not None
            and mb["balance"] < mb["savings_target"]
            and (
                mb["savings_amount"] > 0
                or (
                    overflow_moneybox_mode
                    == OverflowMoneyboxAutomatedSavingsModeType.FILL_UP_LIMITED_MONEYBOXES
                    and overflow_moneybox["balance"] > 0
                )
            )
            and mb["id"] != overflow_moneybox["id"]
        ]

    def _total_balances_with_targets(_moneyboxes: list[dict[str, Any]]) -> int:
        return sum(mb["balance"] for mb in _moneyboxes if mb["savings_target"] is not None)

    def _amount_until_target(mb: dict[str, Any]) -> int:
        return max(0, mb["savings_target"] - mb["balance"])

    def _distribute_amount(mb: dict[str, Any], amount: int, month: int) -> None:
        mb["balance"] += amount
        history = moneybox_with_savings_target_distribution_data[mb["id"]]

        if history and history[-1].month == month:
            prev_amount = history[-1].amount or 0
            history[-1] = MoneyboxSavingsMonthData(
                moneybox_id=mb["id"], month=month, amount=prev_amount + amount
            )
        else:
            history.append(
                MoneyboxSavingsMonthData(moneybox_id=mb["id"], month=month, amount=amount)
            )

    moneyboxes_reached_targets: set[int] = set()
    moneybox_with_savings_target_distribution_data: dict[int, list[MoneyboxSavingsMonthData]] = (
        defaultdict(list)
    )
    moneyboxes_sorted = sorted(moneyboxes, key=lambda item: item["priority"])
    overflow_moneybox = moneyboxes_sorted[0]
    moneyboxes_main = moneyboxes_sorted[1:]

    for mb in moneyboxes_main:
        if mb["savings_target"] is not None and mb["balance"] >= mb["savings_target"]:
            moneybox_with_savings_target_distribution_data[mb["id"]].append(
                MoneyboxSavingsMonthData(moneybox_id=mb["id"], amount=None, month=0)
            )
            moneyboxes_reached_targets.add(mb["id"])

    additive_modes = {
        OverflowMoneyboxAutomatedSavingsModeType.ADD_TO_AUTOMATED_SAVINGS_AMOUNT,
        OverflowMoneyboxAutomatedSavingsModeType.FILL_UP_LIMITED_MONEYBOXES,
    }

    has_amount = (
        (overflow_moneybox["balance"] + app_settings["savings_amount"])
        if overflow_moneybox_mode in additive_modes
        else app_settings["savings_amount"]
    ) > 0

    if not has_amount:
        for mb in moneyboxes_main:
            if mb["id"] not in moneyboxes_reached_targets:
                moneybox_with_savings_target_distribution_data[mb["id"]].append(
                    MoneyboxSavingsMonthData(moneybox_id=mb["id"], amount=None, month=-1)
                )
        return moneybox_with_savings_target_distribution_data

    simulated_month = 1
    last_known_total_balances = -1

    while _get_active_moneyboxes_with_targets(moneyboxes_main):
        match overflow_moneybox_mode:
            case OverflowMoneyboxAutomatedSavingsModeType.COLLECT:
                current_savings_amount = app_settings["savings_amount"]
            case OverflowMoneyboxAutomatedSavingsModeType.ADD_TO_AUTOMATED_SAVINGS_AMOUNT:
                current_savings_amount = (
                    app_settings["savings_amount"] + overflow_moneybox["balance"]
                )
                overflow_moneybox["balance"] = 0
            case OverflowMoneyboxAutomatedSavingsModeType.FILL_UP_LIMITED_MONEYBOXES:
                current_savings_amount = app_settings["savings_amount"]
            case _:
                raise ValueError(f"Unsupported overflow moneybox mode {overflow_moneybox_mode=}")

        for mb in moneyboxes_main:
            if mb["id"] in moneyboxes_reached_targets:
                continue

            dist_amount = min(current_savings_amount, mb["savings_amount"])

            if mb["savings_target"] is not None:
                dist_amount = min(dist_amount, _amount_until_target(mb))

            if dist_amount > 0:
                _distribute_amount(mb, dist_amount, simulated_month)

                if mb["savings_target"] is not None and mb["balance"] >= mb["savings_target"]:
                    moneyboxes_reached_targets.add(mb["id"])

                current_savings_amount -= dist_amount

            if current_savings_amount <= 0:
                break

        if current_savings_amount > 0:
            overflow_moneybox["balance"] += current_savings_amount

        if (
            overflow_moneybox_mode
            is OverflowMoneyboxAutomatedSavingsModeType.FILL_UP_LIMITED_MONEYBOXES
        ):
            for mb in _get_active_moneyboxes_with_targets(moneyboxes_main):
                dist_amount = min(_amount_until_target(mb), overflow_moneybox["balance"])

                if dist_amount > 0:
                    _distribute_amount(mb, dist_amount, simulated_month)
                    overflow_moneybox["balance"] -= dist_amount

                    if mb["savings_target"] is not None and mb["balance"] >= mb["savings_target"]:
                        moneyboxes_reached_targets.add(mb["id"])

                    if overflow_moneybox["balance"] <= 0:
                        break

        simulated_month += 1
        current_total_balances = _total_balances_with_targets(moneyboxes_main)

        if current_total_balances == last_known_total_balances:
            break

        last_known_total_balances = current_total_balances

    non_target_reached_moneybox_ids = [
        mb["id"] for mb in _get_active_moneyboxes_with_targets(moneyboxes_main)
    ]

    for mb in moneyboxes_main:
        if (
            mb["savings_target"] is None
            or (mb["savings_target"] > 0 and mb["savings_amount"] == 0)
            or mb["id"] in non_target_reached_moneybox_ids
        ):
            moneybox_with_savings_target_distribution_data[mb["id"]].append(
                MoneyboxSavingsMonthData(moneybox_id=mb["id"], amount=None, month=-1)
            )

    return moneybox_with_savings_target_distribution_data


async def extract_database_violation_error(error_message: str) -> DBViolationErrorType:
    """Extracts the database violation error from the given error message.

    :param error_message: The str of the exception as error message to extract the
        database violation error. str(exception)
    :type error_message: :class:`str`
    :return: The mapped enum type of the database violation error, if no match found, returns
        DBViolationErrorType.UNKNOWN.
    :rtype: :class:`DBViolationErrorType`
    """

    if "ck_app_settings_send_reports_via_email_requires_email_address" in error_message:
        return DBViolationErrorType.SET_REPORTS_VIA_EMAIL_BUT_NO_EMAIL_ADDRESS

    return DBViolationErrorType.UNKNOWN
