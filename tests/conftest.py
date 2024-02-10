"""Pytest configurations and fixtures are located here."""

from typing import AsyncGenerator

import pytest
from _pytest.monkeypatch import MonkeyPatch
from pytest_asyncio.plugin import FixtureFunction, FixtureFunctionMarker
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.db.models import Base
from src.singleton import db_manager

TEST_DATABASE_URL = "sqlite+aiosqlite://"
async_engine = create_async_engine(url=TEST_DATABASE_URL, echo=True)


@pytest.fixture(scope="session")
async def async_session() -> AsyncGenerator:
    """Fixture to generate an async_session connected to
    the test-database.

    Before yielding the async_session, the tables will be created in
    the database.

    :return: An async_session connected to the test-database.
    :rtype: Generator
    """

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("Database tables created.", flush=True)

    yield async_sessionmaker(bind=async_engine, expire_on_commit=False)

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        print("Database tables dropped.", flush=True)


@pytest.fixture(scope="session", name="db_manager")
async def mocked_db_manager(
    async_session: FixtureFunctionMarker | FixtureFunction,
) -> AsyncGenerator:
    """A fixture that patches the async_session of the db_manager.

    :return: The mocked DBManager
    :rtype: Generator
    """

    with MonkeyPatch.context() as m_patch:
        m_patch.setattr("src.db.db_manager.async_session", async_session)
        print("DB Manager created.", flush=True)
        yield db_manager
        print("DB Manager removed.", flush=True)
