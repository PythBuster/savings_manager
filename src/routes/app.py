"""The general/basic root routes."""

import io
from datetime import datetime
from typing import Any, cast

from async_fastapi_jwt_auth import AuthJWT
from fastapi import APIRouter, Depends, File, UploadFile
from starlette import status
from starlette.requests import Request
from starlette.responses import Response, StreamingResponse

from src.auth.jwt_auth import auth_dep
from src.custom_types import EndpointRouteType
from src.data_classes.requests import LoginUserRequest, ResetDataRequest
from src.data_classes.responses import AppInfoResponse
from src.db.db_manager import DBManager
from src.db.exceptions import InvalidFileError
from src.routes.exceptions import BadUsernameOrPasswordError
from src.routes.responses.app import (
    GET_APP_EXPORT_RESPONSES,
    GET_APP_INFO_RESPONSES,
    POST_APP_IMPORT_RESPONSES,
    POST_APP_RESET_RESPONSES,
)
from src.utils import get_app_data

app_router: APIRouter = APIRouter(
    prefix=f"/{EndpointRouteType.APP}",
    tags=[EndpointRouteType.APP],
)
"""The api router."""


@app_router.get(
    "/metadata",
    response_model=AppInfoResponse,
    responses=GET_APP_INFO_RESPONSES,
)
async def get_app_infos() -> AppInfoResponse:
    """Endpoint for getting app infos like appVersion, appName etc.
    \f

    :return: The app info data.
    :rtype: :class:`AppInfoResponse`
    """

    app_info_data: dict[str, Any] = get_app_data()

    return {  # type: ignore
        "appName": app_info_data["name"],
        "appVersion": app_info_data["version"],
        "appDescription": app_info_data["description"],
    }


@app_router.post(
    "/reset",
    responses=POST_APP_RESET_RESPONSES,
    status_code=status.HTTP_200_OK,
)
async def reset_app(
    request: Request,
    reset_data: ResetDataRequest,
) -> Response:
    """Endpoint for resetting app data.
    keepAppSettings=True is POST data protects the app setting from a reset.
    \f

    :param request: The current request.
    :type request: :class:`Request`
    :param reset_data: Further information for the reset.
    :type reset_data: :class:`ResetDataRequest`
    :return: The app info data.
    :rtype: :class:`Response`
    """

    db_manager: DBManager = cast(DBManager, request.app.state.db_manager)
    await db_manager.reset_database(
        keep_app_settings=reset_data.keep_app_settings,
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app_router.get(
    "/export",
    responses=GET_APP_EXPORT_RESPONSES,
)
async def export_sql_dump(
    request: Request,
) -> StreamingResponse:
    """Endpoint for exporting SQL dump.
    \f

    :param request: The current request.
    :type request: :class:`Request`
    :return: The sql dump as streaming response.
    :rtype: :class:`StreamingResponse`
    """

    db_manager: DBManager = cast(DBManager, request.app.state.db_manager)
    sql_dump_bytes: io.BytesIO = await db_manager.export_sql_dump()

    current_dt_string: str = datetime.now().strftime("%Y-%m-%d_%H%M")
    response: StreamingResponse = StreamingResponse(
        sql_dump_bytes,
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": (
                f'attachment; filename="export_data_savings_manager_{current_dt_string}.sql"'
            )
        },
    )
    return response


@app_router.post(
    "/import",
    responses=POST_APP_IMPORT_RESPONSES,
    status_code=status.HTTP_204_NO_CONTENT,
)
async def import_sql_dump(
    request: Request,
    file: UploadFile = File(),
) -> Response:
    """Endpoint for importing SQL dump.
    \f

    :param request: The current request.
    :type request: :class:`Request`
    :param file: The uploaded SQL dump file.
    :type file: :class:`UploadFile`
    :return: A success message if the import was successful.
    :rtype: Response
    """

    if not file.filename.endswith(".sql"):
        raise InvalidFileError("SQL file required")

    sql_dump: bytes = await file.read()

    db_manager: DBManager = cast(DBManager, request.app.state.db_manager)
    await db_manager.import_sql_dump(sql_dump=sql_dump)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app_router.post("/login")
async def login(
    request: Request,
    user_request_data: LoginUserRequest,
    jwt_authorize: AuthJWT = Depends(auth_dep),
) -> Response:
    """Endpoint for logging in.
    \f

    :param request: The current request.
    :type request: :class:`Request`
    :param user_request_data: The login user data.
    :type user_request_data: :class:`LoginUserRequest`
    :param jwt_authorize: The JWT authorizer dependency.
    :type jwt_authorize: :class:`AuthJWT`
    """

    db_manager: DBManager = cast(DBManager, request.app.state.db_manager)
    user: dict[str, Any] | None = await db_manager.get_user_by_credentials(
        user_login=user_request_data.user_login,
        user_password=user_request_data.user_password.get_secret_value(),
    )

    if user is None:
        raise BadUsernameOrPasswordError(
            user_name=user_request_data.user_name,
        )

    access_token: str = await jwt_authorize.create_access_token(
        subject=str(user["id"]),
        expires_time=7 * 24 * 60 * 60,  # 7 days
    )

    # Set the JWT cookie in the response
    response: Response = Response(status_code=status.HTTP_204_NO_CONTENT)
    await jwt_authorize.set_access_cookies(
        encoded_access_token=access_token,
        response=response,
    )

    return response


@app_router.delete("/logout")
async def logout(jwt_authorize: AuthJWT = Depends(auth_dep)) -> Response:
    """Endpoint for logging in.
    \f

    :param jwt_authorize: The JWT authorizer dependency.
    :type jwt_authorize: :class:`AuthJWT`
    """

    await jwt_authorize.jwt_required()

    response: Response = Response(status_code=status.HTTP_204_NO_CONTENT)
    await jwt_authorize.unset_jwt_cookies(response=response)
    return response
