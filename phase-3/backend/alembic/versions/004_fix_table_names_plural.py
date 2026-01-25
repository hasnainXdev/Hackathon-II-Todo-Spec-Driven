"""fix_table_names_plural

Revision ID: 004_fix_table_names_plural
Revises: 003_add_due_date_and_priority_to_tasks
Create Date: 2026-01-23 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '004_fix_table_names_plural'
down_revision = '003_add_due_date_and_priority_to_tasks'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Rename tables from singular to plural to match model definitions
    # Check if the tables exist with the old names before renaming
    connection = op.get_bind()
    
    # Get table names from the database
    result = connection.execute(sa.text("""
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname = 'public' 
        AND tablename IN ('message', 'conversation')
    """))
    
    tables_exist = [row[0] for row in result.fetchall()]
    
    # Rename tables if they exist with old names
    if 'message' in tables_exist:
        op.rename_table('message', 'messages')
    
    if 'conversation' in tables_exist:
        op.rename_table('conversation', 'conversations')


def downgrade() -> None:
    # Revert table names from plural to singular
    connection = op.get_bind()
    
    # Get table names from the database
    result = connection.execute(sa.text("""
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname = 'public' 
        AND tablename IN ('messages', 'conversations')
    """))
    
    tables_exist = [row[0] for row in result.fetchall()]
    
    # Rename tables back to old names if they exist
    if 'messages' in tables_exist:
        op.rename_table('messages', 'message')
    
    if 'conversations' in tables_exist:
        op.rename_table('conversations', 'conversation')