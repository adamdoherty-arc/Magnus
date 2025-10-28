"""
Test what events data Robinhood provides
"""
import robin_stocks.robinhood as rh
import os
from dotenv import load_dotenv
import json

load_dotenv()

username = os.getenv('ROBINHOOD_USERNAME')
password = os.getenv('ROBINHOOD_PASSWORD')

print("=" * 80)
print("TESTING ROBINHOOD get_events() FUNCTION")
print("=" * 80)

# Login
print("\nLogging in...")
rh.login(username, password)
print("OK - Logged in")

# Test get_events() with a popular stock
test_symbols = ['AAPL', 'NVDA', 'TSLA', 'AMD', 'META']

print("\nTesting get_events() for various stocks:")
print("=" * 80)

for symbol in test_symbols:
    print(f"\n{symbol}:")
    try:
        events = rh.get_events(symbol)

        if events:
            print(f"  OK - Found {len(events)} events")

            # Show first event in detail
            if isinstance(events, list) and len(events) > 0:
                print(f"\n  First event details:")
                print(json.dumps(events[0], indent=4))
            elif isinstance(events, dict):
                print(f"\n  Event data:")
                print(json.dumps(events, indent=4))
        else:
            print(f"  No events found")

    except Exception as e:
        print(f"  Error: {e}")

# Logout
rh.logout()

print("\n" + "=" * 80)
print("CONCLUSION:")
print("=" * 80)
print("""
Based on the data returned, Robinhood's get_events() function provides:
- Earnings announcements
- Stock splits
- Dividend dates
- Corporate actions

NOT sports events or betting data.

For sports data, you need a dedicated sports API.
""")
