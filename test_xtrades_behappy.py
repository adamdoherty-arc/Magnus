"""Test Xtrades Scraper with 'behappy' Profile"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from xtrades_scraper import XtradesScraper, LoginFailedException, ProfileNotFoundException

def test_behappy_profile():
    """Test scraping the 'behappy' profile alerts"""

    print("=" * 80)
    print("XTRADES SCRAPER TEST - 'behappy' Profile")
    print("=" * 80)

    scraper = None
    try:
        # Initialize scraper
        print("\n1. Initializing scraper (headless=False for visibility)...")
        scraper = XtradesScraper(headless=False)

        # Login
        print("\n2. Logging in to Xtrades.net...")
        print("   (You may need to approve Discord OAuth in browser)")
        scraper.login()

        # Get alerts from 'behappy' profile
        print("\n3. Fetching alerts from 'behappy' profile...")
        alerts = scraper.get_profile_alerts("behappy", max_alerts=20)

        # Display results
        print(f"\n4. RESULTS:")
        print("=" * 80)
        print(f"   Total alerts found: {len(alerts)}")

        if alerts:
            print("\n   First 5 Alerts:")
            print("   " + "-" * 76)

            for i, alert in enumerate(alerts[:5], 1):
                print(f"\n   Alert #{i}:")
                print(f"      Ticker: {alert.get('ticker', 'N/A')}")
                print(f"      Strategy: {alert.get('strategy', 'N/A')}")
                print(f"      Action: {alert.get('action', 'N/A')}")
                print(f"      Strike: {alert.get('strike', 'N/A')}")
                print(f"      Expiration: {alert.get('expiration', 'N/A')}")
                print(f"      Premium: {alert.get('premium', 'N/A')}")
                print(f"      Quantity: {alert.get('quantity', 'N/A')}")
                print(f"      Timestamp: {alert.get('alert_timestamp', 'N/A')}")

                # Show raw text snippet
                raw_text = alert.get('raw_text', '')
                if raw_text:
                    snippet = raw_text[:100] + "..." if len(raw_text) > 100 else raw_text
                    print(f"      Raw: {snippet}")
        else:
            print("\n   [!] No alerts found!")
            print("   This could mean:")
            print("      - Profile has no public alerts")
            print("      - HTML selectors need updating")
            print("      - Page structure changed")

        print("\n" + "=" * 80)
        print("TEST COMPLETE")
        print("=" * 80)

        return alerts

    except LoginFailedException as e:
        print(f"\n[ERROR] LOGIN FAILED: {e}")
        print("\nTroubleshooting:")
        print("1. Check your Discord account is linked to Xtrades.net")
        print("2. Ensure you approve the OAuth request in the browser")
        print("3. Check if Xtrades.net is accessible")
        return None

    except ProfileNotFoundException as e:
        print(f"\n[ERROR] PROFILE NOT FOUND: {e}")
        print("\nThe 'behappy' profile may not exist or may not be public")
        return None

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return None

    finally:
        if scraper:
            print("\n5. Closing browser...")
            scraper.close()

if __name__ == "__main__":
    alerts = test_behappy_profile()

    if alerts:
        print(f"\n[OK] SUCCESS: Retrieved {len(alerts)} alerts from 'behappy' profile")
    else:
        print("\n[!] No alerts retrieved - see messages above")
