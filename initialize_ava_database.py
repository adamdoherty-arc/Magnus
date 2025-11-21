"""
Initialize AVA Conversation Memory Database Schema
==================================================

This script initializes the database schema for AVA's conversation memory system.
It creates all necessary tables, functions, triggers, and views.
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
import sys
from dotenv import load_dotenv

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

def initialize_schema():
    """Initialize the AVA conversation memory schema"""

    print("=" * 80)
    print("INITIALIZING AVA CONVERSATION MEMORY SCHEMA")
    print("=" * 80)

    # Get database credentials
    db_host = os.getenv('DB_HOST', 'localhost')
    db_name = os.getenv('DB_NAME', 'magnus')
    db_user = os.getenv('DB_USER', 'postgres')
    db_password = os.getenv('DB_PASSWORD', '')

    print(f"\n📋 Database: {db_name}@{db_host}")
    print(f"👤 User: {db_user}")

    try:
        # Connect to database
        print("\n🔌 Connecting to database...")
        conn = psycopg2.connect(
            host=db_host,
            database=db_name,
            user=db_user,
            password=db_password
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()

        print("✓ Connected successfully")

        # Read schema file
        print("\n📄 Reading schema file...")
        schema_file = 'src/ava/conversation_memory_schema.sql'

        if not os.path.exists(schema_file):
            print(f"✗ Schema file not found: {schema_file}")
            return False

        with open(schema_file, 'r') as f:
            schema_sql = f.read()

        print(f"✓ Schema file loaded ({len(schema_sql)} bytes)")

        # Execute schema
        print("\n⚙️  Executing schema...")

        # Split by semicolons and execute each statement
        statements = schema_sql.split(';')

        for i, statement in enumerate(statements):
            statement = statement.strip()
            if statement:
                try:
                    cur.execute(statement)
                    print(f"  Statement {i+1}/{len(statements)}: ✓")
                except Exception as e:
                    if "already exists" in str(e).lower():
                        print(f"  Statement {i+1}/{len(statements)}: ⚠ Already exists (skipped)")
                    else:
                        print(f"  Statement {i+1}/{len(statements)}: ✗ {str(e)[:50]}")

        # Verify tables were created
        print("\n🔍 Verifying tables...")
        cur.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_name LIKE 'ava_%'
            ORDER BY table_name
        """)

        tables = cur.fetchall()

        if tables:
            print(f"✓ Found {len(tables)} AVA tables:")
            for table in tables:
                print(f"  • {table[0]}")
        else:
            print("⚠ No AVA tables found")

        # Close connection
        cur.close()
        conn.close()

        print("\n" + "=" * 80)
        print("✅ SCHEMA INITIALIZATION COMPLETE")
        print("=" * 80)

        return True

    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\n" + "=" * 80)
        print("❌ SCHEMA INITIALIZATION FAILED")
        print("=" * 80)
        return False


if __name__ == "__main__":
    success = initialize_schema()

    if success:
        print("\n📋 Next Steps:")
        print("1. Test the integration: python test_omnipresent_ava_integration.py")
        print("2. Run the dashboard: streamlit run dashboard.py")
        print("3. Look for AVA at the top of every page")
    else:
        print("\n📋 Troubleshooting:")
        print("1. Check database credentials in .env file")
        print("2. Ensure PostgreSQL is running")
        print("3. Verify magnus database exists")
        print("4. Check database user permissions")
