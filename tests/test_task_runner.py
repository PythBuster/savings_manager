"""All tests for the task runner are located here."""

import asyncio
from datetime import datetime
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
    no_automated_savings_logs = await db_manager.get_automated_savings_logs(
        action_type=ActionType.APPLIED_AUTOMATED_SAVING,
    )
    assert len(no_automated_savings_logs) == 0

    # Get path to class dynamically
    module_path = BackgroundTaskRunner.__module__
    email_sender_path = EmailSender.__module__
    sender_class_name = EmailSender.__qualname__

    # Event to signal when send_message has been called
    send_message_called = asyncio.Event()

    async def mock_send_message(*args, **kwargs) -> None:  # type: ignore  # noqa: ignore  # pylint: disable=unused-argument, line-too-long
        send_message_called.set()  # Signal that send_message was called

    with (
        patch(
            f"{email_sender_path}.{sender_class_name}._send_message", side_effect=mock_send_message
        ) as mock_send,
        patch(f"{module_path}.datetime") as mock_datetime,
    ):
        fake_today = datetime(2022, 1, 1, 15)
        mock_datetime.today.return_value = fake_today

        task_runner = BackgroundTaskRunner(
            db_manager=db_manager,
            email_sender=email_sender,
        )

        asyncio.ensure_future(task_runner.run())
        await send_message_called.wait()

        mock_send.assert_called_once()

        automated_savings_logs = await db_manager.get_automated_savings_logs(
            action_type=ActionType.APPLIED_AUTOMATED_SAVING,
        )
        assert len(automated_savings_logs) == 1


async def test_task_automated_savings_dont_schedule(
    load_test_data: None,  # pylint: disable=unused-argument
    db_manager: DBManager,
    email_sender: EmailSender,
) -> None:
    no_automated_savings_logs = await db_manager.get_automated_savings_logs(
        action_type=ActionType.APPLIED_AUTOMATED_SAVING,
    )
    assert len(no_automated_savings_logs) == 0

    # Get path to class dynamically
    module_path = BackgroundTaskRunner.__module__
    email_sender_path = EmailSender.__module__
    sender_class_name = EmailSender.__qualname__

    with (
        patch(f"{email_sender_path}.{sender_class_name}._send_message") as mock_send,
        patch(f"{module_path}.datetime") as mock_datetime,
    ):
        fake_today = datetime(2022, 1, 2, 15)
        mock_datetime.today.return_value = fake_today

        task_runner = BackgroundTaskRunner(
            db_manager=db_manager,
            email_sender=email_sender,
        )

        await task_runner.run()

        # Now we can assert that send_message was called
        mock_send.assert_not_called()

        automated_savings_logs = await db_manager.get_automated_savings_logs(
            action_type=ActionType.APPLIED_AUTOMATED_SAVING,
        )
        assert len(automated_savings_logs) == 0


async def test_task_automated_savings_no_email_send(  # pylint: disable=too-many-locals
    load_test_data: None,  # pylint: disable=unused-argument
    db_manager: DBManager,
    email_sender: EmailSender,
) -> None:
    no_automated_savings_logs = await db_manager.get_automated_savings_logs(
        action_type=ActionType.APPLIED_AUTOMATED_SAVING,
    )
    assert len(no_automated_savings_logs) == 0

    # Get path to class dynamically
    task_runner_module_path = BackgroundTaskRunner.__module__
    db_manager_module_path = DBManager.__module__
    email_sender_path = EmailSender.__module__
    sender_class_name = EmailSender.__qualname__

    # Event to signal when send_message has been called
    scheduled = asyncio.Event()

    asyncio_sleep_orig = asyncio.sleep

    async def mock_scheduled(duration: int) -> None:
        scheduled.set()
        await asyncio_sleep_orig(duration)

    with (
        patch(f"{task_runner_module_path}.datetime") as mock_datetime_1,
        patch(f"{db_manager_module_path}.datetime") as mock_datetime_2,
        patch(f"{email_sender_path}.{sender_class_name}._send_message") as mock_send,
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

        asyncio.ensure_future(task_runner.run())
        await scheduled.wait()

        mock_sleep.assert_called_once()
        mock_send.assert_not_called()

        automated_savings_logs = await db_manager.get_automated_savings_logs(
            action_type=ActionType.APPLIED_AUTOMATED_SAVING,
        )
        assert len(automated_savings_logs) == 1


async def test_task_automated_savings_no_savings_active(  # pylint: disable=too-many-locals
    load_test_data: None,  # pylint: disable=unused-argument
    db_manager: DBManager,
    email_sender: EmailSender,
) -> None:
    no_automated_savings_logs = await db_manager.get_automated_savings_logs(
        action_type=ActionType.APPLIED_AUTOMATED_SAVING,
    )
    assert len(no_automated_savings_logs) == 0

    # Get path to class dynamically
    task_runner_module_path = BackgroundTaskRunner.__module__
    db_manager_module_path = DBManager.__module__
    email_sender_path = EmailSender.__module__
    sender_class_name = EmailSender.__qualname__

    # Event to signal when send_message has been called
    scheduled = asyncio.Event()

    asyncio_sleep_orig = asyncio.sleep

    async def mock_scheduled(duration: int) -> None:
        scheduled.set()
        await asyncio_sleep_orig(duration)

    with (
        patch(f"{task_runner_module_path}.datetime") as mock_datetime_1,
        patch(f"{db_manager_module_path}.datetime") as mock_datetime_2,
        patch(f"{email_sender_path}.{sender_class_name}._send_message") as mock_send,
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

        asyncio.ensure_future(task_runner.run())
        await scheduled.wait()

        mock_send.assert_not_called()

        automated_savings_logs = await db_manager.get_automated_savings_logs(
            action_type=ActionType.APPLIED_AUTOMATED_SAVING,
        )
        assert len(automated_savings_logs) == 0
