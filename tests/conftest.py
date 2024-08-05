"""Pytest configurations and fixtures are located here."""

import os
import time
from functools import partial
from pathlib import Path
import subprocess
from typing import AsyncGenerator

import pytest
from _pytest.fixtures import FixtureRequest
from alembic import command, context
from alembic.config import Config
from alembic.runtime.environment import EnvironmentContext
from alembic.script import ScriptDirectory
from dotenv import load_dotenv
from httpx import AsyncClient
from sqlalchemy import text

from src.constants import WORKING_DIR
from src.custom_types import DBSettings, TransactionTrigger, TransactionType
from src.db.db_manager import DBManager
from src.db.models import Base
from src.main import app, register_router
from src.utils import get_db_settings
from tests.utils.db_test_data_initializer import DBTestDataInitializer

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
async def default_test_data(db_manager: DBManager) -> None:
    """The default test data fixture.

    Loads a fix dataset of testdata.

    :param db_manager: The database manager.
    :type db_manager: :class:`DBManager`
    """

    await db_manager.truncate_tables()  # type: ignore

    # add 5 moneyboxes
    moneyboxes_data = [
        {"name": "Moneybox 1"},  # id: 1
        {"name": "Moneybox 2"},  # id: 2
        {"name": "Moneybox 3"},  # id: 3
        {"name": "Moneybox 4"},  # id: 4
        {"name": "Moneybox 5"},  # id: 5
    ]

    for moneybox_data in moneyboxes_data:
        await db_manager.add_moneybox(
            moneybox_data=moneybox_data,
        )

    # Moneybox 1
    # 3x add / 1x transfer -> Moneybox 3
    await db_manager.add_amount(
        moneybox_id=1,
        deposit_transaction_data={"amount": 1000, "description": ""},
        transaction_type=TransactionType.DIRECT,
        transaction_trigger=TransactionTrigger.MANUALLY,
    )
    await db_manager.add_amount(
        moneybox_id=1,
        deposit_transaction_data={"amount": 333, "description": ""},
        transaction_type=TransactionType.DIRECT,
        transaction_trigger=TransactionTrigger.MANUALLY,
    )
    await db_manager.add_amount(
        moneybox_id=1,
        deposit_transaction_data={"amount": 2000, "description": ""},
        transaction_type=TransactionType.DIRECT,
        transaction_trigger=TransactionTrigger.MANUALLY,
    )
    await db_manager.transfer_amount(
        from_moneybox_id=1,
        transfer_transaction_data={"to_moneybox_id": 3, "amount": 3000, "description": ""},
        transaction_type=TransactionType.DIRECT,
        transaction_trigger=TransactionTrigger.MANUALLY,
    )

    # Moneybox 2
    # 2x add / 3x sub
    await db_manager.add_amount(
        moneybox_id=2,
        deposit_transaction_data={"amount": 6000, "description": ""},
        transaction_type=TransactionType.DIRECT,
        transaction_trigger=TransactionTrigger.MANUALLY,
    )
    await db_manager.sub_amount(
        moneybox_id=2,
        withdraw_transaction_data={"amount": 500, "description": ""},
        transaction_type=TransactionType.DIRECT,
        transaction_trigger=TransactionTrigger.MANUALLY,
    )
    await db_manager.sub_amount(
        moneybox_id=2,
        withdraw_transaction_data={"amount": 600, "description": ""},
        transaction_type=TransactionType.DIRECT,
        transaction_trigger=TransactionTrigger.MANUALLY,
    )
    await db_manager.add_amount(
        moneybox_id=2,
        deposit_transaction_data={"amount": 5000, "description": ""},
        transaction_type=TransactionType.DIRECT,
        transaction_trigger=TransactionTrigger.MANUALLY,
    )
    await db_manager.sub_amount(
        moneybox_id=2,
        withdraw_transaction_data={"amount": 900, "description": ""},
        transaction_type=TransactionType.DIRECT,
        transaction_trigger=TransactionTrigger.MANUALLY,
    )

    # Moneybox 3
    # 1x add / 2x sub / 1x transfer -> Moneybox 4
    await db_manager.add_amount(
        moneybox_id=3,
        deposit_transaction_data={"amount": 10_000, "description": ""},
        transaction_type=TransactionType.DIRECT,
        transaction_trigger=TransactionTrigger.MANUALLY,
    )
    await db_manager.sub_amount(
        moneybox_id=3,
        withdraw_transaction_data={"amount": 900, "description": ""},
        transaction_type=TransactionType.DIRECT,
        transaction_trigger=TransactionTrigger.MANUALLY,
    )
    await db_manager.transfer_amount(
        from_moneybox_id=3,
        transfer_transaction_data={"to_moneybox_id": 4, "amount": 5000, "description": ""},
        transaction_type=TransactionType.DIRECT,
        transaction_trigger=TransactionTrigger.MANUALLY,
    )
    await db_manager.sub_amount(
        moneybox_id=3,
        withdraw_transaction_data={"amount": 900, "description": ""},
        transaction_type=TransactionType.DIRECT,
        transaction_trigger=TransactionTrigger.MANUALLY,
    )

    # Moneybox 4
    # 1x add / 1x sub / 2x transfer -> Moneyboxes 1 + 3
    await db_manager.add_amount(
        moneybox_id=4,
        deposit_transaction_data={"amount": 20_000, "description": ""},
        transaction_type=TransactionType.DIRECT,
        transaction_trigger=TransactionTrigger.MANUALLY,
    )
    await db_manager.transfer_amount(
        from_moneybox_id=4,
        transfer_transaction_data={"to_moneybox_id": 1, "amount": 15000, "description": ""},
        transaction_type=TransactionType.DIRECT,
        transaction_trigger=TransactionTrigger.MANUALLY,
    )
    await db_manager.sub_amount(
        moneybox_id=4,
        withdraw_transaction_data={"amount": 2000, "description": ""},
        transaction_type=TransactionType.DIRECT,
        transaction_trigger=TransactionTrigger.MANUALLY,
    )
    await db_manager.transfer_amount(
        from_moneybox_id=4,
        transfer_transaction_data={"to_moneybox_id": 3, "amount": 8000, "description": ""},
        transaction_type=TransactionType.DIRECT,
        transaction_trigger=TransactionTrigger.MANUALLY,
    )

    await db_manager.delete_moneybox(moneybox_id=4)


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
        db_environment="test", db_driver="sqlite+aiosqlite", db_file="test_database.sqlite3"
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

    # alembic_ini_path = (Path(__file__).parent.parent / "alembic.ini").resolve().absolute()
    # alembic_cfg = Config(str(alembic_ini_path))  # Adjust the path to your alembic.ini file

    # Dynamically update the sqlalchemy.url
    # alembic_cfg.set_main_option("sqlalchemy.url", str(db_manager.db_connection_string))

    # Upgrade the database using Alembic
    # async with db_manager.async_engine.begin() as conn:
    #    await conn.run_sync(Base.metadata.create_all)
    #    await conn.run_sync(run_migrations, alembic_cfg, "upgrade", "head")
    #    print("Database tables created with Alembic migrations.", flush=True)

    # create db tables and apply all db migrations
    subprocess.Popen(("alembic", "-x", "testing", "upgrade", "head"))
    time.sleep(2)

    yield db_manager

    time.sleep(2)
    # downgrade the test database to base
    subprocess.Popen(("alembic", "-x", "testing", "downgrade", "base"))

    # Downgrade the database using Alembic
    # async with db_manager.async_engine.begin() as conn:
    #    await conn.run_sync(Base.metadata.drop_all)
    #    print("Database tables dropped with Alembic migrations.", flush=True)

    print("DB Manager removed.", flush=True)
