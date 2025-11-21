"""
Find Active Xtrades Profiles with Real Alerts
"""

import sys
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from xtrades_scraper import XtradesScraper
from xtrades_db_manager import XtradesDBManager
from dotenv import load_dotenv

load_dotenv()

# List of potential active profiles based on research
PROFILES_TO_TEST = [
    'alex',
    'chrisg',
    'krazya',
    'hydra',
    'momentum',
    'kevin',
    'kevinwan',
    'elitetrader',
    'stockmillionaire',
    'optionsflow'
]

def test_profile(scraper, username):
    """Test if a profile exists and has alerts"""
    try:
        print(f"\n{'='*70}")
        print(f"Testing profile: {username}")
        print(f"{'='*70}")

        profile_url = f"https://app.xtrades.net/profile/{username}"
        print(f"URL: {profile_url}")

        scraper.driver.get(profile_url)
        time.sleep(3)

        # Check if profile exists
        title = scraper.driver.title
        print(f"Page title: {title}")

        if "404" in title or "not found" in title.lower():
            print(f"[SKIP] Profile '{username}' not found (404)")
            return None

        # Try to get alerts
        alerts = scraper.get_profile_alerts(username, max_alerts=5)

        if alerts:
            print(f"[SUCCESS] Found {len(alerts)} alerts!")
            print("\nFirst alert:")
            alert = alerts[0]
            print(f"  Ticker: {alert.get('ticker')}")
            print(f"  Strategy: {alert.get('strategy')}")
            print(f"  Action: {alert.get('action')}")
            print(f"  Entry: ${alert.get('entry_price', 0):.2f}" if alert.get('entry_price') else "  Entry: N/A")

            return {
                'username': username,
                'alert_count': len(alerts),
                'sample_alert': alert
            }
        else:
            print(f"[EMPTY] Profile exists but has no alerts")
            return None

    except Exception as e:
        print(f"[ERROR] Failed to test profile '{username}': {e}")
        return None

def main():
    print("="*70)
    print("FINDING ACTIVE XTRADES PROFILES")
    print("="*70)

    scraper = XtradesScraper(headless=True)
    db = XtradesDBManager()

    try:
        # Login
        print("\n[1] Logging in to Xtrades...")
        if not scraper.login():
            print("[ERROR] Login failed")
            return 1

        print("[OK] Login successful")

        # Test each profile
        active_profiles = []

        for username in PROFILES_TO_TEST:
            result = test_profile(scraper, username)
            if result:
                active_profiles.append(result)
            time.sleep(2)  # Be nice to the server

        # Summary
        print("\n" + "="*70)
        print("SUMMARY - ACTIVE PROFILES FOUND")
        print("="*70)

        if not active_profiles:
            print("\n[WARN] No active profiles found with alerts")
            print("\nTry these steps:")
            print("1. Visit https://app.xtrades.net manually")
            print("2. Browse the 'Traders' or 'Leaderboard' section")
            print("3. Find profiles with recent alert activity")
            print("4. Note their usernames")
            print("5. Add them using: python add_active_profile.py USERNAME")
            return 0

        print(f"\nFound {len(active_profiles)} profiles with alerts:\n")

        for profile in active_profiles:
            print(f"  - {profile['username']}: {profile['alert_count']} alerts")

        # Ask to add them
        print("\n" + "="*70)
        response = input("\nAdd these profiles to database? (y/n): ")

        if response.lower() == 'y':
            print("\nAdding profiles...")
            for profile in active_profiles:
                try:
                    # Check if already exists
                    existing = db.get_profile_by_username(profile['username'])
                    if existing:
                        print(f"  [SKIP] {profile['username']} already exists")
                        continue

                    profile_id = db.add_profile(
                        username=profile['username'],
                        display_name=profile['username'].title(),
                        notes=f"Active trader with {profile['alert_count']} alerts found"
                    )
                    print(f"  [OK] Added {profile['username']} (ID: {profile_id})")
                except Exception as e:
                    print(f"  [ERROR] Failed to add {profile['username']}: {e}")

            print("\n[SUCCESS] Profiles added!")
            print("\nNext steps:")
            print("1. Run sync: python src/xtrades_sync_service.py")
            print("2. View dashboard: http://localhost:8501")
            print("3. Go to: Xtrades Watchlists page")
        else:
            print("\n[INFO] Profiles not added. You can add them later.")

        return 0

    except Exception as e:
        print(f"\n[ERROR] Script failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        scraper.close()

if __name__ == "__main__":
    sys.exit(main())
