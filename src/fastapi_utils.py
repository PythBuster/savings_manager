"""The FastAPI helper functions for initializing etc.,..."""

import os
from typing import Callable

from fastapi import FastAPI
from pydantic.types import SecretType
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.staticfiles import StaticFiles

from src.constants import PGPASS_FILE_PATH, WEB_UI_DIR_PATH
from src.custom_types import AppEnvVariables, EndpointRouteType
from src.exception_handler import response_exception
from src.routes.app import app_router
from src.routes.app_settings import app_settings_router
from src.routes.email_sender import email_router
from src.routes.moneybox import moneybox_router
from src.routes.moneyboxes import moneyboxes_router
from src.routes.prioritylist import prioritylist_router
from src.routes.user import user_router
from src.routes.web_ui import web_ui_router


# exception handler
async def handle_requests(
    request: Request,
    call_next: Callable,
) -> Response | JSONResponse:
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
        email_router,
        prefix=f"/{EndpointRouteType.APP_ROOT}",
    )
    fastapi_app.include_router(
        app_router,
        prefix=f"/{EndpointRouteType.APP_ROOT}",
    )
    fastapi_app.include_router(
        user_router,
        prefix=f"/{EndpointRouteType.APP_ROOT}",
    )
    fastapi_app.include_router(
        web_ui_router,
        prefix="",
    )

    # Mount the web UI
    fastapi_app.mount(
        path="/",
        app=StaticFiles(directory=WEB_UI_DIR_PATH, html=True),
        name="static",
    )


def create_pgpass(app_env_variables: AppEnvVariables) -> None:
    """Create a .pgpass file in PGPASS_FILE_PATH dir and export
    file path to ENVIRONMENT `PGPASSFILE`. pg_dump and pg_restore
    will need this file for connecting the database.

    :param app_env_variables: The env settings.
    :type app_env_variables: :class:`AppEnvVariables`
    """

    port: int = app_env_variables.db_port
    db: str = app_env_variables.db_name
    user: str = app_env_variables.db_user
    pw: SecretType = app_env_variables.db_password.get_secret_value()
    host: str = app_env_variables.db_host

    pass_data: str = f"{host}:{port}:{db}:{user}:{pw}"
    PGPASS_FILE_PATH.write_text(pass_data, encoding="utf-8")
    PGPASS_FILE_PATH.chmod(0o600)

    os.environ["PGPASSFILE"] = str(PGPASS_FILE_PATH)
