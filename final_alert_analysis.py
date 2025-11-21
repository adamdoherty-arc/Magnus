"""Final comprehensive alert HTML analysis - outputs to file"""

from bs4 import BeautifulSoup
import re

# Read HTML
with open(r'C:\Users\Asus\.xtrades_cache\debug_behappy_page.html', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

# Output file
output = []

def write(text):
    output.append(text)
    print(text)

write("=" * 80)
write("COMPREHENSIVE ALERT HTML STRUCTURE ANALYSIS")
write("=" * 80)

# 1. Current failing selector
write("\n### 1. CURRENT FAILING SELECTOR ###")
failing_selector = soup.find_all(name=re.compile(r'app-.*alert.*', re.I))
write(f"Selector: soup.find_all(name=re.compile(r'app-.*alert.*', re.I))")
write(f"Total elements found: {len(failing_selector)}")

tag_breakdown = {}
for elem in failing_selector:
    tag_breakdown[elem.name] = tag_breakdown.get(elem.name, 0) + 1

write("\nTag breakdown:")
for tag, count in sorted(tag_breakdown.items(), key=lambda x: x[1], reverse=True):
    write(f"  {tag}: {count}")

write("\nWHY IT FAILS:")
write("  - These are CONTAINER elements (app-alerts-tab, app-alerts-table-header-profile)")
write("  - They don't contain the actual trade data directly")
write("  - The real alerts are NESTED INSIDE these containers")

# 2. Find actual alert elements
write("\n\n### 2. FINDING REAL ALERT ELEMENTS ###")
write("Looking for elements with: ticker symbol + dollar sign + reasonable length")

# First, check what's inside the alerts container
alerts_tab = soup.find('app-alerts-tab')
if alerts_tab:
    write(f"\nFound app-alerts-tab container")

    # Try app-post elements (from previous output we saw 3 app-post elements)
    app_posts = alerts_tab.find_all('app-post')
    write(f"\n  app-post elements inside alerts-tab: {len(app_posts)}")

    # Try divs with class 'post'
    post_divs = alerts_tab.find_all('div', class_='post')
    write(f"  div.post elements inside alerts-tab: {len(post_divs)}")

    # Try divs with 'ng-star-inserted' class
    ng_divs = alerts_tab.find_all('div', class_='ng-star-inserted')
    write(f"  div.ng-star-inserted elements: {len(ng_divs)}")

# 3. Analyze elements with actual trade data
write("\n\n### 3. ELEMENTS WITH TRADE DATA ###")
all_elements = soup.find_all()
real_alerts = []

for elem in all_elements:
    text = elem.get_text(strip=True)
    # Must have: uppercase ticker AND dollar sign AND reasonable length
    has_ticker = bool(re.search(r'\b[A-Z]{2,5}\b', text))
    has_price = '$' in text
    reasonable_length = 20 < len(text) < 500

    if has_ticker and has_price and reasonable_length:
        real_alerts.append(elem)

write(f"Total elements with ticker + price + reasonable length: {len(real_alerts)}")

# Get tag distribution
tag_dist = {}
for elem in real_alerts:
    tag_dist[elem.name] = tag_dist.get(elem.name, 0) + 1

write("\nTag distribution:")
for tag, count in sorted(tag_dist.items(), key=lambda x: x[1], reverse=True):
    write(f"  {tag}: {count}")

# 4. Show detailed examples
write("\n\n### 4. DETAILED ALERT EXAMPLES ###")

for i, elem in enumerate(real_alerts[:5], 1):
    write(f"\n{'=' * 70}")
    write(f"ALERT EXAMPLE #{i}")
    write('=' * 70)
    write(f"Tag: {elem.name}")
    write(f"Classes: {elem.get('class', [])}")
    write(f"ID: {elem.get('id', 'None')}")

    text = elem.get_text(strip=True)
    write(f"\nText content ({len(text)} chars):")
    write(text[:200])

    write(f"\nHTML structure:")
    write(str(elem)[:1000])

    # Show parent hierarchy
    write(f"\nParent hierarchy:")
    parent = elem.parent
    depth = 0
    while parent and depth < 5:
        parent_classes = parent.get('class', [])
        write(f"  {'  ' * depth}^ {parent.name} {parent_classes}")
        parent = parent.parent
        depth += 1

# 5. Find the best selector
write("\n\n### 5. RECOMMENDED SELECTOR ###")

# Check if app-post is reliable
app_post_elements = soup.find_all('app-post')
write(f"\nOption 1: soup.find_all('app-post')")
write(f"  Total found: {len(app_post_elements)}")
if app_post_elements:
    has_trade_data = 0
    for elem in app_post_elements:
        text = elem.get_text(strip=True)
        if '$' in text and re.search(r'\b[A-Z]{2,5}\b', text):
            has_trade_data += 1
    write(f"  With trade data: {has_trade_data}")

# Check divs with 'post' class
post_divs = soup.find_all('div', class_='post')
write(f"\nOption 2: soup.find_all('div', class_='post')")
write(f"  Total found: {len(post_divs)}")
if post_divs:
    has_trade_data = 0
    for elem in post_divs:
        text = elem.get_text(strip=True)
        if '$' in text and re.search(r'\b[A-Z]{2,5}\b', text):
            has_trade_data += 1
    write(f"  With trade data: {has_trade_data}")

# Check divs with 'post' AND 'ng-star-inserted' class
post_ng_divs = soup.find_all('div', class_=['post', 'ng-star-inserted'])
write(f"\nOption 3: soup.find_all('div', class_=['post', 'ng-star-inserted'])")
write(f"  Total found: {len(post_ng_divs)}")
if post_ng_divs:
    has_trade_data = 0
    for elem in post_ng_divs:
        text = elem.get_text(strip=True)
        if '$' in text and re.search(r'\b[A-Z]{2,5}\b', text):
            has_trade_data += 1
    write(f"  With trade data: {has_trade_data}")

# 6. Final recommendation
write("\n\n### 6. FINAL RECOMMENDATION ###")
write("\nBest selector: soup.find_all('app-post')")
write("\nWhy:")
write("  - Semantic: 'app-post' is the Angular component for individual posts/alerts")
write("  - Specific: Not too broad like 'div'")
write("  - Reliable: All app-post elements should contain alert data")
write("\nUpdate in xtrades_scraper.py line 584:")
write("  FROM: {'name': re.compile(r'app-.*alert.*', re.I)},")
write("  TO:   {'name': 'app-post'},")

write("\n" + "=" * 80)
write("ANALYSIS COMPLETE")
write("=" * 80)

# Write to file
with open(r'C:\Code\WheelStrategy\ALERT_STRUCTURE_ANALYSIS.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))

print("\n\nOutput saved to: ALERT_STRUCTURE_ANALYSIS.txt")
