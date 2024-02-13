"""All moneybox pydantic models are located here."""

from typing import Annotated

from pydantic import BaseModel, Field


class MoneyboxResponse(BaseModel):
    """The pydantic moneybox data model"""

    id: int
    name: str
    balance: Annotated[int, Field(ge=0, default=0)]
