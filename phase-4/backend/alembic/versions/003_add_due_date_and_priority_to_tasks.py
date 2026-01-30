from alembic import op
import sqlalchemy as sa
from sqlalchemy import Column, String, DateTime
import sqlmodel
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '003_add_due_date_and_priority_to_tasks'
down_revision = '002_add_conversation_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add due_date column to tasks table
    op.add_column('tasks', sa.Column('due_date', sa.DateTime(timezone=True), nullable=True))
    
    # Add priority column to tasks table
    op.add_column('tasks', sa.Column('priority', sa.String(length=20), nullable=True, server_default='medium'))


def downgrade() -> None:
    # Remove priority column from tasks table
    op.drop_column('tasks', 'priority')
    
    # Remove due_date column from tasks table
    op.drop_column('tasks', 'due_date')