"""rename_logs_table

Revision ID: a5a2d923bb37
Revises: d426eb2a54d7
Create Date: 2025-02-23 18:06:07.895554

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a5a2d923bb37'
down_revision: Union[str, None] = 'd426eb2a54d7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.rename_table('automated_savings_logs', 'action_logs')
    op.execute('ALTER SEQUENCE automated_savings_logs_id_seq RENAME TO action_logs_id_seq')
    op.execute('ALTER INDEX pk_automated_savings_logs RENAME TO pk_action_logs')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.rename_table('action_logs', 'automated_savings_logs')
    op.execute('ALTER SEQUENCE action_logs_id_seq RENAME TO automated_savings_logs_id_seq')
    op.execute('ALTER INDEX pk_action_logs RENAME TO pk_automated_savings_logs')
    # ### end Alembic commands ###
