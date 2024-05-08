"""Pytest configurations and fixtures are located here."""

import os
from functools import partial
from pathlib import Path
from typing import AsyncGenerator

import pytest
from _pytest.fixtures import FixtureRequest
from dotenv import load_dotenv
from httpx import AsyncClient
from sqlalchemy import text

from src.custom_types import DBSettings
from src.db.db_manager import DBManager
from src.db.models import Base
from src.main import app, register_router
from src.utils import get_db_settings
from tests.db_test_data_initializer import DBTestDataInitializer

pytest_plugins = ("pytest_asyncio",)
"""The pytest plugins which should be used to run tests."""

dotenv_path = Path(__file__).resolve().parent.parent / "envs" / ".env.test"
"""The test env file path."""

load_dotenv(dotenv_path=dotenv_path)
print(f"Loaded {dotenv_path}")

TEST_DB_DRIVER = os.getenv("DB_DRIVER")
"""The database test driver environment variable."""

db_settings = get_db_settings()
"""The database settings."""


@pytest.fixture(scope="function")
async def load_test_data(request: FixtureRequest, db_manager: DBManager) -> None:
    """The load data fixture.

    :param request: The pytest fixture.
    :type request: :class:`pytest.FixtureRequest`
    :param db_manager: The database manager.
    :type db_manager: :class:`DBManager`
    """

    caller_name = request.node.name
    test_data_initializer_ = DBTestDataInitializer(
        db_manager=db_manager,
        test_case=caller_name,
    )
    await test_data_initializer_.run()


@pytest.fixture(scope="session", name="client")
async def mocked_client(db_manager: DBManager) -> AsyncGenerator:
    """A fixture that creates a fastapi test client.

    :return: A test client.
    :rtype: AsyncGenerator
    """

    register_router(fastapi_app=app)
    app.state.db_manager = db_manager

    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as client:
        yield client


@pytest.fixture(name="db_settings_1", scope="session")
async def example_1_db_settings() -> AsyncGenerator:
    """A fixture to create example db_settings data.

    :return: db_settings example 1.
    :rtype: AsyncGenerator
    """

    yield DBSettings(
        db_user="test_user",
        db_password="test_password",
        db_host="1.2.3.4",
        db_port=1234,
        db_name="test_db",
        db_driver="sqlite+aiosqlite",
    )


@pytest.fixture(scope="session", name="db_manager")
async def mocked_db_manager() -> AsyncGenerator:
    """A fixture to create the db_manager.

    :return: The DBManager connected to the test database.
    :rtype: AsyncGenerator
    """

    db_manager = DBManager(
        db_settings=db_settings,
        engine_args={"echo": True},
    )

    async def truncate_tables(self: DBManager) -> None:
        """Truncate all tables."""

        async with self.async_session.begin() as session:
            await session.execute(text("PRAGMA foreign_keys = OFF;"))

            for table in Base.metadata.sorted_tables:
                await session.execute(table.delete())

            await session.execute(text("PRAGMA foreign_keys = ON;"))

    db_manager.truncate_tables = partial(truncate_tables, db_manager)  # type: ignore

    # create tables by using db_managers database async engine
    async with db_manager.async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("Database tables created.", flush=True)

    yield db_manager

    # drop tables by using db_managers database async engine
    async with db_manager.async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        print("Database tables dropped.", flush=True)

    print("DB Manager removed.", flush=True)
