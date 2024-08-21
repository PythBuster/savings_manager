"""All custom types are located here."""

from enum import StrEnum
from typing import Self

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

    smtp_server: str
    """The address of the smtp server."""

    smtp_method: str
    """The smtp method, supported: STARTTLS and TLS."""

    smtp_port: int
    """The port name of the smtp server."""

    smtp_user_name: str
    """The user name of the smtp server."""

    smtp_password: str
    """The user password."""

    model_config = ConfigDict(extra="forbid")
    """Model config."""

    @model_validator(mode="after")
    def lowercase_smtp_method(self) -> Self:
        """Lowercase the smtp method."""

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
