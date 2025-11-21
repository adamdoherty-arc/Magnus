"""Check what the QA status view returns"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
import json

load_dotenv()

db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': os.getenv('DB_NAME', 'magnus'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD')
}

conn = psycopg2.connect(**db_config)
cur = conn.cursor(cursor_factory=RealDictCursor)

# Get the view definition
cur.execute("""
    SELECT definition
    FROM pg_views
    WHERE viewname = 'v_task_qa_status';
""")

view_def = cur.fetchone()
print("View Definition:")
print(view_def['definition'] if view_def else "View not found!")
print()

# Get sample data
cur.execute("""
    SELECT *
    FROM v_task_qa_status
    LIMIT 1;
""")

sample = cur.fetchone()
if sample:
    print("Sample row columns:")
    for key in sample.keys():
        print(f"  - {key}: {sample[key]}")
else:
    print("No data in view yet")

cur.close()
conn.close()
