import asyncio
import inspect
from datetime import datetime


class BackgroundTaskRunner:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.sleep_time = 5
        self.background_tasks = set()

    async def start_tasks(self):
        # Collect all async methods of the class that start with 'task_'
        task_methods = [
            getattr(self, method_name) for method_name in dir(self)
            if method_name.startswith('task_') and
               inspect.iscoroutinefunction(getattr(self, method_name))
        ]

        for task_method in task_methods:
            task = asyncio.create_task(task_method())
            task.add_done_callback(self.background_tasks.discard)

            self.background_tasks.add(
                task
            )

    async def task_automated_savings(self) -> None:
        """This is the endless task for automated savings.
        Sleeps (self.sleep_time), checks if distribution day is reached and does the task.

        - do task on each 1st of month
        """

        print("Start task for automated savings...")

        while True:
            todays_month_day = datetime.today().day

            if todays_month_day == 1:
                moneyboxes = await self.db_manager.get_moneyboxes()
                print("Moneyboxes:", len(moneyboxes), flush=True)
            else:
                print("Nothing to do", flush=True)

            await asyncio.sleep(self.sleep_time)

        print("Finished task for automated savings...")
