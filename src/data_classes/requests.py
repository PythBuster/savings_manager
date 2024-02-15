"""All request models are located here."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class MoneyboxPostRequest(BaseModel):
    """The pydantic moneybox POST request data model"""

    name: Annotated[str, Field(description="The name of the moneybox. Has to be unique.")]
    balance: Annotated[
        int, Field(ge=0, default=0, description="The balance of the moneybox in CENTS.")
    ]

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "name": "Holiday",
                    "balance": 1000,
                }
            ]
        },
    )


class MoneyboxPatchRequest(BaseModel):
    """The pydantic moneybox POST request data model"""

    name: Annotated[
        str | None, Field(description="The name of the moneybox. Has to be unique.")
    ] = None
    balance: Annotated[
        int | None, Field(ge=0, description="The balance of the moneybox in CENTS.")
    ] = None

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "name": "Holiday",
                    "balance": 1000,
                }
            ]
        },
    )
