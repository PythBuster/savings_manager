"""Further moneyboxes SwaggerUI response codes and examples are located here."""

from typing import Any

from starlette import status

from src.data_classes.responses import (
    MoneyboxesReachingSavingsTargetsResponse,
    MoneyboxesResponse,
)

GET_MONEYBOXES_RESPONSES: dict[status, dict[str, Any]] = {
    status.HTTP_200_OK: {
        "description": "OK",
        "model": MoneyboxesResponse,
    },
    status.HTTP_204_NO_CONTENT: {
        "description": "No Content",
    },
}
"""Further custom responses for endpoint GET: /moneyboxes."""

GET_MONEYBOXES_REACHING_SAVINGS_TARGETS_RESPONSES: dict[status, dict[str, Any]] = {
    status.HTTP_200_OK: {
        "description": "OK",
        "model": MoneyboxesReachingSavingsTargetsResponse,
    },
    status.HTTP_204_NO_CONTENT: {
        "description": "No Content",
    },
}
"""Further custom responses for endpoint GET: /moneyboxes/reaching_savings_targets."""
