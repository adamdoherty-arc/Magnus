"""
Check Dallas Cowboys vs Las Vegas Raiders Kalshi market data
"""
import sys
from src.kalshi_db_manager import KalshiDBManager
import psycopg2.extras

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

db = KalshiDBManager()
conn = db.get_connection()
cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

# Search for Dallas vs Las Vegas market
query = """
SELECT
    ticker,
    title,
    yes_price,
    no_price,
    volume,
    status,
    close_time
FROM kalshi_markets
WHERE
    (title ILIKE '%Dallas%' OR title ILIKE '%Cowboys%')
    AND (title ILIKE '%Las Vegas%' OR title ILIKE '%Raiders%')
    AND status != 'closed'
ORDER BY volume DESC
LIMIT 5;
"""

cur.execute(query)
results = cur.fetchall()

print(f"Found {len(results)} markets matching Dallas vs Las Vegas:\n")

for market in results:
    print(f"Ticker: {market['ticker']}")
    print(f"Title: {market['title']}")
    print(f"Yes Price: {market['yes_price']:.2f}¢")
    print(f"No Price: {market['no_price']:.2f}¢")
    print(f"Volume: {market['volume']}")
    print(f"Status: {market['status']}")
    print(f"Close Time: {market['close_time']}")
    print("-" * 60)

cur.close()
db.release_connection(conn)
