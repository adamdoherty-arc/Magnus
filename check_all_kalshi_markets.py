"""
Check ALL Kalshi markets for college football
"""
import os
from dotenv import load_dotenv
from src.kalshi_integration import KalshiIntegration

def main():
    load_dotenv()

    print("="*80)
    print("FETCHING ALL KALSHI MARKETS")
    print("="*80)

    kalshi = KalshiIntegration()

    # Try to get ALL markets (no limit)
    print("\nFetching ALL active markets from Kalshi...")
    try:
        all_markets = kalshi.get_markets(limit=5000, status='active')
        print(f"Retrieved {len(all_markets)} total active markets")
    except Exception as e:
        print(f"Error fetching markets: {e}")
        return

    # Count by sport/type
    print("\n" + "="*80)
    print("MARKET BREAKDOWN BY PREFIX")
    print("="*80)

    prefixes = {}
    for market in all_markets:
        ticker = market.get('ticker', '')
        prefix = ticker.split('-')[0] if '-' in ticker else ticker[:20]
        prefixes[prefix] = prefixes.get(prefix, 0) + 1

    # Sort and display
    sorted_prefixes = sorted(prefixes.items(), key=lambda x: x[1], reverse=True)

    for prefix, count in sorted_prefixes:
        print(f"{prefix}: {count} markets")

    # Look for any college indicators in titles
    print("\n" + "="*80)
    print("SEARCHING TITLES FOR COLLEGE FOOTBALL INDICATORS")
    print("="*80)

    college_keywords = [
        'cfb', 'ncaa', 'college', 'fbs', 'cfp',
        'alabama', 'georgia bulldogs', 'ohio state', 'michigan',
        'texas longhorns', 'clemson', 'oregon', 'penn state',
        'notre dame', 'usc trojans', 'lsu', 'florida gators',
        'tennessee volunteers', 'oklahoma', 'sec championship',
        'big ten championship', 'acc championship', 'pac-12',
        'playoff', 'bowl'
    ]

    potential_college = []
    for market in all_markets:
        title = market.get('title', '').lower()
        ticker = market.get('ticker', '').lower()
        combined = f"{title} {ticker}"

        for keyword in college_keywords:
            if keyword in combined:
                potential_college.append({
                    'ticker': market.get('ticker'),
                    'title': market.get('title'),
                    'keyword': keyword
                })
                break

    if potential_college:
        print(f"\nFound {len(potential_college)} potential college football markets:")
        for i, m in enumerate(potential_college[:20], 1):
            print(f"\n{i}. {m['ticker']}")
            print(f"   {m['title'][:100]}")
            print(f"   (matched: {m['keyword']})")
    else:
        print("\n>>> NO COLLEGE FOOTBALL MARKETS FOUND <<<")
        print("\nThis means:")
        print("- Kalshi currently doesn't have active college football markets")
        print("- They may be closed/unavailable at this time")
        print("- College football betting may not be offered")

    # Check for closed markets
    print("\n" + "="*80)
    print("CHECKING CLOSED/SETTLED MARKETS")
    print("="*80)

    try:
        print("\nFetching settled markets...")
        settled = kalshi.get_markets(limit=100, status='settled')
        print(f"Retrieved {len(settled)} settled markets")

        # Look for college in settled
        college_settled = []
        for market in settled:
            title = market.get('title', '').lower()
            if any(kw in title for kw in ['cfb', 'ncaa', 'college']):
                college_settled.append(market)

        if college_settled:
            print(f"\nFound {len(college_settled)} settled college football markets:")
            for m in college_settled[:5]:
                print(f"  - {m.get('title', 'N/A')[:80]}")
        else:
            print("No settled college football markets found either")

    except Exception as e:
        print(f"Couldn't fetch settled markets: {e}")

if __name__ == "__main__":
    main()
