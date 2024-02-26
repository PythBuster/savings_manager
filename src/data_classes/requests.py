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

    balance: Annotated[
        int,
        Field(ge=0, description="The balance to add."),
    ]
    """The balance to add."""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "balance": 100,
                }
            ]
        },
    )
    """The config of the model."""


class WithdrawModel(BaseModel):
    """The pydantic moneybox withdraw data model."""

    balance: Annotated[
        int,
        Field(ge=0, description="The balance to sub."),
    ]
    """The balance to sub."""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "balance": 100,
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

    balance: Annotated[
        int,
        Field(ge=0, description="The balance to transfer."),
    ]
    """The balance to transfer."""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "to_moneybox_id": 1,
                    "balance": 50,
                }
            ]
        },
    )
    """The config of the model."""
