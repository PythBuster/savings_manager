"""Further moneyboxes SwaggerUI response codes and examples are located here."""

from typing import Any

from starlette import status

GET_MONEYBOXES_RESPONSES: dict[status, dict[str, Any]] = {
    status.HTTP_200_OK: {
        "description": "OK",
    },
    status.HTTP_204_NO_CONTENT: {
        "description": "No Content",
    },
}
"""Further custom responses for endpoint GET: /moneyboxes."""
