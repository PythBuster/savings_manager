"""Further moneyboxes SwaggerUI response codes and examples are located here."""

from typing import Any

from starlette import status

from src.data_classes.responses import (
    HTTPErrorResponse,
    MoneyboxesResponse,
    MoneyboxForecastListResponse,
)

GET_MONEYBOXES_RESPONSES: dict[status, dict[str, Any]] = {
    status.HTTP_200_OK: {
        "description": "OK",
        "model": MoneyboxesResponse,
    },
    status.HTTP_409_CONFLICT: {
        "description": "Conflict",
        "content": {
            "application/json": {
                "examples": {
                    "OverflowMoneyboxNotFoundError": {
                        "value": HTTPErrorResponse(
                            message=(
                                "No overflow moneybox found in database! "
                                "There has to be one moneybox with "
                                "priority = 0 as column value!"
                            ),
                            details=None,
                        )
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
                                        "type": "too_short",
                                        "message": (
                                            "List should have at least 1 "
                                            "item after validation, not 0"
                                        ),
                                        "field": "moneyboxes",
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
                                        "type": "too_short",
                                        "message": (
                                            "List should have at least 1 "
                                            "item after validation, not 0"
                                        ),
                                        "field": "moneyboxes",
                                    },
                                    {
                                        "type": "missing",
                                        "message": "Field required",
                                        "field": "name",
                                    },
                                ]
                            },
                        )
                    },
                    "Example 3: missing overflow moneybox": {
                        "value": HTTPErrorResponse(
                            message="Validation Error",
                            details={
                                "errors": [
                                    {
                                        "type": "value_error",
                                        "message": "Missing Overflow Moneybox.",
                                        "field": "moneyboxes",
                                    },
                                ]
                            },
                        )
                    },
                    "Example 4: multiple overflow moneyboxes": {
                        "value": HTTPErrorResponse(
                            message="Validation Error",
                            details={
                                "errors": [
                                    {
                                        "type": "value_error",
                                        "message": "Multiple Overflow Moneyboxes are not allowed.",
                                        "field": "moneyboxes",
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
"""Responses for endpoint GET: /moneyboxes"""


GET_SAVINGS_FORECAST_RESPONSES: dict[status, dict[str, Any]] = {
    status.HTTP_200_OK: {
        "description": "OK",
        "model": MoneyboxForecastListResponse,
    },
    status.HTTP_204_NO_CONTENT: {
        "description": "No Content",
    },
    status.HTTP_409_CONFLICT: {
        "description": "Conflict",
        "content": {
            "application/json": {
                "example": HTTPErrorResponse(
                    message="No app settings found.",
                    details=None,
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
                                        "type": "greater_than_equal",
                                        "message": "Input should be greater than or equal to 1",
                                        "field": "amount_of_months",
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
                                        "field": "amount_of_months",
                                    },
                                ]
                            },
                        )
                    },
                    "Example 3: missing overflow moneybox": {
                        "value": HTTPErrorResponse(
                            message="Validation Error",
                            details={
                                "errors": [
                                    {
                                        "type": "value_error",
                                        "message": "Missing Overflow Moneybox.",
                                        "field": "moneyboxes",
                                    },
                                ]
                            },
                        )
                    },
                    "Example 4: multiple overflow moneyboxes": {
                        "value": HTTPErrorResponse(
                            message="Validation Error",
                            details={
                                "errors": [
                                    {
                                        "type": "value_error",
                                        "message": "Multiple Overflow Moneyboxes are not allowed.",
                                        "field": "moneyboxes",
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
"""Responses for endpoints:
- GET: /moneyboxes/savings_forecast
"""
