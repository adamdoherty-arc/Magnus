from src.kalshi_db_manager import KalshiDBManager
import psycopg2.extras

db = KalshiDBManager()
conn = db.get_connection()
cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

# Check all markets
cur.execute("SELECT COUNT(*) as total FROM kalshi_markets")
print(f"Total markets: {cur.fetchone()['total']}")

# Check by market type
cur.execute("""
    SELECT market_type, COUNT(*) as count
    FROM kalshi_markets
    GROUP BY market_type
    ORDER BY count DESC
    LIMIT 10
""")
for row in cur.fetchall():
    print(f"  {row['market_type']}: {row['count']}")

# Check NFL specifically
cur.execute("""
    SELECT COUNT(*) as nfl_count
    FROM kalshi_markets
    WHERE ticker LIKE 'KXNFLGAME%' OR market_type = 'nfl'
""")
print(f"\nNFL markets: {cur.fetchone()['nfl_count']}")

# Sample some NFL markets
cur.execute("""
    SELECT ticker, title, yes_price, no_price, status
    FROM kalshi_markets
    WHERE ticker LIKE 'KXNFLGAME%'
    LIMIT 5
""")
print(f"\nSample NFL markets:")
for row in cur.fetchall():
    print(f"  {row['ticker']}: {row['title']}")
    print(f"    Yes: {row['yes_price']}, No: {row['no_price']}, Status: {row['status']}")

cur.close()
db.release_connection(conn)
