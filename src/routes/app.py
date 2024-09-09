"""The general/basic root routes."""

from fastapi import APIRouter

from src.custom_types import EndpointRouteType
from src.data_classes.responses import AppInfoResponse, AppSettingsResponse
from src.routes.responses.app import GET_APP_INFO_RESPONSES
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
async def get_app_infos() -> AppSettingsResponse:
    """Endpoint for getting app infos."""

    app_info_data = get_app_data()

    return {  # type: ignore
        "appName": app_info_data["name"],
        "appVersion": app_info_data["version"],
        "appDescription": app_info_data["description"],
    }
