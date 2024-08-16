"""The moneybox routes."""

from typing import Annotated

from fastapi import APIRouter, Body, Path
from starlette.requests import Request

from src.custom_types import EndpointRouteType
from src.data_classes.requests import AppSettingsRequest
from src.data_classes.responses import AppSettingsResponse
from src.db.db_manager import DBManager
from src.routes.responses.app_settings import (
    GET_APP_SETTINGS_RESPONSES,
    UPDATE_APP_SETTINGS_RESPONSES,
)

app_settings_router = APIRouter(
    prefix=f"/{EndpointRouteType.APP_SETTINGS}",
    tags=[EndpointRouteType.APP_SETTINGS],
)
"""The moneybox router."""


@app_settings_router.get(
    "/{app_settings_id}",
    response_model=AppSettingsResponse,
    responses=GET_APP_SETTINGS_RESPONSES,
)
async def get_app_settings(
    request: Request,
    app_settings_id: Annotated[
        int, Path(title="Settings ID", description="Settings ID to be retrieved.")
    ],
) -> AppSettingsResponse:
    """Endpoint for updating app settings by app_settings_id."""

    db_manager: DBManager = request.app.state.db_manager
    app_settings_data = await db_manager.get_app_settings(
        app_settings_id=app_settings_id,
    )
    return AppSettingsResponse(**app_settings_data)


@app_settings_router.patch(
    "/{app_settings_id}",
    response_model=AppSettingsResponse,
    responses=UPDATE_APP_SETTINGS_RESPONSES,
)
async def update_app_settings(
    request: Request,
    app_settings_id: Annotated[
        int, Path(title="Settings ID", description="Settings ID to be retrieved.")
    ],
    app_settings_request: Annotated[
        AppSettingsRequest, Body(title="Update Data", description="The updating app settings data.")
    ],
) -> AppSettingsResponse:
    """Endpoint for updating app settings by app_settings_id."""

    db_manager: DBManager = request.app.state.db_manager
    app_settings_data = await db_manager.update_app_settings(
        app_settings_id=app_settings_id,
        app_settings_data=app_settings_request.model_dump(),
    )
    return AppSettingsResponse(**app_settings_data)
