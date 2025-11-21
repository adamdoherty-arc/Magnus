"""Check live NBA markets on Kalshi with actual prices"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from src.kalshi_public_client import KalshiPublicClient

client = KalshiPublicClient()

# Get all open markets
print("Fetching all open markets from Kalshi...")
all_markets = client.get_all_markets(status="open")
print(f"Total open markets: {len(all_markets)}")

# Filter for NBA markets
nba_markets = [m for m in all_markets if 'NBA' in m.get('ticker', '').upper()]
print(f"\nNBA markets found: {len(nba_markets)}")

if nba_markets:
    print("\nSample NBA markets:")
    for market in nba_markets[:10]:
        ticker = market.get('ticker', 'N/A')
        title = market.get('title', 'N/A')
        print(f"\n{ticker}")
        print(f"  Title: {title}")

        # Get orderbook to check for prices
        orderbook = client.get_market_orderbook(ticker)
        if orderbook:
            yes_bid = orderbook.get('yes', [{}])[0].get('price') if orderbook.get('yes') else None
            no_bid = orderbook.get('no', [{}])[0].get('price') if orderbook.get('no') else None
            print(f"  Yes bid: {yes_bid}, No bid: {no_bid}")
else:
    print("\nNo NBA markets found. Searching for basketball...")
    basketball_markets = [m for m in all_markets if 'BASKET' in m.get('ticker', '').upper() or
                          'basketball' in m.get('title', '').lower()]
    print(f"Basketball markets: {len(basketball_markets)}")
    if basketball_markets:
        for market in basketball_markets[:5]:
            print(f"  {market.get('ticker')}: {market.get('title')}")
