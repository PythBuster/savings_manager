"""Further email sender SwaggerUI response codes and examples are located here."""

from typing import Any

from starlette import status

SEND_TESTEMAIL_RESPONSES: dict[status, dict[str, Any]] = {
    status.HTTP_204_NO_CONTENT: {
        "description": "No Content",
    },
}
"""Further custom responses for endpoint GET: /settings."""
