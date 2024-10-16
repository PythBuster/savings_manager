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
"""Further responses for endpoint GET: /app/export"""


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
"""Further responses for endpoint POST: /app/import"""

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
                "example": HTTPErrorResponse(
                    message="Validation Error",
                    details={
                        "args": [
                            [
                                {
                                    "type": "missing",
                                    "loc": [
                                        "body",
                                        "userName"
                                    ],
                                    "msg": "Field required",
                                    "input": {
                                        "userNme": "JohnDoe@mail.com",
                                        "userPassword": "myPassword"
                                    }
                                },
                                {
                                    "type": "extra_forbidden",
                                    "loc": [
                                        "body",
                                        "userNme"
                                    ],
                                    "msg": "Extra inputs are not permitted",
                                    "input": "JohnDoe@mail.com"
                                }
                            ]
                        ],
                        "body": {
                            "userNme": "JohnDoe@mail.com",
                            "userPassword": "myPassword"
                        }
                    },
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
"""Further responses for endpoint POST: /app/login"""

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
"""Further responses for endpoint DELETE: /app/logout"""

