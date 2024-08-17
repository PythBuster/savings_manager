"""All request models are located here."""

from typing import Annotated, Any

from pydantic import BaseModel, ConfigDict, Field, StrictInt, model_validator


class MoneyboxCreateRequest(BaseModel):
    """The pydantic moneybox create request model."""

    name: Annotated[
        str, Field(min_length=1, description="The name of the moneybox. Has to be unique.")
    ]
    """The name of the moneybox. Has to be unique."""

    savings_amount: Annotated[
        StrictInt, Field(default=0, ge=0, description="The current savings amount of the moneybox.")
    ]
    """The current savings amount of the moneybox."""

    savings_target: Annotated[
        StrictInt | None,
        Field(
            default=0,
            ge=0,
            description=(
                "The current savings target. Is relevant for the automated "
                "distributed saving progress."
            ),
        ),
    ]
    """"The current savings target. Is relevant for the automated distributed saving progress."""

    priority: Annotated[StrictInt, Field(ge=1, description="The current priority of the moneybox.")]
    """The current priority of the moneybox."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        json_schema_extra={
            "examples": [
                {
                    "name": "Holiday",
                    "savings_amount": 0,
                    "savings_target": 50000,
                    "priority": 1,
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

    savings_amount: Annotated[
        StrictInt | None,
        Field(default=None, ge=0, description="The current savings amount of the moneybox."),
    ]
    """The current savings amount of the moneybox."""

    savings_target: Annotated[
        StrictInt | None,
        Field(
            default=None,
            ge=0,
            description=(
                "The current savings target. Is relevant for the automated "
                "distributed saving progress."
            ),
        ),
    ]
    """"The current savings target. Is relevant for the automated distributed saving progress."""

    priority: Annotated[
        StrictInt | None,
        Field(default=None, ge=1, description="The current priority of the moneybox."),
    ]
    """The current priority of the moneybox."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        json_schema_extra={
            "examples": [
                {
                    "name": "Holiday",
                    "savings_amount": 0,
                    "savings_target": 50000,
                    "priority": 1,
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


class PriorityRequest(BaseModel):
    """The priority request model."""

    moneybox_id: Annotated[StrictInt, Field(description="The id of the moneybox.")]
    """The id of the moneybox."""

    priority: Annotated[
        StrictInt,
        Field(
            ge=1,
            description="The priority of the moneybox.",
        ),
    ]
    """The priority of the moneybox."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        json_schema_extra={"examples": [{"moneybox_id": 4, "priority": 1}]},
    )
    """The config of the model."""


class PrioritylistRequest(BaseModel):
    """The priority list request model."""

    priority_list: Annotated[
        list[PriorityRequest],
        Field(min_length=1, description="The priority list."),
    ]
    """The priority list."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        json_schema_extra={
            "examples": [
                {
                    "priority_list": [
                        {
                            "moneybox_id": 1,
                            "priority": 0,
                        },
                        {"moneybox_id": 2, "priority": 2},
                        {"moneybox_id": 4, "priority": 1},
                    ],
                },
            ],
        },
    )
    """The config of the model."""


class AppSettingsRequest(BaseModel):
    """The app settings request model."""

    is_automated_saving_active: Annotated[
        bool | None,
        Field(description="Tells if automated saving is active."),
    ] = None
    """Tells if automated saving is active."""

    savings_amount: Annotated[
        StrictInt | None,
        Field(
            ge=0,
            description=(
                "The savings amount for the automated saving which will be distributed "
                "periodically to the moneyboxes, which have a (desired) savings amount > 0."
            ),
        ),
    ] = None
    """The savings amount for the automated saving which will be distributed
    periodically to the moneyboxes, which have a (desired) savings amount > 0."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        json_schema_extra={
            "examples": [
                {
                    "is_automated_saving_active": True,
                    "savings_amount": 60000,
                },
            ],
        },
    )
    """The config of the model."""

    @model_validator(mode="before")
    @classmethod
    def lower_case_enum_str_automated_saving_trigger_day(
        cls, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Lower case 'automated_saving_trigger_day' if type is str."""

        if "automated_saving_trigger_day" in data and isinstance(
            data["automated_saving_trigger_day"], str
        ):
            data["automated_saving_trigger_day"] = data["automated_saving_trigger_day"].lower()

        return data
