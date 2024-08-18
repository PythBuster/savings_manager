"""The background task runner logic."""

import asyncio
import inspect
from datetime import datetime

from src.custom_types import ActionType
from src.db.db_manager import DBManager


class BackgroundTaskRunner:
    """The BackgroundTaskRunner class is responsible for running a background task.

    All tasks can be implemented here and need to start with the prefix name 'task_'.

    The run() method will auto collect all task methods and enqueues the methods as background
    :class:`asyncio.Task` instances.

    Each task_ method has to implement its own endless loop and sleep (->self.sleep_time)
     (if endless task is wanted) and its own date trigger.
    """

    def __init__(self, db_manager: DBManager) -> None:
        self.db_manager = db_manager
        self.sleep_time = 60 * 60  # each hour
        self.background_tasks: set[asyncio.Task] = set()

    async def run(self) -> None:
        """Collect all async methods of the class that start with 'task_'"""

        task_methods = [
            getattr(self, method_name)
            for method_name in dir(self)
            if method_name.startswith("task_")
            and inspect.iscoroutinefunction(getattr(self, method_name))
        ]

        for task_method in task_methods:
            task = asyncio.create_task(task_method())
            self.background_tasks.add(task)
            task.add_done_callback(self.background_tasks.discard)

    async def task_automated_savings(self) -> None:
        """This is the endless task for automated savings.
        Sleeps (self.sleep_time), checks if distribution day is reached and does the task.

        - do task on each 1st of month
        """

        # Get the name of the current method
        current_method_name = inspect.currentframe().f_code.co_name.upper()  # type: ignore

        await self.print_task(task_name=current_method_name, message="Start task ...")

        while True:
            today = datetime.today()
            already_done = False

            if today.day == 1 and today.hour >= 12:
                automated_action_logs = await self.db_manager.get_automated_savings_logs(
                    action_type=ActionType.APPLIED_AUTOMATED_SAVING,
                )

                if automated_action_logs:
                    automated_action_logs_dates = [
                        automated_action_log["action_at"].date()
                        for automated_action_log in automated_action_logs
                    ]

                    if today.date() in automated_action_logs_dates:
                        already_done = True

                if not already_done:
                    result = await self.db_manager.automated_savings()

                    if result:
                        await self.print_task(
                            task_name=current_method_name, message="Automated savings run."
                        )
                    else:
                        await self.print_task(
                            task_name=current_method_name,
                            message="Nothing to do. Automated savings is deactivated.",
                        )

            await asyncio.sleep(self.sleep_time)

        await self.print_task(  # type: ignore
            task_name=current_method_name, message="Task finished."
        )

    async def print_task(self, task_name: str, message: str) -> None:
        """The background task runner is responsible for printing out the task information."""

        print(f"{datetime.now()} - {task_name.strip()}: {message.strip()}", flush=True)
