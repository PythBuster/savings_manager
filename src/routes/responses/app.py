"""Further app SwaggerUI response codes and examples are located here."""

from starlette import status

GET_APP_INFO_RESPONSES = {
    status.HTTP_200_OK: {
        "description": "OK",
    },
}
"""Further responses for endpoint GET: /app/info"""

POST_APP_RESET_RESPONSES = {
    status.HTTP_204_NO_CONTENT: {
        "description": "No Content",
    },
}
"""Further responses for endpoint POST: /app/reset"""

GET_APP_EXPORT_RESPONSES = {
    status.HTTP_200_OK: {
        "description": "OK",
    },
}
"""Further responses for endpoint GET: /app/info"""

POST_APP_EXPORT_RESPONSES = {
    status.HTTP_200_OK: {
        "description": "OK",
    },
}
"""Further responses for endpoint GET: /app/export"""
