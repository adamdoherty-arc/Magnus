"""
Check what sports/categories Kalshi actually offers
"""
import os
import requests
from dotenv import load_dotenv

def main():
    load_dotenv()

    print("="*80)
    print("KALSHI AVAILABLE SPORTS/CATEGORIES")
    print("="*80)

    # Try to get event series (categories) from Kalshi
    base_url = "https://api.kalshi.com/trade-api/v2"

    try:
        # Get event series (sports categories)
        print("\nFetching event series from Kalshi API...")
        response = requests.get(f"{base_url}/series")

        if response.status_code == 200:
            data = response.json()
            series = data.get('series', [])

            print(f"Found {len(series)} event series/categories:\n")

            # Group by category
            categories = {}
            for s in series:
                category = s.get('category', 'Unknown')
                title = s.get('title', 'N/A')
                ticker = s.get('ticker', 'N/A')

                if category not in categories:
                    categories[category] = []
                categories[category].append({
                    'ticker': ticker,
                    'title': title
                })

            # Display by category
            for category, items in sorted(categories.items()):
                print(f"\n{category}:")
                for item in items[:10]:  # Show first 10
                    print(f"  - {item['ticker']}: {item['title']}")
                if len(items) > 10:
                    print(f"  ... and {len(items) - 10} more")

            # Look for sports
            sports_categories = [cat for cat in categories.keys()
                               if any(sport in cat.lower() for sport in
                                     ['sport', 'football', 'nfl', 'ncaa', 'soccer', 'basketball'])]

            print("\n" + "="*80)
            print("SPORTS-RELATED CATEGORIES")
            print("="*80)

            if sports_categories:
                for cat in sports_categories:
                    print(f"\n{cat}: {len(categories[cat])} series")
                    for item in categories[cat]:
                        print(f"  - {item['ticker']}: {item['title']}")
            else:
                print("No obvious sports categories found")

        else:
            print(f"API Error: {response.status_code}")
            print(f"Response: {response.text[:500]}")

    except Exception as e:
        print(f"Error: {e}")

    # Also check exchange schedule
    print("\n" + "="*80)
    print("CHECKING EXCHANGE SCHEDULE")
    print("="*80)

    try:
        response = requests.get(f"{base_url}/exchange/schedule")
        if response.status_code == 200:
            data = response.json()
            schedule = data.get('schedule', {})
            print("\nExchange Status:")
            print(f"  Status: {schedule.get('standard_hours', {}).get('status', 'N/A')}")
            maintenance = schedule.get('maintenance_windows', [])
            if maintenance:
                print(f"  Maintenance windows: {len(maintenance)}")
        else:
            print(f"Couldn't fetch schedule: {response.status_code}")
    except Exception as e:
        print(f"Error checking schedule: {e}")

if __name__ == "__main__":
    main()
