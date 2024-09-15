"""rename_initial_overflow_moneybox

Revision ID: 6c38705366e1
Revises: 516f1d26ce8a
Create Date: 2024-08-20 17:40:26.096304

"""

import uuid
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy import text

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "6c38705366e1"
down_revision: Union[str, None] = "516f1d26ce8a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "app_settings",
        "user_email_address",
        existing_type=sa.VARCHAR(),
        comment="Users email address. Will used for receiving reports.",
        existing_comment="Users report_sender address. Will used for receiving reports.",
        existing_nullable=True,
    )

    # Rename the moneybox with priority=0 to "Overflow Moneybox"
    connection = op.get_bind()
    connection.execute(
        text(
            """
            UPDATE moneyboxes
            SET name = 'Overflow Moneybox'
            WHERE priority = 0
        """
        )
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "app_settings",
        "user_email_address",
        existing_type=sa.VARCHAR(),
        comment="Users report_sender address. Will used for receiving reports.",
        existing_comment="Users email address. Will used for receiving reports.",
        existing_nullable=True,
    )

    # Rename the moneybox with priority=0 to a new UUID4
    connection = op.get_bind()
    new_name = str(uuid.uuid4())
    connection.execute(
        text(
            """
            UPDATE moneyboxes
            SET name = :new_name
            WHERE priority = 0
        """
        ),
        {"new_name": new_name},
    )
    # ### end Alembic commands ###
