"""All util functions are tested here."""

from typing import Any

import pytest

from src.custom_types import AppEnvVariables, OverflowMoneyboxAutomatedSavingsModeType
from src.utils import (
    calculate_savings_forecast,
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


def create_test_moneyboxes(overflow_balance: int) -> list[dict[str, Any]]:
    return [
        {  # overflow moneybox
            "id": 1,
            "priority": 0,
            "balance": overflow_balance,
            "savings_amount": 0,
            "savings_target": None,
        },
        {  # reached at init
            "id": 2,
            "priority": 1,
            "balance": 1000,
            "savings_amount": 500,
            "savings_target": 1000,
        },
        {  # will reach target over time: needs 3 × 1000 => last payment in month 2 (0-based)
            "id": 3,
            "priority": 2,
            "balance": 0,
            "savings_amount": 1000,
            "savings_target": 3000,
        },
        {  # no target
            "id": 4,
            "priority": 3,
            "balance": 0,
            "savings_amount": 1000,
            "savings_target": None,
        },
        {  # unreachable
            "id": 5,
            "priority": 4,
            "balance": 0,
            "savings_amount": 0,
            "savings_target": 1000,
        },
    ]


@pytest.mark.parametrize(
    "savings_amount, overflow_balance, mode, expected",
    [
        # COLLECT
        (1000, 0, OverflowMoneyboxAutomatedSavingsModeType.COLLECT, {2: 0, 3: 3, 4: None, 5: None}),
        (0, 0, OverflowMoneyboxAutomatedSavingsModeType.COLLECT, {2: 0, 3: None, 4: None, 5: None}),
        (
            0,
            250,
            OverflowMoneyboxAutomatedSavingsModeType.COLLECT,
            {2: 0, 3: None, 4: None, 5: None},
        ),
        (
            1000,
            3000,
            OverflowMoneyboxAutomatedSavingsModeType.COLLECT,
            {2: 0, 3: 3, 4: None, 5: None},
        ),
        # ADD
        (
            1000,
            0,
            OverflowMoneyboxAutomatedSavingsModeType.ADD_TO_AUTOMATED_SAVINGS_AMOUNT,
            {2: 0, 3: 3, 4: None, 5: None},
        ),
        (
            0,
            0,
            OverflowMoneyboxAutomatedSavingsModeType.ADD_TO_AUTOMATED_SAVINGS_AMOUNT,
            {2: 0, 3: None, 4: None, 5: None},
        ),
        (
            0,
            250,
            OverflowMoneyboxAutomatedSavingsModeType.ADD_TO_AUTOMATED_SAVINGS_AMOUNT,
            {2: 0, 3: None, 4: None, 5: None},
        ),
        (
            1000,
            3000,
            OverflowMoneyboxAutomatedSavingsModeType.ADD_TO_AUTOMATED_SAVINGS_AMOUNT,
            {2: 0, 3: 3, 4: None, 5: None},
        ),
        # FILL
        (
            1000,
            0,
            OverflowMoneyboxAutomatedSavingsModeType.FILL_UP_LIMITED_MONEYBOXES,
            {2: 0, 3: 3, 4: None, 5: None},
        ),
        (
            0,
            0,
            OverflowMoneyboxAutomatedSavingsModeType.FILL_UP_LIMITED_MONEYBOXES,
            {2: 0, 3: None, 4: None, 5: None},
        ),
        (
            0,
            250,
            OverflowMoneyboxAutomatedSavingsModeType.FILL_UP_LIMITED_MONEYBOXES,
            {2: 0, 3: None, 4: None, 5: None},
        ),
        (
            1000,
            3000,
            OverflowMoneyboxAutomatedSavingsModeType.FILL_UP_LIMITED_MONEYBOXES,
            {2: 0, 3: 1, 4: None, 5: None},
        ),
    ],
)
def test_calculate_savings_forecast__all_combinations(
    savings_amount: int,
    overflow_balance: int,
    mode: OverflowMoneyboxAutomatedSavingsModeType,
    expected: dict[int, int | None],
) -> None:
    result = calculate_savings_forecast(
        moneyboxes=create_test_moneyboxes(overflow_balance),
        app_settings={
            "is_automated_saving_active": True,
            "savings_amount": savings_amount,
        },
        overflow_moneybox_mode=mode,
    )

    assert 1 not in result  # overflow moneybox is excluded from result

    for moneybox_id, expected_month in expected.items():
        assert moneybox_id in result
        last_month = result[moneybox_id][-1].month
        if expected_month is None:
            assert last_month == -1
        else:
            assert (
                last_month == expected_month
            ), f"Moneybox {moneybox_id}: expected month {expected_month}, got {last_month}"
