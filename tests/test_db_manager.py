# pylint: disable=too-many-lines

"""All db_manager tests are located here."""
import io
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError

from alembic.config import CommandLine
from src.custom_types import (
    ActionType,
    AppEnvVariables,
    OverflowMoneyboxAutomatedSavingsModeType,
    TransactionTrigger,
    TransactionType,
    UserRoleType,
)
from src.data_classes.requests import (
    DepositTransactionRequest,
    TransferTransactionRequest,
    WithdrawTransactionRequest,
)
from src.db.db_manager import DBManager
from src.db.exceptions import (
    AppSettingsNotFoundError,
    AutomatedSavingsError,
    BalanceResultIsNegativeError,
    CreateInstanceError,
    DeleteInstanceError,
    HasBalanceError,
    InconsistentDatabaseError,
    MissingDependencyError,
    MoneyboxNameNotFoundError,
    MoneyboxNotFoundError,
    NonPositiveAmountError,
    OverflowMoneyboxNotFoundError,
    OverflowMoneyboxUpdatedError,
    ProcessCommunicationError,
    TransferEqualMoneyboxError,
    UpdateInstanceError,
    UserNameAlreadyExistError,
    UserNotFoundError,
)
from src.db.models import AppSettings, Moneybox
from src.utils import equal_dict
from tests.utils.db_manager import get_moneybox_id_by_name


@pytest.mark.order(1)
async def test_if_test_db_is_used(db_manager: DBManager) -> None:
    assert (
        db_manager.db_connection_string
        == "postgresql+asyncpg://test_postgres:test_postgres@localhost:8765/savings_manager"
    )


@pytest.mark.dependency
async def test_create_db_manager_with_engine_args(
    app_env_variables: AppEnvVariables,
) -> None:
    db_manager = DBManager(db_settings=app_env_variables, engine_args={"echo": True})
    assert db_manager is not None


async def test_overflow_moneybox_add_amount_success(
    load_test_data: None,  # pylint:disable=unused-argument
    db_manager: DBManager,
) -> None:
    app_settings: AppSettings = (
        await db_manager._get_app_settings()  # noqa: ignore  # pylint: disable=protected-access
    )
    overflow_moneybox: Moneybox = (
        await db_manager._get_overflow_moneybox()  # noqa: ignore  # pylint: disable=protected-access
    )

    async with db_manager.async_sessionmaker.begin() as session:
        update_overflow_moneybox = await db_manager._overflow_moneybox_add_amount(  # noqa: ignore  # pylint: disable=protected-access
            app_settings=app_settings.asdict(),
            overflow_moneybox=overflow_moneybox.asdict(),
            amount=5,
            session=session,
        )

    assert update_overflow_moneybox["balance"] == 5

    async with db_manager.async_sessionmaker.begin() as session:
        update_overflow_moneybox = await db_manager._overflow_moneybox_add_amount(  # noqa: ignore  # pylint: disable=protected-access
            app_settings=app_settings.asdict(),
            overflow_moneybox=update_overflow_moneybox,
            amount=-1,  # should not have any effect, 'falltrough' inserted moneybox
            session=session,
        )
    assert update_overflow_moneybox["balance"] == 5


async def test_overflow_moneybox_add_amount_fail(
    db_manager: DBManager,
) -> None:
    app_settings: AppSettings = (
        await db_manager._get_app_settings()  # noqa: ignore  # pylint: disable=protected-access
    )
    overflow_moneybox: Moneybox = (
        await db_manager._get_overflow_moneybox()  # noqa: ignore  # pylint: disable=protected-access
    )

    overflow_moneybox_data: dict[str, Any] = overflow_moneybox.asdict()
    overflow_moneybox_data["id"] = 1234

    async with db_manager.async_sessionmaker.begin() as session:
        with pytest.raises(AutomatedSavingsError):
            await db_manager._overflow_moneybox_add_amount(  # noqa: ignore  # pylint: disable=protected-access
                app_settings=app_settings.asdict(),
                overflow_moneybox=overflow_moneybox_data,  # with non-existing id
                amount=5,
                session=session,
            )


async def test_overflow_moneybox_sub_amount_success(
    db_manager: DBManager,
) -> None:
    app_settings: AppSettings = (
        await db_manager._get_app_settings()  # noqa: ignore  # pylint: disable=protected-access
    )
    overflow_moneybox: Moneybox = (
        await db_manager._get_overflow_moneybox()  # noqa: ignore  # pylint: disable=protected-access
    )

    async with db_manager.async_sessionmaker.begin() as session:
        update_overflow_moneybox = await db_manager._overflow_moneybox_sub_amount(  # noqa: ignore  # pylint: disable=protected-access
            app_settings=app_settings.asdict(),
            overflow_moneybox=overflow_moneybox.asdict(),
            amount=3,
            session=session,
        )

    assert update_overflow_moneybox["balance"] == 2

    async with db_manager.async_sessionmaker.begin() as session:
        update_overflow_moneybox = await db_manager._overflow_moneybox_sub_amount(  # noqa: ignore  # pylint: disable=protected-access
            app_settings=app_settings.asdict(),
            overflow_moneybox=update_overflow_moneybox,
            amount=-1,  # should not have any effect, 'falltrough' inserted moneybox
            session=session,
        )
    assert update_overflow_moneybox["balance"] == 2


async def test_overflow_moneybox_sub_amount_fail(
    db_manager: DBManager,
) -> None:
    app_settings: AppSettings = (
        await db_manager._get_app_settings()  # noqa: ignore  # pylint: disable=protected-access
    )
    overflow_moneybox: Moneybox = (
        await db_manager._get_overflow_moneybox()  # noqa: ignore  # pylint: disable=protected-access
    )

    overflow_moneybox_data: dict[str, Any] = overflow_moneybox.asdict()
    overflow_moneybox_data["id"] = 1234

    async with db_manager.async_sessionmaker.begin() as session:
        with pytest.raises(AutomatedSavingsError):
            await db_manager._overflow_moneybox_sub_amount(  # noqa: ignore  # pylint: disable=protected-access
                app_settings=app_settings.asdict(),
                overflow_moneybox=overflow_moneybox_data,  # with non-existing id
                amount=5,
                session=session,
            )


async def test_get_overflow_moneybox(
    load_test_data: None,  # pylint:disable=unused-argument
    db_manager: DBManager,
) -> None:
    with pytest.raises(OverflowMoneyboxNotFoundError):
        await db_manager._get_overflow_moneybox()  # pylint:disable=protected-access


async def test_add_overflow_moneybox(
    db_manager: DBManager,
) -> None:
    with pytest.raises(CreateInstanceError):
        await db_manager._add_overflow_moneybox(  # pylint:disable=protected-access
            moneybox_data={
                "unknown_key": "what else",
            }
        )


@pytest.mark.dependency(name="test_add_moneybox_success")
async def test_add_moneybox_success(
    load_test_data: None,  # pylint:disable=unused-argument
    db_manager: DBManager,
) -> None:
    # test different combinations of initial values
    moneybox_data = [
        {
            "name": "Test Box 1",
            "balance": 0,
            "savings_amount": 0,
            "savings_target": None,
        },
        {
            "name": "Test Box 2",
            "balance": 350,
            "savings_amount": 0,
            "savings_target": None,
        },
        {
            "name": "Test Box 3",
            "balance": 0,
            "savings_amount": 0,
            "savings_target": None,
        },
        {
            "name": "Test Box 4",
            "balance": 0,
            "savings_amount": 0,
            "savings_target": None,
        },
    ]

    for priority, data in enumerate(moneybox_data):
        result_moneybox_data = await db_manager.add_moneybox(moneybox_data=data)

        assert isinstance(result_moneybox_data["created_at"], datetime)
        assert result_moneybox_data["modified_at"] is None

        del result_moneybox_data["created_at"]
        del result_moneybox_data["modified_at"]

        expected_moneybox_data = {
            "priority": priority + 1,
            "id": result_moneybox_data["id"],
            "balance": 0,
        } | data
        assert result_moneybox_data == expected_moneybox_data


@pytest.mark.dependency(depends=["test_add_moneybox_success"])
async def test_add_moneybox_fail(
    db_manager: DBManager,
) -> None:
    # test different combinations of initial values
    moneybox_data: list[dict[str, Any]] = [
        {
            "name": "Test Box 1",  # name already exists
            "balance": 0,
            "savings_amount": 0,
            "savings_target": None,
        },
        {
            # missing name
            "balance": 350,
            "savings_amount": 0,
            "savings_target": None,
        },
    ]

    for data in moneybox_data:
        with pytest.raises(CreateInstanceError):
            await db_manager.add_moneybox(moneybox_data=data)


@pytest.mark.dependency(depends=["test_add_moneybox_fail"])
async def test_get_prioritylist(
    db_manager: DBManager,
) -> None:
    priorities = await db_manager.get_prioritylist()
    priorities = sorted(priorities, key=lambda x: x["priority"], reverse=False)

    # sort and check if result is sorted by priority
    expected_priorities = [
        {"priority": 4, "name": "Test Box 4"},
        {"priority": 3, "name": "Test Box 3"},
        {"priority": 2, "name": "Test Box 2"},
        {"priority": 1, "name": "Test Box 1"},
    ]
    expected_priorities.sort(key=lambda x: x["priority"])  # type: ignore

    assert equal_dict(
        dict_1=expected_priorities[0],
        dict_2=priorities[0],
        exclude_keys=["moneybox_id"],
    )
    assert equal_dict(
        dict_1=expected_priorities[1],
        dict_2=priorities[1],
        exclude_keys=["moneybox_id"],
    )
    assert equal_dict(
        dict_1=expected_priorities[2],
        dict_2=priorities[2],
        exclude_keys=["moneybox_id"],
    )
    assert equal_dict(
        dict_1=expected_priorities[3],
        dict_2=priorities[3],
        exclude_keys=["moneybox_id"],
    )


@pytest.mark.dependency(depends=["test_get_prioritylist"])
async def test_update_priorities(db_manager: DBManager) -> None:
    first_moneybox_id = (
        await get_moneybox_id_by_name(  # noqa: typing  # pylint:disable=protected-access
            async_session=db_manager.async_sessionmaker,
            name="Test Box 1",
        )
    )
    second_moneybox_id = (
        await get_moneybox_id_by_name(  # noqa: typing  # pylint:disable=protected-access
            async_session=db_manager.async_sessionmaker, name="Test Box 2"
        )
    )
    third_moneybox_id = (
        await get_moneybox_id_by_name(  # noqa: typing  # pylint:disable=protected-access
            async_session=db_manager.async_sessionmaker, name="Test Box 3"
        )
    )
    fourth_moneybox_id = (
        await get_moneybox_id_by_name(  # noqa: typing  # pylint:disable=protected-access
            async_session=db_manager.async_sessionmaker, name="Test Box 4"
        )
    )

    new_priorities_1 = [
        {"moneybox_id": first_moneybox_id, "priority": 4},
        {"moneybox_id": second_moneybox_id, "priority": 3},
        {"moneybox_id": third_moneybox_id, "priority": 2},
        {"moneybox_id": fourth_moneybox_id, "priority": 1},
    ]

    result = await db_manager.update_prioritylist(priorities=new_priorities_1)

    # sort and check if result is sorted by priority
    expected_priorities = [
        {"moneybox_id": first_moneybox_id, "priority": 4, "name": "Test Box 1"},
        {"moneybox_id": second_moneybox_id, "priority": 3, "name": "Test Box 2"},
        {"moneybox_id": third_moneybox_id, "priority": 2, "name": "Test Box 3"},
        {"moneybox_id": fourth_moneybox_id, "priority": 1, "name": "Test Box 4"},
    ]
    expected_priorities.sort(key=lambda x: x["priority"])  # type: ignore

    for i, expected_priority in enumerate(expected_priorities):
        assert equal_dict(
            dict_1=expected_priority,
            dict_2=result[i],
        )

    # exceptions tests

    # fail unknown id
    new_priorities_2 = [
        {"moneybox_id": first_moneybox_id, "priority": 1},
        {"moneybox_id": second_moneybox_id, "priority": 2},
        {"moneybox_id": third_moneybox_id, "priority": 3},
        {"moneybox_id": fourth_moneybox_id, "priority": 4},
        {"moneybox_id": -42, "priority": 5},
    ]

    with pytest.raises(UpdateInstanceError) as ex_info:
        await db_manager.update_prioritylist(priorities=new_priorities_2)

    assert ex_info.value.message == "Tried to update non existing moneyboxes."

    # duplicate ids
    new_priorities_2 = [
        {"moneybox_id": first_moneybox_id, "priority": 1},
        {"moneybox_id": second_moneybox_id, "priority": 2},
        {"moneybox_id": third_moneybox_id, "priority": 3},
        {"moneybox_id": fourth_moneybox_id, "priority": 4},
        {"moneybox_id": first_moneybox_id, "priority": 5},  # duplicate
    ]

    with pytest.raises(UpdateInstanceError) as ex_info:
        await db_manager.update_prioritylist(priorities=new_priorities_2)

    assert ex_info.value.message == "Update priority list has duplicate moneybox ids."

    # fail updating overflow moneybox
    overflow_moneybox = (
        await db_manager._get_overflow_moneybox()  # noqa: ignore  # pylint: disable=protected-access
    )
    new_priorities_3 = [
        {"moneybox_id": overflow_moneybox.id, "priority": 0},
        {"moneybox_id": first_moneybox_id, "priority": 1},
        {"moneybox_id": second_moneybox_id, "priority": 2},
        {"moneybox_id": third_moneybox_id, "priority": 3},
        {"moneybox_id": fourth_moneybox_id, "priority": 4},
    ]

    with pytest.raises(OverflowMoneyboxUpdatedError) as ex_info:
        await db_manager.update_prioritylist(priorities=new_priorities_3)

    assert ex_info.value.message == "Updating overflow moneybox is not allowed/possible!"

    # fail setting priority 0 to another moneybox
    overflow_moneybox = (
        await db_manager._get_overflow_moneybox()  # noqa: ignore  # pylint: disable=protected-access
    )
    new_priorities_4 = [
        {"moneybox_id": first_moneybox_id, "priority": 0},  # not allowed, should fail
        {"moneybox_id": second_moneybox_id, "priority": 2},
        {"moneybox_id": third_moneybox_id, "priority": 3},
        {"moneybox_id": fourth_moneybox_id, "priority": 4},
    ]

    with pytest.raises(UpdateInstanceError) as ex_info:
        await db_manager.update_prioritylist(priorities=new_priorities_4)

    assert (
        ex_info.value.message
        == "Updating priority=0 is not allowed (reserved for Overflow Moneybox)."
    )

    # reset to original priorities
    del new_priorities_2[-1]
    await db_manager.update_prioritylist(priorities=new_priorities_2)


@pytest.mark.dependency(depends=["test_update_priorities"])
async def test_update_moneybox(db_manager: DBManager) -> None:
    first_moneybox_id = (
        await get_moneybox_id_by_name(  # noqa: typing  # pylint:disable=protected-access
            async_session=db_manager.async_sessionmaker, name="Test Box 1"
        )
    )

    moneybox_data = {"name": "Test Box 1 - Updated"}
    result_moneybox_data = await db_manager.update_moneybox(
        moneybox_id=first_moneybox_id,
        moneybox_data=moneybox_data,
    )

    assert isinstance(result_moneybox_data["created_at"], datetime)
    assert isinstance(result_moneybox_data["modified_at"], datetime)

    del result_moneybox_data["created_at"]
    del result_moneybox_data["modified_at"]

    expected_moneybox_data = moneybox_data | {
        "id": first_moneybox_id,
        "balance": 0,
        "savings_amount": 0,
        "savings_target": None,
        "priority": 1,
    }
    assert result_moneybox_data == expected_moneybox_data

    moneybox_data["name"] = "new"
    non_existing_moneybox_ids = [-42, -1, 0, 165485641]
    for moneybox_id in non_existing_moneybox_ids:
        with pytest.raises(UpdateInstanceError) as ex_info:
            await db_manager.update_moneybox(
                moneybox_id=moneybox_id,
                moneybox_data=moneybox_data,
            )

        assert isinstance(ex_info.value.details, dict)
        assert jsonable_encoder(ex_info.value.details) is not None
        assert ex_info.value.record_id == moneybox_id


@pytest.mark.dependency(depends=["test_update_moneybox"])
async def test_get_historical_moneybox_name_success(db_manager: DBManager) -> None:
    first_moneybox_id = (
        await get_moneybox_id_by_name(  # noqa: typing  # pylint:disable=protected-access
            async_session=db_manager.async_sessionmaker, name="Test Box 1 - Updated"
        )
    )
    moneybox_name: str = (
        await db_manager._get_historical_moneybox_name(  # pylint: disable=protected-access
            moneybox_id=first_moneybox_id,
            from_datetime=datetime.now(tz=timezone.utc) + timedelta(hours=2),
        )
    )

    assert moneybox_name == "Test Box 1 - Updated"


@pytest.mark.dependency(depends=["test_get_historical_moneybox_name_success"])
async def test_get_historical_moneybox_name_fail(db_manager: DBManager) -> None:
    first_moneybox_id = (
        await get_moneybox_id_by_name(  # noqa: typing  # pylint:disable=protected-access
            async_session=db_manager.async_sessionmaker, name="Test Box 1 - Updated"
        )
    )

    with pytest.raises(MoneyboxNameNotFoundError):
        await db_manager._get_historical_moneybox_name(  # pylint: disable=protected-access
            moneybox_id=first_moneybox_id,
            from_datetime=datetime.now(tz=timezone.utc) - timedelta(hours=2),
        )


@pytest.mark.dependency(depends=["test_get_historical_moneybox_name_fail"])
async def test_get_moneybox(db_manager: DBManager) -> None:
    first_moneybox_id: int = await get_moneybox_id_by_name(  # pylint:disable=protected-access
        async_session=db_manager.async_sessionmaker, name="Test Box 1 - Updated"
    )
    result_moneybox_data: dict[str, Any] = (
        await db_manager.get_moneybox(  # noqa: typing  # pylint:disable=protected-access
            moneybox_id=first_moneybox_id
        )
    )

    assert isinstance(result_moneybox_data["created_at"], datetime)
    assert isinstance(result_moneybox_data["modified_at"], datetime)
    del result_moneybox_data["created_at"]
    del result_moneybox_data["modified_at"]

    expected_moneybox_data = {
        "id": first_moneybox_id,
        "balance": 0,
        "name": "Test Box 1 - Updated",
        "savings_amount": 0,
        "savings_target": None,
        "priority": 1,
    }
    assert result_moneybox_data == expected_moneybox_data

    non_existing_moneybox_ids = [-42, -1, 0, 165485641]
    for moneybox_id in non_existing_moneybox_ids:
        with pytest.raises(MoneyboxNotFoundError) as ex_info:
            await db_manager.get_moneybox(moneybox_id=moneybox_id)

        assert f"Moneybox with id '{moneybox_id}' does not exist." == ex_info.value.message
        assert isinstance(ex_info.value.details, dict)
        assert jsonable_encoder(ex_info.value.details) is not None
        assert ex_info.value.details["record_id"] == moneybox_id
        assert ex_info.value.record_id == moneybox_id


@pytest.mark.dependency(depends=["test_get_moneybox"], session="scope")
async def test_delete_moneybox(db_manager: DBManager) -> None:
    # add amount to moneybox 3
    third_moneybox_id = (
        await get_moneybox_id_by_name(  # noqa: typing  # pylint:disable=protected-access
            async_session=db_manager.async_sessionmaker, name="Test Box 3"
        )
    )

    deposit_transaction = DepositTransactionRequest(
        amount=1,
        description="Bonus.",
    )
    await db_manager.add_amount(
        moneybox_id=third_moneybox_id,
        deposit_transaction_data=deposit_transaction.model_dump(),
        transaction_type=TransactionType.DIRECT,
        transaction_trigger=TransactionTrigger.MANUALLY,
    )

    with pytest.raises(HasBalanceError):
        await db_manager.delete_moneybox(moneybox_id=third_moneybox_id)

    # sub amount from moneybox 3 for deletion
    withdraw_transaction = WithdrawTransactionRequest(amount=1)
    await db_manager.sub_amount(
        moneybox_id=third_moneybox_id,
        withdraw_transaction_data=withdraw_transaction.model_dump(),
        transaction_type=TransactionType.DIRECT,
        transaction_trigger=TransactionTrigger.MANUALLY,
    )

    assert await db_manager.delete_moneybox(moneybox_id=third_moneybox_id) is None  # type: ignore

    non_existing_moneybox_ids = [-42, -1, 0, 165485641]
    for moneybox_id in non_existing_moneybox_ids:
        with pytest.raises(MoneyboxNotFoundError) as ex_info:
            await db_manager.delete_moneybox(moneybox_id=moneybox_id)

        assert f"Moneybox with id '{moneybox_id}' does not exist." == ex_info.value.message
        assert isinstance(ex_info.value.details, dict)
        assert jsonable_encoder(ex_info.value.details) is not None
        assert ex_info.value.details["record_id"] == moneybox_id
        assert ex_info.value.record_id == moneybox_id


@pytest.mark.dependency(depends=["test_delete_moneybox"])
async def test_add_amount_to_first_moneybox(db_manager: DBManager) -> None:
    first_moneybox_id = (
        await get_moneybox_id_by_name(  # noqa: typing  # pylint:disable=protected-access
            async_session=db_manager.async_sessionmaker, name="Test Box 1 - Updated"
        )
    )

    moneybox_data = await db_manager.get_moneybox(moneybox_id=first_moneybox_id)
    del moneybox_data["created_at"]
    del moneybox_data["modified_at"]

    deposit_transaction_1 = DepositTransactionRequest(
        amount=1,
        description="Bonus.",
    )
    result_moneybox_data_1 = await db_manager.add_amount(
        moneybox_id=first_moneybox_id,
        deposit_transaction_data=deposit_transaction_1.model_dump(),
        transaction_type=TransactionType.DIRECT,
        transaction_trigger=TransactionTrigger.MANUALLY,
    )

    assert isinstance(result_moneybox_data_1["created_at"], datetime)
    assert isinstance(result_moneybox_data_1["modified_at"], datetime)
    del result_moneybox_data_1["created_at"]
    del result_moneybox_data_1["modified_at"]

    moneybox_data["balance"] += 1
    assert moneybox_data == result_moneybox_data_1

    deposit_transaction_2 = DepositTransactionRequest(
        amount=10,
        description="Bonus.",
    )
    result_moneybox_data_2 = await db_manager.add_amount(
        moneybox_id=first_moneybox_id,
        deposit_transaction_data=deposit_transaction_2.model_dump(),
        transaction_type=TransactionType.DIRECT,
        transaction_trigger=TransactionTrigger.MANUALLY,
    )
    moneybox_data["balance"] += 10

    assert isinstance(result_moneybox_data_2["created_at"], datetime)
    assert isinstance(result_moneybox_data_2["modified_at"], datetime)
    del result_moneybox_data_2["created_at"]
    del result_moneybox_data_2["modified_at"]
    assert moneybox_data == result_moneybox_data_2

    # check for add logs
    transaction_logs = await db_manager.get_transaction_logs(moneybox_id=first_moneybox_id)

    for transaction_log in transaction_logs:
        del transaction_log["created_at"]
        del transaction_log["id"]

    expected_dict_1 = {
        "description": "Bonus.",
        "transaction_type": TransactionType.DIRECT,
        "transaction_trigger": TransactionTrigger.MANUALLY,
        "amount": 1,
        "balance": 1,
        "counterparty_moneybox_id": None,
        "counterparty_moneybox_name": None,
        "moneybox_id": first_moneybox_id,
    }
    expected_dict_2 = {
        "description": "Bonus.",
        "transaction_type": TransactionType.DIRECT,
        "transaction_trigger": TransactionTrigger.MANUALLY,
        "amount": 10,
        "balance": 11,
        "counterparty_moneybox_id": None,
        "counterparty_moneybox_name": None,
        "moneybox_id": first_moneybox_id,
    }

    assert len(transaction_logs) == 2
    assert transaction_logs[0] == expected_dict_1
    assert transaction_logs[1] == expected_dict_2

    # expected exception tests
    with pytest.raises(ValidationError):
        await db_manager.add_amount(
            moneybox_id=first_moneybox_id,
            deposit_transaction_data=DepositTransactionRequest(
                amount=0,
                description="Bonus.",
            ).model_dump(),
            transaction_type=TransactionType.DIRECT,
            transaction_trigger=TransactionTrigger.MANUALLY,
        )

    with pytest.raises(NonPositiveAmountError):
        await db_manager.add_amount(
            moneybox_id=first_moneybox_id,
            deposit_transaction_data={
                "amount": 0,
                "description": "Bonus.",
            },
            transaction_type=TransactionType.DIRECT,
            transaction_trigger=TransactionTrigger.MANUALLY,
        )

    # without session
    with pytest.raises(MoneyboxNotFoundError):
        await db_manager.add_amount(
            moneybox_id=654321,
            deposit_transaction_data={
                "amount": 1,
                "description": "Bonus.",
            },
            transaction_type=TransactionType.DIRECT,
            transaction_trigger=TransactionTrigger.MANUALLY,
        )

    # with session
    async with db_manager.async_sessionmaker.begin() as session:
        with pytest.raises(MoneyboxNotFoundError):
            await db_manager.add_amount(
                session=session,
                moneybox_id=654321,
                deposit_transaction_data={
                    "amount": 1,
                    "description": "Bonus.",
                },
                transaction_type=TransactionType.DIRECT,
                transaction_trigger=TransactionTrigger.MANUALLY,
            )


@pytest.mark.dependency(depends=["test_add_amount_to_first_moneybox"])
async def test_sub_amount_from_moneybox(  # pylint: disable=too-many-statements
    db_manager: DBManager,
) -> None:
    first_moneybox_id = await get_moneybox_id_by_name(
        async_session=db_manager.async_sessionmaker, name="Test Box 1 - Updated"
    )

    moneybox_data = await db_manager.get_moneybox(moneybox_id=first_moneybox_id)
    del moneybox_data["created_at"]
    del moneybox_data["modified_at"]

    withdraw_transaction_1 = WithdrawTransactionRequest(amount=1)
    result_moneybox_data_1 = await db_manager.sub_amount(
        moneybox_id=first_moneybox_id,
        withdraw_transaction_data=withdraw_transaction_1.model_dump(),
        transaction_type=TransactionType.DIRECT,
        transaction_trigger=TransactionTrigger.MANUALLY,
    )
    assert isinstance(result_moneybox_data_1["created_at"], datetime)
    assert isinstance(result_moneybox_data_1["modified_at"], datetime)
    del result_moneybox_data_1["created_at"]
    del result_moneybox_data_1["modified_at"]

    moneybox_data["balance"] -= 1
    assert moneybox_data == result_moneybox_data_1

    withdraw_transaction_2 = WithdrawTransactionRequest(
        amount=10,
    )
    result_moneybox_data_2 = await db_manager.sub_amount(
        moneybox_id=first_moneybox_id,
        withdraw_transaction_data=withdraw_transaction_2.model_dump(),
        transaction_type=TransactionType.DIRECT,
        transaction_trigger=TransactionTrigger.MANUALLY,
    )
    assert isinstance(result_moneybox_data_2["created_at"], datetime)
    assert isinstance(result_moneybox_data_2["modified_at"], datetime)
    del result_moneybox_data_2["created_at"]
    del result_moneybox_data_2["modified_at"]

    moneybox_data["balance"] -= 10
    assert moneybox_data == result_moneybox_data_2

    # test sub transaction logs
    transaction_logs = await db_manager.get_transaction_logs(moneybox_id=first_moneybox_id)

    for transaction_log in transaction_logs:
        del transaction_log["created_at"]
        del transaction_log["id"]

    expected_withdraw_dict_1 = {
        "description": "",
        "transaction_type": TransactionType.DIRECT,
        "transaction_trigger": TransactionTrigger.MANUALLY,
        "amount": -1,
        "balance": 10,
        "counterparty_moneybox_id": None,
        "counterparty_moneybox_name": None,
        "moneybox_id": first_moneybox_id,
    }

    expected_withdraw_dict_2 = {
        "description": "",
        "transaction_type": TransactionType.DIRECT,
        "transaction_trigger": TransactionTrigger.MANUALLY,
        "amount": -10,
        "balance": 0,
        "counterparty_moneybox_id": None,
        "counterparty_moneybox_name": None,
        "moneybox_id": first_moneybox_id,
    }

    assert len(transaction_logs) == 4
    assert transaction_logs[2] == expected_withdraw_dict_1
    assert transaction_logs[3] == expected_withdraw_dict_2

    # expected exception tests
    with pytest.raises(ValidationError):
        await db_manager.sub_amount(
            moneybox_id=first_moneybox_id,
            withdraw_transaction_data=WithdrawTransactionRequest(amount=0).model_dump(),
            transaction_type=TransactionType.DIRECT,
            transaction_trigger=TransactionTrigger.MANUALLY,
        )

    withdraw_transaction_3 = WithdrawTransactionRequest(
        amount=1000,
    )

    with pytest.raises(BalanceResultIsNegativeError) as ex_info:
        await db_manager.sub_amount(
            moneybox_id=first_moneybox_id,
            withdraw_transaction_data=withdraw_transaction_3.model_dump(),
            transaction_type=TransactionType.DIRECT,
            transaction_trigger=TransactionTrigger.MANUALLY,
        )

    assert (
        f"Can't sub amount '1000' from Moneybox '{first_moneybox_id}'. Not enough balance to sub."
        == ex_info.value.message
    )
    assert isinstance(ex_info.value.details, dict)
    assert len(ex_info.value.details) == 2
    assert ex_info.value.details["id"] == first_moneybox_id
    assert ex_info.value.details["amount"] == 1000
    assert ex_info.value.record_id == first_moneybox_id

    with pytest.raises(NonPositiveAmountError) as ex_info:
        await db_manager.sub_amount(
            moneybox_id=first_moneybox_id,
            withdraw_transaction_data={"amount": 0},
            transaction_type=TransactionType.DIRECT,
            transaction_trigger=TransactionTrigger.MANUALLY,
        )

    assert (
        ex_info.value.message
        == f"Can't add or sub amount less than 1 '0' to Moneybox '{first_moneybox_id}'."
    )
    assert ex_info.value.details == {"amount": 0, "id": first_moneybox_id}
    assert ex_info.value.record_id == first_moneybox_id

    with pytest.raises(NonPositiveAmountError) as ex_info:
        await db_manager.sub_amount(
            moneybox_id=first_moneybox_id,
            withdraw_transaction_data={
                "amount": -1,
            },
            transaction_type=TransactionType.DIRECT,
            transaction_trigger=TransactionTrigger.MANUALLY,
        )

    assert (
        ex_info.value.message
        == f"Can't add or sub amount less than 1 '-1' to Moneybox '{first_moneybox_id}'."
    )
    assert ex_info.value.details == {"amount": -1, "id": first_moneybox_id}
    assert ex_info.value.record_id == first_moneybox_id

    with pytest.raises(MoneyboxNotFoundError):
        await db_manager.sub_amount(
            moneybox_id=654321,
            withdraw_transaction_data={
                "amount": 1,
            },
            transaction_type=TransactionType.DIRECT,
            transaction_trigger=TransactionTrigger.MANUALLY,
        )


@pytest.mark.dependency(depends=["test_sub_amount_from_moneybox"])
async def test_transfer_amount(db_manager: DBManager) -> None:
    first_moneybox_id = (
        await get_moneybox_id_by_name(  # noqa: typing  # pylint:disable=protected-access
            async_session=db_manager.async_sessionmaker, name="Test Box 1 - Updated"
        )
    )
    second_moneybox_id = (
        await get_moneybox_id_by_name(  # noqa: typing  # pylint:disable=protected-access
            async_session=db_manager.async_sessionmaker, name="Test Box 2"
        )
    )

    from_moneybox_data = await db_manager.get_moneybox(moneybox_id=second_moneybox_id)
    to_moneybox_data = await db_manager.get_moneybox(moneybox_id=first_moneybox_id)

    transfer_transaction_1 = TransferTransactionRequest(
        toMoneyboxId=to_moneybox_data["id"],
        amount=50,
    )

    await db_manager.transfer_amount(
        from_moneybox_id=from_moneybox_data["id"],
        transfer_transaction_data=transfer_transaction_1.model_dump(),
        transaction_type=TransactionType.DIRECT,
        transaction_trigger=TransactionTrigger.MANUALLY,
    )

    new_from_moneybox_data = await db_manager.get_moneybox(moneybox_id=second_moneybox_id)
    new_to_moneybox_data = await db_manager.get_moneybox(moneybox_id=first_moneybox_id)

    assert from_moneybox_data["balance"] - 50 == new_from_moneybox_data["balance"]
    assert to_moneybox_data["balance"] + 50 == new_to_moneybox_data["balance"]

    # test sub transaction logs
    transaction_logs_moneybox_1 = await db_manager.get_transaction_logs(
        moneybox_id=first_moneybox_id
    )
    transaction_logs_moneybox_2 = await db_manager.get_transaction_logs(
        moneybox_id=second_moneybox_id
    )

    for transaction_log in transaction_logs_moneybox_1:
        del transaction_log["created_at"]
        del transaction_log["id"]

    for transaction_log in transaction_logs_moneybox_2:
        del transaction_log["created_at"]
        del transaction_log["id"]

    expected_transfer_dict_moneybox_1 = {
        "description": "",
        "transaction_type": TransactionType.DIRECT,
        "transaction_trigger": TransactionTrigger.MANUALLY,
        "amount": 50,
        "balance": 50,
        "counterparty_moneybox_id": second_moneybox_id,
        "moneybox_id": first_moneybox_id,
        "counterparty_moneybox_name": "Test Box 2",
    }
    expected_transfer_dict_moneybox_2 = {
        "description": "",
        "transaction_type": TransactionType.DIRECT,
        "transaction_trigger": TransactionTrigger.MANUALLY,
        "amount": -50,
        "balance": 300,
        "counterparty_moneybox_id": first_moneybox_id,
        "moneybox_id": second_moneybox_id,
        "counterparty_moneybox_name": "Test Box 1 - Updated",
    }

    assert len(transaction_logs_moneybox_1) == 5
    assert len(transaction_logs_moneybox_2) == 1
    assert expected_transfer_dict_moneybox_1 == transaction_logs_moneybox_1[-1]
    assert expected_transfer_dict_moneybox_2 == transaction_logs_moneybox_2[-1]

    # expected exception tests
    with pytest.raises(ValidationError):
        await db_manager.transfer_amount(
            from_moneybox_id=from_moneybox_data["id"],
            transfer_transaction_data=TransferTransactionRequest(
                to_moneybox_id=to_moneybox_data["id"],
                amount=0,
            ).model_dump(),
            transaction_type=TransactionType.DIRECT,
            transaction_trigger=TransactionTrigger.MANUALLY,
        )

    with pytest.raises(MoneyboxNotFoundError):
        await db_manager.transfer_amount(
            from_moneybox_id=42,
            transfer_transaction_data=TransferTransactionRequest(
                toMoneyboxId=to_moneybox_data["id"],
                amount=10,
            ).model_dump(),
            transaction_type=TransactionType.DIRECT,
            transaction_trigger=TransactionTrigger.MANUALLY,
        )

    with pytest.raises(MoneyboxNotFoundError):
        await db_manager.transfer_amount(
            from_moneybox_id=from_moneybox_data["id"],
            transfer_transaction_data=TransferTransactionRequest(
                toMoneyboxId=41,
                amount=10,
            ).model_dump(),
            transaction_type=TransactionType.DIRECT,
            transaction_trigger=TransactionTrigger.MANUALLY,
        )

    with pytest.raises(BalanceResultIsNegativeError) as ex_info:
        await db_manager.transfer_amount(
            from_moneybox_id=from_moneybox_data["id"],
            transfer_transaction_data=TransferTransactionRequest(
                toMoneyboxId=to_moneybox_data["id"],
                amount=1000,
            ).model_dump(),
            transaction_type=TransactionType.DIRECT,
            transaction_trigger=TransactionTrigger.MANUALLY,
        )

    expected_exception_message = (
        f"Can't sub amount '1000' from Moneybox '{from_moneybox_data['id']}'. "
        "Not enough balance to sub."
    )
    assert ex_info.value.message == expected_exception_message

    with pytest.raises(TransferEqualMoneyboxError) as ex_info:
        await db_manager.transfer_amount(
            from_moneybox_id=first_moneybox_id,
            transfer_transaction_data={
                "to_moneybox_id": first_moneybox_id,
                "amount": 123,
                "description": "Bonus.",
            },
            transaction_type=TransactionType.DIRECT,
            transaction_trigger=TransactionTrigger.MANUALLY,
        )

    assert ex_info.value.message == "Can't transfer within the same moneybox"
    assert ex_info.value.details == {
        "amount": 123,
        "fromMoneyboxId": first_moneybox_id,
        "toMoneyboxId": first_moneybox_id,
    }

    with pytest.raises(NonPositiveAmountError) as ex_info:
        await db_manager.transfer_amount(
            from_moneybox_id=first_moneybox_id,
            transfer_transaction_data={
                "to_moneybox_id": second_moneybox_id,
                "amount": 0,
                "description": "Bonus.",
            },
            transaction_type=TransactionType.DIRECT,
            transaction_trigger=TransactionTrigger.MANUALLY,
        )


@pytest.mark.dependency(depends=["test_transfer_amount"])
async def test_get_transactions_logs_with_counterparty_to_deleted_moneybox(
    db_manager: DBManager,
) -> None:
    # moneybox 4
    moneybox_data_4 = {"name": "4-Test Box", "priority": 6}
    result_moneybox_data_4 = await db_manager.add_moneybox(moneybox_data=moneybox_data_4)

    # moneybox 5
    moneybox_data_5 = {"name": "5-Test Box", "priority": 7}
    result_moneybox_data_5 = await db_manager.add_moneybox(moneybox_data=moneybox_data_5)

    deposit_transaction = DepositTransactionRequest(
        amount=100,
        description="Bonus.",
    )
    await db_manager.add_amount(
        moneybox_id=result_moneybox_data_4["id"],
        deposit_transaction_data=deposit_transaction.model_dump(),
        transaction_type=TransactionType.DIRECT,
        transaction_trigger=TransactionTrigger.MANUALLY,
    )

    transfer_transaction = TransferTransactionRequest(
        toMoneyboxId=result_moneybox_data_5["id"],
        amount=20,
    )

    await db_manager.transfer_amount(
        from_moneybox_id=result_moneybox_data_4["id"],
        transfer_transaction_data=transfer_transaction.model_dump(),
        transaction_type=TransactionType.DIRECT,
        transaction_trigger=TransactionTrigger.MANUALLY,
    )

    withdraw_transaction = WithdrawTransactionRequest(amount=20)
    await db_manager.sub_amount(
        moneybox_id=result_moneybox_data_5["id"],
        withdraw_transaction_data=withdraw_transaction.model_dump(),
        transaction_type=TransactionType.DIRECT,
        transaction_trigger=TransactionTrigger.MANUALLY,
    )

    await db_manager.delete_moneybox(result_moneybox_data_5["id"])

    # should be able to get transaction logs without getting an exception
    transaction_logs = await db_manager.get_transaction_logs(result_moneybox_data_4["id"])
    assert len(transaction_logs) == 2

    withdraw_transaction = WithdrawTransactionRequest(amount=80)
    await db_manager.sub_amount(
        moneybox_id=result_moneybox_data_4["id"],
        withdraw_transaction_data=withdraw_transaction.model_dump(),
        transaction_type=TransactionType.DIRECT,
        transaction_trigger=TransactionTrigger.MANUALLY,
    )

    await db_manager.delete_moneybox(result_moneybox_data_4["id"])


@pytest.mark.dependency(
    depends=["test_get_transactions_logs_with_counterparty_to_deleted_moneybox"]
)
async def test_transactions_logs_between_overflow_moneybox(
    db_manager: DBManager,
) -> None:
    overflow_moneybox: Moneybox = (
        await db_manager._get_overflow_moneybox()  # noqa: ignore  # pylint: disable=protected-access
    )
    first_moneybox_id: int = await get_moneybox_id_by_name(
        async_session=db_manager.async_sessionmaker, name="Test Box 1 - Updated"
    )

    transfer_transaction = TransferTransactionRequest(
        toMoneyboxId=overflow_moneybox.id,
        amount=1,
    )
    await db_manager.transfer_amount(
        from_moneybox_id=first_moneybox_id,
        transfer_transaction_data=transfer_transaction.model_dump(),
        transaction_type=TransactionType.DIRECT,
        transaction_trigger=TransactionTrigger.MANUALLY,
    )

    transaction_logs = await db_manager.get_transaction_logs(moneybox_id=first_moneybox_id)
    assert len(transaction_logs) == 6
    assert transaction_logs[-1]["counterparty_moneybox_name"] == "Overflow Moneybox"


@pytest.mark.dependency(depends=["test_transactions_logs_between_overflow_moneybox"])
async def test_get_app_settings_valid(db_manager: DBManager) -> None:
    _app_settings = await db_manager._get_app_settings()  # pylint: disable=protected-access
    app_settings = await db_manager.get_app_settings(app_settings_id=_app_settings.id)

    expected_data = {
        "is_automated_saving_active": True,
        "savings_amount": 0,
        "id": _app_settings.id,
        "send_reports_via_email": False,
        "user_email_address": None,
        "overflow_moneybox_automated_savings_mode": OverflowMoneyboxAutomatedSavingsModeType.COLLECT,  # noqa: ignore   # pylint: disable=line-too-long
    }

    assert equal_dict(
        dict_1=app_settings,
        dict_2=expected_data,
        exclude_keys=["created_at", "modified_at"],
    )


@pytest.mark.dependency(depends=["test_get_app_settings_valid"])
async def test_update_app_settings_valid(db_manager: DBManager) -> None:
    update_data_1 = {
        "savings_amount": 0,
        "is_automated_saving_active": False,
    }

    updated_app_settings_1 = await db_manager.update_app_settings(
        app_settings_data=update_data_1,
    )

    expected_data_1 = {
        "is_automated_saving_active": False,
        "savings_amount": 0,
        "send_reports_via_email": False,
        "user_email_address": None,
        "overflow_moneybox_automated_savings_mode": OverflowMoneyboxAutomatedSavingsModeType.COLLECT,  # noqa: ignore   # pylint: disable=line-too-long
    }

    assert equal_dict(
        dict_1=updated_app_settings_1,
        dict_2=expected_data_1,
        exclude_keys=["created_at", "modified_at", "id"],
    )

    update_data_2 = {
        "is_automated_saving_active": True,
    }

    updated_app_settings_2 = await db_manager.update_app_settings(
        app_settings_data=update_data_2,
    )

    expected_data_2 = {
        "is_automated_saving_active": True,
        "savings_amount": 0,
        "send_reports_via_email": False,
        "user_email_address": None,
        "overflow_moneybox_automated_savings_mode": OverflowMoneyboxAutomatedSavingsModeType.COLLECT,  # noqa: ignore   # pylint: disable=line-too-long
    }

    assert equal_dict(
        dict_1=updated_app_settings_2,
        dict_2=expected_data_2,
        exclude_keys=["created_at", "modified_at", "id"],
    )


@pytest.mark.dependency(depends=["test_update_app_settings_valid"])
async def test_update_app_settings_invalid(db_manager: DBManager) -> None:
    update_data = {
        # results to asyncpg.exceptions.InvalidTextRepresentationError
        "overflow_moneybox_automated_savings_mode": "unknown_mode",
    }

    with pytest.raises(UpdateInstanceError):
        await db_manager.update_app_settings(
            app_settings_data=update_data,
        )


@pytest.mark.dependency(depends=["test_update_app_settings_valid"])
async def test_get_app_settings_invalid(
    load_test_data: None,  # pylint: disable=unused-argument
    db_manager: DBManager,
) -> None:
    # we assume an app_settings_id = 1
    with pytest.raises(AppSettingsNotFoundError):
        await db_manager.get_app_settings(app_settings_id=1)

    # test _get_app_settings helper function
    with pytest.raises(InconsistentDatabaseError):
        await db_manager._get_app_settings()  # noqa: ignore  # pylint: disable=protected-access


@pytest.mark.dependency(depends=["test_get_app_settings_invalid"])
async def test_add_automated_savings_log_valid_with_session(
    db_manager: DBManager,
) -> None:
    action_at = datetime.now(tz=timezone.utc)
    automated_savings_log_data_collection = [
        {
            "action": ActionType.DEACTIVATED_AUTOMATED_SAVING,
            "action_at": action_at,
            "details": {"meta": "data 3"},
        },
        {
            "action": ActionType.CHANGED_AUTOMATED_SAVINGS_AMOUNT,
            "action_at": action_at,
            "details": {"meta": "data 4"},
        },
    ]

    for i, automated_savings_log_data in enumerate(automated_savings_log_data_collection):
        async with db_manager.async_sessionmaker.begin() as session:
            automated_savings_log = await db_manager.add_automated_savings_logs(
                session=session,
                automated_savings_log_data=automated_savings_log_data,
            )

            assert equal_dict(
                dict_1=automated_savings_log,
                dict_2=automated_savings_log_data_collection[  # noqa: ignore  # pylint: disable=unnecessary-list-index-lookup, line-too-long
                    i
                ],
                exclude_keys=["created_at", "modified_at", "id"],
            )


@pytest.mark.dependency(
    name="test_get_automated_savings_logs",
    depends=["test_add_automated_savings_log_valid_with_session"],
)
@pytest.mark.parametrize(
    "action_type",
    [ActionType.APPLIED_AUTOMATED_SAVING, ActionType.DEACTIVATED_AUTOMATED_SAVING],
)
async def test_get_automated_savings_logs(db_manager: DBManager, action_type: ActionType) -> None:
    expected_data = {
        ActionType.APPLIED_AUTOMATED_SAVING: [
            {
                "action": ActionType.APPLIED_AUTOMATED_SAVING,
                "details": {"meta": "data 2"},
            },
        ],
        ActionType.CHANGED_AUTOMATED_SAVINGS_AMOUNT: [
            {
                "action": ActionType.CHANGED_AUTOMATED_SAVINGS_AMOUNT,
                "details": {"meta": "data 1"},
            },
            {
                "action": ActionType.CHANGED_AUTOMATED_SAVINGS_AMOUNT,
                "details": {"meta": "data 4"},
            },
        ],
        ActionType.DEACTIVATED_AUTOMATED_SAVING: [
            {
                "action": ActionType.DEACTIVATED_AUTOMATED_SAVING,
                "details": {"meta": "data 3"},
            },
        ],
    }

    automated_savings_logs = await db_manager.get_automated_savings_logs(
        action_type=action_type,
    )

    automated_savings_logs = sorted(
        automated_savings_logs, key=lambda item: item["details"]["meta"]
    )

    for i, automated_savings_log in enumerate(automated_savings_logs):
        assert "action_at" in automated_savings_log
        assert isinstance(automated_savings_log["action_at"], datetime)

        assert equal_dict(
            dict_1=automated_savings_log,
            dict_2=expected_data[action_type][i],
            exclude_keys=["created_at", "modified_at", "id", "action_at"],
        )


@pytest.mark.dependency(depends=["test_get_automated_savings_logs"])
async def test_automated_savings_overflow_moneybox_mode_collect(
    load_test_data: None,  # pylint: disable=unused-argument
    db_manager: DBManager,
) -> None:
    await db_manager.automated_savings()

    moneyboxes = await db_manager.get_moneyboxes()
    expected_data = {
        "Overflow Moneybox": 105,
        "Test Box 1": 5,
        "Test Box 2": 5,
        "Test Box 3": 15,
        "Test Box 4": 20,
        "Test Box 5": 0,
        "Test Box 6": 0,
    }

    for moneybox in moneyboxes:
        assert moneybox["balance"] == expected_data[moneybox["name"]]

    # >>>  test case for bug: issue #71
    # - test if correct overflow moneybox mode is set in transaction log of overflow moneybox
    overflow_moneybox = (
        await db_manager._get_overflow_moneybox()  # noqa: typing  # pylint:disable=protected-access
    )
    overflow_moneybox_transaction_logs = await db_manager.get_transaction_logs(
        moneybox_id=overflow_moneybox.id,
    )

    last_transaction_log = overflow_moneybox_transaction_logs[-1]
    expected_description = (
        "Automated Savings with Overflow Moneybox Mode: "
        f"{OverflowMoneyboxAutomatedSavingsModeType.COLLECT}"
    )
    assert last_transaction_log["description"] == expected_description
    # <<<


@pytest.mark.dependency(depends=["test_automated_savings_overflow_moneybox_mode_collect"])
async def test_automated_savings_overflow_moneybox_mode_add_to_amount(
    load_test_data: None,  # pylint: disable=unused-argument
    db_manager: DBManager,
) -> None:
    await db_manager.automated_savings()

    moneyboxes = await db_manager.get_moneyboxes()
    expected_data = {
        "Overflow Moneybox": 105,
        "Test Box 1": 5,
        "Test Box 2": 5,
        "Test Box 3": 15,
        "Test Box 4": 20,
        "Test Box 5": 0,
        "Test Box 6": 0,
    }

    for moneybox in moneyboxes:
        assert moneybox["balance"] == expected_data[moneybox["name"]]

    # >>>  test case for bug: issue #71
    # - test if correct overflow moneybox mode is set in transaction log of overflow moneybox
    overflow_moneybox = (
        await db_manager._get_overflow_moneybox()  # noqa: typing  # pylint:disable=protected-access
    )
    overflow_moneybox_transaction_logs = await db_manager.get_transaction_logs(
        moneybox_id=overflow_moneybox.id,
    )

    last_transaction_log = overflow_moneybox_transaction_logs[-1]
    expected_description = (
        "Automated Savings with Overflow Moneybox Mode: "
        f"{OverflowMoneyboxAutomatedSavingsModeType.ADD_TO_AUTOMATED_SAVINGS_AMOUNT}"
    )
    assert last_transaction_log["description"] == expected_description
    # <<<


@pytest.mark.dependency(depends=["test_automated_savings_overflow_moneybox_mode_add_to_amount"])
async def test_automated_savings_overflow_moneybox_mode_fill_up(
    load_test_data: None,  # pylint: disable=unused-argument
    db_manager: DBManager,
) -> None:
    await db_manager.automated_savings()

    moneyboxes = await db_manager.get_moneyboxes()
    expected_data = {
        "Overflow Moneybox": 75,
        "Test Box 1": 5,
        "Test Box 2": 5,
        "Test Box 3": 15,
        "Test Box 4": 50,
        "Test Box 5": 0,
        "Test Box 6": 0,
    }

    for moneybox in moneyboxes:
        assert moneybox["balance"] == expected_data[moneybox["name"]]

    # >>> test case for bug: issue #71
    # - test if correct overflow moneybox mode is set in transaction log of overflow moneybox
    overflow_moneybox = (
        await db_manager._get_overflow_moneybox()  # noqa: typing  # pylint:disable=protected-access
    )
    overflow_moneybox_transaction_logs = await db_manager.get_transaction_logs(
        moneybox_id=overflow_moneybox.id,
    )

    last_transaction_log = overflow_moneybox_transaction_logs[-1]
    expected_description = (
        "Automated Savings with Overflow Moneybox Mode: "
        f"{OverflowMoneyboxAutomatedSavingsModeType.FILL_UP_LIMITED_MONEYBOXES}"
    )
    assert last_transaction_log["description"] == expected_description
    # <<<


@pytest.mark.dependency(depends=["test_automated_savings_overflow_moneybox_mode_fill_up"])
async def test_reset_database_keep_app_settings(
    load_test_data: None, db_manager: DBManager  # pylint: disable=unused-argument
) -> None:
    original_main = CommandLine.main

    with patch.object(CommandLine, "main") as mock_main:

        def patched_main(cmd_line, args):  # type: ignore
            args = ["-x", "ENVIRONMENT=test"] + args
            original_main(cmd_line, args)

        mock_main.side_effect = patched_main

        old_app_settings_data = (
            await db_manager._get_app_settings()  # pylint: disable=protected-access
        )
        old_moneyboxes = await db_manager.get_moneyboxes()

        await db_manager.reset_database(keep_app_settings=True)

        app_settings_data = await db_manager._get_app_settings()  # pylint: disable=protected-access
        moneyboxes = await db_manager.get_moneyboxes()

        assert equal_dict(
            dict_1=old_app_settings_data.asdict(),
            dict_2=app_settings_data.asdict(),
            exclude_keys=["created_at", "modified_at"],
        )

        assert len(old_moneyboxes) != len(moneyboxes)
        assert len(moneyboxes) == 1

        mock_main.assert_called()


@pytest.mark.dependency(depends=["test_automated_savings_overflow_moneybox_mode_fill_up"])
async def test_reset_database_delete_app_settings(
    load_test_data: None,  # pylint: disable=unused-argument
    db_manager: DBManager,
) -> None:
    original_main = CommandLine.main

    with patch.object(CommandLine, "main") as mock_main:

        def patched_main(cmd_line, args) -> None:  # type: ignore
            args = ["-x", "ENVIRONMENT=test"] + args
            original_main(cmd_line, args)

        mock_main.side_effect = patched_main

        old_app_settings_data = (
            await db_manager._get_app_settings()  # pylint: disable=protected-access
        )
        old_moneyboxes = await db_manager.get_moneyboxes()

        await db_manager.reset_database(keep_app_settings=False)

        app_settings_data = await db_manager._get_app_settings()  # pylint: disable=protected-access
        moneyboxes = await db_manager.get_moneyboxes()

        assert not equal_dict(
            dict_1=old_app_settings_data.asdict(),
            dict_2=app_settings_data.asdict(),
            exclude_keys=["created_at", "modified_at"],
        )

        assert len(old_moneyboxes) != len(moneyboxes)
        assert len(moneyboxes) == 1

        mock_main.assert_called()


@pytest.mark.dependency(depends=["test_reset_database_delete_app_settings"])
@pytest.mark.order(after="tests/test_fastapi_utils.py::test_create_pgpass")
async def test_export_sql_dump(
    load_test_data: None,  # pylint: disable=unused-argument
    db_manager: DBManager,
) -> None:
    dump_stream = await db_manager.export_sql_dump()

    dump_file_path = (Path(__file__).parent / "temp" / "dump.sql").resolve()
    dump_value = dump_stream.getvalue()

    with dump_file_path.open("wb") as f:
        f.write(dump_value)

    assert 35800 < len(dump_value) < 36000


@pytest.mark.dependency(depends=["test_export_sql_dump"])
@pytest.mark.order(after="test_export_sql_dump")
async def test_export_sql_dump_missing_dependency_error(
    db_manager: DBManager,
) -> None:
    with patch(
        "src.db.db_manager.subprocess.Popen", side_effect=Exception("pg_dump not installed")
    ):
        with pytest.raises(MissingDependencyError, match="pg_dump not installed"):
            await db_manager.export_sql_dump()


@pytest.mark.dependency(depends=["test_export_sql_dump"])
@pytest.mark.order(after="test_export_sql_dump_missing_dependency_error")
async def test_export_sql_dump_process_communication_error(
    db_manager: DBManager,
) -> None:
    with patch("src.db.db_manager.subprocess.Popen"), patch("subprocess.Popen") as mock_popen:
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b"", b"Error message")
        mock_process.returncode = -1
        mock_popen.return_value = mock_process

        with pytest.raises(ProcessCommunicationError, match="Error message"):
            await db_manager.export_sql_dump()


@pytest.mark.dependency(depends=["test_export_sql_dump"])
@pytest.mark.order(after="tests/test_app_endpoints.py::test_app_export_valid")
async def test_import_sql_dump(
    load_test_data: None,  # pylint: disable=unused-argument
    db_manager: DBManager,
) -> None:
    original_main = CommandLine.main

    with patch.object(CommandLine, "main") as mock_main:

        def patched_main(cmd_line, args) -> None:  # type: ignore
            args = ["-x", "ENVIRONMENT=test"] + args
            original_main(cmd_line, args)

        mock_main.side_effect = patched_main

        dump_file_path = (Path(__file__).parent / "temp" / "dump.sql").resolve()
        with dump_file_path.open("rb") as f:
            sql_dump = f.read()

        await db_manager.import_sql_dump(sql_dump=sql_dump)

        expected_app_settings_data = {
            "send_reports_via_email": False,
            "user_email_address": "pythbuster@gmail.com",
            "is_automated_saving_active": False,
            "savings_amount": 150,
            "overflow_moneybox_automated_savings_mode": (
                OverflowMoneyboxAutomatedSavingsModeType.FILL_UP_LIMITED_MONEYBOXES
            ),
        }
        expected_moneyboxes = [
            {
                "name": "Overflow Moneybox",
            },
            {
                "name": "Test Box 1",
            },
        ]
        moneyboxes = await db_manager.get_moneyboxes()
        assert len(moneyboxes) == len(expected_moneyboxes)
        assert moneyboxes[0]["name"] == expected_moneyboxes[0]["name"]
        assert moneyboxes[1]["name"] == expected_moneyboxes[1]["name"]

        app_settings = await db_manager._get_app_settings()  # pylint: disable=protected-access
        app_settings_data = app_settings.asdict()
        assert equal_dict(
            dict_1=app_settings_data,
            dict_2=expected_app_settings_data,
            exclude_keys=["created_at", "modified_at", "id"],
        )


@pytest.mark.dependency(depends=["test_import_sql_dump"])
@pytest.mark.order(after="test_import_sql_dump")
async def test_import_sql_dump_missing_dependency_error(
    db_manager: DBManager,
) -> None:
    dump_file_path = (Path(__file__).parent / "temp" / "dump.sql").resolve()
    with dump_file_path.open("rb") as f:
        sql_dump = f.read()

    io_bytes = io.BytesIO(sql_dump)

    with (
        patch(
            "src.db.db_manager.subprocess.Popen",
            side_effect=Exception("pg_restore not installed"),
        ),
        patch.object(
            db_manager,
            attribute="export_sql_dump",
            return_value=io_bytes,
        ),
        patch.object(
            db_manager,
            attribute="reset_database",
        ),
    ):
        with pytest.raises(MissingDependencyError, match="pg_restore not installed"):
            await db_manager.import_sql_dump(sql_dump=sql_dump)


@pytest.mark.dependency(depends=["test_import_sql_dump"])
@pytest.mark.order(after="test_import_sql_dump_missing_dependency_error")
async def test_import_sql_dump_process_communication_error(
    db_manager: DBManager,
) -> None:
    dump_file_path = (Path(__file__).parent / "temp" / "dump.sql").resolve()

    with dump_file_path.open("rb") as f:
        sql_dump = f.read()

    io_bytes = io.BytesIO(sql_dump)

    with (
        patch("src.db.db_manager.subprocess.Popen"),
        patch("subprocess.Popen") as mock_popen,
        patch.object(
            db_manager,
            attribute="export_sql_dump",
            return_value=io_bytes,
        ),
        patch.object(
            db_manager,
            attribute="reset_database",
        ),
    ):
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b"", b"Error message")
        mock_process.returncode = -1
        mock_popen.return_value = mock_process

        with pytest.raises(ProcessCommunicationError, match="Error message"):
            await db_manager.import_sql_dump(sql_dump=sql_dump)


@pytest.mark.dependency
async def test_get_users_empty(
    load_test_data: None,  # pylint: disable=unused-argument
    db_manager: DBManager,
) -> None:
    users = await db_manager.get_users()
    assert len(users) == 0


@pytest.mark.dependency(depends=["test_get_users_empty"])
async def test_add_user_success(
    db_manager: DBManager,
) -> None:
    user_data = {
        "user_name": "hannelore.von.buxtehude@eine-email-adresse-halt.de",
        "user_password": "sicher-ist-nichts",
    }
    user = await db_manager.add_user(
        user_name=user_data["user_name"],
        user_password=user_data["user_password"],
    )

    expected_user_data = {
        "user_name": "hannelore.von.buxtehude@eine-email-adresse-halt.de",
        "role": UserRoleType.USER,
    }

    # TODO: will be renamed in orm model later, remove this if done
    user["user_name"] = user["user_login"]
    del user["user_login"]

    assert equal_dict(
        dict_1=expected_user_data,
        dict_2=user,
        exclude_keys=["created_at", "modified_at", "id"],
    )


@pytest.mark.dependency(depends=["test_add_user_success"])
async def test_add_admin_user_success(
    db_manager: DBManager,
) -> None:
    user_data = {
        "user_name": "admin2",
        "user_password": "admin2",
    }
    user = await db_manager.add_user(
        user_name=user_data["user_name"],
        user_password=user_data["user_password"],
        is_admin=True,
    )

    expected_user_data = {
        "user_name": "admin2",
        "role": UserRoleType.ADMIN,
    }

    # TODO: will be renamed in orm model later, remove this if done
    user["user_name"] = user["user_login"]
    del user["user_login"]

    assert equal_dict(
        dict_1=expected_user_data,
        dict_2=user,
        exclude_keys=["created_at", "modified_at", "id"],
    )


@pytest.mark.dependency(depends=["test_add_admin_user_success"])
async def test_add_user_failed(
    db_manager: DBManager,
) -> None:
    # already existing user
    user_data = {
        "user_name": "hannelore.von.buxtehude@eine-email-adresse-halt.de",
        "user_password": "sicher-ist-nichts",
    }

    with pytest.raises(UserNameAlreadyExistError):
        await db_manager.add_user(
            user_name=user_data["user_name"],
            user_password=user_data["user_password"],
        )


@pytest.mark.dependency(depends=["test_add_user_failed"])
async def test_get_user(
    db_manager: DBManager,
) -> None:
    user_data: dict[str, str] = {
        "user_name": "hannelore2",
        "user_password": "sicher-ist-nichts",
    }
    user: dict[str, Any] = await db_manager.add_user(
        user_name=user_data["user_name"],
        user_password=user_data["user_password"],
    )

    user_id: int = user["id"]
    user = await db_manager.get_user(
        user_id=user_id,
    )

    # TODO: will be renamed in orm model later, remove this if done
    user["user_name"] = user["user_login"]
    del user["user_login"]

    expected_user_data: dict[str, Any] = {
        "user_name": "hannelore2",
        "role": UserRoleType.USER,
    }
    assert equal_dict(
        dict_1=user,
        dict_2=expected_user_data,
        exclude_keys=["created_at", "modified_at", "id"],
    )


@pytest.mark.dependency(depends=["test_get_user"])
async def test_get_user_by_credentials_success(
    db_manager: DBManager,
) -> None:
    user_data: dict[str, str] = {
        "user_name": "hannelore.von.buxtehude@eine-email-adresse-halt.de",
        "user_password": "sicher-ist-nichts",
    }
    user: dict[str, Any] | None = await db_manager.get_user_by_credentials(
        user_name=user_data["user_name"],
        user_password=user_data["user_password"],
    )
    assert user is not None


@pytest.mark.dependency(depends=["test_get_user_by_credentials_success"])
async def test_update_user_name(
    db_manager: DBManager,
) -> None:
    user_data: dict[str, str] = {
        "user_name": "hannelore.von.buxtehude@eine-email-adresse-halt.de",
        "user_password": "sicher-ist-nichts",
    }
    user: dict[str, Any] | None = await db_manager.get_user_by_credentials(
        user_name=user_data["user_name"],
        user_password=user_data["user_password"],
    )

    assert user is not None

    # TODO: will be renamed in orm model later, remove this if done
    user["user_name"] = user["user_login"]
    del user["user_login"]

    new_name: str = "hannelore@buxtehu.de"
    old_name: str = user["user_name"]
    user = await db_manager.update_user_name(
        user_id=user["id"],
        new_user_name=new_name,
    )

    # TODO: will be renamed in orm model later, remove this if done
    user["user_name"] = user["user_login"]
    del user["user_login"]

    assert new_name == user["user_name"]

    # try to get same user with new credentials
    user = await db_manager.get_user_by_credentials(
        user_name=new_name,
        user_password="sicher-ist-nichts",
    )
    assert user is not None

    # try to get same user with old credentials
    user = await db_manager.get_user_by_credentials(
        user_name=old_name,
        user_password="sicher-ist-nichts",
    )
    assert user is None


@pytest.mark.dependency(depends=["test_update_user_name"])
async def test_update_user_password(
    db_manager: DBManager,
) -> None:
    user_data: dict[str, str] = {
        "user_name": "hannelore@buxtehu.de",
        "user_password": "sicher-ist-nichts",
    }
    user: dict[str, Any] | None = await db_manager.get_user_by_credentials(
        user_name=user_data["user_name"],
        user_password=user_data["user_password"],
    )

    assert user is not None

    new_user_password: str = "sicher-ist-wirklich-wirklich-nichts"
    old_user_password: str = "sicher-ist-nichts"
    _ = await db_manager.update_user_password(
        user_id=user["id"],
        new_user_password=new_user_password,
    )

    # try to get same user with new credentials
    user = await db_manager.get_user_by_credentials(
        user_name="hannelore@buxtehu.de",
        user_password=new_user_password,
    )
    assert user is not None

    # try to get same user with old credentials
    user = await db_manager.get_user_by_credentials(
        user_name="hannelore@buxtehu.de",
        user_password=old_user_password,
    )
    assert user is None


@pytest.mark.dependency(depends=["test_update_user_password"])
async def test_delete_user(
    db_manager: DBManager,
) -> None:
    user_data: dict[str, str] = {
        "user_name": "hannelore@buxtehu.de",
        "user_password": "sicher-ist-wirklich-wirklich-nichts",
    }
    user: dict[str, Any] | None = await db_manager.get_user_by_credentials(
        user_name=user_data["user_name"],
        user_password=user_data["user_password"],
    )
    assert user is not None

    user_id: int = user["id"]
    await db_manager.delete_user(
        user_id=user_id,
    )

    with pytest.raises(UserNotFoundError):
        await db_manager.get_user(user_id=user_id)


@pytest.mark.dependency(depends=["test_delete_user"])
async def test_delete_admin_user_fail(
    db_manager: DBManager,
) -> None:
    user_data: dict[str, str] = {
        "user_name": "admin2",
        "user_password": "admin2",
    }
    admin_user: dict[str, Any] | None = await db_manager.get_user_by_credentials(
        user_name=user_data["user_name"],
        user_password=user_data["user_password"],
    )
    assert admin_user is not None

    with pytest.raises(DeleteInstanceError):
        user_id: int = admin_user["id"]
        await db_manager.delete_user(
            user_id=user_id,
        )


@pytest.mark.dependency(depends=["test_delete_admin_user_fail"])
async def test_user_by_credentials_fail(
    db_manager: DBManager,
) -> None:
    user_data: dict[str, str] = {
        "user_name": "hannelore@buxtehu.de",
        "user_password": "sicher-ist-nichts",
    }
    user: dict[str, Any] | None = await db_manager.get_user_by_credentials(
        user_name=user_data["user_name"],
        user_password=user_data["user_password"],
    )
    assert user is None


async def test_distribute_automated_savings_amount__amount_0(
    load_test_data: None,  # pylint: disable=unused-argument
    db_manager: DBManager,
) -> None:
    distribute_amount: int = 0
    moneyboxes: list[dict[str, Any]] = await db_manager.get_moneyboxes()
    sorted_by_priority_moneyboxes: list[dict[str, Any]] = sorted(
        moneyboxes, key=lambda item: item["priority"]
    )
    app_settings: AppSettings = (
        await db_manager._get_app_settings()  # noqa: ignore  # pylint: disable=protected-access
    )

    async with db_manager.async_sessionmaker.begin() as session:
        updated_moneyboxes = await db_manager._distribute_automated_savings_amount(  # noqa: ignore  # pylint: disable=protected-access
            session=session,
            distribute_amount=distribute_amount,
            sorted_by_priority_moneyboxes=sorted_by_priority_moneyboxes,
            fill_mode=False,
            app_settings=app_settings.asdict(),
        )

    assert updated_moneyboxes == sorted_by_priority_moneyboxes


async def test_distribute_automated_savings_amount__amount_negative(db_manager: DBManager) -> None:
    distribute_amount: int = -20
    moneyboxes: list[dict[str, Any]] = await db_manager.get_moneyboxes()
    sorted_by_priority_moneyboxes: list[dict[str, Any]] = sorted(
        moneyboxes, key=lambda item: item["priority"]
    )
    app_settings: AppSettings = (
        await db_manager._get_app_settings()  # noqa: ignore  # pylint: disable=protected-access
    )

    async with db_manager.async_sessionmaker.begin() as session:
        updated_moneyboxes = await db_manager._distribute_automated_savings_amount(  # noqa: ignore  # pylint: disable=protected-access
            session=session,
            distribute_amount=distribute_amount,
            sorted_by_priority_moneyboxes=sorted_by_priority_moneyboxes,
            fill_mode=False,
            app_settings=app_settings.asdict(),
        )

    assert updated_moneyboxes == sorted_by_priority_moneyboxes


async def test_distribute_automated_savings_amount__fill_mode__one_moneybox_with_savings_target_none(  # noqa: ignore  # pylint: disable=line-too-long
    load_test_data: None, db_manager: DBManager  # pylint: disable=unused-argument
) -> None:
    moneyboxes: list[dict[str, Any]] = await db_manager.get_moneyboxes()
    sorted_by_priority_moneyboxes: list[dict[str, Any]] = sorted(
        moneyboxes, key=lambda item: item["priority"]
    )
    app_settings: AppSettings = (
        await db_manager._get_app_settings()  # noqa: ignore  # pylint: disable=protected-access
    )

    async with db_manager.async_sessionmaker.begin() as session:
        updated_moneyboxes = await db_manager._distribute_automated_savings_amount(  # noqa: ignore  # pylint: disable=protected-access
            session=session,
            distribute_amount=app_settings.savings_amount,  # 150
            sorted_by_priority_moneyboxes=sorted_by_priority_moneyboxes,
            fill_mode=True,
            app_settings=app_settings.asdict(),
        )

    assert updated_moneyboxes[0]["balance"] == 140
    assert updated_moneyboxes[1]["balance"] == 5
    assert updated_moneyboxes[2]["balance"] == 5  # savings_amount = 0 but ignored in fill_mode
    assert (
        updated_moneyboxes[3]["balance"] == 0
    )  # target: None and wants 10, but fill mode ignores wises


async def test_distribute_automated_savings_amount__normal_mode__one_moneybox_with_savings_amount_0(
    load_test_data: None, db_manager: DBManager  # pylint: disable=unused-argument
) -> None:
    moneyboxes: list[dict[str, Any]] = await db_manager.get_moneyboxes()
    sorted_by_priority_moneyboxes: list[dict[str, Any]] = sorted(
        moneyboxes, key=lambda item: item["priority"]
    )
    app_settings: AppSettings = (
        await db_manager._get_app_settings()  # noqa: ignore  # pylint: disable=protected-access
    )

    async with db_manager.async_sessionmaker.begin() as session:
        updated_moneyboxes = await db_manager._distribute_automated_savings_amount(  # noqa: ignore  # pylint: disable=protected-access
            session=session,
            distribute_amount=app_settings.savings_amount,  # 150
            sorted_by_priority_moneyboxes=sorted_by_priority_moneyboxes,
            fill_mode=False,
            app_settings=app_settings.asdict(),
        )

    assert updated_moneyboxes[0]["balance"] == 135
    assert updated_moneyboxes[1]["balance"] == 5
    assert updated_moneyboxes[2]["balance"] == 0  # savings_amount = 0 and respected in normal mode
    assert (
        updated_moneyboxes[3]["balance"] == 10
    )  # savings_target=None, but respected savings_amount=10
