"""All util functions are tested here."""

import pytest

from src.custom_types import DBSettings
from src.utils import get_app_data, get_database_url


@pytest.mark.dependency
async def test_db_settings(db_settings_1: DBSettings) -> None:
    # sqlite as file
    db_settings = DBSettings(
        db_driver="sqlite",
        db_file="test.db",
    )

    expected_database_url = "sqlite:///test.db"
    result_database_url = get_database_url(db_settings)
    assert expected_database_url == result_database_url

    # sqlite in memory
    db_settings = DBSettings(
        db_driver="sqlite",
        db_file=":memory:",
    )

    expected_database_url = "sqlite:///:memory:"
    result_database_url = get_database_url(db_settings)
    assert expected_database_url == result_database_url

    # not supported driver
    db_settings = DBSettings(
        db_driver="unknown",
        db_file="123",
    )

    with pytest.raises(ValueError) as ex_info:
        get_database_url(db_settings)

    assert "Not supported database driver." in ex_info.value.args[0]


@pytest.mark.dependency
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
    assert description == "Manage your savings on your physical account via the app."

    authors = app_data["authors"]
    assert len(authors) == 1
    assert "'PythBuster' <'pythbuster@gmail.com'>" == authors[0]
