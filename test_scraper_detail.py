"""
Test Xtrades Scraper - Detailed Diagnostic
===========================================
Check what alert elements are actually being found and why parsing is failing
"""

import os
import sys
from dotenv import load_dotenv

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

from src.xtrades_scraper import XtradesScraper

def test_single_profile():
    """Test scraping a single profile with detailed output"""
    scraper = XtradesScraper(headless=False)  # Non-headless to see what's happening

    try:
        username = "behappy"
        print(f"\n{'='*80}")
        print(f"Testing: {username}")
        print(f"{'='*80}\n")

        # Get alerts
        alerts = scraper.get_profile_alerts(username, max_alerts=10)

        print(f"\n{'='*80}")
        print(f"RESULTS: Got {len(alerts)} parsed alerts")
        print(f"{'='*80}\n")

        for i, alert in enumerate(alerts, 1):
            print(f"\nAlert {i}:")
            print(f"  Ticker: {alert.get('ticker')}")
            print(f"  Strategy: {alert.get('strategy')}")
            print(f"  Action: {alert.get('action')}")
            print(f"  Entry Price: ${alert.get('entry_price')}")
            print(f"  Strike: ${alert.get('strike_price')}")
            print(f"  Text: {alert.get('alert_text')[:100]}...")
            print(f"  Timestamp: {alert.get('alert_timestamp')}")

        # Also print any alert text from the raw elements
        print(f"\n{'='*80}")
        print("If you see this, check the browser window for actual alerts")
        print(f"{'='*80}")

        input("\nPress Enter to close browser and continue...")

    finally:
        scraper.close()

if __name__ == "__main__":
    test_single_profile()
