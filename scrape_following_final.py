"""
Final Working Scraper - Following Alerts with Open/Close Tracking
Scrapes https://app.xtrades.net/alerts → Following tab
Tracks when traders you follow open and close positions
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
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).parent / 'src'))
from xtrades_db_manager import XtradesDBManager
from dotenv import load_dotenv

load_dotenv()

def parse_alert_row(row):
    """Parse complete alert with full trade details"""
    try:
        # FIXED: Use separator=' ' to add spaces between HTML elements!
        full_text = row.get_text(separator=' ', strip=True)

        result = {
            'ticker': None,
            'profile_username': None,
            'action': None,
            'option_type': None,
            'strike_price': None,
            'expiration_date': None,
            'entry_price': None,
            'status': 'unknown',
            'pnl_percent': None,
            'alert_timestamp': None,
            'alert_text': full_text,
        }

        # Extract username (@username)
        username_match = re.search(r'@(\w+)', full_text)
        if username_match:
            result['profile_username'] = username_match.group(1)

        # Extract action and ticker
        actions = ['Bought', 'Sold', 'Shorted', 'Covered', 'Rolled']
        for action in actions:
            if action in full_text:
                result['action'] = action
                # Extract ticker after action
                ticker_match = re.search(rf'{action}\s+([A-Z]{{1,5}})\s', full_text)
                if ticker_match:
                    result['ticker'] = ticker_match.group(1)
                break

        # Extract expiration date (MM/DD)
        exp_match = re.search(r'(\d{1,2}/\d{1,2})', full_text)
        if exp_match:
            exp_str = exp_match.group(1)
            month, day = exp_str.split('/')
            year = datetime.now().year
            try:
                exp_date = datetime(year, int(month), int(day))
                if exp_date < datetime.now():
                    exp_date = datetime(year + 1, int(month), int(day))
                result['expiration_date'] = exp_date.date().isoformat()
            except:
                pass

        # Extract strike price and option type
        strike_match = re.search(r'\$(\d+)\s+(Calls?|Puts?)', full_text)
        if strike_match:
            result['strike_price'] = float(strike_match.group(1))
            result['option_type'] = 'Call' if 'Call' in strike_match.group(2) else 'Put'

        # Extract entry price (@ $X.XX)
        entry_match = re.search(r'@\s*\$(\d+\.?\d*)', full_text)
        if entry_match:
            result['entry_price'] = float(entry_match.group(1))

        # Extract status and time (OPENED or CLOSED)
        if 'Opened' in full_text:
            result['status'] = 'open'
            time_match = re.search(r'Opened\s+(\d+)([hd])\s+ago', full_text)
            if time_match:
                value = int(time_match.group(1))
                unit = time_match.group(2)
                if unit == 'h':
                    result['alert_timestamp'] = (datetime.now() - timedelta(hours=value)).isoformat()
                elif unit == 'd':
                    result['alert_timestamp'] = (datetime.now() - timedelta(days=value)).isoformat()
        elif 'Closed' in full_text:
            result['status'] = 'closed'
            time_match = re.search(r'Closed\s+(\d+)([hd])\s+ago', full_text)
            if time_match:
                value = int(time_match.group(1))
                unit = time_match.group(2)
                if unit == 'h':
                    result['alert_timestamp'] = (datetime.now() - timedelta(hours=value)).isoformat()
                elif unit == 'd':
                    result['alert_timestamp'] = (datetime.now() - timedelta(days=value)).isoformat()

        if not result['alert_timestamp']:
            result['alert_timestamp'] = datetime.now().isoformat()

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
                result['pnl_percent'] = sign * float(match.group(1))
                break

        # Build strategy string
        if result['option_type']:
            result['strategy'] = result['option_type']
            if result['action'] == 'Shorted':
                result['strategy'] = f"Short {result['option_type']}"
            elif result['action'] == 'Bought':
                result['strategy'] = f"Long {result['option_type']}"

        if result['ticker']:
            return result
        return None

    except Exception as e:
        print(f"[ERROR] Parse failed: {e}")
        return None

def main():
    print("="*70)
    print("FOLLOWING ALERTS SCRAPER - WITH OPEN/CLOSE TRACKING")
    print("="*70)
    print("\nThis scrapes: https://app.xtrades.net/alerts")
    print("From the 'Following' tab")
    print("Tracks when positions are opened AND closed")
    print("="*70)

    db = XtradesDBManager()

    # Setup Chrome with explicit binary path
    chrome_options = Options()
    chrome_options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    print("\n[STEP 1] Starting Chrome (not Edge)...")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    wait = WebDriverWait(driver, 10)

    try:
        # Navigate to alerts page
        print("\n[STEP 2] Opening https://app.xtrades.net/alerts...")
        driver.get("https://app.xtrades.net/alerts")
        time.sleep(3)

        # Check if logged in
        if 'Sign in' in driver.page_source:
            print("\n[STEP 3] MANUAL LOGIN - 3 MINUTE TIMER")
            print("="*70)
            print("PLEASE DO THESE STEPS IN THE CHROME WINDOW:")
            print("")
            print("1. Log in with Discord")
            print("2. Click the 'Following' tab at the top")
            print("3. Turn OFF the blue 'Open alerts only' toggle")
            print("4. Wait for alerts to load (you should see trader names)")
            print("")
            print("DO NOT CLOSE THE BROWSER - Script will auto-continue")
            print("="*70)

            # Wait 3 minutes for manual setup
            for i in range(180, 0, -30):
                print(f"[TIMER] {i} seconds remaining for manual setup...")
                time.sleep(30)

                # Check if logged in
                if 'Sign in' not in driver.page_source:
                    print("[OK] Login detected! Waiting for you to finish setup...")
        else:
            print("\n[OK] Already logged in!")
            print("\nPlease manually:")
            print("1. Click 'Following' tab")
            print("2. Turn OFF 'Open alerts only' toggle")
            print("3. Wait for alerts to load")
            time.sleep(30)

        # DO NOT RELOAD - User has already set everything up during manual wait
        print("\n[STEP 4] Verifying setup (NOT reloading page)...")
        time.sleep(2)

        # Verify we're on the right page and content is loaded
        print("\n[STEP 5] Checking for Following tab content...")
        if 'Following' in driver.page_source:
            print("[OK] Following tab detected in page")
        else:
            print("[WARN] Following tab not detected - make sure you clicked it")

        # Check if alerts are present
        print("\n[STEP 6] Checking for alerts...")
        if 'app-alerts-table-row' in driver.page_source or 'Opened' in driver.page_source or 'Closed' in driver.page_source:
            print("[OK] Alerts detected in page")
        else:
            print("[WARN] No alerts detected - make sure page fully loaded")

        # Wait for any final loading
        print("\n[STEP 7] Waiting 10 more seconds for complete load...")
        time.sleep(10)

        # Scroll to load more
        print("\n[STEP 8] Scrolling to load all alerts...")
        for i in range(10):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)

        # Get HTML
        print("\n[STEP 9] Capturing page HTML...")
        page_source = driver.page_source

        # Save for debugging
        html_file = Path.home() / '.xtrades_cache' / 'following_final.html'
        html_file.parent.mkdir(exist_ok=True)
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(page_source)
        print(f"[INFO] Saved HTML to: {html_file}")
        print(f"[INFO] HTML size: {len(page_source):,} bytes")

        # Verify content with detailed feedback
        print("\n[STEP 10] Verifying page content...")
        checks = [
            ('Opened', 'Open positions (Opened X ago)'),
            ('Closed', 'Closed positions (Closed X ago)'),
            ('@', 'Usernames (@username)'),
            ('Bought', 'Buy actions'),
            ('Sold', 'Sell actions'),
            ('app-alerts-table-row', 'Alert row elements'),
        ]
        found_count = 0
        for text, label in checks:
            count = page_source.count(text)
            if count > 0:
                print(f"[OK] {label}: Found {count} occurrences")
                found_count += 1
            else:
                print(f"[WARN] {label}: Not found")

        if found_count < 3:
            print(f"\n[ERROR] Only {found_count}/6 checks passed!")
            print("[ACTION] This suggests the page didn't load properly.")
            print("         Please ensure during manual setup you:")
            print("         1. Successfully logged in")
            print("         2. Clicked the 'Following' tab")
            print("         3. Turned OFF the 'Open alerts only' toggle")
            print("         4. Saw trader names and alerts appear")

        # Parse with BeautifulSoup
        soup = BeautifulSoup(page_source, 'html.parser')
        alert_rows = soup.find_all('app-alerts-table-row')
        print(f"\n[STEP 11] Found {len(alert_rows)} alert row elements")

        if not alert_rows:
            print("\n[ERROR] No <app-alerts-table-row> elements found!")
            print("[ACTION] Make sure during the 3-minute timer you:")
            print("  1. Logged in successfully with Discord")
            print("  2. Clicked 'Following' tab at the top")
            print("  3. Turned OFF the blue 'Open alerts only' toggle")
            print("  4. Waited for alerts to appear (you should see trader names)")
            print(f"\n[DEBUG] Check saved HTML file: {html_file}")
            return 1

        # Show first 3 alert texts for debugging
        print("\n[STEP 12] Sample alert texts (first 3):")
        for i, row in enumerate(alert_rows[:3], 1):
            text = row.get_text(strip=True)
            preview = text[:150] + "..." if len(text) > 150 else text
            print(f"  [{i}] {preview}")

        # Parse each alert
        print(f"\n[STEP 13] Parsing {len(alert_rows)} alerts...")
        parsed_alerts = []
        failed_count = 0

        for i, row in enumerate(alert_rows, 1):
            alert_data = parse_alert_row(row)
            if alert_data:
                parsed_alerts.append(alert_data)
                status = "OPEN" if alert_data['status'] == 'open' else "CLOSED"
                profile = alert_data.get('profile_username', 'unknown')
                ticker = alert_data['ticker']
                action = alert_data.get('action', '?')
                pnl = alert_data.get('pnl_percent', 0) or 0
                print(f"  [{i}] OK - @{profile}: {action} {ticker} - {status} - {pnl:+.1f}%")
            else:
                failed_count += 1
                if failed_count <= 3:  # Show first 3 failures
                    text = row.get_text(strip=True)[:100]
                    print(f"  [{i}] SKIP - Could not parse: {text}...")

        print(f"\n[STEP 14] Parsing Results:")
        print(f"  Total alert rows found: {len(alert_rows)}")
        print(f"  Successfully parsed: {len(parsed_alerts)}")
        print(f"  Failed to parse: {failed_count}")

        if len(parsed_alerts) == 0:
            print("\n[ERROR] No alerts were successfully parsed!")
            print("[ACTION] This usually means:")
            print("  1. The page didn't load properly during manual setup")
            print("  2. The alerts format has changed")
            print("  3. You're not following any traders yet")
            print(f"\n[DEBUG] Check the saved HTML file to see what was captured:")
            print(f"        {html_file}")
            return 1

        # Count by status
        open_count = sum(1 for a in parsed_alerts if a['status'] == 'open')
        closed_count = sum(1 for a in parsed_alerts if a['status'] == 'closed')
        unknown_count = sum(1 for a in parsed_alerts if a['status'] not in ['open', 'closed'])

        print(f"\n  Breakdown by status:")
        print(f"    Open positions: {open_count}")
        print(f"    Closed positions: {closed_count}")
        if unknown_count > 0:
            print(f"    Unknown status: {unknown_count}")

        # Store in database
        print(f"\n[STEP 15] Storing {len(parsed_alerts)} alerts in database...")
        stored = 0

        for alert in parsed_alerts:
            try:
                profile_username = alert.get('profile_username')
                if not profile_username:
                    continue

                # Get or create profile
                profile = db.get_profile_by_username(profile_username)
                if not profile:
                    print(f"  [INFO] Creating profile: {profile_username}")
                    profile_id = db.add_profile(
                        username=profile_username,
                        display_name=f"@{profile_username}",
                        notes='From following alerts feed'
                    )
                    profile = db.get_profile_by_username(profile_username)

                # Check duplicate
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
                    'ticker': alert['ticker'],
                    'strategy': alert.get('strategy', 'Unknown'),
                    'action': alert.get('action', 'Unknown'),
                    'entry_price': alert.get('entry_price'),
                    'strike_price': alert.get('strike_price'),
                    'expiration_date': alert.get('expiration_date'),
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
        print("\n1. Dashboard: http://localhost:8501")
        print("2. Navigate to: Xtrades Watchlists")
        print("3. Active Trades tab: Shows OPEN positions")
        print("4. Closed Trades tab: Shows CLOSED positions")
        print("\nYou can now track when traders open and close positions!")

        # Keep browser open
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
