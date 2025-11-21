"""
Quick check of NBA Kalshi markets in database
"""
from src.kalshi_db_manager import KalshiDBManager
import psycopg2.extras

db = KalshiDBManager()
conn = db.get_connection()
cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

print("\n" + "="*80)
print("NBA KALSHI MARKETS CHECK")
print("="*80)

# Check all NBA markets
cur.execute("""
    SELECT
        ticker, title, sector, market_type, home_team, away_team,
        yes_price, no_price, status
    FROM kalshi_markets
    WHERE LOWER(sector) = 'nba' OR LOWER(market_type) = 'nba'
    ORDER BY yes_price DESC NULLS LAST
    LIMIT 10
""")

nba_markets = cur.fetchall()

print(f"\nFound {len(nba_markets)} NBA markets")
print("\nFirst 10 markets:")
print("-" * 80)

for i, market in enumerate(nba_markets, 1):
    print(f"\n{i}. {market['title']}")
    print(f"   Ticker: {market['ticker']}")
    print(f"   Sector: {market['sector']}")
    print(f"   Market Type: {market['market_type']}")
    print(f"   Teams: {market['away_team']} @ {market['home_team']}")
    print(f"   Prices: YES={market['yes_price']}¢ NO={market['no_price']}¢")
    print(f"   Status: {market['status']}")

# Check active NBA markets with prices
cur.execute("""
    SELECT COUNT(*) as count
    FROM kalshi_markets
    WHERE (LOWER(sector) = 'nba' OR LOWER(market_type) = 'nba')
    AND status = 'active'
    AND yes_price IS NOT NULL
""")

active_count = cur.fetchone()['count']
print(f"\n" + "="*80)
print(f"Active NBA markets with prices: {active_count}")
print("="*80)

cur.close()
db.release_connection(conn)
