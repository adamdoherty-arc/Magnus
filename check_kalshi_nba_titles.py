"""
Search for NBA markets by title
"""
from src.kalshi_db_manager import KalshiDBManager
import psycopg2.extras

db = KalshiDBManager()
conn = db.get_connection()
cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

print("\n" + "="*80)
print("SEARCHING FOR NBA MARKETS BY TITLE")
print("="*80)

# Search for NBA-related titles
cur.execute("""
    SELECT ticker, title, status, yes_price, no_price, market_type
    FROM kalshi_markets
    WHERE (LOWER(title) LIKE '%lakers%'
        OR LOWER(title) LIKE '%warriors%'
        OR LOWER(title) LIKE '%celtics%'
        OR LOWER(title) LIKE '%knicks%'
        OR LOWER(title) LIKE '%heat%'
        OR LOWER(title) LIKE '%nba%'
        OR LOWER(title) LIKE '%basketball%')
    AND status = 'active'
    LIMIT 20
""")

nba_markets = cur.fetchall()

print(f"\nFound {len(nba_markets)} NBA-related active markets:")
print("-" * 80)

for i, market in enumerate(nba_markets, 1):
    price_str = f"YES={market['yes_price']}¢ NO={market['no_price']}¢" if market['yes_price'] else "No prices"
    print(f"{i:2}. {market['title']}")
    print(f"    Ticker: {market['ticker']} | Type: {market['market_type']} | {price_str}")

# Check tickers starting with certain patterns
cur.execute("""
    SELECT ticker, title, status, yes_price, market_type
    FROM kalshi_markets
    WHERE ticker LIKE 'KXNBA%'
    AND status = 'active'
    LIMIT 10
""")

ticker_markets = cur.fetchall()

print("\n" + "="*80)
print(f"Markets with ticker starting with 'KXNBA': {len(ticker_markets)}")
print("-" * 80)

for i, market in enumerate(ticker_markets, 1):
    price_str = f"YES={market['yes_price']}¢" if market['yes_price'] else "No prices"
    print(f"{i}. {market['ticker']} | {market['title'][:50]} | {price_str}")

cur.close()
db.release_connection(conn)
