"""Further prioritylist SwaggerUI response codes and examples are located here."""

from typing import Any

from starlette import status

from src.data_classes.responses import PrioritylistResponse, HTTPErrorResponse

GET_PRIORITYLIST_RESPONSES: dict[status, dict[str, Any]] = {
    status.HTTP_200_OK: {
        "description": "OK",
        "model": PrioritylistResponse,
    },
    status.HTTP_204_NO_CONTENT: {
        "description": "No Content",
    },
    status.HTTP_409_CONFLICT: {
        "description": "Conflict",
        "content": {
            "application/json": {
                "example": HTTPErrorResponse(
                    message="At least one (active) moneybox has priority of 'None'",
                    details={
                        "priorities": [
                            {
                                "moneybox_id": 1,
                                "name": "Holiday",
                                "priority": 'None',
                            },
                            {
                                "moneybox_id": 2,
                                "name": "Car",
                                "priority": '2',
                            },
                        ],
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
                                        "type": "too_short",
                                        "message": "List should have at least 1 item after validation, not 0",
                                        "field": "prioritylist",
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
                                        "type": "missing",
                                        "message": "Field required",
                                        "field": "name",
                                    },
                                    {
                                        "type": "greater_than_equal",
                                        "message": "Input should be greater than or equal to 1",
                                        "field": "priority",
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
"""Responses for endpoint GET: /prioritylist"""

UPDATE_PRIORITYLIST_RESPONSES: dict[status, dict[str, Any]] = {
    status.HTTP_200_OK: {
        "description": "OK",
        "model": PrioritylistResponse,
    },
    status.HTTP_204_NO_CONTENT: {
        "description": "No Content",
    },
    status.HTTP_409_CONFLICT: {
        "description": "Conflict",
        "content": {
            "application/json": {
                "example": HTTPErrorResponse(
                    message="At least one (active) moneybox has priority of 'None'",
                    details={
                        "priorities": [
                            {
                                "moneybox_id": 1,
                                "name": "Holiday",
                                "priority": 'None',
                            },
                            {
                                "moneybox_id": 2,
                                "name": "Car",
                                "priority": '2',
                            },
                        ],
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
                    "Request Validation Error - Example 1: single validation error": {
                        "value": HTTPErrorResponse(
                            message="Validation Error",
                            details={
                                "errors": [
                                    {
                                        "type": "too_short",
                                        "message": "List should have at least 1 item after validation, not 0",
                                        "field": "prioritylist",
                                    },
                                ]
                            },
                        )
                    },
                    "Request Validation Error - Example 2: multiple validation errors": {
                        "value": HTTPErrorResponse(
                            message="Validation Error",
                            details={
                                "errors": [
                                    {
                                        "type": "missing",
                                        "message": "Field required",
                                        "field": "moneybox_id",
                                    },
                                    {
                                        "type": "greater_than_equal",
                                        "message": "Input should be greater than or equal to 1",
                                        "field": "priority",
                                    },
                                ]
                            },
                        )
                    },
                    "Response Validation Error - Example 1: single validation error": {
                        "value": HTTPErrorResponse(
                            message="Validation Error",
                            details={
                                "errors": [
                                    {
                                        "type": "too_short",
                                        "message": "List should have at least 1 item after validation, not 0",
                                        "field": "prioritylist",
                                    },
                                ]
                            },
                        )
                    },
                    "Response Validation Error - Example 2: multiple validation errors": {
                        "value": HTTPErrorResponse(
                            message="Validation Error",
                            details={
                                "errors": [
                                    {
                                        "type": "too_short",
                                        "message": "List should have at least 1 item after validation, not 0",
                                        "field": "moneyboxes",
                                    },
                                    {
                                        "type": "missing",
                                        "message": "Field required",
                                        "field": "name",
                                    },
                                    {
                                        "type": "greater_than_equal",
                                        "message": "Input should be greater than or equal to 1",
                                        "field": "priority",
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
"""Responses for endpoint (update) PATCH: /prioritylist"""
