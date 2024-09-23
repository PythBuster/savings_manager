"""The start module of the savings manager app."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from slowapi.errors import RateLimitExceeded
from starlette.middleware.cors import CORSMiddleware

from src.custom_types import Environment
from src.db.db_manager import DBManager
from src.exception_handler import response_exception
from src.fastapi_metadata import tags_metadata
from src.fastapi_utils import (
    create_pgpass,
    handle_requests,
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

    await background_tasks_runner.stop_tasks()

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

# register/override middlewares, exceptions handlers
print("Register/override middlewares, exceptions handlers ...", flush=True)

app.add_middleware(
    CORSMiddleware,  # type: ignore
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# override registered exception handler of
# - RateLimitExceeded
# - RequestValidationError
app.add_exception_handler(RateLimitExceeded, response_exception)
app.add_exception_handler(RequestValidationError, response_exception)

# handle requests and all other exceptions
app.middleware("http")(handle_requests)


if __name__ == "__main__":
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
