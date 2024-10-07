"""DB core functionalities are located here."""

from typing import Any

from asyncpg import InvalidTextRepresentationError
from fastapi.encoders import jsonable_encoder
from sqlalchemy import (
    Insert,
    Result,
    Select,
    Sequence,
    Update,
    and_,
    insert,
    select,
    update,
)
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.db.exceptions import RecordNotFoundError, UpdateInstanceError, CreateInstanceError, DeleteInstanceError
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

    :raises: CreateInstanceError: if creating instance fails.
    """

    try:
        stmt: Insert = insert(orm_model).values(data).returning(orm_model)

        if isinstance(async_session, AsyncSession):
            result: Result = await async_session.execute(stmt)
            instance: SqlBase = result.scalars().one()
            await async_session.refresh(instance)
        else:
            async with async_session.begin() as session:
                result = await session.execute(stmt)
                instance = result.scalars().one()
    except Exception as ex:
        raise CreateInstanceError(
            message="Failed creating instance",
            details={
                "table": orm_model.__name__,
                "data": data,
            }
        ) from ex

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
        stmt: Select = select(orm_model).where(  # type: ignore
            and_(orm_model.id == record_id, orm_model.is_active.is_(True))  # type: ignore
        )
    else:
        stmt: Select = select(orm_model).where(orm_model.id == record_id)  # type: ignore

    if isinstance(async_session, AsyncSession):
        result: Result = await async_session.execute(stmt)  # type: ignore
    else:
        async with async_session.begin() as session:
            result: Result = await session.execute(stmt)  # type: ignore

    instance: SqlBase | None = result.scalars().one_or_none()
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
        stmt: Select = select(orm_model).where(  # type: ignore
            orm_model.is_active.is_(True)  # type: ignore
        )
    else:
        stmt: Select = select(orm_model)  # type: ignore

    if isinstance(async_session, AsyncSession):
        result: Result = await async_session.execute(stmt)  # type: ignore
    else:
        async with async_session.begin() as session:
            result: Result = await session.execute(stmt)  # type: ignore

    instances: Sequence[SqlBase] = result.scalars().all()
    return instances


async def update_instance(
    async_session: async_sessionmaker | AsyncSession,
    orm_model: SqlBase,
    record_id: int,
    data: dict[str, Any],
) -> SqlBase:
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

    :raises: :class:`UpdateInstanceError`: if updating instance fails.
             :class:`RecordNotFoundError`: if instance does not exist.
    """

    existing_instance: SqlBase | None = await read_instance(
        async_session=async_session,
        orm_model=orm_model,
        record_id=record_id,
    )

    if existing_instance is None:
        raise RecordNotFoundError(record_id=record_id, message="Record not found.")

    try:
        if "created_at" in data:
            del data["created_at"]

        if "modified_at" in data:
            del data["modified_at"]

        if "is_active" in data:
            del data["is_active"]

        stmt: Update = (
            update(orm_model).where(orm_model.id == record_id).values(data).returning(orm_model)
        )

        if isinstance(async_session, AsyncSession):
            result: Result = await async_session.execute(stmt)
            instance: SqlBase = result.scalars().one()
            await async_session.refresh(instance)
        else:
            async with async_session.begin() as session:
                result = await session.execute(stmt)
                instance = result.scalars().one()

    except Exception as ex:
        raise UpdateInstanceError(
            record_id=record_id,
            message="Failed updating instance",
            details={
                "table": orm_model.__name__,
                "data": data,
            }
        ) from ex

    return instance

async def deactivate_instance(
    async_session: async_sessionmaker | AsyncSession,
    orm_model: SqlBase,
    record_id: int,
) -> None:
    """The core deactivate db function. Specific update function to set `ìs_active`
    column to false.

    :param async_session: The current async_session of the database or a session_maker,
        which shall used to create the async_session.
    :type async_session: :class:`async_sessionmaker | AsyncSession`
    :param orm_model: The orm model to handle with (table).
    :type orm_model: :class:`SqlBase`
    :param record_id: The instance id.
    :type record_id: :class:`int`

    :raises: :class:`DeleteInstanceError`: if deleting instance fails.
             :class:`RecordNotFoundError`: if instance does not exist.
    """

    existing_instance: SqlBase | None = await read_instance(
        async_session=async_session,
        orm_model=orm_model,
        record_id=record_id,
    )

    if existing_instance is None:
        raise RecordNotFoundError(record_id=record_id, message="Record not found.")

    try:
        stmt: Update = (
            update(orm_model)
            .where(orm_model.id == record_id)
            .values(is_active=False)
            .returning(orm_model)
        )

        if isinstance(async_session, AsyncSession):
            result: Result = await async_session.execute(stmt)
            instance: SqlBase = result.scalars().one()
            await async_session.refresh(instance)
        else:
            async with async_session.begin() as session:
                _ = await session.execute(stmt)
    except Exception as ex:
        raise DeleteInstanceError(
            record_id=record_id,
            message="Failed updating instance",
            details={
                "table": orm_model.__name__,
            }
        ) from ex
