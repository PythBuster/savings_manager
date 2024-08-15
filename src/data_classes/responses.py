"""All response models are located here."""

from datetime import datetime
from typing import Annotated, Any, Self

from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    StrictInt,
    computed_field,
    field_validator,
    model_validator,
)

from src.custom_types import TransactionTrigger, TransactionType


class HTTPErrorResponse(BaseModel):
    """The http error response model"""

    message: Annotated[str, Field(min_length=1, description="The error message.")]
    """The error message."""

    details: Annotated[dict[str, Any] | None, Field(default=None, description="The error details.")]
    """The error details."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        json_schema_extra={
            "examples": [
                {
                    "message": "No database connection.",
                    "details": {
                        "message": "Connect call failed ('127.0.0.1', 5432)",
                    },
                },
            ]
        },
    )
    """The config of the model."""


class MoneyboxResponse(BaseModel):
    """The pydantic moneybox response model"""

    id: Annotated[StrictInt, Field(description="The id of the moneybox.")]
    """The id of the moneybox."""

    name: Annotated[
        str, Field(min_length=1, description="The name of the moneybox. Has to be unique.")
    ]
    """The name of the moneybox. Has to be unique."""

    balance: Annotated[StrictInt, Field(ge=0, description="The balance of the moneybox in CENTS.")]
    """The balance of the moneybox in CENTS."""

    savings_amount: Annotated[
        StrictInt, Field(ge=0, description="The current savings amount of the moneybox.")
    ]
    """The current savings amount of the moneybox."""

    savings_target: Annotated[
        StrictInt | None,
        Field(
            ge=0,
            description=(
                "The current savings target. Is relevant for the automated "
                "distributed saving progress."
            ),
        ),
    ]
    """"The current savings target. Is relevant for the automated distributed saving progress."""

    priority: Annotated[
        StrictInt | None,
        Field(
            ge=0,
            description=(
                "The current priority of the moneybox. There is only one moneybox with "
                "a priority of Null (will be the marker for the overflow moneybox."
            ),
        ),
    ]
    """The current priority of the moneybox. There is only one moneybox with
    a priority of Null (will be the marker for the overflow moneybox)."""

    created_at: Annotated[AwareDatetime, Field(description="The creation date of the moneybox.")]
    """The creation date of the moneybox."""

    modified_at: Annotated[
        AwareDatetime | None, Field(description="The modification date of the moneybox.")
    ]
    """The modification date of the moneybox."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "name": "Holiday",
                    "balance": 0,
                    "savings_amount": 0,
                    "savings_target": 50000,
                    "priority": 1,
                    "created_at": "2024-08-11 13:57:17.941840 +00:00",
                    "modified_at": "2024-08-11 15:03:17.312860 +00:00",
                }
            ]
        },
    )
    """The config of the model."""

    @model_validator(mode="before")
    @classmethod
    def convert_to_strict_datetimes(cls, data: dict[Any, Any]) -> dict[Any, Any]:
        """Check if 'modified_at' and 'created_at' is type datetime."""

        if data["modified_at"] is not None:
            if isinstance(data["modified_at"], str):
                try:
                    data["modified_at"] = datetime.fromisoformat(data["modified_at"])
                except (TypeError, ValueError) as ex:
                    raise ValueError(
                        "'created_at' must be of type datetime or datetime-string."
                    ) from ex
            elif not isinstance(data["modified_at"], datetime):
                raise ValueError("'modified_at' must be of type datetime or datetime-string.")

        if isinstance(data["created_at"], str):
            try:
                data["created_at"] = datetime.fromisoformat(data["created_at"])
            except (TypeError, ValueError) as ex:
                raise ValueError(
                    "'created_at' must be of type datetime or datetime-string."
                ) from ex

        elif not isinstance(data["created_at"], datetime):
            raise ValueError("'created_at' must be of type datetime or datetime-string.")

        return data

    @model_validator(mode="after")
    def validate_date_order(self) -> Self:
        """Check if 'modified_at' date is after 'created_at'."""

        # create_at datetime has to be smaller than modified_at datetime!
        #   created_at == modified_at is not allowed
        if self.modified_at is not None and self.created_at >= self.modified_at:
            msg = "Error: 'created_at' comes after 'modified_at'."
            raise ValueError(msg)

        return self


class MoneyboxesResponse(BaseModel):
    """The moneyboxes response model."""

    moneyboxes: Annotated[
        list[MoneyboxResponse], Field(min_length=1, description="The list of moneyboxes.")
    ]
    """The list of moneyboxes."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        json_schema_extra={
            "examples": [
                {
                    "total": 2,
                    "moneyboxes": [
                        {
                            "id": 1,
                            "name": "672c0145-c910-4ce8-8202-d6ce9ba405a4",
                            "balance": 0,
                            "savings_amount": 0,
                            "savings_target": None,
                            "priority": 0,
                            "created_at": "2024-08-13 02:50:41.837275 +00:00",
                            "modified_at": None,
                        },
                        {
                            "id": 2,
                            "name": "Holiday",
                            "balance": 1050,
                            "savings_amount": 50,
                            "savings_target": 50000,
                            "priority": 1,
                            "created_at": "2024-08-16 02:50:41.837275 +00:00",
                            "modified_at": "2024-08-17 04:41:45.126672 +00:00",
                        },
                    ],
                }
            ]
        },
    )
    """The config of the model."""

    @computed_field  # type: ignore
    @property
    def total(self) -> int:
        """The count of moneyboxes."""

        return len(self.moneyboxes)


class TransactionLogResponse(BaseModel):
    """The transaction log response model."""

    id: Annotated[StrictInt, Field(description="The ID of the transaction.")]
    """The ID of the transaction."""

    counterparty_moneybox_name: Annotated[
        str | None, Field(min_length=1, description="The name of the counterparty moneybox.")
    ]
    """The name of the counterparty moneybox."""

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
        StrictInt,
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
        StrictInt,
        Field(
            ge=0,
            description="The new balance of the moneybox after the transaction.",
        ),
    ]
    """The new balance of the moneybox after the transaction."""

    counterparty_moneybox_id: Annotated[
        StrictInt | None,
        Field(
            description=(
                "Transaction is a transfer between moneybox_id and "
                "counterparty_moneybox_id, if set."
            ),
        ),
    ]
    """Transaction is a transfer between moneybox_id and
    counterparty_moneybox_id, if set."""

    moneybox_id: Annotated[StrictInt, Field(description="The foreign key to moneybox.")]
    """The foreign key to moneybox."""

    created_at: Annotated[datetime, Field(description="The creation date of the transaction log.")]
    """The creation date of the transaction log."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "moneybox_id": 1,
                    "description": "Transfer Money.",
                    "transaction_type": TransactionType.DIRECT,
                    "transaction_trigger": TransactionTrigger.MANUALLY,
                    "amount": 50,
                    "balance": 50,
                    "counterparty_moneybox_id": 3,
                    "counterparty_moneybox_name": "Moneybox 3",
                    "created_at": "2024-08-11 13:57:17.941840 +00:00",
                }
            ]
        },
    )
    """The config of the model."""

    @field_validator("amount")
    @classmethod
    def check_amount(cls, value: int) -> int:
        """Check if amount is != 0. Transactions with amount of 0 doesn't make sense."""

        if value == 0:
            raise ValueError("Amount has to be positive or negative for the transaction.")

        return value

    @model_validator(mode="before")
    @classmethod
    def convert_to_strict_datetimes(cls, data: dict[str, Any]) -> dict[str, Any]:
        """Check if 'modified_at' and 'created_at' is type datetime."""

        if isinstance(data["created_at"], str):
            try:
                data["created_at"] = datetime.fromisoformat(data["created_at"])
            except (TypeError, ValueError) as ex:
                raise ValueError(
                    "'created_at' must be of type datetime or datetime-string."
                ) from ex
        elif not isinstance(data["created_at"], datetime):
            raise ValueError("'created_at' must be of type datetime or datetime-string.")

        return data

    @model_validator(mode="after")
    @classmethod
    def check_transaction_trigger_and_type_combination(cls, self: Self) -> Self:
        """Check for combinations:
        - TransactionType.DIRECT + TransactionTrigger.AUTOMATICALLY
        - TransactionType.DISTRIBUTION + TransactionTrigger.DIRECT

        and raise exception if combination occurs."""

        if (
            self.transaction_type is not TransactionType.DIRECT
            and self.transaction_trigger is not TransactionTrigger.AUTOMATICALLY
        ):
            raise ValueError(
                "Invalid transaction type and transaction trigger combination!"
                "An automated-direct action is not allowed for now."
            )

        if (
            self.transaction_type is not TransactionType.DISTRIBUTION
            and self.transaction_trigger is not TransactionTrigger.MANUALLY
        ):
            raise ValueError(
                "Invalid transaction type and transaction trigger combination!"
                "A manual-distributed action is not allowed for now."
            )

        return self

    @model_validator(mode="after")
    @classmethod
    def check_counterparty_moneybox(cls, self: Self) -> Self:
        """If counterparty_moneybox_name is set, counterparty_moneybox_id need to be set too."""

        if (self.counterparty_moneybox_name is None) != (self.counterparty_moneybox_id is None):
            raise ValueError("Invalid combination: If one is None, the other must also be None.")

        return self

    @model_validator(mode="after")
    @classmethod
    def check_moneybox_id(cls, self: Self) -> Self:
        """moneybox_id must not be the same as counterparty_moneybox_id"""

        if self.moneybox_id == self.counterparty_moneybox_id:
            raise ValueError("moneybox_id must not be the same as counterparty_moneybox_id.")

        return self

    @model_validator(mode="after")
    @classmethod
    def check_new_balance(cls, self: Self) -> Self:
        """Check balance
        - if amount is positive, balance must be at least greater than or equal to amount.

        raise exception if not."""

        if self.amount > 0 and self.balance < self.amount:
            raise ValueError(
                "New balance of the moneybox must be at least greater than or equal to amount."
            )

        return self

    @model_validator(mode="before")
    @classmethod
    def lowercase_enum_strings(cls, data: dict[Any, Any]) -> dict[Any, Any]:
        """Lowercase transaction type and transaction trigger strings."""

        if "transaction_type" in data and isinstance(data["transaction_type"], str):
            data["transaction_type"] = data["transaction_type"].lower()

        if "transaction_trigger" in data and isinstance(data["transaction_trigger"], str):
            data["transaction_trigger"] = data["transaction_trigger"].lower()

        return data


class TransactionLogsResponse(BaseModel):
    """The transaction logs response model."""

    transaction_logs: Annotated[
        list[TransactionLogResponse], Field(description="The list of transaction logs.")
    ]
    """The list of transaction logs."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        json_schema_extra={
            "examples": [
                {
                    "total": 1,
                    "transaction_logs": [
                        TransactionLogResponse.model_config["json_schema_extra"]["examples"][0],
                    ],
                }
            ]
        },
    )
    """The config of the model."""

    @computed_field  # type: ignore
    @property
    def total(self) -> int:
        """The count of transaction logs."""

        return len(self.transaction_logs)


class PriorityResponse(BaseModel):
    """The priority response model."""

    moneybox_id: Annotated[StrictInt, Field(description="The id of the moneybox.")]
    """The id of the moneybox."""

    name: Annotated[str, Field(min_length=1, description="The name of the moneybox.")]
    """The name of the moneybox."""

    priority: Annotated[StrictInt, Field(ge=1, description="The priority of the moneybox.")]
    """The priority of the moneybox."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        json_schema_extra={"examples": [{"moneybox_id": 4, "name": "Holiday", "priority": 1}]},
    )
    """The config of the model."""


class PrioritylistResponse(BaseModel):
    """The priority list response model."""

    priority_list: Annotated[
        list[PriorityResponse],
        Field(min_length=1, description="The priority list."),
    ]
    """The priority list."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        json_schema_extra={
            "examples": [
                {
                    "priority_list": [
                        {
                            "moneybox_id": 1,
                            "name": "672c0145-c910-4ce8-8202-d6ce9ba405a4",
                            "priority": 0,
                        },
                        {"moneybox_id": 2, "name": "Reserves", "priority": 2},
                        {"moneybox_id": 4, "name": "Holiday", "priority": 1},
                    ],
                },
            ],
        },
    )
    """The config of the model."""
