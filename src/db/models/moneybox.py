"""The MoneyBox ORM model."""

from dictalchemy import make_class_dictable
from sqlalchemy import MetaData
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


make_class_dictable(Base)


class SqlBase(Base):  # pylint: disable=too-few-public-methods
    """An ORM declarative Base model with an ID as primary key"""

    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, comment="The primary ID of the row")

    def asdict(
        self,
        exclude=None,
        exclude_underscore=None,
        exclude_pk=None,
        follow=None,
        include=None,
        only=None,
        **kwargs,
    ):
        if exclude is None:
            exclude = ["is_active"]
        else:
            exclude.append("is_active")

        return super().asdict(
            exclude=exclude,
            exclude_underscore=exclude_underscore,
            exclude_pk=exclude_pk,
            follow=follow,
            include=include,
            only=only,
            **kwargs,
        )


class MoneyBox(SqlBase):  # pylint: disable=too-few-public-methods
    """The ORM model for MoneyBox"""

    __tablename__ = "moneybox"

    name: Mapped[str] = mapped_column(unique=True, comment="The unique name of a moneybox.")

    balance: Mapped[int] = mapped_column(
        default=0,
        comment="The current balance of the moneybox.",
    )
