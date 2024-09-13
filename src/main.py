"""The start module of the savings manager app."""

import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator, Callable

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from requests import Response
from slowapi.errors import RateLimitExceeded
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import FileResponse, JSONResponse
from starlette.staticfiles import StaticFiles

from src.constants import WEB_UI_DIRECTORY, WORKING_DIR
from src.custom_types import AppEnvVariables, EndpointRouteType, Environment
from src.db.db_manager import DBManager
from src.exception_handler import response_exception
from src.limiter import limiter
from src.report_sender.email_sender.sender import EmailSender
from src.routes.app import app_router
from src.routes.app_settings import app_settings_router
from src.routes.email_sender import email_sender_router
from src.routes.moneybox import moneybox_router
from src.routes.moneyboxes import moneyboxes_router
from src.routes.prioritylist import prioritylist_router
from src.routes.responses.custom_openapi_schema import custom_400_500_openapi_schema
from src.task_runner import BackgroundTaskRunner
from src.utils import get_app_data

tags_metadata = [
    {
        "name": "moneybox",
        "description": "All moneybox endpoints.",
    },
    {
        "name": "moneyboxes",
        "description": "All moneyboxes endpoints.",
    },
    {
        "name": "prioritylist",
        "description": "All prioritylist endpoints.",
    },
    {
        "name": "settings",
        "description": "All settings endpoints.",
    },
    {
        "name": "email",
        "description": "All email endpoints.",
    },
    {
        "name": "app",
        "description": "All general app endpoints.",
    },
]
"""Metadata about the endpoints."""

app_data = get_app_data()
"""Reference to the app data."""

author_name, author_mail = app_data["authors"][0].split()
"""Reference to the author's name and report_sender address.'"""

app_env_variables = AppEnvVariables(_env_file=WORKING_DIR.parent / "envs" / ".env")
"""The loaded env settings."""

@asynccontextmanager
async def lifespan(fastapi_app: FastAPI) -> AsyncGenerator:
    """The fast api lifespan."""

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
        }
    )
    email_sender = EmailSender(
        db_manager=db_manager,
        smtp_settings=app_env_variables,
    )
    background_tasks_runner = BackgroundTaskRunner(  # type: ignore
        db_manager=db_manager,
        email_sender=email_sender,
    )

    print("Start background tasks.")
    await background_tasks_runner.run()  # type: ignore

    fastapi_app.state.db_manager = db_manager
    fastapi_app.state.email_sender = email_sender
    fastapi_app.state.background_tasks_runner = background_tasks_runner
    fastapi_app.state.limiter = limiter

    yield

    # deconstruct app here


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
    debug=app_env_variables.environment is Environment.DEV,
    # swagger_ui_parameters={"defaultModelsExpandDepth": -1},
)
"""Reference to the fastapi app."""


# exception handler
async def handle_requests(request: Request, call_next: Callable) -> Response | JSONResponse:
    """Custom request handler as middleware, which will handle
    exceptions individually, which could arise.

    :param request: The current request.
    :param call_next: Callback to handle the request (route).
    :return: The route response or a mapped exception.
    :rtype: :class:`Response` | :class:`JSONResponse`
    """

    try:
        return await call_next(request)
    except Exception as ex:  # pylint:disable=broad-exception-caught
        return await response_exception(request, exception=ex)


# register/override middlewares, exceptions handlers
print("Register/override middlewares, exceptions handlers ...", flush=True)

# override registered exception handler of
# - RateLimitExceeded
# - RequestValidationError
app.add_exception_handler(RateLimitExceeded, response_exception)
app.add_exception_handler(RequestValidationError, response_exception)

# handle requests and all other exceptions
app.middleware("http")(handle_requests)

app.add_middleware(
    CORSMiddleware,  # type: ignore
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def set_custom_openapi_schema(fastapi_app: FastAPI) -> None:
    """Define the custom OpenAPI schema
        save original fastapi_app.openapi to call it later in mocked one.

    :param fastapi_app: The fast api app.
    :type fastapi_app: FastAPI
    """

    fastapi_app.openapi_original = fastapi_app.openapi
    fastapi_app.openapi = lambda: custom_400_500_openapi_schema(fastapi_app)


def register_router(fastapi_app: FastAPI) -> None:
    """Register routes to the FastAPI app.

    :param fastapi_app: The fast api app.
    :rtype fastapi_app: FastAPI
    """

    # router registrations
    fastapi_app.include_router(
        moneybox_router,
        prefix=f"/{EndpointRouteType.APP_ROOT}",
    )
    fastapi_app.include_router(
        moneyboxes_router,
        prefix=f"/{EndpointRouteType.APP_ROOT}",
    )
    fastapi_app.include_router(
        prioritylist_router,
        prefix=f"/{EndpointRouteType.APP_ROOT}",
    )
    fastapi_app.include_router(
        app_settings_router,
        prefix=f"/{EndpointRouteType.APP_ROOT}",
    )
    fastapi_app.include_router(
        email_sender_router,
        prefix=f"/{EndpointRouteType.APP_ROOT}",
    )
    fastapi_app.include_router(
        app_router,
        prefix=f"/{EndpointRouteType.APP_ROOT}",
    )

    # Mount the web UI
    fastapi_app.mount(
        path="/",
        app=StaticFiles(directory=WEB_UI_DIRECTORY, html=True),
        name="static",
    )


# Serve the Vue.js index.html as the root
@app.get("/", include_in_schema=False)
async def vuejs_index() -> FileResponse:
    """The vueJS web ui root."""

    return FileResponse("static/index.html")


if __name__ == "__main__":

    #dotenv_path = Path(__file__).resolve().parent.parent / "envs" / ".env"
    #load_dotenv(dotenv_path=dotenv_path)
    #print(f"Loaded {dotenv_path}")

    print("Start uvicorn server ...", flush=True)
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8001,
        loop="uvloop",
        workers=1,
        reload=app_env_variables.environment is Environment.DEV,
        access_log=app_env_variables.environment is not Environment.PROD,
        # disable access log for prod
    )
    print("Stop uvicorn server.", flush=True)
