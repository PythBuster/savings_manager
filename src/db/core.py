"""DB core functionalities are located here."""

from typing import Any

from sqlalchemy import Sequence, delete, exists, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.db.exceptions import ColumnDoesNotExistError
from src.db.models import SqlBase


async def exists_instance(
    async_session: async_sessionmaker,
    orm_model: SqlBase,
    values: dict[str, Any],
) -> bool:
    """Checks whether an instance exists in the database by given `values`.

    :param async_session: The current async_session of the database.
    :type async_session: :class:`async_sessionmaker`
    :param orm_model: The orm model to handle with (table).
    :type orm_model: :class:`SqlBase`
    :param values: The key-values data used for the where-clausel.
    :return: The created db instance.
    :rtype: :class:`bool`
    """

    stmt = select(orm_model)

    for column, value in values.items():
        orm_field = getattr(orm_model, column, None)

        if orm_field is None:
            raise ColumnDoesNotExistError(table=orm_model.__name__, column=column)

        stmt = stmt.where(orm_field == value)

    exist_stmt = exists(stmt)
    async with async_session() as session:
        result = await session.execute(exist_stmt.select())

    exist = result.scalar_one()
    return exist


async def create_instance(
    async_session: async_sessionmaker,
    orm_model: SqlBase,
    data: dict[str, Any],
) -> SqlBase:
    """The core CREATE db function.

    :param async_session: The current async_session of the database.
    :type async_session: :class:`async_sessionmaker`
    :param orm_model: The orm model to handle with (table).
    :type orm_model: :class:`SqlBase`
    :param data: The ORM model data.
    :type data: :class:`dict[str, Any]`
    :return: The created db instance.
    :rtype: :class:`SqlBase`
    """

    stmt = insert(orm_model).values(data).returning(orm_model)

    async with async_session.begin() as session:
        result = await session.execute(stmt)

    instance = result.scalars().one()
    return instance


async def read_instance(
    async_session: async_sessionmaker,
    orm_model: SqlBase,
    record_id: int,
) -> SqlBase | None:
    """The core SELECT db function.

    :param async_session: The current async_session of the database.
    :type async_session: :class:`async_sessionmaker`
    :param orm_model: The orm model to handle with (table).
    :type orm_model: :class:`SqlBase`
    :param record_id: The instance id.
    :type record_id: :class:`int`
    :return: The requested db instance
        or None, if given record_id does not exist.
    :rtype: :class:`SqlBase | None`
    """

    stmt = select(orm_model).where(orm_model.id == record_id)

    async with async_session.begin() as session:
        result = await session.execute(stmt)

    instance = result.scalars().one_or_none()
    return instance


async def read_instances(
    async_session: async_sessionmaker,
    orm_model: SqlBase,
) -> Sequence[SqlBase]:
    """The core multi SELECT db function.

    :param async_session: The current async_session of the database.
    :type async_session: :class:`async_sessionmaker`
    :param orm_model: The orm model to handle with (table).
    :type orm_model: :class:`SqlBase`
    :return: The requested db instances as list
        or None, if no instances available.
    :rtype: :class:`Sequence[SqlBase]`
    """

    stmt = select(orm_model)

    async with async_session.begin() as session:
        result = await session.execute(stmt)

    instances = result.scalars().all()
    return instances


async def update_instance(
    async_session: async_sessionmaker | AsyncSession,
    orm_model: SqlBase,
    record_id: int,
    data: dict[str, Any],
) -> SqlBase | None:
    """The core UPDATE db function.

    :param async_session: The current async_session of the database.
    :type async_session: :class:`async_sessionmaker` | :class:`AsyncSession`
    :param orm_model: The orm model to handle with (table).
    :type orm_model: :class:`SqlBase`
    :param record_id: The instance id.
    :type record_id: :class:`int`
    :param data: The ORM updating model data.
    :type data: :class:`dict[str, Any]`
    :return: The updated db instance
        or None, if given record_id does not exist.
    :rtype: :class:`SqlBase | None`
    """

    if "created_at" in data:
        del data["created_at"]

    if "modified_at" in data:
        del data["modified_at"]

    if "is_active" in data:
        del data["is_active"]

    stmt = update(orm_model).where(orm_model.id == record_id).values(data).returning(orm_model)

    if isinstance(async_session, AsyncSession):
        result = await async_session.execute(stmt)
    else:
        async with async_session.begin() as session:
            result = await session.execute(stmt)

    instance = result.scalars().one_or_none()
    return instance


async def delete_instance(
    async_session: async_sessionmaker,
    orm_model: SqlBase,
    record_id: int,
) -> int:
    """The core DELETE db function. Delete database record in orm_model by given id.

    :param async_session: The current async_session of the database.
    :type async_session: :class:`async_sessionmaker`
    :param orm_model: The orm model to handle with (table).
    :type orm_model: :class:`SqlBase`
    :param record_id: The instance id.
    :type record_id: :class:`int`
    :return: Amount of deleted rows.
    :rtype: :class:`int`
    """

    stmt = delete(orm_model).where(orm_model.id == record_id)

    async with async_session.begin() as session:
        result = await session.execute(stmt)

    return result.rowcount
