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

    db_user: str = ""
    """Database user name."""

    db_password: SecretStr = SecretStr("")
    """Database password."""

    db_host: str = ""
    """Database host."""

    db_port: int | None = None
    """Database port."""

    db_name: str = ""
    """Database name."""

    db_driver: str
    """Database driver."""

    model_config = ConfigDict(extra="forbid")
    """Model config."""

    @model_validator(mode="before")
    @classmethod
    def convert_port(cls, data: dict[str, Any]) -> dict[str, Any]:
        """Conert db_port as string to int.

        :param data: The model data.
        :type data: :class:`dict[str, Any]
        :return: The updated model data:
        :rtype: :class:`dict[str, Any]
        """

        if "db_port" in data and data["db_port"] is not None:
            data["db_port"] = int(data["db_port"])

        return data


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
