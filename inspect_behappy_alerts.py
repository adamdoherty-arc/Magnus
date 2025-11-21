"""
Inspect BeHappy Profile - Debug Real Alert Structure
This script will login, navigate to behappy profile, and show us what's actually there
"""

import sys
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from xtrades_scraper import XtradesScraper
from selenium.webdriver.common.by import By
from dotenv import load_dotenv

load_dotenv()

def main():
    print("="*70)
    print("INSPECTING BEHAPPY PROFILE FOR REAL ALERTS")
    print("="*70)

    scraper = XtradesScraper(headless=False)  # Non-headless so we can see

    try:
        # Step 1: Login
        print("\n[STEP 1] Logging in with Discord...")
        if not scraper.login():
            print("[ERROR] Login failed")
            return 1
        print("[OK] Login successful")

        # Step 2: Navigate to behappy profile
        print("\n[STEP 2] Navigating to https://app.xtrades.net/profile/behappy")
        scraper.driver.get("https://app.xtrades.net/profile/behappy")
        time.sleep(5)

        print(f"[INFO] Page title: {scraper.driver.title}")

        # Step 3: Try to find and click Alerts tab
        print("\n[STEP 3] Looking for Alerts tab...")
        alerts_clicked = False

        selectors = [
            "//button[contains(text(), 'Alerts')]",
            "//a[contains(text(), 'Alerts')]",
            "//div[contains(text(), 'Alerts') and contains(@class, 'tab')]",
            "//*[contains(@role, 'tab') and contains(text(), 'Alerts')]"
        ]

        for selector in selectors:
            try:
                elem = scraper.driver.find_element(By.XPATH, selector)
                elem.click()
                print(f"[OK] Clicked Alerts tab")
                alerts_clicked = True
                time.sleep(3)
                break
            except:
                continue

        if not alerts_clicked:
            print("[WARN] Could not click Alerts tab, checking current page")

        # Step 4: Wait for content to load
        print("\n[STEP 4] Waiting for alerts to load (20 seconds)...")
        time.sleep(20)

        # Scroll page
        print("[INFO] Scrolling page...")
        for i in range(3):
            scraper.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

        # Step 5: Look for alert elements
        print("\n[STEP 5] Searching for alert elements...")

        # Try to find any divs that might contain alerts
        page_source = scraper.driver.page_source

        # Save full HTML
        debug_file = Path.home() / '.xtrades_cache' / 'behappy_full_inspect.html'
        debug_file.parent.mkdir(exist_ok=True)
        with open(debug_file, 'w', encoding='utf-8') as f:
            f.write(page_source)
        print(f"[OK] Saved full HTML to: {debug_file}")

        # Take screenshot
        screenshot_file = Path.home() / '.xtrades_cache' / 'behappy_screenshot.png'
        scraper.driver.save_screenshot(str(screenshot_file))
        print(f"[OK] Saved screenshot to: {screenshot_file}")

        # Try to find alert containers
        print("\n[STEP 6] Analyzing page structure...")

        # Look for various elements
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(page_source, 'html.parser')

        # Check for app-alert components
        alert_components = soup.find_all(lambda tag: tag.name and 'alert' in tag.name.lower())
        print(f"[INFO] Found {len(alert_components)} tags with 'alert' in name")

        if alert_components:
            for i, comp in enumerate(alert_components[:5], 1):
                print(f"\n  Component {i}: {comp.name}")
                text = comp.get_text(strip=True)[:200]
                print(f"    Text: {text}")

        # Check for rows
        rows = soup.find_all('div', class_=lambda c: c and ('row' in c.lower() or 'item' in c.lower()))
        print(f"\n[INFO] Found {len(rows)} potential row/item divs")

        # Look for any div with substantial text about trades
        print("\n[STEP 7] Looking for text patterns...")
        all_text = soup.get_text()

        # Look for trading keywords
        keywords = ['BTO', 'STO', 'BTC', 'STC', 'CALL', 'PUT', 'CSP', '$']
        found_keywords = []
        for keyword in keywords:
            if keyword in all_text:
                found_keywords.append(keyword)

        if found_keywords:
            print(f"[OK] Found trading keywords: {', '.join(found_keywords)}")
            print("[INFO] The page likely contains trading alerts!")
        else:
            print("[WARN] No trading keywords found - page might be empty or alerts not loaded")

        # Check for "no alerts" or "empty" messages
        empty_messages = ['no alerts', 'no data', 'empty', 'no trades found']
        for msg in empty_messages:
            if msg.lower() in all_text.lower():
                print(f"[WARN] Found message: '{msg}'")

        print("\n[STEP 8] Manual inspection...")
        print("Browser will stay open. Please:")
        print("1. Look at the browser window")
        print("2. Check if you see any alerts/trades")
        print("3. Right-click on an alert and 'Inspect Element'")
        print("4. Note the HTML structure (tag names, class names)")
        print("5. Press Enter here when done...")

        input()

        print("\n[SUCCESS] Inspection complete")
        print(f"\nFiles saved:")
        print(f"  HTML: {debug_file}")
        print(f"  Screenshot: {screenshot_file}")
        print("\nNext: Review these files to understand the alert structure")

        return 0

    except Exception as e:
        print(f"\n[ERROR] Inspection failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        # Don't close immediately
        print("\n[INFO] Keeping browser open for inspection...")
        input("Press Enter to close browser...")
        scraper.close()

if __name__ == "__main__":
    sys.exit(main())
