"""All moneyboxes SwaggerUI response codes and examples are located here."""

from starlette import status

GET_MONEYBOXES_RESPONSES = {
    status.HTTP_200_OK: {
        "description": "OK",
    },
    status.HTTP_204_NO_CONTENT: {
        "description": "No Content",
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
    status.HTTP_500_INTERNAL_SERVER_ERROR: {
        "description": "Internal Server Error",
    },
}
"""The possible responses for endpoint GET: /moneyboxes."""
