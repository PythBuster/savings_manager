"""All custom types are located here."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, SecretStr


class EndpointRouteType(StrEnum):
    """The endpoint names."""

    APP_ROOT = "api"  # /app
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
