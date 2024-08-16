"""All request models tests are located here."""

from typing import Any

import pytest
from pydantic import ValidationError

from src.data_classes.requests import (
    DepositTransactionRequest,
    MoneyboxCreateRequest,
    MoneyboxUpdateRequest,
    PrioritylistRequest,
    PriorityRequest,
    TransferTransactionRequest,
    WithdrawTransactionRequest, AppSettingsRequest,
)


# MoneyboxCreateRequest Tests
@pytest.mark.parametrize(
    "data",
    [
        {"name": "Holiday", "savings_amount": 100, "savings_target": 50000, "priority": 1},
        {"name": "Emergency Fund", "savings_amount": 0, "savings_target": None, "priority": 2},
    ],
)
def test_moneybox_create_request_valid(data: dict[str, Any]) -> None:
    """Test valid MoneyboxCreateRequest creation."""
    response = MoneyboxCreateRequest(**data)
    assert response.name == data["name"]
    assert response.savings_amount == data["savings_amount"]
    assert response.savings_target == data["savings_target"]
    assert response.priority == data["priority"]


@pytest.mark.parametrize(
    "data",
    [
        {"name": "", "savings_amount": 100, "savings_target": 50000, "priority": 1},  # Invalid name
        {
            "name": "Holiday",
            "savings_amount": -10,
            "savings_target": 50000,
            "priority": 1,
        },  # Negative savings_amount
        {
            "name": "Holiday",
            "savings_amount": 100,
            "savings_target": -1,
            "priority": 1,
        },  # Negative savings_target
        {
            "name": "Holiday",
            "savings_amount": 100,
            "savings_target": 50000,
            "priority": -1,
        },  # Negative priority
        {
            "name": "Holiday",
            "savings_amount": 100,
            "savings_target": 50000,
            "priority": 0,
        },  # Null priority
    ],
)
def test_moneybox_create_request_invalid(data: dict[str, Any]) -> None:
    """Test MoneyboxCreateRequest creation with invalid data."""
    with pytest.raises(ValidationError):
        MoneyboxCreateRequest(**data)


# MoneyboxUpdateRequest Tests
@pytest.mark.parametrize(
    "data",
    [
        {"name": "Holiday", "savings_amount": 200, "savings_target": 60000, "priority": 1},
        {"name": None, "savings_amount": 150, "savings_target": None, "priority": 2},
        {"name": "Savings", "savings_amount": None, "savings_target": None, "priority": None},
    ],
)
def test_moneybox_update_request_valid(data: dict[str, Any]) -> None:
    """Test valid MoneyboxUpdateRequest creation."""
    response = MoneyboxUpdateRequest(**data)
    assert response.name == data["name"]
    assert response.savings_amount == data["savings_amount"]
    assert response.savings_target == data["savings_target"]
    assert response.priority == data["priority"]


@pytest.mark.parametrize(
    "data",
    [
        {"name": "", "savings_amount": 200, "savings_target": 60000, "priority": 1},  # Invalid name
        {
            "name": "Holiday",
            "savings_amount": -20,
            "savings_target": 60000,
            "priority": 1,
        },  # Negative savings_amount
        {
            "name": "Holiday",
            "savings_amount": 200,
            "savings_target": -5,
            "priority": 1,
        },  # Negative savings_target
        {
            "name": "Holiday",
            "savings_amount": 200,
            "savings_target": 60000,
            "priority": 0,
        },  # Invalid priority
    ],
)
def test_moneybox_update_request_invalid(data: dict[str, Any]) -> None:
    """Test MoneyboxUpdateRequest creation with invalid data."""
    with pytest.raises(ValidationError):
        MoneyboxUpdateRequest(**data)


# DepositTransactionRequest Tests
@pytest.mark.parametrize(
    "data",
    [
        {"amount": 50, "description": "Bonus."},
        {"amount": 100, "description": ""},
    ],
)
def test_deposit_transaction_request_valid(data: dict[str, Any]) -> None:
    """Test valid DepositTransactionRequest creation."""
    response = DepositTransactionRequest(**data)
    assert response.amount == data["amount"]
    assert response.description == data["description"]


@pytest.mark.parametrize(
    "data",
    [
        {"amount": 0, "description": "Bonus."},  # Invalid amount
        {"amount": -10, "description": "Bonus."},  # Negative amount
    ],
)
def test_deposit_transaction_request_invalid(data: dict[str, Any]) -> None:
    """Test DepositTransactionRequest creation with invalid data."""
    with pytest.raises(ValidationError):
        DepositTransactionRequest(**data)


# WithdrawTransactionRequest Tests
@pytest.mark.parametrize(
    "data",
    [
        {"amount": 30, "description": "Gift."},
        {"amount": 20, "description": ""},
    ],
)
def test_withdraw_transaction_request_valid(data: dict[str, Any]) -> None:
    """Test valid WithdrawTransactionRequest creation."""
    response = WithdrawTransactionRequest(**data)
    assert response.amount == data["amount"]
    assert response.description == data["description"]


@pytest.mark.parametrize(
    "data",
    [
        {"amount": 0, "description": "Gift."},  # Invalid amount
        {"amount": -5, "description": "Gift."},  # Negative amount
    ],
)
def test_withdraw_transaction_request_invalid(data: dict[str, Any]) -> None:
    """Test WithdrawTransactionRequest creation with invalid data."""
    with pytest.raises(ValidationError):
        WithdrawTransactionRequest(**data)


# TransferTransactionRequest Tests
@pytest.mark.parametrize(
    "data",
    [
        {"to_moneybox_id": 3, "amount": 50, "description": "Delete Moneybox."},
        {"to_moneybox_id": 5, "amount": 100, "description": ""},
    ],
)
def test_transfer_transaction_request_valid(data: dict[str, Any]) -> None:
    """Test valid TransferTransactionRequest creation."""
    response = TransferTransactionRequest(**data)
    assert response.to_moneybox_id == data["to_moneybox_id"]
    assert response.amount == data["amount"]
    assert response.description == data["description"]


@pytest.mark.parametrize(
    "data",
    [
        {"to_moneybox_id": 3, "amount": 0, "description": "Delete Moneybox."},  # Invalid amount
    ],
)
def test_transfer_transaction_request_invalid(data: dict[str, Any]) -> None:
    """Test TransferTransactionRequest creation with invalid data."""
    with pytest.raises(ValidationError):
        TransferTransactionRequest(**data)


# PriorityRequest Tests
@pytest.mark.parametrize(
    "data",
    [
        {"moneybox_id": 4, "priority": 1},
        {"moneybox_id": 2, "priority": 2},
    ],
)
def test_priority_request_valid(data: dict[str, Any]) -> None:
    """Test valid PriorityRequest creation."""
    response = PriorityRequest(**data)
    assert response.moneybox_id == data["moneybox_id"]
    assert response.priority == data["priority"]


@pytest.mark.parametrize(
    "data",
    [
        {"moneybox_id": 4, "priority": -2},  # Invalid priority (negative)
        {"moneybox_id": 4, "priority": 0},  # Invalid priority (zero)
    ],
)
def test_priority_request_invalid(data: dict[str, Any]) -> None:
    """Test PriorityRequest creation with invalid data."""
    with pytest.raises(ValidationError):
        PriorityRequest(**data)


# PrioritylistRequest Tests
@pytest.mark.parametrize(
    "data",
    [
        {
            "priority_list": [
                {"moneybox_id": 2, "priority": 2},
                {"moneybox_id": 4, "priority": 1},
            ]
        },
        {
            "priority_list": [
                {"moneybox_id": 10, "priority": 1},
                {"moneybox_id": 11, "priority": 3},
            ]
        },
    ],
)
def test_prioritylist_request_valid(data: dict[str, Any]) -> None:
    """Test valid PrioritylistRequest creation."""
    response = PrioritylistRequest(**data)
    assert len(response.priority_list) == len(data["priority_list"])
    for i, item in enumerate(response.priority_list):
        assert item.moneybox_id == data["priority_list"][i]["moneybox_id"]
        assert item.priority == data["priority_list"][i]["priority"]


@pytest.mark.parametrize(
    "data",
    [
        {
            "priority_list": [
                {"moneybox_id": "one", "priority": 1},  # Invalid type for moneybox_id
                {"moneybox_id": 2, "priority": 2},
            ]
        },
        {
            "priority_list": [
                {"moneybox_id": 1, "priority": -1},  # Invalid priority, negative number
                {"moneybox_id": 2, "priority": 2},
            ]
        },
        {
            "priority_list": [
                {"moneybox_id": 1, "priority": 0},  # Invalid priority, zero number
                {"moneybox_id": 2, "priority": 2},
            ]
        },
        {
            "priority_list": [
                {"priority": 1},  # Missing moneybox_id
                {"moneybox_id": 2, "priority": 2},
            ]
        },
        {
            "priority_list": [],  # Empty list
        },
    ],
)
def test_prioritylist_request_invalid(data: dict[str, Any]) -> None:
    """Test PrioritylistRequest creation with invalid data."""
    with pytest.raises(ValidationError):
        PrioritylistRequest(**data)

# Tests for AppSettingsRequest
@pytest.mark.parametrize(
    "data",
    [
        {
            "is_automated_saving_active": True,
            "savings_amount": 1000,
            "automated_saving_trigger_day": "first_of_month",
        },
        {
            "is_automated_saving_active": False,
            "savings_amount": 500,
            "automated_saving_trigger_day": "last_of_month",
        },
        {
            "is_automated_saving_active": True,
            "savings_amount": 0,
            "automated_saving_trigger_day": "middle_of_month",
        },
    ],
)
def test_app_settings_request_valid(data: dict[str, Any]) -> None:
    """Test valid AppSettingsRequest creation."""
    response = AppSettingsRequest(**data)
    assert response.is_automated_saving_active == data["is_automated_saving_active"]
    assert response.savings_amount == data["savings_amount"]
    assert response.automated_saving_trigger_day == data["automated_saving_trigger_day"]


@pytest.mark.parametrize(
    "data",
    [
        {
            "is_automated_saving_active": "sagsfg",  # Invalid boolean
            "savings_amount": 1000,
            "automated_saving_trigger_day": "first_of_month",
        },
        {
            "is_automated_saving_active": True,
            "savings_amount": -500,  # Negative savings_amount
            "automated_saving_trigger_day": "first_of_month",
        },
        {
            "is_automated_saving_active": True,
            "savings_amount": 1000,
            "automated_saving_trigger_day": "unknown_day",  # Invalid trigger day
        },
    ],
)
def test_app_settings_request_invalid(data: dict[str, Any]) -> None:
    """Test AppSettingsRequest creation with invalid data."""
    with pytest.raises(ValidationError):
        AppSettingsRequest(**data)