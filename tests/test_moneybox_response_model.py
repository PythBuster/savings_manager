from datetime import datetime

import pytest
from pydantic import ValidationError

from src.data_classes.responses import MoneyboxResponse


def test_moneyboxresponse_valid_data():
    """Test valid MoneyboxResponse creation."""
    data = {
        "id": 1,
        "name": "Holiday",
        "balance": 1000,
        "created_at": "2020-05-01T00:00:00Z",
        "modified_at": None,
    }
    response = MoneyboxResponse(**data)
    assert response.id == 1
    assert response.name == "Holiday"
    assert response.balance == 1000
    assert response.created_at == datetime.fromisoformat("2020-05-01T00:00:00+00:00")
    assert response.modified_at is None

def test_moneyboxresponse_invalid_id__0():
    """Test MoneyboxResponse creation with invalid id."""
    data = {
        "id": 0,  # Invalid id, should be >= 1
        "name": "Holiday",
        "balance": 1000,
        "created_at": "2020-05-01T00:00:00Z",
        "modified_at": None,
    }
    with pytest.raises(ValidationError):
        MoneyboxResponse(**data)

def test_moneyboxresponse_invalid_id__negative():
    """Test MoneyboxResponse creation with invalid id."""
    data = {
        "id": -11,  # Invalid id, should be >= 1
        "name": "Holiday",
        "balance": 1000,
        "created_at": "2020-05-01T00:00:00Z",
        "modified_at": None,
    }
    with pytest.raises(ValidationError):
        MoneyboxResponse(**data)

def test_moneyboxresponse_invalid_id__non_int():
    """Test MoneyboxResponse creation with invalid id."""

    data = {
        "id": "one",  # Invalid id, should be integer and >= 1
        "name": "Holiday",
        "balance": 1000,
        "created_at": "2020-05-01T00:00:00Z",
        "modified_at": None,
    }

    with pytest.raises(ValidationError):
        MoneyboxResponse(**data)


def test_moneyboxresponse_invalid_name__minlength():
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


def test_moneyboxresponse_invalid_name__wrong_type():
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

def test_moneyboxresponse_invalid_balance__negative():
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


def test_moneyboxresponse_valid_balance__zero():
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


def test_moneyboxresponse_invalid_balance__wrong_type():
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

def test_moneyboxresponse_invalid_date_order():
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

def test_moneyboxresponse_invalid_date__modified_at_wrong_type():
    """Test MoneyboxResponse creation with invalid date order."""
    data = {
        "id": 1,
        "name": "Holiday",
        "balance": 1000,
        "created_at": "2020-05-02T00:00:00Z",
        "modified_at": 2,
    }
    with pytest.raises(ValueError):
        MoneyboxResponse(**data)

def test_moneyboxresponse_invalid_date__created_at_wrong_type():
    """Test MoneyboxResponse creation with invalid date order."""
    data = {
        "id": 1,
        "name": "Holiday",
        "balance": 1000,
        "created_at": 2,
        "modified_at": "2020-05-02T00:00:00Z",
    }
    with pytest.raises(ValueError):
        MoneyboxResponse(**data)

def test_moneyboxresponse_invalid_date__none_for_created_at():
    """Test MoneyboxResponse creation with invalid date order."""
    data = {
        "id": 1,
        "name": "Holiday",
        "balance": 1000,
        "created_at": None,  # Invalid, has to be a datetime or iso string datetime
        "modified_at": "2020-05-01T00:00:00Z",
    }
    with pytest.raises(ValueError):
        MoneyboxResponse(**data)

def test_moneyboxresponse_valid_date_order():
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
