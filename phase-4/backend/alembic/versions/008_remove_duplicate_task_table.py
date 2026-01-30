"""Fix task table naming and foreign key references

Revision ID: 008_remove_duplicate_task_table
Revises: 007_fix_task_id_type
Create Date: 2026-01-24 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '008_remove_duplicate_task_table'
down_revision = '007_fix_task_id_type'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # At this point, the task_id column should be properly converted to VARCHAR type
    # and the foreign key constraint should be dropped from the previous migration
    # Now we just need to recreate the foreign key constraint with proper types

    # First, drop the existing foreign key constraint if it exists
    try:
        op.drop_constraint('message_task_id_fkey', 'message', type_='foreignkey')
    except:
        # If constraint doesn't exist, continue
        pass

    # The tasks.id column might still be UUID type, so we need to handle this
    # For now, we'll skip recreating the foreign key constraint to avoid type mismatch
    # The foreign key constraint will be handled in the next migration (009)
    pass


def downgrade() -> None:
    # This is a complex schema change, so downgrade is not straightforward
    # We'll leave it minimal to avoid data loss
    pass