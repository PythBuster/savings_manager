"""All util functions are tested here."""

from typing import Any

import pytest

from src.custom_types import AppEnvVariables, OverflowMoneyboxAutomatedSavingsModeType
from src.utils import (
    calculate_months_for_reaching_savings_targets,
    equal_dict,
    get_app_data,
    get_database_url,
)


def test_db_settings() -> None:  # pylint: disable= unused-argument
    db_settings = AppEnvVariables(
        db_driver="postgresql+asyncpg",
        db_name="test_db",
        db_host="mylocalhost",
        db_port=8765,
        db_user="postgres",
        db_password="<PASSWORD>",
        smtp_server="mylocalsmtp",
        smtp_method="TLS",
        smtp_port=1225,
        smtp_user_name="smtp user",
        smtp_password="<PASSWORD>",
        authjwt_secret_key="secret",
        authjwt_cookie_secure=False,
        authjwt_cookie_csrf_protect=False,
        authjwt_cookie_samesite="",
    )

    expected_database_url = "postgresql+asyncpg://postgres:<PASSWORD>@mylocalhost:8765/test_db"
    result_database_url = get_database_url(db_settings)
    assert expected_database_url == result_database_url

    # not supported driver
    unsupported_db_driver = "unknown"
    db_settings = AppEnvVariables(
        db_driver=unsupported_db_driver,
        db_name="test_db",
        db_host="mylocalhost",
        db_port=8765,
        db_user="postgres",
        db_password="<PASSWORD>",
        smtp_server="mylocalsmtp",
        smtp_method="TLS",
        smtp_port=1225,
        smtp_user_name="smtp user",
        smtp_password="<PASSWORD>",
        authjwt_secret_key="secret",
        authjwt_cookie_secure=False,
        authjwt_cookie_csrf_protect=False,
        authjwt_cookie_samesite="",
    )

    with pytest.raises(ValueError) as ex_info:
        get_database_url(db_settings)

    assert f"Not supported database driver: {unsupported_db_driver}" in ex_info.value.args[0]


def test_get_app_data() -> None:
    app_data = get_app_data()
    app_version = app_data["version"]
    major, minor, _ = app_version.split(".")

    int(major)
    int(minor)

    app_name = app_data["name"]
    expected_app_name = "Savings Manager"
    assert app_name == expected_app_name

    description = app_data["description"]
    assert description == (
        "Savings Manager is an intuitive app for managing your savings using "
        "virtual moneyboxes. Allocate budgets, automate savings, and set priorities "
        "to reach goals faster. The app adjusts automatically when you withdraw, "
        "ensuring your plan stays on track. Easily transfer funds between moneyboxes "
        "or make manual deposits, giving you full control over your savings journey."
    )

    authors = app_data["authors"]
    assert len(authors) == 1
    assert "'PythBuster' <'pythbuster@gmail.com'>" == authors[0]


@pytest.mark.parametrize(
    "dict_1, dict_2, exclude_keys, expected_result",
    [
        # Test case 1: Both dictionaries are identical without exclusion
        ({"a": 1, "b": 2, "c": 3}, {"a": 1, "b": 2, "c": 3}, [], True),
        # Test case 2: Dictionaries are identical with exclusion
        ({"a": 1, "b": 2, "c": 3}, {"a": 1, "b": 2, "c": 4}, ["c"], True),
        # Test case 3: Dictionaries are different without exclusion
        ({"a": 1, "b": 2, "c": 3}, {"a": 1, "b": 3, "c": 3}, [], False),
        # Test case 4: Dictionaries are different with exclusion
        ({"a": 1, "b": 2, "c": 3}, {"a": 1, "b": 3, "c": 3}, ["b"], True),
        # Test case 5: Both dictionaries have different additional keys
        ({"a": 1, "b": 2, "d": 4}, {"a": 1, "b": 2, "e": 5}, [], False),
        # Test case 6: Both dictionaries have different additional keys that are excluded
        ({"a": 1, "b": 2, "d": 4}, {"a": 1, "b": 2, "e": 5}, ["d", "e"], True),
        # Test case 7: Empty dictionaries
        ({}, {}, [], True),
        # Test case 8: Empty dictionaries with exclusion
        ({}, {}, ["a"], True),
        # Test case 9: Different dictionaries with exclusion that does not exist
        ({"a": 1}, {"b": 2}, ["c"], False),
    ],
)
def test_equal_dict(
    dict_1: dict[str, Any],
    dict_2: dict[str, Any],
    exclude_keys: list[str],
    expected_result: bool,
) -> None:
    assert equal_dict(dict_1, dict_2, exclude_keys) == expected_result


def test_calculate_months_for_reaching_savings_targets__success__mode_collect() -> None:
    overflow_moneybox_mode = OverflowMoneyboxAutomatedSavingsModeType.COLLECT
    savings_amount = 2000

    moneyboxes: list[dict[str, Any]] = [
        {  # expectation: reached savings target in 5 months
            "id": 3,
            "priority": 1,
            "balance": 0,
            "savings_amount": 2500,
            "savings_target": 10000,
        },
        {  # takes 1000 from month 6 upwards
            "id": 2,
            "priority": 2,
            "balance": 0,
            "savings_amount": 1000,
            "savings_target": None,
        },
        {  # get 1000 from month 6 upwards, expectation: reached target in month 16
            "id": 4,
            "priority": 3,
            "balance": 1000,
            "savings_amount": 5000,
            "savings_target": 10500,
        },
        {  # overflow moneybox
            "id": 1,
            "priority": 0,
            "balance": 0,
            "savings_amount": 0,
            "savings_target": None,
        },
        {  # expectation: reached target directly (month 0)
            "id": 5,
            "priority": 4,
            "balance": 0,
            "savings_amount": 0,
            "savings_target": 0,
        },
        {  # expectation: not part of result, will never reach savings target
            "id": 6,
            "priority": 5,
            "balance": 0,
            "savings_amount": 0,
            "savings_target": 1000,
        },
    ]

    result_1 = calculate_months_for_reaching_savings_targets(
        moneyboxes=moneyboxes,
        app_settings={
            "is_automated_saving_active": True,
            "savings_amount": savings_amount,
        },
        overflow_moneybox_mode=overflow_moneybox_mode,
    )

    assert result_1[3][-1].month == 5
    assert result_1[4][-1].month == 15
    assert result_1[5][-1].month == 0
    assert 1 not in result_1
    assert 6 not in result_1


def test_calculate_months_for_reaching_savings_targets__success__mode_add_to_savings_amount() -> (
    None
):
    overflow_moneybox_mode = (
        OverflowMoneyboxAutomatedSavingsModeType.ADD_TO_AUTOMATED_SAVINGS_AMOUNT
    )
    savings_amount = 5000
    moneyboxes: list[dict[str, Any]] = [
        {  # expectation: reached savings target in 1 month
            "id": 3,
            "priority": 1,
            "balance": 0,
            "savings_amount": 10000,
            "savings_target": 10000,
        },
        {  # takes 1000 from month 1 upwards
            "id": 2,
            "priority": 2,
            "balance": 0,
            "savings_amount": 1000,
            "savings_target": None,
        },
        {  # expectation: reached savings target in 4 months
            "id": 4,
            "priority": 3,
            "balance": 0,
            "savings_amount": 3000,
            "savings_target": 8000,
        },
        {  # overflow moneybox
            # add 10000 to savings_amount for month 1
            "id": 1,
            "priority": 0,
            "balance": 10000,
            "savings_amount": 0,
            "savings_target": None,
        },
    ]

    result_1 = calculate_months_for_reaching_savings_targets(
        moneyboxes=moneyboxes,
        app_settings={
            "is_automated_saving_active": True,
            "savings_amount": savings_amount,
        },
        overflow_moneybox_mode=overflow_moneybox_mode,
    )

    assert result_1[3][-1].month == 1
    assert 1 not in result_1
    assert result_1[4][-1].month == 3


def test_calculate_months_for_reaching_savings_targets__success__mode_fill_up() -> None:
    overflow_moneybox_mode = OverflowMoneyboxAutomatedSavingsModeType.FILL_UP_LIMITED_MONEYBOXES
    savings_amount = 10000
    moneyboxes: list[dict[str, Any]] = [
        {  # expectation: reached savings target in 1 month
            "id": 3,
            "priority": 1,
            "balance": 0,
            "savings_amount": 10000,
            "savings_target": 10000,
        },
        {  # takes 1000 from month 2 upwards
            "id": 2,
            "priority": 2,
            "balance": 0,
            "savings_amount": 1000,
            "savings_target": None,
        },
        {  # expectation: reached savings target in 1 month (filled up from overflow moneybox)
            "id": 4,
            "priority": 3,
            "balance": 0,
            "savings_amount": 2000,
            "savings_target": 10000,
        },
        {  # expectation: reached savings target in 3 months
            "id": 5,
            "priority": 4,
            "balance": 0,
            "savings_amount": 1000,
            "savings_target": 5000,
        },
        {  # overflow moneybox
            # fill up moneybox 4
            "id": 1,
            "priority": 0,
            "balance": 10000,
            "savings_amount": 0,
            "savings_target": None,
        },
    ]

    result_1 = calculate_months_for_reaching_savings_targets(
        moneyboxes=moneyboxes,
        app_settings={
            "is_automated_saving_active": True,
            "savings_amount": savings_amount,
        },
        overflow_moneybox_mode=overflow_moneybox_mode,
    )

    assert result_1[3][-1].month == 1
    assert 1 not in result_1
    assert result_1[4][-1].month == 1
    assert result_1[5][-1].month == 2


def test_calculate_months_for_reaching_savings_targets__success__empty_result_caused_by_empty_moneyboxes() -> (
    None
):
    overflow_moneybox_mode = OverflowMoneyboxAutomatedSavingsModeType.FILL_UP_LIMITED_MONEYBOXES
    savings_amount = 10000
    moneyboxes: list[dict[str, Any]] = []

    result = calculate_months_for_reaching_savings_targets(
        moneyboxes=moneyboxes,
        app_settings={
            "is_automated_saving_active": True,
            "savings_amount": savings_amount,
        },
        overflow_moneybox_mode=overflow_moneybox_mode,
    )
    assert result == {}


def test_calculate_months_for_reaching_savings_targets__success__empty_result_caused_by_savings_amount_of_zero() -> (
    None
):
    overflow_moneybox_mode = OverflowMoneyboxAutomatedSavingsModeType.FILL_UP_LIMITED_MONEYBOXES
    savings_amount = 0
    moneyboxes: list[dict[str, Any]] = [
        {  # expectation: reached savings target in 1 month
            "id": 3,
            "priority": 1,
            "balance": 0,
            "savings_amount": 10000,
            "savings_target": 10000,
        },
        {  # takes 1000 from month 2 upwards
            "id": 2,
            "priority": 2,
            "balance": 0,
            "savings_amount": 1000,
            "savings_target": None,
        },
        {  # expectation: reached savings target in 1 month (filled up from overflow moneybox)
            "id": 4,
            "priority": 3,
            "balance": 0,
            "savings_amount": 2000,
            "savings_target": 10000,
        },
        {  # expectation: reached savings target in 3 months
            "id": 5,
            "priority": 4,
            "balance": 0,
            "savings_amount": 1000,
            "savings_target": 5000,
        },
        {  # overflow moneybox
            # fill up moneybox 4
            "id": 1,
            "priority": 0,
            "balance": 10000,
            "savings_amount": 0,
            "savings_target": None,
        },
    ]

    result = calculate_months_for_reaching_savings_targets(
        moneyboxes=moneyboxes,
        app_settings={
            "is_automated_saving_active": True,
            "savings_amount": savings_amount,
        },
        overflow_moneybox_mode=overflow_moneybox_mode,
    )
    assert result == {}


def test_calculate_months_for_reaching_savings_targets__success__empty_result_caused_by_negative_savings_amount() -> (
    None
):
    overflow_moneybox_mode = OverflowMoneyboxAutomatedSavingsModeType.FILL_UP_LIMITED_MONEYBOXES
    savings_amount = -1
    moneyboxes: list[dict[str, Any]] = [
        {  # expectation: reached savings target in 1 month
            "id": 3,
            "priority": 1,
            "balance": 0,
            "savings_amount": 10000,
            "savings_target": 10000,
        },
        {  # takes 1000 from month 2 upwards
            "id": 2,
            "priority": 2,
            "balance": 0,
            "savings_amount": 1000,
            "savings_target": None,
        },
        {  # expectation: reached savings target in 1 month (filled up from overflow moneybox)
            "id": 4,
            "priority": 3,
            "balance": 0,
            "savings_amount": 2000,
            "savings_target": 10000,
        },
        {  # expectation: reached savings target in 3 months
            "id": 5,
            "priority": 4,
            "balance": 0,
            "savings_amount": 1000,
            "savings_target": 5000,
        },
        {  # overflow moneybox
            # fill up moneybox 4
            "id": 1,
            "priority": 0,
            "balance": 10000,
            "savings_amount": 0,
            "savings_target": None,
        },
    ]

    result = calculate_months_for_reaching_savings_targets(
        moneyboxes=moneyboxes,
        app_settings={
            "is_automated_saving_active": True,
            "savings_amount": savings_amount,
        },
        overflow_moneybox_mode=overflow_moneybox_mode,
    )
    assert result == {}


def test_calculate_months_for_reaching_savings_targets__success__monthly_savings_amount_0__init_reached_target() -> (
    None
):
    overflow_moneybox_mode = OverflowMoneyboxAutomatedSavingsModeType.FILL_UP_LIMITED_MONEYBOXES
    savings_amount = 0
    moneyboxes: list[dict[str, Any]] = [
        {  # expectation: reached savings target in 1 month
            "id": 3,
            "priority": 1,
            "balance": 10000,  # initial full
            "savings_amount": 500,
            "savings_target": 10000,
        },
        {  # takes 1000 from month 2 upwards
            "id": 2,
            "priority": 2,
            "balance": 0,
            "savings_amount": 1000,
            "savings_target": None,
        },
        {  # overflow moneybox
            "id": 1,
            "priority": 0,
            "balance": 0,
            "savings_amount": 0,
            "savings_target": None,
        },
    ]

    result = calculate_months_for_reaching_savings_targets(
        moneyboxes=moneyboxes,
        app_settings={
            "is_automated_saving_active": True,
            "savings_amount": savings_amount,
        },
        overflow_moneybox_mode=overflow_moneybox_mode,
    )

    assert result[3][-1].month == 0
    assert 2 not in result
