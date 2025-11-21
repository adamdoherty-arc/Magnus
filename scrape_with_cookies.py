"""
Xtrades Scraper with Cookie-Based Session Persistence
Log in once manually, then all future runs are automatic
"""

import sys
from pathlib import Path
import time
import re
import pickle
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

COOKIE_FILE = Path.home() / '.xtrades_cache' / 'cookies.pkl'

def parse_alert_row(row):
    """Parse complete alert with full trade details"""
    try:
        # IMPORTANT: Use separator=' ' to add spaces between HTML elements!
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

def save_cookies(driver):
    """Save cookies to file"""
    COOKIE_FILE.parent.mkdir(exist_ok=True)
    cookies = driver.get_cookies()
    with open(COOKIE_FILE, 'wb') as f:
        pickle.dump(cookies, f)
    print(f"[OK] Saved session cookies to: {COOKIE_FILE}")

def load_cookies(driver):
    """Load cookies from file"""
    if not COOKIE_FILE.exists():
        return False

    try:
        with open(COOKIE_FILE, 'rb') as f:
            cookies = pickle.load(f)

        for cookie in cookies:
            # Remove expiry if present as it can cause issues
            if 'expiry' in cookie:
                del cookie['expiry']
            driver.add_cookie(cookie)

        print(f"[OK] Loaded session cookies from: {COOKIE_FILE}")
        return True
    except Exception as e:
        print(f"[WARN] Could not load cookies: {e}")
        return False

def main():
    print("="*70)
    print("XTRADES SCRAPER WITH COOKIE-BASED SESSION")
    print("="*70)
    print("\nFirst run: Log in manually (one time only)")
    print("Future runs: Automatic using saved session")
    print("="*70)

    db = XtradesDBManager()

    # Setup Chrome
    chrome_options = Options()
    chrome_options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    print("\n[STEP 1] Starting Chrome...")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    wait = WebDriverWait(driver, 10)

    try:
        # Navigate to base domain first (required for cookies)
        print("\n[STEP 2] Opening Xtrades...")
        driver.get("https://app.xtrades.net")
        time.sleep(2)

        # Try to load saved cookies
        cookies_loaded = load_cookies(driver)

        # Navigate to alerts page
        print("\n[STEP 3] Opening alerts page...")
        driver.get("https://app.xtrades.net/alerts")
        time.sleep(5)

        # Check if logged in
        is_logged_in = 'Sign in' not in driver.page_source

        if not is_logged_in:
            if cookies_loaded:
                print("[WARN] Cookies didn't work - need to log in again")

            print("\n[STEP 4] MANUAL LOGIN REQUIRED")
            print("="*70)
            print("IN THE CHROME WINDOW:")
            print("")
            print("1. Click 'Sign in with Discord'")
            print("2. Complete Discord OAuth login")
            print("3. You'll be redirected back to Xtrades")
            print("")
            print("After login, I'll save your session for future runs")
            print("="*70)
            print("\nWaiting 2 minutes for you to log in...")

            # Wait for login with progress updates
            for i in range(120, 0, -20):
                print(f"[TIMER] {i} seconds remaining...")
                time.sleep(20)

            print("\n[INFO] Checking login status...")
            time.sleep(2)
            if 'Sign in' not in driver.page_source:
                save_cookies(driver)
                print("[OK] Login successful! Session saved.")
            else:
                print("[ERROR] Login failed. Please try again.")
                return 1
        else:
            print("[OK] Already logged in using saved session!")

        # Now navigate to alerts and set up Following tab
        print("\n[STEP 5] Setting up Following tab...")
        driver.get("https://app.xtrades.net/alerts")
        time.sleep(3)

        # Click Following tab
        try:
            following_btn = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Following')]"))
            )
            following_btn.click()
            print("[OK] Clicked Following tab")
            time.sleep(3)
        except:
            print("[WARN] Could not find Following tab button")

        # Turn OFF "Open alerts only" toggle
        print("\n[STEP 6] Turning OFF 'Open alerts only' toggle...")
        try:
            toggles = driver.find_elements(By.XPATH, "//ion-toggle")
            for i, toggle in enumerate(toggles):
                is_checked = toggle.get_attribute('aria-checked')
                if is_checked == 'true':
                    toggle.click()
                    time.sleep(2)
                    print("[OK] Toggle OFF - showing both open and closed alerts")
                    break
        except Exception as e:
            print(f"[WARN] Toggle error: {e}")

        # Wait for alerts to load
        print("\n[STEP 7] Waiting for alerts to load...")
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
        html_file = Path.home() / '.xtrades_cache' / 'cookies_scrape.html'
        html_file.parent.mkdir(exist_ok=True)
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(page_source)
        print(f"[INFO] Saved HTML to: {html_file}")
        print(f"[INFO] HTML size: {len(page_source):,} bytes")

        # Verify content
        print("\n[STEP 10] Verifying page content...")
        checks = [
            ('Opened', 'Open positions'),
            ('Closed', 'Closed positions'),
            ('@', 'Usernames'),
            ('app-alerts-table-row', 'Alert rows'),
        ]
        for text, label in checks:
            count = page_source.count(text)
            if count > 0:
                print(f"[OK] {label}: Found {count}")
            else:
                print(f"[WARN] {label}: Not found")

        # Parse alerts
        soup = BeautifulSoup(page_source, 'html.parser')
        alert_rows = soup.find_all('app-alerts-table-row')
        print(f"\n[STEP 11] Found {len(alert_rows)} alert rows")

        if not alert_rows:
            print("\n[ERROR] No alerts found!")
            print(f"[DEBUG] Check saved HTML: {html_file}")
            return 1

        # Show samples
        print("\n[STEP 12] Sample alerts (first 3):")
        for i, row in enumerate(alert_rows[:3], 1):
            text = row.get_text(strip=True)[:150]
            print(f"  [{i}] {text}...")

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

        print(f"\n[STEP 14] Results:")
        print(f"  Successfully parsed: {len(parsed_alerts)}")
        print(f"  Failed to parse: {failed_count}")

        if len(parsed_alerts) == 0:
            print("\n[ERROR] No alerts parsed!")
            return 1

        # Count by status
        open_count = sum(1 for a in parsed_alerts if a['status'] == 'open')
        closed_count = sum(1 for a in parsed_alerts if a['status'] == 'closed')
        print(f"\n  Open: {open_count}")
        print(f"  Closed: {closed_count}")

        # Store in database
        print(f"\n[STEP 15] Storing {len(parsed_alerts)} alerts...")
        stored = 0

        for alert in parsed_alerts:
            try:
                profile_username = alert.get('profile_username')
                if not profile_username:
                    continue

                # Get or create profile
                profile = db.get_profile_by_username(profile_username)
                if not profile:
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
        print("SUCCESS")
        print("="*70)
        print("\nDashboard: http://localhost:8501")
        print("Navigate to: Xtrades Watchlists")
        print("")
        print("Next time you run this script, it will use saved cookies")
        print("and skip the manual login step entirely!")

        # Keep browser open briefly
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
