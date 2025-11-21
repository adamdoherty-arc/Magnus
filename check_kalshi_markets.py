"""Check what Kalshi NFL markets look like"""
import psycopg2
import psycopg2.extras
import os

# Get database connection
conn = psycopg2.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    port=os.getenv('DB_PORT', '5432'),
    database=os.getenv('DB_NAME', 'trading'),
    user=os.getenv('DB_USER', 'postgres'),
    password=os.getenv('DB_PASSWORD', ''),
)

cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

# Get sample NFL markets
cur.execute("""
    SELECT ticker, title, market_type, close_time, yes_price, no_price
    FROM kalshi_markets
    WHERE market_type IN ('nfl', 'winner')
      AND status != 'closed'
      AND title ILIKE '%jets%'
    ORDER BY close_time ASC
    LIMIT 5
""")

markets = cur.fetchall()

print("=" * 80)
print("SAMPLE KALSHI NFL MARKETS (Jets related):")
print("=" * 80)

for m in markets:
    print(f"\nTicker: {m['ticker']}")
    print(f"Title: {m['title']}")
    print(f"Type: {m['market_type']}")
    print(f"Close Time: {m['close_time']}")
    print(f"Yes Price: {m['yes_price']}")
    print(f"No Price: {m['no_price']}")

# Also check for Patriots
cur.execute("""
    SELECT ticker, title, market_type, close_time, yes_price, no_price
    FROM kalshi_markets
    WHERE market_type IN ('nfl', 'winner')
      AND status != 'closed'
      AND title ILIKE '%patriots%'
    ORDER BY close_time ASC
    LIMIT 5
""")

markets = cur.fetchall()

print("\n" + "=" * 80)
print("SAMPLE KALSHI NFL MARKETS (Patriots related):")
print("=" * 80)

for m in markets:
    print(f"\nTicker: {m['ticker']}")
    print(f"Title: {m['title']}")
    print(f"Type: {m['market_type']}")

# Get total counts
cur.execute("SELECT market_type, COUNT(*) as count FROM kalshi_markets GROUP BY market_type ORDER BY count DESC LIMIT 10")
types = cur.fetchall()

print("\n" + "=" * 80)
print("MARKET TYPE DISTRIBUTION:")
print("=" * 80)
for t in types:
    print(f"{t['market_type']}: {t['count']}")

cur.close()
conn.close()
