"""The FastAPI helper functions for initializing etc.,..."""

import os
from typing import Callable, Any

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
from src.routes.email_sender import email_sender_router
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


def custom_400_500_openapi_schema(fastapi_app: FastAPI) -> dict[str, Any]:
    """Override the OpenAPI schema for the given FastAPI app

    For all endpoint paths, the following (unified) responses will be created:

    - Status Code 400: For all 4XX responses (except: 401 and 403)
    - Status Code 401
    - Status Code 403
    - Status Code 500: For all 5XX responses

    **Note**: Status Codes 200 and 204 need to be defined in the routes' `responses=` argument.
    This is because not every endpoint will return a 200 status. For example, some endpoints may only return 204.

    :param fastapi_app: The fast api app.
    :type fastapi_app: :class:`FastAPI`
    :return: The new fast api openapi schema.
    :rtype: :class:`dict[str, Any]`
    """

    if fastapi_app.openapi_schema:
        return fastapi_app.openapi_schema

    # adapt sets to exclude paths in autom. response code generations
    api_root = EndpointRouteType.APP_ROOT
    app_root = EndpointRouteType.APP

    exclude_401_for_paths: set[str] = {
        f"/{api_root}/{app_root}/login",
    }
    exclude_403_for_paths: set[str] = {
        f"/{api_root}/{app_root}/login",
    }

    # call original openapi get the openapi schema
    original_openapi: dict[str, Any] = fastapi_app.openapi_original()  # type: ignore

    for path in original_openapi["paths"]:
        for method in original_openapi["paths"][path]:
            # remove default 422 status codes
            if "422" in original_openapi["paths"][path][method]["responses"]:
                del original_openapi["paths"][path][method]["responses"]["422"]

            original_openapi["paths"][path][method]["responses"]["400"] = {
                "description": "Bad Request",
                "content": {
                    "application/json": {
                        "example": {
                            "message": "Validation Error",
                            "details": {
                                "detail": [
                                    {
                                        "type": "string_type",
                                        "loc": ["body", "name"],
                                        "msg": "Input should be a valid string",
                                        "input": 123,
                                        "url": "https://errors.pydantic.dev/2.6/v/string_type",
                                        # noqa: E501  # pylint: disable=line-too-long
                                    }
                                ]
                            },
                        },
                    }
                },
            }

            if path not in exclude_401_for_paths:
                original_openapi["paths"][path][method]["responses"]["401"] = {
                    "description": "Unauthorized",
                    "content": {
                        "application/json": {
                            "example": {
                                "message": "Unauthorized",
                            },
                        }
                    },
                }

            if path not in exclude_403_for_paths:
                original_openapi["paths"][path][method]["responses"]["403"] = {
                    "description": "Forbidden",
                    "content": {
                        "application/json": {
                            "example": {
                                "message": "Forbidden",
                            },
                        }
                    },
                }

            original_openapi["paths"][path][method]["responses"]["500"] = {
                "description": "Internal Server Error",
                "content": {
                    "application/json": {
                        "example": {
                            "message": "No Database Connection",
                            "details": {
                                "ip": "127.0.0.1",
                            },
                        },
                    }
                },
            }

    # override openapi schema with new one
    fastapi_app.openapi_schema = original_openapi

    # return new openapi schema
    return fastapi_app.openapi_schema
