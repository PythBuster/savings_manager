"""All request models are located here."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class MoneyboxCreateRequest(BaseModel):
    """The pydantic moneybox create request model."""

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


class MoneyboxUpdateRequest(BaseModel):
    """The pydantic moneybox update request model."""

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


class DepositRequest(BaseModel):
    """The pydantic moneybox deposit request model."""

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


class WithdrawRequest(BaseModel):
    """The pydantic moneybox withdraw request model."""

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


class TransferRequest(BaseModel):
    """The pydantic moneybox transfer balance request model."""

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


class DepositTransactionRequest(BaseModel):
    """The deposit transaction request model"""

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


class WithdrawTransactionRequest(BaseModel):
    """The withdrawal transaction request model"""

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


class TransferTransactionRequest(BaseModel):
    """The transfer transaction request model"""

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
