"""Further email sender SwaggerUI response codes and examples are located here."""

from starlette import status

SEND_TESTEMAIL_RESPONSES = {
    status.HTTP_204_NO_CONTENT: {
        "description": "No Content",
    },
}
"""Further custom responses for endpoint GET: /settings."""
