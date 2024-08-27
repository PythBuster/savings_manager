"""The Email Sender stuff is located here."""

from datetime import datetime, timezone
from email.message import EmailMessage
from typing import Any

from aiosmtplib import SMTP
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pyexpat.errors import messages

from src.app_logger import logger
from src.custom_types import AppEnvVariables
from src.db.db_manager import DBManager
from src.report_sender.consants import SENDER_DIR_PATH
from src.report_sender.sender import ReportSender


class EmailSender(ReportSender):
    """The EmailSender class is responsible for sending emails."""

    def __init__(
        self,
        db_manager: DBManager,
        smtp_settings: AppEnvVariables,
    ):
        self.smtp_settings = smtp_settings

        sender_template_path = SENDER_DIR_PATH / "email_sender" / "templates"

        jinja_env = Environment(
            loader=FileSystemLoader(sender_template_path),
            autoescape=select_autoescape(["html", "xml"]),
        )
        super().__init__(
            db_manager=db_manager,
            jinja_env=jinja_env,
        )

    async def send_testmail(self, to: str) -> bool:
        """The test mail sender function.

        :param to: The email address to send the test mail to.
        :type to: :class:`str`
        :return: True, if send was successfully, otherwise returns False.
        :rtype: :class:`bool`"""

        try:
            today_dt_str = datetime.now(tz=timezone.utc).isoformat(sep=" ", timespec="seconds")
            message = """This is a testmail.\nYour SMTP outgoing data are correct, congratulations! :)"""

            receiver = {
                "to": to,
                "subj": f"Test Mail from {self.versioned_app_name} ({today_dt_str})",
            }

            await self.send_message(message=message, receiver=receiver)
            return True
        except Exception as ex:
            logger.exception(ex)
            return False

    async def send_email_automated_savings_done_successfully(self, to: str) -> None:
        """The send mail function which will be called after automated savings
        is done successfully.

        :param to: The email recipient.
        :type to: :class:`str`
        """

        template_file = "automated_savings_done.html"
        today_dt_str = datetime.now(tz=timezone.utc).isoformat(sep=" ", timespec="seconds")
        message_data = {"moneyboxes": await self.db_manager.get_moneyboxes()}

        message = await self.render_report(
            message_data=message_data,
            jinja_template_file=template_file,
        )
        receiver = {
            "to": to,
            "subj": f"Automated savings done ({today_dt_str})",
        }

        await self.send_message(
            message=message,
            receiver=receiver,
        )

    async def send_message(self, message: str, receiver: dict[str, Any]) -> None:
        to = receiver["to"]
        _sender = self.smtp_settings.smtp_user_name
        subj = receiver["subj"]

        email_message = EmailMessage()
        email_message["From"] = _sender
        email_message["To"] = to
        email_message["Subject"] = subj
        email_message.set_content(message)

        async with SMTP(
            hostname=self.smtp_settings.smtp_server,
            port=self.smtp_settings.smtp_port,
            username=self.smtp_settings.smtp_user_name,
            password=self.smtp_settings.smtp_password.get_secret_value(),
            start_tls=self.smtp_settings.smtp_method == "starttls",
            use_tls=self.smtp_settings.smtp_method == "tls",
        ) as client:
            await client.send_message(email_message, sender=_sender, recipients=to)
