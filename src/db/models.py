"""The MoneyBox ORM model."""

from datetime import datetime
from typing import Any, List

from sqlalchemy import (
    JSON,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    MetaData,
    func,
    text,
)
from sqlalchemy.ext.declarative import AbstractConcreteBase
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import String

from src.custom_types import (
    ActionType,
    OverflowMoneyboxAutomatedSavingsModeType,
    TransactionTrigger,
    TransactionType,
)
from src.utils import as_dict

meta: MetaData = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)
"""The database meta config."""


# declarative base class
class Base(DeclarativeBase):  # pylint: disable=too-few-public-methods
    """The declarative Base model"""

    metadata = meta
    """The database meta config."""


class SqlBase(AbstractConcreteBase, Base):  # pylint: disable=too-few-public-methods
    """An ORM declarative Base model with an ID as primary key"""

    strict_attrs = True

    id: Mapped[int] = mapped_column(primary_key=True, comment="The primary ID of the row.")
    """The primary ID of the row."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),  # type: ignore
        default=func.now(),  # pylint: disable=not-callable
        server_default=func.now(),  # pylint: disable=not-callable
        nullable=False,
        comment="The created utc datetime.",
    )
    """The created utc datetime."""

    modified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),  # type: ignore
        default=None,
        onupdate=func.now(),  # pylint: disable=not-callable
        nullable=True,
        comment="The modified utc datetime.",
    )
    """The modified utc datetime."""

    is_active: Mapped[bool] = mapped_column(
        default=True,
        server_default=text("true"),
        nullable=False,
        comment="Flag to mark instance as deleted.",
    )
    """Flag to mark instance as deleted."""

    note: Mapped[str] = mapped_column(
        String,  # type: ignore
        default="",
        server_default="",
        nullable=False,
        comment="The note of this record",
    )
    """The note of this record."""

    def asdict(  # type: ignore  # pylint: disable=too-many-arguments
        self,
        exclude=None,
        exclude_underscore=None,
        exclude_pk=None,
        follow=None,
        include=None,
        only=None,
        **kwargs,
    ) -> dict[str, Any]:
        """Overloaded method from make_class_dictable()."""

        if exclude is None:
            exclude = []

        # always exclude these columns
        exclude.append("is_active")
        exclude.append("note")

        return as_dict(  # pylint: disable=no-member
            model=self,
            exclude=list(set(exclude)),  # remove duplicates by casting to set and back to list
            exclude_underscore=exclude_underscore,
            exclude_pk=exclude_pk,
            follow=follow,
            include=include,
            only=only,
            **kwargs,
        )  # pylint: disable=duplicate-code


class Moneybox(SqlBase):  # pylint: disable=too-few-public-methods
    """The ORM model for Moneybox"""

    __tablename__ = "moneyboxes"
    """Moneybox table name."""

    name: Mapped[str] = mapped_column(  # pylint: disable=unsubscriptable-object
        comment="The name of the moneybox.",
        nullable=False,
    )
    """The name of the moneybox."""

    balance: Mapped[int] = mapped_column(  # pylint: disable=unsubscriptable-object
        default=0,
        server_default="0",
        comment="The current balance of the moneybox.",
        nullable=False,
    )
    """The current balance of the moneybox."""

    savings_amount: Mapped[int] = mapped_column(  # pylint: disable=unsubscriptable-object
        default=0,
        server_default="0",
        nullable=False,
        comment="The current savings amount of the moneybox.",
    )
    """The current savings amount of the moneybox."""

    savings_target: Mapped[int] = mapped_column(  # pylint: disable=unsubscriptable-object
        default=None,
        server_default=None,
        nullable=True,
        comment=(
            "The current savings target. Is relevant for the automated distributed "
            "saving progress."
        ),
    )
    """"The current savings target. Is relevant for the automated distributed saving progress."""

    priority: Mapped[int] = mapped_column(  # pylint: disable=unsubscriptable-object
        nullable=True,
        comment=(
            "The current priority of the moneybox. There is only one moneybox with "
            "a priority of Null (will be the marker for the overflow moneybox. And only "
            "disables moneyboxes cant have e NULL value as priority."
        ),
    )
    """The current priority of the moneybox. There is only one moneybox with
    a priority of Null (will be the marker for the overflow moneybox)."""

    transactions_log: Mapped[List["Transaction"]] = (  # pylint: disable=unsubscriptable-object
        relationship(
            back_populates="moneybox",
            foreign_keys="[Transaction.moneybox_id]",
            cascade="all, delete-orphan",
        )
    )

    moneybox_name_history: Mapped[  # noqa: typing  # pylint: disable=(unsubscriptable-object
        List["MoneyboxNameHistory"]
    ] = relationship(
        back_populates="moneybox",
        foreign_keys="[MoneyboxNameHistory.moneybox_id]",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index(
            "idx_unique_moneyboxes_name_active",
            "name",
            unique=True,
            postgresql_where=text("is_active = true"),
        ),
        Index(
            "idx_unique_moneyboxes_priority_active",
            "priority",
            unique=True,
            postgresql_where=text("is_active = true"),
        ),
        CheckConstraint("priority >= 0", name="ck_moneyboxes_priority_nonnegative"),
        CheckConstraint("balance >= 0", name="ck_moneyboxes_balance_nonnegative"),
        CheckConstraint(
            "savings_target IS NULL OR savings_target >= 0",
            name="ck_moneyboxes_savings_target_nonnegative",
        ),
        CheckConstraint("savings_amount >= 0", name="ck_moneyboxes_savings_amount_nonnegative"),
        CheckConstraint("char_length(trim(name)) > 0", name="ck_moneyboxes_name_nonempty"),
        CheckConstraint(
            "NOT (is_active = false AND balance != 0)",
            name="ck_moneyboxes_is_active_balance",
        ),
        CheckConstraint(
            "is_active = true OR priority IS NULL",
            name="ck_moneyboxes_priority_if_inactive",
        ),
        CheckConstraint("name = trim(name)", name="name_no_leading_trailing_whitespace"),
    )


class Transaction(SqlBase):  # pylint: disable=too-few-public-methods
    """The moneybox ORM Transaction log."""

    __tablename__ = "transactions"

    description: Mapped[str] = mapped_column(  # pylint: disable=unsubscriptable-object
        default="",
        server_default="",
        nullable=False,
        comment="The description of the transaction action.",
    )
    """The description of the transaction action."""

    transaction_type: Mapped[TransactionType] = (  # pylint: disable=unsubscriptable-object
        mapped_column(
            nullable=False,
            comment="The type of the transaction. Possible values: direct or distribution.",
        )
    )
    """The type of the transaction. Possible values: direct or distribution."""

    transaction_trigger: Mapped[TransactionTrigger] = mapped_column(  # pylint: disable=E1136
        nullable=False,
        comment=(
            "The transaction trigger type, possible values: manually, automatically. "
            "Says, if balance was deposit or withdrawn manually or automatically."
        ),
    )
    """"The transaction type, possible values: manually, automatically.
    Says, if balance was deposit or withdrawn manually or automatically."""

    amount: Mapped[int] = mapped_column(  # pylint: disable=unsubscriptable-object
        nullable=False,
        comment=(
            "The current amount of the transaction. "
            "Can be negative, negative = withdraw, positive = deposit."
        ),
    )
    """The current amount of the transaction.
    Can be negative, negative = withdraw, positive = deposit."""

    balance: Mapped[int] = mapped_column(  # pylint: disable=unsubscriptable-object
        nullable=False,
        comment="The balance of the moneybox at the time of the transaction.",
    )
    """The balance of the moneybox at the time of the transaction."""

    counterparty_moneybox_id: Mapped[int] = mapped_column(  # pylint: disable=unsubscriptable-object
        nullable=True,
        comment=(
            "Transaction is a transfer between moneybox_id and " "counterparty_moneybox_id, if set."
        ),
    )
    """Transaction is a transfer between moneybox_id and
    counterparty_moneybox_id, if set."""

    moneybox_id: Mapped[int] = mapped_column(  # pylint: disable=unsubscriptable-object
        ForeignKey("moneyboxes.id", ondelete="CASCADE"),  # type: ignore
    )
    """The foreign key to moneybox."""

    moneybox: Mapped["Moneybox"] = relationship(  # pylint: disable=unsubscriptable-object
        back_populates="transactions_log",
        foreign_keys=[moneybox_id],  # type: ignore
        passive_deletes=True,
    )

    __table_args__ = (CheckConstraint("balance >= 0", name="ck_transactions_balance_nonnegative"),)


class MoneyboxNameHistory(SqlBase):  # pylint: disable=too-few-public-methods
    """The MoneyboxNameHistory ORM."""

    __tablename__ = "moneybox_name_histories"

    moneybox_id: Mapped[int] = mapped_column(  # pylint: disable=unsubscriptable-object
        ForeignKey("moneyboxes.id", ondelete="CASCADE"),  # type: ignore
    )
    """The foreign key to moneybox."""

    moneybox: Mapped["Moneybox"] = relationship(  # pylint: disable=unsubscriptable-object
        back_populates="moneybox_name_history",
        foreign_keys=[moneybox_id],  # type: ignore
        passive_deletes=True,
    )

    name: Mapped[str] = mapped_column(  # pylint: disable=unsubscriptable-object
        comment="The new name of the moneybox.",
        nullable=False,
    )
    """The new name of the moneybox."""

    __table_args__ = (
        CheckConstraint("name = trim(name)", name="name_no_leading_trailing_whitespace"),
    )


class AppSettings(SqlBase):  # pylint: disable=too-few-public-methods
    """The AppSettings ORM."""

    __tablename__ = "app_settings"

    send_reports_via_email: Mapped[bool] = mapped_column(  # pylint: disable=unsubscriptable-object
        default=False,
        server_default="false",
        nullable=False,
        comment="Tells if receiving reports via report_sender is desired.",
    )
    """Tells if receiving reports via report_sender is desired."""

    user_email_address: Mapped[str] = mapped_column(  # pylint: disable=unsubscriptable-object
        nullable=True,
        comment="Users email address. Will used for receiving reports.",
    )
    """Users report_sender address. Will used for receiving reports."""

    is_automated_saving_active: Mapped[bool] = (  # pylint: disable=unsubscriptable-object
        mapped_column(
            default=False,
            server_default="false",
            nullable=False,
            comment="Tells if automated saving is active.",
        )
    )
    """Tells if automated saving is active."""

    savings_amount: Mapped[int] = mapped_column(  # pylint: disable=unsubscriptable-object
        default=0,
        server_default="0",
        nullable=False,
        comment=(
            "The savings amount for the automated saving which will be distributed periodically "
            "to the moneyboxes, which have a (desired) savings amount > 0."
        ),
    )
    """The savings amount for the automated saving which will be distributed periodically
    to the moneyboxes, which have a (desired) savings amount > 0."""

    # noqa: ignore  # pylint: disable=line-too-long, unsubscriptable-object
    overflow_moneybox_automated_savings_mode: Mapped[OverflowMoneyboxAutomatedSavingsModeType] = (
        mapped_column(
            nullable=False,
            default=OverflowMoneyboxAutomatedSavingsModeType.COLLECT,
            server_default=str(OverflowMoneyboxAutomatedSavingsModeType.COLLECT).upper(),
            comment=(
                "The mode for the overflow moneybox, which will have an influence on the "
                "automated savings process."
            ),
        )
    )

    __table_args__ = (
        CheckConstraint(sqltext="savings_amount >= 0", name="savings_amount_nonnegative"),
        CheckConstraint(
            sqltext=(
                "(send_reports_via_email = True AND user_email_address IS NOT NULL) OR "
                "send_reports_via_email = False"
            ),
            name="check_send_reports_via_email_requires_mail_address",
        ),
    )


class AutomatedSavingsLog(SqlBase):  # pylint: disable=too-few-public-methods
    """The AutomatedSavingsLog ORM."""

    __tablename__ = "automated_savings_logs"

    action_at: Mapped[datetime] = mapped_column(  # pylint: disable=unsubscriptable-object
        DateTime(timezone=True),  # type: ignore
        nullable=False,
        comment="The utc datetime of the action.",
    )
    """The utc datetime of the action."""

    action: Mapped[ActionType] = mapped_column(  # pylint: disable=unsubscriptable-object
        nullable=False,
        comment="The action type within the automated savings and automated savings logs.",
    )
    """The action type within the automated savings and automated savings logs."""

    details: Mapped[dict] = mapped_column(  # pylint: disable=E1136
        JSON,  # type: ignore
        nullable=True,
        comment="Metadata for the action, like app settings data.",
    )
    """Metadata for the action, like app settings data."""


class User(SqlBase):  # pylint: disable=unsubscriptable-object, too-few-public-methods
    """The User ORM."""

    __tablename__ = "users"

    user_login: Mapped[str] = mapped_column(  # pylint: disable=unsubscriptable-object
        nullable=False,
        comment="The user login, which is an email address in this case.",
    )
    """The user login, which is an email address in this case."""

    user_password_hash: Mapped[str] = mapped_column(  # pylint: disable=unsubscriptable-object
        String(60),
        nullable=False,
        comment="The hashed user password.",
    )
    """The hashed user password."""

    _table_args__ = (
        Index(
            "idx_unique_user_login_active",
            "name",
            unique=True,
            postgresql_where=text("is_active = true"),
        ),
        CheckConstraint(
            "char_length(user_password_hash) == 60", name="ck_user_password_hash_total_len_60"
        ),
        CheckConstraint("char_length(user_login) > 0", name="ck_user_login_min_len_1"),
    )

    def asdict(  # type: ignore  # pylint: disable=too-many-arguments
        self,
        exclude=None,
        exclude_underscore=None,
        exclude_pk=None,
        follow=None,
        include=None,
        only=None,
        **kwargs,
    ) -> dict[str, Any]:
        """Overloaded method from make_class_dictable()."""

        if exclude is None:
            exclude = []

        # always exclude user_password_hash
        exclude.append("user_password_hash")

        return super().asdict(  # pylint: disable=no-member
            exclude=list(set(exclude)),  # remove duplicates by casting to set and back to list
            exclude_underscore=exclude_underscore,
            exclude_pk=exclude_pk,
            follow=follow,
            include=include,
            only=only,
            **kwargs,
        )  # pylint: disable=duplicate-code
