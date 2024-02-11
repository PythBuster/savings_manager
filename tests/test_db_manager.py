"""All db_manager tests are located here."""

import pytest
import sqlalchemy
from fastapi.encoders import jsonable_encoder

from src.custom_types import DBSettings
from src.db.db_manager import DBManager
from src.db.exceptions import MoneyboxNotFoundError
from tests.conftest import TEST_DB_DRIVER


@pytest.mark.first
async def test_if_test_db_in_memory_is_used(db_manager: DBManager) -> None:
    assert db_manager.db_connection_string == f"{TEST_DB_DRIVER}://"


async def test_create_db_manager_with_engine_args(db_settings_1: DBSettings) -> None:
    db_manager = DBManager(db_settings=db_settings_1, engine_args={"echo": True})
    assert db_manager is not None

    db_manager = DBManager(db_settings=db_settings_1, engine_args=None)
    assert db_manager is not None


@pytest.mark.asyncio
@pytest.mark.dependency
async def test_add_moneybox(db_manager: DBManager) -> None:
    moneybox_data = {"name": "Test Box 1"}
    result_moneybox_data = await db_manager.add_moneybox(moneybox_data=moneybox_data)
    expected_moneybox_data = moneybox_data | {"id": 1, "balance": 0}
    assert result_moneybox_data == expected_moneybox_data

    with pytest.raises(sqlalchemy.exc.IntegrityError) as ex_info:
        await db_manager.add_moneybox(moneybox_data=moneybox_data)

    assert "UNIQUE constraint failed: moneybox.name" in ex_info.value.args[0]


@pytest.mark.asyncio
@pytest.mark.dependency(depends=["test_add_moneybox"])
async def test_update_moneybox(db_manager: DBManager) -> None:
    moneybox_data = {"name": "Test Box 2.0"}
    result_moneybox_data = await db_manager.update_moneybox(
        moneybox_id=1,
        moneybox_data=moneybox_data,
    )
    expected_moneybox_data = moneybox_data | {"id": 1, "balance": 0}
    assert result_moneybox_data == expected_moneybox_data

    non_existing_moneybox_ids = [-42, -1, 0, 2, 1654856415456]
    for moneybox_id in non_existing_moneybox_ids:
        with pytest.raises(MoneyboxNotFoundError) as ex_info:
            await db_manager.update_moneybox(
                moneybox_id=moneybox_id,
                moneybox_data=moneybox_data,
            )

        assert f"Moneybox with id {moneybox_id} does not exist." == ex_info.value.message
        assert isinstance(ex_info.value.details, dict)
        assert jsonable_encoder(ex_info.value.details) is not None
        assert ex_info.value.details["id"] == moneybox_id
        assert ex_info.value.details["message"] == ex_info.value.message
        assert ex_info.value.record_id == moneybox_id


@pytest.mark.asyncio
@pytest.mark.dependency(depends=["test_update_moneybox"])
async def test_get_moneybox(db_manager: DBManager) -> None:
    result_moneybox_data = await db_manager.get_moneybox(moneybox_id=1)
    expected_moneybox_data = {"id": 1, "balance": 0, "name": "Test Box 2.0"}
    assert result_moneybox_data == expected_moneybox_data

    non_existing_moneybox_ids = [-42, -1, 0, 2, 1654856415456]
    for moneybox_id in non_existing_moneybox_ids:
        with pytest.raises(MoneyboxNotFoundError) as ex_info:
            await db_manager.get_moneybox(moneybox_id=moneybox_id)

        assert f"Moneybox with id {moneybox_id} does not exist." == ex_info.value.message
        assert isinstance(ex_info.value.details, dict)
        assert jsonable_encoder(ex_info.value.details) is not None
        assert ex_info.value.details["id"] == moneybox_id
        assert ex_info.value.details["message"] == ex_info.value.message
        assert ex_info.value.record_id == moneybox_id


@pytest.mark.asyncio
@pytest.mark.dependency(depends=["test_add_moneybox"])
async def test_delete_moneybox(db_manager: DBManager) -> None:
    assert await db_manager.delete_moneybox(moneybox_id=1) is None  # type: ignore

    non_existing_moneybox_ids = [-42, -1, 0, 2, 1654856415456]
    for moneybox_id in non_existing_moneybox_ids:
        with pytest.raises(MoneyboxNotFoundError) as ex_info:
            await db_manager.delete_moneybox(moneybox_id=moneybox_id)

        assert f"Moneybox with id {moneybox_id} does not exist." == ex_info.value.message
        assert isinstance(ex_info.value.details, dict)
        assert jsonable_encoder(ex_info.value.details) is not None
        assert ex_info.value.details["id"] == moneybox_id
        assert ex_info.value.details["message"] == ex_info.value.message
        assert ex_info.value.record_id == moneybox_id
