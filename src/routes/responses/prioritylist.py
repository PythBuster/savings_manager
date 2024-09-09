"""Further prioritylist SwaggerUI response codes and examples are located here."""

from starlette import status

GET_PRIORITYLIST_RESPONSES = {
    status.HTTP_200_OK: {
        "description": "OK",
    },
    status.HTTP_204_NO_CONTENT: {
        "description": "No Content",
    },
}
"""Further custom responses for endpoint GET: /prioritylist."""

UPDATE_PRIORITYLIST_RESPONSES = {
    status.HTTP_200_OK: {
        "description": "OK",
    },
}
"""Further custom responses for endpoint (update) PATCH: /prioritylist."""
