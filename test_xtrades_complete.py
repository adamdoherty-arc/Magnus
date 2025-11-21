"""
Complete Xtrades Watchlist System Test
=======================================
Tests all components of the xtrades watchlist scraping system:
1. Discord OAuth login
2. Profile scraping (behappy)
3. Database integration
4. Alert parsing
5. Sync service
"""

import sys
import os
from pathlib import Path
import time
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from xtrades_scraper import XtradesScraper, LoginFailedException, ProfileNotFoundException
from xtrades_db_manager import XtradesDBManager
from dotenv import load_dotenv

load_dotenv()

def print_header(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def test_database_connection():
    """Test 1: Database Connection"""
    print_header("TEST 1: Database Connection")

    db = XtradesDBManager()

    try:
        conn = db.get_connection()
        print("[OK] Database connection successful")
        conn.close()
        return True
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")
        return False

def test_profile_management():
    """Test 2: Profile Management"""
    print_header("TEST 2: Profile Management")

    db = XtradesDBManager()

    # Check for behappy profile
    profile = db.get_profile_by_username('behappy')

    if profile:
        print(f"[OK] Found 'behappy' profile (ID: {profile['id']})")
        print(f"   Status: {'Active' if profile['active'] else 'Inactive'}")
        print(f"   Last Sync: {profile['last_sync'] or 'Never'}")
        return True, profile['id']
    else:
        print("[WARN] Profile 'behappy' not found")
        print("   Adding profile...")

        try:
            profile_id = db.add_profile(
                username='behappy',
                display_name='BeHappy Trader',
                notes='Test profile for xtrades scraping'
            )
            print(f"[OK] Profile added (ID: {profile_id})")
            return True, profile_id
        except Exception as e:
            print(f"[ERROR] Failed to add profile: {e}")
            return False, None

def test_discord_login():
    """Test 3: Discord OAuth Login"""
    print_header("TEST 3: Discord OAuth Login")

    print("Initializing Chrome driver...")
    scraper = XtradesScraper(headless=False)  # Non-headless so you can see what's happening

    try:
        print("Attempting Discord OAuth login...")
        print("[WAIT] This may take 20-30 seconds...")

        success = scraper.login()

        if success:
            print("[OK] Login successful!")
            print("   Session cookies saved for future use")
            return True, scraper
        else:
            print("[ERROR] Login failed")
            scraper.close()
            return False, None

    except LoginFailedException as e:
        print(f"[ERROR] Login exception: {e}")
        scraper.close()
        return False, None
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        scraper.close()
        return False, None

def test_profile_scraping(scraper):
    """Test 4: Profile Scraping"""
    print_header("TEST 4: Profile Scraping - 'behappy'")

    try:
        print("Navigating to behappy profile...")
        print("Scraping alerts (max 10 for test)...")

        alerts = scraper.get_profile_alerts('behappy', max_alerts=10)

        if alerts:
            print(f"[OK] Successfully scraped {len(alerts)} alerts\n")

            # Display first few alerts
            for i, alert in enumerate(alerts[:3], 1):
                print(f"Alert {i}:")
                print(f"  Ticker: {alert.get('ticker', 'N/A')}")
                print(f"  Strategy: {alert.get('strategy', 'N/A')}")
                print(f"  Action: {alert.get('action', 'N/A')}")
                print(f"  Entry Price: ${alert.get('entry_price', 0):.2f}" if alert.get('entry_price') else "  Entry Price: N/A")
                print(f"  Status: {alert.get('status', 'N/A')}")
                print(f"  Alert Text: {alert.get('alert_text', '')[:80]}...")
                print()

            return True, alerts
        else:
            print("[WARN] No alerts found")
            print("   This could mean:")
            print("   - Profile is empty")
            print("   - Scraper selectors need updating")
            print("   - Profile access issue")
            return False, []

    except ProfileNotFoundException as e:
        print(f"[ERROR] Profile not found: {e}")
        return False, []
    except Exception as e:
        print(f"[ERROR] Scraping error: {e}")
        import traceback
        traceback.print_exc()
        return False, []

def test_database_storage(alerts):
    """Test 5: Database Storage"""
    print_header("TEST 5: Database Storage")

    db = XtradesDBManager()

    # Get behappy profile
    profile = db.get_profile_by_username('behappy')
    if not profile:
        print("[ERROR] Profile not found in database")
        return False

    print(f"Storing {len(alerts)} alerts in database...")

    stored_count = 0
    duplicate_count = 0

    for alert in alerts:
        try:
            # Check for duplicate
            alert_time = alert.get('alert_timestamp')
            if isinstance(alert_time, str):
                alert_time = datetime.fromisoformat(alert_time)

            existing = db.find_existing_trade(
                profile['id'],
                alert['ticker'],
                alert_time
            )

            if existing:
                duplicate_count += 1
                continue

            # Add trade
            trade_data = {
                'profile_id': profile['id'],
                'ticker': alert.get('ticker'),
                'strategy': alert.get('strategy'),
                'action': alert.get('action'),
                'entry_price': alert.get('entry_price'),
                'quantity': alert.get('quantity', 1),
                'strike_price': alert.get('strike_price'),
                'expiration_date': alert.get('expiration_date'),
                'alert_text': alert.get('alert_text'),
                'alert_timestamp': alert_time,
                'status': alert.get('status', 'open')
            }

            trade_id = db.add_trade(trade_data)
            stored_count += 1
            print(f"  [OK] Stored: {alert['ticker']} - {alert.get('strategy', 'N/A')} (ID: {trade_id})")

        except Exception as e:
            print(f"  [ERROR] Failed to store alert: {e}")

    print(f"\n[STATS] Summary:")
    print(f"   Stored: {stored_count}")
    print(f"   Duplicates: {duplicate_count}")
    print(f"   Total: {len(alerts)}")

    # Update profile sync status
    db.update_profile_sync_status(profile['id'], 'success', stored_count)

    return stored_count > 0

def test_data_retrieval():
    """Test 6: Data Retrieval"""
    print_header("TEST 6: Data Retrieval")

    db = XtradesDBManager()

    # Get all trades for behappy
    profile = db.get_profile_by_username('behappy')
    if not profile:
        print("[ERROR] Profile not found")
        return False

    trades = db.get_trades_by_profile(profile['id'], limit=10)

    if trades:
        print(f"[OK] Retrieved {len(trades)} trades from database")
        print(f"\nRecent trades:")

        for i, trade in enumerate(trades[:3], 1):
            print(f"\n  Trade {i}:")
            print(f"    Ticker: {trade.get('ticker')}")
            print(f"    Strategy: {trade.get('strategy')}")
            print(f"    Entry: ${trade.get('entry_price', 0):.2f}" if trade.get('entry_price') else "    Entry: N/A")
            print(f"    Status: {trade.get('status')}")
            print(f"    Alert Time: {trade.get('alert_timestamp')}")

        # Get statistics
        stats = db.get_profile_stats(profile['id'])
        print(f"\n[STATS] Profile Statistics:")
        print(f"   Total Trades: {stats['total_trades']}")
        print(f"   Open Trades: {stats['open_trades']}")
        print(f"   Closed Trades: {stats['closed_trades']}")

        return True
    else:
        print("[WARN] No trades found in database")
        return False

def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("  XTRADES COMPLETE SYSTEM TEST")
    print("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 70)

    results = {}

    # Test 1: Database
    results['database'] = test_database_connection()
    if not results['database']:
        print("\n[ERROR] Cannot continue without database connection")
        return 1

    # Test 2: Profile Management
    results['profile'], profile_id = test_profile_management()
    if not results['profile']:
        print("\n[ERROR] Cannot continue without profile setup")
        return 1

    # Test 3: Discord Login
    results['login'], scraper = test_discord_login()
    if not results['login']:
        print("\n[ERROR] Cannot continue without successful login")
        print("\n[TIP] Troubleshooting:")
        print("   1. Check XTRADES_USERNAME and XTRADES_PASSWORD in .env")
        print("   2. Verify Discord credentials are correct")
        print("   3. Try running with headless=False to see what's happening")
        return 1

    try:
        # Test 4: Profile Scraping
        results['scraping'], alerts = test_profile_scraping(scraper)

        if results['scraping'] and alerts:
            # Test 5: Database Storage
            results['storage'] = test_database_storage(alerts)

            # Test 6: Data Retrieval
            results['retrieval'] = test_data_retrieval()
        else:
            results['storage'] = False
            results['retrieval'] = False

    finally:
        # Always close the scraper
        if scraper:
            scraper.close()
            print("\n[INFO] Browser closed")

    # Final Summary
    print_header("TEST SUMMARY")

    all_passed = all(results.values())

    for test_name, passed in results.items():
        status = "[OK] PASS" if passed else "[ERROR] FAIL"
        print(f"{status} - {test_name.upper()}")

    print("\n" + "=" * 70)

    if all_passed:
        print("[SUCCESS] ALL TESTS PASSED!")
        print("\nNext steps:")
        print("1. View data in dashboard: streamlit run dashboard.py")
        print("2. Go to: Xtrades Watchlists page")
        print("3. Set up automatic sync: see XTRADES_SETUP_GUIDE.md")
        return 0
    else:
        print("[WARN] SOME TESTS FAILED")
        print("\nCheck the errors above and:")
        print("1. Verify .env configuration")
        print("2. Check database is running")
        print("3. Verify Discord credentials")
        return 1

if __name__ == "__main__":
    sys.exit(main())
