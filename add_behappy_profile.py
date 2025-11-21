"""Add 'behappy' profile and test sync"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from xtrades_db_manager import XtradesDBManager
from xtrades_scraper import XtradesScraper
from datetime import datetime

print("=" * 80)
print("ADD 'BEHAPPY' PROFILE AND TEST SYNC")
print("=" * 80)

# Initialize DB manager
db_manager = XtradesDBManager()

# Step 1: Add profile
print("\n1. Adding 'behappy' profile to database...")
try:
    profile_id = db_manager.add_profile(
        username='behappy',
        display_name='BeHappy Trader'
    )
    print(f"   [OK] Profile added with ID: {profile_id}")
except Exception as e:
    print(f"   [INFO] Profile may already exist: {e}")
    # Get existing profile
    profiles = db_manager.get_all_profiles()
    behappy = next((p for p in profiles if p['username'] == 'behappy'), None)
    if behappy:
        profile_id = behappy['id']
        print(f"   [OK] Using existing profile ID: {profile_id}")
    else:
        print(f"   [ERROR] Could not find or create profile")
        sys.exit(1)

# Step 2: Sync profile
print("\n2. Syncing 'behappy' profile...")
try:
    scraper = XtradesScraper(headless=True)
    print("   - Logging in...")
    scraper.login()

    print("   - Fetching alerts...")
    alerts = scraper.get_profile_alerts('behappy', max_alerts=50)

    print(f"   - Found {len(alerts)} alerts")

    # Store alerts
    new_count = 0
    for alert in alerts:
        # Check if already exists
        existing = db_manager.find_existing_trade(
            profile_id,
            alert['ticker'],
            datetime.fromisoformat(alert['alert_timestamp'])
        )

        if not existing:
            alert['profile_id'] = profile_id
            db_manager.add_trade(alert)
            new_count += 1

    scraper.close()

    # Update profile sync status
    db_manager.update_profile_sync_status(profile_id, 'success', new_count)

    print(f"   [OK] Sync complete: {len(alerts)} alerts found, {new_count} new trades added")

except Exception as e:
    print(f"   [ERROR] Sync failed: {e}")
    import traceback
    traceback.print_exc()
    db_manager.update_profile_sync_status(profile_id, 'error')

# Step 3: Check database
print("\n3. Checking database...")
profile = db_manager.get_profile_by_id(profile_id)
print(f"   Profile: {profile['username']}")
print(f"   Last Sync: {profile['last_sync']}")
print(f"   Sync Status: {profile['last_sync_status']}")
print(f"   Total Trades: {profile['total_trades_scraped']}")

trades = db_manager.get_trades_by_profile(profile_id, limit=10)
print(f"\n   Total trades in database: {len(trades)}")

if trades:
    print("\n   First 5 trades:")
    for i, trade in enumerate(trades[:5], 1):
        print(f"   {i}. {trade['ticker']} {trade.get('strategy', 'N/A')} - {trade.get('alert_timestamp', 'N/A')}")

print("\n" + "=" * 80)
print("COMPLETE")
print("=" * 80)
