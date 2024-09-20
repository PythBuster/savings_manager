"""The FastAPI helper functions for initializing etc.,..."""

import os
from typing import Callable

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from slowapi.errors import RateLimitExceeded
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.staticfiles import StaticFiles

from src.constants import PGPASS_FILE_PATH, WEB_UI_DIR_PATH
from src.custom_types import AppEnvVariables, EndpointRouteType
from src.exception_handler import response_exception
from src.routes.app import app_router
from src.routes.app_settings import app_settings_router
from src.routes.email_sender import email_sender_router
from src.routes.moneybox import moneybox_router
from src.routes.moneyboxes import moneyboxes_router
from src.routes.prioritylist import prioritylist_router
from src.routes.responses.custom_openapi_schema import custom_400_500_openapi_schema
from src.routes.web_ui import web_ui_router


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

    port = app_env_variables.db_port
    db = app_env_variables.db_name
    user = app_env_variables.db_user
    pw = app_env_variables.db_password.get_secret_value()
    host = app_env_variables.db_host

    pass_data = f"{host}:{port}:{db}:{user}:{pw}"
    PGPASS_FILE_PATH.write_text(pass_data, encoding="utf-8")
    PGPASS_FILE_PATH.chmod(0o600)

    os.environ["PGPASSFILE"] = str(PGPASS_FILE_PATH)
