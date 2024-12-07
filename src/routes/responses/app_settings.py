"""Further app-settings SwaggerUI response codes and examples are located here."""

from typing import Any

from starlette import status

from src.data_classes.responses import AppSettingsResponse, HTTPErrorResponse

GET_APP_SETTINGS_RESPONSES: dict[status, dict[str, Any]] = {
    status.HTTP_200_OK: {
        "description": "OK",
        "model": AppSettingsResponse,
    },
    status.HTTP_409_CONFLICT: {
        "description": "Conflict",
        "content": {
            "application/json": {
                "example": HTTPErrorResponse(
                    message=(
                        'new row for relation "app_settings" violates check constraint '
                        '"ck_app_settings_send_reports_via_email_requires_email_address"'
                    ),
                    details={
                        "exception": (
                            "(sqlalchemy.dialects.postgresql.asyncpg.IntegrityError) "
                            "<class 'asyncpg.exceptions.CheckViolationError'>"
                        ),
                        "params": [True, None, 1],
                        "detail": (
                            "Failing row contains (t, 100, 1, 2024-08-18 082142.077403+00, "
                            "2024-08-19 154906.714368+00, t, , COLLECT, t, null)."
                        ),
                    },
                )
            }
        },
    },
    status.HTTP_422_UNPROCESSABLE_ENTITY: {
        "description": "Unprocessable Entity",
        "content": {
            "application/json": {
                "examples": {
                    "Example 1: single validation error": {
                        "value": HTTPErrorResponse(
                            message="Validation Error",
                            details={
                                "errors": [
                                    {
                                        "type": "missing",
                                        "message": "Field required",
                                        "field": "savingsAmount",
                                    }
                                ]
                            },
                        )
                    },
                    "Example 2: multiple validation errors": {
                        "value": HTTPErrorResponse(
                            message="Validation Error",
                            details={
                                "errors": [
                                    {
                                        "type": "extra_forbidden",
                                        "message": "Extra inputs are not permitted",
                                        "field": "extra_field",
                                    },
                                    {
                                        "type": "missing",
                                        "message": "Field required",
                                        "field": "savingsAmount",
                                    },
                                ]
                            },
                        )
                    },
                },
            }
        },
    },
    status.HTTP_500_INTERNAL_SERVER_ERROR: {
        "description": "Internal Server Error",
        "content": {
            "application/json": {
                "example": HTTPErrorResponse(
                    message="Unknown server error.",
                    details=None,
                )
            }
        },
    },
}
"""Responses for for endpoint GET: /settings."""


PATCH_APP_SETTINGS_RESPONSES: dict[status, dict[str, Any]] = {
    status.HTTP_200_OK: {
        "description": "OK",
        "model": AppSettingsResponse,
    },
    status.HTTP_404_NOT_FOUND: {
        "description": "Not Found",
        "content": {
            "application/json": {
                "example": HTTPErrorResponse(
                    message="App settings not found.",
                    details={
                        "settings_id": 1,
                    },
                )
            }
        },
    },
    status.HTTP_409_CONFLICT: {
        "description": "Conflict",
        "content": {
            "application/json": {
                "example": HTTPErrorResponse(
                    message=(
                        'new row for relation "app_settings" violates check constraint '
                        '"ck_app_settings_send_reports_via_email_requires_email_address"'
                    ),
                    details={
                        "exception": (
                            "(sqlalchemy.dialects.postgresql.asyncpg.IntegrityError) "
                            "<class 'asyncpg.exceptions.CheckViolationError'>"
                        ),
                        "params": [True, None, 1],
                        "detail": (
                            "Failing row contains (t, 100, 1, 2024-08-18 082142.077403+00, "
                            "2024-08-19 154906.714368+00, t, , COLLECT, t, null)."
                        ),
                    },
                )
            }
        },
    },
    status.HTTP_422_UNPROCESSABLE_ENTITY: {
        "description": "Unprocessable Entity",
        "content": {
            "application/json": {
                "examples": {
                    "Example 1: single validation error": {
                        "value": HTTPErrorResponse(
                            message="Validation Error",
                            details={
                                "errors": [
                                    {
                                        "type": "missing",
                                        "message": "Field required",
                                        "field": "savingsAmount",
                                    }
                                ]
                            },
                        )
                    },
                    "Example 2: multiple validation errors": {
                        "value": HTTPErrorResponse(
                            message="Validation Error",
                            details={
                                "errors": [
                                    {
                                        "type": "extra_forbidden",
                                        "message": "Extra inputs are not permitted",
                                        "field": "extra_field",
                                    },
                                    {
                                        "type": "missing",
                                        "message": "Field required",
                                        "field": "savingsAmount",
                                    },
                                ]
                            },
                        )
                    },
                },
            }
        },
    },
    status.HTTP_500_INTERNAL_SERVER_ERROR: {
        "description": "Internal Server Error",
        "content": {
            "application/json": {
                "example": HTTPErrorResponse(
                    message="Unknown server error.",
                    details=None,
                )
            }
        },
    },
}
"""Responses for endpoint PATCH: /settings."""
