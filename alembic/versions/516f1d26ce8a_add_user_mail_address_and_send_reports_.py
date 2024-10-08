"""add_user_email_address_and_send_reports_via_email_columns_to_app_settings

Revision ID: 516f1d26ce8a
Revises: a539d5488387
Create Date: 2024-08-19 15:47:22.979200

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "516f1d26ce8a"
down_revision: Union[str, None] = "a539d5488387"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "app_settings",
        sa.Column(
            "send_reports_via_email",
            sa.Boolean(),
            server_default="false",
            nullable=False,
            comment="Tells if receiving reports via report_sender is desired.",
        ),
    )
    op.add_column(
        "app_settings",
        sa.Column(
            "user_email_address",
            sa.String(),
            nullable=True,
            comment="Users report_sender address. Will used for receiving reports.",
        ),
    )

    op.create_check_constraint(
        "send_reports_via_email_requires_email_address",
        "app_settings",
        "(send_reports_via_email = True AND user_email_address IS NOT NULL) OR send_reports_via_email = False",
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("app_settings", "user_email_address")
    op.drop_column("app_settings", "send_reports_via_email")

    op.execute(
        """
    ALTER TABLE app_settings 
    DROP CONSTRAINT IF EXISTS send_reports_via_email_requires_email_address;
    """
    )
    # ### end Alembic commands ###
