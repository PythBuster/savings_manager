"""All custom types are located here."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, SecretStr


class EndpointRouteType(StrEnum):
    """The endpoint names."""

    APP_ROOT = "api"  # /app
    MONEYBOX = "moneybox"  # /moneybox
    MONEYBOXES = "moneyboxes"  # /moneyboxes


class EnvironmentType(StrEnum):
    """The Environment Types to handle env loading logic."""

    DEV = "dev"
    TEST = "test"


class DBSettings(BaseModel):
    """The database credentials."""

    db_user: str = ""
    db_password: SecretStr = SecretStr("")
    db_host: str = ""
    db_port: int | None = None
    db_name: str = ""
    db_driver: str

    model_config = ConfigDict(extra="forbid")
