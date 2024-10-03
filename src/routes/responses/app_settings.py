"""Further app-settings SwaggerUI response codes and examples are located here."""

from typing import Any

from starlette import status

from src.data_classes.responses import AppSettingsResponse

GET_APP_SETTINGS_RESPONSES: dict[status, dict[str, Any]] = {
    status.HTTP_200_OK: {
        "description": "OK",
        "model": AppSettingsResponse,
    },
}
"""Further custom responses for for endpoint GET: /settings."""


UPDATE_APP_SETTINGS_RESPONSES: dict[status, dict[str, Any]] = {
    status.HTTP_200_OK: {
        "description": "OK",
        "model": AppSettingsResponse,
    },
}
"""Further custom responses for endpoint PATCH: /settings."""
