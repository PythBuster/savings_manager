"""All db_manager tests are located here."""

import pytest

from src.db.db_manager import DBManager
from tests.conftest import TEST_DB_DRIVER


@pytest.mark.First
async def test_if_test_db_in_memory_is_used(db_manager: DBManager) -> None:
    assert db_manager.db_connection_string == f"{TEST_DB_DRIVER}://"


@pytest.mark.asyncio
async def test_add_moneybox(db_manager: DBManager) -> None:
    moneybox_data = {"name": "Test Box 1"}
    result_moneybox_data = await db_manager.add_moneybox(moneybox_data=moneybox_data)
    expected_moneybox_data = moneybox_data | {"id": 1, "balance": 0}

    assert result_moneybox_data == expected_moneybox_data
