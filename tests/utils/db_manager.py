"""The utils module of the db_manager."""

from typing import cast

from sqlalchemy import Result, Select, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.db.exceptions import MoneyboxNotFoundByNameError
from src.db.models import Moneybox


async def get_moneybox_id_by_name(
    async_session: async_sessionmaker | AsyncSession,
    name: str,
    only_active_instances: bool = True,
) -> int:
    """Helper function to get moneybox id for the given name.

    :param async_session: The current async_session of the database or a session_maker,
        which shall used to create the async_session.
    :type async_session: :class:`async_sessionmaker | AsyncSession`
    :param name: The name of the moneybox.
    :type name: :class:`str`
    :param only_active_instances: If True, only active moneyboxes will be
        returned, default to True.
    :type only_active_instances: :class:`bool`
    :return: The moneybox id for the given name.
    :rtype: :class:`int`

    :raises: :class:`MoneyboxNotFoundError`: if given moneybox name
        was not found in database.
    """

    stmt: Select = select(Moneybox).where(  # type: ignore
        Moneybox.name == name,
    )

    if only_active_instances:
        stmt = stmt.where(Moneybox.is_active.is_(True))

    if isinstance(async_session, AsyncSession):
        result: Result = await async_session.execute(stmt)  # type: ignore
    else:
        async with async_session() as session:
            result: Result = await session.execute(stmt)  # type: ignore

    moneybox: Moneybox | None = cast(
        Moneybox,
        result.scalars().one_or_none(),
    )

    if moneybox is None:
        raise MoneyboxNotFoundByNameError(name=name)

    return moneybox.id
