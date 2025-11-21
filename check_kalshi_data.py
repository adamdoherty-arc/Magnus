import psycopg2

conn = psycopg2.connect(
    dbname='trading_system',
    user='postgres',
    password='postgres',
    host='localhost'
)
cur = conn.cursor()

# Check active markets
cur.execute("SELECT COUNT(*) FROM kalshi_markets WHERE status = 'active'")
active_count = cur.fetchone()[0]
print(f"Active Kalshi markets: {active_count}")

# Sample markets
cur.execute("SELECT ticker, title, status FROM kalshi_markets LIMIT 10")
print("\nSample markets:")
for row in cur.fetchall():
    print(f"  {row[0]}: {row[1]} ({row[2]})")

cur.close()
conn.close()
