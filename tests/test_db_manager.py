"""All db_manager tests are located here."""

import pytest
import sqlalchemy
from fastapi.encoders import jsonable_encoder

from src.db.db_manager import DBManager
from src.db.exceptions import MoneyboxNotFoundError
from tests.conftest import TEST_DB_DRIVER


@pytest.mark.first
async def test_if_test_db_in_memory_is_used(db_manager: DBManager) -> None:
    assert db_manager.db_connection_string == f"{TEST_DB_DRIVER}://"


@pytest.mark.asyncio
@pytest.mark.dependency
async def test_add_moneybox(db_manager: DBManager) -> None:
    moneybox_data = {"name": "Test Box 1"}
    result_moneybox_data = await db_manager.add_moneybox(moneybox_data=moneybox_data)
    expected_moneybox_data = moneybox_data | {"id": 1, "balance": 0}
    assert result_moneybox_data == expected_moneybox_data

    with pytest.raises(sqlalchemy.exc.IntegrityError) as excinfo:
        await db_manager.add_moneybox(moneybox_data=moneybox_data)

    assert "UNIQUE constraint failed: moneybox.name" in excinfo.value.args[0]


@pytest.mark.asyncio
@pytest.mark.dependency(depends=["test_add_moneybox"])
async def test_delete_moneybox(db_manager: DBManager) -> None:
    assert await db_manager.delete_moneybox(moneybox_id=1) == None

    non_existing_moneybox_ids = [-42, -1, 0, 2, 1654856415456]
    for moneybox_id in non_existing_moneybox_ids:
        with pytest.raises(MoneyboxNotFoundError) as excinfo:
            await db_manager.delete_moneybox(moneybox_id=moneybox_id)

        assert f"Moneybox with id {moneybox_id} does not exist." == excinfo.value.message
        assert isinstance(excinfo.value.details, dict)
        assert jsonable_encoder(excinfo.value.details) is not None
        assert excinfo.value.details["id"] == moneybox_id
        assert excinfo.value.details["message"] == excinfo.value.message
        assert excinfo.value.record_id == moneybox_id
