"""Inspect actual Kalshi NFL markets to understand structure"""
import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    port=os.getenv('DB_PORT', '5432'),
    database=os.getenv('DB_NAME', 'magnus'),
    user=os.getenv('DB_USER', 'postgres'),
    password=os.getenv('DB_PASSWORD', ''),
)

cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

# Check for any NFL-related markets by title
print("=" * 80)
print("NFL MARKETS (by title search):")
print("=" * 80)

cur.execute("""
    SELECT ticker, title, market_type, close_time, yes_price, no_price
    FROM kalshi_markets
    WHERE status != 'closed'
      AND (
          title ILIKE '%NFL%'
          OR title ILIKE '%Jets%'
          OR title ILIKE '%Patriots%'
          OR title ILIKE '%football%'
      )
    ORDER BY close_time ASC
    LIMIT 10
""")

markets = cur.fetchall()
print(f"\nFound {len(markets)} markets\n")

for m in markets:
    print(f"Ticker: {m['ticker']}")
    print(f"Title: {m['title']}")
    print(f"Type: {m['market_type']}")
    print(f"Close: {m['close_time']}")
    print(f"Yes: {m['yes_price']} / No: {m['no_price']}")
    print("-" * 80)

# Check all unique market types
print("\n" + "=" * 80)
print("ALL UNIQUE MARKET TYPES:")
print("=" * 80)
cur.execute("SELECT DISTINCT market_type FROM kalshi_markets")
types = cur.fetchall()
for t in types:
    print(f"  - {t['market_type']}")

# Check if there's a category column
print("\n" + "=" * 80)
print("SAMPLE MARKET STRUCTURE:")
print("=" * 80)
cur.execute("SELECT * FROM kalshi_markets LIMIT 1")
if cur.rowcount > 0:
    sample = cur.fetchone()
    for key, value in sample.items():
        print(f"{key}: {value}")

cur.close()
conn.close()
