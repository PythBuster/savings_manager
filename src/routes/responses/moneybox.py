"""All moneybox SwaggerUI response codes and examples are located here."""

from starlette import status

from src.data_classes.responses import HTTPErrorResponse

GET_MONEYBOX_RESPONSES = {
    status.HTTP_200_OK: {
        "description": "OK",
    },
    status.HTTP_404_NOT_FOUND: {
        "description": "Not Found",
        "content": {
            "application/json": {
                "example": HTTPErrorResponse(
                    message="Moneybox not found.",
                    detail={
                        "moneybox_id": 1,
                    },
                ),
            }
        },
    },
    status.HTTP_422_UNPROCESSABLE_ENTITY: {
        "description": "Unprocessable Content",
        "content": {
            "application/json": {
                "example": {
                    "detail": [
                        {
                            "type": "string_type",
                            "loc": ["body", "name"],
                            "msg": "Input should be a valid string",
                            "input": 123,
                            "url": "https://errors.pydantic.dev/2.6/v/string_type",
                        }
                    ]
                }
            }
        },
    },
}
"""The possible responses for endpoint GET: /moneybox/{moneybox_id}."""

POST_MONEYBOX_RESPONSES = {
    status.HTTP_200_OK: {
        "description": "OK",
    },
    status.HTTP_405_METHOD_NOT_ALLOWED: {
        "description": "Method Not Allowed",
        "content": {
            "application/json": {
                "example": HTTPErrorResponse(
                    message="Moneybox with same name already exist.",
                    detail={
                        "name": "Holiday",
                    },
                ),
            }
        },
    },
    status.HTTP_422_UNPROCESSABLE_ENTITY: {
        "description": "Unprocessable Content",
        "content": {
            "application/json": {
                "example": {
                    "detail": [
                        {
                            "type": "string_type",
                            "loc": ["body", "name"],
                            "msg": "Input should be a valid string",
                            "input": 123,
                            "url": "https://errors.pydantic.dev/2.6/v/string_type",
                        }
                    ]
                }
            },
        },
    },
}
"""The possible responses for endpoint POST: /moneybox."""

PATCH_MONEYBOX_RESPONSES = {
    status.HTTP_200_OK: {
        "description": "OK",
    },
    status.HTTP_404_NOT_FOUND: {
        "description": "Not Found",
        "content": {
            "application/json": {
                "example": HTTPErrorResponse(
                    message="Moneybox not found.",
                    detail={
                        "moneybox_id": 1,
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
                    detail={
                        "name": "Holiday",
                    },
                ),
            }
        },
    },
    status.HTTP_422_UNPROCESSABLE_ENTITY: {
        "description": "Unprocessable Content",
        "content": {
            "application/json": {
                "example": {
                    "detail": [
                        {
                            "type": "string_type",
                            "loc": ["body", "name"],
                            "msg": "Input should be a valid string",
                            "input": 123,
                            "url": "https://errors.pydantic.dev/2.6/v/string_type",
                        }
                    ]
                }
            },
        },
    },
}
"""The possible responses for endpoint PATCH: /moneybox/{moneybox_id}."""


DELETE_MONEYBOX_RESPONSES = {
    status.HTTP_204_NO_CONTENT: {
        "description": "No Content",
    },
    status.HTTP_404_NOT_FOUND: {
        "description": "Not Found",
        "content": {
            "application/json": {
                "example": HTTPErrorResponse(
                    message="Moneybox not found.",
                    detail={
                        "moneybox_id": 1,
                    },
                ),
            }
        },
    },
    status.HTTP_422_UNPROCESSABLE_ENTITY: {
        "description": "Unprocessable Content",
        "content": {
            "application/json": {
                "example": {
                    "detail": [
                        {
                            "type": "string_type",
                            "loc": ["body", "name"],
                            "msg": "Input should be a valid string",
                            "input": 123,
                            "url": "https://errors.pydantic.dev/2.6/v/string_type",
                        }
                    ]
                }
            },
        },
    },
}
"""The possible responses for endpoint DELETE: /moneybox/{moneybox_id}."""
