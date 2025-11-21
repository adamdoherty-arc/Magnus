"""
Test BeHappy Profile Scraping with Extended Wait Times
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from xtrades_scraper import XtradesScraper
from dotenv import load_dotenv

load_dotenv()

def main():
    print("=" * 70)
    print("TESTING BEHAPPY PROFILE WITH EXTENDED WAIT TIMES")
    print("=" * 70)

    scraper = XtradesScraper(headless=False)

    try:
        # Login
        print("\n[1] Logging in...")
        if not scraper.login():
            print("[ERROR] Login failed")
            return 1

        print("[OK] Login successful")

        # Navigate to profile
        profile_url = "https://app.xtrades.net/profile/behappy"
        print(f"\n[2] Navigating to: {profile_url}")
        scraper.driver.get(profile_url)
        time.sleep(5)

        # Check page title
        print(f"[INFO] Page title: {scraper.driver.title}")

        # Check if profile exists
        if "404" in scraper.driver.title:
            print("[ERROR] Profile not found (404)")
            return 1

        # Try to find and click Alerts tab with multiple strategies
        print("\n[3] Looking for Alerts tab...")
        alerts_clicked = False

        selectors = [
            "//button[contains(text(), 'Alerts')]",
            "//a[contains(text(), 'Alerts')]",
            "//*[contains(@class, 'tab') and contains(text(), 'Alerts')]",
            "//div[@role='tab' and contains(text(), 'Alerts')]"
        ]

        from selenium.webdriver.common.by import By

        for selector in selectors:
            try:
                elem = scraper.driver.find_element(By.XPATH, selector)
                elem.click()
                print(f"[OK] Clicked Alerts tab using: {selector[:50]}")
                alerts_clicked = True
                time.sleep(3)
                break
            except:
                continue

        if not alerts_clicked:
            print("[WARN] Could not find Alerts tab, trying direct URL")
            scraper.driver.get(f"{profile_url}/alerts")
            time.sleep(3)

        # Wait extra long for Angular to load
        print("\n[4] Waiting for alerts to load...")
        print("    (This may take 15-20 seconds for dynamic content)")
        time.sleep(15)

        # Scroll to trigger lazy loading
        print("\n[5] Scrolling to trigger content loading...")
        for i in range(5):
            scraper.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            print(f"    Scroll {i+1}/5")

        # Wait a bit more
        time.sleep(5)

        # Now try to scrape
        print("\n[6] Attempting to scrape alerts...")
        alerts = scraper.get_profile_alerts('behappy', max_alerts=20)

        if alerts:
            print(f"\n[SUCCESS] Found {len(alerts)} alerts!")
            for i, alert in enumerate(alerts[:3], 1):
                print(f"\nAlert {i}:")
                print(f"  Ticker: {alert.get('ticker')}")
                print(f"  Strategy: {alert.get('strategy')}")
                print(f"  Action: {alert.get('action')}")
                print(f"  Entry: ${alert.get('entry_price', 0):.2f}" if alert.get('entry_price') else "  Entry: N/A")
        else:
            print("\n[WARN] No alerts found")
            print("\nPossible reasons:")
            print("1. The behappy profile has no trading alerts yet")
            print("2. The profile is private or requires special access")
            print("3. The alert structure has changed and scraper needs updating")

            # Save debug HTML
            page_source = scraper.driver.page_source
            debug_file = Path.home() / '.xtrades_cache' / 'debug_behappy_extended.html'
            debug_file.parent.mkdir(exist_ok=True)
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(page_source)
            print(f"\n[INFO] Saved page HTML to: {debug_file}")
            print("        You can open this file to inspect the page content")

        # Keep browser open for manual inspection
        input("\n[INFO] Browser will remain open. Press Enter to close...")

        return 0

    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        scraper.close()

if __name__ == "__main__":
    sys.exit(main())
