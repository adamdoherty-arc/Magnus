"""
Create Test Trade Data for Demonstration
This script creates sample trade alerts to demonstrate the system working
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import random

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from xtrades_db_manager import XtradesDBManager
from dotenv import load_dotenv

load_dotenv()

def create_sample_trades(db, profile_id, count=10):
    """Create sample trades for testing"""

    tickers = ['AAPL', 'TSLA', 'NVDA', 'AMD', 'SPY', 'QQQ', 'MSFT', 'META', 'GOOGL', 'AMZN']
    strategies = ['CSP', 'Covered Call', 'Iron Condor', 'Vertical Spread', 'Wheel Strategy']
    actions = ['BTO', 'STO', 'BTC', 'STC']

    created_count = 0

    for i in range(count):
        ticker = random.choice(tickers)
        strategy = random.choice(strategies)
        action = random.choice(actions)

        # Create realistic data
        entry_price = round(random.uniform(0.50, 15.00), 2)
        strike_price = random.choice([100, 150, 200, 250, 300, 350, 400, 450, 500])
        quantity = random.choice([1, 2, 3, 5, 10])

        # Random date within last 30 days
        days_ago = random.randint(1, 30)
        alert_timestamp = datetime.now() - timedelta(days=days_ago)

        # Determine status
        status = 'open' if days_ago < 7 else random.choice(['open', 'closed'])

        exit_price = None
        pnl = None
        pnl_percent = None

        if status == 'closed':
            exit_price = round(entry_price * random.uniform(0.5, 1.5), 2)
            pnl = round((exit_price - entry_price) * quantity * 100, 2)
            pnl_percent = round(((exit_price - entry_price) / entry_price) * 100, 2)

        # Create expiration date (future)
        expiration_date = (datetime.now() + timedelta(days=random.randint(7, 45))).date()

        alert_text = f"{action} {quantity}x {ticker} ${strike_price} {strategy} @${entry_price}"
        if status == 'closed':
            alert_text += f" -> CLOSED @${exit_price} ({'+' if pnl > 0 else ''}{pnl_percent}%)"

        trade_data = {
            'profile_id': profile_id,
            'ticker': ticker,
            'strategy': strategy,
            'action': action,
            'entry_price': entry_price,
            'exit_price': exit_price,
            'quantity': quantity,
            'strike_price': strike_price,
            'expiration_date': expiration_date.isoformat(),
            'alert_text': alert_text,
            'alert_timestamp': alert_timestamp.isoformat(),
            'status': status,
            'pnl': pnl,
            'pnl_percent': pnl_percent
        }

        try:
            trade_id = db.add_trade(trade_data)
            created_count += 1
            print(f"  [OK] Created trade {created_count}/{count}: {ticker} {strategy} (ID: {trade_id})")
        except Exception as e:
            print(f"  [ERROR] Failed to create trade: {e}")

    return created_count

def main():
    print("="*70)
    print("CREATE TEST DATA FOR XTRADES WATCHLIST")
    print("="*70)

    db = XtradesDBManager()

    # Create a demo profile
    print("\n[1] Creating demo profile...")

    try:
        # Check if demo profile exists
        demo_profile = db.get_profile_by_username('demo_trader')

        if demo_profile:
            print(f"[INFO] Demo profile already exists (ID: {demo_profile['id']})")
            profile_id = demo_profile['id']
        else:
            profile_id = db.add_profile(
                username='demo_trader',
                display_name='Demo Trader (Test Data)',
                notes='Demo profile with sample trade alerts for testing'
            )
            print(f"[OK] Created demo profile (ID: {profile_id})")

        # Create sample trades
        print("\n[2] Creating sample trade alerts...")
        count = create_sample_trades(db, profile_id, count=15)

        # Update profile sync status
        db.update_profile_sync_status(profile_id, 'success', count)

        print(f"\n[SUCCESS] Created {count} sample trades!")

        # Display stats
        stats = db.get_profile_stats(profile_id)
        print("\n[STATS] Profile Statistics:")
        print(f"  Total Trades: {stats['total_trades']}")
        print(f"  Open Trades: {stats['open_trades']}")
        print(f"  Closed Trades: {stats['closed_trades']}")

        print("\n" + "="*70)
        print("NEXT STEPS")
        print("="*70)
        print("\n1. Open dashboard: http://localhost:8501")
        print("2. Go to: Xtrades Watchlists")
        print("3. Select 'demo_trader' from dropdown")
        print("4. View sample trade data in all tabs")
        print("\nNote: This is test data. To get real data:")
        print("  - Find active xtrades profiles manually")
        print("  - Add them via dashboard or Python script")
        print("  - Run sync service to scrape real alerts")

        return 0

    except Exception as e:
        print(f"\n[ERROR] Failed to create test data: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
