"""Further moneyboxes SwaggerUI response codes and examples are located here."""

from typing import Any

from starlette import status

from src.data_classes.responses import MoneyboxesResponse

GET_MONEYBOXES_RESPONSES: dict[status, dict[str, Any]] = {
    status.HTTP_200_OK: {
        "description": "OK",
        "model": MoneyboxesResponse,
    },
}
"""Further custom responses for endpoint GET: /moneyboxes."""
