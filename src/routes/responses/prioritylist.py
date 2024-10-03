"""Further prioritylist SwaggerUI response codes and examples are located here."""

from typing import Any

from starlette import status

from src.data_classes.responses import PrioritylistResponse

GET_PRIORITYLIST_RESPONSES: dict[status, dict[str, Any]] = {
    status.HTTP_200_OK: {
        "description": "OK",
        "model": PrioritylistResponse,
    },
    status.HTTP_204_NO_CONTENT: {
        "description": "No Content",
    },
}
"""Further custom responses for endpoint GET: /prioritylist."""

UPDATE_PRIORITYLIST_RESPONSES: dict[status, dict[str, Any]] = {
    status.HTTP_200_OK: {
        "description": "OK",
        "model": PrioritylistResponse,
    },
}
"""Further custom responses for endpoint (update) PATCH: /prioritylist."""
