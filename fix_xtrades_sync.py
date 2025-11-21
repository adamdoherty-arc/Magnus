"""
Fix Xtrades Sync - Pull Fresh Alerts
====================================
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

def check_profiles():
    """Check active Xtrades profiles"""
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, username, display_name, active, last_sync
        FROM xtrades_profiles
        ORDER BY id
    """)
    profiles = cursor.fetchall()

    print("\n" + "="*80)
    print("XTRADES PROFILES:")
    print("="*80)
    for p in profiles:
        status = "✅ ACTIVE" if p[3] else "❌ INACTIVE"
        print(f"{status} | ID: {p[0]} | User: {p[1]} | Display: {p[2]} | Last Sync: {p[4]}")

    cursor.close()
    conn.close()
    return profiles

def check_alerts():
    """Check alert counts"""
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM xtrades_trades")
    total = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*) FROM xtrades_trades
        WHERE alert_timestamp > NOW() - INTERVAL '24 hours'
    """)
    recent = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*) FROM xtrades_trades
        WHERE alert_timestamp > NOW() - INTERVAL '7 days'
    """)
    week = cursor.fetchone()[0]

    print("\n" + "="*80)
    print("ALERT COUNTS:")
    print("="*80)
    print(f"Total alerts: {total}")
    print(f"Last 24 hours: {recent}")
    print(f"Last 7 days: {week}")

    cursor.close()
    conn.close()

def run_scraper():
    """Run the Xtrades scraper to pull fresh alerts"""
    print("\n" + "="*80)
    print("RUNNING XTRADES SCRAPER:")
    print("="*80)

    try:
        from src.xtrades_scraper import XtradesScraper

        scraper = XtradesScraper()

        # Get active profiles
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, username
            FROM xtrades_profiles
            WHERE active = TRUE
        """)
        profiles = cursor.fetchall()
        cursor.close()
        conn.close()

        print(f"\nFound {len(profiles)} active profiles to scrape")

        for profile_id, username in profiles:
            print(f"\n🔍 Scraping alerts for: {username} (ID: {profile_id})")
            try:
                trades = scraper.scrape_profile_trades(username)
                print(f"   ✅ Found {len(trades)} trades")

                # Save to database
                scraper.save_trades_to_db(profile_id, trades)
                print(f"   💾 Saved to database")

            except Exception as e:
                print(f"   ❌ Error: {e}")

        print("\n✅ Scraping complete!")

    except Exception as e:
        print(f"❌ Scraper error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("\n" + "="*80)
    print("🤖 AVA - XTRADES SYNC FIX")
    print("="*80)

    # Step 1: Check profiles
    profiles = check_profiles()

    # Step 2: Check current alerts
    check_alerts()

    # Step 3: Run scraper
    if profiles:
        run_scraper()

        # Step 4: Check alerts again
        print("\n" + "="*80)
        print("AFTER SCRAPING:")
        check_alerts()
    else:
        print("\n❌ No profiles found! Need to add profiles to xtrades_profiles table")
