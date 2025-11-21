"""
Sync Xtrades Alerts NOW
========================
Pull fresh alerts from all active profiles
"""

import os
import sys
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

from dotenv import load_dotenv
load_dotenv()

from src.xtrades_scraper import XtradesScraper
from src.xtrades_db_manager import XtradesDBManager

def sync_all_profiles():
    """Sync alerts from all active profiles"""
    db = XtradesDBManager()
    scraper = XtradesScraper()

    print("\n" + "="*80)
    print("🔄 SYNCING XTRADES ALERTS - " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("="*80)

    # Get active profiles
    profiles = db.get_active_profiles()
    print(f"\n📋 Found {len(profiles)} active profiles")

    if not profiles:
        print("❌ No active profiles! Add profiles to xtrades_profiles table")
        return

    total_new_alerts = 0

    for profile in profiles:
        profile_id = profile['id']
        username = profile['username']
        display_name = profile['display_name'] or username

        print(f"\n🔍 Syncing: {display_name} (@{username})")

        try:
            # Log sync start
            db.log_sync_start(profile_id)

            # Get profile alerts from website
            alerts = scraper.get_profile_alerts(username)

            if not alerts:
                print(f"   ℹ️  No alerts found")
                db.log_sync_complete(profile_id, 0, 0)
                continue

            print(f"   📥 Retrieved {len(alerts)} alerts from website")

            # Process each alert
            new_count = 0
            for alert_data in alerts:
                # Check if trade already exists
                existing = db.find_existing_trade(
                    profile_id,
                    alert_data.get('ticker', ''),
                    alert_data.get('strategy', ''),
                    alert_data.get('strike_price'),
                    alert_data.get('expiration_date')
                )

                if not existing:
                    # Add new trade
                    db.add_trade(profile_id, alert_data)
                    new_count += 1

            total_new_alerts += new_count

            # Log sync complete
            db.log_sync_complete(profile_id, len(alerts), new_count)

            print(f"   ✅ Added {new_count} new alerts")

        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()

    scraper.close()

    print("\n" + "="*80)
    print(f"✅ SYNC COMPLETE: {total_new_alerts} new alerts added")
    print("="*80 + "\n")

    return total_new_alerts

if __name__ == "__main__":
    sync_all_profiles()
