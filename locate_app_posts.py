"""Find where app-post elements are located"""

from bs4 import BeautifulSoup
import re
import sys

# Use UTF-8 for output
sys.stdout.reconfigure(encoding='utf-8')

# Read HTML
with open(r'C:\Users\Asus\.xtrades_cache\debug_behappy_page.html', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

print("=" * 80)
print("LOCATING APP-POST ELEMENTS")
print("=" * 80)

# Find all app-post elements
app_posts = soup.find_all('app-post')
print(f"\nTotal app-post elements found: {len(app_posts)}")

# Check what tab/container they're in
for i, post in enumerate(app_posts, 1):
    print(f"\n--- APP-POST #{i} ---")

    # Get parent hierarchy
    print("Parent hierarchy:")
    parent = post.parent
    depth = 0
    while parent and depth < 10:
        parent_name = parent.name
        parent_classes = parent.get('class', [])
        print(f"  {'  ' * depth}^ {parent_name} classes={parent_classes}")

        # Check if this is a tab container
        if parent_name and 'tab' in parent_name.lower():
            print(f"    >>> FOUND IN TAB: {parent_name}")

        parent = parent.parent
        depth += 1

    # Get text content sample
    text = post.get_text(strip=True)
    print(f"\nText sample (first 150 chars):")
    print(f"  {text[:150]}")

# Also check the Alerts tab to see what IS inside it
print("\n\n" + "=" * 80)
print("CHECKING APP-ALERTS-TAB CONTENTS")
print("=" * 80)

alerts_tab = soup.find('app-alerts-tab')
if alerts_tab:
    print("\nFound app-alerts-tab")

    # Get all immediate children
    children = list(alerts_tab.children)
    print(f"Immediate children: {len([c for c in children if hasattr(c, 'name')])}")

    for child in children:
        if hasattr(child, 'name') and child.name:
            print(f"  - {child.name} classes={child.get('class', [])}")

    # Get ALL descendants
    all_descendants = alerts_tab.find_all()
    print(f"\nTotal descendants: {len(all_descendants)}")

    # Show unique tags
    tags = {}
    for desc in all_descendants:
        tags[desc.name] = tags.get(desc.name, 0) + 1

    print("\nDescendant tag distribution (top 20):")
    for tag, count in sorted(tags.items(), key=lambda x: x[1], reverse=True)[:20]:
        print(f"  {tag}: {count}")

    # Check if there are any elements with actual trade text
    print("\nSearching for elements with trade keywords inside alerts-tab...")
    trade_keywords = ['BTO', 'STC', '$', 'CSP', 'CC']
    found_trade_elements = 0

    for desc in all_descendants:
        text = desc.get_text(strip=True)
        if any(kw in text for kw in trade_keywords) and len(text) > 20 and len(text) < 500:
            found_trade_elements += 1
            if found_trade_elements <= 3:  # Show first 3
                print(f"\n  Element: {desc.name} classes={desc.get('class', [])}")
                print(f"    Text: {text[:100]}")

    print(f"\nTotal elements with trade keywords: {found_trade_elements}")

else:
    print("ERROR: app-alerts-tab not found!")

# Check other tab types
print("\n\n" + "=" * 80)
print("ALL TAB ELEMENTS IN PAGE")
print("=" * 80)

all_tabs = soup.find_all(name=re.compile(r'app-.*tab', re.I))
print(f"\nFound {len(all_tabs)} tab elements:")
for tab in all_tabs:
    print(f"  - {tab.name}")

    # Check if it has app-post children
    posts_inside = tab.find_all('app-post')
    if posts_inside:
        print(f"    >>> Contains {len(posts_inside)} app-post elements!")

print("\n" + "=" * 80)
