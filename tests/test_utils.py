"""All util functions are tested here."""

import pytest

from src.custom_types import DBSettings
from src.utils import equal_dict, equal_list_of_dict, get_app_data, get_database_url


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


@pytest.mark.dependency
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
def test_equal_dict(dict_1, dict_2, exclude_keys, expected_result):
    assert equal_dict(dict_1, dict_2, exclude_keys) == expected_result


@pytest.mark.dependency
@pytest.mark.parametrize(
    "list_dict_1, list_dict_2, exclude_keys, expected_result",
    [
        # Test case 1: Both lists of dictionaries are identical without exclusion
        ([{"a": 1, "b": 2, "c": 3}], [{"a": 1, "b": 2, "c": 3}], [], True),
        # Test case 2: Lists of dictionaries are identical with exclusion
        ([{"a": 1, "b": 2, "c": 3}], [{"a": 1, "b": 2, "c": 4}], ["c"], True),
        # Test case 3: Lists of dictionaries are different without exclusion
        ([{"a": 1, "b": 2, "c": 3}], [{"a": 1, "b": 3, "c": 3}], [], False),
        # Test case 4: Lists of dictionaries are different with exclusion
        ([{"a": 1, "b": 2, "c": 3}], [{"a": 1, "b": 3, "c": 3}], ["b"], True),
        # Test case 5: Both lists have different dictionaries
        ([{"a": 1, "b": 2}], [{"a": 1, "b": 2}, {"c": 3}], [], False),
        # Test case 6: Both lists have different dictionaries, but keys are excluded
        ([{"a": 1, "b": 2, "d": 4}], [{"a": 1, "b": 2, "e": 5}], ["d", "e"], True),
        # Test case 7: Empty lists of dictionaries
        ([], [], [], True),
        # Test case 8: Empty lists with exclusion
        ([], [], ["a"], True),
        # Test case 9: Different dictionaries in lists with exclusion that does not exist
        ([{"a": 1}], [{"b": 2}], ["c"], False),
    ],
)
def test_equal_list_of_dict(list_dict_1, list_dict_2, exclude_keys, expected_result):
    assert equal_list_of_dict(list_dict_1, list_dict_2, exclude_keys) == expected_result
