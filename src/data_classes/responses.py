"""All response models are located here."""

from datetime import datetime
from typing import Annotated, Any, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from src.custom_types import TransactionTrigger, TransactionType


class HTTPErrorResponse(BaseModel):
    """The http error response model"""

    message: Annotated[str, Field(min_length=1, description="The error message.")]
    """The error message."""

    details: Annotated[dict[str, Any] | None, Field(default=None, description="The error details.")]
    """The error details."""

    model_config = ConfigDict(
        extra="forbid",
    )
    """The config of the model."""


class MoneyboxResponse(BaseModel):
    """The pydantic moneybox response data model"""

    id: Annotated[int, Field(ge=1, description="The id of the moneybox.")]
    """The id of the moneybox."""

    name: Annotated[
        str, Field(min_length=1, description="The name of the moneybox. Has to be unique.")
    ]
    """The name of the moneybox. Has to be unique."""

    balance: Annotated[int, Field(ge=0, description="The balance of the moneybox in CENTS.")]
    """The balance of the moneybox in CENTS."""

    created_at: Annotated[datetime, Field(description="The creation date of the moneybox.")]
    """The creation date of the moneybox."""

    modified_at: Annotated[
        datetime | None, Field(description="The modification date of the moneybox.")
    ]
    """The modification date of the moneybox."""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "name": "Holiday",
                    "balance": 0,
                    "created_at": "2020-05-01T00:00:00Z",
                    "modified_at": None,
                }
            ]
        },
    )
    """The config of the model."""

    @model_validator(mode="after")
    def validate_date_order(self) -> Self:
        """Check if 'modified_at' date is after 'created_at'."""

        if self.modified_at is not None and self.created_at >= self.modified_at:
            msg = "Error: 'created_at' comes after 'modified_at'."
            raise ValueError(msg)

        return self


class MoneyboxesResponse(BaseModel):
    """The moneyboxes response model."""

    total: Annotated[int, Field(ge=0, description="The count of moneyboxes.")]
    """The count of moneyboxes."""

    moneyboxes: Annotated[list[MoneyboxResponse], Field(description="The list of moneyboxes.")]
    """The list of moneyboxes."""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "total": 2,
                    "moneyboxes": [
                        {
                            "id": 1,
                            "name": "Holiday",
                            "balance": 1255,
                        },
                        {
                            "id": 2,
                            "name": "Extra Bills",
                            "balance": 250,
                        },
                    ],
                }
            ]
        },
    )
    """The config of the model."""


class TransactionLog(BaseModel):
    """The transaction log response model."""

    description: Annotated[str, Field(description="The description of the transaction action.")]
    """The description of the transaction action."""

    transaction_type: Annotated[
        TransactionType,
        Field(description="The type of the transaction. Possible values: direct or distribution."),
    ]
    """The type of the transaction. Possible values: direct or distribution."""

    transaction_trigger: Annotated[
        TransactionTrigger,
        Field(
            description=(
                "The transaction trigger type, possible values: manually, automatically. "
                "Says, if balance was deposit or withdrawn manually or automatically."
            ),
        ),
    ]
    """"The transaction type, possible values: manually, automatically.
    Says, if balance was deposit or withdrawn manually or automatically."""

    amount: Annotated[
        int,
        Field(
            description=(
                "The current amount of the transaction. "
                "Can be negative, negative = withdraw, positive = deposit."
            ),
        ),
    ]
    """The current amount of the transaction.
    Can be negative, negative = withdraw, positive = deposit."""

    balance: Annotated[
        int,
        Field(
            description="The balance of the moneybox at the time of the transaction.",
        ),
    ]
    """The balance of the moneybox at the time of the transaction."""

    counterparty_moneybox_id: Annotated[
        int | None,
        Field(
            description=(
                "Transaction is a transfer between moneybox_id and "
                "counterparty_moneybox_id, if set."
            ),
        ),
    ]
    """Transaction is a transfer between moneybox_id and
    counterparty_moneybox_id, if set."""

    moneybox_id: Annotated[int, Field(description="The foreign key to moneybox.")]
    """The foreign key to moneybox."""


class TransactionLogs(BaseModel):
    """The transaction logs response model."""

    total: Annotated[int, Field(ge=0, description="The count of transaction logs.")]
    """The count of transaction logs."""

    transaction_logs: Annotated[
        list[TransactionLog], Field(description="The list of transaction logs.")
    ]
    """The list of transaction logs."""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "total": 2,
                    "transaction_logs": [
                        {
                            "id": 1,
                            "name": "Holiday",
                            "balance": 1255,
                        },
                        {
                            "id": 2,
                            "name": "Extra Bills",
                            "balance": 250,
                        },
                    ],
                }
            ]
        },
    )
    """The config of the model."""
