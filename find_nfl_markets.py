"""Find actual NFL markets in Kalshi database"""
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

print("=" * 80)
print("SEARCHING FOR NFL MARKETS...")
print("=" * 80)

# Search by ticker pattern (NFL markets usually have NFL in ticker)
cur.execute("""
    SELECT ticker, title, home_team, away_team, close_time, yes_price, no_price, raw_data->>'market_type' as actual_type
    FROM kalshi_markets
    WHERE status != 'closed'
      AND ticker ILIKE '%NFL%'
    ORDER BY close_time ASC
    LIMIT 10
""")

markets = cur.fetchall()
print(f"\n1. Markets with 'NFL' in ticker: {len(markets)}")
if markets:
    for m in markets[:3]:
        print(f"\n  {m['ticker']}")
        print(f"  {m['title']}")
        print(f"  Type: {m['actual_type']}")

# Search by market_type in raw_data
cur.execute("""
    SELECT ticker, title, home_team, away_team, close_time, yes_price, no_price, raw_data->>'market_type' as actual_type
    FROM kalshi_markets
    WHERE status != 'closed'
      AND raw_data->>'market_type' = 'nfl'
    ORDER BY close_time ASC
    LIMIT 10
""")

markets = cur.fetchall()
print(f"\n2. Markets with market_type='nfl' in raw_data: {len(markets)}")
if markets:
    for m in markets[:3]:
        print(f"\n  {m['ticker']}")
        print(f"  {m['title']}")
        print(f"  Home: {m['home_team']} / Away: {m['away_team']}")
        print(f"  Yes: {m['yes_price']} / No: {m['no_price']}")

# Search for week 11 NFL games (current week)
cur.execute("""
    SELECT ticker, title, home_team, away_team, close_time, yes_price, no_price, raw_data->>'market_type' as actual_type
    FROM kalshi_markets
    WHERE status != 'closed'
      AND (
          title ILIKE '%week 11%'
          OR title ILIKE '%ravens%'
          OR title ILIKE '%steelers%'
          OR title ILIKE '%bills%'
          OR title ILIKE '%chiefs%'
      )
      AND close_time BETWEEN '2025-11-15' AND '2025-11-18'
    ORDER BY close_time ASC
    LIMIT 10
""")

markets = cur.fetchall()
print(f"\n3. Markets for Week 11 NFL teams: {len(markets)}")
if markets:
    for m in markets[:3]:
        print(f"\n  {m['ticker']}")
        print(f"  {m['title']}")
        print(f"  Type: {m['actual_type']}")

# Check what market types exist in raw_data
cur.execute("""
    SELECT DISTINCT raw_data->>'market_type' as actual_type, COUNT(*) as count
    FROM kalshi_markets
    WHERE status != 'closed'
    GROUP BY actual_type
    ORDER BY count DESC
    LIMIT 20
""")

types = cur.fetchall()
print(f"\n4. Market types in raw_data:")
for t in types:
    print(f"  {t['actual_type']}: {t['count']}")

cur.close()
conn.close()
