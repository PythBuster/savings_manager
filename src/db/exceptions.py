"""All database exceptions are located."""

from abc import ABC
from typing import Any


class InconsistentDatabaseError(ABC, Exception):
    """Base InconsistentDatabaseError Exception Class"""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        """Initializer for the InconsistentDatabaseError instance.

        :param message: The error message.
        :type message: :class:`str`
        :param details: Additional information about the error.
        :type details: :class:`dict[str, Any]`
        """

        self.message: str = f"Inconsistent Database! {message}"
        self.details: dict[str, Any] | None = details

        super().__init__(message)


class RecordNotFoundError(Exception):
    """Custom RecordNotFound Exception Class"""

    def __init__(
            self,
            record_id: int | None,
            message: str,
            details: dict[str, Any] | None = None,
    ) -> None:
        """Initializer for the RecordNotFoundError instance.

        :param record_id: The record id.
        :type record_id: :class:`int`
        :param message: The error message.
        :type message: :class:`str`
        """

        if details is None:
            details = {}

        self.record_id = record_id
        self.message: str = message
        details |= {
            "record_id": record_id,
        }
        self.details: dict[str, Any] = details
        super().__init__(message)


class CrudDatabaseError(ABC, Exception):
    """Base CrudDatabaseError Exception Class"""

    def __init__(
        self,
        record_id: int | None,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initializer for the CrudDatabaseError instance.

        :param record_id: The record id.
        :type record_id: :class:`int`
        :param message: The error message.
        :type message: :class:`str`
        :param details: Additional information about the error.
        :type details: :class:`dict[str, Any]`
        """

        self.record_id = record_id
        self.message: str = message

        if details is None:
            details = {}

        self.details: dict[str, Any] = details | {
            "id": record_id,
        }
        super().__init__(message)


class UpdateInstanceError(CrudDatabaseError):
    """Base UpdateInstanceError Exception Class"""

    def __init__(
        self,
        record_id: int | None,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initializer for the UpdateInstanceError instance.

        :param record_id: The record id.
        :type record_id: :class:`int`
        :param message: The error message.
        :type message: :class:`str`
        :param details: Additional information about the error.
        :type details: :class:`dict[str, Any]`
        """

        super().__init__(record_id=record_id, message=message, details=details)


class CreateInstanceError(CrudDatabaseError):
    """Base CreateInstanceError Exception Class"""

    def __init__(
        self,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initializer for the CreateInstanceError instance.

        :param message: The error message.
        :type message: :class:`str`
        :param details: Additional information about the error.
        :type details: :class:`dict[str, Any]`
        """

        super().__init__(record_id=None, message=message, details=details)


class DeleteInstanceError(CrudDatabaseError):
    """Base DeleteInstanceError Exception Class"""

    def __init__(
        self,
        record_id: int | None,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initializer for the DeleteInstanceError instance.

        :param record_id: The record id.
        :type record_id: :class:`int`
        :param message: The error message.
        :type message: :class:`str`
        :param details: Additional information about the error.
        :type details: :class:`dict[str, Any]`
        """

        super().__init__(record_id=record_id, message=message, details=details)


class MoneyboxNotFoundError(RecordNotFoundError):
    """Custom MoneyboxNotFound Exception"""

    def __init__(self, moneybox_id: int) -> None:
        """Initializer for the MoneyboxNotFound exception.

        :param moneybox_id: The moneybox id.
        :type moneybox_id: :class:`int`
        """

        message: str = f"Moneybox with id '{moneybox_id}' does not exist."
        super().__init__(record_id=moneybox_id, message=message)

class MoneyboxNameNotFoundError(RecordNotFoundError):
    """Custom MoneyboxNameNotFoundError Exception"""

    def __init__(
            self,
            moneybox_id: int,
            details: dict[str, Any] | None = None,
    ) -> None:
        """Initializer for the MoneyboxNameNotFoundError exception.

        :param moneybox_id: The moneybox id.
        :type moneybox_id: :class:`int`
        """

        message: str = f"No moneybox name is history found."
        super().__init__(
            record_id=moneybox_id,
            message=message,
            details=details,
        )

class UserNotFoundError(RecordNotFoundError):
    """Custom UserNotFoundError Exception"""

    def __init__(self, user_id: int) -> None:
        """Initializer for the UserNotFoundError exception.

        :param user_id: The moneybox id.
        :type user_id: :class:`int`
        """

        message: str = "User does not exist."
        super().__init__(record_id=user_id, message=message)


class AppSettingsNotFoundError(RecordNotFoundError):
    """Custom AppSettingsNotFoundError Exception"""

    def __init__(self, app_settings_id: int) -> None:
        """Initializer for the AppSettingsNotFound exception.

        :param app_settings_id: The app settings id.
        :type app_settings_id: :class:`int`
        """

        message: str = f"App Settings with id '{app_settings_id}' does not exist."
        super().__init__(record_id=app_settings_id, message=message)


class MoneyboxNotFoundByNameError(RecordNotFoundError):
    """Custom MoneyboxNotFoundByNameError Exception"""

    def __init__(self, name: str) -> None:
        """Initializer for the MoneyboxNotFoundByNameError exception.

        :param name: The moneybox name.
        :type name: :class:`str`
        """

        message: str = f"Moneybox with name '{name}' does not exist."
        super().__init__(record_id=None, message=message)


class NonPositiveAmountError(UpdateInstanceError):
    """Custom NonPositiveAmountError Exception"""

    def __init__(self, moneybox_id: int, amount: int) -> None:
        """Initializer for the NonPositiveAmountError exception.

        :param moneybox_id: The moneybox id.
        :type moneybox_id: :class:`int`
        :param amount: The amount.
        :type amount: :class:`int`
        """

        message: str = (
            f"Can't add or sub amount less than 1 '{amount}' to Moneybox '{moneybox_id}'."
        )
        self.amount: int = amount
        super().__init__(record_id=moneybox_id, message=message, details={"amount": amount})


class TransferEqualMoneyboxError(UpdateInstanceError):
    """Custom TransferEqualMoneyboxError Exception"""

    def __init__(self, from_moneybox_id: int, to_moneybox_id: int, amount: int) -> None:
        """Initializer for the TransferEqualMoneyboxError exception.

        :param from_moneybox_id: The moneybox id where the amount was tried to be
            transferred from.
        :type from_moneybox_id: :class:`int`
        :param to_moneybox_id: The moneybox id where the amount was tried to be
            transferred to.
        :type to_moneybox_id: :class:`int`
        :param amount: The transfer amount.
        :type amount: :class:`int`
        """

        self.amount: int = amount
        super().__init__(
            record_id=None,
            message="Can't transfer within the same moneybox",
            details={
                "amount": amount,
                "fromMoneyboxId": from_moneybox_id,
                "toMoneyboxId": to_moneybox_id,
            },
        )

        del self.details["id"]


class BalanceResultIsNegativeError(UpdateInstanceError):
    """Custom BalanceResultIsNegativeError Exception"""

    def __init__(self, moneybox_id: int, amount: int) -> None:
        """Initializer for the BalanceResultIsNegativeError exception.

        :param moneybox_id: The moneybox id.
        :type moneybox_id: :class:`int`
        :param amount: The falsy amount.
        :type amount: :class:`int`
        """

        message: str = (
            f"Can't sub amount '{amount}' from Moneybox '{moneybox_id}'. "
            "Not enough balance to sub."
        )
        self.amount: int = amount
        super().__init__(record_id=moneybox_id, message=message, details={"amount": amount})


class HasBalanceError(DeleteInstanceError):
    """Custom HasBalanceError Exception"""

    def __init__(self, moneybox_id: int, balance: int) -> None:
        """Initializer for the HasBalanceError exception.

        :param moneybox_id: The moneybox id.
        :type moneybox_id: :class:`int`
        :param balance: The falsy balance.
        :type balance: :class:`int`
        """

        message: str = (
            f"Deleting moneyboxes with balance > 0 is not allowed. "
            f"Moneybox '{moneybox_id}' has balance {balance}."
        )
        self.balance: int = balance
        super().__init__(record_id=moneybox_id, message=message, details={"balance": balance})


class OverflowMoneyboxDeleteError(DeleteInstanceError):
    """Custom OverflowMoneyboxDeleteError Exception"""

    def __init__(self, moneybox_id: int) -> None:
        """Initializer for the OverflowMoneyboxDeleteError exception.

        :param moneybox_id: The moneybox id.
        :type moneybox_id: :class:`int`
        """

        message: str = "Deleting overflow moneybox is not allowed/possible!"
        super().__init__(record_id=moneybox_id, message=message)


class OverflowMoneyboxUpdatedError(UpdateInstanceError):
    """Custom OverflowMoneyboxUpdatedError Exception"""

    def __init__(self, moneybox_id: int) -> None:
        """Initializer for the OverflowMoneyboxUpdatedError exception.

        :param moneybox_id: The moneybox id.
        :type moneybox_id: :class:`int`
        """

        message: str = "Updating overflow moneybox is not allowed/possible!"
        super().__init__(record_id=moneybox_id, message=message)


class OverflowMoneyboxNotFoundError(InconsistentDatabaseError):
    """Custom OverflowMoneyboxNotFoundError Exception"""

    def __init__(self) -> None:
        """Initializer for the OverflowMoneyboxNotFoundError exception."""

        message: str = (
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
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initializer for the AutomatedSavingsError exception.

        :param record_id: The record id.
        :type record_id: :class:`int`
        :param message: The message of the error.
        :type message: :class:`str`
        :param details: Additional details of the error.
        :type details: :class:`dict[str, Any]`
        """

        if message is None:
            message = "Failed automated distribution."

        super().__init__(record_id=record_id, message=message, details=details)


class MissingDependencyError(Exception):
    """Custom MissingDependencyError Exception"""

    def __init__(self, message: str) -> None:
        """Initializer for the MissingDependencyError exception.

        :param message: The message of the error.
        :type message: :class:`str`
        """

        self.message: str = message
        super().__init__(message)


class ProcessCommunicationError(Exception):
    """Custom ProcessCommunicationError Exception.

    Error class for errors in communication with extern processes
        like: pg_dumb, pg_restore, etc."""

    def __init__(self, message: str) -> None:
        """Initializer for the ProcessCommunicationError exception.

        :param message: The message of the error.
        :type message: :class:`str`
        """

        self.message: str = message
        super().__init__(message)


class InvalidFileError(Exception):
    """Custom InvalidFileError Exception."""

    def __init__(self, message: str) -> None:
        """Initializer for the InvalidFileError exception.

        :param message: The message of the error.
        :type message: :class:`str`
        """

        self.message: str = message
        super().__init__(message)


class UserNameAlreadyExistError(CrudDatabaseError):
    """Custom UserNameAlreadyExistError Exception."""

    def __init__(
        self,
        user_name: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.user_name: str = user_name
        message: str = "User already exists."

        if details is None:
            details = {}

        details |= {
            "user_name": user_name,
        }

        super().__init__(
            record_id=None,
            message=message,
            details=details,
        )
