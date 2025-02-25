"""The background task runner logic."""

import asyncio
import inspect
from datetime import date, datetime
from http.client import responses
from typing import Any, Callable

from mypy.dmypy_util import receive

from src.custom_types import ActionType
from src.db.db_manager import DBManager
from src.db.models import AppSettings
from src.decorators import every
from src.report_sender.email_sender.sender import EmailSender


class BackgroundTaskRunner:
    """The BackgroundTaskRunner class is responsible for running a background task.

    All tasks can be implemented here and need to start with the prefix name 'task_'.

    The run() method will auto collect all task methods and enqueues the methods as background
    :class:`asyncio.Task` instances.

    Each task_ method has to implement its own endless loop and sleep (->self.sleep_time)
     (if endless task is wanted) and its own date trigger.
    """

    def __init__(self, db_manager: DBManager, email_sender: EmailSender) -> None:
        """Initialize the BackgroundTaskRunner instance.

        :param db_manager: The DBManager instance.
        :type db_manager: :class:`DBManager`
        :param email_sender: The EmailSender instance.
        :type email_sender: :class:`EmailSender`
        """

        self.db_manager: DBManager = db_manager
        self.email_sender: EmailSender = email_sender
        self.sleep_time: int = 60 * 60  # each hour
        self.background_tasks: set[asyncio.Task] = set()

    async def run(self) -> None:
        """Collect all async methods of the class that start with 'task_'"""

        task_methods: list[Callable] = [
            getattr(self, method_name)
            for method_name in dir(self)
            if method_name.startswith("task_")
            and inspect.iscoroutinefunction(getattr(self, method_name))
        ]

        for task_method in task_methods:
            task: asyncio.Task = asyncio.create_task(task_method())
            self.background_tasks.add(task)
            task.add_done_callback(self.background_tasks.discard)

    @every.hour(1)
    async def task_email_sending(self) -> None:
        """Check if there are any emails to send (queued in db table
        'email_send_queue').

        If email was sent successfully, related db record will be removed
        from db table.
        """

        current_method_name: str = inspect.currentframe().f_code.co_name.upper()  # type: ignore

        log_types_for_email_report: set[ActionType] = {
            ActionType.APPLIED_AUTOMATED_SAVING,
        }
        """Report emails for these types of logs."""

        send_email_callbacks = {
            ActionType.APPLIED_AUTOMATED_SAVING: self.email_sender.send_email_automated_savings_done_successfully,
        }
        """Callback function to handle sending emails for different types of logs."""

        app_settings: AppSettings = await self.db_manager._get_app_settings()

        if app_settings.send_reports_via_email:
            receiver_email = app_settings.user_email_address

            for log_type in log_types_for_email_report:
                _send_email = send_email_callbacks[log_type]
                action_logs: list[dict[str, Any]] = await self.db_manager.get_action_logs(
                    action_type=log_type,
                )
                action_logs = [
                    log
                    for log in action_logs
                    if not log["details"].get("report_sent", False)
                ]

                for action_log in reversed(action_logs):
                    response = await _send_email(
                        to=receiver_email,
                        subject=f"Automated savings done ({action_log['created_at']:%Y-%m-%d %H:%M})"
                    )

                    if response:
                        await self.db_manager.update_action_log(
                            action_log_id=action_log["id"],
                            data={"details": action_log["details"] | {"report_sent": True}},
                        )

                if action_logs:
                    await self.print_task(
                        task_name=current_method_name,
                        message=f"{len(action_logs)} reports sent successfully via email."
                    )
                else:
                    await self.print_task(
                        task_name=current_method_name,
                        message="Nothing to do."
                    )
        else:
            await self.print_task(
                task_name=current_method_name,
                message="No emails sent, 'send_reports_via_email' in settings is disabled."
            )

    @every.hour(1)
    async def task_automated_savings(self) -> None:
        """This is the task for automated savings.
        Checks if distribution day is reached and does the task.

        - do task on each 1st of month
        """

        current_method_name: str = inspect.currentframe().f_code.co_name.upper()  # type: ignore
        today_dt: datetime = datetime.today()
        already_done: bool = False

        if today_dt.day == 1 and today_dt.hour >= 12:
            automated_action_logs: list[dict[str, Any]] = (
                await self.db_manager.get_action_logs(
                    action_type=ActionType.APPLIED_AUTOMATED_SAVING,
                )
            )

            if automated_action_logs:
                automated_action_logs_dates: list[date] = [
                    automated_action_log["action_at"].date()
                    for automated_action_log in automated_action_logs
                ]

                if today_dt.date() in automated_action_logs_dates:
                    already_done = True

            if not already_done:
                result: bool = await self.db_manager.automated_savings()

                if result:
                    await self.print_task(
                        task_name=current_method_name, message="Automated savings run."
                    )
                else:
                    await self.print_task(
                        task_name=current_method_name,
                        message="Nothing to do. Automated savings is deactivated.",
                    )

    async def print_task(self, task_name: str, message: str) -> None:
        """The background task runner is responsible for printing out the task information."""

        print(f"{datetime.now()} - {task_name.strip()}: {message.strip()}", flush=True)

    async def stop_tasks(self) -> None:
        """Stops running background tasks."""

        for task in self.background_tasks:
            task.cancel()

        try:
            await asyncio.wait_for(
                asyncio.gather(*self.background_tasks, return_exceptions=True),
                timeout=2,
            )
        except asyncio.TimeoutError:
            print("Timeout reached while waiting for tasks to finish. Force stopping.")
