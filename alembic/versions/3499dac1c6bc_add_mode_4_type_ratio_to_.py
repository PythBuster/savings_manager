"""Redefine overflowmoneyboxautomatedsavingsmodetype enum with RATIO"""

from alembic import op
from typing import Sequence, Union

# Revision identifiers
revision: str = '3499dac1c6bc'
down_revision: Union[str, None] = 'a5a2d923bb37'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Type names
old_type = 'overflowmoneyboxautomatedsavingsmodetype'
new_type = 'overflowmoneyboxautomatedsavingsmodetype_new'

# Table & column – adjust if needed!
table_name = 'app_settings'
column_name = 'overflow_moneybox_automated_savings_mode'

# Enums
values_with_ratio = (
    'COLLECT',
    'ADD_TO_AUTOMATED_SAVINGS_AMOUNT',
    'FILL_UP_LIMITED_MONEYBOXES',
    'RATIO',
)

values_without_ratio = (
    'COLLECT',
    'ADD_TO_AUTOMATED_SAVINGS_AMOUNT',
    'FILL_UP_LIMITED_MONEYBOXES',
)


def upgrade():
    # 1. Create new enum type including RATIO
    op.execute(f"CREATE TYPE {new_type} AS ENUM {values_with_ratio}")

    # 2. Remove default value from column
    op.execute(
        f"ALTER TABLE {table_name} "
        f"ALTER COLUMN {column_name} DROP DEFAULT"
    )

    # 3. Cast column to new enum type
    op.execute(
        f"ALTER TABLE {table_name} "
        f"ALTER COLUMN {column_name} "
        f"TYPE {new_type} USING {column_name}::text::{new_type}"
    )

    # 4. Drop the old enum type
    op.execute(f"DROP TYPE {old_type}")

    # 5. Rename new enum type to original type name
    op.execute(f"ALTER TYPE {new_type} RENAME TO {old_type}")

    # 6. Restore default value
    op.execute(
        f"ALTER TABLE {table_name} "
        f"ALTER COLUMN {column_name} SET DEFAULT 'COLLECT'"
    )


def downgrade():
    tmp_type = f"{old_type}_tmp"

    # 1. Change all RATIO values to COLLECT so the cast works
    op.execute(
        f"UPDATE {table_name} "
        f"SET {column_name} = 'COLLECT' "
        f"WHERE {column_name} = 'RATIO'"
    )

    # 2. Create enum type without RATIO
    op.execute(f"CREATE TYPE {tmp_type} AS ENUM {values_without_ratio}")

    # 3. Remove default value
    op.execute(
        f"ALTER TABLE {table_name} "
        f"ALTER COLUMN {column_name} DROP DEFAULT"
    )

    # 4. Cast column back to enum without RATIO
    op.execute(
        f"ALTER TABLE {table_name} "
        f"ALTER COLUMN {column_name} "
        f"TYPE {tmp_type} USING {column_name}::text::{tmp_type}"
    )

    # 5. Drop old enum type (which includes RATIO)
    op.execute(f"DROP TYPE {old_type}")

    # 6. Rename temporary type back to original name
    op.execute(f"ALTER TYPE {tmp_type} RENAME TO {old_type}")

    # 7. Restore default value
    op.execute(
        f"ALTER TABLE {table_name} "
        f"ALTER COLUMN {column_name} SET DEFAULT 'COLLECT'"
    )
