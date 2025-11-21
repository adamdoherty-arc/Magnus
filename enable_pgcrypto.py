"""Enable pgcrypto extension for digest function"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    port=os.getenv('DB_PORT', '5432'),
    database=os.getenv('DB_NAME', 'magnus'),
    user=os.getenv('DB_USER', 'postgres'),
    password=os.getenv('DB_PASSWORD', '')
)

try:
    with conn.cursor() as cur:
        # Enable pgcrypto extension
        cur.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")
        conn.commit()
        print("[OK] pgcrypto extension enabled successfully")

        # Verify it's enabled
        cur.execute("""
            SELECT extname, extversion
            FROM pg_extension
            WHERE extname = 'pgcrypto';
        """)
        result = cur.fetchone()
        if result:
            print(f"[OK] Verified: pgcrypto version {result[1]} is active")
        else:
            print("[WARNING] Could not verify extension")

except Exception as e:
    print(f"[ERROR] Error enabling pgcrypto: {e}")
    conn.rollback()
finally:
    conn.close()
