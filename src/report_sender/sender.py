"""The abstract class ReportSender is located here."""

from abc import ABC
from typing import Any

from jinja2 import Environment

from src.db.db_manager import DBManager
from src.utils import get_app_data, tabulate_str


class ReportSender(ABC):
    """The abstract base class for all message sender."""

    def __init__(
        self,
        db_manager: DBManager,
        jinja_env: Environment,
    ):
        self.db_manager = db_manager
        self.jinja_env = jinja_env

        app_data = get_app_data()
        self.versioned_app_name = f"{app_data['name']} v{app_data['version']}"
