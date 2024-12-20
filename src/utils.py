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


def calculate_months_for_reaching_savings_targets(  # noqa: ignore  # pylint: disable=line-too-long, too-many-branches,too-many-statements,too-many-locals
    moneyboxes: list[dict[str, Any]],
    app_settings: dict[str, Any],
    overflow_moneybox_mode: OverflowMoneyboxAutomatedSavingsModeType,
) -> dict[int, list[MoneyboxSavingsMonthData]]:
    """Calculates the reaching savings amount based on moneyboxes and savings_amount.

    Note: moneyboxes with savings_target = None will be ignored and not part of the results.

    :param moneyboxes: The moneyboxes the calculation will be work with.
    :type moneyboxes: :class:`list[dict[str, Any]]`
    :param app_settings: The settings data of the app.
    :type app_settings: :class:`dict[str, Any]`
    :param overflow_moneybox_mode: The current overflow moneybox mode.
    :type overflow_moneybox_mode: :class:`OverflowMoneyboxModeType`
    :return: The calculated months for reaching savings amount. Moneyboxes without
        savings_target will not be part of the results.
    :rtype: :class:`dict[int, list[MoneyboxSavingsMonthData]]`
    """

    if not moneyboxes or not app_settings["is_automated_saving_active"]:
        return {}

    moneyboxes_reached_targets: set[int] = set()
    moneybox_with_savings_target_distribution_data: dict[int, list[MoneyboxSavingsMonthData]] = (
        defaultdict(list)
    )

    moneyboxes_sorted_by_priority: list[dict[str, Any]] = sorted(
        moneyboxes, key=lambda item: item["priority"]
    )

    simulated_month: int = 1
    overflow_moneybox: dict[str, Any] = moneyboxes_sorted_by_priority[0]
    moneyboxes_sorted_by_priority_without_overflow_moneybox: list[dict[str, Any]] = (
        moneyboxes_sorted_by_priority[1:]
    )

    # preprocess:
    # - check if there are moneyboxes, that already reached their savings targets
    for moneybox in moneyboxes_sorted_by_priority_without_overflow_moneybox:
        if (
            moneybox["savings_target"] is not None
            and moneybox["balance"] >= moneybox["savings_target"]
        ):
            moneybox_with_savings_target_distribution_data[moneybox["id"]].append(
                MoneyboxSavingsMonthData(
                    moneybox_id=moneybox["id"],
                    savings_amount=0,
                    month=0,
                )
            )
            moneyboxes_reached_targets.add(moneybox["id"])

    if app_settings["savings_amount"] <= 0:
        return moneybox_with_savings_target_distribution_data

    def all_targets_reached(_moneyboxes: list[dict[str, Any]]) -> bool:
        """Checks whether all moneyboxes with a savings_target have reached their target.

        :param _moneyboxes: List of moneyboxes to evaluate.
        :type _moneyboxes: :class:`list[dict[str, Any]]`
        :return: True if all moneyboxes with a savings_target have reached their target,
            otherwise False.
        :rtype: :class:`bool`
        """

        for _moneybox in _moneyboxes:
            # Skip moneyboxes without a savings_target
            if _moneybox["savings_target"] is None or _moneybox["savings_amount"] <= 0:
                continue

            # Check if the target is still not reached
            if _moneybox["balance"] < _moneybox["savings_target"]:
                return False

        # If all checked moneyboxes have reached their target, return True
        return True

    def total_balances_of_moneyboxes_with_savings_targets(_moneyboxes: list[dict[str, Any]]) -> int:
        return sum(
            _moneybox["balance"]
            for _moneybox in _moneyboxes
            if _moneybox["savings_target"] is not None
        )

    endless: bool = False
    last_total_balances: int = -1

    while not all_targets_reached(
        _moneyboxes=moneyboxes_sorted_by_priority_without_overflow_moneybox,
    ):  # pylint: disable=too-many-nested-blocks
        # mode 2
        if (
            overflow_moneybox_mode
            is OverflowMoneyboxAutomatedSavingsModeType.ADD_TO_AUTOMATED_SAVINGS_AMOUNT
        ):
            current_savings_amount = app_settings["savings_amount"] + overflow_moneybox["balance"]
            overflow_moneybox["balance"] = 0
        else:  # mode 1
            current_savings_amount = app_settings["savings_amount"]

        # distribution algorithm
        for moneybox in moneyboxes_sorted_by_priority_without_overflow_moneybox:
            if moneybox["id"] in moneyboxes_reached_targets:
                continue

            # moneybox["savings_amount"] could be 0, that's ok for the algorithm
            distribution_amount: int = min(current_savings_amount, moneybox["savings_amount"])

            if moneybox["savings_target"] is not None:
                distribution_amount = min(
                    distribution_amount,
                    moneybox["savings_target"] - moneybox["balance"],
                )
            else:
                total_balances: int = total_balances_of_moneyboxes_with_savings_targets(
                    _moneyboxes=moneyboxes_sorted_by_priority_without_overflow_moneybox
                )

                # potential blocker (means, this moneybox has not savings_target set)
                if (
                    moneybox["savings_amount"] >= current_savings_amount
                    and last_total_balances == total_balances
                ):
                    endless = True
                    moneybox["balance"] += distribution_amount
                    current_savings_amount -= distribution_amount
                    break

            if distribution_amount > 0:
                moneybox["balance"] += distribution_amount

                if moneybox["savings_target"] is not None:
                    moneybox_with_savings_target_distribution_data[moneybox["id"]].append(
                        MoneyboxSavingsMonthData(
                            moneybox_id=moneybox["id"],
                            month=simulated_month,
                            savings_amount=distribution_amount,
                        )
                    )

                # target for moneybox reached
                if (
                    moneybox["savings_target"] is not None
                    and moneybox["balance"] >= moneybox["savings_target"]
                ):
                    moneyboxes_reached_targets.add(moneybox["id"])

                current_savings_amount -= distribution_amount

            if current_savings_amount <= 0:
                break

        if current_savings_amount > 0:
            overflow_moneybox["balance"] += current_savings_amount

        # mode 3
        if (
            overflow_moneybox_mode
            is OverflowMoneyboxAutomatedSavingsModeType.FILL_UP_LIMITED_MONEYBOXES
            and overflow_moneybox["balance"] > 0
        ):
            for moneybox in moneyboxes_sorted_by_priority[1:]:
                if moneybox["id"] in moneyboxes_reached_targets:
                    continue

                if moneybox["savings_target"] is not None:
                    amount_till_target: int = moneybox["savings_target"] - moneybox["balance"]
                    distribution_amount = min(amount_till_target, overflow_moneybox["balance"])

                    moneybox["balance"] += distribution_amount
                    moneybox_with_savings_target_distribution_data[moneybox["id"]].append(
                        MoneyboxSavingsMonthData(
                            moneybox_id=moneybox["id"],
                            month=simulated_month,
                            savings_amount=distribution_amount,
                            additional_data="Add amount by fillup-mode from Overflow Moneybox.",
                        )
                    )

                    overflow_moneybox["balance"] -= distribution_amount

                    # target for moneybox reached
                    if moneybox["balance"] >= moneybox["savings_target"]:
                        moneyboxes_reached_targets.add(moneybox["id"])

                if overflow_moneybox["balance"] <= 0:
                    break

        simulated_month += 1
        # build new hash to check in next iteration(month)
        #   if something changed for moneyboxes with a target (amounts were distributed)
        last_total_balances = total_balances_of_moneyboxes_with_savings_targets(
            _moneyboxes=moneyboxes_sorted_by_priority_without_overflow_moneybox
        )

        # postprocess:
        # - all moneyboxes without any savings will never get a saving, set to undefined (-1)
        if endless and not all_targets_reached(
            _moneyboxes=moneyboxes_sorted_by_priority_without_overflow_moneybox,
        ):  # not all targets reached but endless
            for moneybox in moneyboxes_sorted_by_priority_without_overflow_moneybox:
                if (
                    moneybox["savings_target"] is not None
                    and moneybox["balance"] < moneybox["savings_target"]
                ):
                    moneybox_with_savings_target_distribution_data[moneybox["id"]].append(
                        MoneyboxSavingsMonthData(
                            moneybox_id=moneybox["id"],
                            savings_amount=-1,
                            month=-1,
                        )
                    )

            break

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
