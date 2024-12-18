"""The moneybox routes."""

from typing import Annotated, Any, cast

from fastapi import APIRouter, Body
from starlette.requests import Request

from src.custom_types import EndpointRouteType
from src.data_classes.requests import AppSettingsRequest
from src.data_classes.responses import AppSettingsResponse
from src.db.db_manager import DBManager
from src.db.models import AppSettings
from src.report_sender.email_sender.sender import EmailSender
from src.routes.exceptions import MissingSMTPSettingsError
from src.routes.responses.app_settings import (
    GET_APP_SETTINGS_RESPONSES,
    PATCH_APP_SETTINGS_RESPONSES,
)

app_settings_router: APIRouter = APIRouter(
    prefix=f"/{EndpointRouteType.APP_SETTINGS}",
    tags=[EndpointRouteType.APP_SETTINGS],
)
"""The moneybox router."""


@app_settings_router.get(
    "",
    response_model=AppSettingsResponse,
    responses=GET_APP_SETTINGS_RESPONSES,
)
async def get_app_settings_endpoint(
    request: Request,
) -> AppSettingsResponse:
    """Endpoint for getting app settings.
    \f

    :param request: The current request object.
    :type request: :class:`Request`
    :return: The app settings data.
    """

    db_manager: DBManager = cast(DBManager, request.app.state.db_manager)
    # use protected method for now
    app_settings_data: AppSettings = (
        await db_manager._get_app_settings()  # pylint: disable=protected-access
    )
    return app_settings_data.asdict()  # type: ignore


@app_settings_router.patch(
    "",
    response_model=AppSettingsResponse,
    responses=PATCH_APP_SETTINGS_RESPONSES,
)
async def patch_app_settings_endpoint(
    request: Request,
    app_settings_request: Annotated[
        AppSettingsRequest,
        Body(title="Update Data", description="The updating app settings data."),
    ],
) -> AppSettingsResponse:
    """Endpoint for updating app settings.
    \f

    :param request: The current request object.
    :type request: :class:`Request`
    :param app_settings_request: The update data of the app settings.
    :type app_settings_request: :class:`AppSettingsRequest`
    :return: The updated app settings data.
    :rtype: :class:`AppSettingsResponse`

    :raises MissingSMTPSettingsError: If the SMTP settings in the app's environment
        variables are missing.
    """

    db_manager: DBManager = cast(DBManager, request.app.state.db_manager)
    email_sender: EmailSender = cast(EmailSender, request.app.state.email_sender)

    if app_settings_request.send_reports_via_email and not email_sender.smtp_settings.smtp_ready:
        raise MissingSMTPSettingsError()

    app_settings_data: dict[str, Any] = await db_manager.update_app_settings(
        app_settings_data=app_settings_request.model_dump(exclude_unset=True),
    )
    return app_settings_data  # type: ignore
