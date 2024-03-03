"""All database definitions are located here."""

from typing import Any

from sqlalchemy import insert, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.custom_types import DBSettings, TransactionTrigger, TransactionType
from src.db.core import (
    create_instance,
    delete_instance,
    exists_instance,
    read_instance,
    read_instances,
    update_instance,
)
from src.db.exceptions import (
    BalanceResultIsNegativeError,
    MoneyboxNameExistError,
    MoneyboxNotFoundError,
    NegativeAmountError,
    NegativeTransferAmountError,
    TransferEqualMoneyboxError,
)
from src.db.models import Moneybox, Transaction
from src.utils import get_database_url


class DBManager:
    """All db manager logic are located here."""

    def __init__(self, db_settings: DBSettings, engine_args: dict[str, Any] | None = None) -> None:
        if engine_args is None:
            engine_args = {}

        self.db_settings = db_settings
        self.async_engine = create_async_engine(
            url=self.db_connection_string,
            **engine_args,
        )
        self.async_session = async_sessionmaker(
            bind=self.async_engine,
            expire_on_commit=False,
        )

    @property
    def db_connection_string(self) -> str:
        """Property to create a database connection string based on db driver.

        :return: A db connection string.
        :rtype: :class:`str`

        :raises: :class:`ValueError`: if self.db_settings.db_driver is not supported.
        """

        return get_database_url(db_settings=self.db_settings)

    async def get_moneyboxes(self) -> list[dict[str, Any]]:
        """DB Function to get all moneyboxes.


        :return: The requested moneybox data.
        :rtype: :class:`list[dict[str, Any]]`
        """

        moneyboxes = await read_instances(
            async_session=self.async_session,
            orm_model=Moneybox,  # type: ignore
        )

        return [moneybox.asdict() for moneybox in moneyboxes]

    async def get_moneybox(
        self,
        moneybox_id: int,
    ) -> dict[str, Any]:
        """DB Function to get a moneybox by moneybox_id.

        :param moneybox_id: The id of the moneybox.
        :type moneybox_id: :class:`int`
        :return: The requested moneybox data.
        :rtype: :class:`dict[str, Any]`

        :raises: :class:`MoneyboxNotFoundError`: if given moneybox_id
            was not found in database.
        """

        moneybox = await read_instance(
            async_session=self.async_session,
            orm_model=Moneybox,  # type: ignore
            record_id=moneybox_id,
        )

        if moneybox is None:
            raise MoneyboxNotFoundError(moneybox_id=moneybox_id)

        return moneybox.asdict()

    async def add_moneybox(self, moneybox_data: dict[str, Any]) -> dict[str, Any]:
        """DB Function to add a new moneybox into database.

        :param moneybox_data: The moneybox data.
        :type moneybox_data: :class:`dict[str, Any]`

        :return: The added moneybox data.
        :rtype: :class:`dict[str, Any]`
        """

        name_exist = await exists_instance(
            async_session=self.async_session,
            orm_model=Moneybox,  # type: ignore
            values={"name": moneybox_data["name"]},
        )

        if name_exist:
            raise MoneyboxNameExistError(name=moneybox_data["name"])

        moneybox = await create_instance(
            async_session=self.async_session,
            orm_model=Moneybox,  # type: ignore
            data=moneybox_data,
        )

        return moneybox.asdict()

    async def update_moneybox(
        self,
        moneybox_id: int,
        moneybox_data: dict[str, Any],
    ) -> dict[str, Any]:
        """DB Function to update a moneybox by moneybox_id.

        :param moneybox_id: The id of the moneybox.
        :type moneybox_id: :class:`int`
        :param moneybox_data: The moneybox data.
        :type moneybox_data: :class:`dict[str, Any]`

        :return: The updated moneybox data.
        :rtype: :class:`dict[str, Any]`

        :raises: :class:`MoneyboxNotFoundError`: if given moneybox_id
            was not found in database.
        """

        moneybox = await update_instance(
            async_session=self.async_session,
            orm_model=Moneybox,  # type: ignore
            record_id=moneybox_id,
            data=moneybox_data,
        )

        if moneybox is None:
            raise MoneyboxNotFoundError(moneybox_id=moneybox_id)

        return moneybox.asdict()

    async def delete_moneybox(self, moneybox_id: int) -> None:
        """DB Function to delete a moneybox by given id.

        :param moneybox_id: The id of the moneybox.
        :type moneybox_id: :class:`int`

        :raises: :class:`MoneyboxNotFoundError`: if given moneybox_id
            was not found in database.
        """

        deleted_rows = await delete_instance(
            async_session=self.async_session,
            orm_model=Moneybox,  # type: ignore
            record_id=moneybox_id,
        )

        if deleted_rows == 0:
            raise MoneyboxNotFoundError(moneybox_id=moneybox_id)

    # TODO refactor: add_amount and  # pylint: disable=fixme
    #  sub_amount are almost identical, combine in one function?
    async def add_amount(
        self,
        moneybox_id: int,
        deposit_transaction_data: dict[str, Any],
    ) -> dict[str, Any]:
        """DB Function to add amount to moneybox by moneybox_id.

        :param moneybox_id: The id of the moneybox.
        :type moneybox_id: :class:`int`
        :param deposit_transaction_data: The deposit transaction data.
        :type deposit_transaction_data: :class:`dict[str, Any]`

        :return: The updated moneybox data.
        :rtype: :class:`dict[str, Any]`

        :raises: :class:`MoneyboxNotFoundError`: if given moneybox_id
                    was not found in database.
                 :class:`NegativeAmountError`: if balance to add is negative.
        """

        amount: int = deposit_transaction_data["deposit_data"]["amount"]

        if amount < 0:
            raise NegativeAmountError(moneybox_id=moneybox_id, amount=amount)

        moneybox = await read_instance(
            async_session=self.async_session,
            orm_model=Moneybox,  # type: ignore
            record_id=moneybox_id,
        )

        if moneybox is None:
            raise NegativeAmountError(moneybox_id=moneybox_id, amount=amount)

        moneybox.balance += amount  # type: ignore

        async with self.async_session.begin() as session:
            updated_moneybox = await update_instance(
                async_session=session,
                orm_model=Moneybox,  # type: ignore
                record_id=moneybox_id,
                data=moneybox.asdict(),
            )

            # should not be possible to reach this block
            if updated_moneybox is None:
                raise MoneyboxNotFoundError(moneybox_id=moneybox_id)

            await self._add_transfer_log(
                moneybox_id=moneybox_id,
                description=deposit_transaction_data["transaction_data"]["description"],
                transaction_type=deposit_transaction_data["transaction_data"]["transaction_type"],
                transaction_trigger=deposit_transaction_data["transaction_data"][
                    "transaction_trigger"
                ],
                amount=amount,
                balance=updated_moneybox.balance,  # type: ignore
                session=session,
            )

        return updated_moneybox.asdict()

    async def sub_amount(  # pylint: disable=too-many-arguments
        self,
        moneybox_id: int,
        withdraw_transaction_data: dict[str, Any],
    ) -> dict[str, Any]:
        """DB Function to sub given amount from moneybox by moneybox_id.

        :param moneybox_id: The id of the moneybox.
        :type moneybox_id: :class:`int`
        :param withdraw_transaction_data: The withdrawal transaction data.
        :type withdraw_transaction_data: :class:`dict[str, Any]`
        :return: The updated moneybox data.
        :rtype: :class:`dict[str, Any]`

        :raises: :class:`MoneyboxNotFoundError`: if given moneybox_id
                    was not found in database.
                 :class:`NegativeAmountError`:
                    if balance to sub  is negative.
                 :class:`BalanceResultIsNegativeError`:
                    if result of withdraw is negative.
        """

        amount: int = withdraw_transaction_data["withdraw_data"]["amount"]

        if amount < 0:
            raise NegativeAmountError(moneybox_id=moneybox_id, amount=amount)

        moneybox = await read_instance(
            async_session=self.async_session,
            orm_model=Moneybox,  # type: ignore
            record_id=moneybox_id,
        )

        if moneybox is None:
            raise NegativeAmountError(moneybox_id=moneybox_id, amount=amount)

        moneybox.balance -= amount  # type: ignore

        if moneybox.balance < 0:  # type: ignore
            raise BalanceResultIsNegativeError(moneybox_id=moneybox_id, amount=amount)

        async with self.async_session.begin() as session:
            updated_moneybox = await update_instance(
                async_session=session,
                orm_model=Moneybox,  # type: ignore
                record_id=moneybox_id,
                data=moneybox.asdict(),
            )

            # should not be possible to reach this block
            if updated_moneybox is None:
                raise MoneyboxNotFoundError(moneybox_id=moneybox_id)

            await self._add_transfer_log(
                moneybox_id=moneybox_id,
                description=withdraw_transaction_data["transaction_data"]["description"],
                transaction_type=withdraw_transaction_data["transaction_data"]["transaction_type"],
                transaction_trigger=withdraw_transaction_data["transaction_data"][
                    "transaction_trigger"
                ],
                amount=-amount,  # negate, withdrawals need to be negative in log data
                balance=updated_moneybox.balance,  # type: ignore
                session=session,
            )

        return updated_moneybox.asdict()

    async def transfer_amount(
        self,
        from_moneybox_id: int,
        transfer_transaction_data: dict[str, Any],
    ) -> None:
        """DB Function to transfer `balance` from `from_moneybox_id`
        from `to_moneybox_id`.

        :param from_moneybox_id: The source id of the moneybox where the balance comes from.
        :type from_moneybox_id: :class:`int`
        :param transfer_transaction_data: The transfer transaction data.
        :type transfer_transaction_data: :class:`dict[str, Any]`

        :raises: :class:`NegativeTransferAmountError`:
                    if balance to transfer is negative.
                 :class:`BalanceResultIsNegativeError`:
                    if result of withdraws from_moneybox_id is negative.
                :class:`TransferEqualMoneyboxError`:
                    if transfer shall happen within the same moneybox.
        """

        to_moneybox_id: int = transfer_transaction_data["transfer_data"]["to_moneybox_id"]
        amount: int = transfer_transaction_data["transfer_data"]["amount"]

        if from_moneybox_id == to_moneybox_id:
            raise TransferEqualMoneyboxError(
                from_moneybox_id=from_moneybox_id,
                to_moneybox_id=to_moneybox_id,
                amount=amount,
            )

        if amount < 0:
            raise NegativeTransferAmountError(
                from_moneybox_id=from_moneybox_id,
                to_moneybox_id=transfer_transaction_data["transfer_data"]["to_moneybox_id"],
                amount=amount,
            )

        from_moneybox = await read_instance(
            async_session=self.async_session,
            orm_model=Moneybox,  # type: ignore
            record_id=from_moneybox_id,
        )

        if from_moneybox is None:
            raise MoneyboxNotFoundError(moneybox_id=from_moneybox_id)

        to_moneybox = await read_instance(
            async_session=self.async_session,
            orm_model=Moneybox,  # type: ignore
            record_id=to_moneybox_id,
        )

        if to_moneybox is None:
            raise MoneyboxNotFoundError(moneybox_id=to_moneybox_id)

        async with self.async_session.begin() as session:
            new_from_moneybox_data = {"balance": from_moneybox.balance - amount}  # type: ignore

            if new_from_moneybox_data["balance"] < 0:
                raise BalanceResultIsNegativeError(moneybox_id=from_moneybox_id, amount=amount)

            new_to_moneybox_data = {"balance": to_moneybox.balance + amount}  # type: ignore

            result_1 = await session.execute(
                update(Moneybox)
                .where(Moneybox.id == from_moneybox_id)
                .values(new_from_moneybox_data)
                .returning(Moneybox)
            )
            updated_from_moneybox = result_1.scalar_one()

            result_2 = await session.execute(
                update(Moneybox)
                .where(Moneybox.id == to_moneybox_id)
                .values(new_to_moneybox_data)
                .returning(Moneybox)
            )
            updated_to_moneybox = result_2.scalar_one()

            # log in `from_moneybox`instance (withdraw)
            await self._add_transfer_log(
                moneybox_id=from_moneybox_id,
                description=transfer_transaction_data["transaction_data"]["description"],
                transaction_type=transfer_transaction_data["transaction_data"]["transaction_type"],
                transaction_trigger=transfer_transaction_data["transaction_data"][
                    "transaction_trigger"
                ],
                amount=-amount,  # negate, withdrawals need to be negative in log data
                balance=updated_from_moneybox.balance,  # type: ignore
                session=session,
            )

            # log in `to_moneybox`instance (deposit)
            await self._add_transfer_log(
                moneybox_id=to_moneybox_id,
                description=transfer_transaction_data["transaction_data"]["description"],
                transaction_type=transfer_transaction_data["transaction_data"]["transaction_type"],
                transaction_trigger=transfer_transaction_data["transaction_data"][
                    "transaction_trigger"
                ],
                amount=amount,
                balance=updated_to_moneybox.balance,  # type: ignore
                session=session,
            )

    async def _add_transfer_log(  # pylint: disable=too-many-arguments
        self,
        moneybox_id: int,
        description: str,
        transaction_type: TransactionType,
        transaction_trigger: TransactionTrigger,
        amount: int,
        balance: int,
        session: AsyncSession,
        counterparty_moneybox_id: int | None = None,
    ) -> None:
        """DB Function to add transfer log to moneybox by moneybox_id.

        :param moneybox_id: The id of the moneybox.
        :type moneybox_id: :class:`int`
        :param description: The description of the transaction action.
        :type description: :class:`str`
        :param transaction_type: The type of the transaction, possible values:
            direct, distribution.
        :type transaction_type: :class:`TransactionType`
        :param transaction_trigger: The transaction trigger type, possible values:
            manually, automatically.
        :type transaction_trigger: :class:`TransactionTrigger`
        :param amount: The amount of the transaction, positive value = deposit,
            negative value = withdrawal.
        :type amount: :class:`int`
        :param balance: The balance of the moneybox at the time of the transaction.
        :type balance: :class:`ìnt`
        :param session: The current session of the db creation.
        :type session: :class:`AsyncSession`
        :param counterparty_moneybox_id: The counterparty moneybox id of the transaction,
            defaults to None.
        :type counterparty_moneybox_id: :class:`int` | :class:`None`
        """

        transaction_log_data = {
            "moneybox_id": moneybox_id,
            "description": description,
            "transaction_type": transaction_type,
            "transaction_trigger": transaction_trigger,
            "amount": amount,
            "balance": balance,
            "counterparty_moneybox_id": counterparty_moneybox_id,
        }

        stmt = insert(Transaction).values(transaction_log_data)
        await session.execute(stmt)
