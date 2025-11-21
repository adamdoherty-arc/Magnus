"""Quick check of database contents"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))
from xtrades_db_manager import XtradesDBManager

db = XtradesDBManager()

# Get all trades
trades = db.get_all_trades()
print(f"Total trades in database: {len(trades)}")

# Count by status
open_trades = [t for t in trades if t.get('status') == 'open']
closed_trades = [t for t in trades if t.get('status') == 'closed']
print(f"Open trades: {len(open_trades)}")
print(f"Closed trades: {len(closed_trades)}")

# Show recent trades
print("\nRecent trades:")
for t in trades[-10:]:
    profile = t.get('profile_username', 'unknown')
    action = t.get('action', '?')
    ticker = t.get('ticker', '?')
    status = t.get('status', 'unknown').upper()
    pnl = t.get('pnl_percent', 0) or 0
    print(f"  - @{profile}: {action} {ticker} - {status} - {pnl:+.1f}%")
