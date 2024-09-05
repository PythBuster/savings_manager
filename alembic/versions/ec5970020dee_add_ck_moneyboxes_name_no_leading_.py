"""add_ck_moneyboxes_name_no_leading_trailing_whitespace_to_moneyboxes_table

Revision ID: ec5970020dee
Revises: 6c38705366e1
Create Date: 2024-09-05 20:34:50.303774

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ec5970020dee'
down_revision: Union[str, None] = '6c38705366e1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_check_constraint(
        "name_no_leading_trailing_whitespace",
        "moneyboxes",
        "name = trim(name)"
    )

    op.create_check_constraint(
        "name_no_leading_trailing_whitespace",
        "moneybox_name_histories",
        "name = trim(name)"
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute("""
    ALTER TABLE moneyboxes 
    DROP CONSTRAINT IF EXISTS ck_moneyboxes_name_no_leading_trailing_whitespace;
    """)

    op.execute("""
    ALTER TABLE moneybox_name_histories 
    DROP CONSTRAINT IF EXISTS ck_moneybox_name_histories_name_no_leading_trailing_whitespace;
    """)
    # ### end Alembic commands ###
