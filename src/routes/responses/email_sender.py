"""Further email sender SwaggerUI response codes and examples are located here."""

from typing import Any

from starlette import status

from src.data_classes.responses import HTTPErrorResponse

PATCH_EMAIL_SEND_TESTEMAIL_RESPONSES: dict[status, dict[str, Any]] = {
    status.HTTP_204_NO_CONTENT: {
        "description": "No Content",
    },
    status.HTTP_500_INTERNAL_SERVER_ERROR: {
        "description": "Internal Server Error",
        "content": {
            "application/json": {
                "example": HTTPErrorResponse(
                    message="Unknown server error.",
                    details=None,
                )
            }
        },
    },
}
"""Responses for endpoint GET: /send-testemail."""
