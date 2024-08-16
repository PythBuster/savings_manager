"""The moneybox routes."""

from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path
from starlette import status
from starlette.requests import Request
from starlette.responses import Response

from src.custom_types import EndpointRouteType, TransactionTrigger, TransactionType
from src.data_classes.requests import (
    DepositTransactionRequest,
    MoneyboxCreateRequest,
    MoneyboxUpdateRequest,
    TransferTransactionRequest,
    WithdrawTransactionRequest, AppSettingsRequest,
)
from src.data_classes.responses import MoneyboxResponse, TransactionLogsResponse, AppSettingsResponse
from src.db.db_manager import DBManager
from src.routes.responses.app_settings import UPDATE_APP_SETTINGS_RESPONSES, GET_APP_SETTINGS_RESPONSES
from src.routes.responses.moneybox import (
    CREATE_MONEYBOX_RESPONSES,
    DELETE_MONEYBOX_RESPONSES,
    DEPOSIT_MONEYBOX_RESPONSES,
    GET_MONEYBOX_RESPONSES,
    MONEYBOX_TRANSACTION_LOGS_RESPONSES,
    TRANSFER_MONEYBOX_RESPONSES,
    UPDATE_MONEYBOX_RESPONSES,
    WITHDRAW_MONEYBOX_RESPONSES,
)
from src.utils import check_existence_of_moneybox_by_id

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
    app_settings_data: Annotated[
        AppSettingsRequest, Body(title="Update Data", description="The updating app settings data.")
    ],
) -> AppSettingsResponse:
    """Endpoint for updating app settings by app_settings_id."""

    db_manager: DBManager = request.app.state.db_manager
    app_settings_data = await db_manager.update_app_settings(
        app_settings_id=app_settings_id,
        app_settings_data=app_settings_data.model_dump(),
    )
    return AppSettingsResponse(**app_settings_data)
