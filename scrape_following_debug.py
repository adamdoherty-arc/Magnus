"""
Debug Script - Following Alerts with Login Verification
Tests login, navigation, and element finding
"""

import sys
from pathlib import Path
import time
import re
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from xtrades_scraper import XtradesScraper
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

def main():
    print("="*70)
    print("DEBUG: Following Alerts Login Test")
    print("="*70)

    scraper = XtradesScraper(headless=False)

    try:
        # Step 1: Login
        print("\n[STEP 1] Logging in...")
        if not scraper.login():
            print("[ERROR] Login failed")
            return 1
        print("[OK] Logged in")

        # Verify login by checking for profile menu
        print("\n[STEP 2] Verifying login...")
        time.sleep(3)
        page_source = scraper.driver.page_source

        if 'Sign in' in page_source:
            print("[ERROR] Still seeing 'Sign in' button - NOT logged in!")
            print("[ACTION] Need to fix authentication")
            return 1
        else:
            print("[OK] Login verified - no 'Sign in' button")

        # Navigate to alerts
        print("\n[STEP 3] Navigating to alerts page...")
        scraper.driver.get("https://app.xtrades.net/alerts")
        time.sleep(8)

        # Check if logged in after navigation
        page_source = scraper.driver.page_source
        if 'Sign in' in page_source:
            print("[ERROR] Lost session after navigation!")
            return 1
        print("[OK] Still logged in")

        # Try to find and click Following tab
        print("\n[STEP 4] Looking for Following tab...")
        try:
            wait = WebDriverWait(scraper.driver, 10)

            # Try different selectors
            following_btn = None
            selectors = [
                "//button[contains(text(), 'Following')]",
                "//ion-button[contains(text(), 'Following')]",
                "//*[contains(text(), 'Following')]",
            ]

            for selector in selectors:
                try:
                    following_btn = scraper.driver.find_element(By.XPATH, selector)
                    print(f"[OK] Found Following button with selector: {selector}")
                    break
                except:
                    continue

            if following_btn:
                following_btn.click()
                print("[OK] Clicked Following tab")
                time.sleep(5)
            else:
                print("[WARN] Could not find Following tab")

        except Exception as e:
            print(f"[WARN] Following tab error: {e}")

        # Look for toggle
        print("\n[STEP 5] Looking for 'Open alerts only' toggle...")
        try:
            toggles = scraper.driver.find_elements(By.XPATH, "//ion-toggle")
            print(f"[INFO] Found {len(toggles)} ion-toggle elements")

            for i, toggle in enumerate(toggles):
                is_checked = toggle.get_attribute('aria-checked')
                print(f"  Toggle {i+1}: aria-checked={is_checked}")

                # If any toggle is checked, try to click it
                if is_checked == 'true':
                    print(f"[ACTION] Clicking toggle {i+1} to turn OFF")
                    toggle.click()
                    time.sleep(3)

        except Exception as e:
            print(f"[WARN] Toggle error: {e}")

        # Wait for content
        print("\n[STEP 6] Waiting 15 seconds for alerts to load...")
        time.sleep(15)

        # Scroll
        print("\n[STEP 7] Scrolling...")
        for i in range(5):
            scraper.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
        scraper.driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)

        # Get HTML and check content
        print("\n[STEP 8] Analyzing page content...")
        page_source = scraper.driver.page_source

        # Save
        html_file = Path.home() / '.xtrades_cache' / 'following_debug.html'
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(page_source)
        print(f"[INFO] Saved HTML: {html_file}")

        # Check for key content
        checks = [
            ('HIMS', 'HIMS ticker'),
            ('Opened', 'Opened status'),
            ('Closed', 'Closed status'),
            ('Bought', 'Bought action'),
            ('Sold', 'Sold action'),
            ('Shorted', 'Shorted action'),
            ('@', 'Username'),
        ]

        for text, label in checks:
            if text in page_source:
                print(f"[SUCCESS] Found {label}: '{text}'")
            else:
                print(f"[WARN] Missing {label}: '{text}'")

        # Parse alerts
        soup = BeautifulSoup(page_source, 'html.parser')
        alert_rows = soup.find_all('app-alerts-table-row')
        print(f"\n[INFO] Found {len(alert_rows)} app-alerts-table-row elements")

        if alert_rows:
            print("\nFirst alert row HTML sample:")
            print(str(alert_rows[0])[:500])

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
