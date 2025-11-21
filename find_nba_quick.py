"""Quick search for NBA markets on Kalshi"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from src.kalshi_public_client import KalshiPublicClient

client = KalshiPublicClient()

# Try specific NBA ticker patterns
test_tickers = [
    'KXNBAGAME-25NOV19DETIND-DET',  # Detroit vs Indiana (user mentioned)
    'KXNBAGAME-25NOV19DETIND-IND',
    'KXNBA',  # Generic NBA search
]

print("Testing specific NBA market tickers...")
for ticker in test_tickers:
    print(f"\nTrying: {ticker}")
    market = client.get_market(ticker)
    if market:
        print(f"  ✓ Found: {market.get('title')}")

        # Get orderbook for prices
        orderbook = client.get_market_orderbook(ticker)
        if orderbook:
            yes_bids = orderbook.get('yes', [])
            no_bids = orderbook.get('no', [])
            if yes_bids:
                yes_price = yes_bids[0].get('price', 'N/A')
                print(f"  Yes price: {yes_price}")
            if no_bids:
                no_price = no_bids[0].get('price', 'N/A')
                print(f"  No price: {no_price}")
        break  # Found one, stop
    else:
        print(f"  ✗ Not found")

# Also try to get markets with series_ticker filter
print("\n\nSearching for NBA series...")
try:
    series_list = client.get_series()
    nba_series = [s for s in series_list if 'NBA' in s.get('ticker', '').upper() or
                  'basketball' in s.get('title', '').lower()]
    print(f"NBA-related series: {len(nba_series)}")
    for series in nba_series[:5]:
        print(f"  {series.get('ticker')}: {series.get('title')}")
except Exception as e:
    print(f"Error fetching series: {e}")
