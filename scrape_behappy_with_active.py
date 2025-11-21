"""
Scrape BOTH Active AND Closed Alerts - Fixed
This will look for both "Opened" and "Closed" alerts
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
    """Parse a single alert row"""
    try:
        result = {
            'ticker': None,
            'status': 'unknown',
            'pnl_percent': None,
            'alert_timestamp': None,
            'alert_text': '',
        }

        # Extract ticker from image
        img = row_element.find('img', {'src': lambda x: x and 'logo' in x})
        if img and img.get('src'):
            src = img['src']
            ticker = src.split('/')[-1].replace('.png', '').upper()
            result['ticker'] = ticker

        # Extract age
        age_div = row_element.find('div', class_=lambda x: x and 'company__pill' in x)
        if age_div:
            age_text = age_div.get_text(strip=True)
            result['alert_text'] = f"{age_text} - "

        # Extract status - LOOK FOR BOTH "Opened" AND "Closed"
        time_spans = row_element.find_all('span', class_='time-profile')
        for span in time_spans:
            text = span.get_text(strip=True)
            result['alert_text'] += text + " "
            if 'Closed' in text:
                result['status'] = 'closed'
            elif 'Opened' in text:
                result['status'] = 'open'  # This is the key difference!

        # Extract P/L
        result_div = row_element.find('app-alert-result')
        if result_div:
            result_text = result_div.get_text(strip=True)
            result['alert_text'] += result_text + " "

            if 'Made' in result_text:
                match = re.search(r'Made\s+([\d.]+)%', result_text)
                if match:
                    result['pnl_percent'] = float(match.group(1))
            elif 'Lost' in result_text:
                match = re.search(r'Lost\s+([\d.]+)%', result_text)
                if match:
                    result['pnl_percent'] = -float(match.group(1))
            elif 'DOWN' in result_text:
                # For active trades showing "DOWN X%"
                match = re.search(r'DOWN\s+([\d.]+)%', result_text)
                if match:
                    result['pnl_percent'] = -float(match.group(1))
            elif 'UP' in result_text:
                match = re.search(r'UP\s+([\d.]+)%', result_text)
                if match:
                    result['pnl_percent'] = float(match.group(1))

        # Timestamp
        if age_div:
            age_text = age_div.get_text(strip=True)
            days_match = re.search(r'(\d+)d', age_text)
            hours_match = re.search(r'(\d+)h', age_text)

            if days_match:
                days_ago = int(days_match.group(1))
                result['alert_timestamp'] = (datetime.now() - timedelta(days=days_ago)).isoformat()
            elif hours_match:
                hours_ago = int(hours_match.group(1))
                result['alert_timestamp'] = (datetime.now() - timedelta(hours=hours_ago)).isoformat()
            else:
                result['alert_timestamp'] = datetime.now().isoformat()
        else:
            result['alert_timestamp'] = datetime.now().isoformat()

        result['alert_text'] = result['alert_text'].strip()

        if result['ticker']:
            return result

        return None

    except Exception as e:
        print(f"[ERROR] Failed to parse row: {e}")
        return None

def main():
    print("="*70)
    print("SCRAPING ACTIVE + CLOSED ALERTS")
    print("="*70)

    scraper = XtradesScraper(headless=False)
    db = XtradesDBManager()

    try:
        # Login
        print("\n[STEP 1] Logging in...")
        if not scraper.login():
            return 1
        print("[OK] Logged in")

        # Navigate
        print("\n[STEP 2] Navigating to behappy profile...")
        scraper.driver.get("https://app.xtrades.net/profile/behappy")
        time.sleep(5)

        # Check for tabs or filters
        print("\n[STEP 3] Looking for Alerts tab...")
        try:
            # Try to click Alerts tab
            alerts_tab = scraper.driver.find_element(By.XPATH, "//*[contains(text(), 'Alerts')]")
            alerts_tab.click()
            print("[OK] Clicked Alerts tab")
            time.sleep(3)
        except:
            print("[INFO] No Alerts tab found, continuing...")

        # Wait longer
        print("\n[STEP 4] Waiting 40 seconds for content...")
        time.sleep(40)

        # Scroll UP first (active trades might be at top)
        print("\n[STEP 5] Scrolling UP to find active trades...")
        for i in range(3):
            scraper.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(2)

        # Then scroll down
        print("\n[STEP 6] Scrolling DOWN...")
        for i in range(5):
            scraper.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)

        # Scroll back to top
        scraper.driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(3)

        # Take screenshot
        screenshot_file = Path.home() / '.xtrades_cache' / 'behappy_with_active.png'
        scraper.driver.save_screenshot(str(screenshot_file))
        print(f"[INFO] Screenshot saved: {screenshot_file}")

        # Get HTML
        print("\n[STEP 7] Parsing HTML...")
        page_source = scraper.driver.page_source

        # Save HTML
        html_file = Path.home() / '.xtrades_cache' / 'behappy_with_active.html'
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(page_source)
        print(f"[INFO] HTML saved: {html_file}")

        # Check if HIMS is there
        if 'HIMS' in page_source.upper():
            print("[SUCCESS] Found HIMS in HTML!")
        else:
            print("[ERROR] HIMS not found in HTML")
            print("[ACTION] Check screenshot to see what page shows")

        # Check for "Opened" text
        if 'Opened' in page_source:
            print("[SUCCESS] Found 'Opened' text - active trades present!")
        else:
            print("[WARN] No 'Opened' text found")

        # Parse
        soup = BeautifulSoup(page_source, 'html.parser')
        alert_rows = soup.find_all('app-alerts-table-row')
        print(f"\n[INFO] Found {len(alert_rows)} alert rows")

        parsed_alerts = []
        for i, row in enumerate(alert_rows, 1):
            alert_data = parse_alert_row(row)
            if alert_data:
                parsed_alerts.append(alert_data)
                status_label = "ACTIVE" if alert_data['status'] == 'open' else "CLOSED"
                print(f"  [{i}] {alert_data['ticker']}: {status_label} - {alert_data.get('pnl_percent', 0)}%")

        print(f"\n[SUCCESS] Parsed {len(parsed_alerts)} alerts")

        # Count by status
        active_count = sum(1 for a in parsed_alerts if a['status'] == 'open')
        closed_count = sum(1 for a in parsed_alerts if a['status'] == 'closed')
        print(f"  Active: {active_count}")
        print(f"  Closed: {closed_count}")

        if active_count == 0:
            print("\n[PROBLEM] No active trades found!")
            print("[ACTION] Check screenshot and HTML files")
            print(f"  Screenshot: {screenshot_file}")
            print(f"  HTML: {html_file}")

        # Store
        print(f"\n[STEP 8] Storing {len(parsed_alerts)} alerts...")
        profile = db.get_profile_by_username('behappy')

        stored = 0
        for alert in parsed_alerts:
            try:
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
                print(f"  [OK] Stored: {alert['ticker']} - {status_label} (ID: {trade_id})")

            except Exception as e:
                print(f"  [ERROR] Failed: {e}")

        print(f"\n[COMPLETE] Stored {stored}/{len(parsed_alerts)} alerts")

        db.update_profile_sync_status(profile['id'], 'success', stored)

        return 0

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        input("\n[WAIT] Press Enter to close browser...")
        scraper.close()

if __name__ == "__main__":
    sys.exit(main())
