"""All custom types are located here."""

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, SecretStr, model_validator


class EnvironmentTypes(StrEnum):
    """The Environment Types to handle env loading logic."""

    DEV = "dev"


class DBSettings(BaseModel):
    """The database credentials."""

    db_user: str = ""
    db_password: SecretStr = SecretStr("")
    db_host: str = ""
    db_port: int | None = None
    db_name: str = ""
    db_driver: str
    in_memory: bool = False

    @model_validator(mode="before")
    @classmethod
    def in_memory_none_to_false(cls, data: dict[str, Any]) -> dict[str, Any]:
        """Validator, that converts in_memory=None in_memory=False.

        :param data: The model data.
        :type data: dict[str, Any]
        :return: The updated model data.
        :rtype: dict[str, Any]
        """

        if data["in_memory"] is None:
            data["in_memory"] = False

        return data

    model_config = ConfigDict(extra="forbid")