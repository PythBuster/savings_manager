"""Pytest configurations and fixtures are located here."""

import asyncio
import subprocess
import time
from functools import partial
from pathlib import Path
from typing import AsyncGenerator

import pytest_asyncio
from _pytest.fixtures import FixtureRequest
from httpx import AsyncClient

from src.constants import WORKING_DIR
from src.custom_types import AppEnvVariables, TransactionTrigger, TransactionType
from src.db.db_manager import DBManager
from src.db.models import Base
from src.limiter import limiter
from src.main import app, register_router, set_custom_openapi_schema
from src.report_sender.email_sender.sender import EmailSender
from tests.utils.db_test_data_initializer import DBTestDataInitializer

pytest_plugins = ("pytest_asyncio",)
"""The pytest plugins which should be used to run tests."""

dotenv_path = Path(__file__).resolve().parent.parent / "envs" / ".env.test"
"""The test env file path."""

app_env_variables = AppEnvVariables(
    _env_file=dotenv_path,
)
"""The database settings."""


@pytest_asyncio.fixture(scope="session")
def event_loop() -> asyncio.AbstractEventLoop:  # type: ignore
    """Needed for https://github.com/igortg/pytest-async-sqlalchemy"""
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def default_test_data(db_manager: DBManager) -> None:
    """The default test data fixture.
    delete_moneybox
        Loads a fix dataset of testdata.

        :param db_manager: The database manager.
        :type db_manager: :class:`DBManager`
    """

    await db_manager.truncate_tables()  # type: ignore

    overflow_moneybox_data = {
        "name": "Overflow Moneybox",
        "savings_amount": 0,
        "savings_target": None,
    }
    overflow_moneybox = await db_manager._add_overflow_moneybox(  # noqa: ignore  # pylint: disable=line-too-long, protected-access
        moneybox_data=overflow_moneybox_data
    )
    moneyboxes = [overflow_moneybox]

    # add 5 moneyboxes + initial overflow moneybox
    moneyboxes_data = [
        {"name": "Moneybox 1"},  # id: 2
        {"name": "Moneybox 2"},  # id: 3
        {"name": "Moneybox 3"},  # id: 4
        {"name": "Moneybox 4"},  # id: 5
        {"name": "Moneybox 5"},  # id: 6
    ]

    for moneybox_data in moneyboxes_data:
        moneybox = await db_manager.add_moneybox(
            moneybox_data=moneybox_data,
        )
        moneyboxes.append(moneybox)

    time.sleep(1)

    # Moneybox 1 (id=2)
    # 3x add / 1x transfer -> Moneybox 3
    await db_manager.add_amount(
        moneybox_id=moneyboxes[1]["id"],
        deposit_transaction_data={"amount": 1000, "description": ""},
        transaction_type=TransactionType.DIRECT,
        transaction_trigger=TransactionTrigger.MANUALLY,
    )
    await db_manager.add_amount(
        moneybox_id=moneyboxes[1]["id"],
        deposit_transaction_data={"amount": 333, "description": ""},
        transaction_type=TransactionType.DIRECT,
        transaction_trigger=TransactionTrigger.MANUALLY,
    )
    await db_manager.add_amount(
        moneybox_id=moneyboxes[1]["id"],
        deposit_transaction_data={"amount": 2000, "description": ""},
        transaction_type=TransactionType.DIRECT,
        transaction_trigger=TransactionTrigger.MANUALLY,
    )
    await db_manager.transfer_amount(
        from_moneybox_id=moneyboxes[1]["id"],
        transfer_transaction_data={
            "to_moneybox_id": moneyboxes[3]["id"],
            "amount": 3000,
            "description": "",
        },
        transaction_type=TransactionType.DIRECT,
        transaction_trigger=TransactionTrigger.MANUALLY,
    )

    # Moneybox 2 (id=3)
    # 2x add / 3x sub
    await db_manager.add_amount(
        moneybox_id=moneyboxes[2]["id"],
        deposit_transaction_data={"amount": 6000, "description": ""},
        transaction_type=TransactionType.DIRECT,
        transaction_trigger=TransactionTrigger.MANUALLY,
    )
    await db_manager.sub_amount(
        moneybox_id=moneyboxes[2]["id"],
        withdraw_transaction_data={"amount": 500, "description": ""},
        transaction_type=TransactionType.DIRECT,
        transaction_trigger=TransactionTrigger.MANUALLY,
    )
    await db_manager.sub_amount(
        moneybox_id=moneyboxes[2]["id"],
        withdraw_transaction_data={"amount": 600, "description": ""},
        transaction_type=TransactionType.DIRECT,
        transaction_trigger=TransactionTrigger.MANUALLY,
    )
    await db_manager.add_amount(
        moneybox_id=moneyboxes[2]["id"],
        deposit_transaction_data={"amount": 5000, "description": ""},
        transaction_type=TransactionType.DIRECT,
        transaction_trigger=TransactionTrigger.MANUALLY,
    )
    await db_manager.sub_amount(
        moneybox_id=moneyboxes[2]["id"],
        withdraw_transaction_data={"amount": 900, "description": ""},
        transaction_type=TransactionType.DIRECT,
        transaction_trigger=TransactionTrigger.MANUALLY,
    )

    # Moneybox 3 (id=4)
    # 1x add / 2x sub / 1x transfer -> Moneybox 4
    await db_manager.add_amount(
        moneybox_id=moneyboxes[3]["id"],
        deposit_transaction_data={"amount": 10_000, "description": ""},
        transaction_type=TransactionType.DIRECT,
        transaction_trigger=TransactionTrigger.MANUALLY,
    )
    await db_manager.sub_amount(
        moneybox_id=moneyboxes[3]["id"],
        withdraw_transaction_data={"amount": 900, "description": ""},
        transaction_type=TransactionType.DIRECT,
        transaction_trigger=TransactionTrigger.MANUALLY,
    )
    await db_manager.transfer_amount(
        from_moneybox_id=moneyboxes[3]["id"],
        transfer_transaction_data={
            "to_moneybox_id": moneyboxes[4]["id"],
            "amount": 5000,
            "description": "",
        },
        transaction_type=TransactionType.DIRECT,
        transaction_trigger=TransactionTrigger.MANUALLY,
    )
    await db_manager.sub_amount(
        moneybox_id=moneyboxes[3]["id"],
        withdraw_transaction_data={"amount": 900, "description": ""},
        transaction_type=TransactionType.DIRECT,
        transaction_trigger=TransactionTrigger.MANUALLY,
    )

    # Moneybox 4 (id=5)
    # 1x add / 1x sub / 2x transfer -> Moneyboxes 1 + 3
    await db_manager.add_amount(
        moneybox_id=moneyboxes[4]["id"],
        deposit_transaction_data={"amount": 20_000, "description": ""},
        transaction_type=TransactionType.DIRECT,
        transaction_trigger=TransactionTrigger.MANUALLY,
    )
    await db_manager.transfer_amount(
        from_moneybox_id=moneyboxes[4]["id"],
        transfer_transaction_data={
            "to_moneybox_id": moneyboxes[1]["id"],
            "amount": 15000,
            "description": "",
        },
        transaction_type=TransactionType.DIRECT,
        transaction_trigger=TransactionTrigger.MANUALLY,
    )
    await db_manager.sub_amount(
        moneybox_id=moneyboxes[4]["id"],
        withdraw_transaction_data={"amount": 2000, "description": ""},
        transaction_type=TransactionType.DIRECT,
        transaction_trigger=TransactionTrigger.MANUALLY,
    )
    await db_manager.transfer_amount(
        from_moneybox_id=moneyboxes[4]["id"],
        transfer_transaction_data={
            "to_moneybox_id": moneyboxes[3]["id"],
            "amount": 8000,
            "description": "",
        },
        transaction_type=TransactionType.DIRECT,
        transaction_trigger=TransactionTrigger.MANUALLY,
    )

    # Delete Moneybox 4
    await db_manager.delete_moneybox(moneybox_id=moneyboxes[4]["id"])

    # Moneybox 5 (id=6)
    # NO TRANSACTIONS!

    time.sleep(1)


@pytest_asyncio.fixture(scope="function")
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


@pytest_asyncio.fixture(scope="session", name="smtp_settings")
async def mocked_smtp_settings(db_settings_1: AppEnvVariables) -> AsyncGenerator:
    """SMTP settings fixture"""

    yield db_settings_1


@pytest_asyncio.fixture(scope="session", name="email_sender")
async def mocked_email_sender(
    db_manager: DBManager,
    smtp_settings: AppEnvVariables,
) -> AsyncGenerator:
    """The email sender fixture."""

    email_sender = EmailSender(
        db_manager=db_manager,
        smtp_settings=smtp_settings,
    )
    # email_sender._send_message = lambda *args, **kwargs: None
    yield email_sender


@pytest_asyncio.fixture(scope="session", name="client")
async def mocked_client(db_manager: DBManager, email_sender: EmailSender) -> AsyncGenerator:
    """A fixture that creates a fastapi test client.

    :return: A test client.
    :rtype: AsyncGenerator
    """

    set_custom_openapi_schema(fastapi_app=app)
    register_router(fastapi_app=app)

    # Load fixtures
    print("Mock states ...", flush=True)
    app.state.db_manager = db_manager
    app.state.email_sender = email_sender
    app.state.limiter = limiter

    async with AsyncClient(app=app, base_url="http://127.0.0.1:8999") as client:
        yield client


@pytest_asyncio.fixture(scope="session", name="db_settings_1")
async def example_1_db_settings() -> AsyncGenerator:
    """A fixture to create example db_settings data.

    :return: db_settings example 1.
    :rtype: AsyncGenerator
    """

    yield AppEnvVariables(
        environment="test",
        db_driver="postgresql+asyncpg",
        db_name="test_db",
        db_host="mylocalhost",
        db_port=1234,
        db_user="postgres",
        db_password="<PASSWORD>",
        smtp_server="mylocalsmtp",
        smtp_method="TLS",
        smtp_port=1225,
        smtp_user_name="smtp user",
        smtp_password="<PASSWORD>",
    )


@pytest_asyncio.fixture(scope="session", name="db_manager")
async def mocked_db_manager() -> DBManager:  # type: ignore
    """A fixture to create the db_manager.

    :return: The DBManager connected to the test database.
    :rtype: AsyncGenerator
    """

    print("Start docker with test database...", flush=True)
    subprocess.call(
        [
            "sh",
            f"{WORKING_DIR.parent / 'scripts' / 'up_test_database.sh'}",
        ]
    )
    wait_for_docker = 5
    print(f"Wait for DB up for {wait_for_docker} seconds...", flush=True)
    time.sleep(wait_for_docker)

    db_manager = DBManager(
        db_settings=app_env_variables,
        engine_args={"echo": True},
    )

    async def truncate_tables(
        self: DBManager, exclude_table_names: list[str] | None = None
    ) -> None:
        """Truncate all tables."""

        if exclude_table_names is None:
            exclude_table_names = []

        async with self.async_session.begin() as session:
            for table in Base.metadata.sorted_tables:
                if table.name not in exclude_table_names:
                    await session.execute(table.delete())

    # add truncate tables help function for tests to database manager
    db_manager.truncate_tables = partial(truncate_tables, db_manager)  # type: ignore

    # clear db if not cleared in last test session
    subprocess.call(("alembic", "-x", "testing", "downgrade", "base"))
    time.sleep(1)
    # drop tables
    async with db_manager.async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    time.sleep(2)

    # create db tables and apply all db migrations
    subprocess.call(("alembic", "-x", "testing", "upgrade", "head"))
    time.sleep(2)

    yield db_manager

    # downgrade the test database to base
    subprocess.call(("alembic", "-x", "testing", "downgrade", "base"))
    time.sleep(1)
    # drop tables
    async with db_manager.async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    print("DB Manager removed.", flush=True)

    print("Stop docker with test database...", flush=True)
    subprocess.call(
        [
            "sh",
            f"{WORKING_DIR.parent / 'scripts' / 'down_test_database.sh'}",
        ]
    )
