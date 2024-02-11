"""The start module of the savings manager app."""

import uvicorn
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from src.custom_types import EnvironmentType
from src.settings import SPHINX_DIRECTORY
from src.utils import get_app_data, load_environment

tags_metadata = [
    {
        "name": "users",
        "description": "Operations with users. The **login** logic is also here.",
    },
    {
        "name": "items",
        "description": "Manage items. So _fancy_ they have their own docs.",
        "externalDocs": {
            "description": "Items external docs",
            "url": "https://fastapi.tiangolo.com/",
        },
    },
]

app_data = get_app_data()
author_name, author_mail = app_data["authors"][0].split()

app = FastAPI(
    title=app_data["name"],
    description=app_data["description"],
    version=app_data["version"],
    contact={
        "name": author_name[1:-1],
        "email": author_mail[2:-2],
    },
    openapi_tags=tags_metadata,
)


def init_router(fastapi_app: FastAPI) -> None:
    """Initialise the FastAPI router with all existing routers

    :param fastapi_app: app to initialise
    """

    fastapi_app.mount(
        path="/sphinx",
        app=StaticFiles(directory=SPHINX_DIRECTORY, html=True),
        name="sphinx",
    )


@app.on_event("startup")
async def startup_event() -> None:
    """The fast api startup event.
    Initialization are located here."""

    init_router(fastapi_app=app)


def main() -> None:
    """Entry point of the app."""

    environment_type = load_environment()

    print("Start uvicorn server.", flush=True)
    uvicorn.run(
        "src.main:app",
        host="localhost",
        port=8000,
        loop="asyncio",
        workers=2,
        reload=environment_type is EnvironmentType.DEV,
    )
    print("Stop uvicorn server.", flush=True)


if __name__ == "__main__":
    main()
