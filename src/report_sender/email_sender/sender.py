"""The Email Sender stuff is located here."""

from collections.abc import Iterable
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path
from typing import Any

from aiosmtplib import SMTP
from jinja2 import Environment, FileSystemLoader, select_autoescape

from src.app_logger import app_logger
from src.custom_types import AppEnvVariables
from src.db.db_manager import DBManager
from src.report_sender.consants import SENDER_DIR_PATH
from src.report_sender.sender import ReportSender
from src.routes.exceptions import MissingSMTPSettingsError
from src.utils import get_app_data, tabulate_str


class EmailSender(ReportSender):
    """The EmailSender class is responsible for sending emails."""

    def __init__(
        self,
        db_manager: DBManager,
        smtp_settings: AppEnvVariables,
    ):
        """Initialize the EmailSender instance.

        :param db_manager: The fastAPI state db_manager instance.
        :type db_manager: :class:`DBManager`
        :param smtp_settings: The smtp settings instance.
        :type smtp_settings: :class:`AppEnvVariables`
        """

        self.smtp_settings: AppEnvVariables = smtp_settings

        sender_template_path: Path = SENDER_DIR_PATH / "email_sender" / "templates"

        jinja_env: Environment = Environment(
            loader=FileSystemLoader(sender_template_path),
            autoescape=select_autoescape(["html", "xml"]),
        )
        super().__init__(
            db_manager=db_manager,
            jinja_env=jinja_env,
        )

    async def send_testemail(self, to: str) -> bool:
        """The test email sender function to test the SMTP outgoing data settings.

        :param to: The email address to send the test email to.
        :type to: :class:`str`
        :return: True, if send was successfully, otherwise returns False.
        :rtype: :class:`bool`
        """

        try:
            today_dt_str: str = datetime.now(tz=timezone.utc).isoformat(
                sep=" ",
                timespec="seconds",
            )
            plain_message: str = (
                "This is a test email.\nYour SMTP outgoing data are correct, congratulations! :)"
            )

            receiver: dict[str, str] = {
                "to": to,
                "subj": f"Test Email from {self.versioned_app_name} ({today_dt_str})",
            }

            await self._send_message(plain_message=plain_message, receiver=receiver)
            return True
        except Exception as ex:  # pylint: disable=broad-exception-caught
            app_logger.exception(ex)
            return False

    async def send_email_automated_savings_done_successfully(self, to: str) -> None:
        """The send email function which will be called after automated savings
        is done successfully.

        :param to: The email recipient.
        :type to: :class:`str`
        """

        today_dt_str: str = datetime.now(tz=timezone.utc).isoformat(
            sep=" ",
            timespec="seconds",
        )
        message_data: dict[str, list[dict[str, Any]]] = {
            "moneyboxes": await self.db_manager.get_moneyboxes()
        }

        plain_message, html_message = await self._render_automated_savings_report(
            message_data=message_data,
        )
        receiver: dict[str, str] = {
            "to": to,
            "subj": f"Automated savings done ({today_dt_str})",
        }

        await self._send_message(
            plain_message=plain_message,
            html_message=html_message,
            receiver=receiver,
        )

    async def _render_automated_savings_report(  # pylint: disable=too-many-locals
        self,
        message_data: dict[str, Any],
    ) -> tuple[str, str]:
        """Helper function to prepare sending data for automated savings report.

        :param message_data: The message data
        :type message_data: :class:`dict[str, Any]`

        :return: The rendered message as plaint text and htl test as tuple.
        :rtype: :class:`tuple[str, str]`
        """

        jinja_template_file: str = "automated_savings_done.html"

        # sort by priority
        message_data["moneyboxes"] = sorted(
            message_data["moneyboxes"],
            key=lambda moneybox: moneybox["priority"],
        )

        total_balance: int = sum(
            int(moneybox["balance"]) for moneybox in message_data["moneyboxes"]
        )
        total_balance_str: str = f"{total_balance / 100:,.2f} €"

        # cast balances to float
        for moneybox in message_data["moneyboxes"]:
            balance_str: str = f"{int(moneybox['balance']) / 100:,.2f} €"
            moneybox["balance"] = balance_str

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

        headers: list[str] = [header.upper() for header in message_data["moneyboxes"][0].keys()]
        rows: list[Iterable] = [data.values() for data in message_data["moneyboxes"]]

        header_string: str = (
            f"{self.versioned_app_name}: automated savings done. :)\n"
            "Your new moneybox balances:\n\n"
        )
        plain_message_parts: list[str] = [
            header_string,
            tabulate_str(headers=headers, rows=rows),
            f"\n\nTotal Balance: {total_balance_str:<15}",
        ]
        plain_message: str = "".join(plain_message_parts)

        header_string_1: str = "automated savings done. :)"
        header_string_2: str = "Your new moneybox balances:"

        app_data_info: dict[str, Any] = get_app_data()
        html_message: str = self.jinja_env.get_template(jinja_template_file).render(
            app_name=app_data_info["name"],
            app_version=app_data_info["version"],
            header_string_1=header_string_1,
            header_string_2=header_string_2,
            moneyboxes_table_header=[header.lower() for header in headers],
            moneyboxes_table_data=message_data["moneyboxes"],
            total_balance=total_balance_str,
        )
        return plain_message, html_message

    async def _send_message(  # pylint: disable=arguments-differ
        self,
        receiver: dict[str, Any],
        plain_message: str,
        html_message: str | None = None,
    ) -> None:
        """Sends a multipart email via smtp client to receiver, if
         html_message is given, if not, keep text/plain only.

        :param receiver: The receiver to send the message to.
        :type receiver: :class:`dict[str, Any]`
        :param plain_message: The plain text message to send.
        :type plain_message: :class:`str`
        :param html_message: The plain text message to send, defaults to None.
        :type html_message: :class:`str`|:class:`None`
        """

        _sender: str | None = self.smtp_settings.smtp_user_name

        if _sender is None:
            raise MissingSMTPSettingsError()

        to: str = receiver["to"]
        subj: str = receiver["subj"]

        email_message: EmailMessage = EmailMessage()
        email_message["From"] = _sender
        email_message["To"] = to
        email_message["Subject"] = subj
        email_message.set_content(plain_message)

        if html_message is not None:
            # Add the HTML content as an alternative
            email_message.add_alternative(html_message, subtype="html")

        async with SMTP(
            hostname=self.smtp_settings.smtp_server,
            port=self.smtp_settings.smtp_port,
            username=self.smtp_settings.smtp_user_name,
            password=self.smtp_settings.smtp_password.get_secret_value(),  # type: ignore
            start_tls=self.smtp_settings.smtp_method == "starttls",
            use_tls=self.smtp_settings.smtp_method == "tls",
        ) as client:
            await client.send_message(email_message, sender=_sender, recipients=to)
