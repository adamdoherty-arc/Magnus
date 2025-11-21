"""
Scrape Real Alerts from BeHappy Profile - No Dummy Data
This will actually scrape and store REAL alerts from the behappy profile
"""

import sys
from pathlib import Path
import time
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from xtrades_scraper import XtradesScraper
from xtrades_db_manager import XtradesDBManager
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

def main():
    print("="*70)
    print("SCRAPING REAL ALERTS FROM BEHAPPY PROFILE")
    print("="*70)

    scraper = XtradesScraper(headless=False)
    db = XtradesDBManager()

    try:
        # Step 1: Login
        print("\n[STEP 1] Logging in...")
        if not scraper.login():
            print("[ERROR] Login failed")
            return 1
        print("[OK] Logged in successfully")

        # Step 2: Navigate to behappy profile
        print("\n[STEP 2] Navigating to https://app.xtrades.net/profile/behappy")
        scraper.driver.get("https://app.xtrades.net/profile/behappy")
        time.sleep(5)

        # Step 3: Wait extra long for Angular to load
        print("\n[STEP 3] Waiting for page to fully load (30 seconds)...")
        time.sleep(30)

        # Scroll to load lazy content
        print("\n[STEP 4] Scrolling to load all content...")
        for i in range(5):
            scraper.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            print(f"  Scrolled {i+1}/5")

        # Wait a bit more
        time.sleep(5)

        # Step 5: Get page source and analyze
        print("\n[STEP 5] Analyzing page HTML...")
        page_source = scraper.driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        # Save for debugging
        debug_file = Path.home() / '.xtrades_cache' / 'behappy_real_scrape.html'
        debug_file.parent.mkdir(exist_ok=True)
        with open(debug_file, 'w', encoding='utf-8') as f:
            f.write(page_source)
        print(f"[INFO] Saved HTML to: {debug_file}")

        # Step 6: Look for ANY content that looks like alerts
        print("\n[STEP 6] Searching for alert content...")

        # Strategy 1: Look for specific text patterns
        all_text = soup.get_text()

        # Check for trade keywords
        trade_keywords = ['BTO', 'STO', 'BTC', 'STC', 'CALL', 'PUT', 'CSP']
        found = [kw for kw in trade_keywords if kw in all_text]

        if found:
            print(f"[OK] Found trading keywords: {', '.join(found)}")
            print("[INFO] Page appears to have trading content")
        else:
            print("[WARN] No obvious trading keywords found")
            print("[INFO] The profile might truly be empty")

        # Strategy 2: Try the actual scraper method
        print("\n[STEP 7] Running scraper's get_profile_alerts method...")
        alerts = scraper.get_profile_alerts('behappy', max_alerts=50)

        if alerts and len(alerts) > 0:
            print(f"\n[SUCCESS] Found {len(alerts)} real alerts!")

            # Show first few
            for i, alert in enumerate(alerts[:5], 1):
                print(f"\nAlert {i}:")
                print(f"  Ticker: {alert.get('ticker', 'N/A')}")
                print(f"  Strategy: {alert.get('strategy', 'N/A')}")
                print(f"  Action: {alert.get('action', 'N/A')}")
                print(f"  Entry: ${alert.get('entry_price', 0):.2f}" if alert.get('entry_price') else "  Entry: N/A")
                print(f"  Text: {alert.get('alert_text', '')[:80]}...")

            # Step 8: Store in database
            print(f"\n[STEP 8] Storing {len(alerts)} alerts in database...")

            profile = db.get_profile_by_username('behappy')
            if not profile:
                print("[ERROR] behappy profile not found in database")
                return 1

            stored = 0
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
                        continue

                    # Store
                    trade_data = {
                        'profile_id': profile['id'],
                        'ticker': alert.get('ticker'),
                        'strategy': alert.get('strategy'),
                        'action': alert.get('action'),
                        'entry_price': alert.get('entry_price'),
                        'exit_price': alert.get('exit_price'),
                        'quantity': alert.get('quantity', 1),
                        'strike_price': alert.get('strike_price'),
                        'expiration_date': alert.get('expiration_date'),
                        'alert_text': alert.get('alert_text'),
                        'alert_timestamp': alert_time,
                        'status': alert.get('status', 'open'),
                        'pnl': alert.get('pnl'),
                        'pnl_percent': alert.get('pnl_percent')
                    }

                    trade_id = db.add_trade(trade_data)
                    stored += 1
                    print(f"  [OK] Stored: {alert['ticker']} (ID: {trade_id})")

                except Exception as e:
                    print(f"  [ERROR] Failed to store alert: {e}")

            print(f"\n[SUCCESS] Stored {stored}/{len(alerts)} real alerts")

            # Update profile sync status
            db.update_profile_sync_status(profile['id'], 'success', stored)

            print("\n[COMPLETE] Real alerts from behappy profile are now in database!")
            print("\nNext steps:")
            print("1. Open dashboard: http://localhost:8501")
            print("2. Go to: Xtrades Watchlists")
            print("3. Select 'behappy' from profile dropdown")
            print("4. View the REAL alerts!")

            return 0

        else:
            print("\n[WARN] No alerts found")
            print("\nPossible reasons:")
            print("1. The behappy profile genuinely has no alerts posted")
            print("2. Alerts are behind authentication/privacy settings")
            print("3. The page structure has changed and scraper needs updating")

            print("\nLet's check what's actually on the page...")

            # Look for "empty" indicators
            if any(msg in all_text.lower() for msg in ['no alerts', 'no data', 'empty']):
                print("[INFO] Page shows 'no alerts' or 'empty' message")
                print("[CONCLUSION] The behappy profile appears to be genuinely empty")
            else:
                print("[INFO] No 'empty' message found")
                print("[ACTION NEEDED] The page HTML needs manual inspection")
                print(f"[FILE] Check: {debug_file}")

            return 1

    except Exception as e:
        print(f"\n[ERROR] Scraping failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        print("\n[INFO] Closing browser...")
        scraper.close()

if __name__ == "__main__":
    sys.exit(main())
