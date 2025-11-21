"""
Xtrades Scraper Using Scrapling
Modern, adaptive scraper with better stability and anti-detection
"""

import sys
from pathlib import Path
import time
import re
import os
from datetime import datetime, timedelta
from scrapling import Fetcher
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent / 'src'))
from xtrades_db_manager import XtradesDBManager

load_dotenv()

def parse_alert_row(row_html):
    """Parse alert row from HTML text"""
    try:
        full_text = row_html.text

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

        # Extract username
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

        # Extract expiration date
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

        # Extract entry price
        entry_match = re.search(r'@\s*\$(\d+\.?\d*)', full_text)
        if entry_match:
            result['entry_price'] = float(entry_match.group(1))

        # Extract status and time
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

        # Build strategy
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
    print("XTRADES SCRAPER WITH SCRAPLING")
    print("="*70)

    db = XtradesDBManager()

    # Get credentials
    username = os.getenv('XTRADES_USERNAME')
    password = os.getenv('XTRADES_PASSWORD')

    if not username or not password:
        print("[ERROR] XTRADES_USERNAME and XTRADES_PASSWORD must be set in .env")
        return 1

    try:
        # Initialize Scrapling Stealthy Fetcher (Firefox-based with anti-detection)
        print("\n[STEP 1] Initializing Scrapling browser...")
        fetcher = StealthyFetcher(
            headless=False,  # Show browser for login
            auto_match_enabled=True  # Enable adaptive element matching
        )

        # Navigate to login page
        print("\n[STEP 2] Opening Xtrades login...")
        page = fetcher.get("https://app.xtrades.net/login", network_idle=True)
        time.sleep(3)

        print("\n[STEP 3] Looking for Discord login button...")
        # Look for Discord button
        discord_btns = page.css("button, a").filter(lambda x: 'discord' in x.text.lower())

        if discord_btns:
            print("[OK] Found Discord button, clicking...")
            discord_btns[0].click()
            time.sleep(5)

            # Check if we're on Discord OAuth page
            current_url = fetcher.page.url
            if 'discord.com' in current_url:
                print("[OK] On Discord OAuth page")

                # Fill in Discord credentials
                try:
                    print("[INFO] Entering Discord credentials...")
                    email_input = fetcher.page.locator("input[name='email']")
                    if email_input.is_visible():
                        email_input.fill(username)
                        time.sleep(1)

                    password_input = fetcher.page.locator("input[name='password']")
                    if password_input.is_visible():
                        password_input.fill(password)
                        time.sleep(1)

                    # Click login
                    login_btn = fetcher.page.locator("button[type='submit']")
                    if login_btn.is_visible():
                        login_btn.click()
                        print("[OK] Clicked Discord login")
                        time.sleep(5)

                    # Look for Authorize button
                    authorize_btn = fetcher.page.locator("button:has-text('Authorize'), button:has-text('authorize')")
                    if authorize_btn.is_visible(timeout=5000):
                        authorize_btn.click()
                        print("[OK] Clicked Authorize")
                        time.sleep(5)
                except Exception as e:
                    print(f"[WARN] OAuth flow warning: {e}")

        # Wait for redirect to Xtrades
        print("\n[STEP 4] Waiting for redirect...")
        time.sleep(5)

        # Navigate to alerts page
        print("\n[STEP 5] Navigating to alerts page...")
        page = fetcher.get("https://app.xtrades.net/alerts", network_idle=True)
        time.sleep(5)

        # Verify login
        if 'Sign in' in page.text:
            print("[ERROR] Not logged in! Please check credentials.")
            input("\nPress ENTER to manually log in, then continue...")
            time.sleep(5)
            page = fetcher.get("https://app.xtrades.net/alerts", network_idle=True)

        print("[OK] On alerts page")

        # Click Following tab
        print("\n[STEP 6] Clicking 'Following' tab...")
        try:
            following_btn = fetcher.page.locator("button:has-text('Following')")
            if following_btn.is_visible(timeout=5000):
                following_btn.click()
                print("[OK] Clicked Following tab")
                time.sleep(3)
        except:
            print("[WARN] Could not find Following tab")

        # Turn OFF "Open alerts only" toggle
        print("\n[STEP 7] Checking 'Open alerts only' toggle...")
        try:
            toggles = fetcher.page.locator("ion-toggle")
            count = toggles.count()
            print(f"[INFO] Found {count} toggles")

            for i in range(count):
                toggle = toggles.nth(i)
                is_checked = toggle.get_attribute('aria-checked')
                if is_checked == 'true':
                    print(f"[ACTION] Turning OFF toggle {i+1}")
                    toggle.click()
                    time.sleep(2)
        except Exception as e:
            print(f"[WARN] Toggle error: {e}")

        # Wait for alerts to load
        print("\n[STEP 8] Waiting for alerts to load...")
        time.sleep(10)

        # Scroll to load more alerts
        print("\n[STEP 9] Scrolling to load all alerts...")
        for i in range(5):
            fetcher.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(2)
        fetcher.page.evaluate("window.scrollTo(0, 0)")
        time.sleep(2)

        # Get page content
        print("\n[STEP 10] Parsing alerts...")
        page_html = fetcher.page.content()

        # Save HTML for debugging
        html_file = Path.home() / '.xtrades_cache' / 'scrapling_alerts.html'
        html_file.parent.mkdir(exist_ok=True)
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(page_html)
        print(f"[INFO] Saved HTML: {html_file}")

        # Parse with Scrapling
        from scrapling import Adaptor
        parsed_page = Adaptor(page_html)
        alert_rows = parsed_page.css("app-alerts-table-row")
        print(f"\n[INFO] Found {len(alert_rows)} alert rows")

        if not alert_rows:
            print("[ERROR] No alerts found!")
            print("[ACTION] Check if you:")
            print("  1. Successfully logged in")
            print("  2. Clicked Following tab")
            print("  3. Turned OFF 'Open alerts only' toggle")
            return 1

        # Parse each alert
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
        print(f"\n[STEP 11] Storing {len(parsed_alerts)} alerts...")
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
        print("2. Go to: Xtrades Watchlists")
        print("3. Active Trades tab: Open alerts")
        print("4. Closed Trades tab: Closed alerts")

        return 0

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        print("\n[INFO] Closing browser...")
        try:
            fetcher.close()
        except:
            pass

if __name__ == "__main__":
    sys.exit(main())
