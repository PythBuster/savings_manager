"""add_users_table

Revision ID: a68e0b6f86bd
Revises: ec5970020dee
Create Date: 2024-09-28 16:56:41.880051

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'a68e0b6f86bd'
down_revision: Union[str, None] = 'ec5970020dee'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('user_login', sa.String(), nullable=False, comment='The user login, which is an email address in this case.'),
    sa.Column('user_password_hash', sa.String(length=60), nullable=False, comment='The hashed user password.'),
    sa.Column('id', sa.Integer(), nullable=False, comment='The primary ID of the row.'),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='The created utc datetime.'),
    sa.Column('modified_at', sa.DateTime(timezone=True), nullable=True, comment='The modified utc datetime.'),
    sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False, comment='Flag to mark instance as deleted.'),
    sa.Column('note', sa.String(), server_default='', nullable=False, comment='The note of this record'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_users')),
    sa.CheckConstraint(
        "char_length(user_password_hash) = 60",
        name=op.f("ck_user_password_hash_total_len_60"),
    ),
    sa.CheckConstraint(
        "char_length(user_login) > 0",
        name=op.f("ck_user_login_min_len_1"),
    )
    )
    # ### end Alembic commands ###

    op.create_index(
        "idx_unique_user_login_active",
        "users",
        ["user_login"],
        unique=True,
        postgresql_where=sa.text("is_active = true"),
    )

def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('users')
    # ### end Alembic commands ###
