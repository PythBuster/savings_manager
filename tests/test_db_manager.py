"""All db_manager tests are located here."""

from src.db.db_manager import DBManager


async def test_add_moneybox(db_manager: DBManager) -> None:
    moneybox_data = {"name": "Test box 1"}

    result_moneybox_data = await db_manager.add_moneybox(moneybox_data=moneybox_data)

    expected_moneybox_data = moneybox_data | {"id": 1, "balance": 0}
    assert result_moneybox_data == expected_moneybox_data
