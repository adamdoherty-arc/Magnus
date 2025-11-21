"""Check profiles and their recent trades"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))
from xtrades_db_manager import XtradesDBManager

db = XtradesDBManager()

# Get all profiles
profiles = db.get_all_profiles()
print(f"Total profiles: {len(profiles)}")
print("\nProfiles:")
for p in profiles:
    username = p.get('username', 'unknown')
    display = p.get('display_name', 'N/A')
    print(f"  - {display} (username: {username}, id: {p.get('id')})")

print("\n" + "="*70)
print("Recent trades by profile:")
print("="*70)

# Get trades for each profile
for p in profiles:
    profile_id = p.get('id')
    username = p.get('username', 'unknown')
    trades = db.get_trades_by_profile(profile_id)

    if trades:
        print(f"\n@{username} ({len(trades)} trades):")
        for t in trades[-5:]:  # Last 5 trades
            action = t.get('action', '?')
            ticker = t.get('ticker', '?')
            status = t.get('status', 'unknown').upper()
            pnl = t.get('pnl_percent', 0) or 0
            timestamp = t.get('alert_timestamp', 'N/A')
            print(f"  - {action} {ticker} - {status} - {pnl:+.1f}% (at {timestamp})")
