"""All custom types are located here."""

from enum import StrEnum
from typing import Self, Any

from pydantic import ConfigDict, SecretStr, model_validator
from pydantic_settings import BaseSettings


class EndpointRouteType(StrEnum):
    """The endpoint names."""

    APP_ROOT = "api"  # /api
    """Root endpoint path name."""

    MONEYBOX = "moneybox"  # /moneybox
    """Moneybox endpoint path name."""

    MONEYBOXES = "moneyboxes"  # /moneyboxes
    """Moneyboxes endpoint path name."""

    PRIORITYLIST = "prioritylist"  # /prioritylist
    """Prioritylist endpoint path name."""

    APP_SETTINGS = "settings"  # /settings
    """Settings endpoint path name."""


class AppEnvVariables(BaseSettings):
    """The app env vars, with all settings/credentials for:
    - database
    - smtp
    """

    db_driver: str
    """Database driver."""

    db_name: str
    """Database name."""

    db_host: str
    """Database host."""

    db_port: int
    """Database port."""

    db_user: str
    """Database user."""

    db_password: SecretStr
    """Database password."""

    smtp_server: str|None = None
    """The address of the smtp server."""

    smtp_method: str|None = None
    """The smtp method, supported: STARTTLS and TLS."""

    smtp_port: int|None = None
    """The port name of the smtp server."""

    smtp_user_name: str|None = None
    """The user name of the smtp server."""

    smtp_password: SecretStr|None = None
    """The user password."""

    model_config = ConfigDict(extra="forbid")
    """Model config."""

    @property
    def smtp_ready(self):
        return not any(
            (
                self.smtp_server is None,
                self.smtp_method is None,
                self.smtp_port is None,
                self.smtp_user_name is None,
                self.smtp_password is None,
            )
        )

    @model_validator(mode="before")
    @classmethod
    def smtp_data_empty_to_none(cls, data: dict[str, Any]) -> dict[str, Any]:
        if data["smtp_server"] == "":
            data["smtp_server"] = None

        if data["smtp_method"] == "":
            data["smtp_method"] = None

        if data["smtp_port"] == "":
            data["smtp_port"] = None

        if data["smtp_user_name"] == "":
            data["smtp_user_name"] = None

        if data["smtp_password"] == "":
            data["smtp_password"] = None

        return data

    @model_validator(mode="after")
    def lowercase_smtp_method(self) -> Self:
        """Lowercase the smtp method."""

        if self.smtp_method is not None:
            self.smtp_method = self.smtp_method.lower()

        return self


class TransactionTrigger(StrEnum):
    """The transaction trigger."""

    MANUALLY = "manually"
    """Transaction was triggered manually."""

    AUTOMATICALLY = "automatically"
    """Transaction was triggered automatically."""


class TransactionType(StrEnum):
    """The transaction type."""

    DIRECT = "direct"
    """Transaction was made in this moneybox directly."""

    DISTRIBUTION = "distribution"
    """Transaction caused by distribution strategy."""


class ActionType(StrEnum):
    """The action type especially used in context of the automated savings and
    automated savings logs."""

    ACTIVATED_AUTOMATED_SAVING = "activated_automated_saving"
    """Action for activating the automated savings in app settings."""

    DEACTIVATED_AUTOMATED_SAVING = "deactivated_automated_saving"
    """Action for deactivating the automated savings in app settings."""

    APPLIED_AUTOMATED_SAVING = "applied_automated_saving"
    """Action for executing the automated savings."""

    CHANGED_AUTOMATED_SAVINGS_AMOUNT = "changed_automated_savings_amount"
    """Action for changing the savings amount in app settings."""


class OverflowMoneyboxAutomatedSavingsModeType(StrEnum):
    """The transaction type."""

    COLLECT = "collect"
    """Just collect amounts in overflow moneybox.."""

    ADD_TO_AUTOMATED_SAVINGS_AMOUNT = "add_to_automated_savings_amount"
    """Push up the initial automated savings amount and add all balance to
    distributing savings amount."""

    FILL_UP_LIMITED_MONEYBOXES = "fill_up_limited_moneyboxes"
    """After the automated savings process, the entire balance from the overflow
    moneybox should be distributed to the moneyboxes with upper limits, in the order of
    the priority list. Try to fill them up."""
