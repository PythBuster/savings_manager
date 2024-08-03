"""All moneybox response model tests are located here."""

from datetime import datetime
from typing import Any

import pytest
from pydantic import ValidationError

from src.data_classes.responses import MoneyboxResponse


@pytest.mark.parametrize(
    "data",
    [
        {
            "id": 1,
            "name": "Holiday",
            "balance": 1000,
            "created_at": "2020-05-01T00:00:00Z",
            "modified_at": None,
        },
        {
            "id": 2,
            "name": "Holymoly",
            "balance": 1234,
            "created_at": "2020-05-01T00:00:00Z",
            "modified_at": "2020-06-01T00:00:00Z",
        },
    ],
)
def test_moneybox_response_valid_data(data: dict[str, Any]) -> None:
    """Test valid MoneyboxResponse creation."""

    data_id = data["id"]
    data_name = data["name"]
    data_balance = data["balance"]
    data_created_at = datetime.fromisoformat(data["created_at"])
    data_modified_at = (
        datetime.fromisoformat(data["modified_at"]) if data["modified_at"] is not None else None
    )

    response = MoneyboxResponse(**data)

    assert response.id == data_id
    assert response.name == data_name
    assert response.balance == data_balance
    assert response.created_at == data_created_at
    assert response.modified_at == data_modified_at


@pytest.mark.parametrize(
    "data",
    [
        {
            "id": "one",  # Invalid id, should be type int
            "name": "Holiday",
            "balance": 1000,
            "created_at": "2020-05-01T00:00:00Z",
            "modified_at": None,
        },
        {
            "id": "1",  # Invalid id, should be type int
            "name": "Holiday",
            "balance": 1000,
            "created_at": "2020-05-01T00:00:00Z",
            "modified_at": None,
        },
        {
            "id": "jkhalkjghaökdsghdsg",  # Invalid id, should be type int
            "name": "Holiday",
            "balance": 1000,
            "created_at": "2020-05-01T00:00:00Z",
            "modified_at": None,
        },
    ],
)
def test_moneybox_response_invalid_id__non_int_type(data: dict[str, Any]) -> None:
    """Test MoneyboxResponse creation with invalid id."""

    with pytest.raises(ValidationError):
        MoneyboxResponse(**data)


def test_moneybox_response_invalid_name__minlength() -> None:
    """Test MoneyboxResponse creation with invalid name."""

    data = {
        "id": 1,
        "name": "",  # Invalid name, should be at least 1 character
        "balance": 1000,
        "created_at": "2020-05-01T00:00:00Z",
        "modified_at": None,
    }
    with pytest.raises(ValidationError):
        MoneyboxResponse(**data)


def test_moneybox_response_invalid_name__wrong_type() -> None:
    """Test MoneyboxResponse creation with invalid name."""

    data = {
        "id": 1,
        "name": 234423,  # Invalid name, should be a str and at least 1 character
        "balance": 1000,
        "created_at": "2020-05-01T00:00:00Z",
        "modified_at": None,
    }
    with pytest.raises(ValidationError):
        MoneyboxResponse(**data)


def test_moneybox_response_invalid_balance__negative() -> None:
    """Test MoneyboxResponse creation with invalid balance."""

    data = {
        "id": 1,
        "name": "Holiday",
        "balance": -1,  # Invalid balance, should be >= 0
        "created_at": "2020-05-01T00:00:00Z",
        "modified_at": None,
    }

    with pytest.raises(ValidationError):
        MoneyboxResponse(**data)


def test_moneybox_response_valid_balance__zero() -> None:
    """Test MoneyboxResponse creation with invalid balance."""

    data = {
        "id": 1,
        "name": "Holiday",
        "balance": 0,
        "created_at": "2020-05-01T00:00:00Z",
        "modified_at": None,
    }

    response = MoneyboxResponse(**data)

    assert response.id == 1
    assert response.name == "Holiday"
    assert response.balance == 0
    assert response.created_at == datetime.fromisoformat("2020-05-01T00:00:00Z")
    assert response.modified_at is None


def test_moneybox_response_invalid_balance__wrong_type() -> None:
    """Test MoneyboxResponse creation with invalid balance."""

    data = {
        "id": 1,
        "name": "Holiday",
        "balance": "zero",  # Invalid balance, should be an int and >= 0
        "created_at": "2020-05-01T00:00:00Z",
        "modified_at": None,
    }

    with pytest.raises(ValidationError):
        MoneyboxResponse(**data)


def test_moneybox_response_invalid_date_order() -> None:
    """Test MoneyboxResponse creation with invalid date order."""

    data = {
        "id": 1,
        "name": "Holiday",
        "balance": 1000,
        "created_at": "2020-05-02T00:00:00Z",
        "modified_at": "2020-05-01T00:00:00Z",  # Invalid order, modified_at is before created_at
    }
    with pytest.raises(ValueError, match="Error: 'created_at' comes after 'modified_at'."):
        MoneyboxResponse(**data)


def test_moneybox_response_invalid_date__modified_at_wrong_type__int() -> None:
    """Test MoneyboxResponse creation with invalid modified_at date value."""

    data = {
        "id": 1,
        "name": "Holiday",
        "balance": 1000,
        "created_at": "2020-05-02T00:00:00Z",
        "modified_at": 2,
    }

    with pytest.raises(ValueError):
        MoneyboxResponse(**data)


def test_moneybox_response_invalid_date__modified_at_string_type__not_isoformat_datetime() -> None:
    """Test MoneyboxResponse creation with invalid modified_at date value."""

    data = {
        "id": 1,
        "name": "Holiday",
        "balance": 1000,
        "created_at": "2020-05-02T00:00:00Z",
        "modified_at": "2",
    }

    with pytest.raises(ValueError):
        MoneyboxResponse(**data)


def test_moneybox_response_invalid_date__created_at_wrong_type__int() -> None:
    """Test MoneyboxResponse creation with invalid created_at date value."""

    data = {
        "id": 1,
        "name": "Holiday",
        "balance": 1000,
        "created_at": 2,
        "modified_at": "2020-05-02T00:00:00Z",
    }

    with pytest.raises(ValueError):
        MoneyboxResponse(**data)


def test_moneybox_response_invalid_date__created_at_string_type__not_isoformat_datetime() -> None:
    """Test MoneyboxResponse creation with invalid created_at date value."""

    data = {
        "id": 1,
        "name": "Holiday",
        "balance": 1000,
        "created_at": "2",
        "modified_at": "2020-05-02T00:00:00Z",
    }

    with pytest.raises(ValueError):
        MoneyboxResponse(**data)


def test_moneybox_response_invalid_date__none_for_created_at() -> None:
    """Test MoneyboxResponse creation with invalid date order."""

    data = {
        "id": 1,
        "name": "Holiday",
        "balance": 1000,
        "created_at": None,  # Invalid, has to be a datetime or iso string datetime
        "modified_at": "2020-05-01T00:00:00",
    }
    with pytest.raises(ValueError):
        MoneyboxResponse(**data)


def test_moneybox_response_valid_date_order() -> None:
    """Test MoneyboxResponse creation with valid date order."""

    data = {
        "id": 1,
        "name": "Holiday",
        "balance": 1000,
        "created_at": "2020-05-01T00:00:00Z",
        "modified_at": "2020-05-02T00:00:00Z",  # Valid order, modified_at is after created_at
    }
    response = MoneyboxResponse(**data)
    assert response.modified_at > response.created_at
