# pylint: disable=too-many-lines
"""All database definitions are located here."""

import asyncio
import io
import subprocess
import tempfile
from datetime import datetime, timezone
from functools import cached_property
from typing import Any, Sequence, cast

import bcrypt
from fastapi.encoders import jsonable_encoder
from sqlalchemy import (
    Result,
    Select,
    and_,
    desc,
    insert,
    select,
    update,
)
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import joinedload

from alembic.config import CommandLine
from src.custom_types import (
    ActionType,
    AppEnvVariables,
    OverflowMoneyboxAutomatedSavingsModeType,
    TransactionTrigger,
    TransactionType,
    UserRoleType,
)
from src.db.core import (
    create_instance,
    deactivate_instance,
    read_instance,
    read_instances,
    update_instance,
)
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
    OverflowMoneyboxDeleteError,
    OverflowMoneyboxNotFoundError,
    OverflowMoneyboxUpdatedError,
    ProcessCommunicationError,
    RecordNotFoundError,
    TransferEqualMoneyboxError,
    UpdateInstanceError,
    UserNameAlreadyExistError,
    UserNotFoundError,
)
from src.db.models import (
    ActionLog,
    AppSettings,
    Moneybox,
    MoneyboxNameHistory,
    SqlBase,
    Transaction,
    User,
)
from src.utils import get_database_url


class DBManager:  # pylint: disable=too-many-public-methods
    """All db manager logic are located here."""

    def __init__(
        self, db_settings: AppEnvVariables, engine_args: dict[str, Any] | None = None
    ) -> None:
        """Initializer for the DBManager instance.

        :param db_settings: The database settings.
        :type db_settings: :class:`AppEnvVariables`
        :param engine_args: The asynch engine args.
        :type engine_args: :class:`dict[str, Any] | None`
        """

        if engine_args is None:
            engine_args = {"echo": False}

        self.db_settings: AppEnvVariables = db_settings

        self.async_engine: AsyncEngine = create_async_engine(
            url=self.db_connection_string,
            **engine_args,
        )
        self.async_sessionmaker: async_sessionmaker = async_sessionmaker(
            bind=self.async_engine,
            expire_on_commit=False,
        )

    @cached_property
    def db_connection_string(self) -> str:
        """Property to create a database connection string based on db driver.

        :return: A db connection string.
        :rtype: :class:`str`

        :raises: :class:`ValueError`: if self.db_settings.db_driver is not supported.
        """

        return get_database_url(db_settings=self.db_settings)

    async def get_moneyboxes(self) -> list[dict[str, Any]]:
        """DB Function to get all moneyboxes sorted by priority.

        :return: The requested moneybox data sorted by priority.
        :rtype: :class:`list[dict[str, Any]]`
        """

        moneyboxes: Sequence[SqlBase] = await read_instances(
            async_session=self.async_sessionmaker,
            orm_model=cast(SqlBase, Moneybox),
        )

        return [
            moneybox.asdict()
            for moneybox in sorted(moneyboxes, key=lambda moneybox: moneybox.priority)
        ]

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

        moneybox: SqlBase | None = await read_instance(
            async_session=self.async_sessionmaker,
            orm_model=cast(SqlBase, Moneybox),
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

        stmt: Select = select(Moneybox).where(  # type: ignore
            and_(
                Moneybox.priority == 0,
                Moneybox.is_active.is_(True),
            )
        )

        async with self.async_sessionmaker() as session:
            result: Result = await session.execute(stmt)  # type: ignore

        moneybox: Moneybox | None = cast(
            Moneybox,
            result.scalars().one_or_none(),
        )

        if moneybox is None:
            raise OverflowMoneyboxNotFoundError()

        return moneybox  # type: ignore

    async def _add_overflow_moneybox(
        self,
        moneybox_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Helper DB Function to add the overflow moneybox into database.

        :param moneybox_data: The overflow moneybox data.
        :type moneybox_data: :class:`dict[str, Any]`

        :return: The added overflow moneybox data.
        :rtype: :class:`dict[str, Any]`

        :raises: :class:`CreateInstanceError`: when something went wrong while
            creating instance in database.
        """

        async with self.async_sessionmaker.begin() as session:
            moneybox_data["priority"] = 0
            moneybox: Moneybox = cast(
                Moneybox,
                await create_instance(
                    async_session=session,
                    orm_model=cast(SqlBase, Moneybox),
                    data=moneybox_data,
                ),
            )

        return moneybox.asdict()

    async def add_moneybox(self, moneybox_data: dict[str, Any]) -> dict[str, Any]:
        """DB Function to add a new moneybox into database.

        :param moneybox_data: The moneybox data.
        :type moneybox_data: :class:`dict[str, Any]`

        :return: The added moneybox data.
        :rtype: :class:`dict[str, Any]`
        """

        try:
            async with self.async_sessionmaker.begin() as session:
                priority_list: list[dict[str, int | str]] = await self.get_prioritylist()
                moneybox_data["priority"] = (
                    1 if not priority_list else priority_list[-1]["priority"] + 1  # type: ignore
                )

                moneybox: Moneybox = cast(
                    Moneybox,
                    await create_instance(
                        async_session=session,
                        orm_model=cast(SqlBase, Moneybox),
                        data=moneybox_data,
                    ),
                )

                moneybox_name_history_data: dict[str, str | int] = {
                    "name": moneybox.name,  # type: ignore
                    "moneybox_id": moneybox.id,
                }

                await create_instance(
                    async_session=session,
                    orm_model=cast(SqlBase, MoneyboxNameHistory),
                    data=moneybox_name_history_data,
                )
        except Exception as ex:
            raise CreateInstanceError(
                message="Failed to create moneybox.",
                details=moneybox_data,
            ) from ex

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

        :raises: :class:`OverflowMoneyboxUpdatedError`: when something went
            wrong while updating the overflow moneybox in db transaction.
                :class:`UpdateInstanceError`: when something went
            wrong while updating progress in db transaction.
        """

        # get overflow moneybox and protect updating it
        _overflow_moneybox: Moneybox = await self._get_overflow_moneybox()

        if moneybox_id == _overflow_moneybox.id:
            raise OverflowMoneyboxUpdatedError(moneybox_id=_overflow_moneybox.id)

        try:
            async with self.async_sessionmaker.begin() as session:
                moneybox: Moneybox = cast(
                    Moneybox,
                    await update_instance(
                        async_session=session,
                        orm_model=cast(SqlBase, Moneybox),
                        record_id=moneybox_id,
                        data=moneybox_data,
                    ),
                )

                if "name" in moneybox_data:
                    moneybox_name_history_data: dict[str, str | int] = {
                        "name": moneybox.name,  # type: ignore
                        "moneybox_id": moneybox.id,
                    }

                    await create_instance(
                        async_session=session,
                        orm_model=cast(SqlBase, MoneyboxNameHistory),
                        data=moneybox_name_history_data,
                    )
        except Exception as ex:
            raise UpdateInstanceError(
                record_id=moneybox_id,
                message="Failed to update moneybox.",
                details=moneybox_data,
            ) from ex

        return moneybox.asdict()

    async def delete_moneybox(self, moneybox_id: int) -> None:
        """DB Function to delete a moneybox by given id.

        :param moneybox_id: The id of the moneybox.
        :type moneybox_id: :class:`int`

        :raises: :class:`OverflowMoneyboxDeleteError`: overflow moneybox
            is not allowed to be deleted.
                :class:`HasBalanceError`: a moneybox with a balance > 0
            is not allowed to be deleted.
                :class:`DeleteInstanceError`: when something went
            wrong while deleting progress in db transaction.
        """

        moneybox: dict[str, Any] = await self.get_moneybox(moneybox_id=moneybox_id)
        _overflow_moneybox: Moneybox = await self._get_overflow_moneybox()

        if moneybox["id"] == _overflow_moneybox.id:
            raise OverflowMoneyboxDeleteError(moneybox_id=moneybox_id)

        if moneybox["balance"] > 0:
            raise HasBalanceError(moneybox_id=moneybox_id, balance=moneybox["balance"])

        async with self.async_sessionmaker.begin() as session:
            _ = await update_instance(
                async_session=session,
                orm_model=cast(SqlBase, Moneybox),
                record_id=moneybox_id,
                data={"priority": None},
            )

            await deactivate_instance(
                async_session=session,
                orm_model=cast(SqlBase, Moneybox),
                record_id=moneybox_id,
            )

            sorted_by_priority_prioritylist: list[dict[str, int | str]] = (
                await self.get_prioritylist()
            )

            sorted_by_priority_prioritylist = [
                priority_data
                for priority_data in sorted_by_priority_prioritylist
                if priority_data["moneybox_id"] != moneybox_id
            ]

            new_priorities: list[dict[str, int]] = [
                {
                    "moneybox_id": priority_data["moneybox_id"],  # type: ignore
                    "priority": i + 1,
                }
                for i, priority_data in enumerate(sorted_by_priority_prioritylist)
            ]

            await self.update_prioritylist(
                priorities=new_priorities,
                session=session,
            )

    # TODO refactor: add_amount and  # pylint: disable=fixme
    #  sub_amount are almost identical, combine in one function?
    async def add_amount(  # noqa: ignore  pylint:disable=too-many-locals, too-many-arguments, too-many-positional-arguments
        self,
        moneybox_id: int,
        deposit_transaction_data: dict[str, Any],
        transaction_type: TransactionType,
        transaction_trigger: TransactionTrigger,
        session: AsyncSession | None = None,
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
        :param session: The current session of the db creation.
        :type session: :class:`AsyncSession`

        :return: The updated moneybox data.
        :rtype: :class:`dict[str, Any]`

        :raises: :class:`MoneyboxNotFoundError`: if given moneybox_id
                    was not found in database.
                 :class:NonPositiveAmountError`: if amount of deposit
                    is <= 0.
        """

        amount: int = deposit_transaction_data["amount"]

        if amount <= 0:
            raise NonPositiveAmountError(
                moneybox_id=moneybox_id,
                amount=amount,
            )

        # Determine the session to use
        if session is None:
            async with self.async_sessionmaker.begin() as session:
                moneybox: Moneybox | None = cast(
                    Moneybox,
                    await read_instance(
                        async_session=session,
                        orm_model=cast(SqlBase, Moneybox),
                        record_id=moneybox_id,
                    ),
                )

                if moneybox is None:
                    raise MoneyboxNotFoundError(moneybox_id=moneybox_id)

                new_balance: int = moneybox.balance + amount

                updated_moneybox: Moneybox = cast(
                    Moneybox,
                    await update_instance(
                        async_session=session,
                        orm_model=cast(SqlBase, Moneybox),
                        record_id=moneybox_id,
                        data={"balance": new_balance},
                    ),
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
        else:
            moneybox = cast(
                Moneybox,
                await read_instance(
                    async_session=session,
                    orm_model=cast(SqlBase, Moneybox),
                    record_id=moneybox_id,
                ),
            )

            if moneybox is None:
                raise MoneyboxNotFoundError(moneybox_id=moneybox_id)

            new_balance = moneybox.balance + amount
            session.expunge(moneybox)

            updated_moneybox = cast(
                Moneybox,
                await update_instance(
                    async_session=session,
                    orm_model=cast(SqlBase, Moneybox),
                    record_id=moneybox_id,
                    data={"balance": new_balance},
                ),
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

    async def sub_amount(  # pylint: disable=too-many-arguments, too-many-positional-arguments
        self,
        moneybox_id: int,
        withdraw_transaction_data: dict[str, Any],
        transaction_type: TransactionType,
        transaction_trigger: TransactionTrigger,
        session: AsyncSession | None = None,
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
        :param session: The current session of the db creation.
        :type session: :class:`AsyncSession`
        :return: The updated moneybox data.
        :rtype: :class:`dict[str, Any]`

        :raises: :class:`MoneyboxNotFoundError`: if given moneybox_id
            was not found in database.
                 :class:`NonPositiveAmountError`:
            if amount to sub is negative.
                 :class:`BalanceResultIsNegativeError`:
            if result of withdraw is negative.
        """

        amount: int = withdraw_transaction_data["amount"]

        if amount <= 0:
            raise NonPositiveAmountError(moneybox_id=moneybox_id, amount=amount)

        if session is None:
            moneybox: Moneybox | None = cast(
                Moneybox,
                await read_instance(
                    async_session=self.async_sessionmaker,
                    orm_model=cast(SqlBase, Moneybox),
                    record_id=moneybox_id,
                ),
            )
        else:
            moneybox = cast(
                Moneybox,
                await read_instance(
                    async_session=session,
                    orm_model=cast(SqlBase, Moneybox),
                    record_id=moneybox_id,
                ),
            )

        if moneybox is None:
            raise MoneyboxNotFoundError(moneybox_id=moneybox_id)

        new_balance: int = moneybox.balance - amount  # type: ignore

        if new_balance < 0:  # type: ignore
            raise BalanceResultIsNegativeError(
                moneybox_id=moneybox_id,
                amount=amount,
                balance=new_balance,
            )

        if session is None:
            async with self.async_sessionmaker.begin() as session:
                updated_moneybox: Moneybox = cast(
                    Moneybox,
                    await update_instance(
                        async_session=session,
                        orm_model=cast(SqlBase, Moneybox),
                        record_id=moneybox_id,
                        data={"balance": new_balance},
                    ),
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
        else:
            session.expunge(moneybox)

            updated_moneybox = cast(
                Moneybox,
                await update_instance(
                    async_session=session,
                    orm_model=cast(SqlBase, Moneybox),
                    record_id=moneybox_id,
                    data={"balance": new_balance},
                ),
            )

            await self._add_transfer_log(
                session=session,
                moneybox_id=moneybox_id,
                description=withdraw_transaction_data["description"],
                transaction_type=transaction_type,
                transaction_trigger=transaction_trigger,
                amount=-amount,  # negate, withdrawals need to be negative in log data
                balance=updated_moneybox.balance,  # type: ignore
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

        :raises: :class:`MoneyboxNotFoundError`: if given moneybox_id
            was not found in database.
                 :class:`BalanceResultIsNegativeError`:
            if result of withdraws from_moneybox_id is negative.
                :class:`NonPositiveAmountError`:
            if amount to transfer is negative or zero.
                :class:`TransferEqualMoneyboxError`:
            if transfer shall happen within the same moneybox.
        """

        if transfer_transaction_data["amount"] <= 0:
            raise NonPositiveAmountError(
                moneybox_id=from_moneybox_id,
                amount=transfer_transaction_data["amount"],
            )

        to_moneybox_id: int = transfer_transaction_data["to_moneybox_id"]
        amount: int = transfer_transaction_data["amount"]

        if from_moneybox_id == to_moneybox_id:
            raise TransferEqualMoneyboxError(
                from_moneybox_id=from_moneybox_id,
                to_moneybox_id=to_moneybox_id,
                amount=amount,
            )

        from_moneybox: Moneybox | None = cast(
            Moneybox,
            await read_instance(
                async_session=self.async_sessionmaker,
                orm_model=cast(SqlBase, Moneybox),
                record_id=from_moneybox_id,
            ),
        )

        if from_moneybox is None:
            raise MoneyboxNotFoundError(moneybox_id=from_moneybox_id)

        to_moneybox: Moneybox | None = cast(
            Moneybox,
            await read_instance(
                async_session=self.async_sessionmaker,
                orm_model=cast(SqlBase, Moneybox),
                record_id=to_moneybox_id,
            ),
        )

        if to_moneybox is None:
            raise MoneyboxNotFoundError(moneybox_id=to_moneybox_id)

        async with self.async_sessionmaker.begin() as session:
            new_from_moneybox_data: dict[str, int] = {
                "balance": from_moneybox.balance - amount,
            }

            if new_from_moneybox_data["balance"] < 0:
                raise BalanceResultIsNegativeError(
                    moneybox_id=from_moneybox_id,
                    amount=amount,
                    balance=new_from_moneybox_data["balance"],
                )

            new_to_moneybox_data: dict[str, int] = {"balance": to_moneybox.balance + amount}

            result_1: Result = await session.execute(
                update(Moneybox)
                .where(Moneybox.id == from_moneybox_id)
                .values(new_from_moneybox_data)
                .returning(Moneybox)
            )
            updated_from_moneybox: Moneybox | None = cast(
                Moneybox,
                result_1.scalar_one(),
            )

            result_2: Result = await session.execute(
                update(Moneybox)
                .where(Moneybox.id == to_moneybox_id)
                .values(new_to_moneybox_data)
                .returning(Moneybox)
            )
            updated_to_moneybox: Moneybox | None = cast(
                Moneybox,
                result_2.scalar_one(),
            )

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

    async def _add_transfer_log(  # noqa: ignore  # pylint: disable=too-many-arguments, too-many-positional-arguments
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

        stmt: Select = (
            select(Moneybox)  # type: ignore
            .options(joinedload(Moneybox.transactions_log))  # type: ignore
            .where(
                and_(
                    Moneybox.id == moneybox_id,
                    Moneybox.is_active.is_(True),
                )
            )
        )

        async with self.async_sessionmaker() as session:
            result: Result = await session.execute(stmt)

        moneybox: Moneybox | None = cast(
            Moneybox,
            result.unique().scalars().one_or_none(),
        )

        if moneybox is None:
            raise MoneyboxNotFoundError(moneybox_id=moneybox_id)

        _overflow_moneybox: Moneybox = await self._get_overflow_moneybox()

        # TODO: save resolved names on a cache?
        #   map like:  id  -> datetimerange -> name
        async def resolve_moneybox_name(
            counterparty_moneybox_id_: int | None,
            from_datetime: datetime,
        ) -> str | None:
            if counterparty_moneybox_id_ is None:
                return None

            if counterparty_moneybox_id_ == _overflow_moneybox.id:
                return _overflow_moneybox.name

            counterparty_moneybox_name: str = await self._get_historical_moneybox_name(
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

    async def _get_historical_moneybox_name(self, moneybox_id: int, from_datetime: datetime) -> str:
        """Get historical moneybox name for the given moneybox id within given datetime.

        Note: It doesn't matter if the moneybox is deactivated (soft deleted => is_active=False)

        :param moneybox_id: The moneybox id.
        :type moneybox_id: :class:`int`
        :param from_datetime: The datetime of the moneybox name.
        :type from_datetime: :class:`datetime.datetime`
        :return: The historical moneybox name for the given moneybox id within given datetime.
        :rtype: :class:`str`

        :raises: :class:`MoneyboxNotFoundError`: if given moneybox_id
            was not found in database.
        """

        # check existence before working with it
        _ = await self.get_moneybox(
            moneybox_id=moneybox_id,
            only_active_instances=False,
        )

        stmt: Select = (
            select(MoneyboxNameHistory)  # type: ignore
            .order_by(desc(MoneyboxNameHistory.created_at))  # type: ignore
            .limit(1)
        ).where(
            and_(
                MoneyboxNameHistory.moneybox_id == moneybox_id,
                MoneyboxNameHistory.created_at <= from_datetime,
            )
        )

        async with self.async_sessionmaker() as session:
            result: Result = await session.execute(stmt)  # type: ignore

        moneybox_name_history: MoneyboxNameHistory | None = cast(
            MoneyboxNameHistory,
            result.scalars().one_or_none(),
        )

        if moneybox_name_history is None:
            raise MoneyboxNameNotFoundError(
                moneybox_id=moneybox_id,
                details={"from_datetime": from_datetime},
            )

        return moneybox_name_history.name

    async def get_prioritylist(self) -> list[dict[str, int | str]]:
        """Get the priority list ASC ordered by priority
        (overflow moneybox NOT included).

        :return: The priority list.
        :rtype: :class:`list[dict[str, int|str]]`

        :raises: :class:`InconsistentDatabaseError`: if at least one (active) moneybox has
            `priority=None`.
        """

        stmt: Select = (
            select(Moneybox.id, Moneybox.priority, Moneybox.name)  # type: ignore
            .where(
                Moneybox.is_active.is_(True),
            )
            .order_by(Moneybox.priority)  # type: ignore
        )

        async with self.async_sessionmaker() as session:
            result: Result = await session.execute(stmt)

        priorities: list[tuple[int, int, str]] = result.all()  # type: ignore

        priority_map: list[dict[str, int | str]] = [
            {
                "moneybox_id": moneybox_id,
                "name": name,
                "priority": priority,
            }
            for moneybox_id, priority, name in priorities
            if priority != 0
        ]

        if any(moneybox["priority"] is None for moneybox in priority_map):
            raise InconsistentDatabaseError(
                message="At least one (active) moneybox has priority of 'None'",
                details={
                    "priorities": priority_map,
                },
            )

        return priority_map

    async def update_prioritylist(
        self,
        priorities: list[dict[str, int]],
        session: AsyncSession | None = None,
    ) -> list[dict[str, str | int]]:
        """Set new priorities by given priority list.

        :param priorities: The priority list (moneybox_id to priority and name map).
        :type priorities: :class:`list[dict[str, int]]`
        :param session: The current session of the db creation, defaults to None.
        :type session: :class:`AsyncSession`|:class:`None`
        :return: The updated priority list (moneybox_id to priority and name map).
        :rtype: :class:`list[dict[str, str|int]]`

        :raises: :class:`OverflowMoneyboxUpdatedError`: when something went
            wrong while updating the overflow moneybox in db transaction.
                 :class:`UpdateInstanceError`: when something went
            wrong while updating progress in db transaction.
        """

        moneybox_id_priority_map: dict[int, int] = {
            priority["moneybox_id"]: priority["priority"] for priority in priorities
        }

        if len(moneybox_id_priority_map) < len(priorities):
            raise UpdateInstanceError(
                record_id=None,
                message="Update priority list has duplicate moneybox ids.",
                details={"moneybox_ids": [priority["moneybox_id"] for priority in priorities]},
            )

        _overflow_moneybox: Moneybox = await self._get_overflow_moneybox()
        moneybox_ids: set[int] = set(moneybox_id_priority_map.keys())

        if _overflow_moneybox.id in set(moneybox_id_priority_map.keys()):
            raise OverflowMoneyboxUpdatedError(
                moneybox_id=_overflow_moneybox.id,
            )

        if 0 in set(moneybox_id_priority_map.values()):
            raise UpdateInstanceError(
                record_id=None,
                message="Updating priority=0 is not allowed (reserved for Overflow Moneybox).",
                details={"prioritylist": priorities},  # type: ignore
            )

        stmt = select(Moneybox).where(Moneybox.id.in_(moneybox_id_priority_map.keys()))

        async def session_execution(_session: AsyncSession) -> list[Moneybox]:
            # Get all Moneybox entries that are in the update list
            result = await _session.execute(stmt)
            _moneyboxes = result.scalars().all()

            not_existing_moneybox_ids = moneybox_ids - {moneybox.id for moneybox in _moneyboxes}

            if not_existing_moneybox_ids:
                raise UpdateInstanceError(
                    record_id=None,
                    message="Tried to update non existing moneyboxes.",
                    details={"non_existing_moneybox_ids": not_existing_moneybox_ids},
                )

            # reset priority of each entry to None
            for moneybox in _moneyboxes:
                moneybox.priority = None

            # Flush changes into database
            await _session.flush()

            # Update each matched entry in the session
            for moneybox in _moneyboxes:
                moneybox.priority = moneybox_id_priority_map[moneybox.id]

            return _moneyboxes  # type: ignore

        if session is None:
            async with self.async_sessionmaker.begin() as session:
                moneyboxes = await session_execution(_session=session)
        else:
            moneyboxes = await session_execution(_session=session)

        priority_map: list[dict[str, int | str]] = [
            {
                "moneybox_id": moneybox.id,
                "name": moneybox.name,
                "priority": moneybox.priority,
            }
            for moneybox in moneyboxes
        ]

        return sorted(priority_map, key=lambda x: x["priority"])

    async def get_app_settings(
        self,
        app_settings_id: int,
    ) -> dict[str, Any]:
        """Get app settings by app_settings id.

        :param app_settings_id: The app settings id.
        :type app_settings_id: :class:`int`
        :return: The app settings data.
        :rtype: :class:`dict[str, Any]`

        :raises: :class:`AppSettingsNotFoundError`: if there are no overflow moneybox in the
            database, missing moneybox with priority = 0.
        """

        app_settings: AppSettings | None = cast(
            AppSettings,
            await read_instance(
                async_session=self.async_sessionmaker,
                orm_model=cast(SqlBase, AppSettings),
                record_id=app_settings_id,
            ),
        )

        if app_settings is None:
            raise AppSettingsNotFoundError(app_settings_id=app_settings_id)

        return app_settings.asdict()

    async def update_app_settings(
        self,
        app_settings_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Update app settings by app_settings id.

        :param app_settings_data: The app settings data.
        :type app_settings_data: :class:`dict[str, Any]`
        :return: The updated app settings data.
        :rtype: :class:`dict[str, Any]`
        """

        app_settings: AppSettings = await self._get_app_settings()

        updating_data = {
            key: app_settings_data[key]
            for key, value in app_settings.asdict().items()
            if key in app_settings_data and value != app_settings_data[key]
        }

        async with self.async_sessionmaker.begin() as session:
            app_settings = cast(
                AppSettings,
                await update_instance(
                    async_session=session,
                    orm_model=cast(SqlBase, AppSettings),
                    record_id=app_settings.id,
                    data=updating_data,
                ),
            )

            if "is_automated_saving_active" in app_settings_data:
                activate: bool = app_settings.is_automated_saving_active  # type: ignore
                action_type: ActionType = (
                    ActionType.ACTIVATED_AUTOMATED_SAVING
                    if activate
                    else ActionType.DEACTIVATED_AUTOMATED_SAVING
                )
                automated_savings_log_data: dict[str, Any] = {
                    "action": action_type,
                    "action_at": datetime.now(tz=timezone.utc),
                    "details": jsonable_encoder(app_settings.asdict()),
                }

                await self.add_action_log(
                    session=session,
                    automated_savings_log_data=automated_savings_log_data,
                )

            if "savings_amount" in app_settings_data:
                automated_savings_log_data = {
                    "action": ActionType.CHANGED_AUTOMATED_SAVINGS_AMOUNT,
                    "action_at": datetime.now(tz=timezone.utc),
                    "details": jsonable_encoder(app_settings.asdict()),
                }

                await self.add_action_log(
                    session=session,
                    automated_savings_log_data=automated_savings_log_data,
                )

        return app_settings.asdict()

    async def _get_all_app_settings(self) -> list[AppSettings]:
        """Get all active app settings records.

        :return: The active app settings records.
        :rtype: :class:`list[AppSettings]`
        """

        stmt: Select = select(AppSettings).where(AppSettings.is_active.is_(True))  # type: ignore

        async with self.async_sessionmaker() as session:
            result: Result = await session.execute(stmt)  # type: ignore

        return result.scalars().all()  # type: ignore

    async def _get_app_settings(self) -> AppSettings:
        """Get app settings if automated savings.

        :return: The app settings.
        :rtype: :class:`AppSettings`

        :raises: :class:`InconsistentDatabaseError` when data in database
            are inconsistent.
        """

        all_app_settings: list[AppSettings] = await self._get_all_app_settings()

        if not all_app_settings:
            raise InconsistentDatabaseError(message="No app settings found.")

        # get the single app setting
        return all_app_settings[0]

    async def _overflow_moneybox_add_amount(
        self,
        app_settings: dict[str, Any],
        overflow_moneybox: dict[str, Any],
        amount: int,
        session: AsyncSession,
    ) -> dict[str, Any]:
        """Helper function for adding amount the overflow moneybox.

        :param app_settings: The app settings.
        :type app_settings: :class:`dict[str, Any]`
        :param overflow_moneybox: The overflow moneybox.
        :type overflow_moneybox: :class:`dict[str, Any]`
        :param amount: The amount to add.
        :type amount: :class:`int`
        :param session: The current database session.
        :type session: :class:`AsyncSession`
        :return: The updated overflow moneybox.
        :rtype: :class:`dict[str, Any]`

        :raises: :class:`AutomatedSavingsError`: when something went wrong while session
            transactions.
        """

        if amount <= 0:
            return overflow_moneybox

        overflow_mode: OverflowMoneyboxAutomatedSavingsModeType = app_settings[
            "overflow_moneybox_automated_savings_mode"
        ]

        deposit_transaction_data: dict[str, int | str] = {
            "amount": amount,
            "description": ("Automated Savings with Overflow Moneybox Mode: " f"{overflow_mode}"),
        }

        try:
            updated_overflow_moneybox: dict[str, Any] = await self.add_amount(
                session=session,
                moneybox_id=overflow_moneybox["id"],
                deposit_transaction_data=deposit_transaction_data,
                transaction_type=TransactionType.DISTRIBUTION,
                transaction_trigger=TransactionTrigger.AUTOMATICALLY,
            )
        except Exception as ex:
            raise AutomatedSavingsError(
                record_id=overflow_moneybox["id"],
                message="AutomatedSavings failed while add_amount() from overflow moneybox.",
                details={
                    "deposit_transaction_data": deposit_transaction_data,
                    "overflow_moneybox": jsonable_encoder(overflow_moneybox),
                    "overflow_moneybox_automated_savings_mode": overflow_mode,  # noqa: ignore  # pylint:disable=line-too-long
                    "app_settings": jsonable_encoder(app_settings),
                },
            ) from ex

        return updated_overflow_moneybox

    async def _overflow_moneybox_sub_amount(
        self,
        app_settings: dict[str, Any],
        overflow_moneybox: dict[str, Any],
        amount: int,
        session: AsyncSession,
    ) -> dict[str, Any]:
        """Helper function for subbing amount the overflow moneybox.

        :param app_settings: The app settings.
        :type app_settings: :class:`dict[str, Any]`
        :param overflow_moneybox: The overflow moneybox.
        :type overflow_moneybox: :class:`dict[str, Any]`
        :param amount: The amount to sub.
        :type amount: :class:`int`
        :param session: The current database session.
        :type session: :class:`AsyncSession`
        :return: The updated overflow moneybox.
        :rtype: :class:`dict[str, Any]`

        :raises: :class:`AutomatedSavingsError`: when something went wrong while session
            transactions.
        """

        if amount <= 0:
            return overflow_moneybox

        overflow_mode: OverflowMoneyboxAutomatedSavingsModeType = app_settings[
            "overflow_moneybox_automated_savings_mode"
        ]
        withdraw_transaction_data: dict[str, int | str] = {
            "amount": amount,
            "description": ("Automated Savings with Overflow Moneybox Mode: " f"{overflow_mode}"),
        }

        try:
            updated_overflow_moneybox: dict[str, Any] = await self.sub_amount(
                session=session,
                moneybox_id=overflow_moneybox["id"],
                withdraw_transaction_data=withdraw_transaction_data,
                transaction_type=TransactionType.DISTRIBUTION,
                transaction_trigger=TransactionTrigger.AUTOMATICALLY,
            )
        except Exception as ex:
            raise AutomatedSavingsError(
                record_id=overflow_moneybox["id"],
                message="AutomatedSavings failed while sub_amount() from overflow moneybox.",
                details={
                    "withdraw_transaction_data": withdraw_transaction_data,
                    "overflow_moneybox": jsonable_encoder(overflow_moneybox),
                    "overflow_moneybox_automated_savings_mode": overflow_mode,  # noqa: ignore  # pylint:disable=line-too-long
                    "app_settings": jsonable_encoder(app_settings),
                },
            ) from ex

        return updated_overflow_moneybox

    async def automated_savings(self) -> bool:  # pylint:disable=too-many-locals
        """The automated savings algorithm.

        App savings amount will be distributed to moneyboxes in priority order (excepted the
        Overflow Moneybox). If there is a leftover that could not been distributed,
        the overflow moneybox will get the leftover.

        :return: True, if distribution is done, false, if automated savings is deactivated.
        :rtype: :class:`bool`

        :raises: :class:`AutomatedSavingsError`: is something went wrong while session
            transactions.
        """

        app_settings: AppSettings = await self._get_app_settings()

        if not app_settings.is_automated_saving_active:
            return False

        moneyboxes: list[dict[str, Any]] = await self.get_moneyboxes()
        sorted_moneyboxes: list[dict[str, Any]] = sorted(
            moneyboxes,
            key=lambda item: item["priority"],
        )
        distribution_amount: int = app_settings.savings_amount

        async with self.async_sessionmaker.begin() as session:
            # Mode 1: COLLECT

            # Mode 2: ADD_TO_AUTOMATED_SAVINGS_AMOUNT
            action: OverflowMoneyboxAutomatedSavingsModeType = (
                app_settings.overflow_moneybox_automated_savings_mode
            )

            if (
                action is OverflowMoneyboxAutomatedSavingsModeType.ADD_TO_AUTOMATED_SAVINGS_AMOUNT
                and sorted_moneyboxes[0]["balance"] > 0
            ):
                distribution_amount = app_settings.savings_amount + sorted_moneyboxes[0]["balance"]

                # remove balance from overflow moneybox
                from_overflow_moneybox_distributed_amount: int = sorted_moneyboxes[0]["balance"]

                sorted_moneyboxes[0] = await self._overflow_moneybox_sub_amount(
                    session=session,
                    app_settings=app_settings.asdict(),
                    overflow_moneybox=sorted_moneyboxes[0],
                    amount=from_overflow_moneybox_distributed_amount,
                )

            updated_moneyboxes: list[dict[str, Any]] = (
                await self._distribute_automated_savings_amount(  # type: ignore  # noqa: ignore  # pylint:disable=line-too-long
                    session=session,
                    sorted_by_priority_moneyboxes=sorted_moneyboxes,
                    fill_mode=False,
                    distribute_amount=distribution_amount,
                    app_settings=app_settings.asdict(),
                )
            )

            # Mode 3: FILL_UP_LIMITED_MONEYBOXES
            if (
                app_settings.overflow_moneybox_automated_savings_mode
                is OverflowMoneyboxAutomatedSavingsModeType.FILL_UP_LIMITED_MONEYBOXES
                and updated_moneyboxes[0]["balance"] > 0
            ):
                # filter moneyboxes only with savings_target != None AND > 0
                filtered_moneyboxes: list[dict[str, Any]] = [
                    moneybox
                    for moneybox in updated_moneyboxes
                    if moneybox["priority"] == 0
                    or moneybox["savings_target"] is not None
                    and moneybox["savings_target"] > 0
                ]

                # sort moneyboxes by priority
                updated_moneyboxes = sorted(
                    filtered_moneyboxes,
                    key=lambda item: item["priority"],
                )
                old_overflow_moneybox_balance: int = updated_moneyboxes[0]["balance"]

                # remove balance from overflow moneybox
                updated_moneyboxes[0] = await self._overflow_moneybox_sub_amount(
                    session=session,
                    app_settings=app_settings.asdict(),
                    overflow_moneybox=sorted_moneyboxes[0],
                    amount=updated_moneyboxes[0]["balance"],
                )

                _ = await self._distribute_automated_savings_amount(
                    session=session,
                    sorted_by_priority_moneyboxes=updated_moneyboxes,
                    fill_mode=True,
                    distribute_amount=old_overflow_moneybox_balance,
                    app_settings=app_settings.asdict(),
                )

            # log automated saving
            automated_savings_log_data: dict[str, Any] = {
                "action": ActionType.APPLIED_AUTOMATED_SAVING,
                "action_at": datetime.now(tz=timezone.utc),
                "details": jsonable_encoder(
                    app_settings.asdict() | {"distribution_amount": distribution_amount}
                ),
            }

            await self.add_action_log(
                session=session,
                automated_savings_log_data=automated_savings_log_data,
            )

        return True

    async def _distribute_automated_savings_amount(  # noqa: ignore  # pylint:disable=too-many-locals, too-many-arguments, too-many-positional-arguments
        self,
        session: AsyncSession,
        distribute_amount: int,
        sorted_by_priority_moneyboxes: list[dict[str, Any]],
        fill_mode: bool,
        app_settings: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """A separate helper function to distribute amount to given moneyboxes.

        :param session: Database session.
        :type session: :class:`AsyncSession`
        :param distribute_amount: The distributing amount.
        :type distribute_amount: int
        :param sorted_by_priority_moneyboxes: A list of moneyboxes ASC sorted by priority (the
            overflow moneybox included).
        :type sorted_by_priority_moneyboxes: :class:`list[dict[str, Any]]`
        :param fill_mode: Flag to indicate whether the savings amount
            of moneyboxes should be considered. This applies during the normal distribution process.

            In Fill-Up Mode, the savings amount does not need to be considered because this mode
            focuses on reaching the savings target by fully allocating (all-in) to the
            highest-priority moneybox first, then moving on to the next in line, and so on.

        :type fill_mode: :class:`bool`
        :param app_settings: The app settings.
        :type app_settings: :class:`dict[str, Any]`
        :return: Returns an updated moneyboxes list (sorted by priority,
            overflow moneybox included).
        :rtype: :class:`list[dict[str, Any]]`

        :raises: :class:`AutomatedSavingsError`: when something went wrong while
            session transactions.
        """

        if distribute_amount <= 0:
            return sorted_by_priority_moneyboxes

        updated_moneyboxes: list[dict[str, Any]] = [
            sorted_by_priority_moneyboxes[0]
        ]  # add initially the overflow moneybox

        for moneybox in sorted_by_priority_moneyboxes[1:]:  # skip overflow moneybox (priority=0)
            amount_to_distribute: int = distribute_amount

            # normal mode [NOT fill mode] (limit distribution amount to savings_amount)
            #   fill mode need to ignore the wises of the moneybox
            if not fill_mode:
                amount_to_distribute = min(
                    moneybox["savings_amount"],  # limit so savings_amount (wished amount)
                    amount_to_distribute,
                )

            if moneybox["savings_target"] is not None:
                missing_amount_until_target: int = moneybox["savings_target"] - moneybox["balance"]

                if missing_amount_until_target > 0:
                    amount_to_distribute = min(
                        amount_to_distribute,
                        missing_amount_until_target,
                    )
                else:
                    # Moneybox is full (reached amount target )
                    updated_moneyboxes.append(moneybox)
                    continue
            else:  # savings_target not set
                if fill_mode:  # and savings_amount ignored -> means:
                    # can't enforce distribution because there is no target to reach
                    #  in fill mode
                    updated_moneyboxes.append(moneybox)
                    continue

            if amount_to_distribute > 0:
                updated_moneybox: dict[str, Any] = await self.add_amount(
                    session=session,
                    moneybox_id=moneybox["id"],
                    deposit_transaction_data={
                        "amount": amount_to_distribute,
                        "description": "Automated savings.",
                    },
                    transaction_type=TransactionType.DISTRIBUTION,
                    transaction_trigger=TransactionTrigger.AUTOMATICALLY,
                )
                updated_moneyboxes.append(updated_moneybox)

                distribute_amount -= amount_to_distribute
            else:
                updated_moneyboxes.append(moneybox)
                continue

        # add the rest of app_savings_amount to overflow_moneybox if there is a rest
        rest_amount: int = distribute_amount

        updated_moneyboxes[0] = await self._overflow_moneybox_add_amount(
            session=session,
            app_settings=app_settings,
            overflow_moneybox=updated_moneyboxes[0],
            amount=rest_amount,
        )

        return updated_moneyboxes

    async def get_action_logs(self, action_type: ActionType) -> list[dict[str, Any]]:
        """Get action logs by action.

        :param action_type: Action type.
        :type action_type: :class:`ActionType`
        :return: The action logs data.
        :rtype: :class:`list[dict[str, Any]]`
        """

        stmt: Select = (
            select(ActionLog)  # type: ignore
            .where(
                and_(
                    ActionLog.action == action_type,
                    ActionLog.is_active.is_(True),
                )
            )
            .order_by(ActionLog.action_at.desc())
        )

        async with self.async_sessionmaker() as session:
            result: Result = await session.execute(stmt)  # type: ignore

        action_logs: list[ActionLog] = result.scalars().all()  # type: ignore

        return [get_automated_savings_log.asdict() for get_automated_savings_log in action_logs]

    async def add_action_log(
        self,
        session: AsyncSession,
        automated_savings_log_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Add action log data into database.

        :param session: Database session.
        :type session: :class:`AsyncSession`
        :param automated_savings_log_data: Automated savings log data.
        :type automated_savings_log_data: :class:`dict[str, Any]`
        :return: The created automated savings logs data.
        :rtype: :class:`dict[str, Any]`
        """

        action_log: ActionLog = cast(
            ActionLog,
            await create_instance(
                async_session=session,
                orm_model=cast(SqlBase, ActionLog),
                data=automated_savings_log_data,
            ),
        )

        return action_log.asdict()  # type: ignore

    async def update_action_log(
        self,
        action_log_id: int,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """Update action log data in database by id.

        :param action_log_id: The ID of the action log entry.
        :type action_log_id: :class:`int`
        :param data: Automated savings log data.
        :type data: :class:`dict[str, Any]`
        :return: The created automated savings log data.
        :rtype: :class:`dict[str, Any]`
        """

        action_log: ActionLog = cast(
            ActionLog,
            await update_instance(
                async_session=self.async_sessionmaker,
                orm_model=cast(SqlBase, ActionLog),
                record_id=action_log_id,
                data=data,
            ),
        )

        return action_log.asdict()  # type: ignore

    async def reset_database(self, keep_app_settings: bool) -> None:
        """Reset database data by using alembic upgrade and downgrade logic.

        :param keep_app_settings: Indicates if app settings shall be also
            deleted.
        :type keep_app_settings: :class:`bool`
        """

        if keep_app_settings:
            # TODO use private function for now, because there is
            #   only one app settings
            backup_app_settings: AppSettings = await self._get_app_settings()

        cmd_line: CommandLine = CommandLine()
        await asyncio.to_thread(
            CommandLine.main,
            cmd_line,
            ["downgrade", "base"],
        )

        # After migration, invalidate cache or reset connection pool
        await self.async_engine.dispose(close=False)
        await asyncio.sleep(0.5)

        await asyncio.to_thread(
            CommandLine.main,
            cmd_line,
            ["upgrade", "head"],
        )

        # After migration, invalidate cache or reset connection pool
        await self.async_engine.dispose(close=False)
        await asyncio.sleep(0.5)

        if keep_app_settings:
            # TODO: adapt update_app_settings by adding settings_id
            #   if there is a multi user mode later
            await self.update_app_settings(app_settings_data=backup_app_settings.asdict())

    async def export_sql_dump(self) -> io.BytesIO:
        """Export a sql dump by using pg_dump.

        :return: The sql dump as bytes.
        :rtype: :class:`io.BytesIO`

        :raises: :class:`MissingDependencyError`: if pg_dump is not installed
            or found.
                 :class:`ProcessCommunicationError`: if pg_dump itself has
            an error
        """

        command: list[str] = [
            "pg_dump",
            "-Fc",
            "-h",
            self.db_settings.db_host,
            "-p",
            str(self.db_settings.db_port),
            "-U",
            self.db_settings.db_user,
            "-d",
            self.db_settings.db_name,
        ]

        try:
            process: subprocess.Popen = subprocess.Popen(  # pylint: disable=consider-using-with
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except Exception as ex:  # noqa: E722
            raise MissingDependencyError(message="pg_dump not installed.") from ex

        with process:
            stdout, stderr = process.communicate(timeout=15)

            if process.returncode != 0:
                raise ProcessCommunicationError(
                    message=stderr.decode("utf-8"),
                )

            return io.BytesIO(stdout)

    async def import_sql_dump(self, sql_dump: bytes) -> None:
        """Export a sql dump by using pg_dump.

        :return: The sql dump as bytes.
        :rtype: :class:`io.BytesIO`

        :raises: :class:`MissingDependencyError`: if pg_dump is not installed
            or found.
                 :class:`ProcessCommunicationError`: if pg_dump itself has
            an error
        """

        # backup database
        backup_database_dump_bytes: io.BytesIO = await self.export_sql_dump()
        await self.reset_database(keep_app_settings=False)

        try:
            await self._import_sql_dump(sql_dump=sql_dump)
        except:  # noqa: E722
            # restore db on fail restoring users import
            await self._import_sql_dump(
                sql_dump=backup_database_dump_bytes.getvalue(),
            )
            raise

    async def _import_sql_dump(
        self,
        sql_dump: bytes,
    ) -> None:
        with tempfile.NamedTemporaryFile(delete=True) as tmp_file:
            tmp_file.write(sql_dump)
            tmp_file_path = tmp_file.name

            command: list[str] = [
                "pg_restore",
                "--clean",
                "--if-exists",
                "-h",
                self.db_settings.db_host,
                "-p",
                str(self.db_settings.db_port),
                "-U",
                self.db_settings.db_user,
                "-d",
                self.db_settings.db_name,
                tmp_file_path,
            ]

            try:
                process: subprocess.Popen = subprocess.Popen(  # pylint: disable=consider-using-with
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
            except Exception as ex:  # noqa: E722
                raise MissingDependencyError(message="pg_restore not installed.") from ex

            with process:
                _, stderr = process.communicate(timeout=15)

                if process.returncode != 0:
                    raise ProcessCommunicationError(
                        message=stderr.decode("utf-8"),
                    )

    async def _exists_active_user_name(
        self, user_name: str, exclude_ids: list[int] | None = None
    ) -> bool:
        """Helper function to check, if username already exists in database

        :param user_name: User`s name.
        :type user_name: :class:`str`
        :param exclude_ids: User ids to ignore in check.
        :type exclude_ids: :class:`list`
        :return: True, if username exists in database, false if not.
        :rtype: :class:`bool`
        """

        if exclude_ids is None:
            exclude_ids = []

        existing_user: Select = select(User).where(
            and_(
                User.is_active.is_(True),
                User.user_login == user_name,
                User.id.notin_(exclude_ids),
            )
        )

        async with self.async_sessionmaker() as session:
            result: Result = await session.execute(existing_user)

        # will raise exception is more users with same name was found,
        # we will accept exception as unexpected error for now
        user_exists = result.scalars().one_or_none() is not None

        return user_exists

    async def add_user(
        self,
        user_name: str,
        user_password: str,
        is_admin: bool = False,
    ) -> dict[str, Any]:
        """Create a user database entry and returns new entry.

        :param user_name: The username.
        :type user_name: :class:`str`
        :param user_password: The password of the user. The password
            will be hashed before persisting into database.
        :type user_password: :class:`str`
        :param is_admin: Assign role ADMIN to user if True,
            otherwise assign role USER, defaults to False.
        :type is_admin: :class:`UserRoleType`
        :return: The new user database entry.
        :rtype: :class:`dict[str, Any]`

        :raises UserNameAlreadyExistError: if username already exists.
                CreateInstanceError: if creating database entry fails.
        """

        user_exists = await self._exists_active_user_name(user_name=user_name)

        if user_exists:
            raise UserNameAlreadyExistError(user_name=user_name)

        user: User = cast(
            User,
            await create_instance(
                async_session=self.async_sessionmaker,
                orm_model=cast(SqlBase, User),
                data={
                    "user_login": user_name,
                    "user_password_hash": await self.get_password_hash(password=user_password),
                    "role": UserRoleType.ADMIN if is_admin else UserRoleType.USER,
                },
            ),
        )

        return user.asdict()

    async def update_user_password(
        self,
        user_id: int,
        new_user_password: str,
    ) -> dict[str, Any]:
        """Update user password and return updated user.

        :param user_id: The id of the user.
        :type user_id: :class:`int`
        :param new_user_password: The new user password.
        :type new_user_password: :class:`str`
        :return: The updated user data.
        :rtype: :class:`dict`
        """

        hashed_password = await self.get_password_hash(password=new_user_password)

        updated_user: User = cast(
            User,
            await update_instance(
                async_session=self.async_sessionmaker,
                record_id=user_id,
                orm_model=cast(SqlBase, User),
                data={"user_password_hash": hashed_password},
            ),
        )

        return updated_user.asdict()

    async def update_user_name(
        self,
        user_id: int,
        new_user_name: str,
    ) -> dict[str, Any]:
        """Update username and return updated user.

        :param user_id: The id of the user.
        :type user_id: :class:`int`
        :param new_user_name: The new username.
        :type new_user_name: :class:`str`
        :return: The updated user data.
        :rtype: :class:`dict`

        :raises UserNameAlreadyExistError: if username already exists.
                UpdateInstanceError: if updating username fails.
        """

        user_exists = await self._exists_active_user_name(
            user_name=new_user_name,
            exclude_ids=[user_id],
        )

        if user_exists:
            raise UserNameAlreadyExistError(user_name=new_user_name)

        updated_user: User = cast(
            User,
            await update_instance(
                async_session=self.async_sessionmaker,
                record_id=user_id,
                orm_model=cast(SqlBase, User),
                data={"user_login": new_user_name},
            ),
        )

        return updated_user.asdict()

    async def delete_user(self, user_id: int) -> None:
        """Delete a user database entry by given ID.

        :param user_id: The user ID.
        :type user_id: :class:`int`

        :raises DeleteInstanceError: if deleting user fails.
                UserNotFoundError: if user does not exist.
        """

        user: dict[str, Any] = await self.get_user(user_id=user_id)

        if user["role"] is UserRoleType.ADMIN:
            raise DeleteInstanceError(
                record_id=user_id, message="An admin user can't be deleted.", details=user
            )

        try:
            await deactivate_instance(
                async_session=self.async_sessionmaker,
                orm_model=cast(SqlBase, User),
                record_id=user_id,
            )
        except RecordNotFoundError as ex:
            raise UserNotFoundError(user_id=user_id) from ex

    async def get_user_by_credentials(
        self,
        user_name: str,
        user_password: str,
    ) -> dict[str, Any] | None:
        """Get user by credentials. If user not found, rerun None, else
        user data as dict will be returned.

        :param user_name: The name of the user.
        :type user_name: :class:`str`
        :param user_password: The password of the user.
        :type user_password: :class:`str`
        :return: The user data, if not found, returns None.
        :rtype: :class:`dict[str, Any] | None`
        """

        stmt: Select = select(User).where(  # type: ignore
            and_(
                User.user_login == user_name,
                User.is_active.is_(True),
            )
        )

        async with self.async_sessionmaker() as session:
            result: Result = await session.execute(stmt)

        user: User | None = cast(
            User,
            result.scalars().one_or_none(),
        )

        if user is None or not await self.verify_password(
            user_password,
            user.user_password_hash,
        ):
            return None

        return user.asdict()

    async def get_user(
        self,
        user_id: int,
    ) -> dict[str, Any]:
        """Get user by user_id

        :param user_id: The ID of the user.
        :type user_id: :class:`int`
        :return: The user data.
        :rtype: :class:`dict[str, Any]`

        :raises UserNotFountError: if user by id not found.
        """

        user = await read_instance(
            async_session=self.async_sessionmaker,
            orm_model=cast(SqlBase, User),
            record_id=user_id,
        )

        if user is None:
            raise UserNotFoundError(user_id=user_id)

        return user.asdict()

    async def get_users(
        self,
        only_active_instances: bool = True,
    ) -> list[dict[str, Any]]:
        """Get all user as a list.

        :param only_active_instances: If True, only return active users.
        :type only_active_instances: :class:`bool`
        :return: The user data, if not found, returns None.
        :rtype: :class:`dict[str, Any] | None`
        """

        users = await read_instances(
            async_session=self.async_sessionmaker,
            orm_model=cast(SqlBase, User),
            only_active_instances=only_active_instances,
        )
        return [user.asdict() for user in users]

    async def verify_password(
        self, plain_password: str | bytes, hashed_password: str | bytes
    ) -> bool:
        """Verify the plain_password matches the hashed password.

        :param plain_password: The plain password.
        :type plain_password: :class:`str` | :class:`bytes`
        :param hashed_password: The hashed password.
        :type hashed_password: :class:`str` | :class:`bytes`
        :return: True, if the hashed password matches the plain_password.
        :rtype: :class:`bool`
        """

        if isinstance(plain_password, str):
            plain_password = plain_password.encode("utf-8")

        if isinstance(hashed_password, str):
            hashed_password = hashed_password.encode("utf-8")

        return bcrypt.checkpw(password=plain_password, hashed_password=hashed_password)

    async def get_password_hash(self, password: str | bytes) -> str:
        """Get hashed password.

        :param password: The password.
        :type password: :class:`str`
        :return: The hashed password.
        :rtype: :class:`str`
        """

        if isinstance(password, str):
            password = password.encode("utf-8")

        return bcrypt.hashpw(password, bcrypt.gensalt(12)).decode()
