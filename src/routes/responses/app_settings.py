"""All prioritylist SwaggerUI response codes and examples are located here."""

from starlette import status

from src.data_classes.responses import HTTPErrorResponse


GET_APP_SETTINGS_RESPONSES = {
    status.HTTP_200_OK: {
        "description": "OK",
    },
    status.HTTP_400_BAD_REQUEST: {
        "description": "No database connection.",
        "content": {
            "application/json": {
                "example": HTTPErrorResponse(
                    message="No database connection.",
                    details={
                        "message": "Connect call failed ('127.0.0.1', 5432)",
                    },
                ),
            }
        },
    },
    status.HTTP_404_NOT_FOUND: {
        "description": "Not Found",
        "content": {
            "application/json": {
                "example": HTTPErrorResponse(
                    message="App settings not found.",
                    details={
                        "app_settings_id": 1,
                    },
                ),
            }
        },
    },
    status.HTTP_500_INTERNAL_SERVER_ERROR: {
        "description": "Internal Server Error",
    },
}
"""The possible responses for endpoint GET: /settings."""


UPDATE_APP_SETTINGS_RESPONSES = {
    status.HTTP_200_OK: {
        "description": "OK",
    },
    status.HTTP_400_BAD_REQUEST: {
        "description": "No database connection.",
        "content": {
            "application/json": {
                "example": HTTPErrorResponse(
                    message="No database connection.",
                    details={
                        "message": "Connect call failed ('127.0.0.1', 5432)",
                    },
                ),
            }
        },
    },
    status.HTTP_404_NOT_FOUND: {
        "description": "Not Found",
        "content": {
            "application/json": {
                "example": HTTPErrorResponse(
                    message="App settings not found.",
                    details={
                        "app_settings_id": 1,
                    },
                ),
            }
        },
    },
    status.HTTP_500_INTERNAL_SERVER_ERROR: {
        "description": "Internal Server Error",
    },
}
"""The possible responses for endpoint PATCH: /settings."""
