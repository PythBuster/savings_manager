"""All response models are located here."""

from typing import Annotated, Any

from pydantic import BaseModel, ConfigDict, Field


class HTTPErrorResponse(BaseModel):
    """The http error response model"""

    message: str = Field(min_length=1)
    detail: dict[str, Any] | None = None

    model_config = ConfigDict(
        extra="forbid",
    )


class MoneyboxResponse(BaseModel):
    """The pydantic moneybox response data model"""

    id: int

    name: str
    balance: Annotated[int, Field(ge=0, default=0)]

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "name": "Holiday",
                    "balance": 1255,
                }
            ]
        },
    )
