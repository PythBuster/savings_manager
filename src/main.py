"""The start module of the savings manager app."""

from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

import uvicorn
from async_fastapi_jwt_auth.exceptions import AuthJWTException
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from slowapi.errors import RateLimitExceeded
from starlette.middleware.cors import CORSMiddleware

from src.constants import GENERAL_ENV_FILE_PATH
from src.custom_types import EnvironmentType
from src.db.db_manager import DBManager
from src.exception_handler import response_exception
from src.fastapi_metadata import tags_metadata
from src.fastapi_utils import handle_requests, register_router
from src.report_sender.email_sender.sender import EmailSender
from src.task_runner import BackgroundTaskRunner
from src.utils import get_app_data, get_app_env_variables

# load general environments (postgres_server.env.general file)
load_dotenv(dotenv_path=GENERAL_ENV_FILE_PATH)


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI) -> AsyncGenerator:
    """The fast api lifespan.

    :param fastapi_app: The FastAPI app instance.
    :type fastapi_app: :class:`FastAPI?
    :return: A fastapi/asnyc generator.
    :rtype: :class:`AsyncGenerator`
    """

    environment, app_env_variables = get_app_env_variables()  # pylint: disable=redefined-outer-name

    print(f"Register routers (id={id(fastapi_app)}) ...", flush=True)
    register_router(fastapi_app=fastapi_app)

    print("Initialize app states ...", flush=True)
    # create db_manager, email_sender and background task runner
    db_manager: DBManager = DBManager(
        db_settings=app_env_variables,
        engine_args={
            "echo": environment is EnvironmentType.DEV,
        },
    )
    email_sender: EmailSender = EmailSender(
        db_manager=db_manager,
        smtp_settings=app_env_variables,
    )
    background_tasks_runner: BackgroundTaskRunner = BackgroundTaskRunner(  # type: ignore
        db_manager=db_manager,
        email_sender=email_sender,
    )

    if environment is EnvironmentType.PROD:
        print("Start background tasks.")
        await background_tasks_runner.run()  # type: ignore

    fastapi_app.state.db_manager = db_manager
    fastapi_app.state.email_sender = email_sender
    fastapi_app.state.background_tasks_runner = background_tasks_runner

    yield

    await background_tasks_runner.stop_tasks()

    # deconstruct app here


app_data: dict[str, Any] = get_app_data()
"""Reference to the app data."""

author_name, author_mail = app_data["authors"][0].split()
"""Reference to the author's name and report_sender address.'"""

# Initialize the fastAPI app
app: FastAPI = FastAPI(
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

allowed_origins = [
    # production
    "http://192.168.2.100:64000",
    # dev
    "http://127.0.0.1:5173",
    "http://localhost:5173",
    "http://127.0.0.1:5000",
    "http://localhost:5000",
    "http://127.0.0.1:8001",
    "http://localhost:8001",
]
app.add_middleware(
    CORSMiddleware,  # type: ignore
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# override registered exception handler of
# - RateLimitExceeded
# - RequestValidationError
# - AuthJWTException
app.add_exception_handler(RateLimitExceeded, response_exception)
app.add_exception_handler(RequestValidationError, response_exception)
app.add_exception_handler(AuthJWTException, response_exception)

# handle requests and all other exceptions
app.middleware("http")(handle_requests)


if __name__ == "__main__":
    environment, _ = get_app_env_variables()

    print("Start uvicorn server ...", flush=True)
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8001,
        loop="auto",
        workers=1,
        reload=environment is EnvironmentType.DEV,
        access_log=environment is not EnvironmentType.PROD,
        # disable access log for prod
    )
    print("Stop uvicorn server.", flush=True)
