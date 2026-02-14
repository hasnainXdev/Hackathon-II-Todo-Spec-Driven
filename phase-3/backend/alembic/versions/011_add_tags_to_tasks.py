"""Add tags column to tasks table

Revision ID: 011_add_tags_to_tasks
Revises: 010_fix_foreign_key_relationship
Create Date: 2026-02-14 15:30:00.000000

"""
from typing import Sequence, Union
import json
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
from sqlmodel import SQLModel
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = '011_add_tags_to_tasks'
down_revision: Union[str, None] = '010_fix_foreign_key_relationship'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add the tags column as a JSON type column
    op.add_column('tasks', sa.Column('tags', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    
    # Update existing tasks to have an empty tags array
    conn = op.get_bind()
    conn.execute(sa.text("UPDATE tasks SET tags = '[]' WHERE tags IS NULL OR tags = ''"))
    

def downgrade() -> None:
    # Remove the tags column
    op.drop_column('tasks', 'tags')