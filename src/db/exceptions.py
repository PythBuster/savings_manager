"""All database exceptions are located."""

from abc import ABC


class RecordNotFoundError(ABC, Exception):
    """Base RecordNotFound Exception Class"""

    def __init__(self, record_id: int, message: str) -> None:
        self.record_id = record_id
        self.message = message
        self.details = {
            "id": record_id,
            "message": message,
        }
        super().__init__(message)


class MoneyboxNotFoundError(RecordNotFoundError):
    """Custom MoneyboxNotFound Exception"""

    def __init__(self, moneybox_id: int) -> None:
        message = f"Moneybox with id {moneybox_id} does not exist."
        super().__init__(record_id=moneybox_id, message=message)
