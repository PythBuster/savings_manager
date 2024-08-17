"""All custom types are located here."""

from enum import StrEnum

from pydantic import ConfigDict, SecretStr
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


class EnvironmentType(StrEnum):
    """The Environment Types to handle env loading logic."""

    LIVE = "live"
    """Live Environment (including DEV, STAGE, PROD)."""

    TEST = "test"
    """Testing Environment."""


class DBSettings(BaseSettings):
    """The database credentials."""

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

    model_config = ConfigDict(extra="forbid")
    """Model config."""


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

    CATCHED_UP_AUTOMATED_SAVING = "catched_up_automated_saving"
    """Action for catching up passed automated savings."""

    CHANGED_AUTOMATED_SAVINGS_AMOUNT = "changed_automated_savings_amount"
    """Action for changing the savings amount in app settings."""
