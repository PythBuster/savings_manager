"""All util functions are tested here."""

import pytest

from src.custom_types import DBSettings
from src.utils import get_database_url


@pytest.mark.dependency
async def test_db_settings(db_settings_1: DBSettings) -> None:
    # sqlite as file
    db_settings = DBSettings(
        db_driver="sqlite",
        db_name="test.db",
        in_memory=False,
    )

    expected_database_url = "sqlite:///test.db"
    result_database_url = get_database_url(db_settings)
    assert expected_database_url == result_database_url

    # sqlite in memory
    db_settings = DBSettings(
        db_driver="sqlite",
        db_name="test.db",
        in_memory=True,
    )

    expected_database_url = "sqlite://"
    result_database_url = get_database_url(db_settings)
    assert expected_database_url == result_database_url

    # postgres
    db_settings = db_settings_1
    db_settings.db_driver = "postgres"

    expected_database_url = "postgres://test_user:test_password@1.2.3.4:1234/test_db"
    result_database_url = get_database_url(db_settings)
    assert expected_database_url == result_database_url

    # not supported driver
    db_settings = DBSettings(
        db_driver="unknown",
    )

    with pytest.raises(ValueError) as ex_info:
        get_database_url(db_settings)

    assert "Not supported database driver." in ex_info.value.args[0]
