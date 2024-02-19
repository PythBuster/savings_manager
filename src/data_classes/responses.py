"""All response models are located here."""

from typing import Annotated, Any

from pydantic import BaseModel, ConfigDict, Field


class HTTPErrorResponse(BaseModel):
    """The http error response model"""

    message: Annotated[str, Field(min_length=1, description="The error message.")]
    """The error message."""

    detail: Annotated[dict[str, Any] | None, Field(default=None, description="The error details.")]
    """The error details."""

    model_config = ConfigDict(
        extra="forbid",
    )
    """The model config for the HTTPErrorResponse model."""


class MoneyboxResponse(BaseModel):
    """The pydantic moneybox response data model"""

    id: Annotated[int, Field(ge=1, description="The id of the moneybox.")]
    """The id of the moneybox."""

    name: Annotated[
        str, Field(min_length=1, description="The name of the moneybox. Has to be unique.")
    ]
    """The name of the moneybox. Has to be unique."""

    balance: Annotated[
        int, Field(ge=0, default=0, description="The balance of the moneybox in CENTS.")
    ]
    """The balance of the moneybox in CENTS."""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "name": "Holiday",
                    "balance": 0,
                }
            ]
        },
    )
    """The model config for the MoneyboxResponse model."""


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
    """The model config for the MoneyboxesResponse model."""
