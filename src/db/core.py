"""DB core functionalities are located here."""

from typing import Any

from sqlalchemy import Sequence, and_, delete, exists, func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.db.exceptions import ColumnDoesNotExistError
from src.db.models import SqlBase


async def exists_instance(
    async_session: async_sessionmaker,
    orm_model: SqlBase,
    values: dict[str, Any],
    exclude_ids: list[int] | None = None,
) -> bool:
    """Checks whether an instance exists in the database by given `values`.

    :param async_session: The current async_session of the database.
    :type async_session: :class:`async_sessionmaker`
    :param orm_model: The orm model to handle with (table).
    :type orm_model: :class:`SqlBase`
    :param values: The key-values data used for the where-clause.
    :type values: :class:`dict[str, Any]`
    :param exclude_ids: The list of record ids to exclude from the exist query.
    :type exclude_ids: :class:`list[int] | None`
    :return: The created db instance.
    :rtype: :class:`bool`
    """

    if exclude_ids is None:
        exclude_ids = []

    stmt = select(orm_model).where(
        and_(
            orm_model.is_active.is_(True),
            orm_model.id.notin_(exclude_ids),
        )
    )

    for column, value in values.items():
        orm_field = getattr(orm_model, column, None)

        if orm_field is None:
            raise ColumnDoesNotExistError(table=orm_model.__name__, column=column)

        if orm_field == "name":
            stmt = stmt.where(orm_field == value)

        stmt = stmt.where(func.lower(orm_field) == func.lower(value))

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
    only_active_instances: bool = True,
) -> SqlBase | None:
    """The core SELECT db function.

    :param async_session: The current async_session of the database.
    :type async_session: :class:`async_sessionmaker`
    :param orm_model: The orm model to handle with (table).
    :type orm_model: :class:`SqlBase`
    :param record_id: The instance id.
    :type record_id: :class:`int`
    :param only_active_instances: If true, only active instances will be returned (is_active=True).
        If false, inclusive inactive instances will be returned (is_active=False).
    :type only_active_instances: :class:`bool`
    :return: The requested db instance
        or None, if given record_id does not exist.
    :rtype: :class:`SqlBase | None`
    """

    if only_active_instances:
        stmt = select(orm_model).where(
            and_(orm_model.id == record_id, orm_model.is_active.is_(True))
        )
    else:
        stmt = select(orm_model).where(orm_model.id == record_id)

    async with async_session.begin() as session:
        result = await session.execute(stmt)

    instance = result.scalars().one_or_none()
    return instance


async def read_instances(
    async_session: async_sessionmaker,
    orm_model: SqlBase,
    only_active_instances: bool = True,
) -> Sequence[SqlBase]:
    """The core multi SELECT db function.

    :param async_session: The current async_session of the database.
    :type async_session: :class:`async_sessionmaker`
    :param orm_model: The orm model to handle with (table).
    :type orm_model: :class:`SqlBase`
    :param only_active_instances: If true, only active instances will be returned (is_active=True).
        If false, inclusive inactive instances will be returned (is_active=False).
    :type only_active_instances: :class:`bool`
    :return: The requested db instances as list
        or None, if no instances available.
    :rtype: :class:`Sequence[SqlBase]`
    """

    if only_active_instances:
        stmt = select(orm_model).where(orm_model.is_active.is_(True))
    else:
        stmt = select(orm_model)

    async with async_session() as session:
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


async def deactivate_instance(
    async_session: async_sessionmaker,
    orm_model: SqlBase,
    record_id: int,
) -> bool:
    """The core deactivate db function. Specific update function to set `ìs_active`
    column to false.

    :param async_session: The current async_session of the database.
    :type async_session: :class:`async_sessionmaker`
    :param orm_model: The orm model to handle with (table).
    :type orm_model: :class:`SqlBase`
    :param record_id: The instance id.
    :type record_id: :class:`int`

    :return: If deactivated successfully, returns True, otherwise returns False.
    :rtype: :class:`bool`
    """

    active_moneybox = await read_instance(
        async_session=async_session,
        orm_model=orm_model,
        record_id=record_id,
    )

    if active_moneybox is not None:
        stmt = (
            update(orm_model)
            .where(orm_model.id == record_id)
            .values(is_active=False)
            .returning(orm_model)
        )

        if isinstance(async_session, AsyncSession):
            result = await async_session.execute(stmt)
        else:
            async with async_session.begin() as session:
                result = await session.execute(stmt)

        updated_instance = result.scalars().one_or_none()

        if updated_instance is not None:
            return True

    return False


async def activate_instance(
    async_session: async_sessionmaker,
    orm_model: SqlBase,
    record_id: int,
) -> bool:
    """The core activate db function. Specific update function to set `ìs_active`
    column to true.

    :param async_session: The current async_session of the database.
    :type async_session: :class:`async_sessionmaker`
    :param orm_model: The orm model to handle with (table).
    :type orm_model: :class:`SqlBase`
    :param record_id: The instance id.
    :type record_id: :class:`int`

    :return: If activated successfully, returns True, otherwise returns False.
    :rtype: :class:`bool`
    """

    moneybox = await read_instance(
        async_session=async_session,
        orm_model=orm_model,
        record_id=record_id,
        only_active_instances=False,
    )

    if moneybox is not None and not moneybox.is_active:
        stmt = (
            update(orm_model)
            .where(orm_model.id == record_id)
            .values(is_active=True)
            .returning(orm_model)
        )

        if isinstance(async_session, AsyncSession):
            result = await async_session.execute(stmt)
        else:
            async with async_session.begin() as session:
                result = await session.execute(stmt)

        updated_instance = result.scalars().one_or_none()

        if updated_instance is not None:
            return True

    return False
