"""
Scrape Alerts from Your Followed Profiles
This scrapes the main alerts feed at https://app.xtrades.net/alerts
which shows ALL alerts from profiles you follow
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
from dotenv import load_dotenv

load_dotenv()

def parse_alert_row(row_element):
    """Parse alert row from main feed"""
    try:
        result = {
            'ticker': None,
            'status': 'unknown',
            'pnl_percent': None,
            'alert_timestamp': None,
            'alert_text': '',
            'profile_username': None  # We'll extract this too
        }

        # Extract ticker from image
        img = row_element.find('img', {'src': lambda x: x and 'logo' in x})
        if img and img.get('src'):
            src = img['src']
            ticker = src.split('/')[-1].replace('.png', '').upper()
            result['ticker'] = ticker

        # Extract profile username (if shown)
        # This might be in a link or username element
        profile_links = row_element.find_all('a', href=lambda x: x and '/profile/' in str(x))
        if profile_links:
            for link in profile_links:
                href = link.get('href', '')
                if '/profile/' in href:
                    username = href.split('/profile/')[-1].split('/')[0].split('?')[0]
                    if username:
                        result['profile_username'] = username
                        break

        # Extract age
        age_div = row_element.find('div', class_=lambda x: x and 'company__pill' in x)
        if age_div:
            age_text = age_div.get_text(strip=True)
            result['alert_text'] = f"{age_text} - "

            # Parse timestamp from age
            days_match = re.search(r'(\d+)d', age_text)
            hours_match = re.search(r'(\d+)h', age_text)
            mins_match = re.search(r'(\d+)m', age_text)

            if days_match:
                days_ago = int(days_match.group(1))
                result['alert_timestamp'] = (datetime.now() - timedelta(days=days_ago)).isoformat()
            elif hours_match:
                hours_ago = int(hours_match.group(1))
                result['alert_timestamp'] = (datetime.now() - timedelta(hours=hours_ago)).isoformat()
            elif mins_match:
                mins_ago = int(mins_match.group(1))
                result['alert_timestamp'] = (datetime.now() - timedelta(minutes=mins_ago)).isoformat()
            else:
                result['alert_timestamp'] = datetime.now().isoformat()
        else:
            result['alert_timestamp'] = datetime.now().isoformat()

        # Extract status - "Opened" or "Closed"
        time_spans = row_element.find_all('span', class_='time-profile')
        for span in time_spans:
            text = span.get_text(strip=True)
            result['alert_text'] += text + " "
            if 'Closed' in text:
                result['status'] = 'closed'
            elif 'Opened' in text:
                result['status'] = 'open'

        # Extract P/L or current status
        result_div = row_element.find('app-alert-result')
        if result_div:
            result_text = result_div.get_text(strip=True)
            result['alert_text'] += result_text + " "

            # Parse different formats
            patterns = [
                (r'Made\s+([\d.]+)%', 1, False),
                (r'Lost\s+([\d.]+)%', -1, False),
                (r'DOWN\s+([\d.]+)%', -1, False),
                (r'UP\s+([\d.]+)%', 1, False),
            ]

            for pattern, sign, _ in patterns:
                match = re.search(pattern, result_text)
                if match:
                    result['pnl_percent'] = sign * float(match.group(1))
                    break

        result['alert_text'] = result['alert_text'].strip()

        if result['ticker']:
            return result

        return None

    except Exception as e:
        print(f"[ERROR] Parse failed: {e}")
        return None

def main():
    print("="*70)
    print("SCRAPING ALERTS FROM FOLLOWED PROFILES")
    print("="*70)

    scraper = XtradesScraper(headless=False)
    db = XtradesDBManager()

    try:
        # Login
        print("\n[STEP 1] Logging in...")
        if not scraper.login():
            return 1
        print("[OK] Logged in")

        # Navigate to ALERTS FEED (not profile page!)
        print("\n[STEP 2] Navigating to alerts feed...")
        scraper.driver.get("https://app.xtrades.net/alerts")
        time.sleep(5)

        # Wait for alerts to load
        print("\n[STEP 3] Waiting 30 seconds for alerts to load...")
        time.sleep(30)

        # Scroll to load more
        print("\n[STEP 4] Scrolling to load all alerts...")
        for i in range(5):
            scraper.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            print(f"  Scrolled {i+1}/5")

        # Scroll back to top
        scraper.driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)

        # Get HTML
        print("\n[STEP 5] Parsing alerts...")
        page_source = scraper.driver.page_source

        # Save for debugging
        html_file = Path.home() / '.xtrades_cache' / 'followed_alerts.html'
        html_file.parent.mkdir(exist_ok=True)
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(page_source)
        print(f"[INFO] Saved HTML: {html_file}")

        # Check for HIMS
        if 'HIMS' in page_source.upper():
            print("[SUCCESS] Found HIMS in HTML!")
        else:
            print("[WARN] HIMS not found")

        # Check for "Opened"
        if 'Opened' in page_source:
            print("[SUCCESS] Found 'Opened' - active trades present!")
        else:
            print("[WARN] No 'Opened' text")

        # Parse
        soup = BeautifulSoup(page_source, 'html.parser')
        alert_rows = soup.find_all('app-alerts-table-row')
        print(f"\n[INFO] Found {len(alert_rows)} alert rows")

        parsed_alerts = []
        for i, row in enumerate(alert_rows, 1):
            alert_data = parse_alert_row(row)
            if alert_data:
                parsed_alerts.append(alert_data)
                status = "ACTIVE" if alert_data['status'] == 'open' else "CLOSED"
                profile = alert_data.get('profile_username', 'unknown')
                pnl = alert_data.get('pnl_percent', 0)
                print(f"  [{i}] {alert_data['ticker']} ({profile}): {status} - {pnl}%")

        print(f"\n[SUCCESS] Parsed {len(parsed_alerts)} alerts")

        # Count by status
        active = sum(1 for a in parsed_alerts if a['status'] == 'open')
        closed = sum(1 for a in parsed_alerts if a['status'] == 'closed')
        print(f"  Active: {active}")
        print(f"  Closed: {closed}")

        # Store alerts
        print(f"\n[STEP 6] Storing {len(parsed_alerts)} alerts in database...")

        stored = 0
        for alert in parsed_alerts:
            try:
                # Get or create profile
                profile_username = alert.get('profile_username', 'behappy')
                profile = db.get_profile_by_username(profile_username)

                if not profile:
                    # Auto-create profile if it doesn't exist
                    print(f"  [INFO] Creating profile: {profile_username}")
                    profile_id = db.add_profile(
                        username=profile_username,
                        display_name=profile_username.title(),
                        notes='Auto-created from alerts feed'
                    )
                    profile = db.get_profile_by_username(profile_username)

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
                    'ticker': alert['ticker'],
                    'strategy': 'Unknown',
                    'action': 'Unknown',
                    'entry_price': None,
                    'alert_text': alert['alert_text'],
                    'alert_timestamp': alert_time,
                    'status': alert['status'],
                    'pnl_percent': alert.get('pnl_percent')
                }

                trade_id = db.add_trade(trade_data)
                stored += 1
                status_label = "ACTIVE" if alert['status'] == 'open' else "CLOSED"
                print(f"  [OK] {alert['ticker']} ({profile_username}): {status_label} (ID: {trade_id})")

            except Exception as e:
                print(f"  [ERROR] Failed to store: {e}")

        print(f"\n[COMPLETE] Stored {stored}/{len(parsed_alerts)} alerts")

        # Update sync status for all profiles
        all_profiles = db.get_active_profiles()
        for prof in all_profiles:
            db.update_profile_sync_status(prof['id'], 'success', 0)

        print("\n" + "="*70)
        print("SUCCESS - REFRESH DASHBOARD TO SEE ALERTS")
        print("="*70)
        print("\n1. Go to: http://localhost:8501")
        print("2. Navigate to: Xtrades Watchlists")
        print("3. Check both Active and Closed tabs")
        print("4. You should see your followed alerts!")

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
