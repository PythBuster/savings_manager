"""All transaction log response model tests are located here."""

from datetime import datetime
from typing import Any

import pytest

from src.custom_types import TransactionType, TransactionTrigger
from src.data_classes.responses import TransactionLogResponse


@pytest.mark.parametrize(
    "data",
    [
        {
            "id": 1,
            "counterparty_moneybox_name": "Holiday",
            "description": "A Description",
            "transaction_type": TransactionType.DIRECT,
            "transaction_trigger": TransactionTrigger.MANUALLY,
            "amount": 123,
            "balance": 123,
            "counterparty_moneybox_id": 2,
            "moneybox_id": 1,
            "created_at": "2020-05-01T00:00:00Z",
        },
        {
            "id": 2,
            "counterparty_moneybox_name": None,
            "description": "A Description",
            "transaction_type": TransactionType.DIRECT,
            "transaction_trigger": TransactionTrigger.MANUALLY,
            "amount": -1,
            "balance": 0,
            "counterparty_moneybox_id": None,
            "moneybox_id": 2,
            "created_at": "2020-05-01T00:00:00Z",
        },
        {
            "id": 3,
            "counterparty_moneybox_name": "Holymoly",
            "description": "",
            "transaction_type": TransactionType.DISTRIBUTION,
            "transaction_trigger": TransactionTrigger.AUTOMATICALLY,
            "amount": 1,
            "balance": 100,
            "counterparty_moneybox_id": 1,
            "moneybox_id": 3,
            "created_at": "2020-05-01T00:00:00Z",
        },
        {
            "id": 4,
            "counterparty_moneybox_name": "Holiday",
            "description": "A Description",
            "transaction_type": TransactionType.DIRECT,
            "transaction_trigger": TransactionTrigger.MANUALLY,
            "amount": -123,
            "balance": 0,
            "counterparty_moneybox_id": 2,
            "moneybox_id": 4,
            "created_at": "2020-05-01T00:00:00Z",
        },
    ],
)
def test_transaction_log_response_valid_data(data: dict[str, Any]):
    """Test valid TransactionLog creation."""

    data_id = data["id"]
    data_counterparty_moneybox_name = data["counterparty_moneybox_name"]
    data_description = data["description"]
    data_transaction_type = data["transaction_type"]
    data_transaction_trigger = data["transaction_trigger"]
    data_amount = data["amount"]
    data_balance = data["balance"]
    data_counterparty_moneybox_id = data["counterparty_moneybox_id"]
    data_moneybox_id = data["moneybox_id"]
    data_created_at = datetime.fromisoformat(data["created_at"])

    response = TransactionLogResponse(**data)

    assert response.id == data_id
    assert response.counterparty_moneybox_name == data_counterparty_moneybox_name
    assert response.description == data_description
    assert response.transaction_type == data_transaction_type
    assert response.transaction_trigger == data_transaction_trigger
    assert response.amount == data_amount
    assert response.balance == data_balance
    assert response.counterparty_moneybox_id == data_counterparty_moneybox_id
    assert response.moneybox_id == data_moneybox_id
    assert response.created_at == data_created_at
