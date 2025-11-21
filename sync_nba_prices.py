"""Sync NBA game market prices from Kalshi"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from src.kalshi_public_client import KalshiPublicClient
from src.kalshi_db_manager import KalshiDBManager

print("=" * 80)
print("KALSHI NBA PRICE SYNC")
print("=" * 80)

client = KalshiPublicClient()
db = KalshiDBManager()

# Get all NBA game markets from database
conn = db.get_connection()
cur = conn.cursor()

cur.execute("""
    SELECT ticker
    FROM kalshi_markets
    WHERE ticker LIKE 'KXNBAGAME%'
    AND status = 'active'
""")

nba_markets = [row[0] for row in cur.fetchall()]
print(f"\nFound {len(nba_markets)} active NBA game markets")

# Update prices for each market
updated_count = 0
empty_count = 0

print("\nFetching latest prices...")
for ticker in nba_markets:
    try:
        orderbook = client.get_market_orderbook(ticker)

        if orderbook:
            # Kalshi orderbook is nested: {'orderbook': {'yes': [[price_cents, volume]], ...}}
            orderbook_data = orderbook.get('orderbook', {})
            yes_bids = orderbook_data.get('yes', [])
            no_bids = orderbook_data.get('no', [])

            if yes_bids and no_bids:
                # Each bid is [price_in_cents, volume]
                # Use the highest bid price (last in sorted list) as market consensus
                yes_price = yes_bids[-1][0] / 100  # Last element = highest price
                no_price = no_bids[-1][0] / 100

                if yes_price > 0 and no_price > 0:
                    # Update database
                    cur.execute("""
                        UPDATE kalshi_markets
                        SET yes_price = %s,
                            no_price = %s,
                            last_updated = NOW()
                        WHERE ticker = %s
                    """, (yes_price, no_price, ticker))

                    updated_count += 1
                    print(f"  ✓ {ticker}: {yes_price:.2f} / {no_price:.2f}")
                else:
                    empty_count += 1
            else:
                empty_count += 1
        else:
            empty_count += 1

    except Exception as e:
        print(f"  ✗ Error for {ticker}: {e}")

conn.commit()
cur.close()
db.release_connection(conn)

print("\n" + "=" * 80)
print("SYNC COMPLETE")
print("=" * 80)
print(f"✅ Updated prices: {updated_count}")
print(f"⚠️  Empty orderbooks: {empty_count}")
print(f"📊 Total markets: {len(nba_markets)}")
print(f"📈 Coverage: {updated_count}/{len(nba_markets)} ({updated_count/len(nba_markets)*100:.1f}%)")
print("=" * 80)
