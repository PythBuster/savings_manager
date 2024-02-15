"""All request models are located here."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class MoneyboxPostRequest(BaseModel):
    """The pydantic moneybox POST request data model"""

    name: str = Field(description="The name of the moneybox. Has to be unique.")
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
