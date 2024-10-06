"""All response models are located here."""

from datetime import datetime
from typing import Annotated, Any, Self

from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    StringConstraints,
    computed_field,
    field_validator,
    model_validator,
)
from pydantic_extra_types.semantic_version import SemanticVersion

from src.custom_types import (
    OverflowMoneyboxAutomatedSavingsModeType,
    TransactionTrigger,
    TransactionType,
)
from src.utils import to_camel_cleaned_suffix


class HTTPErrorResponse(BaseModel):
    """The http error response model"""

    message: Annotated[
        str,
        StringConstraints(  # type: ignore
            min_length=1,
            strip_whitespace=True,
        ),
        Field(description="The error message."),  # additional field metadata
    ]
    """The error message."""

    details: Annotated[dict[str, Any] | None, Field(default=None, description="The error details.")]
    """The error details."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        json_schema_extra={
            "examples": [
                {
                    "message": "No database connection.",
                    "details": {
                        "message": "Connect call failed ('127.0.0.1', 5432)",
                    },
                },
            ],
        },
    )
    """The config of the model."""


class MoneyboxResponse(BaseModel):
    """The pydantic moneybox response model"""

    id_: Annotated[int, Field(description="The id of the moneybox.")]
    """The id of the moneybox."""

    name: Annotated[
        str,
        Field(
            alias="name",
            min_length=1,
            description="The name of the moneybox. Has to be unique.",
        ),
    ]
    """The name of the moneybox. Has to be unique."""

    balance: Annotated[int, Field(ge=0, description="The balance of the moneybox in CENTS.")]
    """The balance of the moneybox in CENTS."""

    savings_amount: Annotated[
        int,
        Field(
            validation_alias="savings_amount",
            ge=0,
            description="The current savings amount of the moneybox.",
        ),
    ]
    """The current savings amount of the moneybox."""

    savings_target: Annotated[
        int | None,
        Field(
            validation_alias="savings_target",
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
        Field(
            ge=0,
            description=(
                "The current priority of the moneybox. There is only one moneybox with "
                "a priority of Null (will be the marker for the overflow moneybox."
            ),
        ),
    ]
    """The current priority of the moneybox. There is only one moneybox with
    a priority of Null (will be the marker for the overflow moneybox)."""

    created_at: Annotated[
        AwareDatetime,
        Field(
            validation_alias="created_at",
            description="The creation date of the moneybox.",
        ),
    ]
    """The creation date of the moneybox."""

    modified_at: Annotated[
        AwareDatetime | None,
        Field(
            validation_alias="modified_at",
            description="The modification date of the moneybox.",
        ),
    ]
    """The modification date of the moneybox."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        alias_generator=to_camel_cleaned_suffix,
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "name": "Holiday",
                    "balance": 0,
                    "savingsAmount": 0,
                    "savingsTarget": 50000,
                    "priority": 1,
                    "createdAt": "2024-08-11 13:57:17.941840 +00:00",
                    "modifiedAt": "2024-08-11 15:03:17.312860 +00:00",
                }
            ]
        },
    )
    """The config of the model."""

    @model_validator(mode="before")
    @classmethod
    def transform_string_datetimes_to_datetimes(cls, data: dict[Any, Any]) -> dict[Any, Any]:
        """Try to transform 'modified_at' and 'created_at' datetime strings
        to datetimes if possible and necessary."""

        if data["modified_at"] is not None:
            if isinstance(data["modified_at"], str):
                try:
                    data["modified_at"] = datetime.fromisoformat(data["modified_at"])
                except (TypeError, ValueError) as ex:
                    raise ValueError(
                        "'modified_at' must be of type datetime or datetime-string."
                    ) from ex
            elif not isinstance(data["modified_at"], datetime):
                raise ValueError("'modified_at' must be of type datetime or datetime-string.")

        if isinstance(data["created_at"], str):
            try:
                data["created_at"] = datetime.fromisoformat(data["created_at"])
            except (TypeError, ValueError) as ex:
                raise ValueError(
                    "'created_at' must be of type datetime or datetime-string."
                ) from ex

        elif not isinstance(data["created_at"], datetime):
            raise ValueError("'created_at' must be of type datetime or datetime-string.")

        return data

    @model_validator(mode="after")
    def validate_created_at_and_modified_at_date_order(self) -> Self:
        """Check if 'modified_at' date is after 'created_at'."""

        # create_at datetime has to be smaller than modified_at datetime!
        #   created_at == modified_at is not allowed
        if self.modified_at is not None and self.created_at >= self.modified_at:
            msg = "Error: 'created_at' comes after 'modified_at'."
            raise ValueError(msg)

        return self

    @field_validator("name")
    @classmethod
    def validate_name_for_leading_trailing_spaces(cls, value: str) -> str:
        """Check for leading and trailing whitespaces in value."""

        if value != value.strip():
            raise ValueError("Leading and trailing spaces in name are not allowed.")

        return value


class MoneyboxesResponse(BaseModel):
    """The moneyboxes response model."""

    moneyboxes: Annotated[
        list[MoneyboxResponse],
        Field(min_length=1, description="The list of moneyboxes."),
    ]
    """The list of moneyboxes."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        json_schema_extra={
            "examples": [
                {
                    "total": 2,
                    "moneyboxes": [
                        {
                            "id": 1,
                            "name": "672c0145-c910-4ce8-8202-d6ce9ba405a4",
                            "balance": 0,
                            "savingsAmount": 0,
                            "savingsTarget": None,
                            "priority": 0,
                            "createdAt": "2024-08-13 02:50:41.837275 +00:00",
                            "modifiedAt": None,
                        },
                        {
                            "id": 2,
                            "name": "Holiday",
                            "balance": 1050,
                            "savingsAmount": 50,
                            "savingsTarget": 50000,
                            "priority": 1,
                            "createdAt": "2024-08-16 02:50:41.837275 +00:00",
                            "modifiedAt": "2024-08-17 04:41:45.126672 +00:00",
                        },
                    ],
                }
            ]
        },
    )
    """The config of the model."""

    @computed_field  # type: ignore
    @property
    def total(self) -> int:
        """The count of moneyboxes."""

        return len(self.moneyboxes)


class TransactionLogResponse(BaseModel):
    """The transaction log response model."""

    id_: Annotated[
        int,
        Field(
            description="The ID of the transaction.",
        ),
    ]
    """The ID of the transaction."""

    counterparty_moneybox_name: Annotated[
        str | None,
        Field(
            validation_alias="counterparty_moneybox_name",
            min_length=1,
            description="The name of the counterparty moneybox.",
        ),
    ]
    """The name of the counterparty moneybox."""

    description: Annotated[
        str,
        StringConstraints(  # type: ignore
            strip_whitespace=True,
        ),
        Field(description="The description of the transaction action."),
    ]
    """The description of the transaction action."""

    transaction_type: Annotated[
        TransactionType,
        Field(
            validation_alias="transaction_type",
            description=(
                "The type of the transaction. Possible values: " "direct or distribution."
            ),
        ),
    ]
    """The type of the transaction. Possible values: direct or distribution."""

    transaction_trigger: Annotated[
        TransactionTrigger,
        Field(
            validation_alias="transaction_trigger",
            description=(
                "The transaction trigger type, possible values: manually, automatically. "
                "Says, if balance was deposit or withdrawn manually or automatically."
            ),
        ),
    ]
    """"The transaction type, possible values: manually, automatically.
    Says, if balance was deposit or withdrawn manually or automatically."""

    amount: Annotated[
        int,
        Field(
            description=(
                "The current amount of the transaction. "
                "Can be negative, negative = withdraw, positive = deposit."
            ),
        ),
    ]
    """The current amount of the transaction.
    Can be negative, negative = withdraw, positive = deposit."""

    balance: Annotated[
        int,
        Field(
            ge=0,
            description="The new balance of the moneybox after the transaction.",
        ),
    ]
    """The new balance of the moneybox after the transaction."""

    counterparty_moneybox_id: Annotated[
        int | None,
        Field(
            validation_alias="counterparty_moneybox_id",
            description=(
                "Transaction is a transfer between moneybox_id and "
                "counterparty_moneybox_id, if set."
            ),
        ),
    ]
    """Transaction is a transfer between moneybox_id and
    counterparty_moneybox_id, if set."""

    moneybox_id: Annotated[
        int,
        Field(validation_alias="moneybox_id", description="The foreign key to moneybox."),
    ]
    """The foreign key to moneybox."""

    created_at: Annotated[
        AwareDatetime,
        Field(
            validation_alias="created_at",
            description="The creation date of the transaction log.",
        ),
    ]
    """The creation date of the transaction log."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        alias_generator=to_camel_cleaned_suffix,
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "moneyboxId": 1,
                    "description": "Transfer Money.",
                    "transactionType": TransactionType.DIRECT,
                    "transactionTrigger": TransactionTrigger.MANUALLY,
                    "amount": 50,
                    "balance": 50,
                    "counterpartyMoneyboxId": 3,
                    "counterpartyMoneyboxName": "Moneybox 3",
                    "createdAt": "2024-08-11 13:57:17.941840 +00:00",
                }
            ]
        },
    )
    """The config of the model."""

    @field_validator("amount")
    @classmethod
    def validate_amount_not_zero(cls, value: int) -> int:
        """Check if amount is != 0. Transactions with amount of 0 doesn't make sense."""

        if value == 0:
            raise ValueError("Amount has to be positive or negative for the transaction.")

        return value

    @field_validator("created_at", mode="before")
    @classmethod
    def transform_create_at_string_datetime_to_datetime(
        cls,
        value: Any,
    ) -> Any:
        """Try to transform 'created_at' string datetime to datetime,
        if possible and necessary."""

        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value)
            except (TypeError, ValueError) as ex:
                raise ValueError(
                    "'created_at' must be of type datetime or datetime-string."
                ) from ex
        elif not isinstance(value, datetime):
            raise ValueError("'created_at' must be of type datetime or datetime-string.")

        return value

    @model_validator(mode="after")
    def validate_transaction_type_and_transaction_trigger_accepted_combinations(
        self,
    ) -> Self:
        """Check for combinations:
        - TransactionType.DIRECT + TransactionTrigger.AUTOMATICALLY
        - TransactionType.DISTRIBUTION + TransactionTrigger.DIRECT

        and raise exception if combination occurs."""

        if (
            self.transaction_type is not TransactionType.DIRECT
            and self.transaction_trigger is not TransactionTrigger.AUTOMATICALLY
        ):
            raise ValueError(
                "Invalid transaction type and transaction trigger combination!"
                "An automated-direct action is not allowed for now."
            )

        if (
            self.transaction_type is not TransactionType.DISTRIBUTION
            and self.transaction_trigger is not TransactionTrigger.MANUALLY
        ):
            raise ValueError(
                "Invalid transaction type and transaction trigger combination!"
                "A manual-distributed action is not allowed for now."
            )

        return self

    @model_validator(mode="after")
    def validate_counterparty_moneybox_name_and_counterparty_moneybox_id_both_set(
        self,
    ) -> Self:
        """If counterparty_moneybox_name is set, counterparty_moneybox_id need to be set too."""

        if (self.counterparty_moneybox_name is None) != (self.counterparty_moneybox_id is None):
            raise ValueError("Invalid combination: If one is None, the other must also be None.")

        return self

    @model_validator(mode="after")
    def validate_moneybox_id_not_same_as_counterparty_moneybox_id(self) -> Self:
        """moneybox_id must not be the same as counterparty_moneybox_id"""

        if self.moneybox_id == self.counterparty_moneybox_id:
            raise ValueError("moneybox_id must not be the same as counterparty_moneybox_id.")

        return self

    @model_validator(mode="after")
    def validate_balance_against_amount(self) -> Self:
        """Check balance
        - if amount is positive, balance must be at least greater than or equal to amount.

        raise exception if not."""

        if self.amount > 0 and self.balance < self.amount:
            raise ValueError(
                "New balance of the moneybox must be at least greater than or equal to amount."
            )

        return self

    @model_validator(mode="before")
    @classmethod
    def transform_enum_strings_to_enum_values(cls, data: dict[Any, Any]) -> dict[Any, Any]:
        """Lowercase and cast strings to transaction type and transaction trigger."""

        if "transaction_type" in data and isinstance(data["transaction_type"], str):
            data["transaction_type"] = TransactionType(data["transaction_type"].lower())

        if "transaction_trigger" in data and isinstance(data["transaction_trigger"], str):
            data["transaction_trigger"] = TransactionTrigger(data["transaction_trigger"].lower())

        return data

    @field_validator("counterparty_moneybox_name")
    @classmethod
    def validate_name_for_leading_trailing_spaces(cls, value: str | None) -> str | None:
        """Check for leading and trailing whitespaces in value."""

        if value is None:
            return value

        if value != value.strip():
            raise ValueError(
                "Leading and trailing spaces in counterparty_moneybox_name are not allowed."
            )

        return value


class TransactionLogsResponse(BaseModel):
    """The transaction logs response model."""

    transaction_logs: Annotated[
        list[TransactionLogResponse],
        Field(
            validation_alias="transaction_logs",
            description="The list of transaction logs.",
        ),
    ]
    """The list of transaction logs."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        alias_generator=to_camel_cleaned_suffix,
        json_schema_extra={
            "examples": [
                {
                    "total": 1,
                    "transactionLogs": [
                        TransactionLogResponse.model_config["json_schema_extra"]["examples"][0],
                    ],
                }
            ]
        },
    )
    """The config of the model."""

    @computed_field  # type: ignore
    @property
    def total(self) -> int:
        """The count of transaction logs."""

        return len(self.transaction_logs)


class PriorityResponse(BaseModel):
    """The priority response model."""

    moneybox_id: Annotated[
        int,
        Field(
            validation_alias="moneybox_id",
            description="The id of the moneybox.",
        ),
    ]
    """The id of the moneybox."""

    name: Annotated[str, Field(min_length=1, description="The name of the moneybox.")]
    """The name of the moneybox."""

    priority: Annotated[int, Field(ge=1, description="The priority of the moneybox.")]
    """The priority of the moneybox."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        alias_generator=to_camel_cleaned_suffix,
        json_schema_extra={
            "examples": [
                {
                    "moneyboxId": 4,
                    "name": "Holiday",
                    "priority": 1,
                },
            ],
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


class PrioritylistResponse(BaseModel):
    """The priority list response model."""

    prioritylist: Annotated[
        list[PriorityResponse],
        Field(min_length=1, description="The priority list."),
    ]
    """The priority list."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        alias_generator=to_camel_cleaned_suffix,
        json_schema_extra={
            "examples": [
                {
                    "total": 3,
                    "prioritylist": [
                        {
                            "moneyboxId": 1,
                            "name": "672c0145-c910-4ce8-8202-d6ce9ba405a4",
                            "priority": 0,
                        },
                        {"moneyboxId": 2, "name": "Reserves", "priority": 2},
                        {
                            "moneyboxId": 4,
                            "name": "Holiday",
                            "priority": 1,
                        },
                    ],
                },
            ],
        },
    )
    """The config of the model."""

    @computed_field  # type: ignore
    @property
    def total(self) -> int:
        """The len of prioritylist."""

        return len(self.prioritylist)


class AppInfoResponse(BaseModel):
    """The application info response model."""

    app_name: Annotated[
        str,
        Field(
            min_length=1,
            description="The name of the application.",
        ),
    ]
    """The name of the application."""

    app_version: Annotated[
        SemanticVersion,
        Field(description="The version of the application."),
    ]
    """The version of the application."""

    app_description: Annotated[
        str,
        Field(
            min_length=1,
            description="The description of the application.",
        ),
    ]
    """The description of the application."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        alias_generator=to_camel_cleaned_suffix,
        json_schema_extra={
            "examples": [
                {
                    "appName": "Savings Manager",
                    "appVersion": "2.13.0",
                    "appDescription": "The Savings Manager ....",
                },
            ],
        },
    )
    """The config of the model."""


class AppSettingsResponse(BaseModel):
    """The app settings response model."""

    id_: Annotated[
        int,
        Field(
            description="The ID of the app settings.",
        ),
    ]
    """The ID of the app settings."""

    created_at: Annotated[
        AwareDatetime,
        Field(
            validation_alias="created_at",
            description="The creation date of the moneybox.",
        ),
    ]
    """The creation date of the app settings."""

    modified_at: Annotated[
        AwareDatetime | None,
        Field(
            validation_alias="modified_at",
            description="The modification date of the moneybox.",
        ),
    ]
    """The modification date of the app settings."""

    send_reports_via_email: Annotated[
        bool,
        Field(
            validation_alias="send_reports_via_email",
            description="Tells if receiving reports via report_sender is desired.",
        ),
    ]
    """Tells if receiving reports via report_sender is desired."""

    user_email_address: Annotated[
        EmailStr | None,
        Field(
            validation_alias="user_email_address",
            description=("Users report_sender address. Will used for receiving reports."),
        ),
    ]
    """Users report_sender address. Will used for receiving reports."""

    is_automated_saving_active: Annotated[
        bool,
        Field(
            validation_alias="is_automated_saving_active",
            description="Tells if automated saving is active.",
        ),
    ]
    """Tells if automated saving is active."""

    savings_amount: Annotated[
        int,
        Field(
            validation_alias="savings_amount",
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
            validation_alias="overflow_moneybox_automated_savings_mode",
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
                    "id": 1,
                    "createdAt": "2024-08-11 13:57:17.941840 +00:00",
                    "modifiedAt": "2024-08-11 15:03:17.312860 +00:00",
                    "sendReportsViaEmail": False,
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
    def validate_create_at_and_modified_datetimes(cls, data: dict[str, Any]) -> dict[str, Any]:
        """Check if 'modified_at' and 'created_at' is type datetime."""

        if data["modified_at"] is not None:
            if isinstance(data["modified_at"], str):
                try:
                    data["modified_at"] = datetime.fromisoformat(data["modified_at"])
                except (TypeError, ValueError) as ex:
                    raise ValueError(
                        "'created_at' must be of type datetime or datetime-string."
                    ) from ex
            elif not isinstance(data["modified_at"], datetime):
                raise ValueError("'modified_at' must be of type datetime or datetime-string.")

        if isinstance(data["created_at"], str):
            try:
                data["created_at"] = datetime.fromisoformat(data["created_at"])
            except (TypeError, ValueError) as ex:
                raise ValueError(
                    "'created_at' must be of type datetime or datetime-string."
                ) from ex
        elif not isinstance(data["created_at"], datetime):
            raise ValueError("'created_at' must be of type datetime or datetime-string.")

        return data

    @model_validator(mode="after")
    def validate_user_email_address_if_set(self) -> Self:
        """Check if email exists, when send_reports_via_email is set to true,
        if not, raise ValueError."""

        if self.send_reports_via_email and self.user_email_address is None:
            raise ValueError("Can't activate receiving emails, user email address is not set!")

        return self


class LoginUserResponse(BaseModel):
    """The login user response model."""

    id_: Annotated[
        int,
        Field(
            description="The id of the user.",
        ),
    ]
    """The id of the moneybox."""

    created_at: Annotated[
        AwareDatetime,
        Field(
            validation_alias="created_at",
            description="The creation date of the user.",
        ),
    ]
    """The creation date of the user."""

    modified_at: Annotated[
        AwareDatetime | None,
        Field(
            validation_alias="modified_at",
            description="The modification date of the user.",
        ),
    ]
    """The modification date of the user."""

    user_name: Annotated[
        str,
        Field(
            validation_alias="user_name",
            description="The user's name.",
        ),
    ]
    """The user's name."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        alias_generator=to_camel_cleaned_suffix,
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "userName": "JohnDoe@mail.com",
                    "createdAt": "2024-08-11 13:57:17.941840Z",
                    "modifiedAt": "2024-08-11 15:03:17.312860Z",
                },
            ],
        },
    )
    """The config of the model."""

    # TODO: user_login will be renamend in orm, remove model_validator if done.
    @model_validator(mode="before")
    @classmethod
    def transform_user_login_to_user_name(cls, data: dict[str, Any]) -> dict[str, Any]:
        """Validator to rename user_login key from database to user_name key for the response.

        Will be removed, when ORM column is renamend.

        :param data: The orm data.
        :type data: :class:`dict[str, Any]`
        :return: The new data for pydantic model.
        :rtype: :class:`dict[str, Any]`
        """

        if "user_login" in data:
            data["user_name"] = data["user_login"]
            del data["user_login"]

        return data
