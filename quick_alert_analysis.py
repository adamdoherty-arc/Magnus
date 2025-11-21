"""Quick analysis of alert HTML structure"""

from bs4 import BeautifulSoup
import re

# Read HTML
with open(r'C:\Users\Asus\.xtrades_cache\debug_behappy_page.html', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

print("=" * 80)
print("QUICK ALERT ANALYSIS")
print("=" * 80)

# 1. Find all app-* tags
print("\n1. ALL APP-* TAGS:")
all_app_tags = soup.find_all(name=re.compile(r'^app-', re.I))
tag_counts = {}
for tag in all_app_tags:
    tag_counts[tag.name] = tag_counts.get(tag.name, 0) + 1

for tag_name, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"   {tag_name}: {count}")

# 2. Find elements with 'alert' in name
print("\n2. ELEMENTS WITH 'ALERT' IN TAG NAME:")
alert_tags = soup.find_all(name=re.compile(r'alert', re.I))
alert_counts = {}
for tag in alert_tags:
    alert_counts[tag.name] = alert_counts.get(tag.name, 0) + 1

for tag_name, count in sorted(alert_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"   {tag_name}: {count}")

# 3. Check the current failing selector
failing_selector = soup.find_all(name=re.compile(r'app-.*alert.*', re.I))
print(f"\n3. CURRENT SELECTOR (app-.*alert.*): Found {len(failing_selector)} elements")

# Check how many have actual trade content
trade_keywords = ['BTO', 'STC', 'BTC', 'STO', 'CSP', 'CC', '$']
elements_with_trade_data = 0
for elem in failing_selector:
    text = elem.get_text(strip=True)
    if any(keyword in text for keyword in trade_keywords):
        elements_with_trade_data += 1

print(f"   Elements with trade keywords: {elements_with_trade_data}")
print(f"   Elements WITHOUT trade data: {len(failing_selector) - elements_with_trade_data}")

# 4. Find elements that actually contain ticker + price
print("\n4. ELEMENTS WITH TICKER PATTERN + DOLLAR SIGN:")
all_elements = soup.find_all()
real_alerts = []

for elem in all_elements:
    text = elem.get_text(strip=True)
    # Must have: uppercase ticker AND dollar sign AND reasonable length
    has_ticker = bool(re.search(r'\b[A-Z]{2,5}\b', text))
    has_price = '$' in text
    reasonable_length = 20 < len(text) < 500

    if has_ticker and has_price and reasonable_length:
        real_alerts.append({
            'tag': elem.name,
            'text': text,
            'length': len(text),
            'classes': elem.get('class', [])
        })

print(f"   Found {len(real_alerts)} elements with ticker + price")

# Get unique tag names
unique_real_alert_tags = {}
for alert in real_alerts:
    tag_name = alert['tag']
    unique_real_alert_tags[tag_name] = unique_real_alert_tags.get(tag_name, 0) + 1

print("\n   Tag distribution for REAL alerts:")
for tag_name, count in sorted(unique_real_alert_tags.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f"      {tag_name}: {count}")

# 5. Show examples of real alerts
print("\n5. EXAMPLE REAL ALERTS (first 3):")
for i, alert in enumerate(real_alerts[:3], 1):
    print(f"\n   --- EXAMPLE {i} ---")
    print(f"   Tag: {alert['tag']}")
    print(f"   Classes: {alert['classes']}")
    # Use ascii encoding to avoid unicode issues
    safe_text = alert['text'][:150].encode('ascii', 'replace').decode('ascii')
    print(f"   Text ({alert['length']} chars): {safe_text}...")

    # Get full HTML (first 800 chars)
    matching_elem = soup.find(alert['tag'], class_=alert['classes'][0] if alert['classes'] else None)
    if matching_elem:
        print(f"   HTML (first 800 chars):")
        safe_html = str(matching_elem)[:800].encode('ascii', 'replace').decode('ascii')
        print(f"   {safe_html}")

# 6. Try to find the common parent
print("\n6. RECOMMENDATION:")
if unique_real_alert_tags:
    most_common_tag = max(unique_real_alert_tags.items(), key=lambda x: x[1])
    print(f"\n   Most common tag for real alerts: '{most_common_tag[0]}' ({most_common_tag[1]} occurrences)")
    print(f"\n   RECOMMENDED SELECTOR:")
    print(f"      soup.find_all('{most_common_tag[0]}')")
    print(f"\n   Or with BeautifulSoup syntax:")
    print(f"      elements = soup.find_all('{most_common_tag[0]}')")
else:
    print("\n   Could not identify a specific tag pattern!")

print("\n" + "=" * 80)
