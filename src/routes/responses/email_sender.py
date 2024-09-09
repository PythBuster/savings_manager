"""All email sender SwaggerUI response codes and examples are located here."""

from starlette import status

from src.data_classes.responses import HTTPErrorResponse

SEND_TESTEMAIL_RESPONSES = {
    status.HTTP_204_NO_CONTENT: {
        "description": "No Content",
    },
    status.HTTP_400_BAD_REQUEST: {
        "description": "No database connection.",
        "content": {
            "application/json": {
                "example": HTTPErrorResponse(
                    message="No database connection.",
                    details={
                        "message": "Connect call failed ('127.0.0.1', 5432)",
                    },
                ),
            }
        },
    },
    status.HTTP_409_CONFLICT: {
        "description": "Conflict",
    },
    status.HTTP_429_TOO_MANY_REQUESTS: {
        "description": "Error: Too Many Requests",
        "content": {
            "application/json": {
                "example": {"error": "Rate limit exceeded: 1 per 1 minute"},
            }
        },
    },
    status.HTTP_500_INTERNAL_SERVER_ERROR: {
        "description": "Internal Server Error",
    },
}
"""The possible responses for endpoint GET: /settings."""
