"""All custom decorators are located here."""

import asyncio
from functools import wraps
from typing import Callable


# decorator class
class every:
    """Task function decorator for functions used in BackgroundTaskRunner"""

    @staticmethod
    def hour(interval: int) -> Callable:
        def decorator(func: Callable) -> Callable:
            func_name = func.__name__.upper()  # Capture the name of the decorated function

            @wraps(func)
            async def wrapper(obj, *args, **kwargs):  # type: ignore
                await obj.print_task(
                    task_name=func_name,
                    message="Task started ...",
                )

                while True:
                    await func(obj, *args, **kwargs)
                    await asyncio.sleep(interval * 3600)  # wait given interval in hours

            return wrapper

        return decorator

    @staticmethod
    def minute(interval: int) -> Callable:
        def decorator(func: Callable) -> Callable:
            func_name = func.__name__.upper()  # Capture the name of the decorated function

            @wraps(func)
            async def wrapper(obj, *args, **kwargs):  # type: ignore
                await obj.print_task(
                    task_name=func_name,
                    message="Task started ...",
                )

                while True:
                    await func(obj, *args, **kwargs)
                    await asyncio.sleep(interval * 60)  # wait given interval in minutes

            return wrapper

        return decorator

    @staticmethod
    def second(interval: int) -> Callable:
        def decorator(func: Callable) -> Callable:
            func_name = func.__name__.upper()  # Capture the name of the decorated function

            @wraps(func)
            async def wrapper(obj, *args, **kwargs):  # type: ignore
                await obj.print_task(
                    task_name=func_name,
                    message="Start task ...",
                )

                while True:
                    await func(obj, *args, **kwargs)
                    await asyncio.sleep(interval)  # wait given interval in seconds

            return wrapper

        return decorator
