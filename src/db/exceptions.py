"""All database exceptions are located."""

from abc import ABC
from collections.abc import Hashable
from typing import Any


class InconsistentDatabaseError(ABC, Exception):
    """Base InconsistentDatabaseError Exception Class"""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        self.message = f"Inconsistent Database! {message}"
        self.message = f"Inconsistent Database! {message}"
        self.details = details

        super().__init__(message)


class RecordNotFoundError(ABC, Exception):
    """Base RecordNotFound Exception Class"""

    def __init__(self, record_id: int | None, message: str) -> None:
        self.record_id = record_id
        self.message = message
        self.details = {
            "id": record_id,
        }
        super().__init__(message)


class CrudDatabaseError(ABC, Exception):
    """Base CrudDatabaseError Exception Class"""

    def __init__(
        self, record_id: int | None, message: str, details: dict[Hashable, Any] | None = None
    ) -> None:
        self.record_id = record_id
        self.message = message

        if details is None:
            details = {}

        self.details = details | {
            "id": record_id,
        }
        super().__init__(message)


class UpdateInstanceError(CrudDatabaseError):
    """Base UpdateInstanceError Exception Class"""

    def __init__(
        self,
        record_id: int | None,
        message: str,
        details: dict[Hashable, Any] | None = None,
    ) -> None:
        super().__init__(record_id=record_id, message=message, details=details)


class CreateInstanceError(CrudDatabaseError):
    """Base CreateInstanceError Exception Class"""

    def __init__(
        self, record_id: int | None, message: str, details: dict[Hashable, Any] | None = None
    ) -> None:
        super().__init__(record_id=record_id, message=message, details=details)


class DeleteInstanceError(CrudDatabaseError):
    """Base DeleteInstanceError Exception Class"""

    def __init__(
        self, record_id: int | None, message: str, details: dict[Hashable, Any] | None = None
    ) -> None:
        super().__init__(record_id=record_id, message=message, details=details)


class ColumnDoesNotExistError(Exception):
    """Custom Exception ColumnDoesNotExistError"""

    def __init__(self, table: str, column: str) -> None:
        self.table = table
        self.column = column
        super().__init__(
            f"Table '{self.table}' has no column named '{self.column}'",
        )


class MoneyboxNotFoundError(RecordNotFoundError):
    """Custom MoneyboxNotFound Exception"""

    def __init__(self, moneybox_id: int) -> None:
        message = f"Moneybox with id '{moneybox_id}' does not exist."
        super().__init__(record_id=moneybox_id, message=message)


class AppSettingsNotFoundError(RecordNotFoundError):
    """Custom AppSettingsNotFoundError Exception"""

    def __init__(self, app_settings_id: int) -> None:
        message = f"App Settings with id '{app_settings_id}' does not exist."
        super().__init__(record_id=app_settings_id, message=message)


class MoneyboxNotFoundByNameError(RecordNotFoundError):
    """Custom MoneyboxNotFoundByNameError Exception"""

    def __init__(self, name: str) -> None:
        message = f"Moneybox with name '{name}' does not exist."
        super().__init__(record_id=None, message=message)


class NonPositiveAmountError(UpdateInstanceError):
    """Custom NonPositiveAmountError Exception"""

    def __init__(self, moneybox_id: int, amount: int) -> None:
        message = f"Can't add or sub amount less than 1 '{amount}' to Moneybox '{moneybox_id}'."
        self.amount = amount
        super().__init__(record_id=moneybox_id, message=message, details={"amount": amount})


class TransferEqualMoneyboxError(UpdateInstanceError):
    """Custom TransferEqualMoneyboxError Exception"""

    def __init__(self, from_moneybox_id: int, to_moneybox_id: int, amount: int) -> None:
        self.amount = amount
        super().__init__(
            record_id=None,
            message="Can't transfer within the same moneybox",
            details={
                "amount": amount,
                "from_moneybox_id": from_moneybox_id,
                "to_moneybox_id": to_moneybox_id,
            },
        )

        del self.details["id"]


class BalanceResultIsNegativeError(UpdateInstanceError):
    """Custom BalanceResultIsNegativeError Exception"""

    def __init__(self, moneybox_id: int, amount: int) -> None:
        message = (
            f"Can't sub amount '{amount}' from Moneybox '{moneybox_id}'. "
            "Not enough balance to sub."
        )
        self.amount = amount
        super().__init__(record_id=moneybox_id, message=message, details={"amount": amount})


class HasBalanceError(DeleteInstanceError):
    """Custom HasBalanceError Exception"""

    def __init__(self, moneybox_id: int, balance: int) -> None:
        message = (
            f"Deleting moneyboxes with balance > 0 is not allowed. "
            f"Moneybox '{moneybox_id}' has balance {balance}."
        )
        self.balance = balance
        super().__init__(record_id=moneybox_id, message=message, details={"balance": balance})


class OverflowMoneyboxCantBeDeletedError(DeleteInstanceError):
    """Custom OverflowMoneyboxCantBeDeletedError Exception"""

    def __init__(self, moneybox_id: int) -> None:
        message = "Deleting overflow moneybox is not allowed/possible!"
        super().__init__(record_id=moneybox_id, message=message)


class OverflowMoneyboxCantBeUpdatedError(UpdateInstanceError):
    """Custom OverflowMoneyboxCantBeUpdatedError Exception"""

    def __init__(self, moneybox_id: int) -> None:
        message = "Updating overflow moneybox is not allowed/possible!"
        super().__init__(record_id=moneybox_id, message=message)


class OverflowMoneyboxNotFoundError(InconsistentDatabaseError):
    """Custom OverflowMoneyboxNotFoundError Exception"""

    def __init__(self) -> None:
        message = (
            "No overflow moneybox found in database! There has to be one moneybox with "
            "priority = 0 as column value!"
        )
        super().__init__(
            message=message,
        )


class AutomatedSavingsError(CrudDatabaseError):
    """Custom AutomatedSavingsError Exception"""

    def __init__(
        self,
        record_id: int | None,
        message: str | None = None,
        details: dict[Hashable, Any] | None = None,
    ) -> None:
        if message is None:
            message = "Failed automated distribution."

        super().__init__(record_id=record_id, message=message, details=details)
