"""All request models are located here."""

from typing import Annotated, Any

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    StringConstraints,
    field_validator,
    model_validator,
)

from src.custom_types import OverflowMoneyboxAutomatedSavingsModeType
from src.utils import to_camel_cleaned_suffix


class MoneyboxCreateRequest(BaseModel):
    """The pydantic moneybox create request model."""

    name: Annotated[
        str,
        Field(
            min_length=1,
            description="The name of the moneybox. Has to be unique.",
        ),
    ]
    """The name of the moneybox. Has to be unique."""

    savings_amount: Annotated[
        int,
        Field(
            serialization_alias="savings_amount",
            default=0,
            ge=0,
            description="The current savings amount of the moneybox.",
        ),
    ]
    """The current savings amount of the moneybox."""

    savings_target: Annotated[
        int | None,
        Field(
            serialization_alias="savings_target",
            default=0,
            ge=0,
            description=(
                "The current savings target. Is relevant for the automated "
                "distributed saving progress."
            ),
        ),
    ]
    """"The current savings target. Is relevant for the automated distributed saving progress."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        alias_generator=to_camel_cleaned_suffix,
        json_schema_extra={
            "examples": [
                {
                    "name": "Holiday",
                    "savingsAmount": 0,
                    "savingsTarget": 50000,
                }
            ]
        },
    )
    """The config of the model."""

    @field_validator("name")
    @classmethod
    def validate_name_for_leading_trailing_spaces(cls, value: str) -> str:
        """Check for leading and trailing whitespaces in value."""

        if value != value.strip():
            raise ValueError("Leading and trailing spaces in name are not allowed.")

        return value


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
        int,
        Field(
            serialization_alias="savings_amount",
            default=None,
            ge=0,
            description="The current savings amount of the moneybox.",
        ),
    ]
    """The current savings amount of the moneybox."""

    savings_target: Annotated[
        int | None,
        Field(
            serialization_alias="savings_target",
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
        int | None,
        Field(default=None, ge=1, description="The current priority of the moneybox."),
    ]
    """The current priority of the moneybox."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        alias_generator=to_camel_cleaned_suffix,
        json_schema_extra={
            "examples": [
                {
                    "name": "Holiday",
                    "savingsAmount": 0,
                    "savingsTarget": 50000,
                    "priority": 1,
                }
            ]
        },
    )
    """The config of the model."""

    @field_validator("name")
    @classmethod
    def validate_name_for_leading_trailing_spaces(cls, value: str | None) -> str | None:
        """Check for leading and trailing whitespaces in value."""

        if value is None:
            return value

        if value != value.strip():
            raise ValueError("Leading and trailing spaces in name are not allowed.")

        return value


class DepositTransactionRequest(BaseModel):
    """The deposit transaction request model"""

    amount: Annotated[
        int,
        Field(ge=1, description="The amount to add, value has to be at least 1."),
    ]
    """The amount to add, value has to be at least 1."""

    description: Annotated[
        str,
        StringConstraints(  # type: ignore
            strip_whitespace=True,
        ),
        Field(default="", description="The description of the withdraw transaction."),
    ]
    """The description of the withdraw transaction."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        alias_generator=to_camel_cleaned_suffix,
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
        StringConstraints(  # type: ignore
            strip_whitespace=True,
        ),
        Field(default="", description="The description of the withdraw transaction."),
    ]
    """The description of the withdraw transaction."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        alias_generator=to_camel_cleaned_suffix,
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
        Field(
            serialization_alias="to_moneybox_id",
            description="The id of the moneybox to transfer balance to.",
        ),
    ]
    """The id of the moneybox to transfer balance to."""

    amount: Annotated[
        int,
        Field(
            ge=1,
            description="The amount to transfer, value has to be at least 1.",
        ),
    ]
    """The amount to transfer, value has to be at least 1."""

    description: Annotated[
        str,
        StringConstraints(  # type: ignore
            strip_whitespace=True,
        ),
        Field(default="", description="The description of the withdraw transaction."),
    ]
    """The description of the withdraw transaction."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        alias_generator=to_camel_cleaned_suffix,
        json_schema_extra={
            "examples": [
                {
                    "amount": 50,
                    "toMoneyboxId": 3,
                    "description": "Delete Moneybox.",
                }
            ]
        },
    )
    """The config of the model."""


class PriorityRequest(BaseModel):
    """The priority request model."""

    moneybox_id: Annotated[
        int,
        Field(
            serialization_alias="moneybox_id",
            description="The id of the moneybox.",
        ),
    ]
    """The id of the moneybox."""

    priority: Annotated[
        int,
        Field(
            ge=1,
            description="The priority of the moneybox.",
        ),
    ]
    """The priority of the moneybox."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        alias_generator=to_camel_cleaned_suffix,
        json_schema_extra={
            "examples": [
                {"moneyboxId": 4, "priority": 1},
            ],
        },
    )
    """The config of the model."""


class PrioritylistRequest(BaseModel):
    """The prioritylist request model."""

    prioritylist: Annotated[
        list[PriorityRequest],
        Field(min_length=1, description="The prioritylist."),
    ]
    """The prioritylist."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        alias_generator=to_camel_cleaned_suffix,
        json_schema_extra={
            "examples": [
                {
                    "prioritylist": [
                        {
                            "moneyboxId": 1,
                            "priority": 0,
                        },
                        {
                            "moneyboxId": 2,
                            "priority": 2,
                        },
                        {
                            "moneyboxId": 4,
                            "priority": 1,
                        },
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
            serialization_alias="send_reports_via_email",
            default=None,
            description="Tells if receiving reports via report_sender is desired.",
        ),
    ]
    """Tells if receiving reports via report_sender is desired."""

    user_email_address: Annotated[
        EmailStr | None,
        Field(
            serialization_alias="user_email_address",
            default=None,
            description="Users report_sender address. Will used for receiving reports.",
        ),
    ]
    """Users report_sender address. Will used for receiving reports."""

    is_automated_saving_active: Annotated[
        bool,
        Field(
            serialization_alias="is_automated_saving_active",
            default=None,
            description="Tells if automated saving is active.",
        ),
    ]
    """Tells if automated saving is active."""

    savings_amount: Annotated[
        int,
        Field(
            serialization_alias="savings_amount",
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
            serialization_alias="overflow_moneybox_automated_savings_mode",
            default=None,
            description="The mode for automated savings.",
        ),
    ]
    """"The mode for automated savings."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        alias_generator=to_camel_cleaned_suffix,
        json_schema_extra={
            "examples": [
                {
                    "sendReportsViaEmail": True,
                    "userEmailAddress": "pythbuster@gmail.com",
                    "isAutomatedSavingActive": True,
                    "savingsAmount": 60000,
                    "overflowMoneyboxAutomatedSavingsMode": OverflowMoneyboxAutomatedSavingsModeType.COLLECT,  # noqa: ignore  # pylint: disable=line-too-long
                },
            ],
        },
    )
    """The config of the model."""

    @model_validator(mode="before")
    @classmethod
    def transform_enum_strings_to_enum_type(cls, data: dict[str, Any]) -> dict[str, Any]:
        """Lower case enum strings and concerts to enum."""

        if "overflowMoneyboxAutomatedSavingsMode" in data and isinstance(
            data["overflowMoneyboxAutomatedSavingsMode"], str
        ):
            data["overflowMoneyboxAutomatedSavingsMode"] = OverflowMoneyboxAutomatedSavingsModeType(
                data["overflowMoneyboxAutomatedSavingsMode"].lower()
            )

        return data


class ResetDataRequest(BaseModel):
    keep_app_settings: Annotated[
        bool,
        Field(
            description="Indicates if app settings shall be also deleted."
        )
    ]
    """Indicates if app settings shall be also deleted."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        alias_generator=to_camel_cleaned_suffix,
        json_schema_extra={
            "examples": [
                {
                    "keepApp_Settings": True,
                },
            ],
        },
    )
    """The config of the model."""