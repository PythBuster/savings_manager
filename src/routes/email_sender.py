"""The email sender routes."""

from fastapi import APIRouter
from starlette import status
from starlette.requests import Request
from starlette.responses import Response

from src.custom_types import EndpointRouteType
from src.db.db_manager import DBManager
from src.report_sender.email_sender.sender import EmailSender
from src.routes.responses.email_sender import SEND_TESTEMAIL_RESPONSES

email_sender_router = APIRouter(
    prefix=f"/{EndpointRouteType.EMAIL_SENDER}",
    tags=[EndpointRouteType.EMAIL_SENDER],
)
"""The moneybox router."""


@email_sender_router.patch(
    "/send-testemail",
    responses=SEND_TESTEMAIL_RESPONSES,
    status_code=status.HTTP_204_NO_CONTENT,  # set default status code to 204
)
async def send_testemail(request: Request) -> Response:
    """Endpoint for sending a test email."""

    email_sender: EmailSender = request.app.state.email_sender
    db_manager: DBManager = request.app.state.db_manager

    app_settings = await db_manager._get_app_settings()  # pylint: disable=protected-access
    succeeded = await email_sender.send_testemail(to=app_settings.user_email_address)

    if succeeded:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return Response(status_code=status.HTTP_409_CONFLICT)
