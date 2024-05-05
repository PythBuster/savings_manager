"""All db_manager and db core tests are located here."""

from datetime import datetime

import pytest
from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError

from src.custom_types import DBSettings, TransactionTrigger, TransactionType
from src.data_classes.requests import (
    DepositTransactionModel,
    TransferTransactionModel,
    WithdrawTransactionModel,
)
from src.db import core
from src.db.db_manager import DBManager
from src.db.exceptions import (
    BalanceResultIsNegativeError,
    ColumnDoesNotExistError,
    MoneyboxNameExistError,
    MoneyboxNotFoundError,
    NonPositiveAmountError,
    NonPositiveTransferAmountError,
    TransferEqualMoneyboxError,
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

    assert (
        "Creation Error: Please choose another name, 'Test Box 1' "
        "is already in use (case insensitive)."
    ) in ex_info.value.args[0]

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

    assert (
        "Creation Error: Please choose another name, 'Test Box 2' "
        "is already in use (case insensitive)."
    ) in ex_info.value.args[0]

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

    assert (
        "Creation Error: Please choose another name, 'Test Box 3' "
        "is already in use (case insensitive)."
    ) in ex_info.value.args[0]

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

    assert (
        "Creation Error: Please choose another name, 'Test Box 4'"
        " is already in use (case insensitive)."
    ) in ex_info.value.args[0]


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

    moneybox_data["name"] = "new"
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
    assert isinstance(result_moneybox_data["created_at"], datetime)
    assert isinstance(result_moneybox_data["modified_at"], datetime)
    del result_moneybox_data["created_at"]
    del result_moneybox_data["modified_at"]

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
        case_insensitive=True,
    )
    assert existing

    non_existing = await core.exists_instance(
        async_session=db_manager.async_session,
        orm_model=Moneybox,  # type: ignore
        values={"name": "nope, no no no"},
        case_insensitive=True,
    )
    assert not non_existing

    with pytest.raises(ColumnDoesNotExistError) as ex_info:
        await core.exists_instance(
            async_session=db_manager.async_session,
            orm_model=Moneybox,  # type: ignore
            values={"no_existing_field": "BLABLA"},
            case_insensitive=True,
        )

    assert ex_info.value.args[0] == "Table 'Moneybox' has no column named 'no_existing_field'"
    assert ex_info.value.table == "Moneybox"
    assert ex_info.value.column == "no_existing_field"


@pytest.mark.dependency(depends=["test_add_moneybox"], session="scope")
async def test_delete_moneybox(db_manager: DBManager) -> None:
    assert await db_manager.delete_moneybox(moneybox_id=2) is None  # type: ignore

    non_existing_moneybox_ids = [-42, -1, 0, 1654856415456]
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
    del moneybox_data["created_at"]
    del moneybox_data["modified_at"]

    deposit_transaction_1 = DepositTransactionModel(
        amount=1,
        description="Bonus.",
    )
    result_moneybox_data_1 = await db_manager.add_amount(
        moneybox_id=1,
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

    deposit_transaction_2 = DepositTransactionModel(
        amount=10,
        description="Bonus.",
    )
    result_moneybox_data_2 = await db_manager.add_amount(
        moneybox_id=1,
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
    transaction_logs = await db_manager.get_transaction_logs(moneybox_id=1)

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
        "moneybox_id": 1,
    }
    expected_dict_2 = {
        "description": "Bonus.",
        "transaction_type": TransactionType.DIRECT,
        "transaction_trigger": TransactionTrigger.MANUALLY,
        "amount": 10,
        "balance": 11,
        "counterparty_moneybox_id": None,
        "counterparty_moneybox_name": None,
        "moneybox_id": 1,
    }

    assert len(transaction_logs) == 2
    assert transaction_logs[0] == expected_dict_1
    assert transaction_logs[1] == expected_dict_2

    # expected exception tests
    with pytest.raises(ValidationError):
        await db_manager.add_amount(
            moneybox_id=1,
            deposit_transaction_data=DepositTransactionModel(
                amount=0,
                description="Bonus.",
            ).model_dump(),
            transaction_type=TransactionType.DIRECT,
            transaction_trigger=TransactionTrigger.MANUALLY,
        )

    with pytest.raises(NonPositiveAmountError) as ex_info:
        await db_manager.add_amount(
            moneybox_id=1,
            deposit_transaction_data={
                "amount": 0,
                "description": "Bonus.",
            },
            transaction_type=TransactionType.DIRECT,
            transaction_trigger=TransactionTrigger.MANUALLY,
        )

    assert ex_info.value.message == "Can't add or sub amount less than 1 '0' to Moneybox '1'."
    assert ex_info.value.details == {"amount": 0, "id": 1}
    assert ex_info.value.record_id == 1

    with pytest.raises(NonPositiveAmountError) as ex_info:
        await db_manager.add_amount(
            moneybox_id=2,
            deposit_transaction_data={"amount": -1, "description": "Bonus."},
            transaction_type=TransactionType.DIRECT,
            transaction_trigger=TransactionTrigger.MANUALLY,
        )

    assert ex_info.value.message == "Can't add or sub amount less than 1 '-1' to Moneybox '2'."
    assert ex_info.value.details == {"amount": -1, "id": 2}
    assert ex_info.value.record_id == 2


@pytest.mark.dependency(depends=["test_add_balance_to_moneybox"])
async def test_sub_balance_to_moneybox(db_manager: DBManager) -> None:
    moneybox_data = await db_manager.get_moneybox(moneybox_id=1)
    del moneybox_data["created_at"]
    del moneybox_data["modified_at"]

    withdraw_transaction_1 = WithdrawTransactionModel(amount=1)
    result_moneybox_data_1 = await db_manager.sub_amount(
        moneybox_id=1,
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

    withdraw_transaction_2 = WithdrawTransactionModel(
        amount=10,
    )
    result_moneybox_data_2 = await db_manager.sub_amount(
        moneybox_id=1,
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
    transaction_logs = await db_manager.get_transaction_logs(moneybox_id=1)

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
        "moneybox_id": 1,
    }

    expected_withdraw_dict_2 = {
        "description": "",
        "transaction_type": TransactionType.DIRECT,
        "transaction_trigger": TransactionTrigger.MANUALLY,
        "amount": -10,
        "balance": 0,
        "counterparty_moneybox_id": None,
        "counterparty_moneybox_name": None,
        "moneybox_id": 1,
    }

    assert len(transaction_logs) == 4
    assert transaction_logs[2] == expected_withdraw_dict_1
    assert transaction_logs[3] == expected_withdraw_dict_2

    # expected exception tests
    with pytest.raises(ValidationError):
        await db_manager.sub_amount(
            moneybox_id=1,
            withdraw_transaction_data=WithdrawTransactionModel(amount=0).model_dump(),
            transaction_type=TransactionType.DIRECT,
            transaction_trigger=TransactionTrigger.MANUALLY,
        )

    withdraw_transaction_3 = WithdrawTransactionModel(
        amount=1000,
    )

    with pytest.raises(BalanceResultIsNegativeError) as ex_info:
        await db_manager.sub_amount(
            moneybox_id=1,
            withdraw_transaction_data=withdraw_transaction_3.model_dump(),
            transaction_type=TransactionType.DIRECT,
            transaction_trigger=TransactionTrigger.MANUALLY,
        )

    assert (
        "Can't sub amount '1000' from Moneybox '1'. Not enough balance to sub."
        == ex_info.value.message
    )
    assert isinstance(ex_info.value.details, dict)
    assert len(ex_info.value.details) == 2
    assert ex_info.value.details["id"] == 1
    assert ex_info.value.details["amount"] == 1000
    assert ex_info.value.record_id == 1

    with pytest.raises(NonPositiveAmountError) as ex_info:
        await db_manager.sub_amount(
            moneybox_id=1,
            withdraw_transaction_data={"amount": 0},
            transaction_type=TransactionType.DIRECT,
            transaction_trigger=TransactionTrigger.MANUALLY,
        )

    assert ex_info.value.message == "Can't add or sub amount less than 1 '0' to Moneybox '1'."
    assert ex_info.value.details == {"amount": 0, "id": 1}
    assert ex_info.value.record_id == 1

    with pytest.raises(NonPositiveAmountError) as ex_info:
        await db_manager.sub_amount(
            moneybox_id=2,
            withdraw_transaction_data={
                "amount": -1,
            },
            transaction_type=TransactionType.DIRECT,
            transaction_trigger=TransactionTrigger.MANUALLY,
        )

    assert ex_info.value.message == "Can't add or sub amount less than 1 '-1' to Moneybox '2'."
    assert ex_info.value.details == {"amount": -1, "id": 2}
    assert ex_info.value.record_id == 2


@pytest.mark.dependency(depends=["test_sub_balance_to_moneybox"])
async def test_transfer_amount(db_manager: DBManager) -> None:
    from_moneybox_data = await db_manager.get_moneybox(moneybox_id=3)
    to_moneybox_data = await db_manager.get_moneybox(moneybox_id=1)

    transfer_transaction_1 = TransferTransactionModel(
        to_moneybox_id=to_moneybox_data["id"],
        amount=33,
    )

    await db_manager.transfer_amount(
        from_moneybox_id=from_moneybox_data["id"],
        transfer_transaction_data=transfer_transaction_1.model_dump(),
        transaction_type=TransactionType.DIRECT,
        transaction_trigger=TransactionTrigger.MANUALLY,
    )

    new_from_moneybox_data = await db_manager.get_moneybox(moneybox_id=3)
    new_to_moneybox_data = await db_manager.get_moneybox(moneybox_id=1)

    assert from_moneybox_data["balance"] - 33 == new_from_moneybox_data["balance"]
    assert to_moneybox_data["balance"] + 33 == new_to_moneybox_data["balance"]

    # test sub transaction logs
    transaction_logs_moneybox_1 = await db_manager.get_transaction_logs(moneybox_id=1)
    transaction_logs_moneybox_3 = await db_manager.get_transaction_logs(moneybox_id=3)

    for transaction_log in transaction_logs_moneybox_1:
        del transaction_log["created_at"]
        del transaction_log["id"]

    for transaction_log in transaction_logs_moneybox_3:
        del transaction_log["created_at"]
        del transaction_log["id"]

    expected_transfer_dict_moneybox_1 = {
        "description": "",
        "transaction_type": TransactionType.DIRECT,
        "transaction_trigger": TransactionTrigger.MANUALLY,
        "amount": 33,
        "balance": 33,
        "counterparty_moneybox_id": 3,
        "moneybox_id": 1,
        "counterparty_moneybox_name": "Test Box 3",
    }
    expected_transfer_dict_moneybox_3 = {
        "description": "",
        "transaction_type": TransactionType.DIRECT,
        "transaction_trigger": TransactionTrigger.MANUALLY,
        "amount": -33,
        "balance": 300,
        "counterparty_moneybox_id": 1,
        "moneybox_id": 3,
        "counterparty_moneybox_name": "Test Box 1 - Updated",
    }

    assert len(transaction_logs_moneybox_1) == 5
    assert len(transaction_logs_moneybox_3) == 1
    assert expected_transfer_dict_moneybox_1 == transaction_logs_moneybox_1[-1]
    assert expected_transfer_dict_moneybox_3 == transaction_logs_moneybox_3[-1]

    # expected exception tests
    with pytest.raises(ValidationError):
        await db_manager.transfer_amount(
            from_moneybox_id=from_moneybox_data["id"],
            transfer_transaction_data=TransferTransactionModel(
                to_moneybox_id=to_moneybox_data["id"],
                amount=0,
            ).model_dump(),
            transaction_type=TransactionType.DIRECT,
            transaction_trigger=TransactionTrigger.MANUALLY,
        )

    with pytest.raises(MoneyboxNotFoundError):
        await db_manager.transfer_amount(
            from_moneybox_id=42,
            transfer_transaction_data=TransferTransactionModel(
                to_moneybox_id=to_moneybox_data["id"],
                amount=10,
            ).model_dump(),
            transaction_type=TransactionType.DIRECT,
            transaction_trigger=TransactionTrigger.MANUALLY,
        )

    with pytest.raises(MoneyboxNotFoundError):
        await db_manager.transfer_amount(
            from_moneybox_id=from_moneybox_data["id"],
            transfer_transaction_data=TransferTransactionModel(
                to_moneybox_id=41,
                amount=10,
            ).model_dump(),
            transaction_type=TransactionType.DIRECT,
            transaction_trigger=TransactionTrigger.MANUALLY,
        )

    with pytest.raises(BalanceResultIsNegativeError) as ex_info:
        await db_manager.transfer_amount(
            from_moneybox_id=from_moneybox_data["id"],
            transfer_transaction_data=TransferTransactionModel(
                to_moneybox_id=to_moneybox_data["id"],
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

    with pytest.raises(NonPositiveTransferAmountError) as ex_info:
        await db_manager.transfer_amount(
            from_moneybox_id=1,
            transfer_transaction_data={
                "to_moneybox_id": 2,
                "amount": 0,
            },
            transaction_type=TransactionType.DIRECT,
            transaction_trigger=TransactionTrigger.MANUALLY,
        )

    assert ex_info.value.message == (
        "Can't transfer amount from moneybox '1'  to '2'. "
        "Amount to transfer has to be greater than 0: amount=0."
    )
    assert ex_info.value.details == {"amount": 0, "from_moneybox_id": 1, "to_moneybox_id": 2}

    with pytest.raises(NonPositiveTransferAmountError) as ex_info:
        await db_manager.transfer_amount(
            from_moneybox_id=1,
            transfer_transaction_data={
                "to_moneybox_id": 2,
                "amount": 0,
                "description": "Bonus.",
            },
            transaction_type=TransactionType.DIRECT,
            transaction_trigger=TransactionTrigger.MANUALLY,
        )

    assert ex_info.value.message == (
        "Can't transfer amount from moneybox '1'  to '2'. "
        "Amount to transfer has to be greater than 0: amount=0."
    )
    assert ex_info.value.details == {"amount": 0, "from_moneybox_id": 1, "to_moneybox_id": 2}

    with pytest.raises(TransferEqualMoneyboxError) as ex_info:
        await db_manager.transfer_amount(
            from_moneybox_id=1,
            transfer_transaction_data={
                "to_moneybox_id": 1,
                "amount": 123,
                "description": "Bonus.",
            },
            transaction_type=TransactionType.DIRECT,
            transaction_trigger=TransactionTrigger.MANUALLY,
        )

    assert ex_info.value.message == "Can't transfer within the same moneybox"
    assert ex_info.value.details == {"amount": 123, "from_moneybox_id": 1, "to_moneybox_id": 1}


@pytest.mark.dependency(depends=["test_sub_balance_to_moneybox"])
async def test_get_transactionslogs_with_counterparty_to_deleted_moneybox(
    db_manager: DBManager,
) -> None:
    # moneybox 4
    moneybox_data_4 = {"name": "4-Test Box"}
    result_moneybox_data_4 = await db_manager.add_moneybox(moneybox_data=moneybox_data_4)

    # moneybox 5
    moneybox_data_5 = {"name": "5-Test Box"}
    result_moneybox_data_5 = await db_manager.add_moneybox(moneybox_data=moneybox_data_5)

    deposit_transaction = DepositTransactionModel(
        amount=100,
        description="Bonus.",
    )
    await db_manager.add_amount(
        moneybox_id=result_moneybox_data_4["id"],
        deposit_transaction_data=deposit_transaction.model_dump(),
        transaction_type=TransactionType.DIRECT,
        transaction_trigger=TransactionTrigger.MANUALLY,
    )

    transfer_transaction = TransferTransactionModel(
        to_moneybox_id=result_moneybox_data_5["id"],
        amount=20,
    )

    await db_manager.transfer_amount(
        from_moneybox_id=result_moneybox_data_4["id"],
        transfer_transaction_data=transfer_transaction.model_dump(),
        transaction_type=TransactionType.DIRECT,
        transaction_trigger=TransactionTrigger.MANUALLY,
    )

    withdraw_transaction = WithdrawTransactionModel(amount=20)
    await db_manager.sub_amount(
        moneybox_id=result_moneybox_data_5["id"],
        withdraw_transaction_data=withdraw_transaction.model_dump(),
        transaction_type=TransactionType.DIRECT,
        transaction_trigger=TransactionTrigger.MANUALLY,
    )

    await db_manager.delete_moneybox(result_moneybox_data_5["id"])

    # should able to get transaction logs without getting an exception
    assert await db_manager.get_transaction_logs(result_moneybox_data_4["id"])

    withdraw_transaction = WithdrawTransactionModel(amount=80)
    await db_manager.sub_amount(
        moneybox_id=result_moneybox_data_4["id"],
        withdraw_transaction_data=withdraw_transaction.model_dump(),
        transaction_type=TransactionType.DIRECT,
        transaction_trigger=TransactionTrigger.MANUALLY,
    )

    await db_manager.delete_moneybox(result_moneybox_data_4["id"])
