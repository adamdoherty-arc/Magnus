"""
Test Suite for Xtrades Database Manager

Run with: python -m pytest src/test_xtrades_db_manager.py -v
"""

import pytest
from datetime import datetime, timedelta
from src.xtrades_db_manager import XtradesDBManager
import psycopg2


@pytest.fixture(scope="module")
def db_manager():
    """Create a database manager instance for testing"""
    return XtradesDBManager()


@pytest.fixture(scope="module")
def test_profile(db_manager):
    """Create a test profile and clean up after tests"""
    # Create test profile
    profile_id = db_manager.add_profile(
        username="test_trader_123",
        display_name="Test Trader",
        notes="Automated test profile"
    )

    yield profile_id

    # Cleanup: deactivate profile after tests
    db_manager.deactivate_profile(profile_id)


@pytest.fixture
def sample_trade_data(test_profile):
    """Sample trade data for testing"""
    return {
        'profile_id': test_profile,
        'ticker': 'AAPL',
        'strategy': 'CSP',
        'action': 'STO',
        'entry_price': 2.50,
        'entry_date': datetime.now(),
        'quantity': 1,
        'strike_price': 150.00,
        'expiration_date': (datetime.now() + timedelta(days=30)).date(),
        'alert_text': 'Test alert: Sold AAPL 150P for $2.50',
        'alert_timestamp': datetime.now(),
        'xtrades_alert_id': 'test_alert_001'
    }


class TestProfileManagement:
    """Test profile CRUD operations"""

    def test_add_profile(self, db_manager):
        """Test adding a new profile"""
        profile_id = db_manager.add_profile(
            username="test_user_add",
            display_name="Test User Add",
            notes="Test note"
        )

        assert profile_id is not None
        assert isinstance(profile_id, int)
        assert profile_id > 0

        # Cleanup
        db_manager.deactivate_profile(profile_id)

    def test_add_duplicate_profile(self, db_manager):
        """Test adding duplicate profile (should update existing)"""
        username = "test_user_duplicate"

        # Add first time
        profile_id_1 = db_manager.add_profile(username, "First Name")

        # Add again with different display name
        profile_id_2 = db_manager.add_profile(username, "Second Name")

        # Should be the same profile ID
        assert profile_id_1 == profile_id_2

        # Check that display name was updated
        profile = db_manager.get_profile_by_id(profile_id_1)
        assert profile['display_name'] == "Second Name"

        # Cleanup
        db_manager.deactivate_profile(profile_id_1)

    def test_get_active_profiles(self, db_manager, test_profile):
        """Test retrieving active profiles"""
        profiles = db_manager.get_active_profiles()

        assert isinstance(profiles, list)
        assert len(profiles) > 0

        # Check that test profile is in the list
        profile_ids = [p['id'] for p in profiles]
        assert test_profile in profile_ids

    def test_get_profile_by_id(self, db_manager, test_profile):
        """Test getting profile by ID"""
        profile = db_manager.get_profile_by_id(test_profile)

        assert profile is not None
        assert profile['id'] == test_profile
        assert profile['username'] == "test_trader_123"
        assert profile['display_name'] == "Test Trader"
        assert profile['active'] is True

    def test_get_profile_by_username(self, db_manager):
        """Test getting profile by username"""
        profile = db_manager.get_profile_by_username("test_trader_123")

        assert profile is not None
        assert profile['username'] == "test_trader_123"
        assert profile['display_name'] == "Test Trader"

    def test_get_nonexistent_profile(self, db_manager):
        """Test getting profile that doesn't exist"""
        profile = db_manager.get_profile_by_id(999999)
        assert profile is None

        profile = db_manager.get_profile_by_username("nonexistent_user")
        assert profile is None

    def test_update_profile_sync_status(self, db_manager, test_profile):
        """Test updating profile sync status"""
        success = db_manager.update_profile_sync_status(
            test_profile,
            status='success',
            trades_count=5
        )

        assert success is True

        # Verify update
        profile = db_manager.get_profile_by_id(test_profile)
        assert profile['last_sync_status'] == 'success'
        assert profile['last_sync'] is not None
        assert profile['total_trades_scraped'] >= 5

    def test_deactivate_reactivate_profile(self, db_manager):
        """Test deactivating and reactivating a profile"""
        # Create test profile
        profile_id = db_manager.add_profile("test_deactivate", "Test Deactivate")

        # Deactivate
        success = db_manager.deactivate_profile(profile_id)
        assert success is True

        # Verify deactivated
        profile = db_manager.get_profile_by_id(profile_id)
        assert profile['active'] is False

        # Should not appear in active profiles
        active_profiles = db_manager.get_active_profiles()
        active_ids = [p['id'] for p in active_profiles]
        assert profile_id not in active_ids

        # Reactivate
        success = db_manager.reactivate_profile(profile_id)
        assert success is True

        # Verify reactivated
        profile = db_manager.get_profile_by_id(profile_id)
        assert profile['active'] is True

        # Cleanup
        db_manager.deactivate_profile(profile_id)


class TestTradeManagement:
    """Test trade CRUD operations"""

    def test_add_trade(self, db_manager, sample_trade_data):
        """Test adding a new trade"""
        trade_id = db_manager.add_trade(sample_trade_data)

        assert trade_id is not None
        assert isinstance(trade_id, int)
        assert trade_id > 0

        # Verify trade was added
        trade = db_manager.get_trade_by_id(trade_id)
        assert trade is not None
        assert trade['ticker'] == 'AAPL'
        assert trade['strategy'] == 'CSP'
        assert float(trade['entry_price']) == 2.50
        assert trade['status'] == 'open'

    def test_get_trade_by_id(self, db_manager, sample_trade_data):
        """Test retrieving trade by ID"""
        trade_id = db_manager.add_trade(sample_trade_data)
        trade = db_manager.get_trade_by_id(trade_id)

        assert trade is not None
        assert trade['id'] == trade_id
        assert trade['ticker'] == 'AAPL'

    def test_update_trade(self, db_manager, sample_trade_data):
        """Test updating trade fields"""
        trade_id = db_manager.add_trade(sample_trade_data)

        # Update trade
        update_data = {
            'exit_price': 1.25,
            'exit_date': datetime.now(),
            'pnl': 125.00,
            'pnl_percent': 50.00,
            'status': 'closed'
        }

        success = db_manager.update_trade(trade_id, update_data)
        assert success is True

        # Verify update
        trade = db_manager.get_trade_by_id(trade_id)
        assert float(trade['exit_price']) == 1.25
        assert trade['status'] == 'closed'
        assert float(trade['pnl']) == 125.00

    def test_close_trade(self, db_manager, sample_trade_data):
        """Test closing a trade with P&L calculation"""
        trade_id = db_manager.add_trade(sample_trade_data)

        # Close trade
        success = db_manager.close_trade(
            trade_id=trade_id,
            exit_price=1.00,
            status='closed'
        )

        assert success is True

        # Verify trade was closed
        trade = db_manager.get_trade_by_id(trade_id)
        assert trade['status'] == 'closed'
        assert trade['exit_price'] is not None
        assert trade['pnl'] is not None

        # P&L should be positive (sold for 2.50, bought back for 1.00)
        assert float(trade['pnl']) > 0

    def test_get_trades_by_profile(self, db_manager, test_profile, sample_trade_data):
        """Test retrieving trades for a profile"""
        # Add multiple trades
        db_manager.add_trade(sample_trade_data)

        trade_data_2 = sample_trade_data.copy()
        trade_data_2['ticker'] = 'TSLA'
        db_manager.add_trade(trade_data_2)

        # Get all trades for profile
        trades = db_manager.get_trades_by_profile(test_profile)

        assert isinstance(trades, list)
        assert len(trades) >= 2

        # Check that all trades belong to the profile
        for trade in trades:
            assert trade['profile_id'] == test_profile

    def test_get_trades_by_status(self, db_manager, test_profile, sample_trade_data):
        """Test filtering trades by status"""
        # Add open trade
        trade_id_1 = db_manager.add_trade(sample_trade_data)

        # Add and close another trade
        trade_data_2 = sample_trade_data.copy()
        trade_data_2['ticker'] = 'NVDA'
        trade_id_2 = db_manager.add_trade(trade_data_2)
        db_manager.close_trade(trade_id_2, exit_price=1.00)

        # Get only open trades
        open_trades = db_manager.get_trades_by_profile(test_profile, status='open')
        open_ids = [t['id'] for t in open_trades]

        assert trade_id_1 in open_ids
        assert trade_id_2 not in open_ids

        # Get only closed trades
        closed_trades = db_manager.get_trades_by_profile(test_profile, status='closed')
        closed_ids = [t['id'] for t in closed_trades]

        assert trade_id_2 in closed_ids
        assert trade_id_1 not in closed_ids

    def test_find_existing_trade(self, db_manager, sample_trade_data):
        """Test finding existing trade to prevent duplicates"""
        # Add trade
        trade_id = db_manager.add_trade(sample_trade_data)

        # Try to find it
        found_id = db_manager.find_existing_trade(
            profile_id=sample_trade_data['profile_id'],
            ticker=sample_trade_data['ticker'],
            alert_timestamp=sample_trade_data['alert_timestamp']
        )

        assert found_id == trade_id

    def test_find_nonexistent_trade(self, db_manager, test_profile):
        """Test finding trade that doesn't exist"""
        found_id = db_manager.find_existing_trade(
            profile_id=test_profile,
            ticker='ZZZZ',
            alert_timestamp=datetime.now()
        )

        assert found_id is None

    def test_get_open_trades_by_profile(self, db_manager, test_profile, sample_trade_data):
        """Test getting all open trades for a profile"""
        # Add some open trades
        db_manager.add_trade(sample_trade_data)

        trade_data_2 = sample_trade_data.copy()
        trade_data_2['ticker'] = 'GOOGL'
        db_manager.add_trade(trade_data_2)

        # Get open trades
        open_trades = db_manager.get_open_trades_by_profile(test_profile)

        assert isinstance(open_trades, list)
        assert len(open_trades) >= 2

        # All should have status 'open'
        for trade in open_trades:
            assert trade['status'] == 'open'


class TestSyncLogging:
    """Test sync log operations"""

    def test_log_sync_start(self, db_manager):
        """Test creating a sync log entry"""
        sync_log_id = db_manager.log_sync_start()

        assert sync_log_id is not None
        assert isinstance(sync_log_id, int)
        assert sync_log_id > 0

    def test_log_sync_complete(self, db_manager):
        """Test completing a sync log entry"""
        # Start sync
        sync_log_id = db_manager.log_sync_start()

        # Complete sync
        stats = {
            'profiles_synced': 3,
            'trades_found': 15,
            'new_trades': 5,
            'updated_trades': 2,
            'errors': None,
            'duration_seconds': 12.5,
            'status': 'success'
        }

        success = db_manager.log_sync_complete(sync_log_id, stats)
        assert success is True

        # Verify log
        latest_sync = db_manager.get_latest_sync()
        assert latest_sync is not None
        assert latest_sync['id'] == sync_log_id
        assert latest_sync['profiles_synced'] == 3
        assert latest_sync['new_trades'] == 5
        assert latest_sync['status'] == 'success'

    def test_log_sync_with_errors(self, db_manager):
        """Test logging a failed sync"""
        sync_log_id = db_manager.log_sync_start()

        stats = {
            'profiles_synced': 1,
            'trades_found': 0,
            'new_trades': 0,
            'updated_trades': 0,
            'errors': 'Connection timeout',
            'duration_seconds': 30.0,
            'status': 'failed'
        }

        success = db_manager.log_sync_complete(sync_log_id, stats)
        assert success is True

        # Verify error was logged
        latest_sync = db_manager.get_latest_sync()
        assert latest_sync['status'] == 'failed'
        assert 'timeout' in latest_sync['errors'].lower()

    def test_get_sync_history(self, db_manager):
        """Test retrieving sync history"""
        # Create a couple sync logs
        sync_id_1 = db_manager.log_sync_start()
        db_manager.log_sync_complete(sync_id_1, {
            'profiles_synced': 2,
            'trades_found': 10,
            'new_trades': 3,
            'updated_trades': 1,
            'duration_seconds': 8.5,
            'status': 'success'
        })

        # Get history
        history = db_manager.get_sync_history(limit=10)

        assert isinstance(history, list)
        assert len(history) > 0

        # Most recent should be first
        assert history[0]['id'] >= sync_id_1


class TestNotifications:
    """Test notification logging operations"""

    def test_log_notification(self, db_manager, sample_trade_data):
        """Test logging a notification"""
        # Create a trade first
        trade_id = db_manager.add_trade(sample_trade_data)

        # Log notification
        notif_id = db_manager.log_notification(
            trade_id=trade_id,
            notification_type='new_trade',
            telegram_msg_id='TG_123456',
            status='sent'
        )

        assert notif_id is not None
        assert isinstance(notif_id, int)

    def test_log_failed_notification(self, db_manager, sample_trade_data):
        """Test logging a failed notification"""
        trade_id = db_manager.add_trade(sample_trade_data)

        notif_id = db_manager.log_notification(
            trade_id=trade_id,
            notification_type='new_trade',
            status='failed',
            error_message='Telegram API timeout'
        )

        assert notif_id is not None

        # Verify error was recorded
        notifications = db_manager.get_notifications_for_trade(trade_id)
        assert len(notifications) > 0
        assert notifications[0]['status'] == 'failed'
        assert 'timeout' in notifications[0]['error_message'].lower()

    def test_get_notifications_for_trade(self, db_manager, sample_trade_data):
        """Test retrieving notifications for a trade"""
        trade_id = db_manager.add_trade(sample_trade_data)

        # Log multiple notifications
        db_manager.log_notification(trade_id, 'new_trade', 'TG_001')
        db_manager.log_notification(trade_id, 'trade_update', 'TG_002')

        notifications = db_manager.get_notifications_for_trade(trade_id)

        assert len(notifications) >= 2

        # Check notification types
        types = [n['notification_type'] for n in notifications]
        assert 'new_trade' in types
        assert 'trade_update' in types

    def test_get_unsent_notifications(self, db_manager, sample_trade_data):
        """Test getting trades that need notifications"""
        # Add trade without notification
        trade_id = db_manager.add_trade(sample_trade_data)

        # Get unsent
        unsent = db_manager.get_unsent_notifications()

        assert isinstance(unsent, list)

        # Our trade should be in the list
        trade_ids = [t['id'] for t in unsent]
        assert trade_id in trade_ids

        # Now log notification
        db_manager.log_notification(trade_id, 'new_trade', 'TG_123')

        # Should no longer appear in unsent
        unsent_after = db_manager.get_unsent_notifications()
        trade_ids_after = [t['id'] for t in unsent_after]
        assert trade_id not in trade_ids_after


class TestAnalytics:
    """Test analytics and statistics operations"""

    def test_get_profile_stats(self, db_manager, test_profile, sample_trade_data):
        """Test getting statistics for a profile"""
        # Add some trades with different outcomes
        trade_id_1 = db_manager.add_trade(sample_trade_data)
        db_manager.close_trade(trade_id_1, exit_price=1.00)  # Winning trade

        trade_data_2 = sample_trade_data.copy()
        trade_data_2['ticker'] = 'MSFT'
        trade_id_2 = db_manager.add_trade(trade_data_2)
        db_manager.close_trade(trade_id_2, exit_price=3.00)  # Losing trade

        # Add open trade
        trade_data_3 = sample_trade_data.copy()
        trade_data_3['ticker'] = 'AMZN'
        db_manager.add_trade(trade_data_3)

        # Get stats
        stats = db_manager.get_profile_stats(test_profile)

        assert stats is not None
        assert stats['total_trades'] >= 3
        assert stats['open_trades'] >= 1
        assert stats['closed_trades'] >= 2
        assert 'total_pnl' in stats
        assert 'win_rate' in stats

    def test_get_overall_stats(self, db_manager):
        """Test getting system-wide statistics"""
        stats = db_manager.get_overall_stats()

        assert stats is not None
        assert 'total_profiles' in stats
        assert 'total_trades' in stats
        assert 'open_trades' in stats
        assert 'closed_trades' in stats
        assert 'total_pnl' in stats
        assert 'win_rate' in stats

        # Should have at least our test data
        assert stats['total_trades'] > 0

    def test_get_trades_by_ticker(self, db_manager, sample_trade_data):
        """Test getting all trades for a specific ticker"""
        # Add trades for specific ticker
        sample_trade_data['ticker'] = 'SPY'
        db_manager.add_trade(sample_trade_data)

        trade_data_2 = sample_trade_data.copy()
        db_manager.add_trade(trade_data_2)

        # Get trades for ticker
        trades = db_manager.get_trades_by_ticker('SPY', limit=10)

        assert isinstance(trades, list)
        assert len(trades) >= 2

        # All should be for SPY
        for trade in trades:
            assert trade['ticker'] == 'SPY'

    def test_get_recent_activity(self, db_manager, sample_trade_data):
        """Test getting recent trading activity"""
        # Add some recent trades
        db_manager.add_trade(sample_trade_data)

        # Get recent activity
        activity = db_manager.get_recent_activity(days=7, limit=50)

        assert isinstance(activity, list)
        assert len(activity) > 0

        # Should include profile info
        if activity:
            assert 'username' in activity[0]
            assert 'ticker' in activity[0]


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_update_nonexistent_trade(self, db_manager):
        """Test updating a trade that doesn't exist"""
        success = db_manager.update_trade(999999, {'status': 'closed'})
        assert success is False

    def test_close_nonexistent_trade(self, db_manager):
        """Test closing a trade that doesn't exist"""
        success = db_manager.close_trade(999999, exit_price=1.00)
        assert success is False

    def test_empty_update_data(self, db_manager, sample_trade_data):
        """Test updating with no valid fields"""
        trade_id = db_manager.add_trade(sample_trade_data)

        # Try to update with invalid fields
        success = db_manager.update_trade(trade_id, {'invalid_field': 'value'})
        assert success is False

    def test_get_stats_for_nonexistent_profile(self, db_manager):
        """Test getting stats for profile that doesn't exist"""
        stats = db_manager.get_profile_stats(999999)

        assert stats is not None
        assert stats['total_trades'] == 0
        assert stats['total_pnl'] == 0.0

    def test_username_case_insensitive(self, db_manager):
        """Test that usernames are case-insensitive"""
        # Add profile with mixed case
        profile_id = db_manager.add_profile("TestUser_CASE")

        # Should find with lowercase
        profile = db_manager.get_profile_by_username("testuser_case")
        assert profile is not None
        assert profile['id'] == profile_id

        # Cleanup
        db_manager.deactivate_profile(profile_id)


if __name__ == "__main__":
    print("Running Xtrades DB Manager Tests...")
    print("=" * 60)
    print()
    print("To run tests, execute:")
    print("  python -m pytest src/test_xtrades_db_manager.py -v")
    print()
    print("For specific test class:")
    print("  python -m pytest src/test_xtrades_db_manager.py::TestProfileManagement -v")
    print()
    print("For coverage report:")
    print("  python -m pytest src/test_xtrades_db_manager.py --cov=src.xtrades_db_manager --cov-report=html")
    print("=" * 60)
