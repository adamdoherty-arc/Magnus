"""Compare Alerts Tab vs Feed Tab content"""

from bs4 import BeautifulSoup
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\Asus\.xtrades_cache\debug_behappy_page.html', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

print("=" * 80)
print("ALERTS TAB vs FEED TAB COMPARISON")
print("=" * 80)

# Check Alerts Tab
print("\n### APP-ALERTS-TAB ###")
alerts_tab = soup.find('app-alerts-tab')
if alerts_tab:
    print("Found alerts tab")
    print(f"Total descendants: {len(alerts_tab.find_all())}")

    # Get full HTML (first 2000 chars)
    print("\nFull HTML of alerts tab (first 2000 chars):")
    print(str(alerts_tab)[:2000])
else:
    print("NOT FOUND")

# Check Feed Tab
print("\n\n" + "=" * 80)
print("### APP-FEED-TAB ###")
feed_tab = soup.find('app-feed-tab')
if feed_tab:
    print("Found feed tab")
    print(f"Total descendants: {len(feed_tab.find_all())}")

    # Check for posts
    posts = feed_tab.find_all('app-post')
    print(f"app-post elements: {len(posts)}")

    # Get first post's text
    if posts:
        print("\nFirst post text:")
        print(posts[0].get_text(strip=True)[:300])

    # Get full HTML (first 2000 chars)
    print("\n\nFull HTML of feed tab (first 2000 chars):")
    print(str(feed_tab)[:2000])
else:
    print("NOT FOUND")

# Check Activity Tab
print("\n\n" + "=" * 80)
print("### APP-ACTIVITY-TAB ###")
activity_tab = soup.find('app-activity-tab')
if activity_tab:
    print("Found activity tab")
    print(f"Total descendants: {len(activity_tab.find_all())}")

    # Check for posts or alerts
    posts = activity_tab.find_all('app-post')
    print(f"app-post elements: {len(posts)}")

    # Get full HTML (first 2000 chars)
    print("\nFull HTML of activity tab (first 1500 chars):")
    print(str(activity_tab)[:1500])
else:
    print("NOT FOUND")

# Summary
print("\n\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print("\nThe scraper is clicking on 'Alerts' tab, which shows app-alerts-tab")
print("However, the actual trade alerts (app-post elements) are in app-feed-tab!")
print("\nPossible explanations:")
print("  1. 'Alerts' tab might be empty or show a different view")
print("  2. 'Feed' tab contains the chronological list of posts/alerts")
print("  3. The tab click logic might need to click 'Feed' instead of 'Alerts'")

print("\nRECOMMENDATION:")
print("  Update scraper to click 'Feed' or 'Activity' tab instead of 'Alerts'")
print("  OR scrape from the default tab (might be Feed)")
