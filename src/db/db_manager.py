"""All database definitions are located here."""

from typing import Any

from sqlalchemy import update
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.custom_types import DBSettings
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
    NegativeBalanceError,
    NegativeTransferBalanceError,
)
from src.db.models import Moneybox
from src.utils import get_database_url


class DBManager:
    """All db manager logic are located here."""

    def __init__(self, db_settings: DBSettings, engine_args: dict[str, Any] | None = None) -> None:
        if engine_args is None:
            engine_args = {}

        self.db_settings = db_settings
        self.async_engine = create_async_engine(url=self.db_connection_string, **engine_args)
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

    async def add_balance(
        self,
        moneybox_id: int,
        balance: int,
    ) -> dict[str, Any]:
        """DB Function to add balance to moneybox by moneybox_id.

        :param moneybox_id: The id of the moneybox.
        :type moneybox_id: :class:`int`
        :param balance: The balance to add to given moneybox.
        :type balance: :class:`int`

        :return: The updated moneybox data.
        :rtype: :class:`dict[str, Any]`

        :raises: :class:`MoneyboxNotFoundError`: if given moneybox_id
                    was not found in database.
                 :class:`NegativeBalanceError`: if balance to add is negative.
        """

        if balance < 0:
            raise NegativeBalanceError(moneybox_id=moneybox_id, balance=balance)

        moneybox = await read_instance(
            async_session=self.async_session,
            orm_model=Moneybox,  # type: ignore
            record_id=moneybox_id,
        )

        if moneybox is None:
            raise MoneyboxNotFoundError(moneybox_id=moneybox_id)

        moneybox.balance += balance  # type: ignore

        updated_moneybox = await update_instance(
            async_session=self.async_session,
            orm_model=Moneybox,  # type: ignore
            record_id=moneybox_id,
            data=moneybox.asdict(),
        )

        # should not be possible to reach this block
        if updated_moneybox is None:
            raise MoneyboxNotFoundError(moneybox_id=moneybox_id)

        return updated_moneybox.asdict()

    async def sub_balance(
        self,
        moneybox_id: int,
        balance: int,
    ) -> dict[str, Any]:
        """DB Function to sub balance from moneybox by moneybox_id.

        :param moneybox_id: The id of the moneybox.
        :type moneybox_id: :class:`int`
        :param balance: The balance to sub from given moneybox.
        :type balance: :class:`int`

        :return: The updated moneybox data.
        :rtype: :class:`dict[str, Any]`

        :raises: :class:`MoneyboxNotFoundError`: if given moneybox_id
                    was not found in database.
                 :class:`NegativeBalanceError`:
                    if balance to sub  is negative.
                 :class:`BalanceResultIsNegativeError`:
                    if result of withdraw is negative.
        """

        if balance < 0:
            raise NegativeBalanceError(moneybox_id=moneybox_id, balance=balance)

        moneybox = await read_instance(
            async_session=self.async_session,
            orm_model=Moneybox,  # type: ignore
            record_id=moneybox_id,
        )

        if moneybox is None:
            raise NegativeBalanceError(moneybox_id=moneybox_id, balance=balance)

        moneybox.balance -= balance  # type: ignore

        if moneybox.balance < 0:  # type: ignore
            raise BalanceResultIsNegativeError(moneybox_id=moneybox_id, balance=balance)

        updated_moneybox = await update_instance(
            async_session=self.async_session,
            orm_model=Moneybox,  # type: ignore
            record_id=moneybox_id,
            data=moneybox.asdict(),
        )

        # should not be possible to reach this block
        if updated_moneybox is None:
            raise MoneyboxNotFoundError(moneybox_id=moneybox_id)

        return updated_moneybox.asdict()

    async def transfer_balance(
        self,
        from_moneybox_id: int,
        to_moneybox_id: int,
        balance: int,
    ) -> None:
        """DB Function to transfer `balance` from `from_moneybox_id`
        from `to_moneybox_id`.

        :param from_moneybox_id: The source id of the moneybox where the balance comes from.
        :type from_moneybox_id: :class:`int`
        :param to_moneybox_id: The target id of the moneybox where the balance shall
            be transferred to.
        :type to_moneybox_id: :class:`int`
        :param balance: The balance to transfer.
        :type balance: :class:`int`

        :raises: :class:`NegativeTransferBalanceError`:
                    if balance to transfer is negative.
                 :class:`BalanceResultIsNegativeError`:
                    if result of withdraws from_moneybox_id is negative.
        """

        if balance < 0:
            raise NegativeTransferBalanceError(
                from_moneybox_id=from_moneybox_id,
                to_moneybox_id=to_moneybox_id,
                balance=balance,
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
            new_from_moneybox_data = {"balance": from_moneybox.balance - balance}

            if new_from_moneybox_data["balance"] < 0:
                raise BalanceResultIsNegativeError(moneybox_id=from_moneybox_id, balance=balance)

            new_to_moneybox_data = {"balance": to_moneybox.balance + balance}

            await session.execute(
                update(Moneybox)
                .where(Moneybox.id == from_moneybox_id)
                .values(new_from_moneybox_data)
            )
            await session.execute(
                update(Moneybox).where(Moneybox.id == to_moneybox_id).values(new_to_moneybox_data)
            )
