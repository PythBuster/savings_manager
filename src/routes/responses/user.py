"""Further user SwaggerUI response codes and examples are located here."""

from typing import Any

from starlette import status

from src.data_classes.responses import LoginUserResponse

GET_USER_RESPONSES: dict[status, dict[str, Any]] = {
    status.HTTP_200_OK: {
        "description": "OK",
        "model": LoginUserResponse,
    },
}
"""Further custom responses for endpoint GET: /user/{user_id}"""

ADD_USER_RESPONSES: dict[status, dict[str, Any]] = {
    status.HTTP_200_OK: {
        "description": "OK",
        "model": LoginUserResponse,
    },
}
"""Further custom responses for endpoint POST: /user/register"""

UPDATE_USER_PASSWORD_RESPONSES: dict[status, dict[str, Any]] = {
    status.HTTP_200_OK: {
        "description": "OK",
        "model": LoginUserResponse,
    },
}
"""Further custom responses for endpoint PATCH: /user/{user_id}/password"""

UPDATE_USER_NAME_RESPONSES: dict[status, dict[str, Any]] = {
    status.HTTP_200_OK: {
        "description": "OK",
        "model": LoginUserResponse,
    },
}
"""Further custom responses for endpoint PATCH: /user/{user_id}/name"""

DELETE_USER_RESPONSES: dict[status, dict[str, Any]] = {
    status.HTTP_204_NO_CONTENT: {
        "description": "No Content",
    },
}
"""Further responses for endpoint DELETE: /app/user/{user_id}"""
