"""All env settings stuff are located here."""

from enum import Enum
from typing import Any

from pydantic import SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.config import ENV_FILE


class EnvironmentType(str, Enum):
    """The Environment Types"""

    TEST = "test"
    DEV = "dev"
    STAGING = "staging"
    PROD = "prod"


class Settings(BaseSettings):
    """The values loaded from .env file provided as model."""

    environment: EnvironmentType
    db_driver: str
    db_user: str
    db_password: SecretStr
    db_host: str
    db_name: str

    @model_validator(mode="before")
    @classmethod
    def environment_type_to_lower(cls, data: dict[str, Any]) -> dict[str, Any]:
        """Lower case every string whose capitalization is not important."""

        data["environment"] = data["environment"].lower()
        data["db_driver"] = data["db_driver"].lower()
        data["db_host"] = data["db_host"].lower()

        return data

    model_config = SettingsConfigDict(env_file=ENV_FILE)
