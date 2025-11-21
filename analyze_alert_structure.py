"""Analyze alert HTML structure"""

from bs4 import BeautifulSoup
import re

with open(r'C:\Users\Asus\.xtrades_cache\debug_behappy_page.html', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

# Find the alerts container
alerts_container = soup.find('app-alerts-tab')

if alerts_container:
    print("Found app-alerts-tab container")

    # Get all child elements
    all_children = alerts_container.find_all()

    print(f"\nTotal child elements: {len(all_children)}")

    # Look for elements with 'row' in class or tag name
    row_elements = [e for e in all_children if ('row' in str(e.get('class', [])).lower() or 'row' in e.name.lower())]

    print(f"\nFound {len(row_elements)} elements with 'row' in name/class:")
    for i, elem in enumerate(row_elements[:20], 1):
        text = elem.get_text(strip=True)
        classes = elem.get('class', [])
        print(f"\n{i}. Tag: {elem.name}")
        print(f"   Classes: {classes}")
        print(f"   Text ({len(text)} chars): {text[:150]}...")

        # Check if this looks like an alert (has ticker-like pattern)
        if re.search(r'\b[A-Z]{2,5}\b', text) and len(text) > 50:
            print(f"   >>> POTENTIAL ALERT! <<<")
else:
    print("Could not find app-alerts-tab container")

# Also search for any component that might be an alert row
print("\n\n=== SEARCHING FOR ALERT COMPONENTS ===")
alert_row_tags = soup.find_all(name=re.compile(r'app.*row', re.I))
print(f"Found {len(alert_row_tags)} elements with 'app.*row' pattern:")
for i, elem in enumerate(alert_row_tags[:10], 1):
    print(f"\n{i}. Tag: {elem.name}")
    print(f"   Text: {elem.get_text(strip=True)[:100]}...")
