"""All custom types are located here."""

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, SecretStr, model_validator


class EndpointRouteType(StrEnum):
    """The endpoint names."""

    APP_ROOT = "api"  # /api
    """Root endpoint path name."""

    MONEYBOX = "moneybox"  # /moneybox
    """Moneybox endpoint path name."""

    MONEYBOXES = "moneyboxes"  # /moneyboxes
    """Moneyboxes endpoint path name."""


class EnvironmentType(StrEnum):
    """The Environment Types to handle env loading logic."""

    DEV = "dev"
    """Development Environment."""

    TEST = "test"
    """Testing Environment."""


class DBSettings(BaseModel):
    """The database credentials."""

    db_driver: str
    """Database driver."""

    db_file: str
    """Database file path."""

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
