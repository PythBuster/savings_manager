"""All request models are located here."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from src.custom_types import TransactionTrigger, TransactionType


class MoneyboxCreateModel(BaseModel):
    """The pydantic moneybox create data model."""

    name: Annotated[
        str, Field(min_length=1, description="The name of the moneybox. Has to be unique.")
    ]
    """The name of the moneybox. Has to be unique."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        json_schema_extra={
            "examples": [
                {
                    "name": "Holiday",
                }
            ]
        },
    )
    """The config of the model."""


class MoneyboxUpdateModel(BaseModel):
    """The pydantic moneybox update data model."""

    name: Annotated[
        str | None,
        Field(
            default=None, min_length=1, description="The name of the moneybox. Has to be unique."
        ),
    ]
    """The name of the moneybox. Has to be unique."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        json_schema_extra={
            "examples": [
                {
                    "name": "Holiday",
                }
            ]
        },
    )
    """The config of the model."""


class DepositModel(BaseModel):
    """The pydantic moneybox deposit data model."""

    amount: Annotated[
        int,
        Field(ge=0, description="The amount to add."),
    ]
    """The amount to add."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        json_schema_extra={
            "examples": [
                {
                    "amount": 100,
                }
            ]
        },
    )
    """The config of the model."""


class WithdrawModel(BaseModel):
    """The pydantic moneybox withdraw data model."""

    amount: Annotated[
        int,
        Field(ge=0, description="The amount to sub."),
    ]
    """The amount to sub."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        json_schema_extra={
            "examples": [
                {
                    "amount": 100,
                }
            ]
        },
    )
    """The config of the model."""


class TransferModel(BaseModel):
    """The pydantic moneybox transfer balance data model."""

    to_moneybox_id: Annotated[
        int,
        Field(ge=1, description="The id of the moneybox to transfer balance to."),
    ]
    """The id of the moneybox to transfer balance to."""

    amount: Annotated[
        int,
        Field(ge=0, description="The amount to transfer."),
    ]
    """The amount to transfer."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        json_schema_extra={
            "examples": [
                {
                    "to_moneybox_id": 1,
                    "amount": 50,
                }
            ]
        },
    )
    """The config of the model."""


class TransactionMetaModel(BaseModel):
    """The transaction meta pydantic model."""

    description: Annotated[
        str,
        Field(description="The description of the withdraw transaction."),
    ]
    """The description of the withdraw transaction."""

    transaction_trigger: Annotated[
        TransactionTrigger,
        Field(
            description="The transaction trigger, defaults to `manually`.",
        ),
    ]
    """The transaction trigger, defaults to `manually`."""

    transaction_type: Annotated[
        TransactionType,
        Field(
            description="The transaction type, defaults to `direct`.",
        ),
    ]
    """The transaction type, defaults to `direct`."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        json_schema_extra={
            "examples": [
                {
                    "description": "Bonus.",
                    "transaction_trigger": TransactionTrigger.MANUALLY,
                    "transaction_type": TransactionType.DIRECT,
                },
                {
                    "description": "Unexpected expenses.",
                    "transaction_trigger": TransactionTrigger.MANUALLY,
                    "transaction_type": TransactionType.DIRECT,
                },
                {
                    "description": "Transfer money.",
                    "transaction_trigger": TransactionTrigger.MANUALLY,
                    "transaction_type": TransactionType.DIRECT,
                },
            ]
        },
    )
    """The config of the model."""


class DepositTransactionModel(BaseModel):
    """The deposit transaction pydantic model"""

    deposit_data: Annotated[DepositModel, Field(description="The deposit data.")]
    """The deposit data."""

    transaction_data: Annotated[
        TransactionMetaModel, Field(description="The transaction meta data.")
    ]
    """The transaction data."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        json_schema_extra={
            "examples": [
                {
                    "deposit_data": DepositModel.model_config["json_schema_extra"]["examples"][0],
                    "transaction_data": TransactionMetaModel.model_config["json_schema_extra"][
                        "examples"
                    ][0],
                }
            ]
        },
    )
    """The config of the model."""


class WithdrawTransactionModel(BaseModel):
    """The withdrawal transaction pydantic model"""

    withdraw_data: Annotated[WithdrawModel, Field(description="The withdraw data.")]
    """The withdraw data."""

    transaction_data: Annotated[
        TransactionMetaModel, Field(description="The transaction meta data.")
    ]
    """The transaction data."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        json_schema_extra={
            "examples": [
                {
                    "withdraw_data": WithdrawModel.model_config["json_schema_extra"]["examples"][0],
                    "transaction_data": TransactionMetaModel.model_config["json_schema_extra"][
                        "examples"
                    ][1],
                }
            ]
        },
    )
    """The config of the model."""


class TransferTransactionModel(BaseModel):
    """The transfer transaction pydantic model"""

    transfer_data: Annotated[TransferModel, Field(description="The transfer data.")]
    """The transfer data."""

    transaction_data: Annotated[
        TransactionMetaModel, Field(description="The transaction meta data.")
    ]
    """The transaction data."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        json_schema_extra={
            "examples": [
                {
                    "transfer_data": TransferModel.model_config["json_schema_extra"]["examples"][0],
                    "transaction_data": TransactionMetaModel.model_config["json_schema_extra"][
                        "examples"
                    ][2],
                }
            ]
        },
    )
    """The config of the model."""
