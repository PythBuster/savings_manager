"""All tests for the task runner are located here."""

import asyncio
from datetime import datetime
from typing import Any
from unittest.mock import patch

from src.custom_types import ActionType
from src.db.db_manager import DBManager
from src.report_sender.email_sender.sender import EmailSender
from src.task_runner import BackgroundTaskRunner


async def test_task_automated_savings_schedule(
    load_test_data: None,  # pylint: disable=unused-argument
    db_manager: DBManager,
    email_sender: EmailSender,
) -> None:
    no_action_logs = await db_manager.get_action_logs(
        action_type=ActionType.APPLIED_AUTOMATED_SAVING,
    )
    assert len(no_action_logs) == 0

    # Get path to class dynamically
    module_path = BackgroundTaskRunner.__module__
    db_manager_path = DBManager.__module__
    db_manager_path_class_name = DBManager.__qualname__

    # Event to signal when autom. savings done and write log has been called
    automated_savings_done_write_log = asyncio.Event()

    add_action_log = db_manager.add_action_log

    async def mock_write_lock_automated_savings_done(*args, **kwargs) -> None:  # type: ignore  # noqa: ignore  # pylint: disable=unused-argument, line-too-long
        async with db_manager.async_sessionmaker.begin() as session:
            kwargs["session"] = session
            await add_action_log(*args, **kwargs)

        automated_savings_done_write_log.set()  # Signal that log is written was called

    with (
        patch(
            f"{db_manager_path}.{db_manager_path_class_name}.add_action_log",
            side_effect=mock_write_lock_automated_savings_done,
        ) as mock_distribute,
        patch(f"{module_path}.datetime") as mock_datetime,
    ):
        fake_today = datetime(2022, 1, 1, 15)
        mock_datetime.today.return_value = fake_today

        task_runner = BackgroundTaskRunner(
            db_manager=db_manager,
            email_sender=email_sender,
        )

        asyncio.ensure_future(task_runner.run())
        await automated_savings_done_write_log.wait()

        mock_distribute.assert_called_once()

        action_logs = await db_manager.get_action_logs(
            action_type=ActionType.APPLIED_AUTOMATED_SAVING,
        )
        assert len(action_logs) == 1
        assert not action_logs[0]["details"].get("report_sent", False)


async def test_task_automated_savings_dont_schedule(
    load_test_data: None,  # pylint: disable=unused-argument
    db_manager: DBManager,
    email_sender: EmailSender,
) -> None:
    no_action_logs = await db_manager.get_action_logs(
        action_type=ActionType.APPLIED_AUTOMATED_SAVING,
    )
    assert len(no_action_logs) == 0

    # Get path to class dynamically
    module_path = BackgroundTaskRunner.__module__
    db_manager_path = DBManager.__module__
    db_manager_path_class_name = DBManager.__qualname__

    with (
        patch(f"{db_manager_path}.{db_manager_path_class_name}.add_action_log") as mock_distribute,
        patch(f"{module_path}.datetime") as mock_datetime,
    ):
        fake_today = datetime(2022, 1, 2, 15)
        mock_datetime.today.return_value = fake_today

        task_runner = BackgroundTaskRunner(
            db_manager=db_manager,
            email_sender=email_sender,
        )

        await task_runner.run()

        # Now we can assert that autom. savings were not applied.
        mock_distribute.assert_not_called()

        action_logs = await db_manager.get_action_logs(
            action_type=ActionType.APPLIED_AUTOMATED_SAVING,
        )
        assert len(action_logs) == 0


async def test_task_automated_savings_no_email_send(  # pylint: disable=too-many-locals
    load_test_data: None,  # pylint: disable=unused-argument
    db_manager: DBManager,
    email_sender: EmailSender,
) -> None:
    no_action_logs = await db_manager.get_action_logs(
        action_type=ActionType.APPLIED_AUTOMATED_SAVING,
    )
    assert len(no_action_logs) == 0

    # Get path to class dynamically
    task_runner_module_path = BackgroundTaskRunner.__module__
    db_manager_module_path = DBManager.__module__
    db_manager_path_class_name = DBManager.__qualname__

    # Event to signal when send_message has been called
    scheduled = asyncio.Event()

    asyncio_sleep_orig = asyncio.sleep

    async def mock_scheduled(duration: int) -> None:
        scheduled.set()
        await asyncio_sleep_orig(duration)

    orig_add_action_log = db_manager.add_action_log

    async def _add_action_log(*args, **kwargs) -> dict[str, Any]:  # type: ignore
        return await orig_add_action_log(*args, **kwargs)

    with (
        patch(f"{task_runner_module_path}.datetime") as mock_datetime_1,
        patch(f"{db_manager_module_path}.datetime") as mock_datetime_2,
        patch(
            f"{db_manager_module_path}.{db_manager_path_class_name}.add_action_log",
            site_effect=_add_action_log,
        ) as mock_distribute,
        patch(f"{task_runner_module_path}.asyncio.sleep", side_effect=mock_scheduled) as mock_sleep,
    ):
        fake_today = datetime(2022, 1, 1, 15)
        mock_datetime_1.today.return_value = fake_today
        mock_datetime_2.today.return_value = fake_today
        mock_datetime_2.now.return_value = fake_today

        task_runner = BackgroundTaskRunner(
            db_manager=db_manager,
            email_sender=email_sender,
        )

        task_runner.task_email_sending = lambda: ()

        asyncio.ensure_future(task_runner.run())
        await scheduled.wait()

        mock_sleep.assert_called_once()
        mock_distribute.assert_called_once()


async def test_task_automated_savings_no_savings_active(  # pylint: disable=too-many-locals
    load_test_data: None,  # pylint: disable=unused-argument
    db_manager: DBManager,
    email_sender: EmailSender,
) -> None:
    no_action_logs = await db_manager.get_action_logs(
        action_type=ActionType.APPLIED_AUTOMATED_SAVING,
    )
    assert len(no_action_logs) == 0

    # Get path to class dynamically
    task_runner_module_path = BackgroundTaskRunner.__module__
    db_manager_module_path = DBManager.__module__
    db_manager_path_class_name = DBManager.__qualname__

    # Event to signal when send_message has been called
    scheduled = asyncio.Event()

    asyncio_sleep_orig = asyncio.sleep

    async def mock_scheduled(duration: int) -> None:
        scheduled.set()
        await asyncio_sleep_orig(duration)

    with (
        patch(f"{task_runner_module_path}.datetime") as mock_datetime_1,
        patch(f"{db_manager_module_path}.datetime") as mock_datetime_2,
        patch(
            f"{db_manager_module_path}.{db_manager_path_class_name}.add_action_log",
        ) as mock_distribute,
        patch(f"{task_runner_module_path}.asyncio.sleep", side_effect=mock_scheduled),
    ):
        fake_today = datetime(2022, 1, 1, 15)
        mock_datetime_1.today.return_value = fake_today
        mock_datetime_2.today.return_value = fake_today
        mock_datetime_2.now.return_value = fake_today

        task_runner = BackgroundTaskRunner(
            db_manager=db_manager,
            email_sender=email_sender,
        )

        task_runner.task_email_sending = lambda: ()

        asyncio.ensure_future(task_runner.run())
        await scheduled.wait()

        mock_distribute.assert_not_called()

        action_logs = await db_manager.get_action_logs(
            action_type=ActionType.APPLIED_AUTOMATED_SAVING,
        )
        assert len(action_logs) == 0


async def test_task_email_sending__one_of_one(  # pylint: disable=too-many-locals
    load_test_data: None,  # pylint: disable=unused-argument
    db_manager: DBManager,
    email_sender: EmailSender,
) -> None:
    action_logs = await db_manager.get_action_logs(
        action_type=ActionType.APPLIED_AUTOMATED_SAVING,
    )
    assert len(action_logs) == 1
    assert not action_logs[0]["details"].get("report_sent", False)

    # Get path to class dynamically
    task_runner_module_path = BackgroundTaskRunner.__module__
    email_sender_path = EmailSender.__module__
    sender_class_name = EmailSender.__qualname__
    db_manager_module_path = DBManager.__module__
    db_manager_path_class_name = DBManager.__qualname__

    # Event to signal when db update has been called
    updated = asyncio.Event()

    update_action_log = db_manager.update_action_log

    async def mock_email_sent(*args, **kwargs) -> dict[str, Any]:  # type: ignore  # noqa: ignore  # pylint: disable=unused-argument, line-too-long
        return await update_action_log(*args, **kwargs)

    asyncio_sleep_orig = asyncio.sleep

    async def mock_scheduled(duration: int) -> None:
        updated.set()
        await asyncio_sleep_orig(duration)

    with (
        patch(
            f"{email_sender_path}.{sender_class_name}._send_message",
            return_value="Requested mail action okay, completed: id=1MPaIK-1tzl112bWE-00NrbF",
        ),
        patch(
            f"{db_manager_module_path}.{db_manager_path_class_name}.update_action_log",
            side_effect=mock_email_sent,
        ) as mock_send,
        patch(f"{task_runner_module_path}.asyncio.sleep", side_effect=mock_scheduled),
    ):
        task_runner = BackgroundTaskRunner(
            db_manager=db_manager,
            email_sender=email_sender,
        )

        task_runner.task_automated_savings = lambda: ()

        asyncio.ensure_future(task_runner.run())
        await updated.wait()

        mock_send.assert_called_once()

        action_logs = await db_manager.get_action_logs(
            action_type=ActionType.APPLIED_AUTOMATED_SAVING,
        )
        assert len(action_logs) == 1
        assert action_logs[0]["details"]["report_sent"]


async def test_task_email_sending__two_of_two(  # pylint: disable=too-many-locals
    load_test_data: None,  # pylint: disable=unused-argument
    db_manager: DBManager,
    email_sender: EmailSender,
) -> None:
    action_logs = await db_manager.get_action_logs(
        action_type=ActionType.APPLIED_AUTOMATED_SAVING,
    )
    assert len(action_logs) == 2
    assert not action_logs[0]["details"].get("report_sent", False)
    assert not action_logs[1]["details"].get("report_sent", False)

    # Get path to class dynamically
    task_runner_module_path = BackgroundTaskRunner.__module__
    email_sender_path = EmailSender.__module__
    sender_class_name = EmailSender.__qualname__
    db_manager_module_path = DBManager.__module__
    db_manager_path_class_name = DBManager.__qualname__

    # Event to signal when db update has been called
    updated = asyncio.Event()

    update_action_log = db_manager.update_action_log

    async def mock_email_sent(*args, **kwargs) -> dict[str, Any]:  # type: ignore  # noqa: ignore  # pylint: disable=unused-argument, line-too-long
        return await update_action_log(*args, **kwargs)

    asyncio_sleep_orig = asyncio.sleep

    async def mock_scheduled(duration: int) -> None:
        updated.set()
        await asyncio_sleep_orig(duration)

    with (
        patch(
            f"{email_sender_path}.{sender_class_name}._send_message",
            return_value="Requested mail action okay, completed: id=1MPaIK-1tzl112bWE-00NrbF",
        ),
        patch(
            f"{db_manager_module_path}.{db_manager_path_class_name}.update_action_log",
            side_effect=mock_email_sent,
        ) as mock_send,
        patch(f"{task_runner_module_path}.asyncio.sleep", side_effect=mock_scheduled),
    ):
        task_runner = BackgroundTaskRunner(
            db_manager=db_manager,
            email_sender=email_sender,
        )

        task_runner.task_automated_savings = lambda: ()

        asyncio.ensure_future(task_runner.run())
        await updated.wait()

        assert mock_send.call_count == 2

        action_logs = await db_manager.get_action_logs(
            action_type=ActionType.APPLIED_AUTOMATED_SAVING,
        )
        assert len(action_logs) == 2
        assert action_logs[0]["details"]["report_sent"]
        assert action_logs[1]["details"]["report_sent"]


async def test_task_email_sending__two_of_three(  # pylint: disable=too-many-locals
    load_test_data: None,  # pylint: disable=unused-argument
    db_manager: DBManager,
    email_sender: EmailSender,
) -> None:
    action_logs = await db_manager.get_action_logs(
        action_type=ActionType.APPLIED_AUTOMATED_SAVING,
    )
    assert len(action_logs) == 3
    assert not action_logs[0]["details"].get("report_sent", False)
    assert action_logs[1]["details"]["report_sent"]
    assert not action_logs[2]["details"].get("report_sent", False)

    # Get path to class dynamically
    task_runner_module_path = BackgroundTaskRunner.__module__
    email_sender_path = EmailSender.__module__
    sender_class_name = EmailSender.__qualname__
    db_manager_module_path = DBManager.__module__
    db_manager_path_class_name = DBManager.__qualname__

    # Event to signal when db update has been called
    updated = asyncio.Event()

    update_action_log = db_manager.update_action_log

    async def mock_email_sent(  # type: ignore
        *args, **kwargs
    ) -> dict[str, Any]:  # noqa: ignore  # pylint: disable=unused-argument, line-too-long
        return await update_action_log(*args, **kwargs)

    asyncio_sleep_orig = asyncio.sleep

    async def mock_scheduled(duration: int) -> None:
        updated.set()
        await asyncio_sleep_orig(duration)

    with (
        patch(
            f"{email_sender_path}.{sender_class_name}._send_message",
            return_value="Requested mail action okay, completed: id=1MPaIK-1tzl112bWE-00NrbF",
        ),
        patch(
            f"{db_manager_module_path}.{db_manager_path_class_name}.update_action_log",
            side_effect=mock_email_sent,
        ) as mock_send,
        patch(f"{task_runner_module_path}.asyncio.sleep", side_effect=mock_scheduled),
    ):
        task_runner = BackgroundTaskRunner(
            db_manager=db_manager,
            email_sender=email_sender,
        )

        task_runner.task_automated_savings = lambda: ()

        asyncio.ensure_future(task_runner.run())
        await updated.wait()

        assert mock_send.call_count == 2

        action_logs = await db_manager.get_action_logs(
            action_type=ActionType.APPLIED_AUTOMATED_SAVING,
        )
        assert len(action_logs) == 3
        assert action_logs[0]["details"]["report_sent"]
        assert action_logs[1]["details"]["report_sent"]
        assert action_logs[2]["details"]["report_sent"]
