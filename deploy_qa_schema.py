"""
Deploy QA Multi-Agent System Database Schema
============================================

Deploys the QA system schema to the Magnus database.
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def deploy_schema():
    """Deploy QA schema to database"""

    # Database configuration
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', 5432)),
        'database': os.getenv('DB_NAME', 'magnus'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD')
    }

    print("Connecting to database...")
    conn = psycopg2.connect(**db_config)
    conn.autocommit = True
    cursor = conn.cursor()

    print("Reading schema file...")
    with open('src/qa_multi_agent_schema.sql', 'r', encoding='utf-8') as f:
        schema_sql = f.read()

    print("Deploying QA schema...")
    cursor.execute(schema_sql)

    print("Verifying deployment...")
    cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_name LIKE 'qa_%'
        ORDER BY table_name;
    """)

    tables = cursor.fetchall()
    print(f"\nCreated {len(tables)} QA tables:")
    for table in tables:
        print(f"  - {table[0]}")

    # Check views
    cursor.execute("""
        SELECT table_name
        FROM information_schema.views
        WHERE table_name LIKE 'v_%qa%'
        ORDER BY table_name;
    """)

    views = cursor.fetchall()
    print(f"\nCreated {len(views)} QA views:")
    for view in views:
        print(f"  - {view[0]}")

    cursor.close()
    conn.close()

    print("\n[OK] QA schema deployed successfully!")
    return True

if __name__ == "__main__":
    try:
        deploy_schema()
    except Exception as e:
        print(f"\n[ERROR] Failed to deploy schema: {e}")
        raise
