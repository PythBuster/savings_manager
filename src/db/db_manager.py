"""All database definitions are located here."""

from datetime import datetime
from typing import Any, Hashable

from sqlalchemy import and_, desc, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import joinedload

from src.custom_types import DBSettings, TransactionTrigger, TransactionType
from src.db.core import (
    create_instance,
    deactivate_instance,
    read_instance,
    update_instance, read_instances,
)
from src.db.exceptions import (
    BalanceResultIsNegativeError,
    CreateInstanceError,
    DeleteInstanceError,
    HasBalanceError,
    MoneyboxNotFoundByNameError,
    MoneyboxNotFoundError,
    NonPositiveAmountError,
    OverflowMoneyboxCantBeDeletedError,
    OverflowMoneyboxCantBeUpdatedError,
    OverflowMoneyboxNotFoundError,
    TransferEqualMoneyboxError,
    UpdateInstanceError,
)
from src.db.models import Moneybox, MoneyboxNameHistory, Transaction
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
        only_active_instances: bool = True,
    ) -> dict[str, Any]:
        """DB Function to get a moneybox by moneybox_id.

        :param moneybox_id: The id of the moneybox.
        :type moneybox_id: :class:`int`
        :param only_active_instances: If True, only active moneyboxes will be
            returned, default to True.
        :type only_active_instances: :class:`bool`
        :return: The requested moneybox data.
        :rtype: :class:`dict[str, Any]`

        :raises: :class:`MoneyboxNotFoundError`: if given moneybox_id
            was not found in database.
        """

        moneybox = await read_instance(
            async_session=self.async_session,
            orm_model=Moneybox,  # type: ignore
            record_id=moneybox_id,
            only_active_instances=only_active_instances,
        )

        if moneybox is None:
            raise MoneyboxNotFoundError(moneybox_id=moneybox_id)

        return moneybox.asdict()

    async def _get_overflow_moneybox(self) -> Moneybox:
        """DB Function to get the overflow moneybox.

        There is only one overflow moneybox (special moneybox) which has the
        priority colum value of 0.
        Note: Only 'is_active' moneyboxes will be requested.

        :return: The overflow moneybox orm instance.
        :rtype: :class:`Moneybox`

        :raises: :class:`OverflowMoneyboxNotFoundError`: if there are no overflow moneybox in the
            database, missing moneybox with priority = 0.
        """

        stmt = select(Moneybox).where(and_(Moneybox.priority == 0, Moneybox.is_active.is_(True)))

        async with self.async_session() as session:
            result = await session.execute(stmt)

        moneybox = result.scalars().one_or_none()

        if moneybox is None:
            raise OverflowMoneyboxNotFoundError()

        return moneybox

    async def add_moneybox(self, moneybox_data: dict[str, Any]) -> dict[str, Any]:
        """DB Function to add a new moneybox into database.

        :param moneybox_data: The moneybox data.
        :type moneybox_data: :class:`dict[str, Any]`

        :return: The added moneybox data.
        :rtype: :class:`dict[str, Any]`
        """

        async with self.async_session.begin() as session:
            moneybox = await create_instance(
                async_session=session,
                orm_model=Moneybox,  # type: ignore
                data=moneybox_data,
            )

            if moneybox is None:
                raise CreateInstanceError(
                    record_id=None,
                    message="Failed to create moneybox.",
                    details=moneybox_data,
                )

            moneybox_name_history_data = {
                "name": moneybox.name,
                "moneybox_id": moneybox.id,
            }
            moneybox_name_history = await create_instance(
                async_session=session,
                orm_model=MoneyboxNameHistory,  # type: ignore
                data=moneybox_name_history_data,
            )

            if moneybox_name_history is None:
                raise CreateInstanceError(
                    record_id=None,
                    message="Failed to create moneybox name history.",
                    details=moneybox_name_history_data,
                )

        return moneybox.asdict()

    async def _create_moneybox_name_history(
        self,
        moneybox_id: int,
        name: str,
        session: AsyncSession,
    ) -> dict[str, Any]:
        """DB Function to create a moneybox history for a moneybox id.

        :param moneybox_id: The id of the moneybox.
        :type moneybox_id: :class:`int`
        :param name: The name of the moneybox.
        :type name: :class:`str`
        :param session: The current session of the db creation.
        :type session:: class:`AsyncSession`

        :return: The created moneybox history data.
        """

        moneybox_name_history = await create_instance(
            async_session=session,
            orm_model=MoneyboxNameHistory,  # type: ignore
            data={
                "moneybox_id": moneybox_id,
                "name": name,
            },
        )

        return moneybox_name_history.asdict()

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

        # get overflow moneybox and protect updating it
        _overflow_moneybox: Moneybox = await self._get_overflow_moneybox()

        if moneybox_id == _overflow_moneybox.id:
            raise OverflowMoneyboxCantBeUpdatedError(moneybox_id=_overflow_moneybox.id)

        async with self.async_session.begin() as session:
            moneybox = await update_instance(
                async_session=session,
                orm_model=Moneybox,  # type: ignore
                record_id=moneybox_id,
                data=moneybox_data,
            )

            if moneybox is None:
                raise MoneyboxNotFoundError(moneybox_id=moneybox_id)

            if "name" in moneybox_data:
                moneybox_name_history_data = {
                    "name": moneybox.name,
                    "moneybox_id": moneybox.id,
                }
                moneybox_name_history = await create_instance(
                    async_session=session,
                    orm_model=MoneyboxNameHistory,  # type: ignore
                    data=moneybox_name_history_data,
                )

                if moneybox_name_history is None:
                    raise UpdateInstanceError(
                        record_id=None,
                        message="Failed to update moneybox name history.",
                        details=moneybox_name_history_data,
                    )

        return moneybox.asdict()

    async def delete_moneybox(self, moneybox_id: int) -> None:
        """DB Function to delete a moneybox by given id.

        :param moneybox_id: The id of the moneybox.
        :type moneybox_id: :class:`int`

        :raises: :class:`MoneyboxNotFoundError`: if given moneybox_id
            was not found in database.
        """

        moneybox = await self.get_moneybox(moneybox_id=moneybox_id)
        _overflow_moneybox: Moneybox = await self._get_overflow_moneybox()

        if moneybox["id"] == _overflow_moneybox.id:
            raise OverflowMoneyboxCantBeDeletedError(moneybox_id=moneybox_id)

        if moneybox["balance"] > 0:
            raise HasBalanceError(moneybox_id=moneybox_id, balance=moneybox["balance"])

        async with self.async_session.begin() as session:
            updated_moneybox = await update_instance(
                async_session=session,
                orm_model=Moneybox,  # type: ignore
                record_id=moneybox_id,
                data={"priority": None},
            )

            if not updated_moneybox:
                raise UpdateInstanceError(
                    record_id=moneybox_id,
                    message="Failed to update moneybox priority.",
                    details={"priority": None},
                )

            deactivated: bool = await deactivate_instance(
                async_session=session,
                orm_model=Moneybox,  # type: ignore
                record_id=moneybox_id,
            )

            if not deactivated:
                raise DeleteInstanceError(
                    record_id=moneybox_id,
                    message="Failed to delete (deactivate) moneybox.",
                    details={"deactivated": deactivated},
                )

    # TODO refactor: add_amount and  # pylint: disable=fixme
    #  sub_amount are almost identical, combine in one function?
    async def add_amount(
        self,
        moneybox_id: int,
        deposit_transaction_data: dict[str, Any],
        transaction_type: TransactionType,
        transaction_trigger: TransactionTrigger,
    ) -> dict[str, Any]:
        """DB Function to add amount to moneybox by moneybox_id.

        :param moneybox_id: The id of the moneybox.
        :type moneybox_id: :class:`int`
        :param deposit_transaction_data: The deposit transaction data.
        :type deposit_transaction_data: :class:`dict[str, Any]`
        :param transaction_type: The transaction type of the transaction.
        :type transaction_type: :class:`TransactionType`
        :param transaction_trigger: The transaction trigger for the transaction.
        :type transaction_trigger: :class:`TransactionTrigger`

        :return: The updated moneybox data.
        :rtype: :class:`dict[str, Any]`

        :raises: :class:`MoneyboxNotFoundError`: if given moneybox_id
                    was not found in database.
                 :class:`NegativeAmountError`: if balance to add is negative.
        """

        moneybox = await read_instance(
            async_session=self.async_session,
            orm_model=Moneybox,  # type: ignore
            record_id=moneybox_id,
        )

        if moneybox is None:
            raise MoneyboxNotFoundError(moneybox_id=moneybox_id)

        moneybox.balance += deposit_transaction_data["amount"]

        async with self.async_session.begin() as session:
            updated_moneybox = await update_instance(
                async_session=session,
                orm_model=Moneybox,  # type: ignore
                record_id=moneybox_id,
                data=moneybox.asdict(),
            )

            await self._add_transfer_log(
                moneybox_id=moneybox_id,
                description=deposit_transaction_data["description"],
                transaction_type=transaction_type,
                transaction_trigger=transaction_trigger,
                amount=deposit_transaction_data["amount"],
                balance=updated_moneybox.balance,  # type: ignore
                session=session,
            )

        return updated_moneybox.asdict()  # type: ignore

    async def sub_amount(  # pylint: disable=too-many-arguments
        self,
        moneybox_id: int,
        withdraw_transaction_data: dict[str, Any],
        transaction_type: TransactionType,
        transaction_trigger: TransactionTrigger,
    ) -> dict[str, Any]:
        """DB Function to sub given amount from moneybox by moneybox_id.

        :param moneybox_id: The id of the moneybox.
        :type moneybox_id: :class:`int`
        :param withdraw_transaction_data: The withdrawal transaction data.
        :type withdraw_transaction_data: :class:`dict[str, Any]`
        :param transaction_type: The transaction type of the transaction.
        :type transaction_type: :class:`TransactionType`
        :param transaction_trigger: The transaction trigger for the transaction.
        :type transaction_trigger: :class:`TransactionTrigger`
        :return: The updated moneybox data.
        :rtype: :class:`dict[str, Any]`

        :raises: :class:`MoneyboxNotFoundError`: if given moneybox_id
                    was not found in database.
                 :class:`NegativeAmountError`:
                    if balance to sub  is negative.
                 :class:`BalanceResultIsNegativeError`:
                    if result of withdraw is negative.
        """

        amount = withdraw_transaction_data["amount"]

        if amount <= 0:
            raise NonPositiveAmountError(moneybox_id=moneybox_id, amount=amount)

        moneybox = await read_instance(
            async_session=self.async_session,
            orm_model=Moneybox,  # type: ignore
            record_id=moneybox_id,
        )

        if moneybox is None:
            raise MoneyboxNotFoundError(moneybox_id=moneybox_id)

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

            await self._add_transfer_log(
                moneybox_id=moneybox_id,
                description=withdraw_transaction_data["description"],
                transaction_type=transaction_type,
                transaction_trigger=transaction_trigger,
                amount=-amount,  # negate, withdrawals need to be negative in log data
                balance=updated_moneybox.balance,  # type: ignore
                session=session,
            )

        return updated_moneybox.asdict()  # type: ignore

    async def transfer_amount(  # pylint: disable=too-many-locals
        self,
        from_moneybox_id: int,
        transfer_transaction_data: dict[str, Any],
        transaction_type: TransactionType,
        transaction_trigger: TransactionTrigger,
    ) -> None:
        """DB Function to transfer `balance` from `from_moneybox_id`
        from `to_moneybox_id`.

        :param from_moneybox_id: The source id of the moneybox where the balance comes from.
        :type from_moneybox_id: :class:`int`
        :param transfer_transaction_data: The transfer transaction data.
        :type transfer_transaction_data: :class:`dict[str, Any]`
        :param transaction_type: The transaction type of the transaction.
        :type transaction_type: :class:`TransactionType`
        :param transaction_trigger: The transaction trigger for the transaction.
        :type transaction_trigger: :class:`TransactionTrigger`

        :raises: :class:`NegativeTransferAmountError`:
                    if balance to transfer is negative.
                 :class:`BalanceResultIsNegativeError`:
                    if result of withdraws from_moneybox_id is negative.
                :class:`TransferEqualMoneyboxError`:
                    if transfer shall happen within the same moneybox.
        """

        to_moneybox_id = transfer_transaction_data["to_moneybox_id"]
        amount = transfer_transaction_data["amount"]

        if from_moneybox_id == to_moneybox_id:
            raise TransferEqualMoneyboxError(
                from_moneybox_id=from_moneybox_id,
                to_moneybox_id=to_moneybox_id,
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
                counterparty_moneybox_id=to_moneybox_id,
                description=transfer_transaction_data["description"],
                transaction_type=transaction_type,
                transaction_trigger=transaction_trigger,
                amount=-amount,  # negate, withdrawals need to be negative in log data
                balance=updated_from_moneybox.balance,  # type: ignore
                session=session,
            )

            # log in `to_moneybox`instance (deposit)
            await self._add_transfer_log(
                moneybox_id=to_moneybox_id,
                counterparty_moneybox_id=from_moneybox_id,
                description=transfer_transaction_data["description"],
                transaction_type=transaction_type,
                transaction_trigger=transaction_trigger,
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

    async def get_transaction_logs(self, moneybox_id: int) -> list[dict[str, Any]]:
        """Get a list of transaction logs for the given moneybox id.

        :param moneybox_id: The moneybox id.
        :type moneybox_id: :class:`int`
        :return: A list of transaction logs for the given moneybox id.
        :rtype: :class:`list[dict[str, Any]]`

        :raises: :class:`MoneyboxNotFoundError`: if given moneybox_id
            was not found in database.
        """

        stmt = (
            select(Moneybox)
            .options(joinedload(Moneybox.transactions_log))
            .where(
                and_(
                    Moneybox.id == moneybox_id,
                    Moneybox.is_active.is_(True),
                )
            )
        )

        async with self.async_session() as session:
            result = await session.execute(stmt)

        moneybox = result.unique().scalars().one_or_none()

        if moneybox is None:
            raise MoneyboxNotFoundError(moneybox_id=moneybox_id)

        # TODO: save resolved names on a cache?
        #   map like:  id  -> datetimerange -> name
        async def resolve_moneybox_name(
            counterparty_moneybox_id_: int | None,
            from_datetime: datetime,
        ) -> str | None:
            if counterparty_moneybox_id_ is None:
                return None

            counterparty_moneybox_name = await self._get_historical_moneybox_name(
                moneybox_id=counterparty_moneybox_id_,
                from_datetime=from_datetime,
            )

            return counterparty_moneybox_name

        return [
            transaction.asdict(exclude=["modified_at"])
            | {
                "counterparty_moneybox_name": await resolve_moneybox_name(
                    counterparty_moneybox_id_=transaction.counterparty_moneybox_id,
                    from_datetime=transaction.created_at,
                )
            }
            for transaction in moneybox.transactions_log
        ]

    async def _get_historical_moneybox_name(
        self, moneybox_id: int, from_datetime: datetime | None = None
    ) -> str:
        """Get historical moneybox name for the given moneybox id within given datetime.

        :param moneybox_id: The moneybox id.
        :type moneybox_id: :class:`int`
        :param from_datetime: The datetime of the moneybox name, defaults to None.
        :type from_datetime: :class:`datetime.datetime` | :class:`None`
        :return: The historical moneybox name for the given moneybox id within given datetime.
        :rtype: :class:`str`
        """

        stmt = select(MoneyboxNameHistory).order_by(desc(MoneyboxNameHistory.created_at)).limit(1)

        if from_datetime is None:
            stmt = stmt.where(
                MoneyboxNameHistory.moneybox_id == moneybox_id,
            )
        else:
            stmt = stmt.where(
                and_(
                    MoneyboxNameHistory.moneybox_id == moneybox_id,
                    MoneyboxNameHistory.created_at <= from_datetime,
                )
            )

        async with self.async_session() as session:
            result = await session.execute(stmt)

        moneybox_name_history = result.scalars().one_or_none()

        if moneybox_name_history is None:
            raise MoneyboxNotFoundError(moneybox_id=moneybox_id)

        return moneybox_name_history.name

    async def _get_moneybox_id_by_name(self, name: str) -> int:
        """Get moneybox id for the given name.

        :param name: The name of the moneybox.
        :type name: :class:`str`
        :return: The moneybox id for the given name.
        :rtype: :class:`int`
        """

        stmt = select(Moneybox).where(Moneybox.name == name)

        async with self.async_session() as session:
            result = await session.execute(stmt)

        moneybox = result.scalars().one_or_none()

        if moneybox is None:
            raise MoneyboxNotFoundByNameError(name=name)

        return moneybox.id

    async def get_priority_list(self) -> list[dict[Hashable, Any]]:
        """Get the priority list (moneybox_id to priority and name map).

        :return: The priority list (moneybox_id, priority and name key-values).
        :type: :class:`list[dict[Hashable, Any]]`
        """

        stmt = select(Moneybox.id, Moneybox.priority, Moneybox.name).where(
            Moneybox.is_active.is_(True),
        )

        async with self.async_session() as session:
            result = await session.execute(stmt)

        priorities = result.all()

        priority_map = [
            {
                "moneybox_id": moneybox_id,
                "name": name,
                "priority": priority,
            }
            for moneybox_id, priority, name in priorities
        ]

        return priority_map

    async def update_priority_list(
        self, priorities: list[dict[int, int]]
    ) -> list[dict[Hashable, Any]]:
        """Set new priorities by given priority list.

        :param priorities: The priority list (moneybox_id to priority and name map).
        :type priorities: :class:`list[dict[int, int]]`
        :return: The updated priority list (moneybox_id to priority and name map).
        :type: :class:`list[dict[Hashable, Any]]`
        """

        if 0 in set(priority["priority"] for priority in priorities):
            raise UpdateInstanceError(
                record_id=None,
                message="Updating priority=0 is not allowed (reserved for Overflow Moneybox)",
                details={"priority_list": priorities},  # type: ignore
            )

        async with self.async_session.begin() as session:
            reset_data = [
                {"id": priority["moneybox_id"], "priority": None}
                for priority in priorities
            ]

            # ORM Bulk UPDATE by Primary Key -> set priority to None
            await session.execute(
                update(Moneybox),
                params=reset_data,
            )

            data = [
                {"id": priority["moneybox_id"], "priority": priority["priority"]}
                for priority in priorities
            ]

            # ORM Bulk UPDATE by Primary Key -> set real priorities
            await session.execute(
                update(Moneybox),
                params=data,
            )

        return await self.get_priority_list()
