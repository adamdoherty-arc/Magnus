"""
Find actual college football markets on Kalshi
"""
import os
from dotenv import load_dotenv
from src.kalshi_integration import KalshiIntegration

def main():
    load_dotenv()

    print("="*80)
    print("SEARCHING FOR COLLEGE FOOTBALL MARKETS")
    print("="*80)

    kalshi = KalshiIntegration()

    # Get more markets
    print("\nFetching markets from Kalshi...")
    all_markets = kalshi.get_markets(limit=1000, status='active')
    print(f"Retrieved {len(all_markets)} total markets\n")

    # Analyze ALL ticker prefixes
    print("Analyzing all ticker prefixes...")
    prefixes = {}
    for market in all_markets:
        ticker = market.get('ticker', '')
        # Get first part before hyphen
        prefix = ticker.split('-')[0] if '-' in ticker else ticker
        if prefix not in prefixes:
            prefixes[prefix] = []
        prefixes[prefix].append(market)

    print(f"Found {len(prefixes)} unique ticker prefixes\n")

    # Look for college/NCAA related prefixes
    print("="*80)
    print("SEARCHING FOR COLLEGE FOOTBALL PREFIXES")
    print("="*80)

    college_prefixes = []
    for prefix in prefixes.keys():
        prefix_lower = prefix.lower()
        # Look for CFB, NCAA, COL, NCAAF patterns
        if any(pattern in prefix_lower for pattern in ['cfb', 'ncaa', 'col', 'ncaaf', 'fbs']):
            college_prefixes.append(prefix)
            print(f"\nFound college prefix: {prefix} ({len(prefixes[prefix])} markets)")
            # Show sample
            sample = prefixes[prefix][0]
            print(f"  Sample: {sample.get('title', 'N/A')[:80]}")

    if not college_prefixes:
        print("\nNo obvious college football prefixes found.")
        print("\nShowing ALL unique prefixes to manually identify:")
        print("="*80)
        for prefix, markets in sorted(prefixes.items(), key=lambda x: len(x[1]), reverse=True):
            if prefix.startswith('KX'):
                print(f"\n{prefix}: {len(markets)} markets")
                print(f"  Sample: {markets[0].get('title', 'N/A')[:80]}")

                # Show first market details
                if len(markets) > 0:
                    m = markets[0]
                    ticker = m.get('ticker', '')
                    title = m.get('title', '')

                    # Check if it might be college by looking for university names
                    college_indicators = ['university', 'state', 'college', 'wildcats',
                                         'bulldogs', 'crimson', 'longhorns', 'buckeyes',
                                         'wolverines', 'tigers', 'aggies', 'rebels']

                    if any(ind in title.lower() for ind in college_indicators):
                        print(f"  >>> POSSIBLE COLLEGE MARKET!")

if __name__ == "__main__":
    main()
