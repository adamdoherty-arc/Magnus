"""Quick test of Kalshi public API - NO AUTH REQUIRED"""
from src.kalshi_public_client import KalshiPublicClient

client = KalshiPublicClient()

# Get all open markets
print("Fetching markets...")
markets = client.get_all_markets(status='open', limit=10)
print(f"✅ Found {len(markets)} markets")

if markets:
    print(f"\nFirst market: {markets[0].get('title')}")
    print(f"Ticker: {markets[0].get('ticker')}")

    # Get orderbook
    ticker = markets[0].get('ticker')
    orderbook = client.get_market_orderbook(ticker)
    if orderbook:
        print(f"✅ Orderbook retrieved for {ticker}")
