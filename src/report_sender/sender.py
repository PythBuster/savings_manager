"""The abstract class ReportSender is located here."""

from abc import ABC
from typing import Any

from jinja2 import Environment

from src.db.db_manager import DBManager
from src.utils import get_app_data


class ReportSender(ABC):  # pylint: disable=too-few-public-methods
    """The abstract base class for all message sender."""

    def __init__(
        self,
        db_manager: DBManager,
        jinja_env: Environment,
    ):
        """Initialize the ReportSender instance.

        :param db_manager: The database manager instance.
        :type db_manager: :class:`DBManager`
        :param jinja_env: The jinja env instance.
        :type jinja_env: :class:`Jinja2`
        """

        self.db_manager: DBManager = db_manager
        self.jinja_env: Environment = jinja_env

        app_data: dict[str, Any] = get_app_data()
        self.versioned_app_name: str = f"{app_data['name']} v{app_data['version']}"
