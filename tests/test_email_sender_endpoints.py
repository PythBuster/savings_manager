"""All email_sender endpoint tests are located here."""

from unittest.mock import patch

from httpx import AsyncClient
from starlette import status

from src.custom_types import EndpointRouteType


async def test_send_testemail_success(
    client: AsyncClient,
) -> None:
    with patch("src.routes.email_sender.patch_email_send_testemail_endpoint") as end_testemail_mock:
        end_testemail_mock.return_value = False
        response = await client.patch(
            f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.EMAIL_SENDER}/send-testemail",
        )
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

        end_testemail_mock.return_value = True
        response = await client.patch(
            f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.EMAIL_SENDER}/send-testemail",
        )
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
