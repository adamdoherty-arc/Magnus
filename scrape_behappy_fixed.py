"""
FIXED: Scrape Real Alerts from BeHappy - Correct Element Parsing
This will scrape the actual app-alerts-table-row elements and extract real data
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
    """
    Parse a single app-alerts-table-row element

    Structure:
    - Ticker: from img src URL (e.g., https://storage.xtrades.net/images/logo/mstr.png -> MSTR)
    - Age: from div with "4d", "3d", etc.
    - Status: "Closed" or "Open", with time like "3d ago"
    - Result: "Made X%" or "Lost X%"
    - Sentiment: likes, bookmarks, comments
    """
    try:
        result = {
            'ticker': None,
            'status': 'unknown',
            'pnl_percent': None,
            'alert_timestamp': None,
            'alert_text': '',
            'entry_price': None,
            'strategy': None,
            'action': None
        }

        # Extract ticker from image URL
        img = row_element.find('img', {'src': lambda x: x and 'logo' in x})
        if img and img.get('src'):
            # URL like: https://storage.xtrades.net/images/logo/mstr.png
            src = img['src']
            ticker = src.split('/')[-1].replace('.png', '').upper()
            result['ticker'] = ticker

        # Extract age (like "4d")
        age_div = row_element.find('div', class_=lambda x: x and 'company__pill' in x)
        if age_div:
            age_text = age_div.get_text(strip=True)
            result['alert_text'] = f"{age_text} - "

        # Extract status (Closed/Open) and time
        time_spans = row_element.find_all('span', class_='time-profile')
        if time_spans:
            for span in time_spans:
                text = span.get_text(strip=True)
                result['alert_text'] += text + " "
                if 'closed' in text.lower():
                    result['status'] = 'closed'
                elif 'open' in text.lower():
                    result['status'] = 'open'

        # Extract P/L result
        result_div = row_element.find('app-alert-result')
        if result_div:
            result_text = result_div.get_text(strip=True)
            result['alert_text'] += result_text + " "

            # Parse Made/Lost X%
            if 'Made' in result_text:
                match = re.search(r'Made\s+([\d.]+)%', result_text)
                if match:
                    result['pnl_percent'] = float(match.group(1))
            elif 'Lost' in result_text:
                match = re.search(r'Lost\s+([\d.]+)%', result_text)
                if match:
                    result['pnl_percent'] = -float(match.group(1))

        # Estimate timestamp based on age
        if age_div:
            age_text = age_div.get_text(strip=True)
            days_match = re.search(r'(\d+)d', age_text)
            if days_match:
                days_ago = int(days_match.group(1))
                result['alert_timestamp'] = (datetime.now() - timedelta(days=days_ago)).isoformat()
            else:
                result['alert_timestamp'] = datetime.now().isoformat()
        else:
            result['alert_timestamp'] = datetime.now().isoformat()

        # Clean up alert text
        result['alert_text'] = result['alert_text'].strip()

        # Only return if we have minimum data
        if result['ticker']:
            return result

        return None

    except Exception as e:
        print(f"[ERROR] Failed to parse row: {e}")
        return None

def main():
    print("="*70)
    print("SCRAPING REAL ALERTS - FIXED VERSION")
    print("="*70)

    scraper = XtradesScraper(headless=False)
    db = XtradesDBManager()

    try:
        # Step 1: Login
        print("\n[STEP 1] Logging in...")
        if not scraper.login():
            print("[ERROR] Login failed")
            return 1
        print("[OK] Logged in")

        # Step 2: Navigate
        print("\n[STEP 2] Navigating to behappy profile...")
        scraper.driver.get("https://app.xtrades.net/profile/behappy")
        time.sleep(5)

        # Step 3: Wait and scroll
        print("\n[STEP 3] Waiting for content (30 seconds)...")
        time.sleep(30)

        print("[STEP 4] Scrolling...")
        for i in range(5):
            scraper.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)

        # Step 5: Parse HTML
        print("\n[STEP 5] Parsing alert rows...")
        page_source = scraper.driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        # Find all alert row elements
        alert_rows = soup.find_all('app-alerts-table-row')
        print(f"[INFO] Found {len(alert_rows)} alert row elements")

        # Parse each row
        parsed_alerts = []
        for i, row in enumerate(alert_rows, 1):
            alert_data = parse_alert_row(row)
            if alert_data:
                parsed_alerts.append(alert_data)
                print(f"  [{i}] {alert_data['ticker']}: {alert_data['status']} - {alert_data.get('pnl_percent', 0)}%")

        print(f"\n[SUCCESS] Parsed {len(parsed_alerts)} real alerts!")

        if not parsed_alerts:
            print("[ERROR] No alerts parsed")
            return 1

        # Step 6: Store in database
        print(f"\n[STEP 6] Storing {len(parsed_alerts)} alerts in database...")

        profile = db.get_profile_by_username('behappy')
        if not profile:
            print("[ERROR] behappy profile not found")
            return 1

        stored = 0
        for alert in parsed_alerts:
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
                    'ticker': alert['ticker'],
                    'strategy': alert.get('strategy', 'Unknown'),
                    'action': alert.get('action', 'Unknown'),
                    'entry_price': alert.get('entry_price'),
                    'exit_price': alert.get('exit_price'),
                    'quantity': alert.get('quantity', 1),
                    'strike_price': alert.get('strike_price'),
                    'expiration_date': alert.get('expiration_date'),
                    'alert_text': alert['alert_text'],
                    'alert_timestamp': alert_time,
                    'status': alert['status'],
                    'pnl': None,
                    'pnl_percent': alert.get('pnl_percent')
                }

                trade_id = db.add_trade(trade_data)
                stored += 1
                print(f"  [OK] Stored: {alert['ticker']} - {alert['status']} ({trade_id})")

            except Exception as e:
                print(f"  [ERROR] Failed to store: {e}")

        print(f"\n[SUCCESS] Stored {stored}/{len(parsed_alerts)} real alerts!")

        # Update profile
        db.update_profile_sync_status(profile['id'], 'success', stored)

        print("\n" + "="*70)
        print("COMPLETE - REAL ALERTS NOW IN DATABASE")
        print("="*70)
        print("\nNext:")
        print("1. Open dashboard: http://localhost:8501")
        print("2. Go to: Xtrades Watchlists")
        print("3. Select 'behappy' profile")
        print("4. View REAL alerts!")

        return 0

    except Exception as e:
        print(f"\n[ERROR] Scraping failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        scraper.close()

if __name__ == "__main__":
    sys.exit(main())
