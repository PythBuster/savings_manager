"""All response models are located here."""

from typing import Annotated, Any

from pydantic import BaseModel, ConfigDict, Field


class HTTPErrorResponse(BaseModel):
    """The http error response model"""

    message: Annotated[str, Field(min_length=1, description="The error message.")]
    detail: Annotated[dict[str, Any] | None, Field(default=None, description="The error details.")]

    model_config = ConfigDict(
        extra="forbid",
    )


class MoneyboxResponse(BaseModel):
    """The pydantic moneybox response data model"""

    id: int
    name: Annotated[
        str, Field(min_length=1, description="The name of the moneybox. Has to be unique.")
    ]
    balance: Annotated[
        int, Field(ge=0, default=0, description="The balance of the moneybox in CENTS.")
    ]

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


class MoneyboxesResponse(BaseModel):
    """The moneyboxes response model."""

    total: Annotated[int, Field(ge=0, description="The count of moneyboxes.")]
    moneyboxes: Annotated[list[MoneyboxResponse], Field(description="The list of moneyboxes.")]

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
