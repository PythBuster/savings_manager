"""All moneybox SwaggerUI response codes and examples are located here."""

from starlette import status

from src.data_classes.responses import HTTPErrorResponse

GET_MONEYBOX_RESPONSES = {
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
                    message="Moneybox not found.",
                    details={
                        "moneyboxId": 1,
                    },
                ),
            }
        },
    },
    status.HTTP_500_INTERNAL_SERVER_ERROR: {
        "description": "Internal Server Error",
    },
}
"""The possible responses for endpoint GET: /moneybox/{moneybox_id}."""

CREATE_MONEYBOX_RESPONSES = {
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
    status.HTTP_405_METHOD_NOT_ALLOWED: {
        "description": "Method Not Allowed",
        "content": {
            "application/json": {
                "example": HTTPErrorResponse(
                    message="Moneybox with same name already exist.",
                    details={
                        "name": "Holiday",
                    },
                ),
            }
        },
    },
    status.HTTP_409_CONFLICT: {
        "description": "Conflict",
        "content": {
            "application/json": {
                "example": HTTPErrorResponse(
                    message="moneyboxes.name",
                    details={
                        "exception": "(sqlite3.IntegrityError) UNIQUE constraint failed",
                        "params": ["Holiday", 0, 0, 50000, 0, 1, ""],
                        "detail": "",
                    },
                )
            }
        },
    },
    status.HTTP_500_INTERNAL_SERVER_ERROR: {
        "description": "Internal Server Error",
    },
}
"""The possible responses for endpoint (create) POST: /moneybox."""

UPDATE_MONEYBOX_RESPONSES = {
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
                    message="Moneybox not found.",
                    details={
                        "moneyboxId": 1,
                    },
                ),
            }
        },
    },
    status.HTTP_405_METHOD_NOT_ALLOWED: {
        "description": "Method Not Allowed",
        "content": {
            "application/json": {
                "example": HTTPErrorResponse(
                    message="Moneybox with same name already exist.",
                    details={
                        "name": "Holiday",
                    },
                ),
            }
        },
    },
    status.HTTP_409_CONFLICT: {
        "description": "Conflict",
        "content": {
            "application/json": {
                "example": HTTPErrorResponse(
                    message="moneyboxes.name",
                    details={
                        "exception": "(sqlite3.IntegrityError) UNIQUE constraint failed",
                        "params": ["Holiday", 0, 0, 50000, 0, 1, ""],
                        "detail": "",
                    },
                )
            }
        },
    },
    status.HTTP_500_INTERNAL_SERVER_ERROR: {
        "description": "Internal Server Error",
    },
}
"""The possible responses for endpoint (update) PATCH: /moneybox/{moneybox_id}."""


DELETE_MONEYBOX_RESPONSES = {
    status.HTTP_204_NO_CONTENT: {
        "description": "No Content",
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
                    message="Moneybox not found.",
                    details={
                        "moneyboxId": 1,
                    },
                ),
            }
        },
    },
    status.HTTP_405_METHOD_NOT_ALLOWED: {
        "description": "Method Not Allowed",
        "content": {
            "application/json": {
                "example": {
                    "message": (
                        "Deleting moneyboxes with balance > 0 ist not allowed.Moneybox '1' "
                        "has balance 4300."
                    ),
                    "details": {"balance": 4300, "id": 1},
                }
            }
        },
    },
    status.HTTP_500_INTERNAL_SERVER_ERROR: {
        "description": "Internal Server Error",
    },
}
"""The possible responses for endpoint DELETE: /moneybox/{moneybox_id}."""

DEPOSIT_MONEYBOX_RESPONSES = {
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
                    message="Moneybox not found.",
                    details={
                        "moneyboxId": 1,
                    },
                ),
            }
        },
    },
    status.HTTP_405_METHOD_NOT_ALLOWED: {
        "description": "Method Not Allowed",
        "content": {
            "application/json": {
                "example": HTTPErrorResponse(
                    message="Moneybox with same name already exist.",
                    details={
                        "name": "Holiday",
                    },
                ),
            }
        },
    },
    status.HTTP_500_INTERNAL_SERVER_ERROR: {
        "description": "Internal Server Error",
    },
}
"""The possible responses for endpoint (deposit) POST: /moneybox/{moneybox_id}/balance/add."""

WITHDRAW_MONEYBOX_RESPONSES = DEPOSIT_MONEYBOX_RESPONSES.copy()
"""The possible responses for endpoint (withdraw) POST: /moneybox/{moneybox_id}/balance/sub."""

TRANSFER_MONEYBOX_RESPONSES = {
    status.HTTP_204_NO_CONTENT: {
        "description": "No Content",
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
                    message="Moneybox not found.",
                    details={
                        "moneyboxId": 1,
                    },
                ),
            }
        },
    },
    status.HTTP_405_METHOD_NOT_ALLOWED: {
        "description": "Method Not Allowed",
        "content": {
            "application/json": {
                "example": HTTPErrorResponse(
                    message="Moneybox with same name already exist.",
                    details={
                        "name": "Holiday",
                    },
                ),
            }
        },
    },
    status.HTTP_500_INTERNAL_SERVER_ERROR: {
        "description": "Internal Server Error",
    },
}
"""The possible responses for endpoint (transfer) POST: /moneybox/{moneybox_id}/balance/transfer."""


MONEYBOX_TRANSACTION_LOGS_RESPONSES = {
    status.HTTP_200_OK: {
        "description": "OK",
    },
    status.HTTP_204_NO_CONTENT: {
        "description": "No Content",
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
                    message="Moneybox not found.",
                    details={
                        "moneyboxId": 1,
                    },
                ),
            }
        },
    },
    status.HTTP_500_INTERNAL_SERVER_ERROR: {
        "description": "Internal Server Error",
    },
}
"""The possible responses for endpoint /moneybox/{moneybox_id}/transactions"""
