"""Further moneybox SwaggerUI response codes and examples are located here."""

from typing import Any

from starlette import status

from src.data_classes.responses import (
    HTTPErrorResponse,
    MoneyboxResponse,
    TransactionLogsResponse,
)

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
                    message="Moneybox not found.",
                    details={
                        "id": 1,
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
                                        "type": "string_too_short",
                                        "message": "String should have at least 1 character",
                                        "field": "name",
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
                                        "field": "name",
                                    },
                                    {
                                        "type": "missing",
                                        "message": "Field required",
                                        "field": "balance",
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
"""Responses for endpoint GET: /moneybox/{moneybox_id}"""

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
                    message="Inconsistent Database! At least one (active) moneybox has priority of 'None'",
                    details={
                        "priorities": [
                            {
                                "moneybox_id": 2,
                                "name": "Holiday",
                                "priority": "type: null",
                            },
                            {
                                "moneybox_id": 4,
                                "name": "Marriage",
                                "priority": 2,
                            },
                            {
                                "moneybox_id": 3,
                                "name": "Car",
                                "priority": 3,
                            },
                        ]
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
                                        "type": "string_too_short",
                                        "message": "String should have at least 1 character",
                                        "field": "name",
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
                                        "field": "name",
                                    },
                                    {
                                        "type": "missing",
                                        "message": "Field required",
                                        "field": "balance",
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
"""Responses for endpoint (create) POST: /moneybox"""


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
                    message="Moneybox not found.",
                    details={
                        "id": 1,
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
                                "id": 1,
                            },
                        )
                    },
                    "UpdateInstanceError": {
                        "value": HTTPErrorResponse(
                            message="Failed to update moneybox.",
                            details={
                                "id": 1,
                            },
                        ),
                    },
                },
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
                                        "type": "string_too_short",
                                        "message": "String should have at least 1 character",
                                        "field": "name",
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
                                        "field": "name",
                                    },
                                    {
                                        "type": "missing",
                                        "message": "Field required",
                                        "field": "balance",
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
"""Responses for endpoint (update) PATCH: /moneybox/{moneybox_id}"""

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
                        "id": 1,
                    },
                )
            }
        },
    },
    status.HTTP_405_METHOD_NOT_ALLOWED: {
        "description": "Method Not Allowed",
        "content": {
            "application/json": {
                "example": HTTPErrorResponse(
                    message="It is not allowed to delete the Overflow Moneybox!",
                    details={
                        "id": 1,
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
                                "id": 1,
                            },
                        )
                    },
                    "DeleteInstanceError": {
                        "value": HTTPErrorResponse(
                            message="Failed updating instance",
                            details={"id": 1, "table": "moneyboxes"},
                        ),
                    },
                    "HasBalanceError": {
                        "value": HTTPErrorResponse(
                            message=(
                                f"Deleting moneyboxes with balance > 0 is not allowed. "
                                f"Moneybox '1' has balance 1234."
                            ),
                            details={
                                "id": 1,
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
                                "id": 1,
                                "balance": 1234,
                            },
                        ),
                    },
                    "UpdateInstanceError 2": {
                        "value": HTTPErrorResponse(
                            message="Update priority list has duplicate moneybox ids.",
                            details={
                                "id": None,
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
"""Responses for endpoint DELETE: /moneybox/{moneybox_id}"""

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
                    message="Moneybox not found.",
                    details={
                        "id": 1,
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
                                "id": 1,
                            },
                        )
                    },
                    "UpdateInstanceError": {
                        "value": HTTPErrorResponse(
                            message="Failed updating instance.",
                            details={
                                "id": None,
                                "table": "moneyboxes",
                                "balance": 50,
                            },
                        ),
                    },
                },
            },
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
                                        "type": "string_too_short",
                                        "message": "String should have at least 1 character",
                                        "field": "name",
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
                                        "field": "name",
                                    },
                                    {
                                        "type": "missing",
                                        "message": "Field required",
                                        "field": "balance",
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
"""Responses for endpoint (deposit) POST: /moneybox/{moneybox_id}/deposit"""

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
                    message="Moneybox not found.",
                    details={
                        "id": 1,
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
                                "id": 1,
                            },
                        )
                    },
                    "BalanceResultIsNegativeError": {
                        "value": HTTPErrorResponse(
                            message="Can't sub amount. Not enough balance to sub.",
                            details={
                                "id": 1,
                                "amount": 50,
                                "balance": 20,
                            },
                        ),
                    },
                    "UpdateInstanceError": {
                        "value": HTTPErrorResponse(
                            message="Failed updating instance.",
                            details={
                                "id": None,
                                "table": "moneyboxes",
                                "balance": 50,
                            },
                        ),
                    },
                },
            },
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
                                        "type": "string_too_short",
                                        "message": "String should have at least 1 character",
                                        "field": "name",
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
                                        "field": "name",
                                    },
                                    {
                                        "type": "missing",
                                        "message": "Field required",
                                        "field": "balance",
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
"""Responses for endpoint (withdraw) POST: /moneybox/{moneybox_id}/withdraw"""

POST_TRANSFER_MONEYBOX_RESPONSES: dict[status, dict[str, Any]] = {
    status.HTTP_204_NO_CONTENT: {
        "description": "No Content",
    },
    status.HTTP_404_NOT_FOUND: {
        "description": "Not Found",
        "content": {
            "application/json": {
                "example": HTTPErrorResponse(
                    message="Moneybox not found.",
                    details={
                        "id": 1,
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
                                "id": 1,
                            },
                        )
                    },
                    "BalanceResultIsNegativeError": {
                        "value": HTTPErrorResponse(
                            message="Can't sub amount. Not enough balance to sub.",
                            details={
                                "id": 1,
                                "amount": 50,
                                "balance": 20,
                            },
                        ),
                    },
                    "TransferEqualMoneyboxError": {
                        "value": HTTPErrorResponse(
                            message="Can't transfer within the same moneybox.",
                            details={
                                "id": 1,
                                "amount": 50,
                                "fromMoneyboxId": 2,
                                "toMoneyboxId": 2,
                            },
                        ),
                    },
                },
            },
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
                                        "type": "greater_than_equal",
                                        "message": "Input should be greater than or equal to 1",
                                        "field": "amount",
                                    },
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
                                        "type": "greater_than_equal",
                                        "message": "Input should be greater than or equal to 1",
                                        "field": "amount",
                                    },
                                    {
                                        "type": "missing",
                                        "message": "Field required",
                                        "field": "toMoneyboxId",
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
"""Responses for endpoint (transfer) POST: /moneybox/{moneybox_id}/transfer"""


GET_MONEYBOX_TRANSACTION_LOGS_RESPONSES: dict[status, dict[str, Any]] = {
    status.HTTP_200_OK: {
        "description": "OK",
        "model": TransactionLogsResponse,
    },
    status.HTTP_204_NO_CONTENT: {
        "description": "No Content",
    },
    status.HTTP_404_NOT_FOUND: {
        "description": "Not Found",
        "content": {
            "application/json": {
                "example": HTTPErrorResponse(
                    message="Moneybox not found.",
                    details={
                        "id": 1,
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
                                        "field": "transactionType",
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
                                        "type": "greater_than_equal",
                                        "message": "Input should be greater than or equal to 1",
                                        "field": "balance",
                                    },
                                    {
                                        "type": "missing",
                                        "message": "Field required",
                                        "field": "transactionType",
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
"""Responses for endpoint GET: /moneybox/{moneybox_id}/transactions"""
