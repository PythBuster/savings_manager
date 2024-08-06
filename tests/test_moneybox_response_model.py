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
            "savings_amount": 0,
            "savings_target": None,
            "priority": 1,
        },
        {
            "id": 2,
            "name": "Holymoly",
            "balance": 1234,
            "created_at": "2020-05-01T00:00:00Z",
            "modified_at": "2020-06-01T00:00:00Z",
            "savings_amount": 0,
            "savings_target": None,
            "priority": 2,
        },
    ],
)
async def test_moneybox_response_valid_data(data: dict[str, Any]) -> None:
    """Test valid MoneyboxResponse creation."""

    data_id = data["id"]
    data_name = data["name"]
    data_balance = data["balance"]
    data_created_at = datetime.fromisoformat(data["created_at"])
    data_modified_at = (
        datetime.fromisoformat(data["modified_at"]) if data["modified_at"] is not None else None
    )
    data_savings_amount = data["savings_amount"]
    data_savings_target = data["savings_target"]
    data_priority = data["priority"]

    response = MoneyboxResponse(**data)

    assert response.id == data_id
    assert response.name == data_name
    assert response.balance == data_balance
    assert response.created_at == data_created_at
    assert response.modified_at == data_modified_at
    assert response.savings_amount == data_savings_amount
    assert response.savings_target == data_savings_target
    assert response.priority == data_priority


@pytest.mark.parametrize(
    "data",
    [
        {
            "id": "one",  # Invalid id, should be type int
            "name": "Holiday",
            "balance": 1000,
            "created_at": "2020-05-01T00:00:00Z",
            "modified_at": None,
            "savings_amount": 0,
            "savings_target": None,
            "priority": 1,
        },
        {
            "id": "1",  # Invalid id, should be type int
            "name": "Holiday",
            "balance": 1000,
            "created_at": "2020-05-01T00:00:00Z",
            "modified_at": None,
            "savings_amount": 0,
            "savings_target": None,
            "priority": 1,
        },
        {
            "id": "jkhalkjghaökdsghdsg",  # Invalid id, should be type int
            "name": "Holiday",
            "balance": 1000,
            "created_at": "2020-05-01T00:00:00Z",
            "modified_at": None,
            "savings_amount": 0,
            "savings_target": None,
            "priority": 1,
        },
    ],
)
async def test_moneybox_response_invalid_id__non_int_type(data: dict[str, Any]) -> None:
    """Test MoneyboxResponse creation with invalid id."""

    with pytest.raises(ValidationError):
        MoneyboxResponse(**data)


async def test_moneybox_response_invalid_name__minlength() -> None:
    """Test MoneyboxResponse creation with invalid name."""

    data = {
        "id": 1,
        "name": "",  # Invalid name, should be at least 1 character
        "balance": 1000,
        "created_at": "2020-05-01T00:00:00Z",
        "modified_at": None,
        "savings_amount": 0,
        "savings_target": None,
        "priority": 1,
    }
    with pytest.raises(ValidationError):
        MoneyboxResponse(**data)


async def test_moneybox_response_invalid_name__wrong_type() -> None:
    """Test MoneyboxResponse creation with invalid name."""

    data = {
        "id": 1,
        "name": 234423,  # Invalid name, should be a str and at least 1 character
        "balance": 1000,
        "created_at": "2020-05-01T00:00:00Z",
        "modified_at": None,
        "savings_amount": 0,
        "savings_target": None,
        "priority": 1,
    }
    with pytest.raises(ValidationError):
        MoneyboxResponse(**data)


async def test_moneybox_response_invalid_balance__negative() -> None:
    """Test MoneyboxResponse creation with invalid balance."""

    data = {
        "id": 1,
        "name": "Holiday",
        "balance": -1,  # Invalid balance, should be >= 0
        "created_at": "2020-05-01T00:00:00Z",
        "modified_at": None,
        "savings_amount": 0,
        "savings_target": None,
        "priority": 1,
    }

    with pytest.raises(ValidationError):
        MoneyboxResponse(**data)


async def test_moneybox_response_valid_balance__zero() -> None:
    """Test MoneyboxResponse creation with invalid balance."""

    data = {
        "id": 1,
        "name": "Holiday",
        "balance": 0,
        "created_at": "2020-05-01T00:00:00Z",
        "modified_at": None,
        "savings_amount": 0,
        "savings_target": None,
        "priority": 1,
    }

    response = MoneyboxResponse(**data)

    assert response.id == 1
    assert response.name == "Holiday"
    assert response.balance == 0
    assert response.created_at == datetime.fromisoformat("2020-05-01T00:00:00Z")
    assert response.modified_at is None
    assert response.savings_amount == 0
    assert response.savings_target is None
    assert response.priority == 1


async def test_moneybox_response_invalid_balance__wrong_type() -> None:
    """Test MoneyboxResponse creation with invalid balance."""

    data = {
        "id": 1,
        "name": "Holiday",
        "balance": "zero",  # Invalid balance, should be an int and >= 0
        "created_at": "2020-05-01T00:00:00Z",
        "modified_at": None,
        "savings_amount": 0,
        "savings_target": None,
        "priority": 1,
    }

    with pytest.raises(ValidationError):
        MoneyboxResponse(**data)


async def test_moneybox_response_invalid_savings_amount__negative() -> None:
    """Test MoneyboxResponse creation with invalid savings_amount."""

    data = {
        "id": 1,
        "name": "Holiday",
        "balance": 10,  # Invalid balance, should be >= 0
        "created_at": "2020-05-01T00:00:00Z",
        "modified_at": None,
        "savings_amount": -10,
        "savings_target": None,
        "priority": 1,
    }

    with pytest.raises(ValidationError):
        MoneyboxResponse(**data)


async def test_moneybox_response_valid_savings_amount__zero() -> None:
    """Test MoneyboxResponse creation with invalid saving_amount."""

    data = {
        "id": 1,
        "name": "Holiday",
        "balance": 10,
        "created_at": "2020-05-01T00:00:00Z",
        "modified_at": None,
        "savings_amount": 0,
        "savings_target": None,
        "priority": 1,
    }

    response = MoneyboxResponse(**data)

    assert response.id == 1
    assert response.name == "Holiday"
    assert response.balance == 10
    assert response.created_at == datetime.fromisoformat("2020-05-01T00:00:00Z")
    assert response.modified_at is None
    assert response.savings_amount == 0
    assert response.savings_target is None
    assert response.priority == 1


async def test_moneybox_response_invalid_balance__wrong_type__string_number() -> None:
    """Test MoneyboxResponse creation with invalid balance."""

    data = {
        "id": 1,
        "name": "Holiday",
        "balance": 0,
        "created_at": "2020-05-01T00:00:00Z",
        "modified_at": None,
        "savings_amount": "zero",
        "savings_target": None,
        "priority": 1,
    }

    with pytest.raises(ValidationError):
        MoneyboxResponse(**data)


async def test_moneybox_response_invalid_balance__wrong_type__str_int() -> None:
    """Test MoneyboxResponse creation with invalid balance."""

    data = {
        "id": 1,
        "name": "Holiday",
        "balance": 0,
        "created_at": "2020-05-01T00:00:00Z",
        "modified_at": None,
        "savings_amount": "0",
        "savings_target": None,
        "priority": 1,
    }

    with pytest.raises(ValidationError):
        MoneyboxResponse(**data)


async def test_moneybox_response_invalid_date_order() -> None:
    """Test MoneyboxResponse creation with invalid date order."""

    data = {
        "id": 1,
        "name": "Holiday",
        "balance": 1000,
        "created_at": "2020-05-02T00:00:00Z",
        "modified_at": "2020-05-01T00:00:00Z",  # Invalid order, modified_at is before created_at
        "savings_amount": 0,
        "savings_target": None,
        "priority": 1,
    }
    with pytest.raises(ValueError, match="Error: 'created_at' comes after 'modified_at'."):
        MoneyboxResponse(**data)


async def test_moneybox_response_invalid_date__modified_at_wrong_type__int() -> None:
    """Test MoneyboxResponse creation with invalid modified_at date value."""

    data = {
        "id": 1,
        "name": "Holiday",
        "balance": 1000,
        "created_at": "2020-05-02T00:00:00Z",
        "modified_at": 2,
        "savings_amount": 0,
        "savings_target": None,
        "priority": 1,
    }

    with pytest.raises(ValueError):
        MoneyboxResponse(**data)


async def test_moneybox_response_invalid_date__modified_at_string_type__not_isoformat_datetime() -> (
    None
):
    """Test MoneyboxResponse creation with invalid modified_at date value."""

    data = {
        "id": 1,
        "name": "Holiday",
        "balance": 1000,
        "created_at": "2020-05-02T00:00:00Z",
        "modified_at": "2",
        "savings_amount": 0,
        "savings_target": None,
        "priority": 1,
    }

    with pytest.raises(ValueError):
        MoneyboxResponse(**data)


async def test_moneybox_response_invalid_date__created_at_wrong_type__int() -> None:
    """Test MoneyboxResponse creation with invalid created_at date value."""

    data = {
        "id": 1,
        "name": "Holiday",
        "balance": 1000,
        "created_at": 2,
        "modified_at": "2020-05-02T00:00:00Z",
        "savings_amount": 0,
        "savings_target": None,
        "priority": 1,
    }

    with pytest.raises(ValueError):
        MoneyboxResponse(**data)


async def test_moneybox_response_invalid_date__created_at_string_type__not_isoformat_datetime() -> (
    None
):
    """Test MoneyboxResponse creation with invalid created_at date value."""

    data = {
        "id": 1,
        "name": "Holiday",
        "balance": 1000,
        "created_at": "2",
        "modified_at": "2020-05-02T00:00:00Z",
        "savings_amount": 0,
        "savings_target": None,
        "priority": 1,
    }

    with pytest.raises(ValueError):
        MoneyboxResponse(**data)


async def test_moneybox_response_invalid_date__none_for_created_at() -> None:
    """Test MoneyboxResponse creation with invalid date order."""

    data = {
        "id": 1,
        "name": "Holiday",
        "balance": 1000,
        "created_at": None,  # Invalid, has to be a datetime or iso string datetime
        "modified_at": "2020-05-01T00:00:00",
        "savings_amount": 0,
        "savings_target": None,
        "priority": 1,
    }
    with pytest.raises(ValueError):
        MoneyboxResponse(**data)


async def test_moneybox_response_valid_date_order() -> None:
    """Test MoneyboxResponse creation with valid date order."""

    data = {
        "id": 1,
        "name": "Holiday",
        "balance": 1000,
        "created_at": "2020-05-01T00:00:00Z",
        "modified_at": "2020-05-02T00:00:00Z",  # Valid order, modified_at is after created_at
        "savings_amount": 0,
        "savings_target": None,
        "priority": 1,
    }
    response = MoneyboxResponse(**data)
    assert response.modified_at > response.created_at
