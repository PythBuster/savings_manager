"""The general/basic root routes."""
from typing import cast

from fastapi import APIRouter
from starlette import status
from starlette.requests import Request
from starlette.responses import Response

from src.custom_types import EndpointRouteType
from src.data_classes.requests import ResetDataRequest
from src.data_classes.responses import AppInfoResponse
from src.db.db_manager import DBManager
from src.routes.responses.app import GET_APP_INFO_RESPONSES, POST_APP_RESET_RESPONSES
from src.utils import get_app_data

app_router = APIRouter(
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

    app_info_data = get_app_data()

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

    db_manager = cast(DBManager, request.app.state.db_manager)
    await db_manager.reset_database(
        keep_app_settings=reset_data.keep_app_settings,
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
