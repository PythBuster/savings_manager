"""The start module of the savings manager app."""

from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator, Callable

import uvicorn
from IPython.utils.tz import utcnow
from dotenv import load_dotenv
from fastapi import FastAPI
from requests import Response
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.staticfiles import StaticFiles

from src import exception_handler
from src.constants import SPHINX_DIRECTORY
from src.custom_types import EndpointRouteType
from src.db.db_manager import DBManager
from src.routes.app_settings import app_settings_router
from src.routes.moneybox import moneybox_router
from src.routes.moneyboxes import moneyboxes_router
from src.routes.prioritylist import prioritylist_router
from src.routes.responses.custom_openapi_schema import custom_422_openapi_schema
from src.task_runner import BackgroundTaskRunner
from src.utils import get_app_data, get_db_settings

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
]
"""Metadata about the endpoints."""

app_data = get_app_data()
"""Reference to the app data."""

author_name, author_mail = app_data["authors"][0].split()
"""Reference to the author's name and email address.'"""


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI) -> AsyncGenerator:
    """The fast api lifespan."""

    print(f"Initialize fastAPI app (id={id(fastapi_app)}) ...", flush=True)
    initialize_app(fastapi_app=fastapi_app)

    print(f"Register routers (id={id(fastapi_app)}) ...", flush=True)
    register_router(fastapi_app=fastapi_app)

    print("Start background tasks.")
    await fastapi_app.state.background_tasks_runner.start_tasks()

    yield

    # deconstruct app here


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


# exception handler
async def catch_exceptions_middleware(
    request: Request, call_next: Callable
) -> Response | JSONResponse:
    """Custom exception handler as middleware.

    :param request: The current request.
    :param call_next: Callback to handle the request (route).
    :return: The route response or a mapped exception.
    :rtype: :class:`Response` | :class:`JSONResponse`
    """

    try:
        return await call_next(request)
    except Exception as ex:  # pylint:disable=broad-exception-caught
        return await exception_handler.response_exception(exception=ex)


# register/override middlewares
print("Register/override middlewares ...", flush=True)
app.middleware("http")(catch_exceptions_middleware)

_origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def initialize_app(fastapi_app: FastAPI) -> None:
    """Initialise the FastAPI app.

    :param fastapi_app: The fast api app.
    :rtype fastapi_app: FastAPI
    """

    db_manager = DBManager(
        db_settings=get_db_settings(),
    )
    fastapi_app.state.db_manager = db_manager
    fastapi_app.state.background_tasks_runner = BackgroundTaskRunner(db_manager=db_manager)

    set_custom_openapi_schema(fastapi_app=fastapi_app)


def set_custom_openapi_schema(fastapi_app: FastAPI) -> None:
    """Define the custom OpenAPI schema
        save original fastapi_app.openapi to call it later in mocked one.

    :param fastapi_app: The fast api app.
    :type fastapi_app: FastAPI
    """

    fastapi_app.openapi_original = fastapi_app.openapi
    fastapi_app.openapi = lambda: custom_422_openapi_schema(fastapi_app)


def register_router(fastapi_app: FastAPI) -> None:
    """Register routes to the FastAPI app.

    :param fastapi_app: The fast api app.
    :rtype fastapi_app: FastAPI
    """

    # mounts
    fastapi_app.mount(
        path="/sphinx",
        app=StaticFiles(directory=SPHINX_DIRECTORY, html=True),
        name="sphinx",
    )

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


def main() -> None:
    """Entry point of the app."""

    # load live env
    dotenv_path = Path(__file__).resolve().parent.parent / "envs" / ".env"
    load_dotenv(dotenv_path=dotenv_path)
    print(f"Loaded {dotenv_path}")

    print("Start uvicorn server ...", flush=True)
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8001,
        loop="asyncio",
        workers=1,
    )
    print("Stop uvicorn server.", flush=True)


if __name__ == "__main__":
    main()
