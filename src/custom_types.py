"""All custom types are located here."""

from enum import StrEnum
from typing import Self

from pydantic import ConfigDict, SecretStr, model_validator
from pydantic_settings import BaseSettings


class EndpointRouteType(StrEnum):
    """The endpoint names."""

    APP: str = "app"  # /app
    """App endpoint path name"""

    APP_ROOT: str = "api"  # /api
    """Root endpoint path name."""

    MONEYBOX: str = "moneybox"  # /moneybox
    """Moneybox endpoint path name."""

    MONEYBOXES: str = "moneyboxes"  # /moneyboxes
    """Moneyboxes endpoint path name."""

    PRIORITYLIST: str = "prioritylist"  # /prioritylist
    """Prioritylist endpoint path name."""

    APP_SETTINGS: str = "settings"  # /settings
    """Settings endpoint path name."""

    EMAIL_SENDER: str = "email"  # /email
    """Email endpoint path name."""


class EnvironmentType(StrEnum):
    """App environment types/names."""

    PROD: str = "prod"
    """The Production environment."""

    DEV: str = "dev"
    """The Development environment."""

    TEST: str = "test"
    """The Testing environment."""


class AppEnvVariables(BaseSettings):
    """The app env vars, with all settings/credentials for:
    - general
    - database
    - smtp
    - JWT
    """

    # DATABASE
    db_driver: str
    """Database driver."""

    db_name: str
    """Database name."""

    db_host: str
    """Database host."""

    db_port: int
    """Database port."""

    db_user: str
    """Database user."""

    db_password: SecretStr
    """Database password."""

    # SMTP
    smtp_server: str | None = None
    """The address of the smtp server."""

    smtp_method: str | None = None
    """The smtp method, supported: STARTTLS and TLS."""

    smtp_port: int | str | None = None
    """The port name of the smtp server."""

    smtp_user_name: str | None = None
    """The user name of the smtp server."""

    smtp_password: SecretStr | None = None
    """The user password."""

    # AUTH JWT DATA
    authjwt_secret_key: SecretStr
    """The JWT secret key."""

    authjwt_cookie_secure: bool
    """Enable cookie secure."""

    authjwt_cookie_csrf_protect: bool
    """Enable CSRF protection."""

    authjwt_cookie_samesite: str
    """Same-site protection mode."""

    model_config = ConfigDict(extra="forbid")
    """Model config."""

    @property
    def smtp_ready(self) -> bool:
        """Property to check smtp readiness."""

        return not any(
            (
                self.smtp_server is None,
                self.smtp_method is None,
                self.smtp_port is None,
                self.smtp_user_name is None,
                self.smtp_password is None,
            )
        )

    @model_validator(mode="after")
    def transform_smtp_data_to_none(self) -> Self:
        """Convert emtpy string to None in smtp data."""

        if self.smtp_server is not None and self.smtp_server == "":
            self.smtp_server = None

        if self.smtp_method is not None and self.smtp_method == "":
            self.smtp_method = None

        if self.smtp_port is not None:
            if self.smtp_port == "":
                self.smtp_port = None
            else:
                self.smtp_port = int(self.smtp_port)

        if self.smtp_user_name is not None and self.smtp_user_name == "":
            self.smtp_user_name = None

        if self.smtp_password is not None and self.smtp_password == "":
            self.smtp_password = None

        return self

    @model_validator(mode="after")
    def transform_smtp_method_to_lower(self) -> Self:
        """Lowercase the smtp method."""

        if isinstance(self.smtp_method, str):
            self.smtp_method = self.smtp_method.lower()

        return self


class TransactionTrigger(StrEnum):
    """The transaction trigger."""

    MANUALLY: str = "manually"
    """Transaction was triggered manually."""

    AUTOMATICALLY: str = "automatically"
    """Transaction was triggered automatically."""


class TransactionType(StrEnum):
    """The transaction type."""

    DIRECT: str = "direct"
    """Transaction was made in this moneybox directly."""

    DISTRIBUTION: str = "distribution"
    """Transaction caused by distribution strategy."""


class ActionType(StrEnum):
    """The action type especially used in context of the automated savings and
    automated savings logs."""

    ACTIVATED_AUTOMATED_SAVING: str = "activated_automated_saving"
    """Action for activating the automated savings in app settings."""

    DEACTIVATED_AUTOMATED_SAVING: str = "deactivated_automated_saving"
    """Action for deactivating the automated savings in app settings."""

    APPLIED_AUTOMATED_SAVING: str = "applied_automated_saving"
    """Action for executing the automated savings."""

    CHANGED_AUTOMATED_SAVINGS_AMOUNT: str = "changed_automated_savings_amount"
    """Action for changing the savings amount in app settings."""


class OverflowMoneyboxAutomatedSavingsModeType(StrEnum):
    """The transaction type."""

    COLLECT: str = "collect"
    """Just collect amounts in overflow moneybox.."""

    ADD_TO_AUTOMATED_SAVINGS_AMOUNT: str = "add_to_automated_savings_amount"
    """Push up the initial automated savings amount and add all balance to
    distributing savings amount."""

    FILL_UP_LIMITED_MONEYBOXES: str = "fill_up_limited_moneyboxes"
    """After the automated savings process, the entire balance from the overflow
    moneybox should be distributed to the moneyboxes with upper limits, in the order of
    the priority list. Try to fill them up."""
