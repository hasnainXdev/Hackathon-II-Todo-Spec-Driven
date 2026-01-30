"""Fix message task_id column type

Revision ID: 005_fix_message_task_id_type
Revises: 004_fix_table_names_plural
Create Date: 2026-01-23 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '005_fix_message_task_id_type'
down_revision = '004_fix_table_names_plural'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # The issue is that the task_id column was created as VARCHAR but should be TEXT
    # to properly match our GUID type that stores as string
    # Actually, since our GUID type is configured with as_uuid=False, the column should remain as text
    # But we need to make sure it's consistent

    # First, drop the foreign key constraint
    op.drop_constraint('message_task_id_fkey', 'message', type_='foreignkey')

    # Make sure the column is properly set as text to match our GUID type expectation
    op.alter_column('message', 'task_id', type_=sa.Text())

    # Recreate the foreign key constraint
    op.create_foreign_key('message_task_id_fkey', 'message', 'tasks', ['task_id'], ['id'])


def downgrade() -> None:
    # Revert the changes: drop FK constraint, change column back to VARCHAR, recreate FK
    op.drop_constraint('message_task_id_fkey', 'message', type_='foreignkey')

    op.alter_column('message', 'task_id', type_=sa.String())

    # Recreate the foreign key constraint
    op.create_foreign_key('message_task_id_fkey', 'message', 'tasks', ['task_id'], ['id'])