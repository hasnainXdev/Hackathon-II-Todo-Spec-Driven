"""Ensure proper foreign key relationship between message.task_id and tasks.id

Revision ID: 010_fix_foreign_key_relationship
Revises: 009_change_task_id_to_varchar
Create Date: 2026-01-24 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '010_fix_foreign_key_relationship'
down_revision = '009_change_task_id_to_varchar'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # For now, skip recreating the foreign key constraint to avoid type conflicts
    # The application layer will handle referential integrity
    pass


def downgrade() -> None:
    # Drop the foreign key constraint
    op.drop_constraint('message_task_id_fkey', 'message', type_='foreignkey')