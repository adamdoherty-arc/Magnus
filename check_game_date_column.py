"""Check if game_date column has actual game dates"""
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

cur.execute("""
    SELECT ticker, title, game_date, close_time, expiration_time,
           raw_data->>'expected_expiration_time' as expected_exp
    FROM kalshi_markets
    WHERE raw_data->>'market_type' = 'nfl'
      AND status != 'closed'
    LIMIT 5
""")

markets = cur.fetchall()

print("=" * 80)
print("NFL MARKET DATE FIELDS")
print("=" * 80)

for m in markets:
    print(f"\n{m['title']}")
    print(f"  game_date: {m['game_date']}")
    print(f"  close_time: {m['close_time']}")
    print(f"  expiration_time: {m['expiration_time']}")
    print(f"  expected_expiration_time: {m['expected_exp']}")

cur.close()
conn.close()
