"""
Test the fixed parser on already-saved HTML
"""
import sys
from pathlib import Path
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent / 'src'))

def parse_alert_row_FIXED(row):
    """Parse with FIXED text extraction (with spaces)"""
    try:
        # FIXED: Use separator=' ' to add spaces!
        full_text = row.get_text(separator=' ', strip=True)

        result = {
            'ticker': None,
            'profile_username': None,
            'action': None,
            'status': 'unknown',
            'pnl_percent': None,
        }

        # Extract username
        username_match = re.search(r'@(\w+)', full_text)
        if username_match:
            result['profile_username'] = username_match.group(1)

        # Extract action and ticker
        actions = ['Bought', 'Sold', 'Shorted', 'Covered', 'Rolled']
        for action in actions:
            if action in full_text:
                result['action'] = action
                ticker_match = re.search(rf'{action}\s+([A-Z]{{1,5}})\s', full_text)
                if ticker_match:
                    result['ticker'] = ticker_match.group(1)
                break

        # Extract status
        if 'Opened' in full_text:
            result['status'] = 'open'
        elif 'Closed' in full_text:
            result['status'] = 'closed'

        # Extract P/L
        pnl_patterns = [
            (r'Made\s+([\d.]+)%', 1),
            (r'Lost\s+([\d.]+)%', -1),
            (r'Up\s+([\d.]+)%', 1),
            (r'Down\s+([\d.]+)%', -1),
        ]
        for pattern, sign in pnl_patterns:
            match = re.search(pattern, full_text)
            if match:
                result['pnl_percent'] = sign * float(match.group(1))
                break

        if result['ticker']:
            return result, full_text
        return None, full_text

    except Exception as e:
        return None, str(e)

# Load saved HTML
html_file = Path.home() / '.xtrades_cache' / 'cookies_scrape.html'
print(f"Loading: {html_file}")

with open(html_file, 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')
alert_rows = soup.find_all('app-alerts-table-row')

print(f"\nFound {len(alert_rows)} alert rows")
print("\nTesting FIXED parser:")
print("="*70)

parsed = 0
failed = 0

for i, row in enumerate(alert_rows[:5], 1):  # Test first 5
    result, text = parse_alert_row_FIXED(row)

    print(f"\n[{i}] Text (first 100 chars): {text[:100]}...")

    if result:
        parsed += 1
        print(f"    [OK] PARSED: @{result['profile_username']} - {result['action']} {result['ticker']} - {result['status'].upper()} - {result.get('pnl_percent', 0):+.1f}%")
    else:
        failed += 1
        print(f"    [FAIL] Could not parse")

print(f"\n{'='*70}")
print(f"Results: {parsed} parsed, {failed} failed out of 5 tested")
