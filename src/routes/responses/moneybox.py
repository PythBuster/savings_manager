"""All moneybox SwaggerUI response codes and examples are located here"""

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
                    details={
                        "moneybox_id": 1,
                    },
                ),
            }
        },
    },
    status.HTTP_422_UNPROCESSABLE_ENTITY: {
        "description": "Unprocessable Content",
        "content": {"application/json": {"example": {}}},
    },
}


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
                    details={
                        "name": "Holiday",
                    },
                ),
            }
        },
    },
    status.HTTP_422_UNPROCESSABLE_ENTITY: {
        "description": "Unprocessable Content",
        "content": {"application/json": {"example": {}}},
    },
}
