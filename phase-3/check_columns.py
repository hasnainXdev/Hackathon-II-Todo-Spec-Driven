import psycopg2
import os

# Get database URL from environment or use the hardcoded one
database_url = os.environ.get('DATABASE_URL', 'postgresql://neondb_owner:npg_pi5rAIb9acJg@ep-morning-meadow-ahcztv8a-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require')

# Connect to the database
conn = psycopg2.connect(database_url)
cur = conn.cursor()

# Check if due_date column exists in tasks table
cur.execute("""
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'tasks' AND column_name = 'due_date'
""")

result = cur.fetchall()
print('Current due_date column status:', result)

# Check if priority column exists in tasks table
cur.execute("""
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'tasks' AND column_name = 'priority'
""")
result2 = cur.fetchall()
print('Current priority column status:', result2)

cur.close()
conn.close()