"""
Scrape ALL Alerts from Following Feed
Includes both OPEN and CLOSED alerts with full trade details
"""

import sys
from pathlib import Path
import time
import re
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from xtrades_scraper import XtradesScraper
from xtrades_db_manager import XtradesDBManager
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from dotenv import load_dotenv

load_dotenv()

def parse_alert_row(row_element):
    """Parse complete alert with full trade details"""
    try:
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
            'alert_text': '',
        }

        # Extract profile username from avatar/link
        # Look for @username pattern
        username_spans = row_element.find_all('span', string=lambda x: x and '@' in str(x))
        if username_spans:
            username_text = username_spans[0].get_text(strip=True)
            result['profile_username'] = username_text.replace('@', '')
        else:
            # Try finding in link
            profile_links = row_element.find_all('a', href=lambda x: x and '/profile/' in str(x))
            if profile_links:
                href = profile_links[0].get('href', '')
                username = href.split('/profile/')[-1].split('/')[0].split('?')[0]
                if username:
                    result['profile_username'] = username

        # Get the main trade text (like "Bought HIMS 11/07 $50 Puts @ $7.28")
        # This is usually in a text node or specific element
        trade_text_elem = row_element.find('div', class_='column--trade')
        if not trade_text_elem:
            # Try alternative selectors
            trade_text_elem = row_element.find('app-company-logo')

        # Get all text from the row to parse
        full_text = row_element.get_text(strip=True)
        result['alert_text'] = full_text

        # Extract action (Bought, Sold, Shorted, Covered, etc.)
        actions = ['Bought', 'Sold', 'Shorted', 'Covered', 'Rolled']
        for action in actions:
            if action in full_text:
                result['action'] = action
                break

        # Extract ticker (uppercase letters before expiration date or after action)
        # Pattern: "Bought HIMS" or "Sold TSLA"
        ticker_match = re.search(r'(?:Bought|Sold|Shorted|Covered|Rolled)\s+([A-Z]{1,5})\s', full_text)
        if ticker_match:
            result['ticker'] = ticker_match.group(1)

        # Extract expiration date (MM/DD format)
        exp_match = re.search(r'(\d{1,2}/\d{1,2})', full_text)
        if exp_match:
            exp_str = exp_match.group(1)
            # Convert to full date (assume current or next year)
            month, day = exp_str.split('/')
            year = datetime.now().year
            try:
                exp_date = datetime(year, int(month), int(day))
                if exp_date < datetime.now():
                    exp_date = datetime(year + 1, int(month), int(day))
                result['expiration_date'] = exp_date.date().isoformat()
            except:
                pass

        # Extract strike price (like $50, $210)
        strike_match = re.search(r'\$(\d+)\s+(?:Calls?|Puts?)', full_text)
        if strike_match:
            result['strike_price'] = float(strike_match.group(1))

        # Extract option type (Calls or Puts)
        if 'Calls' in full_text or 'Call' in full_text:
            result['option_type'] = 'Call'
        elif 'Puts' in full_text or 'Put' in full_text:
            result['option_type'] = 'Put'

        # Extract entry price (@ $7.28)
        entry_match = re.search(r'@\s*\$(\d+\.?\d*)', full_text)
        if entry_match:
            result['entry_price'] = float(entry_match.group(1))

        # Extract status and time
        if 'Opened' in full_text:
            result['status'] = 'open'
            # Extract time (6h ago, 4d ago)
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
        if 'Down' in full_text:
            pnl_match = re.search(r'Down\s+([\d.]+)%', full_text)
            if pnl_match:
                result['pnl_percent'] = -float(pnl_match.group(1))
        elif 'Up' in full_text:
            pnl_match = re.search(r'Up\s+([\d.]+)%', full_text)
            if pnl_match:
                result['pnl_percent'] = float(pnl_match.group(1))
        elif 'Made' in full_text:
            pnl_match = re.search(r'Made\s+([\d.]+)%', full_text)
            if pnl_match:
                result['pnl_percent'] = float(pnl_match.group(1))
        elif 'Lost' in full_text:
            pnl_match = re.search(r'Lost\s+([\d.]+)%', full_text)
            if pnl_match:
                result['pnl_percent'] = -float(pnl_match.group(1))

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
    print("SCRAPING FOLLOWING ALERTS (OPEN + CLOSED)")
    print("="*70)

    scraper = XtradesScraper(headless=False)
    db = XtradesDBManager()

    try:
        # Login
        print("\n[STEP 1] Logging in...")
        if not scraper.login():
            return 1
        print("[OK] Logged in")

        # Navigate to alerts
        print("\n[STEP 2] Navigating to alerts page...")
        scraper.driver.get("https://app.xtrades.net/alerts")
        time.sleep(5)

        # Click "Following" tab
        print("\n[STEP 3] Clicking 'Following' tab...")
        try:
            following_btn = scraper.driver.find_element(By.XPATH, "//button[contains(text(), 'Following')]")
            following_btn.click()
            print("[OK] Clicked Following tab")
            time.sleep(3)
        except:
            print("[WARN] Could not click Following tab, continuing...")

        # Turn OFF "Open alerts only" toggle to see ALL alerts
        print("\n[STEP 4] Turning OFF 'Open alerts only' toggle...")
        try:
            # The toggle might be an ion-toggle or input element
            toggle = scraper.driver.find_element(By.XPATH, "//ion-toggle[contains(@class, 'ion-toggle')]")
            # Check if it's currently on
            is_checked = toggle.get_attribute('aria-checked') == 'true'
            if is_checked:
                toggle.click()
                print("[OK] Turned OFF 'Open alerts only'")
                time.sleep(2)
            else:
                print("[INFO] Toggle already OFF")
        except:
            print("[WARN] Could not find toggle, continuing...")

        # Wait for alerts to load
        print("\n[STEP 5] Waiting 30 seconds for all alerts to load...")
        time.sleep(30)

        # Scroll to load more
        print("\n[STEP 6] Scrolling to load all alerts...")
        for i in range(10):
            scraper.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            print(f"  Scrolled {i+1}/10")

        # Scroll back to top
        scraper.driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)

        # Get HTML
        print("\n[STEP 7] Parsing alerts...")
        page_source = scraper.driver.page_source

        # Save
        html_file = Path.home() / '.xtrades_cache' / 'following_all_alerts.html'
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(page_source)
        print(f"[INFO] Saved HTML: {html_file}")

        # Check for expected content
        if 'HIMS' in page_source.upper():
            print("[SUCCESS] Found HIMS")
        if 'Opened' in page_source:
            print("[SUCCESS] Found 'Opened'")
        if 'Closed' in page_source:
            print("[SUCCESS] Found 'Closed'")

        # Parse
        soup = BeautifulSoup(page_source, 'html.parser')
        alert_rows = soup.find_all('app-alerts-table-row')
        print(f"\n[INFO] Found {len(alert_rows)} alert rows")

        parsed_alerts = []
        for i, row in enumerate(alert_rows, 1):
            alert_data = parse_alert_row(row)
            if alert_data:
                parsed_alerts.append(alert_data)
                status = "OPEN" if alert_data['status'] == 'open' else "CLOSED"
                profile = alert_data.get('profile_username', 'unknown')
                ticker = alert_data['ticker']
                action = alert_data.get('action', '?')
                pnl = alert_data.get('pnl_percent', 0)
                print(f"  [{i}] @{profile}: {action} {ticker} - {status} - {pnl:+.1f}%")

        print(f"\n[SUCCESS] Parsed {len(parsed_alerts)} alerts")

        # Count
        open_count = sum(1 for a in parsed_alerts if a['status'] == 'open')
        closed_count = sum(1 for a in parsed_alerts if a['status'] == 'closed')
        print(f"  Open: {open_count}")
        print(f"  Closed: {closed_count}")

        # Store
        print(f"\n[STEP 8] Storing {len(parsed_alerts)} alerts...")

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

        print(f"\n[COMPLETE] Stored {stored}/{len(parsed_alerts)} alerts")

        print("\n" + "="*70)
        print("SUCCESS - REFRESH DASHBOARD")
        print("="*70)
        print("\n1. Dashboard: http://localhost:8501")
        print("2. Go to: Xtrades Watchlists")
        print("3. Check Active Trades tab for open alerts")
        print("4. Check Closed Trades tab for closed alerts")

        return 0

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        print("\n[INFO] Keeping browser open for 10 seconds...")
        time.sleep(10)
        scraper.close()

if __name__ == "__main__":
    sys.exit(main())
