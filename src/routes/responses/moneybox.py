"""Further moneybox SwaggerUI response codes and examples are located here."""

from typing import Any

from starlette import status

GET_MONEYBOX_RESPONSES: dict[status, dict[str, Any]] = {
    status.HTTP_200_OK: {
        "description": "OK",
    },
}
"""Further custom responses for endpoint GET: /moneybox/{moneybox_id}."""

CREATE_MONEYBOX_RESPONSES: dict[status, dict[str, Any]] = {
    status.HTTP_200_OK: {
        "description": "OK",
    },
}
"""Further custom responses for endpoint (create) POST: /moneybox."""

UPDATE_MONEYBOX_RESPONSES: dict[status, dict[str, Any]] = {
    status.HTTP_200_OK: {
        "description": "OK",
    },
}
"""Further custom responses for endpoint (update) PATCH: /moneybox/{moneybox_id}."""

DELETE_MONEYBOX_RESPONSES: dict[status, dict[str, Any]] = {
    status.HTTP_204_NO_CONTENT: {
        "description": "No Content",
    },
}
"""Further custom responses for endpoint DELETE: /moneybox/{moneybox_id}."""

DEPOSIT_MONEYBOX_RESPONSES: dict[status, dict[str, Any]] = {
    status.HTTP_200_OK: {
        "description": "OK",
    },
}
"""Further custom responses for endpoint (deposit) POST: /moneybox/{moneybox_id}/balance/add."""

WITHDRAW_MONEYBOX_RESPONSES: dict[status, dict[str, Any]] = {
    status.HTTP_200_OK: {
        "description": "OK",
    },
}
"""Further custom responses for endpoint (withdraw) POST: /moneybox/{moneybox_id}/balance/sub."""

TRANSFER_MONEYBOX_RESPONSES: dict[status, dict[str, Any]] = {
    status.HTTP_204_NO_CONTENT: {
        "description": "No Content",
    },
}
"""Further custom responses for endpoint (transfer)
POST: /moneybox/{moneybox_id}/balance/transfer."""


MONEYBOX_TRANSACTION_LOGS_RESPONSES: dict[status, dict[str, Any]] = {
    status.HTTP_200_OK: {
        "description": "OK",
    },
    status.HTTP_204_NO_CONTENT: {
        "description": "No Content",
    },
}
"""Further custom responses for endpoint /moneybox/{moneybox_id}/transactions"""
