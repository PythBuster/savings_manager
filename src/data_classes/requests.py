"""All request models are located here."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


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
        Field(ge=1, description="The amount to add, value has to be at least 1."),
    ]
    """The amount to add, value has to be at least 1."""

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
        Field(ge=1, description="The amount to sub, value has to be at least 1."),
    ]
    """The amount to sub, value has to be at least 1."""

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
        Field(description="The id of the moneybox to transfer balance to."),
    ]
    """The id of the moneybox to transfer balance to."""

    amount: Annotated[
        int,
        Field(ge=1, description="The amount to transfer, value has to be at least 1."),
    ]
    """The amount to transfer, value has to be at least 1."""

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


class DepositTransactionModel(BaseModel):
    """The deposit transaction pydantic model"""

    amount: Annotated[
        int,
        Field(ge=1, description="The amount to add, value has to be at least 1."),
    ]
    """The amount to add, value has to be at least 1."""

    description: Annotated[
        str,
        Field(default="", description="The description of the withdraw transaction."),
    ]
    """The description of the withdraw transaction."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        json_schema_extra={
            "examples": [
                {
                    "amount": 50,
                    "description": "Bonus.",
                }
            ]
        },
    )
    """The config of the model."""


class WithdrawTransactionModel(BaseModel):
    """The withdrawal transaction pydantic model"""

    amount: Annotated[
        int,
        Field(ge=1, description="The amount to sub, value has to be at least 1."),
    ]
    """The amount to sub, value has to be at least 1."""

    description: Annotated[
        str,
        Field(default="", description="The description of the withdraw transaction."),
    ]
    """The description of the withdraw transaction."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        json_schema_extra={
            "examples": [
                {
                    "amount": 50,
                    "description": "Gift.",
                }
            ]
        },
    )
    """The config of the model."""


class TransferTransactionModel(BaseModel):
    """The transfer transaction pydantic model"""

    to_moneybox_id: Annotated[
        int,
        Field(description="The id of the moneybox to transfer balance to."),
    ]
    """The id of the moneybox to transfer balance to."""

    amount: Annotated[
        int,
        Field(ge=1, description="The amount to transfer, value has to be at least 1."),
    ]
    """The amount to transfer, value has to be at least 1."""

    description: Annotated[
        str,
        Field(default="", description="The description of the withdraw transaction."),
    ]
    """The description of the withdraw transaction."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        json_schema_extra={
            "examples": [
                {
                    "amount": 50,
                    "to_moneybox_id": 3,
                    "description": "Delete Moneybox.",
                }
            ]
        },
    )
    """The config of the model."""
