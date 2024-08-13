"""test

Revision ID: 55d336db51de
Revises: 
Create Date: 2024-08-12 06:51:51.806340

"""
import datetime
import uuid
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '55d336db51de'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('moneyboxes',
    sa.Column('name', sa.String(), nullable=False, comment='The name of the moneybox.'),
    sa.Column('balance', sa.Integer(), server_default='0', nullable=False, comment='The current balance of the moneybox.'),
    sa.Column('savings_amount', sa.Integer(), server_default='0', nullable=False, comment='The current savings amount of the moneybox.'),
    sa.Column('savings_target', sa.Integer(), nullable=True, comment='The current savings target. Is relevant for the automated distributed saving progress.'),
    sa.Column('priority', sa.Integer(), nullable=True, comment='The current priority of the moneybox. There is only one moneybox with a priority of Null (will be the marker for the overflow moneybox. And only disables moneyboxes cant have e NULL value as priority.'),
    sa.Column('id', sa.Integer(), nullable=False, comment='The primary ID of the row.'),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='The created utc datetime.'),
    sa.Column('modified_at', sa.DateTime(timezone=True), nullable=True, comment='The modified utc datetime.'),
    sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False, comment='Flag to mark instance as deleted.'),
    sa.Column('note', sa.String(), server_default='', nullable=False, comment='The note of this record'),
    sa.CheckConstraint('NOT (is_active = false AND balance != 0)', name=op.f('ck_moneyboxes_ck_moneyboxes_is_active_balance')),
    sa.CheckConstraint('balance >= 0', name=op.f('ck_moneyboxes_ck_moneyboxes_balance_nonnegative')),
    sa.CheckConstraint('char_length(trim(name)) > 0', name=op.f('ck_moneyboxes_ck_moneyboxes_name_nonempty')),
    sa.CheckConstraint('is_active = true OR priority IS NULL', name=op.f('ck_moneyboxes_ck_moneyboxes_priority_if_inactive')),
    sa.CheckConstraint('priority >= 0', name=op.f('ck_moneyboxes_ck_moneyboxes_priority_nonnegative')),
    sa.CheckConstraint('savings_amount >= 0', name=op.f('ck_moneyboxes_ck_moneyboxes_savings_amount_nonnegative')),
    sa.CheckConstraint('savings_target IS NULL OR savings_target >= 0', name=op.f('ck_moneyboxes_ck_moneyboxes_savings_target_nonnegative')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_moneyboxes'))
    )
    op.create_index('idx_unique_moneyboxes_name_active', 'moneyboxes', ['name'], unique=True, postgresql_where=sa.text('is_active = true'))
    op.create_index('idx_unique_moneyboxes_priority_active', 'moneyboxes', ['priority'], unique=True, postgresql_where=sa.text('is_active = true'))
    op.create_table('moneybox_name_histories',
    sa.Column('moneybox_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False, comment='The new name of the moneybox.'),
    sa.Column('id', sa.Integer(), nullable=False, comment='The primary ID of the row.'),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='The created utc datetime.'),
    sa.Column('modified_at', sa.DateTime(timezone=True), nullable=True, comment='The modified utc datetime.'),
    sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False, comment='Flag to mark instance as deleted.'),
    sa.Column('note', sa.String(), server_default='', nullable=False, comment='The note of this record'),
    sa.ForeignKeyConstraint(['moneybox_id'], ['moneyboxes.id'], name=op.f('fk_moneybox_name_histories_moneybox_id_moneyboxes'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_moneybox_name_histories'))
    )
    op.create_table('transactions',
    sa.Column('description', sa.String(), server_default='', nullable=False, comment='The description of the transaction action.'),
    sa.Column('transaction_type', sa.Enum('DIRECT', 'DISTRIBUTION', name='transactiontype'), nullable=False, comment='The type of the transaction. Possible values: direct or distribution.'),
    sa.Column('transaction_trigger', sa.Enum('MANUALLY', 'AUTOMATICALLY', name='transactiontrigger'), nullable=False, comment='The transaction trigger type, possible values: manually, automatically. Says, if balance was deposit or withdrawn manually or automatically.'),
    sa.Column('amount', sa.Integer(), nullable=False, comment='The current amount of the transaction. Can be negative, negative = withdraw, positive = deposit.'),
    sa.Column('balance', sa.Integer(), nullable=False, comment='The balance of the moneybox at the time of the transaction.'),
    sa.Column('counterparty_moneybox_id', sa.Integer(), nullable=True, comment='Transaction is a transfer between moneybox_id and counterparty_moneybox_id, if set.'),
    sa.Column('moneybox_id', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False, comment='The primary ID of the row.'),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='The created utc datetime.'),
    sa.Column('modified_at', sa.DateTime(timezone=True), nullable=True, comment='The modified utc datetime.'),
    sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False, comment='Flag to mark instance as deleted.'),
    sa.Column('note', sa.String(), server_default='', nullable=False, comment='The note of this record'),
    sa.CheckConstraint('balance >= 0', name=op.f('ck_transactions_ck_transactions_balance_nonnegative')),
    sa.ForeignKeyConstraint(['moneybox_id'], ['moneyboxes.id'], name=op.f('fk_transactions_moneybox_id_moneyboxes'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_transactions'))
    )
    # Insert initial moneybox data with priority = NULL
    new_moneybox = {
        "name": str(uuid.uuid4()),
        "created_at": datetime.datetime.now(tz=datetime.timezone.utc),
        "balance": 0,
        "savings_amount": 0,
        "savings_target": None,
        "is_active": True,
        "priority": 0,
    }

    connection = op.get_bind()
    connection.execute(
        sa.text("""
                    INSERT INTO moneyboxes (name, created_at, balance, savings_amount, savings_target, is_active, priority)
                    VALUES (:name, :created_at, :balance, :savings_amount, :savings_target, :is_active, :priority)
                """).params(**new_moneybox)
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('transactions')
    op.drop_table('moneybox_name_histories')
    op.drop_index('idx_unique_moneyboxes_priority_active', table_name='moneyboxes',
                  postgresql_where=sa.text('is_active = true'))
    op.drop_index('idx_unique_moneyboxes_name_active', table_name='moneyboxes',
                  postgresql_where=sa.text('is_active = true'))
    op.drop_table('moneyboxes')

    # Drop the Enum type 'transactiontype' manually
    op.execute('DROP TYPE IF EXISTS transactiontype')

    # Drop the Enum type 'transactiontrigger' manually
    op.execute('DROP TYPE IF EXISTS transactiontrigger')
    # ### end Alembic commands ###
