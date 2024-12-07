"""Further app SwaggerUI response codes and examples are located here."""

import json
from typing import Any

from starlette import status

from src.data_classes.responses import AppInfoResponse, LoginUserResponse, HTTPErrorResponse

GET_APP_METADATA_RESPONSES: dict[status, dict[str, Any]] = {
    status.HTTP_200_OK: {
        "description": "OK",
        "model": AppInfoResponse,
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
                                        "field": "appName",
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
                                        "type": "string_too_short",
                                        "message": "String should have at least 1 character",
                                        "field": "appName",
                                    },
                                    {
                                        "type": "missing",
                                        "message": "Field required",
                                        "field": "appName",
                                    },
                                ]
                            },
                        )
                    },
                }
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
"""Responses for endpoint GET: /app/metadata"""

POST_APP_RESET_RESPONSES: dict[status, dict[str, Any]] = {
    status.HTTP_204_NO_CONTENT: {
        "description": "No Content",
    },
    status.HTTP_409_CONFLICT: {
        "description": "Internal Server Error",
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
                                        "field": "keepAppSettings",
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
                                        "field": "keepApp",
                                    },
                                    {
                                        "type": "missing",
                                        "message": "Field required",
                                        "field": "keepAppSettings",
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
"""Responses for endpoint POST: /app/reset"""


GET_APP_EXPORT_RESPONSES: dict[status, dict[str, Any]] = {
    status.HTTP_200_OK: {"description": "OK", "content": {"application/octet-stream": {}}},
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
"""Responses for endpoint GET: /app/export"""


POST_APP_IMPORT_RESPONSES: dict[status, dict[str, Any]] = {
    status.HTTP_204_NO_CONTENT: {
        "description": "No Content",
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
"""Responses for endpoint POST: /app/import"""

POST_APP_LOGIN_RESPONSES: dict[status, dict[str, Any]] = {
    status.HTTP_200_OK: {
        "description": "OK",
        "model": LoginUserResponse,
    },
    status.HTTP_401_UNAUTHORIZED: {
        "description": "Unauthorized",
        "content": {
            "application/json": {
                "example": HTTPErrorResponse(
                    message="Username or password incorrect.",
                    details={
                        "user_name": "pythbuster",
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
                                        "field": "userPassword",
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
                                        "field": "user",
                                    },
                                    {
                                        "type": "missing",
                                        "message": "Field required",
                                        "field": "userPassword",
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
"""Responses for endpoint POST: /app/login"""

DELETE_APP_LOGOUT_RESPONSES: dict[status, dict[str, Any]] = {
    status.HTTP_204_NO_CONTENT: {
        "description": "No Content",
    },
    status.HTTP_401_UNAUTHORIZED: {
        "description": "Unauthorized",
        "content": {
            "application/json": {
                "example": HTTPErrorResponse(
                    message="Missing cookie savings_manager",
                )
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
"""Responses for endpoint DELETE: /app/logout"""
