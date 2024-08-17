import asyncio
import inspect
from asyncio import current_task

from datetime import datetime


class BackgroundTaskRunner:
    """The BackgroundTaskRunner class is responsible for running a background task.

    All tasks can be implemented here and need to start with the prefix name 'task_'.

    The run() method will auto collect all task methods and enqueues the methods as background
    :class:`asyncio.Task` instances.

    Each task_ method has to implement its own endless loop and sleep (->self.sleep_time)
     (if endless task is wanted) and its own date trigger.
    """

    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.sleep_time = 10  # each hour
        self.background_tasks = set()

    async def run(self):
        # Collect all async methods of the class that start with 'task_'
        task_methods = [
            getattr(self, method_name) for method_name in dir(self)
            if method_name.startswith('task_') and
               inspect.iscoroutinefunction(getattr(self, method_name))
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
        current_method_name = inspect.currentframe().f_code.co_name.upper()

        await self.print_task(
            task_name=current_method_name,
            message="Start task ..."
        )
        while True:
            today_month_day = datetime.today().day

            if today_month_day == 1:
                # TODO: check mal ob für diesen monat zum 1. bereits verteilt

                result = await self.db_manager.automated_savings()

                if result:
                    await self.print_task(
                        task_name=current_method_name,
                        message="Automated savings run."
                    )
                else:
                    await self.print_task(
                        task_name=current_method_name,
                        message="Nothing to do. Automated savings is deactivated."
                    )

                # TODO:
                # - get logs and check (-> from db_manager),
                #       if distribution for this month is done: do nothing,
                #       if not, do job
                # - implement savings distribution logic (-> in db manager)
                # - call app saving amount distribution (-> call db_manager function)

            await asyncio.sleep(self.sleep_time)

        await self.print_task(
            task_name=current_method_name,
            message="Task finished."
        )

    async def print_task(self, task_name: str, message: str) -> None:
        print(f"{datetime.now()} - {task_name.strip()}: {message.strip()}", flush=True)