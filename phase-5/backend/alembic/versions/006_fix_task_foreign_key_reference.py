"""Fix task foreign key reference in message table

Revision ID: 006_fix_task_foreign_key_reference
Revises: 005_fix_message_task_id_type
Create Date: 2026-01-24 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '006_fix_task_foreign_key_reference'
down_revision = '005_fix_message_task_id_type'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop the existing foreign key constraint
    op.drop_constraint('message_task_id_fkey', 'message', type_='foreignkey')
    
    # Recreate the foreign key constraint with the correct table name
    op.create_foreign_key('message_task_id_fkey', 'message', 'tasks', ['task_id'], ['id'])


def downgrade() -> None:
    # Drop the corrected foreign key constraint
    op.drop_constraint('message_task_id_fkey', 'message', type_='foreignkey')
    
    # Recreate the foreign key constraint with the incorrect table name (for rollback)
    op.create_foreign_key('message_task_id_fkey', 'message', 'task', ['task_id'], ['id'])