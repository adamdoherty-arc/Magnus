"""
Fix existing trades with missing P/L data
Extract P/L from alert_text and update database
"""
import sys
from pathlib import Path
import re

sys.path.insert(0, str(Path(__file__).parent / 'src'))
from xtrades_db_manager import XtradesDBManager

db = XtradesDBManager()

# Get all trades
trades = db.get_all_trades()
print(f"Total trades: {len(trades)}")

# Find trades with missing P/L but have alert_text
trades_to_fix = []
for t in trades:
    if t.get('pnl_percent') is None and t.get('alert_text'):
        trades_to_fix.append(t)

print(f"Trades with missing P/L: {len(trades_to_fix)}")

if not trades_to_fix:
    print("\nNo trades need fixing!")
    sys.exit(0)

print("\nExtracting P/L from alert_text...")

# P/L extraction patterns (same as scraper)
pnl_patterns = [
    (r'Made\s+([\d.]+)%', 1),
    (r'Lost\s+([\d.]+)%', -1),
    (r'Up\s+([\d.]+)%', 1),
    (r'Down\s+([\d.]+)%', -1),
]

fixed_count = 0
for t in trades_to_fix:
    alert_text = t.get('alert_text', '')

    # Try to extract P/L
    pnl_percent = None
    for pattern, sign in pnl_patterns:
        match = re.search(pattern, alert_text)
        if match:
            pnl_percent = sign * float(match.group(1))
            break

    if pnl_percent is not None:
        # Update database
        try:
            db.update_trade(t['id'], {'pnl_percent': pnl_percent})
            ticker = t.get('ticker', '?')
            profile_username = t.get('profile_username', 'unknown')
            print(f"  [OK] Trade #{t['id']}: @{profile_username} {ticker} - Updated P/L to {pnl_percent:+.1f}%")
            fixed_count += 1
        except Exception as e:
            print(f"  [ERROR] Trade #{t['id']}: {e}")

print(f"\n{fixed_count}/{len(trades_to_fix)} trades updated successfully")
