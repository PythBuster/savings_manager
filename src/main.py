"""The start module of the savings manager app."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from src.custom_types import EndpointRouteType
from src.db.db_manager import DBManager
from src.routes.moneybox import moneybox_router
from src.routes.moneyboxes import moneyboxes_router
from src.settings import SPHINX_DIRECTORY
from src.utils import get_app_data, get_db_settings, load_environment

tags_metadata = [
    {
        "name": "moneybox",
        "description": "All moneybox endpoints.",
    },
    {
        "name": "moneyboxes",
        "description": "All moneyboxes endpoints.",
    },
]

app_data = get_app_data()
author_name, author_mail = app_data["authors"][0].split()


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI) -> AsyncGenerator:
    """The fast api lifespan."""

    print(f"Initialize fastAPI app (id={id(fastapi_app)}) ...", flush=True)
    initialize_app(fastapi_app=fastapi_app)

    print(f"Register routers (id={id(fastapi_app)}) ...", flush=True)
    register_router(fastapi_app=fastapi_app)

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


def initialize_app(fastapi_app: FastAPI) -> None:
    """Initialise the FastAPI app.

    :param fastapi_app: The fast api app.
    :rtype fastapi_app: FastAPI
    """

    load_environment()

    fastapi_app.state.db_manager = DBManager(db_settings=get_db_settings())


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


def main() -> None:
    """Entry point of the app."""

    print("Start uvicorn server.", flush=True)
    uvicorn.run(
        "src.main:app",
        host="localhost",
        port=8000,
        loop="asyncio",
        workers=1,
        # reload=environment_type is EnvironmentType.DEV,
    )
    print("Stop uvicorn server.", flush=True)


if __name__ == "__main__":
    main()
