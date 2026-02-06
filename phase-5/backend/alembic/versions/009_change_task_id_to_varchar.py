"""Change message task_id column to use VARCHAR instead of UUID

Revision ID: 009_change_task_id_to_varchar
Revises: 008_remove_duplicate_task_table
Create Date: 2026-01-24 17:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '009_change_task_id_to_varchar'
down_revision = '008_remove_duplicate_task_table'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Change the task_id column to VARCHAR(36) to store UUID as string
    # The foreign key constraint was already dropped in the previous migration
    op.alter_column('message', 'task_id',
                   type_=sa.String(36),
                   existing_type=sa.UUID(as_uuid=False))  # Assuming it was UUID before

    # Don't recreate the foreign key constraint yet - that will be done in the next migration
    # when the tasks.id column is also changed to VARCHAR


def downgrade() -> None:
    # Drop the foreign key constraint
    op.drop_constraint('message_task_id_fkey', 'message', type_='foreignkey')
    
    # Change the column back to UUID type
    op.alter_column('message', 'task_id',
                   type_=sa.UUID(as_uuid=False),
                   existing_type=sa.String(36))
    
    # Recreate the foreign key constraint
    op.create_foreign_key('message_task_id_fkey', 'message', 'tasks', ['task_id'], ['id'])