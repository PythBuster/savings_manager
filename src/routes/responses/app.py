"""Further app SwaggerUI response codes and examples are located here."""

from typing import Any

from starlette import status

from src.data_classes.responses import AppInfoResponse, LoginUserResponse

GET_APP_INFO_RESPONSES: dict[status, dict[str, Any]] = {
    status.HTTP_200_OK: {
        "description": "OK",
        "model": AppInfoResponse,
    },
}
"""Further responses for endpoint GET: /app/info"""

POST_APP_RESET_RESPONSES: dict[status, dict[str, Any]] = {
    status.HTTP_204_NO_CONTENT: {
        "description": "No Content",
    },
}
"""Further responses for endpoint POST: /app/reset"""


GET_APP_EXPORT_RESPONSES: dict[status, dict[str, Any]] = {
    status.HTTP_200_OK: {
        "description": "OK",
        "content": {
            "application/octet-stream": {}
        }
    }
}
"""Further responses for endpoint GET: /app/export"""


POST_APP_IMPORT_RESPONSES: dict[status, dict[str, Any]] = {
    status.HTTP_204_NO_CONTENT: {
        "description": "No Content",
    },
}
"""Further responses for endpoint POST: /app/import"""

POST_APP_LOGIN_RESPONSES: dict[status, dict[str, Any]] = {
    status.HTTP_200_OK: {
        "description": "OK",
        "model": LoginUserResponse,
    },
}
"""Further responses for endpoint POST: /app/login"""

DELETE_APP_LOGOUT_RESPONSES: dict[status, dict[str, Any]] = {
    status.HTTP_204_NO_CONTENT: {
        "description": "No Content",
    },
}
"""Further responses for endpoint DELETE: /app/logout"""
