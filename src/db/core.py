"""DB core functionalities are located here."""

from typing import Any

from sqlalchemy import Sequence, and_, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.db.models import SqlBase


async def create_instance(
    async_session: async_sessionmaker | AsyncSession,
    orm_model: SqlBase,
    data: dict[str, Any],
) -> SqlBase:
    """The core CREATE db function.

    :param async_session: The current async_session of the database or a session_maker,
        which shall used to create the async_session.
    :type async_session: :class:`async_sessionmaker | AsyncSession`
    :param orm_model: The orm model to handle with (table).
    :type orm_model: :class:`SqlBase`
    :param data: The ORM model data.
    :type data: :class:`dict[str, Any]`
    :return: The created db instance.
    :rtype: :class:`SqlBase`
    """

    stmt = insert(orm_model).values(data).returning(orm_model)

    if isinstance(async_session, AsyncSession):
        result = await async_session.execute(stmt)
    else:
        async with async_session.begin() as session:
            result = await session.execute(stmt)

    instance = result.scalars().one()
    return instance


async def read_instance(
    async_session: async_sessionmaker | AsyncSession,
    orm_model: SqlBase,
    record_id: int,
    only_active_instances: bool = True,
) -> SqlBase | None:
    """The core SELECT db function.

    :param async_session: The current async_session of the database or a session_maker,
        which shall used to create the async_session.
    :type async_session: :class:`async_sessionmaker | AsyncSession`
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

    if isinstance(async_session, AsyncSession):
        result = await async_session.execute(stmt)
    else:
        async with async_session.begin() as session:
            result = await session.execute(stmt)

    instance = result.scalars().one_or_none()
    return instance


async def read_instances(
    async_session: async_sessionmaker | AsyncSession,
    orm_model: SqlBase,
    only_active_instances: bool = True,
) -> Sequence[SqlBase]:
    """The core multi SELECT db function.

    :param async_session: The current async_session of the database or a session_maker,
        which shall used to create the async_session.
    :type async_session: :class:`async_sessionmaker | AsyncSession`
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

    if isinstance(async_session, AsyncSession):
        result = await async_session.execute(stmt)
    else:
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

    :param async_session: The current async_session of the database or a session_maker,
        which shall used to create the async_session.
    :type async_session: :class:`async_sessionmaker | AsyncSession`
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


async def deactivate_instance(
    async_session: async_sessionmaker | AsyncSession,
    orm_model: SqlBase,
    record_id: int,
) -> bool:
    """The core deactivate db function. Specific update function to set `ìs_active`
    column to false.

    :param async_session: The current async_session of the database or a session_maker,
        which shall used to create the async_session.
    :type async_session: :class:`async_sessionmaker | AsyncSession`
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
