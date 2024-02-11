"""Pytest configurations and fixtures are located here."""

import os
from typing import AsyncGenerator

import pytest

from src.db.db_manager import DBManager
from src.db.models import Base
from src.utils import get_db_settings

pytest_plugins = ("pytest_asyncio",)


TEST_DB_DRIVER = "sqlite+aiosqlite"
os.environ["DB_DRIVER"] = TEST_DB_DRIVER
os.environ["IN_MEMORY"] = "1"


db_settings = get_db_settings()


@pytest.fixture(scope="session", name="db_manager")
async def mocked_db_manager() -> AsyncGenerator:
    """A fixture to create the db_manager.

    :return: The DBManager connected to the test database.
    :rtype: Generator
    """

    db_manager = DBManager(
        db_settings=db_settings,
        engine_args={"echo": True},
    )

    # create tables by using db_managers database async engine
    async with db_manager.async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("Database tables created.", flush=True)

    print("DB Manager created.", flush=True)
    yield db_manager
    print("DB Manager removed.", flush=True)

    # drop tables by using db_managers database async engine
    async with db_manager.async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        print("Database tables dropped.", flush=True)
