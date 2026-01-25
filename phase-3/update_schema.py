import psycopg2
import os
from urllib.parse import urlparse

# Get database URL from environment or use the hardcoded one
database_url = os.environ.get('DATABASE_URL', 'postgresql://neondb_owner:npg_pi5rAIb9acJg@ep-morning-meadow-ahcztv8a-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require')

# Ensure SSL mode is properly set
if 'sslmode=' not in database_url:
    if '?' in database_url:
        database_url += "&sslmode=require"
    else:
        database_url += "?sslmode=require"

# Connect to the database with proper SSL settings
conn = psycopg2.connect(database_url)
cur = conn.cursor()

try:
    # Add due_date column if it doesn't exist
    cur.execute("""
    DO $$ 
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'tasks' AND column_name = 'due_date'
        ) THEN
            ALTER TABLE tasks ADD COLUMN due_date TIMESTAMP WITH TIME ZONE;
        END IF;
    END $$;
    """)
    print("Successfully ensured due_date column exists")

    # Add priority column if it doesn't exist
    cur.execute("""
    DO $$ 
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'tasks' AND column_name = 'priority'
        ) THEN
            ALTER TABLE tasks ADD COLUMN priority VARCHAR(20) DEFAULT 'medium';
        END IF;
    END $$;
    """)
    print("Successfully ensured priority column exists")

    # Commit the changes
    conn.commit()
    print("Database schema updated successfully!")

except Exception as e:
    print(f"Error updating database schema: {e}")
    conn.rollback()

finally:
    cur.close()
    conn.close()