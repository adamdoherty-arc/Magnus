"""Check specific trade details"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))
from xtrades_db_manager import XtradesDBManager

db = XtradesDBManager()

# Get the most recent trade from each new profile
print("Recent trades with full details:")
print("="*70)

for username in ['aspentrade1703', 'krazya', 'waldenco']:
    profile = db.get_profile_by_username(username)
    if profile:
        trades = db.get_trades_by_profile(profile['id'])
        if trades:
            print(f"\n@{username}:")
            for t in trades[-2:]:  # Last 2 trades
                print(f"  Trade ID: {t.get('id')}")
                print(f"  Ticker: {t.get('ticker')}")
                print(f"  Action: {t.get('action')}")
                print(f"  Status: {t.get('status')}")
                print(f"  P/L: {t.get('pnl_percent')}%")
                print(f"  Entry: ${t.get('entry_price')}")
                print(f"  Strike: ${t.get('strike_price')}")
                print(f"  Expiry: {t.get('expiration_date')}")
                print(f"  Alert text (first 100 chars): {t.get('alert_text', '')[:100]}")
                print(f"  Timestamp: {t.get('alert_timestamp')}")
                print()
