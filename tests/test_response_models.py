"""All response models tests are located here."""

from datetime import datetime, timedelta, timezone
from typing import Any

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
        {"message": "   Error occurred.   ", "details": None},  # with whitespace
    ],
)
def test_http_error_response_valid(data: dict[str, Any]) -> None:
    """Test valid HTTPErrorResponse creation."""
    response = HTTPErrorResponse(**data)
    assert response.message == data["message"].strip()
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
            "description": "",
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
            "description": "",
        },
        {
            "id": 3,
            "name": "Holiday",
            "balance": 1000,
            "savings_amount": 500,
            "savings_target": 2000,
            "priority": 1,
            "created_at": datetime.now(tz=timezone.utc),
            "modified_at": datetime.now(tz=timezone.utc) + timedelta(days=1),
            "description": "",
        },  # Valid datetimes
        {
            "id": 4,
            "name": "Emergency Fund",
            "balance": 200,
            "savings_amount": 100,
            "savings_target": None,
            "priority": 2,
            "created_at": datetime.now(tz=timezone.utc),
            "modified_at": None,
            "description": "",
        },  # None modifiedAt
        {
            "id": 5,
            "name": "Vacation",
            "balance": 500,
            "savings_amount": 200,
            "savings_target": 1500,
            "priority": 1,
            "created_at": datetime.now(tz=timezone.utc).isoformat(),
            "modified_at": (datetime.now(tz=timezone.utc) + timedelta(days=2)).isoformat(),
            "description": "",
        },  # ISO format strings for datetimes
        {
            "id": 5,
            "name": "Vacation",
            "balance": 500,
            "savings_amount": 200,
            "savings_target": 1500,
            "priority": 1,
            "created_at": datetime.now(tz=timezone.utc).isoformat(),
            "modified_at": (datetime.now(tz=timezone.utc) + timedelta(days=2)).isoformat(),
            "description": "test",
        },
    ],
)
def test_moneybox_response_valid(data: dict[str, Any]) -> None:
    """Test valid MoneyboxResponse creation."""
    response = MoneyboxResponse(**data)
    assert response.id_ == data["id"]
    assert response.name == data["name"]
    assert response.balance == data["balance"]
    assert response.savings_amount == data["savings_amount"]
    assert response.savings_target == data["savings_target"]
    assert response.priority == data["priority"]
    assert response.description == data["description"]

    if isinstance(data["created_at"], str):
        assert response.created_at == datetime.fromisoformat(data["created_at"])
    else:
        assert response.created_at == data["created_at"]

    if isinstance(data["modified_at"], str):
        assert response.modified_at == datetime.fromisoformat(data["modified_at"])
    else:
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
            "description": "",
        },  # Negative balance
        {
            "id": 2,
            "name": "Holiday",
            "balance": 1000,
            "savingsAmount": 500,
            "savingsTarget": 2000,
            "priority": 1,
            "created_at": datetime.now(tz=timezone.utc),
            "modified_at": datetime.now(tz=timezone.utc) - timedelta(days=1),
            "description": "",
        },  # modified_at before createdAt,
        {
            "id": 3,
            "name": "Holiday",
            "balance": 1000,
            "savingsAmount": 500,
            "savingsTarget": 2000,
            "priority": 1,
            "created_at": "2024-08-11 13:57:17.941840+00:00",
            "modified_at": "not-a-datetime",
            "description": "",
        },  # Invalid modified_at format
        {
            "id": 4,
            "name": "Emergency Fund",
            "balance": 200,
            "savingsAmount": 100,
            "savingsTarget": None,
            "priority": 2,
            "created_at": "not-a-datetime",
            "modified_at": None,
            "description": "",
        },  # Invalid modified_at format
        {
            "id": 5,
            "name": "Vacation",
            "balance": 500,
            "savingsAmount": 200,
            "savingsTarget": 1500,
            "priority": 1,
            "created_at": datetime.now(tz=timezone.utc),
            "modified_at": datetime.now(tz=timezone.utc) - timedelta(days=1),
            "description": "",
        },  # modified_at before created_at
        {
            "id": 6,
            "name": "Vacation",
            "balance": 500,
            "savingsAmount": 200,
            "savingsTarget": 1500,
            "priority": 1,
            "created_at": {},  # incorrect type
            "modified_at": datetime.now(tz=timezone.utc),
            "description": "",
        },
        {
            "id": 7,
            "name": "Vacation",
            "balance": 500,
            "savingsAmount": 200,
            "savingsTarget": 1500,
            "priority": 1,
            "created_at": datetime.now(tz=timezone.utc),
            "modified_at": {},  # incorrect type
            "description": "",
        },
        {
            "id": 8,
            "name": " Box 1",  # leading whitespace
            "balance": 500,
            "savings_amount": 200,
            "savings_target": 1500,
            "priority": 1,
            "created_at": datetime.now(tz=timezone.utc),
            "modified_at": None,
            "description": "",
        },
        {
            "id": 9,
            "name": "Box 1",
            "balance": 500,
            "savings_amount": 200,
            "savings_target": 1500,
            "priority": 1,
            "created_at": datetime.now(tz=timezone.utc),
            "modified_at": None,
            "description": "  test  ",  # leading/tailing whitespace
        },
        {
            "id": 10,
            "name": 123,  # invalid type
            "balance": 500,
            "savings_amount": 200,
            "savings_target": 1500,
            "priority": 1,
            "created_at": datetime.now(tz=timezone.utc),
            "modified_at": None,
            "description": "",
        },
        {
            "id": 11,
            "name": "Box 1 ",
            "balance": 500,
            "savings_amount": 200,
            "savings_target": 1500,
            "priority": 1,
            "created_at": datetime.now(tz=timezone.utc),
            "modified_at": None,
            "description": 123,  # invalid type
        },
        {
            "id": 12,
            "name": None,  # required
            "balance": 500,
            "savings_amount": 200,
            "savings_target": 1500,
            "priority": 1,
            "created_at": datetime.now(tz=timezone.utc),
            "modified_at": None,
            "description": "",
        },
        {
            "id": 13,
            "name": "Holiday",
            "balance": 500,
            "savings_amount": 200,
            "savings_target": 1500,
            "priority": 1,
            "created_at": datetime.now(tz=timezone.utc),
            "modified_at": None,
            "description": None,  # required
        },
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
                    "id": 0,
                    "name": "Overflow Moneybox",
                    "balance": 0,
                    "savings_amount": 0,
                    "savings_target": None,
                    "priority": 0,
                    "created_at": datetime.now(tz=timezone.utc),
                    "modified_at": None,
                    "description": "",
                },
                {
                    "id": 1,
                    "name": "Holiday",
                    "balance": 1000,
                    "savings_amount": 500,
                    "savings_target": 2000,
                    "priority": 1,
                    "created_at": datetime.now(tz=timezone.utc),
                    "modified_at": datetime.now(tz=timezone.utc) + timedelta(days=1),
                    "description": "",
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
                    "description": "",
                },
            ]
        },
        {
            "moneyboxes": [
                {
                    "id": 0,
                    "name": "Overflow Moneybox",
                    "balance": 0,
                    "savings_amount": 0,
                    "savings_target": None,
                    "priority": 0,
                    "created_at": datetime.now(tz=timezone.utc),
                    "modified_at": None,
                    "description": "",
                },
                {
                    "id": 1,
                    "name": "Holiday",
                    "balance": 1000,
                    "savings_amount": 500,
                    "savings_target": 2000,
                    "priority": 1,
                    "created_at": (datetime.now(tz=timezone.utc) - timedelta(days=1)).isoformat(),
                    "modified_at": (datetime.now(tz=timezone.utc)).isoformat(),
                    "description": "",
                },
                {
                    "id": 2,
                    "name": "Emergency Fund",
                    "balance": 200,
                    "savings_amount": 100,
                    "savings_target": None,
                    "priority": 2,
                    "created_at": (datetime.now(tz=timezone.utc) - timedelta(days=1)).isoformat(),
                    "modified_at": None,
                    "description": "",
                },
            ]
        },  # Valid ISO format datetimes
    ],
)
def test_moneyboxes_response_valid(data: dict[str, Any]) -> None:
    """Test valid MoneyboxesResponse creation."""
    response = MoneyboxesResponse(**data)
    assert len(response.moneyboxes) == len(data["moneyboxes"])
    for i, box in enumerate(response.moneyboxes):
        assert box.id_ == data["moneyboxes"][i]["id"]
        assert box.name == data["moneyboxes"][i]["name"]
    assert response.total == len(data["moneyboxes"])  # Validate the computed `total` property


@pytest.mark.parametrize(
    "data",
    [
        {"moneyboxes": []},  # Empty moneyboxes list (missing overflow moneybox
        {
            "moneyboxes": [
                {
                    "id": 1,
                    "name": "Holiday",
                    "balance": 1000,
                    "savings_amount": 500,
                    "savings_target": 2000,
                    "priority": 1,
                    "created_at": "not-a-datetime",
                    "modified_at": datetime.now(tz=timezone.utc),
                    "description": "",
                },
            ]
        },  # Invalid created_at format (string not a datetime)
        {
            "moneyboxes": [
                {
                    "id": 2,
                    "name": "Emergency Fund",
                    "balance": 200,
                    "savings_amount": 100,
                    "savings_target": None,
                    "priority": 2,
                    "created_at": datetime.now(tz=timezone.utc),
                    "modified_at": datetime.now(tz=timezone.utc) - timedelta(days=1),
                    "description": "",
                },
            ]
        },  # Invalid: modified_at is before created_at
        {
            "moneyboxes": [
                {
                    "id": 2,
                    "name": "Emergency Fund",
                    "balance": 200,
                    "savings_amount": 100,
                    "savings_target": None,
                    "priority": 2,
                    "created_at": datetime.now(tz=timezone.utc),
                    "modified_at": datetime.now(tz=timezone.utc) - timedelta(days=1),
                },
            ]
        },  # Invalid: description missing
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
        },
        {
            "id": 2,
            "counterparty_moneybox_name": "Savings Box",
            "description": "Automated savings",
            "transaction_type": "distribution",
            "transaction_trigger": "automatically",
            "amount": 1000,
            "balance": 2000,
            "counterparty_moneybox_id": 3,
            "moneybox_id": 2,
            "created_at": (datetime.now(tz=timezone.utc) - timedelta(days=1)).isoformat(),
        },  # Valid ISO format datetime
    ],
)
def test_transaction_log_response_valid(data: dict[str, Any]) -> None:
    """Test valid TransactionLogResponse creation."""
    response = TransactionLogResponse(**data)
    assert response.id_ == data["id"]
    assert response.amount == data["amount"]
    assert response.balance == data["balance"]

    if isinstance(data["created_at"], str):
        assert response.created_at == datetime.fromisoformat(data["created_at"])
    else:
        assert response.created_at == data["created_at"]


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
            "id": 2,
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
        {
            "id": 3,
            "counterparty_moneybox_name": "Invalid Date",
            "description": "Test transaction",
            "transaction_type": "direct",
            "transaction_trigger": "manually",
            "amount": 100,
            "balance": 1100,
            "counterparty_moneybox_id": 2,
            "moneybox_id": 1,
            "created_at": "not-a-datetime",
        },  # Invalid created_at format (string not a datetime)
        {
            "id": 4,
            "counterparty_moneybox_name": "Savings Box",
            "description": "Automated savings",
            "transaction_type": "distribution",
            "transaction_trigger": "automatically",
            "amount": 1000,
            "balance": 2000,
            "counterparty_moneybox_id": 3,
            "moneybox_id": 2,
            "created_at": 1621621621,
        },  # Invalid created_at format (timestamp)
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
        assert log.id_ == data["transaction_logs"][i]["id"]


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
            "prioritylist": [
                {"moneybox_id": 2, "priority": 2, "name": "Moneybox 2"},
                {"moneybox_id": 4, "priority": 1, "name": "Moneybox 3"},
            ]
        },
        {
            "prioritylist": [
                {"moneybox_id": 10, "priority": 1, "name": "Moneybox 4"},
                {"moneybox_id": 11, "priority": 3, "name": "Moneybox 5"},
            ]
        },
    ],
)
def test_prioritylist_response_valid(data: dict[str, Any]) -> None:
    """Test valid PrioritylistResponse creation."""
    response = PrioritylistResponse(**data)
    assert response.total == len(data["prioritylist"])
    for i, item in enumerate(response.prioritylist):
        assert item.moneybox_id == data["prioritylist"][i]["moneybox_id"]
        assert item.priority == data["prioritylist"][i]["priority"]
        assert item.name == data["prioritylist"][i]["name"]


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
            "created_at": "2024-08-10 12:30:00+00:00",  # Valid datetime string
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
            "modified_at": "2024-08-10 11:45:00+00:00",  # Valid datetime string
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
    assert response.id_ == data["id"]

    if isinstance(data["created_at"], str):
        assert response.created_at == datetime.fromisoformat(data["created_at"])
    else:
        assert response.created_at == data["created_at"]

    if isinstance(data["modified_at"], str):
        assert response.modified_at == datetime.fromisoformat(data["modified_at"])
    else:
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
            "overflow_moneybox_automated_savings_mode": "collect",  # Invalid enum value
            "send_reports_via_email": True,
            "user_email_address": "pythbuster@gmail.com",
        },
        {
            "id": 4,
            "created_at": "invalid-datetime",  # Invalid datetime string
            "modified_at": None,
            "is_automated_saving_active": False,
            "savings_amount": 1000,
            "overflow_moneybox_automated_savings_mode": OverflowMoneyboxAutomatedSavingsModeType.COLLECT,  # noqa: ignore  # pylint: disable=line-too-long
            "send_reports_via_email": True,
            "user_email_address": "pythbuster@gmail.com",
        },
        {
            "id": 6,
            "created_at": datetime(2024, 8, 9, 10, 15, 0, tzinfo=timezone.utc),
            "modified_at": datetime(2024, 8, 10, 11, 45, 0, tzinfo=timezone.utc),
            "is_automated_saving_active": True,
            "savings_amount": -100,  # Negative savings_amount
            "overflow_moneybox_automated_savings_mode": OverflowMoneyboxAutomatedSavingsModeType.COLLECT,  # noqa: ignore  # pylint: disable=line-too-long
            "send_reports_via_email": True,
            "user_email_address": "pythbuster@gmail.com",
        },
        {
            "id": 7,
            "created_at": datetime(2024, 8, 9, 10, 15, 0, tzinfo=timezone.utc),
            "modified_at": datetime(2024, 8, 10, 11, 45, 0, tzinfo=timezone.utc),
            "is_automated_saving_active": True,
            "savings_amount": -100,
            "overflow_moneybox_automated_savings_mode": OverflowMoneyboxAutomatedSavingsModeType.COLLECT,  # noqa: ignore  # pylint: disable=line-too-long
            "send_reports_via_email": False,
            "user_email_address": "1",  # Invalid email address
        },
        {
            "id": 8,
            "created_at": datetime(2024, 8, 9, 10, 15, 0, tzinfo=timezone.utc),
            "modified_at": datetime(2024, 8, 10, 11, 45, 0, tzinfo=timezone.utc),
            "is_automated_saving_active": True,
            "savings_amount": 100,
            "overflow_moneybox_automated_savings_mode": "unknown",  # Invalid enum value
            "send_reports_via_email": False,
            "user_email_address": None,
        },
        {
            "id": 9,
            "created_at": datetime(2024, 8, 9, 10, 15, 0, tzinfo=timezone.utc),
            "modified_at": datetime(2024, 8, 10, 11, 45, 0, tzinfo=timezone.utc),
            "is_automated_saving_active": True,
            "savings_amount": 100,
            "overflow_moneybox_automated_savings_mode": OverflowMoneyboxAutomatedSavingsModeType.COLLECT,  # noqa: ignore  # pylint: disable=line-too-long
            "send_reports_via_email": True,  # True, but user_email_address is not set
            "user_email_address": None,
        },
        {
            "id": 10,
            "created_at": datetime(2024, 8, 9, 10, 15, 0, tzinfo=timezone.utc),
            "modified_at": datetime(2024, 8, 10, 11, 45, 0, tzinfo=timezone.utc),
            "is_automated_saving_active": True,
            "savings_amount": 100,
            "overflow_moneybox_automated_savings_mode": OverflowMoneyboxAutomatedSavingsModeType.COLLECT,  # noqa: ignore  # pylint: disable=line-too-long
            "send_reports_via_email": True,
            "user_email_address": "",  # Empty email address (Invalid)
        },
        {
            "id": 11,
            "created_at": datetime(2024, 8, 9, 10, 15, 0, tzinfo=timezone.utc),
            "modified_at": "dsf",
            "is_automated_saving_active": True,
            "savings_amount": 100,
            "overflow_moneybox_automated_savings_mode": OverflowMoneyboxAutomatedSavingsModeType.COLLECT,  # noqa: ignore  # pylint: disable=line-too-long
            "send_reports_via_email": True,  # True, but user_email_address is not set
            "user_email_address": None,
        },
        {
            "id": 12,
            "created_at": "dsf",
            "modified_at": datetime(2024, 8, 9, 10, 15, 0, tzinfo=timezone.utc),
            "is_automated_saving_active": True,
            "savings_amount": 100,
            "overflow_moneybox_automated_savings_mode": OverflowMoneyboxAutomatedSavingsModeType.COLLECT,  # noqa: ignore  # pylint: disable=line-too-long
            "send_reports_via_email": True,  # True, but user_email_address is not set
            "user_email_address": None,
        },
        {
            "id": 13,
            "created_at": {},
            "modified_at": datetime(2024, 8, 9, 10, 15, 0, tzinfo=timezone.utc),
            "is_automated_saving_active": True,
            "savings_amount": 100,
            "overflow_moneybox_automated_savings_mode": OverflowMoneyboxAutomatedSavingsModeType.COLLECT,  # noqa: ignore  # pylint: disable=line-too-long
            "send_reports_via_email": True,  # True, but user_email_address is not set
            "user_email_address": None,
        },
        {
            "id": 14,
            "created_at": datetime(2024, 8, 9, 10, 15, 0, tzinfo=timezone.utc),
            "modified_at": {},
            "is_automated_saving_active": True,
            "savings_amount": 100,
            "overflow_moneybox_automated_savings_mode": OverflowMoneyboxAutomatedSavingsModeType.COLLECT,  # noqa: ignore  # pylint: disable=line-too-long
            "send_reports_via_email": True,  # True, but user_email_address is not set
            "user_email_address": None,
        },
    ],
)
def test_app_settings_response_invalid(data: dict[str, Any]) -> None:
    """Test AppSettingsResponse creation with invalid data."""
    with pytest.raises(ValidationError):
        AppSettingsResponse(**data)


def test_validate_multiple_overflow_moneyboxes() -> None:
    """Test that the validator raises an error when multiple Overflow Moneyboxes are present."""
    moneyboxes = [
        MoneyboxResponse(
            id=1,
            name="Overflow Moneybox 1",
            balance=0,
            savings_amount=0,
            savings_target=None,
            priority=0,
            created_at="2024-08-13 02:50:41.837275+00:00",
            modified_at=None,
            description="",
        ),
        MoneyboxResponse(
            id=2,
            name="Overflow Moneybox 2",
            balance=0,
            savings_amount=0,
            savings_target=None,
            priority=0,
            created_at="2024-08-13 02:50:41.837275+00:00",
            modified_at=None,
            description="",
        ),
        MoneyboxResponse(
            id=3,
            name="Holiday",
            balance=1000,
            savings_amount=50,
            savings_target=50000,
            priority=1,
            created_at="2024-08-13 02:50:41.837275+00:00",
            modified_at=None,
            description="",
        ),
    ]

    with pytest.raises(ValidationError, match="Multiple Overflow Moneyboxes are not allowed"):
        MoneyboxesResponse(moneyboxes=moneyboxes)


def test_validate_missing_overflow_moneybox() -> None:
    """Test that the validator raises an error when no Overflow Moneybox is present."""
    moneyboxes = [
        MoneyboxResponse(
            id=1,
            name="Holiday",
            balance=1000,
            savings_amount=50,
            savings_target=50000,
            priority=1,
            created_at="2024-08-13 02:50:41.837275+00:00",
            modified_at=None,
            description="",
        ),
        MoneyboxResponse(
            id=2,
            name="Emergency Fund",
            balance=2000,
            savings_amount=100,
            savings_target=10000,
            priority=2,
            created_at="2024-08-14 02:50:41.837275+00:00",
            modified_at=None,
            description="",
        ),
    ]

    with pytest.raises(ValidationError, match="Missing Overflow Moneybox"):
        MoneyboxesResponse(moneyboxes=moneyboxes)


def test_validate_valid_moneyboxes() -> None:
    """Test that no errors are raised for valid moneyboxes configuration."""
    moneyboxes = [
        MoneyboxResponse(
            id=1,
            name="Overflow Moneybox",
            balance=0,
            savings_amount=0,
            savings_target=None,
            priority=0,
            created_at="2024-08-13 02:50:41.837275+00:00",
            modified_at=None,
            description="",
        ),
        MoneyboxResponse(
            id=2,
            name="Holiday",
            balance=1000,
            savings_amount=50,
            savings_target=50000,
            priority=1,
            created_at="2024-08-15 02:50:41.837275+00:00",
            modified_at=None,
            description="",
        ),
    ]

    response = MoneyboxesResponse(moneyboxes=moneyboxes)
    assert response.total == 2  # Ensure the total computed field works correctly
