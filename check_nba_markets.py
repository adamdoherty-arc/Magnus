"""Check NBA Kalshi market format"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from src.kalshi_db_manager import KalshiDBManager
import psycopg2.extras

db = KalshiDBManager()
conn = db.get_connection()
cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

cur.execute("""
    SELECT ticker, title, yes_price, no_price
    FROM kalshi_markets
    WHERE ticker LIKE 'KXNBAGAME%'
    AND status = 'active'
    LIMIT 5
""")

results = cur.fetchall()
print('Sample NBA Kalshi markets:')
for r in results:
    print(f'  {r["ticker"]}')
    print(f'    Title: {r["title"]}')
    print(f'    Odds: Yes={r["yes_price"]:.2f}, No={r["no_price"]:.2f}')
    print()

cur.close()
db.release_connection(conn)
