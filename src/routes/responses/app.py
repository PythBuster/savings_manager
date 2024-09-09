"""Further app SwaggerUI response codes and examples are located here."""

from starlette import status

GET_APP_INFO_RESPONSES = {
    status.HTTP_200_OK: {
        "description": "OK",
    },
}
"""Further responses for endpoint GET: /app/info."""
