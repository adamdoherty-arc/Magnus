"""Show complete HTML examples of real alerts"""

from bs4 import BeautifulSoup
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\Asus\.xtrades_cache\debug_behappy_page.html', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

print("=" * 80)
print("COMPLETE ALERT HTML EXAMPLES")
print("=" * 80)

# Get all app-post elements
posts = soup.find_all('app-post')

print(f"\nTotal app-post elements found: {len(posts)}\n")

for i, post in enumerate(posts, 1):
    print(f"\n{'#' * 80}")
    print(f"ALERT EXAMPLE #{i}")
    print('#' * 80)

    # Show text content
    text = post.get_text(strip=True)
    print(f"\nText Content ({len(text)} characters):")
    print("-" * 80)
    print(text[:300])
    print("-" * 80)

    # Show HTML structure (formatted)
    print(f"\nFull HTML Structure:")
    print("-" * 80)
    print(post.prettify()[:1500])
    print("...")
    print("-" * 80)

    # Extract key fields
    print(f"\nKey Fields:")
    print("-" * 80)

    # Find ticker symbols
    import re
    tickers = re.findall(r'\$([A-Z]{1,5})\b', text)
    if tickers:
        print(f"  Tickers: {', '.join(set(tickers))}")

    # Find username
    username_elem = post.find('span', class_=None)
    if username_elem and '@' in username_elem.text:
        print(f"  Username: {username_elem.text.strip()}")

    # Find display name
    displayname_elem = post.find('div', class_='post__header__details__author__displayname')
    if displayname_elem:
        print(f"  Display Name: {displayname_elem.text.strip()}")

    # Find X-score
    xscore_elem = post.find('div', class_='avatar__xscore')
    if xscore_elem:
        print(f"  X-Score: {xscore_elem.text.strip()}")

    # Find timestamp
    time_match = re.search(r'(\d+[mhd])\s+ago', text)
    if time_match:
        print(f"  Posted: {time_match.group(0)}")

    # Find trade actions
    actions = []
    for action in ['BTO', 'STC', 'BTC', 'STO']:
        if action in text:
            actions.append(action)
    if actions:
        print(f"  Actions: {', '.join(actions)}")

    # Find strategies
    strategies = []
    for strategy in ['CSP', 'CC', 'Put', 'Call']:
        if strategy in text:
            strategies.append(strategy)
    if strategies:
        print(f"  Strategies: {', '.join(strategies)}")

    print("-" * 80)

# Show the correct selector
print(f"\n\n{'=' * 80}")
print("CORRECT SELECTOR")
print('=' * 80)
print("\nPython Code:")
print("-" * 80)
print("alerts = soup.find_all('app-post')")
print("-" * 80)

print(f"\nThis will find: {len(posts)} alert elements")
print("\nCompare to current selector:")
print("  soup.find_all(name=re.compile(r'app-.*alert.*', re.I))")
print(f"  Finds: {len(soup.find_all(name=re.compile(r'app-.*alert.*', re.I)))} elements (containers only)")

# Show extraction example
print(f"\n\n{'=' * 80}")
print("FIELD EXTRACTION GUIDE")
print('=' * 80)

print("""
For each <app-post> element:

1. TICKER:
   - Find: $TICKER pattern in text
   - Code: re.findall(r'\\$([A-Z]{1,5})\\b', text)

2. USERNAME:
   - Find: <span> with @ character
   - Code: post.find('span', class_=None, string=re.compile(r'@\\w+'))

3. DISPLAY NAME:
   - Find: div.post__header__details__author__displayname
   - Code: post.find('div', class_='post__header__details__author__displayname')

4. X-SCORE:
   - Find: div.avatar__xscore
   - Code: post.find('div', class_='avatar__xscore')

5. TIMESTAMP:
   - Find: "Xm ago", "Xh ago", "Xd ago" pattern
   - Code: re.search(r'(\\d+[mhd])\\s+ago', text)

6. TRADE TEXT:
   - Find: app-quill-text element
   - Code: post.find('app-quill-text')

7. ACTIONS:
   - Find: BTO, STC, BTC, STO in text
   - Code: re.findall(r'\\b(BTO|STC|BTC|STO)\\b', text, re.I)

8. STRATEGY:
   - Find: CSP, CC, Put, Call, etc.
   - Code: re.search(r'\\b(CSP|CC|Put|Call|Spread)\\b', text, re.I)
""")

print("=" * 80)
