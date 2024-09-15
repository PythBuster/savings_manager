"""add_app_settings_table

Revision ID: a3cb260cb89f
Revises: 55d336db51de
Create Date: 2024-08-16 00:10:59.509704

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a3cb260cb89f"
down_revision: Union[str, None] = "55d336db51de"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "app_settings",
        sa.Column(
            "is_automated_saving_active",
            sa.Boolean(),
            server_default="true",
            nullable=False,
            comment="Tells if automated saving is active.",
        ),
        sa.Column(
            "savings_amount",
            sa.Integer(),
            server_default="0",
            nullable=False,
            comment="The savings amount for the automated saving which will be distributed periodically to the moneyboxes, which have a (desired) savings amount > 0.",
        ),
        sa.Column(
            "automated_saving_trigger_day",
            sa.Enum(
                "FIRST_OF_MONTH", "MIDDLE_OF_MONTH", "LAST_OF_MONTH", name="triggerday"
            ),
            server_default="FIRST_OF_MONTH",
            nullable=False,
            comment="The automated saving trigger day.",
        ),
        sa.Column(
            "id", sa.Integer(), nullable=False, comment="The primary ID of the row."
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
            comment="The created utc datetime.",
        ),
        sa.Column(
            "modified_at",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="The modified utc datetime.",
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
            comment="Flag to mark instance as deleted.",
        ),
        sa.Column(
            "note",
            sa.String(),
            server_default="",
            nullable=False,
            comment="The note of this record",
        ),
        sa.CheckConstraint(
            "savings_amount >= 0",
            name=op.f("ck_app_settings_savings_amount_nonnegative"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_app_settings")),
    )

    # Insert initial app settings data
    app_settings_data = {
        "is_automated_saving_active": True,
        "savings_amount": 0,
        "automated_saving_trigger_day": "FIRST_OF_MONTH",
        "is_active": True,
        "note": "",
    }

    connection = op.get_bind()
    connection.execute(
        sa.text(
            """
                    INSERT INTO app_settings (is_automated_saving_active, savings_amount, automated_saving_trigger_day, is_active, note)
                    VALUES (:is_automated_saving_active,:savings_amount,:automated_saving_trigger_day,:is_active,:note)
                """
        ).params(**app_settings_data)
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("app_settings")

    # Drop the Enum type 'triggerday' manually
    op.execute("DROP TYPE IF EXISTS triggerday")
    # ### end Alembic commands ###
