"""The abstract class ReportSender is located here."""

from abc import ABC
from typing import Any

from jinja2 import Environment

from src.db.db_manager import DBManager
from src.utils import tabulate_str


class ReportSender(ABC):
    """The abstract base class for all message sender."""

    def __init__(
        self,
        db_manager: DBManager,
        jinja_env: Environment,
    ):
        self.db_manager = db_manager
        self.jinja_env = jinja_env

    async def render_report(
        self,
        message_data: dict[str, Any],
        jinja_template_file: str,  # pylint: disable=unused-argument
    ) -> str:
        """Render message and sends it to receiver."""

        # sort by priority
        message_data["moneyboxes"] = sorted(
            message_data["moneyboxes"],
            key=lambda moneybox: moneybox["priority"],
        )

        total_balance = sum(int(moneybox["balance"]) for moneybox in message_data["moneyboxes"])
        total_balance_str = f"{total_balance / 100:,.2f} €".replace(".", ",")

        # cast balances to float
        for moneybox in message_data["moneyboxes"]:
            moneybox["balance"] = f"{int(moneybox['balance']) / 100:,.2f} €".replace(".", ",")

        # reduce name length and set fix with for all data
        for moneybox in message_data["moneyboxes"]:
            for key, value in moneybox.items():
                value = str(value)
                if len(value) > 23:
                    value = value[:20] + "..."

                moneybox[key] = str(value)

        # remove moneybox data, keep: name, balance
        message_data["moneyboxes"] = [
            {"moneybox_name": moneybox["name"], "balance": moneybox["balance"]}
            for moneybox in message_data["moneyboxes"]
        ]

        headers = [header.upper() for header in message_data["moneyboxes"][0].keys()]
        rows = [data.values() for data in message_data["moneyboxes"]]

        return_contents = [
            "Automated savings done. :)\nYour new moneybox balances:\n\n",
            tabulate_str(headers=headers, rows=rows),
            f"\n\nTotal Balance: {total_balance_str:<15}",
        ]

        return "".join(return_contents)

    async def send_message(self, message: str, receiver: dict[str, Any]) -> None:
        """Abstract sender method, which will raise NotImplementedError, if
        subclass does not implement it.

        Sends the message vie smtp client to receiver.

        :param message: The message to send.
        :type message: :class:`str`
        :param receiver: The receiver to send the message to.
        :type receiver: :class:`dict[str, Any]`
        """

        raise NotImplementedError("Send message not implemented")
