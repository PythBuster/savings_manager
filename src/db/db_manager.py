"""All database definitions are located here."""

from typing import Any

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.custom_types import DBSettings
from src.db.core import create
from src.db.models import MoneyBox
from src.utils import get_database_url


class DBManager:
    """All db manager logic are located here."""

    def __init__(self, db_settings: DBSettings, engine_args: dict[str, Any] | None = None) -> None:
        if engine_args is None:
            engine_args = {}

        self.db_settings = db_settings
        self.async_engine = create_async_engine(url=self.db_connection_string, **engine_args)
        self.async_session = async_sessionmaker(bind=self.async_engine, expire_on_commit=False)

    @property
    def db_connection_string(self) -> str:
        """Property to create a database connection string based on db driver.

        :return: A db connection string.
        :rtype: str

        :raises: ValueError: if self.db_settings.db_driver is not supported.
        """

        return get_database_url(db_settings=self.db_settings)

    async def add_moneybox(self, moneybox_data: dict[str, Any]) -> dict[str, Any]:
        """DB Function to add a new moneybox into database.

        :param moneybox_data: The moneybox data.
        :type moneybox_data: dict[str, Any]

        :return: The added moneybox data.
        :rtype: dict[str, Any]
        """

        moneybox = await create(
            async_session=self.async_session,
            orm_model=MoneyBox,  # type: ignore
            data=moneybox_data,
        )

        return moneybox.asdict()
