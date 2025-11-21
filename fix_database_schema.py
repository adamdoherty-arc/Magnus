"""
Quick fix for database schema issues preventing dashboard from starting
"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def fix_database_schema():
    """Drop and recreate problematic tables"""
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cur = conn.cursor()

        print("Fixing database schema issues...")

        # Drop the problematic tables if they exist
        print("Dropping problematic tables...")
        cur.execute("DROP TABLE IF EXISTS watchlist_stocks CASCADE;")
        cur.execute("DROP TABLE IF EXISTS tradingview_watchlists CASCADE;")

        # Recreate them with correct schema
        print("Recreating tables with correct schema...")

        cur.execute("""
            CREATE TABLE IF NOT EXISTS tradingview_watchlists (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) UNIQUE NOT NULL,
                created_date TIMESTAMP DEFAULT NOW(),
                last_updated TIMESTAMP
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS watchlist_stocks (
                id SERIAL PRIMARY KEY,
                watchlist_id INTEGER REFERENCES tradingview_watchlists(id) ON DELETE CASCADE,
                symbol VARCHAR(10) NOT NULL,
                added_date TIMESTAMP DEFAULT NOW(),
                current_price DECIMAL(10,2),
                price_updated TIMESTAMP,
                UNIQUE(watchlist_id, symbol)
            )
        """)

        # Create indexes
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_watchlist_stocks_symbol
            ON watchlist_stocks(symbol)
        """)

        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_watchlist_stocks_watchlist_id
            ON watchlist_stocks(watchlist_id)
        """)

        conn.commit()
        print("[SUCCESS] Database schema fixed!")

        cur.close()
        conn.close()
        return True

    except Exception as e:
        print(f"[ERROR] Failed to fix database schema: {e}")
        return False

if __name__ == "__main__":
    fix_database_schema()
