"""All database definitions are located here."""

from typing import Any

from sqlalchemy import insert
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.db.models import MoneyBox
from src.utils import get_database_url

async_engine = create_async_engine(url=get_database_url())
async_session = async_sessionmaker(bind=async_engine, expire_on_commit=False)


class DBManager:  # pylint: disable=too-few-public-methods
    """The Database Manager with all CRUD methods."""

    def __init__(self) -> None:
        print("DB_Manager created.", flush=True)

    async def add_moneybox(self, moneybox_data: dict[str, Any]) -> dict[str, Any]:
        """DB Function to add a new moneybox into database.

        :param moneybox_data: The moneybox data.
        :type moneybox_data: dict[str, Any]

        :return: The added moneybox data.
        :rtype: dict[str, Any]
        """

        stmt = insert(MoneyBox).values(**moneybox_data).returning(MoneyBox)

        async with async_session.begin() as session:
            result = await session.execute(stmt)

        moneybox = result.scalars().one()
        return moneybox.asdict()
