"""Fix message task_id column type to properly handle UUID

Revision ID: 007_fix_task_id_type
Revises: 006_fix_task_foreign_key_reference
Create Date: 2026-01-24 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '007_fix_task_id_type'
down_revision = '006_fix_task_foreign_key_reference'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop the foreign key constraint
    op.drop_constraint('message_task_id_fkey', 'message', type_='foreignkey')
    
    # Alter the task_id column to be UUID type
    op.alter_column('message', 'task_id', 
                   type_=postgresql.UUID(as_uuid=False),  # Store as string representation
                   postgresql_using='task_id::uuid')
    
    # Recreate the foreign key constraint
    op.create_foreign_key('message_task_id_fkey', 'message', 'tasks', ['task_id'], ['id'])


def downgrade() -> None:
    # Drop the foreign key constraint
    op.drop_constraint('message_task_id_fkey', 'message', type_='foreignkey')
    
    # Change the column back to varchar
    op.alter_column('message', 'task_id', 
                   type_=sa.VARCHAR(),
                   postgresql_using='task_id::varchar')
    
    # Recreate the foreign key constraint
    op.create_foreign_key('message_task_id_fkey', 'message', 'tasks', ['task_id'], ['id'])