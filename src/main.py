"""The start module of the savings manager app."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI

from src.custom_types import Environment
from src.db.db_manager import DBManager
from src.fastapi_metadata import tags_metadata
from src.fastapi_utils import (
    create_pgpass,
    register_handler_and_middleware,
    register_router,
    set_custom_openapi_schema,
)
from src.limiter import limiter
from src.report_sender.email_sender.sender import EmailSender
from src.task_runner import BackgroundTaskRunner
from src.utils import get_app_data, get_app_env_variables


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI) -> AsyncGenerator:
    """The fast api lifespan."""

    app_env_variables = get_app_env_variables()  # pylint: disable=redefined-outer-name

    print("Create .pgpass for sql import/export functionality ...", flush=True)
    create_pgpass(app_env_variables=app_env_variables)

    print("Set custom openapi schema ...", flush=True)
    set_custom_openapi_schema(fastapi_app=fastapi_app)

    print(f"Register routers (id={id(fastapi_app)}) ...", flush=True)
    register_router(fastapi_app=fastapi_app)

    print("Initialize app states ...", flush=True)
    # create db_manager, email_sender and background task runner
    db_manager = DBManager(
        db_settings=app_env_variables,
        engine_args={
            "echo": app_env_variables.environment is Environment.DEV,
        },
    )
    email_sender = EmailSender(
        db_manager=db_manager,
        smtp_settings=app_env_variables,
    )
    background_tasks_runner = BackgroundTaskRunner(  # type: ignore
        db_manager=db_manager,
        email_sender=email_sender,
    )

    if app_env_variables.environment is Environment.PROD:
        print("Start background tasks.")
        await background_tasks_runner.run()  # type: ignore

    fastapi_app.state.db_manager = db_manager
    fastapi_app.state.email_sender = email_sender
    fastapi_app.state.background_tasks_runner = background_tasks_runner
    fastapi_app.state.limiter = limiter

    yield

    # deconstruct app here


app_data = get_app_data()
"""Reference to the app data."""

author_name, author_mail = app_data["authors"][0].split()
"""Reference to the author's name and report_sender address.'"""

# Initialize the fastAPI app
app = FastAPI(
    lifespan=lifespan,
    title=app_data["name"],
    description=app_data["description"],
    version=app_data["version"],
    contact={
        "name": author_name[1:-1],
        "email": author_mail[2:-2],
    },
    openapi_tags=tags_metadata,
    # swagger_ui_parameters={"defaultModelsExpandDepth": -1},
)
"""Reference to the fastapi app."""


if __name__ == "__main__":
    register_handler_and_middleware(fastapi_app=app)

    app_env_variables = get_app_env_variables()

    print("Start uvicorn server ...", flush=True)
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8001,
        loop="auto",
        workers=1,
        reload=app_env_variables.environment is Environment.DEV,
        access_log=app_env_variables.environment is not Environment.PROD,
        # disable access log for prod
    )
    print("Stop uvicorn server.", flush=True)
