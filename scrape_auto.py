"""
Automated Scraper - No Manual Input Required
Uses timed waits instead of input() prompts
"""

import sys
from pathlib import Path
import time
import re
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from xtrades_db_manager import XtradesDBManager
from dotenv import load_dotenv

load_dotenv()

def main():
    print("="*70)
    print("AUTOMATED SCRAPER - ALERTS PAGE")
    print("="*70)
    print("\nThis will:")
    print("1. Open Chrome browser")
    print("2. Wait 60 seconds for you to manually log in")
    print("3. Auto-navigate and scrape alerts")
    print("="*70)

    db = XtradesDBManager()

    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    # Initialize driver
    print("\n[STEP 1] Starting Chrome...")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # Navigate to xtrades
        print("\n[STEP 2] Opening xtrades.net/alerts...")
        driver.get("https://app.xtrades.net/alerts")

        print("\n[STEP 3] MANUAL LOGIN - 60 SECOND TIMER")
        print("="*70)
        print("Please log in with Discord in the browser window.")
        print("After logging in:")
        print("1. Click the 'Following' tab")
        print("2. Turn OFF the 'Open alerts only' toggle (if it's ON/blue)")
        print("3. Wait for all alerts to load")
        print("="*70)

        # Wait 60 seconds
        for i in range(60, 0, -10):
            print(f"[TIMER] {i} seconds remaining...")
            time.sleep(10)

        print("\n[STEP 4] Proceeding with scrape...")

        # Get current page HTML
        print("[INFO] Capturing page HTML...")
        time.sleep(2)
        page_source = driver.page_source

        # Save for debugging
        html_file = Path.home() / '.xtrades_cache' / 'auto_scrape.html'
        html_file.parent.mkdir(exist_ok=True)
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(page_source)
        print(f"[INFO] Saved HTML: {html_file}")

        # Parse
        soup = BeautifulSoup(page_source, 'html.parser')
        alert_rows = soup.find_all('app-alerts-table-row')
        print(f"\n[INFO] Found {len(alert_rows)} alert rows")

        if not alert_rows:
            print("[ERROR] No alerts found. Make sure you:")
            print("  1. Logged in successfully")
            print("  2. Clicked the 'Following' tab")
            print("  3. Turned OFF 'Open alerts only' toggle")
            print("  4. Let the page fully load")
            return 1

        # Parse each row
        print("\n[STEP 5] Parsing alerts...")
        parsed_alerts = []

        for i, row in enumerate(alert_rows, 1):
            full_text = row.get_text(strip=True)

            # Extract basic info
            alert_data = {
                'alert_text': full_text,
                'profile_username': None,
                'ticker': None,
                'action': None,
                'status': 'unknown',
                'pnl_percent': None,
                'alert_timestamp': datetime.now().isoformat()
            }

            # Extract username (@username)
            username_match = re.search(r'@(\w+)', full_text)
            if username_match:
                alert_data['profile_username'] = username_match.group(1)

            # Extract ticker and action
            for action in ['Bought', 'Sold', 'Shorted', 'Covered', 'Rolled']:
                if action in full_text:
                    alert_data['action'] = action
                    ticker_match = re.search(rf'{action}\s+([A-Z]{{1,5}})\s', full_text)
                    if ticker_match:
                        alert_data['ticker'] = ticker_match.group(1)
                    break

            # Extract status
            if 'Opened' in full_text:
                alert_data['status'] = 'open'
            elif 'Closed' in full_text:
                alert_data['status'] = 'closed'

            # Extract P/L
            pnl_patterns = [
                (r'Made\s+([\d.]+)%', 1),
                (r'Lost\s+([\d.]+)%', -1),
                (r'Up\s+([\d.]+)%', 1),
                (r'Down\s+([\d.]+)%', -1),
            ]
            for pattern, sign in pnl_patterns:
                match = re.search(pattern, full_text)
                if match:
                    alert_data['pnl_percent'] = sign * float(match.group(1))
                    break

            if alert_data['ticker']:
                parsed_alerts.append(alert_data)
                status = "OPEN" if alert_data['status'] == 'open' else "CLOSED"
                profile = alert_data.get('profile_username', 'unknown')
                pnl = alert_data.get('pnl_percent', 0)
                print(f"  [{i}] @{profile}: {alert_data['ticker']} - {status} - {pnl:+.1f}%")

        print(f"\n[SUCCESS] Parsed {len(parsed_alerts)} alerts")

        # Count
        open_count = sum(1 for a in parsed_alerts if a['status'] == 'open')
        closed_count = sum(1 for a in parsed_alerts if a['status'] == 'closed')
        print(f"  Open: {open_count}")
        print(f"  Closed: {closed_count}")

        # Store in database
        print(f"\n[STEP 6] Storing in database...")
        stored = 0

        for alert in parsed_alerts:
            try:
                profile_username = alert.get('profile_username', 'unknown')

                # Get or create profile
                profile = db.get_profile_by_username(profile_username)
                if not profile:
                    profile_id = db.add_profile(
                        username=profile_username,
                        display_name=f"@{profile_username}",
                        notes='From alerts feed'
                    )
                    profile = db.get_profile_by_username(profile_username)

                # Check duplicate
                alert_time = datetime.fromisoformat(alert['alert_timestamp'])
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
                    'ticker': alert['ticker'],
                    'strategy': 'Unknown',
                    'action': alert.get('action', 'Unknown'),
                    'alert_text': alert['alert_text'],
                    'alert_timestamp': alert_time,
                    'status': alert['status'],
                    'pnl_percent': alert.get('pnl_percent'),
                    'quantity': 1
                }

                trade_id = db.add_trade(trade_data)
                stored += 1
                status_label = "OPEN" if alert['status'] == 'open' else "CLOSED"
                print(f"  [OK] @{profile_username}: {alert['ticker']} {status_label} (ID: {trade_id})")

            except Exception as e:
                print(f"  [ERROR] {e}")

        print(f"\n[COMPLETE] Stored {stored}/{len(parsed_alerts)} new alerts")

        print("\n" + "="*70)
        print("SUCCESS - REFRESH DASHBOARD")
        print("="*70)
        print("\nDashboard: http://localhost:8501")
        print("Navigate to: Xtrades Watchlists")
        print("- Active Trades tab: Shows open alerts")
        print("- Closed Trades tab: Shows closed alerts")

        # Keep browser open for 10 seconds
        print("\n[INFO] Closing browser in 10 seconds...")
        time.sleep(10)

        return 0

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        driver.quit()

if __name__ == "__main__":
    sys.exit(main())
