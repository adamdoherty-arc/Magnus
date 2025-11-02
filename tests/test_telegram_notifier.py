"""
Comprehensive Test Suite for Telegram Notifier

This module provides extensive testing for the TelegramNotifier class,
including unit tests, integration tests, and mocking for offline testing.

Run with: pytest tests/test_telegram_notifier.py -v

Author: Magnus Trading Dashboard
Created: 2025-11-02
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta, date
from decimal import Decimal
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from telegram_notifier import TelegramNotifier, create_notifier


class TestTelegramNotifierInitialization:
    """Test cases for TelegramNotifier initialization."""

    @patch.dict(os.environ, {
        'TELEGRAM_BOT_TOKEN': 'test_token',
        'TELEGRAM_CHAT_ID': 'test_chat_id',
        'TELEGRAM_ENABLED': 'true'
    })
    @patch('telegram_notifier.Bot')
    def test_init_with_env_vars(self, mock_bot_class):
        """Test initialization with environment variables."""
        notifier = TelegramNotifier()

        assert notifier.bot_token == 'test_token'
        assert notifier.chat_id == 'test_chat_id'
        assert notifier.enabled is True
        mock_bot_class.assert_called_once_with(token='test_token')

    def test_init_with_parameters(self):
        """Test initialization with direct parameters."""
        with patch('telegram_notifier.Bot') as mock_bot_class:
            notifier = TelegramNotifier(
                bot_token='param_token',
                chat_id='param_chat',
                enabled=True
            )

            assert notifier.bot_token == 'param_token'
            assert notifier.chat_id == 'param_chat'
            assert notifier.enabled is True

    @patch.dict(os.environ, {'TELEGRAM_ENABLED': 'false'})
    def test_init_disabled(self):
        """Test initialization when disabled."""
        notifier = TelegramNotifier()

        assert notifier.enabled is False
        assert notifier.bot is None

    @patch.dict(os.environ, {
        'TELEGRAM_ENABLED': 'true',
        'TELEGRAM_BOT_TOKEN': '',
        'TELEGRAM_CHAT_ID': ''
    })
    def test_init_missing_credentials(self):
        """Test initialization with missing credentials."""
        notifier = TelegramNotifier()

        assert notifier.enabled is False
        assert notifier.bot is None

    def test_init_custom_retry_settings(self):
        """Test initialization with custom retry settings."""
        notifier = TelegramNotifier(
            max_retries=5,
            retry_delay=3.0
        )

        assert notifier.max_retries == 5
        assert notifier.retry_delay == 3.0


class TestMessageFormatting:
    """Test cases for message formatting methods."""

    def setup_method(self):
        """Set up test fixtures."""
        self.notifier = TelegramNotifier(enabled=False)

    def test_format_currency_basic(self):
        """Test basic currency formatting."""
        assert self.notifier._format_currency(100) == "$100.00"
        assert self.notifier._format_currency(1234.56) == "$1,234.56"
        assert self.notifier._format_currency(Decimal("99.99")) == "$99.99"

    def test_format_currency_with_sign(self):
        """Test currency formatting with sign."""
        assert self.notifier._format_currency(100, include_sign=True) == "+$100.00"
        assert self.notifier._format_currency(-50, include_sign=True) == "-$50.00"
        assert self.notifier._format_currency(0, include_sign=True) == "$0.00"

    def test_format_currency_edge_cases(self):
        """Test currency formatting edge cases."""
        assert self.notifier._format_currency(None) == "N/A"
        assert self.notifier._format_currency("invalid") == "invalid"
        assert self.notifier._format_currency(0) == "$0.00"

    def test_format_percent_basic(self):
        """Test basic percentage formatting."""
        assert self.notifier._format_percent(50) == "50.00%"
        assert self.notifier._format_percent(12.345) == "12.35%"
        assert self.notifier._format_percent(Decimal("99.99")) == "99.99%"

    def test_format_percent_with_sign(self):
        """Test percentage formatting with sign."""
        assert self.notifier._format_percent(25, include_sign=True) == "+25.00%"
        assert self.notifier._format_percent(-10, include_sign=True) == "-10.00%"

    def test_format_percent_edge_cases(self):
        """Test percentage formatting edge cases."""
        assert self.notifier._format_percent(None) == "N/A"
        assert self.notifier._format_percent("invalid") == "invalid"

    def test_format_date(self):
        """Test date formatting."""
        test_date = date(2025, 11, 2)
        assert self.notifier._format_date(test_date) == "2025-11-02"

        test_datetime = datetime(2025, 11, 2, 14, 30)
        assert self.notifier._format_date(test_datetime) == "2025-11-02"

        assert self.notifier._format_date(None) == "N/A"

    def test_format_datetime(self):
        """Test datetime formatting."""
        test_datetime = datetime(2025, 11, 2, 14, 30)
        assert self.notifier._format_datetime(test_datetime) == "2025-11-02 02:30 PM"

        test_datetime_am = datetime(2025, 11, 2, 9, 15)
        assert self.notifier._format_datetime(test_datetime_am) == "2025-11-02 09:15 AM"

        assert self.notifier._format_datetime(None) == "N/A"


class TestNewTradeAlert:
    """Test cases for new trade alerts."""

    def setup_method(self):
        """Set up test fixtures."""
        with patch('telegram_notifier.Bot'):
            self.notifier = TelegramNotifier(
                bot_token='test_token',
                chat_id='test_chat',
                enabled=True
            )

        self.sample_trade = {
            'profile_username': 'traderJoe',
            'ticker': 'AAPL',
            'strategy': 'CSP',
            'action': 'STO',
            'entry_price': Decimal('2.50'),
            'quantity': 1,
            'strike_price': Decimal('170.00'),
            'expiration_date': date(2025, 12, 20),
            'alert_timestamp': datetime(2025, 11, 2, 14, 30),
            'alert_text': 'AAPL CSP: STO 1x $170 PUT @ $2.50'
        }

    def test_new_trade_alert_success(self):
        """Test successful new trade alert."""
        mock_message = Mock()
        mock_message.message_id = '12345'
        self.notifier.bot.send_message = Mock(return_value=mock_message)

        message_id = self.notifier.send_new_trade_alert(self.sample_trade)

        assert message_id == '12345'
        self.notifier.bot.send_message.assert_called_once()

        # Verify message content
        call_args = self.notifier.bot.send_message.call_args
        message_text = call_args.kwargs['text']
        assert 'NEW TRADE ALERT' in message_text
        assert 'traderJoe' in message_text
        assert 'AAPL' in message_text
        assert 'CSP' in message_text
        assert '$2.50' in message_text

    def test_new_trade_alert_disabled(self):
        """Test new trade alert when disabled."""
        self.notifier.enabled = False
        message_id = self.notifier.send_new_trade_alert(self.sample_trade)
        assert message_id is None

    def test_new_trade_alert_missing_data(self):
        """Test new trade alert with missing data."""
        mock_message = Mock()
        mock_message.message_id = '12345'
        self.notifier.bot.send_message = Mock(return_value=mock_message)

        minimal_trade = {
            'profile_username': 'testuser',
            'ticker': 'TSLA'
        }

        message_id = self.notifier.send_new_trade_alert(minimal_trade)
        assert message_id == '12345'

        # Verify message was sent with defaults
        call_args = self.notifier.bot.send_message.call_args
        message_text = call_args.kwargs['text']
        assert 'testuser' in message_text
        assert 'TSLA' in message_text
        assert 'N/A' in message_text


class TestTradeUpdateAlert:
    """Test cases for trade update alerts."""

    def setup_method(self):
        """Set up test fixtures."""
        with patch('telegram_notifier.Bot'):
            self.notifier = TelegramNotifier(
                bot_token='test_token',
                chat_id='test_chat',
                enabled=True
            )

        self.sample_trade = {
            'profile_username': 'traderJoe',
            'ticker': 'AAPL',
            'strategy': 'CSP'
        }

    def test_trade_update_price_change(self):
        """Test trade update with price change."""
        mock_message = Mock()
        mock_message.message_id = '12345'
        self.notifier.bot.send_message = Mock(return_value=mock_message)

        changes = {
            'exit_price': {'before': None, 'after': Decimal('1.25')},
            'status': {'before': 'open', 'after': 'closed'}
        }

        message_id = self.notifier.send_trade_update_alert(self.sample_trade, changes)

        assert message_id == '12345'
        call_args = self.notifier.bot.send_message.call_args
        message_text = call_args.kwargs['text']
        assert 'TRADE UPDATE' in message_text
        assert 'Exit Price' in message_text
        assert '$1.25' in message_text

    def test_trade_update_pnl_change(self):
        """Test trade update with P&L change."""
        mock_message = Mock()
        mock_message.message_id = '12345'
        self.notifier.bot.send_message = Mock(return_value=mock_message)

        changes = {
            'pnl': {'before': Decimal('0'), 'after': Decimal('125.00')},
            'pnl_percent': {'before': 0, 'after': 50.00}
        }

        message_id = self.notifier.send_trade_update_alert(self.sample_trade, changes)

        assert message_id == '12345'
        call_args = self.notifier.bot.send_message.call_args
        message_text = call_args.kwargs['text']
        assert '+$125.00' in message_text
        assert '50.00%' in message_text


class TestTradeClosedAlert:
    """Test cases for trade closed alerts."""

    def setup_method(self):
        """Set up test fixtures."""
        with patch('telegram_notifier.Bot'):
            self.notifier = TelegramNotifier(
                bot_token='test_token',
                chat_id='test_chat',
                enabled=True
            )

    def test_trade_closed_profit(self):
        """Test trade closed alert with profit."""
        mock_message = Mock()
        mock_message.message_id = '12345'
        self.notifier.bot.send_message = Mock(return_value=mock_message)

        closed_trade = {
            'profile_username': 'traderJoe',
            'ticker': 'AAPL',
            'strategy': 'CSP',
            'pnl': Decimal('125.00'),
            'pnl_percent': Decimal('50.00'),
            'entry_date': datetime(2025, 10, 1),
            'exit_date': datetime(2025, 11, 1)
        }

        message_id = self.notifier.send_trade_closed_alert(closed_trade)

        assert message_id == '12345'
        call_args = self.notifier.bot.send_message.call_args
        message_text = call_args.kwargs['text']
        assert 'PROFIT' in message_text
        assert '+$125.00' in message_text
        assert '31 days' in message_text

    def test_trade_closed_loss(self):
        """Test trade closed alert with loss."""
        mock_message = Mock()
        mock_message.message_id = '12345'
        self.notifier.bot.send_message = Mock(return_value=mock_message)

        closed_trade = {
            'profile_username': 'traderJoe',
            'ticker': 'TSLA',
            'strategy': 'CC',
            'pnl': Decimal('-50.00'),
            'pnl_percent': Decimal('-25.00'),
            'entry_date': datetime(2025, 10, 15),
            'exit_date': datetime(2025, 10, 22)
        }

        message_id = self.notifier.send_trade_closed_alert(closed_trade)

        assert message_id == '12345'
        call_args = self.notifier.bot.send_message.call_args
        message_text = call_args.kwargs['text']
        assert 'LOSS' in message_text
        assert '-$50.00' in message_text


class TestSyncErrorAlert:
    """Test cases for sync error alerts."""

    def setup_method(self):
        """Set up test fixtures."""
        with patch('telegram_notifier.Bot'):
            self.notifier = TelegramNotifier(
                bot_token='test_token',
                chat_id='test_chat',
                enabled=True
            )

    def test_sync_error_with_profiles(self):
        """Test sync error alert with affected profiles."""
        mock_message = Mock()
        mock_message.message_id = '12345'
        self.notifier.bot.send_message = Mock(return_value=mock_message)

        error_msg = "Database connection failed"
        profiles = ['traderJoe', 'optionsGuru']

        message_id = self.notifier.send_sync_error_alert(error_msg, profiles)

        assert message_id == '12345'
        call_args = self.notifier.bot.send_message.call_args
        message_text = call_args.kwargs['text']
        assert 'SYNC ERROR' in message_text
        assert error_msg in message_text
        assert 'traderJoe' in message_text
        assert 'optionsGuru' in message_text

    def test_sync_error_without_profiles(self):
        """Test sync error alert without profiles."""
        mock_message = Mock()
        mock_message.message_id = '12345'
        self.notifier.bot.send_message = Mock(return_value=mock_message)

        error_msg = "General sync error"

        message_id = self.notifier.send_sync_error_alert(error_msg)

        assert message_id == '12345'
        call_args = self.notifier.bot.send_message.call_args
        message_text = call_args.kwargs['text']
        assert error_msg in message_text


class TestDailySummary:
    """Test cases for daily summary alerts."""

    def setup_method(self):
        """Set up test fixtures."""
        with patch('telegram_notifier.Bot'):
            self.notifier = TelegramNotifier(
                bot_token='test_token',
                chat_id='test_chat',
                enabled=True
            )

    def test_daily_summary(self):
        """Test daily summary alert."""
        mock_message = Mock()
        mock_message.message_id = '12345'
        self.notifier.bot.send_message = Mock(return_value=mock_message)

        summary = {
            'total_trades': 50,
            'new_trades': 5,
            'closed_trades': 3,
            'total_pnl': Decimal('1250.00'),
            'win_rate': 75.5,
            'active_profiles': 10
        }

        message_id = self.notifier.send_daily_summary(summary)

        assert message_id == '12345'
        call_args = self.notifier.bot.send_message.call_args
        message_text = call_args.kwargs['text']
        assert 'DAILY TRADING SUMMARY' in message_text
        assert '5' in message_text  # new trades
        assert '3' in message_text  # closed trades
        assert '+$1,250.00' in message_text
        assert '75.50%' in message_text


class TestRetryLogic:
    """Test cases for retry logic and error handling."""

    def setup_method(self):
        """Set up test fixtures."""
        with patch('telegram_notifier.Bot'):
            self.notifier = TelegramNotifier(
                bot_token='test_token',
                chat_id='test_chat',
                enabled=True,
                max_retries=3,
                retry_delay=0.1
            )

    def test_retry_on_timeout(self):
        """Test retry logic on timeout."""
        from telegram.error import TimedOut

        # First two calls timeout, third succeeds
        mock_message = Mock()
        mock_message.message_id = '12345'
        self.notifier.bot.send_message = Mock(
            side_effect=[TimedOut(), TimedOut(), mock_message]
        )

        with patch('time.sleep'):  # Don't actually sleep in tests
            message_id = self.notifier._send_message("Test message")

        assert message_id == '12345'
        assert self.notifier.bot.send_message.call_count == 3

    def test_retry_on_network_error(self):
        """Test retry logic on network error."""
        from telegram.error import NetworkError

        # First call fails, second succeeds
        mock_message = Mock()
        mock_message.message_id = '12345'
        self.notifier.bot.send_message = Mock(
            side_effect=[NetworkError("Connection failed"), mock_message]
        )

        with patch('time.sleep'):
            message_id = self.notifier._send_message("Test message")

        assert message_id == '12345'
        assert self.notifier.bot.send_message.call_count == 2

    def test_max_retries_exceeded(self):
        """Test when max retries is exceeded."""
        from telegram.error import TimedOut

        self.notifier.bot.send_message = Mock(side_effect=TimedOut())

        with patch('time.sleep'):
            message_id = self.notifier._send_message("Test message")

        assert message_id is None
        assert self.notifier.bot.send_message.call_count == 3

    def test_rate_limit_handling(self):
        """Test rate limit handling."""
        from telegram.error import RetryAfter

        mock_message = Mock()
        mock_message.message_id = '12345'
        retry_error = RetryAfter(2)
        self.notifier.bot.send_message = Mock(
            side_effect=[retry_error, mock_message]
        )

        with patch('time.sleep') as mock_sleep:
            message_id = self.notifier._send_message("Test message")

        assert message_id == '12345'
        mock_sleep.assert_called_with(2)


class TestCustomMessage:
    """Test cases for custom messages."""

    def setup_method(self):
        """Set up test fixtures."""
        with patch('telegram_notifier.Bot'):
            self.notifier = TelegramNotifier(
                bot_token='test_token',
                chat_id='test_chat',
                enabled=True
            )

    def test_custom_message_markdown(self):
        """Test custom message with markdown."""
        mock_message = Mock()
        mock_message.message_id = '12345'
        self.notifier.bot.send_message = Mock(return_value=mock_message)

        message_id = self.notifier.send_custom_message("*Bold* _italic_ `code`")

        assert message_id == '12345'
        call_args = self.notifier.bot.send_message.call_args
        assert call_args.kwargs['parse_mode'] == 'Markdown'

    def test_custom_message_html(self):
        """Test custom message with HTML."""
        mock_message = Mock()
        mock_message.message_id = '12345'
        self.notifier.bot.send_message = Mock(return_value=mock_message)

        message_id = self.notifier.send_custom_message(
            "<b>Bold</b> <i>italic</i>",
            parse_mode='HTML'
        )

        assert message_id == '12345'
        call_args = self.notifier.bot.send_message.call_args
        assert call_args.kwargs['parse_mode'] == 'HTML'


class TestUtilityMethods:
    """Test cases for utility methods."""

    def setup_method(self):
        """Set up test fixtures."""
        with patch('telegram_notifier.Bot'):
            self.notifier = TelegramNotifier(
                bot_token='test_token',
                chat_id='test_chat',
                enabled=True
            )

    def test_is_available_enabled(self):
        """Test _is_available when enabled."""
        assert self.notifier._is_available() is True

    def test_is_available_disabled(self):
        """Test _is_available when disabled."""
        self.notifier.enabled = False
        assert self.notifier._is_available() is False

    def test_is_available_no_bot(self):
        """Test _is_available when bot is None."""
        self.notifier.bot = None
        assert self.notifier._is_available() is False

    def test_get_bot_info(self):
        """Test get_bot_info method."""
        mock_bot_user = Mock()
        mock_bot_user.id = 123456
        mock_bot_user.username = 'test_bot'
        mock_bot_user.first_name = 'Test Bot'
        mock_bot_user.is_bot = True

        self.notifier.bot.get_me = Mock(return_value=mock_bot_user)

        bot_info = self.notifier.get_bot_info()

        assert bot_info['id'] == 123456
        assert bot_info['username'] == 'test_bot'
        assert bot_info['first_name'] == 'Test Bot'
        assert bot_info['is_bot'] is True

    def test_test_connection_success(self):
        """Test test_connection method success."""
        mock_message = Mock()
        mock_message.message_id = '12345'
        self.notifier.bot.send_message = Mock(return_value=mock_message)

        result = self.notifier.test_connection()

        assert result is True
        self.notifier.bot.send_message.assert_called_once()

    def test_test_connection_failure(self):
        """Test test_connection method failure."""
        self.notifier.bot.send_message = Mock(return_value=None)

        result = self.notifier.test_connection()

        assert result is False


class TestCreateNotifier:
    """Test cases for create_notifier factory function."""

    def test_create_notifier_default(self):
        """Test create_notifier with defaults."""
        with patch('telegram_notifier.Bot'):
            notifier = create_notifier(
                bot_token='test_token',
                chat_id='test_chat',
                enabled=True
            )

        assert isinstance(notifier, TelegramNotifier)
        assert notifier.bot_token == 'test_token'

    def test_create_notifier_with_args(self):
        """Test create_notifier with arguments."""
        with patch('telegram_notifier.Bot'):
            notifier = create_notifier(
                bot_token='custom_token',
                chat_id='custom_chat',
                enabled=True,
                max_retries=5
            )

        assert notifier.max_retries == 5


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
