"""The MoneyBox ORM model."""

from datetime import datetime
from typing import Any, List

from dictalchemy import make_class_dictable
from sqlalchemy import ForeignKey, MetaData, text
from sqlalchemy.ext.declarative import AbstractConcreteBase
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy_utc import UtcDateTime, utcnow
from sqlalchemy.types import String
from src.custom_types import TransactionTrigger, TransactionType

meta = MetaData(
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


make_class_dictable(Base)


class SqlBase(AbstractConcreteBase, Base):  # pylint: disable=too-few-public-methods
    """An ORM declarative Base model with an ID as primary key"""

    strict_attrs = True

    id: Mapped[int] = mapped_column(primary_key=True, comment="The primary ID of the row.")
    """The primary ID of the row."""

    created_at: Mapped[datetime] = mapped_column(
        UtcDateTime,  # type: ignore
        default=utcnow(),
        nullable=False,
        comment="The created utc datetime.",
    )
    """The created utc datetime."""

    modified_at: Mapped[datetime | None] = mapped_column(
        UtcDateTime,  # type: ignore
        default=None,
        onupdate=utcnow(),
        nullable=True,
        comment="The modified utc datetime.",
    )
    """The modified utc datetime."""

    is_active: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
        comment="Flag to mark instance as deleted.",
    )
    """Flag to mark instance as deleted."""

    note: Mapped[str] = mapped_column(
        String,
        default="",
        server_default="",
        nullable=True,
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
        method="asdict",
        **kwargs,
    ) -> dict[str, Any]:
        """Overloaded method from make_class_dictable()."""

        if exclude is None:
            exclude = []

        # always exlude these columns
        exclude.append("is_active")
        exclude.append("note")

        return super().asdict(  # pylint: disable=no-member
            exclude=list(set(exclude)),  # remove duplicates by casting to set and back to list
            exclude_underscore=exclude_underscore,
            exclude_pk=exclude_pk,
            follow=follow,
            include=include,
            only=only,
            method=method,
            **kwargs,
        )


class Moneybox(SqlBase):  # pylint: disable=too-few-public-methods
    """The ORM model for Moneybox"""

    __tablename__ = "moneyboxes"
    """Moneybox table name."""

    name: Mapped[str] = mapped_column(  # pylint: disable=unsubscriptable-object
        comment="The name of a moneybox.",
        nullable=False,
    )
    """The name of a moneybox."""

    balance: Mapped[int] = mapped_column(  # pylint: disable=unsubscriptable-object
        default=0,
        comment="The current balance of the moneybox.",
        nullable=False,
    )
    """The current balance of the moneybox."""

    savings_amount: Mapped[int] = mapped_column(
        default=0,
        server_default=text("0"),
        nullable=False,
        comment="The current savings amount of the moneybox.",
    )
    """The current savings amount of the moneybox."""

    savings_target: Mapped[int] = mapped_column(
        default=None,
        server_default=None,
        nullable=True,
        comment=(
            "The current savings target. Is relevant for the automated distributed "
            "saving progress."
        ),
    )
    """"The current savings target. Is relevant for the automated 
    distributed saving progress."""

    priority: Mapped[int] = mapped_column(
        nullable=True,
        unique=True,
        comment=(
            "The current priority of the moneybox. There is only one moneybox with "
            "a priority of Null (will be the marker for the overflow moneybox."
        ),
    )
    """The current priority of the moneybox. There is only one moneybox with
    a priority of Null (will be the marker for the overflow moneybox)."""

    transactions_log: Mapped[List["Transaction"]] = (  # pylint: disable=unsubscriptable-object
        relationship(
            back_populates="moneybox",
            foreign_keys="[Transaction.moneybox_id]",
        )
    )


class Transaction(SqlBase):  # pylint: disable=too-few-public-methods
    """The moneybox ORM Transaction log."""

    __tablename__ = "transactions"

    description: Mapped[str] = mapped_column(  # pylint: disable=unsubscriptable-object
        default="",
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
        ForeignKey("moneyboxes.id"),
        nullable=True,
        comment=(
            "Transaction is a transfer between moneybox_id and " "counterparty_moneybox_id, if set."
        ),
    )
    """Transaction is a transfer between moneybox_id and
    counterparty_moneybox_id, if set."""

    counterparty_moneybox: Mapped[Moneybox] = (  # pylint: disable=unsubscriptable-object
        relationship(
            foreign_keys=[counterparty_moneybox_id],
        )
    )
    """The foreign key to moneybox as counterparty relation, which can be None."""

    moneybox_id: Mapped[int] = mapped_column(  # pylint: disable=unsubscriptable-object
        ForeignKey("moneyboxes.id"),
    )
    """The foreign key to moneybox."""

    moneybox: Mapped["Moneybox"] = relationship(  # pylint: disable=unsubscriptable-object
        back_populates="transactions_log",
        foreign_keys=[moneybox_id],
    )
