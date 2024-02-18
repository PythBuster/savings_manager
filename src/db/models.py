"""The MoneyBox ORM model."""

from typing import Any

from dictalchemy import make_class_dictable
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import AbstractConcreteBase
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

meta = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)


# declarative base class
class Base(DeclarativeBase):  # pylint: disable=too-few-public-methods
    """The declarative Base model"""

    metadata = meta


make_class_dictable(Base)


class SqlBase(AbstractConcreteBase, Base):  # pylint: disable=too-few-public-methods
    """An ORM declarative Base model with an ID as primary key"""

    strict_attrs = True
    id: Mapped[int] = mapped_column(primary_key=True, comment="The primary ID of the row.")
    is_active: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
        comment="Flag to mark instance as deleted.",
    )

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

        if "is_active" not in exclude:
            exclude.append("is_active")

        return super().asdict(  # pylint: disable=no-member
            exclude=exclude,
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

    __tablename__ = "moneybox"

    name: Mapped[str] = mapped_column(
        comment="The name of a moneybox.",
        nullable=False,
    )

    balance: Mapped[int] = mapped_column(
        default=0,
        comment="The current balance of the moneybox.",
        nullable=False,
    )
