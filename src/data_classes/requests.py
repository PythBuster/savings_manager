"""All request models are located here."""

from typing import Annotated, Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field, StrictInt, model_validator

from src.custom_types import OverflowMoneyboxAutomatedSavingsModeType


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
        str,
        Field(
            default=None, min_length=1, description="The name of the moneybox. Has to be unique."
        ),
    ]
    """The name of the moneybox. Has to be unique."""

    savings_amount: Annotated[
        StrictInt,
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

    send_reports_via_email: Annotated[
        bool,
        Field(
            default=None,
            description="Tells if receiving reports via report_sender is desired.",
        ),
    ]
    """Tells if receiving reports via report_sender is desired."""

    user_email_address: Annotated[
        EmailStr | None,
        Field(
            default=None,
            description="Users report_sender address. Will used for receiving reports.",
        ),
    ]
    """Users report_sender address. Will used for receiving reports."""

    is_automated_saving_active: Annotated[
        bool,
        Field(
            default=None,
            description="Tells if automated saving is active.",
        ),
    ]
    """Tells if automated saving is active."""

    savings_amount: Annotated[
        StrictInt,
        Field(
            default=None,
            ge=0,
            description=(
                "The savings amount for the automated saving which will be distributed "
                "periodically to the moneyboxes, which have a (desired) savings amount > 0."
            ),
        ),
    ]
    """The savings amount for the automated saving which will be distributed
    periodically to the moneyboxes, which have a (desired) savings amount > 0."""

    overflow_moneybox_automated_savings_mode: Annotated[
        OverflowMoneyboxAutomatedSavingsModeType,
        Field(
            default=None,
            description="The mode for automated savings.",
        ),
    ]
    """"The mode for automated savings."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        json_schema_extra={
            "examples": [
                {
                    "send_reports_via_email": True,
                    "user_email_address": "pythbuster@gmail.com",
                    "is_automated_saving_active": True,
                    "savings_amount": 60000,
                    "overflow_moneybox_automated_savings_mode": OverflowMoneyboxAutomatedSavingsModeType.COLLECT,  # noqa: ignore  # pylint: disable=line-too-long
                },
            ],
        },
    )
    """The config of the model."""

    @model_validator(mode="before")
    @classmethod
    def lower_case_enum_strings(cls, data: dict[str, Any]) -> dict[str, Any]:
        """Lower case enum strings."""

        if "overflow_moneybox_automated_savings_mode" in data and isinstance(
            data["overflow_moneybox_automated_savings_mode"], str
        ):
            data["overflow_moneybox_automated_savings_mode"] = data[
                "overflow_moneybox_automated_savings_mode"
            ].lower()

        return data
