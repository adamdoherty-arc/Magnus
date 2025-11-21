"""
Check Kalshi for college football market naming patterns
"""
import os
from dotenv import load_dotenv
from src.kalshi_integration import KalshiIntegration

def main():
    load_dotenv()

    print("="*80)
    print("KALSHI COLLEGE FOOTBALL MARKET ANALYSIS")
    print("="*80)

    kalshi = KalshiIntegration()

    # Get a larger sample
    print("\nFetching markets from Kalshi...")
    all_markets = kalshi.get_markets(limit=1000, status='active')
    print(f"Retrieved {len(all_markets)} total markets")

    # Look for college/NCAA patterns
    print("\nSearching for college football markets...")

    college_patterns = [
        'cfb', 'ncaaf', 'college', 'ncaa', 'fbs', 'cfp',
        'sec-', 'big10', 'big12', 'acc-', 'pac12',
        'alabama', 'georgia', 'ohio', 'michigan', 'texas',
        'clemson', 'oregon', 'penn', 'notre dame', 'usc',
        'lsu', 'florida', 'tennessee', 'oklahoma', 'auburn',
        'miami', 'wisconsin', 'iowa', 'nebraska', 'stanford'
    ]

    college_markets = []

    for market in all_markets:
        ticker = market.get('ticker', '').lower()
        title = market.get('title', '').lower()
        subtitle = market.get('subtitle', '').lower()

        combined = f"{ticker} {title} {subtitle}"

        # Check all patterns
        for pattern in college_patterns:
            if pattern in combined:
                college_markets.append(market)
                break

    print(f"\nFound {len(college_markets)} college football markets")

    if college_markets:
        print("\nSample college football markets:")
        for i, market in enumerate(college_markets[:10], 1):
            print(f"\n{i}. Ticker: {market.get('ticker', 'N/A')}")
            print(f"   Title: {market.get('title', 'N/A')}")
            print(f"   Subtitle: {market.get('subtitle', 'N/A')}")
            print(f"   Status: {market.get('status', 'N/A')}")
    else:
        print("\nNo college markets found with common patterns.")
        print("Showing sample of all markets to identify patterns:")
        for i, market in enumerate(all_markets[:20], 1):
            ticker = market.get('ticker', '')
            if 'nfl' not in ticker.lower():  # Skip NFL to see other sports
                print(f"\n{i}. Ticker: {ticker}")
                print(f"   Title: {market.get('title', 'N/A')}")

    # Show ticker prefixes to understand naming
    print("\n" + "="*80)
    print("TICKER PREFIX ANALYSIS")
    print("="*80)
    prefixes = {}
    for market in all_markets:
        ticker = market.get('ticker', '')
        prefix = ticker.split('-')[0] if '-' in ticker else ticker[:10]
        prefixes[prefix] = prefixes.get(prefix, 0) + 1

    print("\nTop ticker prefixes (showing sports/categories):")
    for prefix, count in sorted(prefixes.items(), key=lambda x: x[1], reverse=True)[:20]:
        print(f"  {prefix}: {count} markets")

if __name__ == "__main__":
    main()
