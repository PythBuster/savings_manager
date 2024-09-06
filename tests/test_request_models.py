"""All request models tests are located here."""

from typing import Any

import pytest
from pydantic import ValidationError
from pydantic.alias_generators import to_snake

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
from src.utils import equal_dict, to_camel_cleaned_suffix


# MoneyboxCreateRequest Tests
@pytest.mark.parametrize(
    "data",
    [
        {"name": "Holiday", "savingsAmount": 100, "savingsTarget": 50000},
        {"name": "Emergency Fund", "savingsAmount": 0, "savingsTarget": None},
    ],
)
def test_moneybox_create_request_valid(data: dict[str, Any]) -> None:
    """Test valid MoneyboxCreateRequest creation."""
    response = MoneyboxCreateRequest(**data)
    assert response.name == data["name"]
    assert response.savings_amount == data["savingsAmount"]
    assert response.savings_target == data["savingsTarget"]


@pytest.mark.parametrize(
    "data",
    [
        {"name": "", "savingsAmount": 100, "savingsTarget": 50000, "priority": 1},  # Invalid name
        {
            "name": "Holiday",
            "savingsAmount": -10,
            "savingsTarget": 50000,
        },  # Negative savings_amount
        {
            "name": "Holiday",
            "savingsAmount": 100,
            "savingsTarget": -1,
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
        {"name": "Holiday", "savingsAmount": 200, "savingsTarget": 60000},
        {"savingsAmount": 150, "savingsTarget": None},
        {"name": "Savings", "savingsTarget": None},
    ],
)
def test_moneybox_update_request_valid(data: dict[str, Any]) -> None:
    """Test valid MoneyboxUpdateRequest creation."""
    response = MoneyboxUpdateRequest(**data)

    for key in data.keys():
        assert getattr(response, to_snake(key)) == data[key]


@pytest.mark.parametrize(
    "data",
    [
        {"name": "", "savingsAmount": 200, "savingsTarget": 60000, "priority": 1},  # Invalid name
        {
            "name": "Holiday",
            "savingsAmount": -20,
            "savingsTarget": 60000,
        },  # Negative savings_amount
        {
            "name": "Holiday",
            "savingsAmount": 200,
            "savingsTarget": -5,
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
        {"toMoneyboxId": 3, "amount": 50, "description": "Delete Moneybox."},
        {"toMoneyboxId": 5, "amount": 100, "description": ""},
    ],
)
def test_transfer_transaction_request_valid(data: dict[str, Any]) -> None:
    """Test valid TransferTransactionRequest creation."""
    response = TransferTransactionRequest(**data)
    assert response.to_moneybox_id == data["toMoneyboxId"]
    assert response.amount == data["amount"]
    assert response.description == data["description"]


@pytest.mark.parametrize(
    "data",
    [
        {"toMoneyboxId": 3, "amount": 0, "description": "Delete Moneybox."},  # Invalid amount
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
        {"moneyboxId": 4, "priority": 1},
        {"moneyboxId": 2, "priority": 2},
    ],
)
def test_priority_request_valid(data: dict[str, Any]) -> None:
    """Test valid PriorityRequest creation."""
    response = PriorityRequest(**data)
    assert response.moneybox_id == data["moneyboxId"]
    assert response.priority == data["priority"]


@pytest.mark.parametrize(
    "data",
    [
        {"moneyboxId": 4, "priority": -2},  # Invalid priority (negative)
        {"moneyboxId": 4, "priority": 0},  # Invalid priority (zero)
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
                {"moneyboxId": 2, "priority": 2},
                {"moneyboxId": 4, "priority": 1},
            ]
        },
        {
            "prioritylist": [
                {"moneyboxId": 10, "priority": 1},
                {"moneyboxId": 11, "priority": 3},
            ]
        },
    ],
)
def test_prioritylist_request_valid(data: dict[str, Any]) -> None:
    """Test valid PrioritylistRequest creation."""
    response = PrioritylistRequest(**data)
    assert len(response.prioritylist) == len(data["prioritylist"])
    for i, item in enumerate(response.prioritylist):
        assert item.moneybox_id == data["prioritylist"][i]["moneyboxId"]
        assert item.priority == data["prioritylist"][i]["priority"]


@pytest.mark.parametrize(
    "data",
    [
        {
            "prioritylist": [
                {"moneyboxId": "one", "priority": 1},  # Invalid type for moneybox_id
                {"moneyboxId": 2, "priority": 2},
            ]
        },
        {
            "prioritylist": [
                {"moneyboxId": 1, "priority": -1},  # Invalid priority, negative number
                {"moneyboxId": 2, "priority": 2},
            ]
        },
        {
            "prioritylist": [
                {"moneyboxId": 1, "priority": 0},  # Invalid priority, zero number
                {"moneyboxId": 2, "priority": 2},
            ]
        },
        {
            "prioritylist": [
                {"priority": 1},  # Missing moneybox_id
                {"moneyboxId": 2, "priority": 2},
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
            "isAutomatedSavingActive": True,
            "savingsAmount": 1000,
        },
        {
            "isAutomatedSavingActive": False,
            "savingsAmount": 500,
        },
        {
            "isAutomatedSavingActive": True,
            "savingsAmount": 0,
        },
        {
            "isAutomatedSavingActive": False,
        },
        {
            "savingsAmount": 1230,
            "overflowMoneyboxAutomatedSavingsMode": OverflowMoneyboxAutomatedSavingsModeType.COLLECT,  # noqa: ignore  # pylint: disable=line-too-long
        },
        {
            "overflowMoneyboxAutomatedSavingsMode": OverflowMoneyboxAutomatedSavingsModeType.ADD_TO_AUTOMATED_SAVINGS_AMOUNT,  # noqa: ignore  # pylint: disable=line-too-long
        },
        {
            "overflowMoneyboxAutomatedSavingsMode": "collect",
        },  # strings converts to enum
    ],
)
def test_app_settings_request_valid(data: dict[str, Any]) -> None:
    """Test valid AppSettingsRequest creation."""
    response = AppSettingsRequest(**data)
    set_attributes = response.model_dump(exclude_unset=True)

    # convert snake_case keys to camelCase
    set_attributes = {to_camel_cleaned_suffix(key): value for key, value in set_attributes.items()}
    assert equal_dict(dict_1=set_attributes, dict_2=data)


@pytest.mark.parametrize(
    "data",
    [
        {
            "isAutomatedSavingActive": "sagsfg",  # Invalid boolean
            "savingsAmount": 1000,
        },
        {
            "isAutomatedSavingActive": True,
            "savingsAmount": -500,  # Negative savings_amount
        },
        {
            "overflowMoneyboxAutomatedSavingsMode": "unknown",  # unknown mode
        },
    ],
)
def test_app_settings_request_invalid(data: dict[str, Any]) -> None:
    """Test AppSettingsRequest creation with invalid data."""
    with pytest.raises(ValidationError):
        AppSettingsRequest(**data)
