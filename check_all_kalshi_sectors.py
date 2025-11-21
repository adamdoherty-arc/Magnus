"""
Check what sectors/sports exist in Kalshi database
"""
from src.kalshi_db_manager import KalshiDBManager
import psycopg2.extras

db = KalshiDBManager()
conn = db.get_connection()
cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

print("\n" + "="*80)
print("KALSHI MARKETS - SECTOR ANALYSIS")
print("="*80)

# Count by sector
cur.execute("""
    SELECT
        COALESCE(sector, 'NULL') as sector,
        COUNT(*) as count,
        SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active_count,
        SUM(CASE WHEN yes_price IS NOT NULL THEN 1 ELSE 0 END) as with_prices
    FROM kalshi_markets
    GROUP BY sector
    ORDER BY count DESC
""")

sectors = cur.fetchall()

print("\nMarkets by Sector:")
print("-" * 80)
for sector in sectors:
    print(f"{sector['sector']:20} | Total: {sector['count']:4} | Active: {sector['active_count']:4} | With Prices: {sector['with_prices']:4}")

# Count by market_type
cur.execute("""
    SELECT
        COALESCE(market_type, 'NULL') as market_type,
        COUNT(*) as count,
        SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active_count
    FROM kalshi_markets
    GROUP BY market_type
    ORDER BY count DESC
""")

types = cur.fetchall()

print("\n" + "="*80)
print("Markets by Type:")
print("-" * 80)
for mtype in types:
    print(f"{mtype['market_type']:20} | Total: {mtype['count']:4} | Active: {mtype['active_count']:4}")

# Show sample active markets
cur.execute("""
    SELECT ticker, title, sector, market_type
    FROM kalshi_markets
    WHERE status = 'active'
    AND yes_price IS NOT NULL
    LIMIT 20
""")

samples = cur.fetchall()

print("\n" + "="*80)
print("Sample Active Markets with Prices:")
print("-" * 80)
for i, market in enumerate(samples, 1):
    print(f"{i:2}. [{market['sector']:10}] {market['title'][:60]}")

# Search for basketball or NBA
cur.execute("""
    SELECT COUNT(*) as count
    FROM kalshi_markets
    WHERE LOWER(title) LIKE '%lakers%'
    OR LOWER(title) LIKE '%warriors%'
    OR LOWER(title) LIKE '%basketball%'
    OR LOWER(title) LIKE '%nba%'
""")

bball_count = cur.fetchone()['count']
print(f"\n" + "="*80)
print(f"Markets mentioning NBA/basketball teams: {bball_count}")
print("="*80)

cur.close()
db.release_connection(conn)
