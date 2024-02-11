"""DB core CRUD functionalities are located here."""

from typing import Any

from sqlalchemy import delete, insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import SqlBase


async def create_instance(
    async_session: AsyncSession,
    orm_model: SqlBase,
    data: dict[str, Any],
) -> SqlBase:
    """The core CREATE db function.

    :param async_session: The current async_session of the database.
    :type async_session: AsyncSession
    :param orm_model: The orm model to handle with (table).
    :type orm_model: SqlBase
    :param data: The ORM model data.
    :type data: dict[str, Any]
    :return: The created db instance.
    :rtype: SqlBase
    """

    stmt = insert(orm_model).values(**data).returning(orm_model)

    async with async_session.begin() as session:
        result = await session.execute(stmt)

    db_instance = result.scalars().one()

    return db_instance


async def delete_instance(
    async_session: AsyncSession,
    orm_model: SqlBase,
    record_id: int,
) -> int:
    """The core DELETE db function. Delete database record in orm_model by given id.

    :param async_session: The current async_session of the database.
    :type async_session: AsyncSession
    :param orm_model: The orm model to handle with (table).
    :type orm_model: SqlBase
    :param record_id: The instance id.
    :type record_id: int
    :return: Amount of deleted rows.
    :rtype: int
    """

    stmt = delete(orm_model).where(orm_model.id == record_id)

    async with async_session.begin() as session:
        result = await session.execute(stmt)

    return result.rowcount
