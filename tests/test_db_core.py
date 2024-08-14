"""All db core tests are located here."""

from src.db.core import create_instance
from src.db.db_manager import DBManager
from src.db.models import Moneybox


async def test_create_instance(
    load_test_data: None,  # pylint: disable=unused-argument
    db_manager: DBManager,
) -> None:
    moneybox_data = {
        "id": 1,
        "name": "Test Box 1",
        "balance": 0,
        "priority": 1,
        "savings_amount": 0,
        "savings_target": None,
    }

    created_instance: Moneybox = await create_instance(
        async_session=db_manager.async_session,
        orm_model=Moneybox,  # type: ignore
        data=moneybox_data,
    )

    assert created_instance.name == "Test Box 1"
    assert created_instance.is_active is True
    assert created_instance.priority == 1
    assert created_instance.savings_amount == 0
    assert created_instance.savings_target is None
