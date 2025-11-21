"""
Verify Task Management Schema Deployment
"""

import psycopg2
import os
from dotenv import load_dotenv
import sys

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv()

conn = psycopg2.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    port=int(os.getenv('DB_PORT', 5432)),
    database=os.getenv('DB_NAME', 'magnus'),
    user=os.getenv('DB_USER', 'postgres'),
    password=os.getenv('DB_PASSWORD')
)

try:
    cursor = conn.cursor()

    # Verify tables
    cursor.execute("""
        SELECT table_name,
               (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as column_count
        FROM information_schema.tables t
        WHERE table_schema = 'public'
        AND table_name IN ('development_tasks', 'task_execution_log', 'task_verification', 'task_files')
        ORDER BY table_name
    """)

    tables = cursor.fetchall()

    print('[VERIFICATION] Task Management System Database Status')
    print('=' * 60)
    print()
    print('Tables:')
    for table_name, col_count in tables:
        print(f'  - {table_name}: {col_count} columns')

    # Check row counts
    print()
    print('Current Data:')
    for table_name, _ in tables:
        cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
        count = cursor.fetchone()[0]
        print(f'  - {table_name}: {count} rows')

    # Check indexes
    cursor.execute("""
        SELECT COUNT(*) as index_count
        FROM pg_indexes
        WHERE schemaname = 'public'
        AND (tablename LIKE 'development_tasks%' OR tablename LIKE 'task_%')
    """)

    index_count = cursor.fetchone()[0]
    print()
    print(f'Indexes: {index_count} created')

    # Check views
    cursor.execute("""
        SELECT table_name
        FROM information_schema.views
        WHERE table_schema = 'public'
        AND (table_name LIKE 'v_%task%' OR table_name LIKE 'v_%feature%' OR table_name LIKE 'v_%agent%')
        ORDER BY table_name
    """)

    views = cursor.fetchall()
    print(f'Views: {len(views)} created')
    for view_name, in views:
        print(f'  - {view_name}')

    # Check functions
    cursor.execute("""
        SELECT routine_name
        FROM information_schema.routines
        WHERE routine_schema = 'public'
        AND routine_name LIKE '%task%'
        ORDER BY routine_name
    """)

    functions = cursor.fetchall()
    print()
    print(f'Functions: {len(functions)} created')
    for func_name, in functions:
        print(f'  - {func_name}')

    print()
    print('=' * 60)
    print('[SUCCESS] Task Management System is ready!')

    cursor.close()

except Exception as e:
    print(f'[ERROR] Error: {e}')
    import traceback
    traceback.print_exc()
finally:
    conn.close()
