"""Further moneybox SwaggerUI response codes and examples are located here."""

from typing import Any

from starlette import status

from src.data_classes.responses import MoneyboxResponse, TransactionLogsResponse, HTTPErrorResponse

GET_MONEYBOX_RESPONSES: dict[status, dict[str, Any]] = {
    status.HTTP_200_OK: {
        "description": "OK",
        "model": MoneyboxResponse,
    },
    status.HTTP_404_NOT_FOUND: {
        "description": "Not Found",
        "content": {
            "application/json": {
                "example": HTTPErrorResponse(
                    message="Moneybox not found",
                    details={
                        "record_id": 1,
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
"""Responses for endpoint GET: /moneybox/{moneybox_id}."""

POST_MONEYBOX_RESPONSES: dict[status, dict[str, Any]] = {
    status.HTTP_200_OK: {
        "description": "OK",
        "model": MoneyboxResponse,
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
"""Responses for endpoint (create) POST: /moneybox."""


PATCH_MONEYBOX_RESPONSES: dict[status, dict[str, Any]] = {
    status.HTTP_200_OK: {
        "description": "OK",
        "model": MoneyboxResponse,
    },
    status.HTTP_404_NOT_FOUND: {
        "description": "Not Found",
        "content": {
            "application/json": {
                "example": HTTPErrorResponse(
                    message="Moneybox not found",
                    details={
                        "record_id": 1,
                    },
                )
            }
        },
    },
    status.HTTP_409_CONFLICT: {
        "description": "Conflict",
        "content": {
            "application/json": {
                "examples": {
                    "OverflowMoneyboxUpdatedError": {
                        "value": HTTPErrorResponse(
                                message="Updating overflow moneybox is not allowed/possible!",
                                details={
                                    "record_id": 1,
                                },
                            )

                    },
                    "UpdateInstanceError": {
                        "value": HTTPErrorResponse(
                                message="Failed to update moneybox.",
                                details={
                                    "record_id": 1,
                                },
                            ),

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
"""Responses for endpoint (update) PATCH: /moneybox/{moneybox_id}."""

DELETE_MONEYBOX_RESPONSES: dict[status, dict[str, Any]] = {
    status.HTTP_204_NO_CONTENT: {
        "description": "No Content",
    },
    status.HTTP_404_NOT_FOUND: {
        "description": "Not Found",
        "content": {
            "application/json": {
                "example": HTTPErrorResponse(
                    message="Record not found",
                    details={
                        "record_id": 1,
                    },
                )
            }
        },
    },
    status.HTTP_409_CONFLICT: {
        "description": "Conflict",
        "content": {
            "application/json": {
                "examples": {
                    "OverflowMoneyboxDeleteError": {
                        "value": HTTPErrorResponse(
                                message="Deleting overflow moneybox is not allowed/possible!",
                                details={
                                    "record_id": 1,
                                },
                            )
                    },
                    "DeleteInstanceError": {
                        "value": HTTPErrorResponse(
                            message="Failed updating instance",
                            details={
                                "record_id": 1,
                                "table": "moneyboxes"
                            },
                        ),
                    },
                    "HasBalanceError": {
                        "value": HTTPErrorResponse(
                            message=(
                                f"Deleting moneyboxes with balance > 0 is not allowed. "
                                f"Moneybox '1' has balance 1234."
                            ),
                            details={
                                "record_id": 1,
                                "balance": 1234,
                            },
                        ),
                    },
                    "UpdateInstanceError 1": {
                        "value": HTTPErrorResponse(
                            message=(
                                f"Deleting moneyboxes with balance > 0 is not allowed. "
                                f"Moneybox '1' has balance 1234."
                            ),
                            details={
                                "record_id": 1,
                                "balance": 1234,
                            },
                        ),
                    },
                    "UpdateInstanceError 2": {
                        "value": HTTPErrorResponse(
                            message="Update priority list has duplicate moneybox ids.",
                            details={
                                "record_id": None,
                                "moneybox_ids": [2, 3, 4],
                            },
                        ),
                    },
                },
            },
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
"""Responses for endpoint DELETE: /moneybox/{moneybox_id}."""

POST_MONEYBOX_DEPOSIT_RESPONSES: dict[status, dict[str, Any]] = {
    status.HTTP_200_OK: {
        "description": "OK",
        "model": MoneyboxResponse,
    },
    status.HTTP_404_NOT_FOUND: {
        "description": "Not Found",
        "content": {
            "application/json": {
                "example": HTTPErrorResponse(
                    message="Moneybox not found",
                    details={
                        "record_id": 1,
                    },
                )
            }
        },
    },
    status.HTTP_409_CONFLICT: {
        "description": "Conflict",
        "content": {
            "application/json": {
                "examples": {
                    "NonPositiveAmountError": {
                        "value": HTTPErrorResponse(
                            message="Can't add or sub amount <= 0.",
                            details={
                                "amount": 0,
                                "record_id": 1,
                            },
                        )
                    },
                    "UpdateInstanceError": {
                        "value": HTTPErrorResponse(
                            message="Failed updating instance.",
                            details={
                                "record_id": None,
                                "table": "moneyboxes",
                                "balance": 50,
                            },
                        ),
                    },
                },
            },
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
"""Responses for endpoint (deposit) POST: /moneybox/{moneybox_id}/deposit."""

POST_MONEYBOX_WITHDRAW_RESPONSES: dict[status, dict[str, Any]] = {
    status.HTTP_200_OK: {
        "description": "OK",
        "model": MoneyboxResponse,
    },
    status.HTTP_404_NOT_FOUND: {
        "description": "Not Found",
        "content": {
            "application/json": {
                "example": HTTPErrorResponse(
                    message="Moneybox not found",
                    details={
                        "record_id": 1,
                    },
                )
            }
        },
    },
    status.HTTP_409_CONFLICT: {
        "description": "Conflict",
        "content": {
            "application/json": {
                "examples": {
                    "NonPositiveAmountError": {
                        "value": HTTPErrorResponse(
                                message="Can't add or sub amount <= 0.",
                                details={
                                    "amount": 0,
                                    "record_id": 1,
                                },
                            )
                    },
                    "BalanceResultIsNegativeError": {
                        "value": HTTPErrorResponse(
                            message="Can't sub amount. Not enough balance to sub.",
                            details={
                                "record_id": 1,
                                "amount": 50,
                                "balance": 20,
                            },
                        ),
                    },
                    "UpdateInstanceError": {
                        "value": HTTPErrorResponse(
                            message="Failed updating instance.",
                            details={
                                "record_id": None,
                                "table": "moneyboxes",
                                "balance": 50,
                            },
                        ),
                    },
                },
            },
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
"""Responses for endpoint (withdraw) POST: /moneybox/{moneybox_id}/withdraw."""

TRANSFER_MONEYBOX_RESPONSES: dict[status, dict[str, Any]] = {
    status.HTTP_204_NO_CONTENT: {
        "description": "No Content",
    },
}
"""Further custom responses for endpoint (transfer) POST: /moneybox/{moneybox_id}/transfer."""


MONEYBOX_TRANSACTION_LOGS_RESPONSES: dict[status, dict[str, Any]] = {
    status.HTTP_200_OK: {
        "description": "OK",
        "model": TransactionLogsResponse,
    },
    status.HTTP_204_NO_CONTENT: {
        "description": "No Content",
    },
}
"""Further custom responses for endpoint /moneybox/{moneybox_id}/transactions"""
