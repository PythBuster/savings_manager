"""The email sender routes."""

from typing import cast

from fastapi import APIRouter
from starlette import status
from starlette.requests import Request
from starlette.responses import Response

from src.custom_types import EndpointRouteType
from src.db.db_manager import DBManager
from src.db.models import AppSettings
from src.report_sender.email_sender.sender import EmailSender
from src.routes.responses.email_sender import PATCH_EMAIL_SEND_TESTEMAIL_RESPONSES
from src.singleton import limiter

email_router: APIRouter = APIRouter(
    prefix=f"/{EndpointRouteType.EMAIL_SENDER}",
    tags=[EndpointRouteType.EMAIL_SENDER],
)
"""The moneybox router."""


@email_router.patch(
    "/send-testemail",
    responses=PATCH_EMAIL_SEND_TESTEMAIL_RESPONSES,
    status_code=status.HTTP_204_NO_CONTENT,  # set default status code to 204
)
@limiter.limit("1/minute")
async def patch_email_send_testemail_endpoint(request: Request) -> Response:
    """Endpoint for sending a test email. Limited to 1 request per minute.
    \f

    :param request: The current request object.
    :type request: :class:`Request`
    :return: The response object with the status code included.
    :rtype: :class:`Response`
    """

    email_sender: EmailSender = cast(EmailSender, request.app.state.email_sender)
    db_manager: DBManager = cast(DBManager, request.app.state.db_manager)

    app_settings: AppSettings = (
        await db_manager._get_app_settings()  # pylint: disable=protected-access
    )
    await email_sender.send_testemail(to=app_settings.user_email_address)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
