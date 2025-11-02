"""
Xtrades Database Manager - Usage Examples

This file demonstrates common usage patterns for the XtradesDBManager class.
"""

from src.xtrades_db_manager import XtradesDBManager
from datetime import datetime, timedelta


def example_1_profile_management():
    """Example 1: Managing Xtrades profiles"""
    print("=" * 60)
    print("EXAMPLE 1: Profile Management")
    print("=" * 60)

    db = XtradesDBManager()

    # Add a new profile to monitor
    print("\n1. Adding new profile...")
    profile_id = db.add_profile(
        username="wheeltraderguru",
        display_name="Wheel Trader Guru",
        notes="Focuses on cash-secured puts and covered calls"
    )
    print(f"   Created profile ID: {profile_id}")

    # Get all active profiles
    print("\n2. Getting all active profiles...")
    active_profiles = db.get_active_profiles()
    for profile in active_profiles:
        print(f"   - {profile['username']} ({profile['display_name']})")
        print(f"     Total trades: {profile['total_trades_scraped']}")
        print(f"     Last sync: {profile['last_sync']}")

    # Get specific profile
    print("\n3. Getting profile by username...")
    profile = db.get_profile_by_username("wheeltraderguru")
    if profile:
        print(f"   Found: {profile['display_name']}")
        print(f"   Active: {profile['active']}")

    # Update sync status
    print("\n4. Updating sync status...")
    db.update_profile_sync_status(
        profile_id=profile_id,
        status='success',
        trades_count=10
    )
    print("   Sync status updated")

    # Deactivate profile
    print("\n5. Deactivating profile...")
    db.deactivate_profile(profile_id)
    print("   Profile deactivated")

    print()


def example_2_trade_management():
    """Example 2: Managing trades"""
    print("=" * 60)
    print("EXAMPLE 2: Trade Management")
    print("=" * 60)

    db = XtradesDBManager()

    # Create a test profile first
    profile_id = db.add_profile("example_trader", "Example Trader")

    # Add a new trade (opening position)
    print("\n1. Adding new trade (opening CSP)...")
    trade_data = {
        'profile_id': profile_id,
        'ticker': 'AAPL',
        'strategy': 'CSP',
        'action': 'STO',
        'entry_price': 3.50,
        'entry_date': datetime.now(),
        'quantity': 2,
        'strike_price': 175.00,
        'expiration_date': datetime.now() + timedelta(days=45),
        'alert_text': 'STO 2 AAPL 45DTE 175P @ $3.50',
        'alert_timestamp': datetime.now(),
        'xtrades_alert_id': 'ALERT_001'
    }

    trade_id = db.add_trade(trade_data)
    print(f"   Created trade ID: {trade_id}")

    # Check for duplicate
    print("\n2. Checking for duplicate trade...")
    existing_id = db.find_existing_trade(
        profile_id=profile_id,
        ticker='AAPL',
        alert_timestamp=trade_data['alert_timestamp']
    )
    print(f"   Found existing trade: {existing_id}")

    # Get all open trades for profile
    print("\n3. Getting open trades for profile...")
    open_trades = db.get_open_trades_by_profile(profile_id)
    for trade in open_trades:
        print(f"   - {trade['ticker']} {trade['strike_price']}P")
        print(f"     Entry: ${trade['entry_price']} x {trade['quantity']} contracts")
        print(f"     Expiration: {trade['expiration_date']}")

    # Update trade (add exit)
    print("\n4. Closing trade with profit...")
    db.close_trade(
        trade_id=trade_id,
        exit_price=1.50,  # Bought back for less
        exit_date=datetime.now(),
        status='closed'
    )

    # Verify trade was closed
    closed_trade = db.get_trade_by_id(trade_id)
    print(f"   Trade closed: {closed_trade['status']}")
    print(f"   P&L: ${closed_trade['pnl']:.2f} ({closed_trade['pnl_percent']:.1f}%)")

    # Cleanup
    db.deactivate_profile(profile_id)
    print()


def example_3_sync_logging():
    """Example 3: Logging sync operations"""
    print("=" * 60)
    print("EXAMPLE 3: Sync Operation Logging")
    print("=" * 60)

    db = XtradesDBManager()

    # Start a sync operation
    print("\n1. Starting sync operation...")
    sync_log_id = db.log_sync_start()
    print(f"   Sync log ID: {sync_log_id}")

    # Simulate some work
    print("\n2. Processing profiles and trades...")
    # (In real usage, this is where you'd scrape Xtrades.net)
    import time
    start_time = time.time()

    # Simulate finding trades
    new_trades = 5
    updated_trades = 2

    time.sleep(0.5)  # Simulate work
    duration = time.time() - start_time

    # Complete the sync
    print("\n3. Completing sync operation...")
    stats = {
        'profiles_synced': 3,
        'trades_found': 15,
        'new_trades': new_trades,
        'updated_trades': updated_trades,
        'errors': None,
        'duration_seconds': duration,
        'status': 'success'
    }

    db.log_sync_complete(sync_log_id, stats)
    print(f"   Sync completed: {stats['status']}")
    print(f"   New trades: {new_trades}, Updated: {updated_trades}")
    print(f"   Duration: {duration:.2f}s")

    # Get sync history
    print("\n4. Getting recent sync history...")
    history = db.get_sync_history(limit=5)
    for log in history:
        print(f"   - {log['sync_timestamp']}: {log['status']}")
        print(f"     Profiles: {log['profiles_synced']}, "
              f"New: {log['new_trades']}, Updated: {log['updated_trades']}")

    print()


def example_4_notifications():
    """Example 4: Managing notifications"""
    print("=" * 60)
    print("EXAMPLE 4: Notification Management")
    print("=" * 60)

    db = XtradesDBManager()

    # Create test data
    profile_id = db.add_profile("notif_test", "Notification Test")
    trade_data = {
        'profile_id': profile_id,
        'ticker': 'TSLA',
        'strategy': 'CC',
        'action': 'STO',
        'entry_price': 5.00,
        'entry_date': datetime.now(),
        'quantity': 1,
        'strike_price': 250.00,
        'expiration_date': datetime.now() + timedelta(days=30),
        'alert_text': 'STO 1 TSLA 30DTE 250C @ $5.00',
        'alert_timestamp': datetime.now()
    }
    trade_id = db.add_trade(trade_data)

    # Log notification sent
    print("\n1. Logging notification sent to Telegram...")
    notif_id = db.log_notification(
        trade_id=trade_id,
        notification_type='new_trade',
        telegram_msg_id='TG_MSG_12345',
        status='sent'
    )
    print(f"   Notification logged: ID {notif_id}")

    # Get notifications for trade
    print("\n2. Getting all notifications for this trade...")
    notifications = db.get_notifications_for_trade(trade_id)
    for notif in notifications:
        print(f"   - Type: {notif['notification_type']}")
        print(f"     Status: {notif['status']}")
        print(f"     Telegram ID: {notif['telegram_message_id']}")
        print(f"     Sent: {notif['sent_at']}")

    # Get unsent notifications
    print("\n3. Checking for trades needing notifications...")
    unsent = db.get_unsent_notifications()
    print(f"   Found {len(unsent)} trades without notifications")

    # Cleanup
    db.deactivate_profile(profile_id)
    print()


def example_5_analytics():
    """Example 5: Analytics and statistics"""
    print("=" * 60)
    print("EXAMPLE 5: Analytics & Statistics")
    print("=" * 60)

    db = XtradesDBManager()

    # Create test data with multiple trades
    profile_id = db.add_profile("analytics_test", "Analytics Test Trader")

    # Add winning trade
    trade_1 = {
        'profile_id': profile_id,
        'ticker': 'SPY',
        'strategy': 'CSP',
        'action': 'STO',
        'entry_price': 4.00,
        'entry_date': datetime.now() - timedelta(days=30),
        'quantity': 1,
        'strike_price': 450.00,
        'expiration_date': datetime.now() - timedelta(days=1),
        'alert_timestamp': datetime.now() - timedelta(days=30)
    }
    trade_id_1 = db.add_trade(trade_1)
    db.close_trade(trade_id_1, exit_price=1.50, status='closed')

    # Add losing trade
    trade_2 = trade_1.copy()
    trade_2['ticker'] = 'QQQ'
    trade_2['entry_price'] = 3.00
    trade_id_2 = db.add_trade(trade_2)
    db.close_trade(trade_id_2, exit_price=4.50, status='closed')

    # Add open trade
    trade_3 = trade_1.copy()
    trade_3['ticker'] = 'IWM'
    trade_3['alert_timestamp'] = datetime.now()
    db.add_trade(trade_3)

    # Get profile statistics
    print("\n1. Profile Statistics:")
    stats = db.get_profile_stats(profile_id)
    print(f"   Total trades: {stats['total_trades']}")
    print(f"   Open: {stats['open_trades']}, Closed: {stats['closed_trades']}")
    print(f"   Total P&L: ${stats['total_pnl']:.2f}")
    print(f"   Average P&L: ${stats['avg_pnl']:.2f}")
    print(f"   Win rate: {stats['win_rate']:.1f}%")

    if stats['best_trade']:
        print(f"\n   Best trade: {stats['best_trade']['ticker']}")
        print(f"   P&L: ${stats['best_trade']['pnl']:.2f}")

    if stats['worst_trade']:
        print(f"\n   Worst trade: {stats['worst_trade']['ticker']}")
        print(f"   P&L: ${stats['worst_trade']['pnl']:.2f}")

    # Get overall system statistics
    print("\n2. Overall System Statistics:")
    overall = db.get_overall_stats()
    print(f"   Total profiles: {overall['total_profiles']}")
    print(f"   Total trades: {overall['total_trades']}")
    print(f"   Open: {overall['open_trades']}, Closed: {overall['closed_trades']}")
    print(f"   System P&L: ${overall['total_pnl']:.2f}")
    print(f"   Win rate: {overall['win_rate']:.1f}%")

    if overall['most_active_ticker']:
        print(f"\n   Most active ticker: {overall['most_active_ticker']['ticker']}")
        print(f"   Trade count: {overall['most_active_ticker']['trade_count']}")

    # Get trades by ticker
    print("\n3. All SPY trades across all profiles:")
    spy_trades = db.get_trades_by_ticker('SPY', limit=10)
    for trade in spy_trades:
        print(f"   - {trade['username']}: {trade['strategy']}")
        print(f"     {trade['strike_price']}P @ ${trade['entry_price']}")
        if trade['pnl']:
            print(f"     P&L: ${trade['pnl']:.2f}")

    # Get recent activity
    print("\n4. Recent trading activity (last 7 days):")
    recent = db.get_recent_activity(days=7, limit=10)
    for trade in recent[:5]:  # Show first 5
        print(f"   - {trade['ticker']} by {trade['username']}")
        print(f"     {trade['strategy']} - {trade['status']}")
        print(f"     Alert: {trade['alert_timestamp']}")

    # Cleanup
    db.deactivate_profile(profile_id)
    print()


def example_6_complete_workflow():
    """Example 6: Complete workflow - monitoring a trader"""
    print("=" * 60)
    print("EXAMPLE 6: Complete Workflow - Monitoring a Trader")
    print("=" * 60)

    db = XtradesDBManager()

    # Step 1: Add trader to monitor
    print("\n[STEP 1] Adding trader to monitoring list...")
    profile_id = db.add_profile(
        username="optionsmaster",
        display_name="Options Master",
        notes="Top-performing wheel strategy trader"
    )
    print(f"   Profile created: ID {profile_id}")

    # Step 2: Start sync operation
    print("\n[STEP 2] Starting synchronization...")
    sync_log_id = db.log_sync_start()

    # Step 3: Process alerts (simulated)
    print("\n[STEP 3] Processing Xtrades alerts...")
    alerts = [
        {
            'ticker': 'AAPL',
            'strategy': 'CSP',
            'action': 'STO',
            'entry_price': 3.25,
            'strike_price': 180.00,
            'alert_timestamp': datetime.now()
        },
        {
            'ticker': 'MSFT',
            'strategy': 'CSP',
            'action': 'STO',
            'entry_price': 4.50,
            'strike_price': 380.00,
            'alert_timestamp': datetime.now()
        }
    ]

    new_trades = 0
    for alert in alerts:
        # Check if trade already exists
        existing = db.find_existing_trade(
            profile_id=profile_id,
            ticker=alert['ticker'],
            alert_timestamp=alert['alert_timestamp']
        )

        if not existing:
            trade_data = {
                'profile_id': profile_id,
                'ticker': alert['ticker'],
                'strategy': alert['strategy'],
                'action': alert['action'],
                'entry_price': alert['entry_price'],
                'entry_date': datetime.now(),
                'quantity': 1,
                'strike_price': alert['strike_price'],
                'expiration_date': datetime.now() + timedelta(days=45),
                'alert_text': f"{alert['action']} {alert['ticker']} {alert['strike_price']}P @ ${alert['entry_price']}",
                'alert_timestamp': alert['alert_timestamp']
            }

            trade_id = db.add_trade(trade_data)
            print(f"   New trade added: {alert['ticker']} (ID: {trade_id})")

            # Send notification
            notif_id = db.log_notification(
                trade_id=trade_id,
                notification_type='new_trade',
                telegram_msg_id=f'TG_{trade_id}',
                status='sent'
            )
            print(f"   Notification sent: {notif_id}")

            new_trades += 1
        else:
            print(f"   Duplicate trade found for {alert['ticker']}, skipping")

    # Step 4: Complete sync
    print("\n[STEP 4] Completing synchronization...")
    db.update_profile_sync_status(profile_id, 'success', new_trades)

    sync_stats = {
        'profiles_synced': 1,
        'trades_found': len(alerts),
        'new_trades': new_trades,
        'updated_trades': 0,
        'errors': None,
        'duration_seconds': 2.5,
        'status': 'success'
    }
    db.log_sync_complete(sync_log_id, sync_stats)
    print(f"   Sync completed: {new_trades} new trades")

    # Step 5: View current positions
    print("\n[STEP 5] Current open positions:")
    open_positions = db.get_open_trades_by_profile(profile_id)
    for pos in open_positions:
        print(f"   - {pos['ticker']} {pos['strike_price']}P")
        print(f"     Premium: ${pos['entry_price']} x {pos['quantity']} contracts")
        print(f"     Expiration: {pos['expiration_date']}")

    # Step 6: Check for unsent notifications
    print("\n[STEP 6] Checking for unsent notifications...")
    unsent = db.get_unsent_notifications()
    print(f"   Trades needing notifications: {len(unsent)}")

    # Step 7: Get trader performance
    print("\n[STEP 7] Trader performance summary:")
    stats = db.get_profile_stats(profile_id)
    print(f"   Total trades: {stats['total_trades']}")
    print(f"   Currently open: {stats['open_trades']}")
    print(f"   Total P&L: ${stats['total_pnl']:.2f}")

    # Cleanup
    print("\n[CLEANUP] Deactivating test profile...")
    db.deactivate_profile(profile_id)

    print("\n✓ Workflow complete!")
    print()


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("XTRADES DATABASE MANAGER - USAGE EXAMPLES")
    print("=" * 60)
    print()

    try:
        example_1_profile_management()
        example_2_trade_management()
        example_3_sync_logging()
        example_4_notifications()
        example_5_analytics()
        example_6_complete_workflow()

        print("\n" + "=" * 60)
        print("ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print()

    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
