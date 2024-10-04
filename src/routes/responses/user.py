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
"""Further custom responses for endpoint POST: /user/{user_id}"""

DELETE_USER_RESPONSES: dict[status, dict[str, Any]] = {
    status.HTTP_204_NO_CONTENT: {
        "description": "No Content",
    },
}
"""Further responses for endpoint DELETE: /app/user/{user_id}"""
