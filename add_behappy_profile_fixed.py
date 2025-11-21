"""
Add BeHappy Profile to Xtrades Database
========================================
This script adds the 'behappy' profile to the database if it doesn't exist.
Run this before starting the sync service.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from xtrades_db_manager import XtradesDBManager
from dotenv import load_dotenv

load_dotenv()

def main():
    print("=" * 70)
    print("ADD BEHAPPY PROFILE TO XTRADES DATABASE")
    print("=" * 70)

    db_manager = XtradesDBManager()

    # Check if profile already exists
    existing = db_manager.get_profile_by_username('behappy')

    if existing:
        print(f"\n[OK] Profile 'behappy' already exists (ID: {existing['id']})")
        print(f"   Status: {'Active' if existing['active'] else 'Inactive'}")
        print(f"   Display Name: {existing['display_name'] or 'Not set'}")
        print(f"   Total Trades: {existing['total_trades_scraped']}")
        print(f"   Last Sync: {existing['last_sync'] or 'Never'}")

        # Ask if user wants to reactivate
        if not existing['active']:
            response = input("\nProfile is inactive. Reactivate? (y/n): ")
            if response.lower() == 'y':
                db_manager.reactivate_profile(existing['id'])
                print("[OK] Profile reactivated!")
    else:
        print("\n[WORKING] Adding 'behappy' profile to database...")

        try:
            profile_id = db_manager.add_profile(
                username='behappy',
                display_name='BeHappy Trader',
                notes='Example Xtrades.net profile for monitoring option trades'
            )

            print(f"\n[SUCCESS] Profile added with ID: {profile_id}")
            print("\nNext steps:")
            print("1. Run the sync service: python xtrades_sync_service.py")
            print("2. Or view in dashboard: streamlit run dashboard.py")
            print("3. Go to: Xtrades Watchlists -> Manage Profiles")

        except Exception as e:
            print(f"\n[ERROR] Failed to add profile")
            print(f"   {str(e)}")
            return 1

    print("\n" + "=" * 70)
    return 0

if __name__ == "__main__":
    sys.exit(main())
