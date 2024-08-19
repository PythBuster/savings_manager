"""All response models tests are located here."""

from datetime import datetime, timedelta, timezone
from typing import Any
from xmlrpc.client import Fault

import pytest
from pydantic import ValidationError

from src.custom_types import OverflowMoneyboxAutomatedSavingsModeType
from src.data_classes.responses import (
    AppSettingsResponse,
    HTTPErrorResponse,
    MoneyboxesResponse,
    MoneyboxResponse,
    PrioritylistResponse,
    PriorityResponse,
    TransactionLogResponse,
    TransactionLogsResponse,
)


# HTTPErrorResponse Tests
@pytest.mark.parametrize(
    "data",
    [
        {"message": "No database connection.", "details": {"info": "DB offline"}},
        {"message": "Error occurred.", "details": None},
    ],
)
def test_http_error_response_valid(data: dict[str, Any]) -> None:
    """Test valid HTTPErrorResponse creation."""
    response = HTTPErrorResponse(**data)
    assert response.message == data["message"]
    assert response.details == data["details"]


@pytest.mark.parametrize(
    "data",
    [
        {"message": "", "details": {"info": "DB offline"}},  # Invalid message
    ],
)
def test_http_error_response_invalid(data: dict[str, Any]) -> None:
    """Test HTTPErrorResponse creation with invalid data."""
    with pytest.raises(ValidationError):
        HTTPErrorResponse(**data)


# MoneyboxResponse Tests
@pytest.mark.parametrize(
    "data",
    [
        {
            "id": 1,
            "name": "Holiday",
            "balance": 1000,
            "savings_amount": 500,
            "savings_target": 2000,
            "priority": 1,
            "created_at": datetime.now(tz=timezone.utc),
            "modified_at": datetime.now(tz=timezone.utc) + timedelta(days=1),
        },
        {
            "id": 2,
            "name": "Emergency Fund",
            "balance": 200,
            "savings_amount": 100,
            "savings_target": None,
            "priority": 2,
            "created_at": datetime.now(tz=timezone.utc),
            "modified_at": None,
        },
    ],
)
def test_moneybox_response_valid(data: dict[str, Any]) -> None:
    """Test valid MoneyboxResponse creation."""
    response = MoneyboxResponse(**data)
    assert response.id == data["id"]
    assert response.name == data["name"]
    assert response.balance == data["balance"]
    assert response.savings_amount == data["savings_amount"]
    assert response.savings_target == data["savings_target"]
    assert response.priority == data["priority"]
    assert response.created_at == data["created_at"]
    assert response.modified_at == data["modified_at"]


@pytest.mark.parametrize(
    "data",
    [
        {
            "id": 1,
            "name": "Holiday",
            "balance": -100,
            "savings_amount": 500,
            "savings_target": 2000,
            "priority": 1,
            "created_at": datetime.now(tz=timezone.utc),
            "modified_at": datetime.now(tz=timezone.utc),
        },  # Negative balance
        {
            "id": 1,
            "name": "Holiday",
            "balance": 1000,
            "savings_amount": 500,
            "savings_target": 2000,
            "priority": 1,
            "created_at": datetime.now(tz=timezone.utc),
            "modified_at": datetime.now(tz=timezone.utc) - timedelta(days=1),
        },  # modified_at before created_at
    ],
)
def test_moneybox_response_invalid(data: dict[str, Any]) -> None:
    """Test MoneyboxResponse creation with invalid data."""
    with pytest.raises(ValidationError):
        MoneyboxResponse(**data)


# MoneyboxesResponse Tests
@pytest.mark.parametrize(
    "data",
    [
        {
            "moneyboxes": [
                {
                    "id": 1,
                    "name": "Holiday",
                    "balance": 1000,
                    "savings_amount": 500,
                    "savings_target": 2000,
                    "priority": 1,
                    "created_at": datetime.now(tz=timezone.utc),
                    "modified_at": datetime.now(tz=timezone.utc) + timedelta(days=1),
                },
                {
                    "id": 2,
                    "name": "Emergency Fund",
                    "balance": 200,
                    "savings_amount": 100,
                    "savings_target": None,
                    "priority": 2,
                    "created_at": datetime.now(tz=timezone.utc),
                    "modified_at": None,
                },
            ]
        },
    ],
)
def test_moneyboxes_response_valid(data: dict[str, Any]) -> None:
    """Test valid MoneyboxesResponse creation."""
    response = MoneyboxesResponse(**data)
    assert len(response.moneyboxes) == len(data["moneyboxes"])
    for i, box in enumerate(response.moneyboxes):
        assert box.id == data["moneyboxes"][i]["id"]
        assert box.name == data["moneyboxes"][i]["name"]


@pytest.mark.parametrize(
    "data",
    [
        {"moneyboxes": []},
    ],
)
def test_moneyboxes_response_invalid(data: dict[str, Any]) -> None:
    """Test invalid MoneyboxesResponse creation."""
    with pytest.raises(ValidationError):
        MoneyboxesResponse(**data)


# TransactionLogResponse Tests
@pytest.mark.parametrize(
    "data",
    [
        {
            "id": 1,
            "counterparty_moneybox_name": "Other Box",
            "description": "Test transaction",
            "transaction_type": "direct",
            "transaction_trigger": "manually",
            "amount": 500,
            "balance": 1500,
            "counterparty_moneybox_id": 2,
            "moneybox_id": 1,
            "created_at": datetime.now(tz=timezone.utc),
        }
    ],
)
def test_transaction_log_response_valid(data: dict[str, Any]) -> None:
    """Test valid TransactionLogResponse creation."""
    response = TransactionLogResponse(**data)
    assert response.id == data["id"]
    assert response.amount == data["amount"]
    assert response.balance == data["balance"]


@pytest.mark.parametrize(
    "data",
    [
        {
            "id": 1,
            "counterparty_moneybox_name": "Other Box",
            "description": "Test transaction",
            "transaction_type": "DIRECT",
            "transaction_trigger": "MANUALLY",
            "amount": 0,
            "balance": 1000,
            "counterparty_moneybox_id": 2,
            "moneybox_id": 1,
            "created_at": datetime.now(tz=timezone.utc),
        },  # Invalid amount
        {
            "id": 1,
            "counterparty_moneybox_name": "Other Box",
            "description": "Test transaction",
            "transaction_type": "DISTRIBUTION",
            "transaction_trigger": "MANUALLY",
            "amount": 100,
            "balance": 1100,
            "counterparty_moneybox_id": 2,
            "moneybox_id": 1,
            "created_at": datetime.now(tz=timezone.utc),
        },  # Invalid transaction type and trigger combination
    ],
)
def test_transaction_log_response_invalid(data: dict[str, Any]) -> None:
    """Test TransactionLogResponse creation with invalid data."""
    with pytest.raises(ValidationError):
        TransactionLogResponse(**data)


# TransactionLogsResponse Tests
@pytest.mark.parametrize(
    "data",
    [
        {
            "transaction_logs": [
                {
                    "id": 1,
                    "counterparty_moneybox_name": "Other Box",
                    "description": "Test transaction",
                    "transaction_type": "DIRECT",
                    "transaction_trigger": "MANUALLY",
                    "amount": 500,
                    "balance": 1500,
                    "counterparty_moneybox_id": 2,
                    "moneybox_id": 1,
                    "created_at": datetime.now(tz=timezone.utc),
                }
            ]
        }
    ],
)
def test_transaction_logs_response_valid(data: dict[str, Any]) -> None:
    """Test valid TransactionLogsResponse creation."""
    response = TransactionLogsResponse(**data)
    assert len(response.transaction_logs) == len(data["transaction_logs"])
    for i, log in enumerate(response.transaction_logs):
        assert log.id == data["transaction_logs"][i]["id"]


# PriorityResponse Tests
@pytest.mark.parametrize(
    "data",
    [
        {"moneybox_id": 4, "priority": 1, "name": "Moneybox 1"},
        {"moneybox_id": 2, "priority": 2, "name": "Moneybox 2"},
    ],
)
def test_priority_response_valid(data: dict[str, Any]) -> None:
    """Test valid PriorityResponse creation."""
    response = PriorityResponse(**data)
    assert response.moneybox_id == data["moneybox_id"]
    assert response.priority == data["priority"]
    assert response.name == data["name"]


@pytest.mark.parametrize(
    "data",
    [
        {"moneybox_id": -1, "priority": 1},  # Invalid moneybox_id
        {"moneybox_id": 4, "priority": -2},  # Invalid priority (negative)
        {"moneybox_id": 4, "priority": 0},  # Invalid priority (zero)
    ],
)
def test_priority_response_invalid(data: dict[str, Any]) -> None:
    """Test PriorityResponse creation with invalid data."""
    with pytest.raises(ValidationError):
        PriorityResponse(**data)


# PrioritylistResponse Tests
@pytest.mark.parametrize(
    "data",
    [
        {
            "priority_list": [
                {"moneybox_id": 2, "priority": 2, "name": "Moneybox 2"},
                {"moneybox_id": 4, "priority": 1, "name": "Moneybox 3"},
            ]
        },
        {
            "priority_list": [
                {"moneybox_id": 10, "priority": 1, "name": "Moneybox 4"},
                {"moneybox_id": 11, "priority": 3, "name": "Moneybox 5"},
            ]
        },
    ],
)
def test_prioritylist_response_valid(data: dict[str, Any]) -> None:
    """Test valid PrioritylistResponse creation."""
    response = PrioritylistResponse(**data)
    assert len(response.priority_list) == len(data["priority_list"])
    for i, item in enumerate(response.priority_list):
        assert item.moneybox_id == data["priority_list"][i]["moneybox_id"]
        assert item.priority == data["priority_list"][i]["priority"]
        assert item.name == data["priority_list"][i]["name"]


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
def test_prioritylist_response_invalid(data: dict[str, Any]) -> None:
    """Test PrioritylistResponse creation with invalid data."""

    with pytest.raises(ValidationError):
        PrioritylistResponse(**data)


# Tests for AppSettingsResponse
@pytest.mark.parametrize(
    "data",
    [
        {
            "id": 1,
            "created_at": datetime(2024, 8, 11, 13, 57, 17, 941840, tzinfo=timezone.utc),
            "modified_at": datetime(2024, 8, 11, 15, 3, 17, 312860, tzinfo=timezone.utc),
            "is_automated_saving_active": True,
            "savings_amount": 60000,
            "overflow_moneybox_automated_savings_mode": OverflowMoneyboxAutomatedSavingsModeType.COLLECT,  # noqa: ignore  # pylint: disable=line-too-long
            "send_reports_via_email": False,
            "user_email_address": None,
        },
        {
            "id": 2,
            "created_at": datetime(2024, 8, 10, 12, 30, 0, tzinfo=timezone.utc),
            "modified_at": None,
            "is_automated_saving_active": False,
            "savings_amount": 1000,
            "overflow_moneybox_automated_savings_mode": OverflowMoneyboxAutomatedSavingsModeType.ADD_TO_AUTOMATED_SAVINGS_AMOUNT,  # noqa: ignore  # pylint: disable=line-too-long
            "send_reports_via_email": False,
            "user_email_address": None,
        },
        {
            "id": 3,
            "created_at": datetime(2024, 8, 9, 10, 15, 0, tzinfo=timezone.utc),
            "modified_at": datetime(2024, 8, 10, 11, 45, 0, tzinfo=timezone.utc),
            "is_automated_saving_active": True,
            "savings_amount": 0,
            "overflow_moneybox_automated_savings_mode": OverflowMoneyboxAutomatedSavingsModeType.FILL_UP_LIMITED_MONEYBOXES,  # noqa: ignore  # pylint: disable=line-too-long
            "send_reports_via_email": True,
            "user_email_address": "pythbuster@gmail.com",
        },
    ],
)
def test_app_settings_response_valid(data: dict[str, Any]) -> None:
    """Test valid AppSettingsResponse creation."""
    response = AppSettingsResponse(**data)
    assert response.id == data["id"]
    assert response.created_at == data["created_at"]
    assert response.modified_at == data["modified_at"]
    assert response.send_reports_via_email == data["send_reports_via_email"]
    assert response.user_email_address == data["user_email_address"]
    assert response.is_automated_saving_active == data["is_automated_saving_active"]
    assert response.savings_amount == data["savings_amount"]


@pytest.mark.parametrize(
    "data",
    [
        {
            "id": "one",  # Invalid id type
            "created_at": datetime(2024, 8, 11, 13, 57, 17, 941840, tzinfo=timezone.utc),
            "modified_at": datetime(2024, 8, 11, 15, 3, 17, 312860, tzinfo=timezone.utc),
            "is_automated_saving_active": True,
            "savings_amount": 60000,
            "send_reports_via_email": True,
            "user_mail_address": "pythbuster@gmail.com",
        },
        {
            "id": 4,
            "created_at": "2024-08-10T12:30:00",  # Invalid datetime type
            "modified_at": None,
            "is_automated_saving_active": False,
            "savings_amount": 1000,
            "send_reports_via_email": True,
            "user_email_address": "pythbuster@gmail.com",
        },
        {
            "id": 5,
            "created_at": datetime(2024, 8, 9, 10, 15, 0, tzinfo=timezone.utc),
            "modified_at": datetime(2024, 8, 10, 11, 45, 0, tzinfo=timezone.utc),
            "is_automated_saving_active": True,
            "savings_amount": -100,  # Negative savings_amount
            "send_reports_via_email": True,
            "user_email_address": "pythbuster@gmail.com",
        },
        {
            "id": 5,
            "created_at": datetime(2024, 8, 9, 10, 15, 0, tzinfo=timezone.utc),
            "modified_at": datetime(2024, 8, 10, 11, 45, 0, tzinfo=timezone.utc),
            "is_automated_saving_active": True,
            "savings_amount": -100,
            "send_reports_via_email": False,
            "user_email_address": "1",  # invalid email address
        },
        {
            "id": 6,
            "created_at": datetime(2024, 8, 9, 10, 15, 0, tzinfo=timezone.utc),
            "modified_at": datetime(2024, 8, 10, 11, 45, 0, tzinfo=timezone.utc),
            "is_automated_saving_active": True,
            "savings_amount": -100,
            "send_reports_via_email": True,  # is true, but email not set
            "user_email_address": None,
        },
    ],
)
def test_app_settings_response_invalid(data: dict[str, Any]) -> None:
    """Test AppSettingsResponse creation with invalid data."""
    with pytest.raises(ValidationError):
        AppSettingsResponse(**data)
