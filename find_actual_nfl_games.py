"""Find actual NFL game winner markets"""
import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    port=os.getenv('DB_PORT'),
    database=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
)

cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

print("=" * 80)
print("SEARCHING FOR AMERICAN FOOTBALL NFL MARKETS")
print("=" * 80)

# Search for markets with "Winner?" in title and nfl type
cur.execute("""
    SELECT ticker, title, game_date, close_time, expiration_time,
           raw_data->>'expected_expiration_time' as expected_exp,
           raw_data->>'market_type' as mkt_type
    FROM kalshi_markets
    WHERE status != 'closed'
      AND raw_data->>'market_type' = 'nfl'
      AND title ILIKE '%Winner?%'
      AND (
          title ILIKE '%Miami%'
          OR title ILIKE '%Washington%'
          OR title ILIKE '%Pittsburgh%'
          OR title ILIKE '%Buffalo%'
      )
    ORDER BY close_time ASC
    LIMIT 10
""")

markets = cur.fetchall()

print(f"\nFound {len(markets)} NFL game winner markets\n")

for m in markets:
    print(f"{m['title']}")
    print(f"  Ticker: {m['ticker']}")
    print(f"  Type: {m['mkt_type']}")
    print(f"  game_date: {m['game_date']}")
    print(f"  close_time: {m['close_time']}")
    print(f"  expected_expiration_time: {m['expected_exp']}")
    print()

cur.close()
conn.close()
