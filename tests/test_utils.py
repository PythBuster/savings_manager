"""All util functions are tested here."""

from typing import Any

import pytest

from src.custom_types import AppEnvVariables
from src.utils import equal_dict, get_app_data, get_database_url


def test_db_settings() -> None:  # pylint: disable= unused-argument
    db_settings = AppEnvVariables(
        environment="test",
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
    )

    expected_database_url = "postgresql+asyncpg://postgres:<PASSWORD>@mylocalhost:8765/test_db"
    result_database_url = get_database_url(db_settings)
    assert expected_database_url == result_database_url

    # not supported driver
    unsupported_db_driver = "unknown"
    db_settings = AppEnvVariables(
        environment="test",
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
