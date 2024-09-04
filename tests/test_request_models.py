"""All request models tests are located here."""

from typing import Any

import pytest
from pydantic import ValidationError

from src.custom_types import OverflowMoneyboxAutomatedSavingsModeType
from src.data_classes.requests import (
    AppSettingsRequest,
    DepositTransactionRequest,
    MoneyboxCreateRequest,
    MoneyboxUpdateRequest,
    PrioritylistRequest,
    PriorityRequest,
    TransferTransactionRequest,
    WithdrawTransactionRequest,
)
from src.utils import equal_dict


# MoneyboxCreateRequest Tests
@pytest.mark.parametrize(
    "data",
    [
        {"name": "Holiday", "savings_amount": 100, "savings_target": 50000},
        {"name": "Emergency Fund", "savings_amount": 0, "savings_target": None},
    ],
)
def test_moneybox_create_request_valid(data: dict[str, Any]) -> None:
    """Test valid MoneyboxCreateRequest creation."""
    response = MoneyboxCreateRequest(**data)
    assert response.name == data["name"]
    assert response.savings_amount == data["savings_amount"]
    assert response.savings_target == data["savings_target"]


@pytest.mark.parametrize(
    "data",
    [
        {"name": "", "savings_amount": 100, "savings_target": 50000, "priority": 1},  # Invalid name
        {
            "name": "Holiday",
            "savings_amount": -10,
            "savings_target": 50000,
        },  # Negative savings_amount
        {
            "name": "Holiday",
            "savings_amount": 100,
            "savings_target": -1,
        },  # Negative savings_target
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
        {"name": "Holiday", "savings_amount": 200, "savings_target": 60000},
        {"savings_amount": 150, "savings_target": None},
        {"name": "Savings", "savings_target": None},
    ],
)
def test_moneybox_update_request_valid(data: dict[str, Any]) -> None:
    """Test valid MoneyboxUpdateRequest creation."""
    response = MoneyboxUpdateRequest(**data)

    assert equal_dict(dict_1=data, dict_2=response.model_dump(exclude_unset=True))


@pytest.mark.parametrize(
    "data",
    [
        {"name": "", "savings_amount": 200, "savings_target": 60000, "priority": 1},  # Invalid name
        {
            "name": "Holiday",
            "savings_amount": -20,
            "savings_target": 60000,
        },  # Negative savings_amount
        {
            "name": "Holiday",
            "savings_amount": 200,
            "savings_target": -5,
        },  # Negative savings_target
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
            "prioritylist": [
                {"moneybox_id": 2, "priority": 2},
                {"moneybox_id": 4, "priority": 1},
            ]
        },
        {
            "prioritylist": [
                {"moneybox_id": 10, "priority": 1},
                {"moneybox_id": 11, "priority": 3},
            ]
        },
    ],
)
def test_prioritylist_request_valid(data: dict[str, Any]) -> None:
    """Test valid PrioritylistRequest creation."""
    response = PrioritylistRequest(**data)
    assert len(response.prioritylist) == len(data["prioritylist"])
    for i, item in enumerate(response.prioritylist):
        assert item.moneybox_id == data["prioritylist"][i]["moneybox_id"]
        assert item.priority == data["prioritylist"][i]["priority"]


@pytest.mark.parametrize(
    "data",
    [
        {
            "prioritylist": [
                {"moneybox_id": "one", "priority": 1},  # Invalid type for moneybox_id
                {"moneybox_id": 2, "priority": 2},
            ]
        },
        {
            "prioritylist": [
                {"moneybox_id": 1, "priority": -1},  # Invalid priority, negative number
                {"moneybox_id": 2, "priority": 2},
            ]
        },
        {
            "prioritylist": [
                {"moneybox_id": 1, "priority": 0},  # Invalid priority, zero number
                {"moneybox_id": 2, "priority": 2},
            ]
        },
        {
            "prioritylist": [
                {"priority": 1},  # Missing moneybox_id
                {"moneybox_id": 2, "priority": 2},
            ]
        },
        {
            "prioritylist": [],  # Empty list
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
        },
        {
            "is_automated_saving_active": False,
            "savings_amount": 500,
        },
        {
            "is_automated_saving_active": True,
            "savings_amount": 0,
        },
        {
            "is_automated_saving_active": False,
        },
        {
            "savings_amount": 1230,
            "overflow_moneybox_automated_savings_mode": OverflowMoneyboxAutomatedSavingsModeType.COLLECT,  # noqa: ignore  # pylint: disable=line-too-long
        },
        {
            "overflow_moneybox_automated_savings_mode": OverflowMoneyboxAutomatedSavingsModeType.ADD_TO_AUTOMATED_SAVINGS_AMOUNT,  # noqa: ignore  # pylint: disable=line-too-long
        },
        {
            "overflow_moneybox_automated_savings_mode": "collect",
        },
    ],
)
def test_app_settings_request_valid(data: dict[str, Any]) -> None:
    """Test valid AppSettingsRequest creation."""
    response = AppSettingsRequest(**data)
    set_attributes = response.model_dump(exclude_unset=True)

    assert equal_dict(dict_1=set_attributes, dict_2=data)


@pytest.mark.parametrize(
    "data",
    [
        {
            "is_automated_saving_active": "sagsfg",  # Invalid boolean
            "savings_amount": 1000,
        },
        {
            "is_automated_saving_active": True,
            "savings_amount": -500,  # Negative savings_amount
        },
        {
            "overflow_moneybox_automated_savings_mode": "unknown",  # unknown mode
        },
    ],
)
def test_app_settings_request_invalid(data: dict[str, Any]) -> None:
    """Test AppSettingsRequest creation with invalid data."""
    with pytest.raises(ValidationError):
        AppSettingsRequest(**data)
