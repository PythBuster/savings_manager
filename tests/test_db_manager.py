"""All db_manager and db core tests are located here."""
from datetime import datetime

import pytest
from fastapi.encoders import jsonable_encoder

from src.custom_types import DBSettings
from src.db import core
from src.db.db_manager import DBManager
from src.db.exceptions import (
    BalanceResultIsNegativeError,
    ColumnDoesNotExistError,
    MoneyboxNameExistError,
    MoneyboxNotFoundError,
    NegativeAmountError,
    NegativeTransferAmountError,
)
from src.db.models import Moneybox
from tests.conftest import TEST_DB_DRIVER


@pytest.mark.first
async def test_if_test_db_in_memory_is_used(db_manager: DBManager) -> None:
    assert db_manager.db_connection_string == f"{TEST_DB_DRIVER}:///:memory:"


@pytest.mark.dependency
async def test_create_db_manager_with_engine_args(db_settings_1: DBSettings) -> None:
    db_manager = DBManager(db_settings=db_settings_1, engine_args={"echo": True})
    assert db_manager is not None

    db_manager = DBManager(db_settings=db_settings_1, engine_args=None)
    assert db_manager is not None


@pytest.mark.dependency
async def test_add_moneybox(db_manager: DBManager) -> None:
    # moneybox 1
    moneybox_data_1 = {"name": "Test Box 1"}
    result_moneybox_data_1 = await db_manager.add_moneybox(moneybox_data=moneybox_data_1)

    assert isinstance(result_moneybox_data_1["created_at"], datetime)
    assert result_moneybox_data_1["modified_at"] is None

    del result_moneybox_data_1["created_at"]
    del result_moneybox_data_1["modified_at"]

    expected_moneybox_data = moneybox_data_1 | {"id": 1, "balance": 0}
    assert result_moneybox_data_1 == expected_moneybox_data

    with pytest.raises(MoneyboxNameExistError) as ex_info:
        await db_manager.add_moneybox(moneybox_data=moneybox_data_1)

    assert "Moneybox name 'Test Box 1' already exists" in ex_info.value.args[0]

    # moneybox 2
    moneybox_data_2 = {"name": "Test Box 2"}
    result_moneybox_data_2 = await db_manager.add_moneybox(moneybox_data=moneybox_data_2)

    assert isinstance(result_moneybox_data_2["created_at"], datetime)
    assert result_moneybox_data_2["modified_at"] is None

    del result_moneybox_data_2["created_at"]
    del result_moneybox_data_2["modified_at"]

    expected_moneybox_data = moneybox_data_2 | {"id": 2, "balance": 0}
    assert result_moneybox_data_2 == expected_moneybox_data

    with pytest.raises(MoneyboxNameExistError) as ex_info:
        await db_manager.add_moneybox(moneybox_data=moneybox_data_2)

    assert "Moneybox name 'Test Box 2' already exists" in ex_info.value.args[0]

    # moneybox 3
    moneybox_data_3: dict[str, str | int] = {"name": "Test Box 3", "balance": 333}
    result_moneybox_data_3 = await db_manager.add_moneybox(moneybox_data=moneybox_data_3)

    assert isinstance(result_moneybox_data_3["created_at"], datetime)
    assert result_moneybox_data_3["modified_at"] is None

    del result_moneybox_data_3["created_at"]
    del result_moneybox_data_3["modified_at"]

    expected_moneybox_data = moneybox_data_3 | {"id": 3, "balance": 333}
    assert result_moneybox_data_3 == expected_moneybox_data

    with pytest.raises(MoneyboxNameExistError) as ex_info:
        await db_manager.add_moneybox(moneybox_data=moneybox_data_3)

    assert "Moneybox name 'Test Box 3' already exists" in ex_info.value.args[0]

    # moneybox 4
    moneybox_data_4 = {"name": "Test Box 4"}
    result_moneybox_data_4 = await db_manager.add_moneybox(moneybox_data=moneybox_data_4)

    assert isinstance(result_moneybox_data_4["created_at"], datetime)
    assert result_moneybox_data_4["modified_at"] is None

    del result_moneybox_data_4["created_at"]
    del result_moneybox_data_4["modified_at"]

    expected_moneybox_data = moneybox_data_4 | {"id": 4, "balance": 0}
    assert result_moneybox_data_4 == expected_moneybox_data

    with pytest.raises(MoneyboxNameExistError) as ex_info:
        await db_manager.add_moneybox(moneybox_data=moneybox_data_4)

    assert "Moneybox name 'Test Box 4' already exists" in ex_info.value.args[0]


@pytest.mark.dependency(depends=["test_add_moneybox"])
async def test_update_moneybox(db_manager: DBManager) -> None:
    moneybox_data = {"name": "Test Box 1 - Updated"}
    result_moneybox_data = await db_manager.update_moneybox(
        moneybox_id=1,
        moneybox_data=moneybox_data,
    )

    assert isinstance(result_moneybox_data["created_at"], datetime)
    assert isinstance(result_moneybox_data["modified_at"], datetime)

    del result_moneybox_data["created_at"]
    del result_moneybox_data["modified_at"]

    expected_moneybox_data = moneybox_data | {"id": 1, "balance": 0}
    assert result_moneybox_data == expected_moneybox_data

    non_existing_moneybox_ids = [-42, -1, 0, 5, 1654856415456]
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
        assert ex_info.value.record_id == moneybox_id


@pytest.mark.dependency(depends=["test_update_moneybox"])
async def test_get_moneybox(db_manager: DBManager) -> None:
    result_moneybox_data = await db_manager.get_moneybox(moneybox_id=1)
    expected_moneybox_data = {"id": 1, "balance": 0, "name": "Test Box 1 - Updated"}
    assert result_moneybox_data == expected_moneybox_data

    non_existing_moneybox_ids = [-42, -1, 0, 5, 1654856415456]
    for moneybox_id in non_existing_moneybox_ids:
        with pytest.raises(MoneyboxNotFoundError) as ex_info:
            await db_manager.get_moneybox(moneybox_id=moneybox_id)

        assert f"Moneybox with id {moneybox_id} does not exist." == ex_info.value.message
        assert isinstance(ex_info.value.details, dict)
        assert jsonable_encoder(ex_info.value.details) is not None
        assert ex_info.value.details["id"] == moneybox_id
        assert ex_info.value.record_id == moneybox_id


@pytest.mark.dependency(depends=["test_get_moneybox"])
async def test_core_exists_instance__moneybox_name(db_manager: DBManager) -> None:
    result_moneybox_data = await db_manager.get_moneybox(moneybox_id=1)
    moneybox_name = result_moneybox_data["name"]

    existing = await core.exists_instance(
        async_session=db_manager.async_session,
        orm_model=Moneybox,  # type: ignore
        values={"name": moneybox_name},
    )
    assert existing

    non_existing = await core.exists_instance(
        async_session=db_manager.async_session,
        orm_model=Moneybox,  # type: ignore
        values={"name": "nope, no no no"},
    )
    assert not non_existing

    with pytest.raises(ColumnDoesNotExistError) as ex_info:
        await core.exists_instance(
            async_session=db_manager.async_session,
            orm_model=Moneybox,  # type: ignore
            values={"no_existing_field": "BLABLA"},
        )

    assert ex_info.value.args[0] == "Table 'Moneybox' has no column named 'no_existing_field'"
    assert ex_info.value.table == "Moneybox"
    assert ex_info.value.column == "no_existing_field"


@pytest.mark.dependency(depends=["test_add_moneybox"], session="scope")
async def test_delete_moneybox(db_manager: DBManager) -> None:
    assert await db_manager.delete_moneybox(moneybox_id=2) is None  # type: ignore

    non_existing_moneybox_ids = [-42, -1, 0, 2, 1654856415456]
    for moneybox_id in non_existing_moneybox_ids:
        with pytest.raises(MoneyboxNotFoundError) as ex_info:
            await db_manager.delete_moneybox(moneybox_id=moneybox_id)

        assert f"Moneybox with id {moneybox_id} does not exist." == ex_info.value.message
        assert isinstance(ex_info.value.details, dict)
        assert jsonable_encoder(ex_info.value.details) is not None
        assert ex_info.value.details["id"] == moneybox_id
        assert ex_info.value.record_id == moneybox_id


@pytest.mark.dependency(depends=["test_add_moneybox"])
async def test_add_balance_to_moneybox(db_manager: DBManager) -> None:
    moneybox_data = await db_manager.get_moneybox(moneybox_id=1)

    result_moneybox_data_1 = await db_manager.add_balance(
        moneybox_id=1,
        balance=0,
    )
    assert moneybox_data == result_moneybox_data_1

    result_moneybox_data_2 = await db_manager.add_balance(
        moneybox_id=1,
        balance=10,
    )
    moneybox_data["balance"] += 10
    assert moneybox_data == result_moneybox_data_2

    with pytest.raises(NegativeAmountError) as ex_info:
        await db_manager.add_balance(
            moneybox_id=1,
            balance=-1,
        )

    assert "Can't add or sub negative balance '-1' to Moneybox '1'." == ex_info.value.message
    assert isinstance(ex_info.value.details, dict)
    assert len(ex_info.value.details) == 2
    assert ex_info.value.details["id"] == 1
    assert ex_info.value.details["balance"] == -1
    assert ex_info.value.record_id == 1


@pytest.mark.dependency(depends=["test_add_balance_to_moneybox"])
async def test_sub_balance_to_moneybox(db_manager: DBManager) -> None:
    moneybox_data = await db_manager.get_moneybox(moneybox_id=1)

    result_moneybox_data_1 = await db_manager.sub_amount(
        moneybox_id=1,
        amount=0,
    )
    assert moneybox_data == result_moneybox_data_1

    result_moneybox_data_2 = await db_manager.sub_amount(
        moneybox_id=1,
        amount=10,
    )
    moneybox_data["balance"] -= 10
    assert moneybox_data == result_moneybox_data_2

    with pytest.raises(NegativeAmountError) as ex_info:
        await db_manager.sub_amount(
            moneybox_id=1,
            amount=-1,
        )

    assert "Can't add or sub negative balance '-1' to Moneybox '1'." == ex_info.value.message
    assert isinstance(ex_info.value.details, dict)
    assert len(ex_info.value.details) == 2
    assert ex_info.value.details["id"] == 1
    assert ex_info.value.details["balance"] == -1
    assert ex_info.value.record_id == 1

    with pytest.raises(BalanceResultIsNegativeError) as ex_info:
        await db_manager.sub_amount(
            moneybox_id=1,
            amount=1000,
        )

    assert (
        "Can't sub balance '1000' from Moneybox '1'. Not enough balance to sub."
        == ex_info.value.message
    )
    assert isinstance(ex_info.value.details, dict)
    assert len(ex_info.value.details) == 2
    assert ex_info.value.details["id"] == 1
    assert ex_info.value.details["balance"] == 1000
    assert ex_info.value.record_id == 1


@pytest.mark.dependency(depends=["test_sub_balance_to_moneybox"])
async def test_transfer_balance(db_manager: DBManager) -> None:
    from_moneybox_data = await db_manager.get_moneybox(moneybox_id=3)
    to_moneybox_data = await db_manager.get_moneybox(moneybox_id=1)

    await db_manager.transfer_amount(
        from_moneybox_id=from_moneybox_data["id"],
        to_moneybox_id=to_moneybox_data["id"],
        amount=33,
    )

    new_from_moneybox_data = await db_manager.get_moneybox(moneybox_id=3)
    new_to_moneybox_data = await db_manager.get_moneybox(moneybox_id=1)

    assert from_moneybox_data["balance"] - 33 == new_from_moneybox_data["balance"]
    assert to_moneybox_data["balance"] + 33 == new_to_moneybox_data["balance"]

    with pytest.raises(NegativeTransferAmountError) as ex_info:
        await db_manager.transfer_amount(
            from_moneybox_id=from_moneybox_data["id"],
            to_moneybox_id=to_moneybox_data["id"],
            amount=-1,
        )

    assert (
        f"Can't transfer balance from moneybox '{from_moneybox_data['id']}' "
        f" to '{to_moneybox_data['id']}'. Balance to transfer is negative: -1."
    ) == ex_info.value.message

    with pytest.raises(MoneyboxNotFoundError):
        await db_manager.transfer_amount(
            from_moneybox_id=42,
            to_moneybox_id=to_moneybox_data["id"],
            amount=10,
        )

    with pytest.raises(MoneyboxNotFoundError):
        await db_manager.transfer_amount(
            from_moneybox_id=from_moneybox_data["id"],
            to_moneybox_id=42,
            amount=10,
        )

    with pytest.raises(BalanceResultIsNegativeError) as ex_info:
        await db_manager.transfer_amount(
            from_moneybox_id=from_moneybox_data["id"],
            to_moneybox_id=to_moneybox_data["id"],
            amount=1_000,
        )

    expected_exception_message = (
        f"Can't sub balance '1000' from Moneybox '{from_moneybox_data['id']}'. "
        "Not enough balance to sub."
    )
    assert ex_info.value.message == expected_exception_message
