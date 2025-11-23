"""
Telegram Notification System for Magnus Wheel Strategy Trading Dashboard

This module provides comprehensive Telegram notification capabilities for Xtrades trade alerts.
It handles new trades, trade updates, trade closures, and sync errors with proper formatting,
error handling, and retry logic.

Usage:
    from telegram_notifier import TelegramNotifier

    notifier = TelegramNotifier()
    notifier.send_new_trade_alert(trade_data)

Requirements:
    - TELEGRAM_BOT_TOKEN: Bot token from @BotFather
    - TELEGRAM_CHAT_ID: Chat ID from @userinfobot
    - TELEGRAM_ENABLED: Set to 'true' to enable notifications

Author: Magnus Trading Dashboard
Created: 2025-11-02
"""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from decimal import Decimal
import time

from dotenv import load_dotenv

try:
    from telegram import Bot
    from telegram.error import TelegramError, NetworkError, RetryAfter, TimedOut
    from telegram.constants import ParseMode
    TELEGRAM_AVAILABLE = True
except ImportError:
    try:
        # Try old version
        from telegram import Bot, ParseMode
        from telegram.error import TelegramError, NetworkError, RetryAfter, TimedOut
        TELEGRAM_AVAILABLE = True
    except ImportError:
        TELEGRAM_AVAILABLE = False
        Bot = None
        ParseMode = None
        TelegramError = Exception
        NetworkError = Exception
        RetryAfter = Exception
        TimedOut = Exception


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TelegramNotifier:
    """
    Telegram notification handler for Xtrades trading alerts.

    This class manages all Telegram notifications for the Magnus trading dashboard,
    including new trades, updates, closures, and errors. It includes robust error
    handling, retry logic, and graceful degradation when Telegram is unavailable.

    Attributes:
        bot_token (str): Telegram bot token
        chat_id (str): Telegram chat ID for sending messages
        enabled (bool): Whether notifications are enabled
        bot (Bot): Telegram bot instance
        max_retries (int): Maximum number of retry attempts
        retry_delay (float): Base delay between retries in seconds
    """

    def __init__(
        self,
        bot_token: Optional[str] = None,
        chat_id: Optional[str] = None,
        enabled: Optional[bool] = None,
        max_retries: int = 3,
        retry_delay: float = 2.0
    ):
        """
        Initialize the Telegram notifier.

        Args:
            bot_token: Telegram bot token (defaults to TELEGRAM_BOT_TOKEN env var)
            chat_id: Telegram chat ID (defaults to TELEGRAM_CHAT_ID env var)
            enabled: Enable/disable notifications (defaults to TELEGRAM_ENABLED env var)
            max_retries: Maximum number of retry attempts for failed sends
            retry_delay: Base delay between retries in seconds
        """
        # Load environment variables
        load_dotenv()

        # Configuration
        self.bot_token = bot_token or os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = chat_id or os.getenv('TELEGRAM_CHAT_ID')
        self.enabled = enabled if enabled is not None else \
            os.getenv('TELEGRAM_ENABLED', 'false').lower() == 'true'
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        # Check if python-telegram-bot is installed
        if not TELEGRAM_AVAILABLE:
            logger.warning(
                "python-telegram-bot package not installed. "
                "Install with: pip install python-telegram-bot"
            )
            self.bot = None
            self.enabled = False
            return

        # Initialize bot if enabled and configured
        if self.enabled and self.bot_token and self.chat_id:
            try:
                self.bot = Bot(token=self.bot_token)
                logger.info("Telegram notifier initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Telegram bot: {e}")
                self.bot = None
                self.enabled = False
        else:
            self.bot = None
            if self.enabled:
                logger.warning(
                    "Telegram enabled but missing credentials. "
                    "Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env"
                )
                self.enabled = False

    def send_new_trade_alert(self, trade_data: Dict[str, Any]) -> Optional[str]:
        """
        Send notification for a new trade alert.

        Args:
            trade_data: Dictionary containing trade information with keys:
                - profile_username (str): Xtrades profile username
                - ticker (str): Stock ticker symbol
                - strategy (str): Options strategy type
                - action (str): Trade action (BTO, STO, etc.)
                - entry_price (Decimal): Entry price
                - quantity (int): Number of contracts
                - strike_price (Decimal): Strike price
                - expiration_date (date): Option expiration date
                - alert_timestamp (datetime): When alert was created
                - alert_text (str, optional): Full alert text

        Returns:
            Telegram message ID if successful, None otherwise
        """
        if not self._is_available():
            return None

        try:
            # Extract data with safe defaults
            username = trade_data.get('profile_username', 'Unknown')
            ticker = trade_data.get('ticker', 'N/A')
            strategy = trade_data.get('strategy', 'N/A')
            action = trade_data.get('action', 'N/A')
            entry_price = self._format_currency(trade_data.get('entry_price'))
            quantity = trade_data.get('quantity', 0)
            strike = self._format_currency(trade_data.get('strike_price'))
            exp_date = self._format_date(trade_data.get('expiration_date'))
            alert_time = self._format_datetime(trade_data.get('alert_timestamp'))

            # Build message
            message = (
                f"\U0001F195 *NEW TRADE ALERT*\n\n"
                f"\U0001F464 Profile: `{username}`\n"
                f"\U0001F4C8 Ticker: *{ticker}*\n"
                f"\U0001F4BC Strategy: `{strategy}`\n"
                f"\U0001F4CA Action: `{action}`\n"
                f"\U0001F4B0 Entry: `{entry_price}` x {quantity}\n"
                f"\U0001F3AF Strike: `{strike}`\n"
                f"\U0001F4C5 Expiration: `{exp_date}`\n"
                f"\U0001F553 Alert Time: `{alert_time}`\n"
            )

            # Add alert text if available
            if trade_data.get('alert_text'):
                message += f"\n\U0001F4DD Alert: _{trade_data['alert_text']}_\n"

            # Add link to Xtrades profile
            profile_url = f"https://app.xtrades.net/profile/{username}"
            message += f"\n[View on Xtrades]({profile_url})"

            return self._send_message(message)

        except Exception as e:
            logger.error(f"Error formatting new trade alert: {e}")
            return None

    def send_trade_update_alert(
        self,
        trade_data: Dict[str, Any],
        changes: Dict[str, Any]
    ) -> Optional[str]:
        """
        Send notification for a trade update.

        Args:
            trade_data: Current trade data
            changes: Dictionary of changes with 'before' and 'after' values
                Example: {'exit_price': {'before': None, 'after': 2.50}}

        Returns:
            Telegram message ID if successful, None otherwise
        """
        if not self._is_available():
            return None

        try:
            username = trade_data.get('profile_username', 'Unknown')
            ticker = trade_data.get('ticker', 'N/A')
            strategy = trade_data.get('strategy', 'N/A')

            message = (
                f"\U0001F504 *TRADE UPDATE*\n\n"
                f"\U0001F464 Profile: `{username}`\n"
                f"\U0001F4C8 Ticker: *{ticker}*\n"
                f"\U0001F4BC Strategy: `{strategy}`\n\n"
                f"\U0001F4CA Changes:\n"
            )

            # Format changes
            for field, change in changes.items():
                before = change.get('before', 'N/A')
                after = change.get('after', 'N/A')

                # Format field name nicely
                field_name = field.replace('_', ' ').title()

                # Format values based on field type
                if 'price' in field.lower():
                    before = self._format_currency(before)
                    after = self._format_currency(after)
                elif 'pnl' in field.lower() and 'percent' not in field.lower():
                    before = self._format_currency(before, include_sign=True)
                    after = self._format_currency(after, include_sign=True)
                elif 'percent' in field.lower():
                    before = self._format_percent(before)
                    after = self._format_percent(after)
                elif 'date' in field.lower():
                    before = self._format_date(before)
                    after = self._format_date(after)

                message += f"  \u2022 {field_name}: `{before}` \u2192 `{after}`\n"

            return self._send_message(message)

        except Exception as e:
            logger.error(f"Error formatting trade update alert: {e}")
            return None

    def send_trade_closed_alert(self, trade_data: Dict[str, Any]) -> Optional[str]:
        """
        Send notification for a closed trade.

        Args:
            trade_data: Trade data including P&L information

        Returns:
            Telegram message ID if successful, None otherwise
        """
        if not self._is_available():
            return None

        try:
            username = trade_data.get('profile_username', 'Unknown')
            ticker = trade_data.get('ticker', 'N/A')
            strategy = trade_data.get('strategy', 'N/A')
            pnl = trade_data.get('pnl', 0)
            pnl_percent = trade_data.get('pnl_percent', 0)
            entry_date = trade_data.get('entry_date')
            exit_date = trade_data.get('exit_date')

            # Calculate duration
            duration_str = "N/A"
            if entry_date and exit_date:
                duration = exit_date - entry_date
                duration_str = f"{duration.days} days"

            # Determine if profit or loss
            pnl_float = float(pnl) if pnl else 0
            pnl_percent_float = float(pnl_percent) if pnl_percent else 0

            if pnl_float > 0:
                emoji = "\U0001F4B9"  # Green chart up
                status = "PROFIT"
            elif pnl_float < 0:
                emoji = "\U0001F4C9"  # Red chart down
                status = "LOSS"
            else:
                emoji = "\U0001F4CA"  # Neutral
                status = "BREAKEVEN"

            message = (
                f"{emoji} *TRADE CLOSED - {status}*\n\n"
                f"\U0001F464 Profile: `{username}`\n"
                f"\U0001F4C8 Ticker: *{ticker}*\n"
                f"\U0001F4BC Strategy: `{strategy}`\n\n"
                f"\U0001F4B0 P&L: `{self._format_currency(pnl, include_sign=True)}`\n"
                f"\U0001F4CA Percent: `{self._format_percent(pnl_percent, include_sign=True)}`\n"
                f"\U0001F4C5 Duration: `{duration_str}`\n"
                f"\U0001F553 Closed: `{self._format_datetime(exit_date)}`\n"
            )

            return self._send_message(message)

        except Exception as e:
            logger.error(f"Error formatting trade closed alert: {e}")
            return None

    def send_sync_error_alert(
        self,
        error_msg: str,
        profiles: Optional[List[str]] = None
    ) -> Optional[str]:
        """
        Send notification for sync errors.

        Args:
            error_msg: Error message to send
            profiles: List of affected profile usernames (optional)

        Returns:
            Telegram message ID if successful, None otherwise
        """
        if not self._is_available():
            return None

        try:
            message = (
                f"\u26A0\uFE0F *SYNC ERROR*\n\n"
                f"\U0001F6A8 Error: {error_msg}\n"
            )

            if profiles:
                message += f"\n\U0001F464 Affected Profiles:\n"
                for profile in profiles:
                    message += f"  \u2022 `{profile}`\n"

            message += f"\n\U0001F553 Time: `{self._format_datetime(datetime.now())}`"

            return self._send_message(message)

        except Exception as e:
            logger.error(f"Error formatting sync error alert: {e}")
            return None

    def send_daily_summary(self, summary_data: Dict[str, Any]) -> Optional[str]:
        """
        Send daily summary of trading activity.

        Args:
            summary_data: Dictionary containing summary statistics:
                - total_trades (int): Number of trades
                - new_trades (int): New trades today
                - closed_trades (int): Trades closed today
                - total_pnl (Decimal): Total P&L
                - win_rate (float): Win rate percentage
                - active_profiles (int): Number of active profiles

        Returns:
            Telegram message ID if successful, None otherwise
        """
        if not self._is_available():
            return None

        try:
            message = (
                f"\U0001F4CA *DAILY TRADING SUMMARY*\n\n"
                f"\U0001F4C5 Date: `{self._format_date(datetime.now())}`\n\n"
                f"\U0001F4C8 Activity:\n"
                f"  \u2022 New Trades: `{summary_data.get('new_trades', 0)}`\n"
                f"  \u2022 Closed Trades: `{summary_data.get('closed_trades', 0)}`\n"
                f"  \u2022 Total Active: `{summary_data.get('total_trades', 0)}`\n\n"
                f"\U0001F4B0 Performance:\n"
                f"  \u2022 Total P&L: `{self._format_currency(summary_data.get('total_pnl', 0), include_sign=True)}`\n"
                f"  \u2022 Win Rate: `{self._format_percent(summary_data.get('win_rate', 0))}`\n\n"
                f"\U0001F464 Active Profiles: `{summary_data.get('active_profiles', 0)}`\n"
            )

            return self._send_message(message)

        except Exception as e:
            logger.error(f"Error formatting daily summary: {e}")
            return None

    def send_custom_message(self, message: str, parse_mode: str = "Markdown") -> Optional[str]:
        """
        Send a custom formatted message.

        Args:
            message: Message text to send
            parse_mode: Telegram parse mode ('Markdown', 'HTML', or None)

        Returns:
            Telegram message ID if successful, None otherwise
        """
        if not self._is_available():
            return None

        return self._send_message(message, parse_mode=parse_mode)

    def _send_message(
        self,
        text: str,
        parse_mode: str = "Markdown",
        disable_web_page_preview: bool = True
    ) -> Optional[str]:
        """
        Internal method to send messages with retry logic and error handling.

        Args:
            text: Message text to send
            parse_mode: Telegram parse mode
            disable_web_page_preview: Disable link previews

        Returns:
            Message ID if successful, None otherwise
        """
        if not self._is_available():
            return None

        for attempt in range(self.max_retries):
            try:
                # Handle both async (v20+) and sync (older) versions
                import asyncio
                import inspect

                send_result = self.bot.send_message(
                    chat_id=self.chat_id,
                    text=text,
                    parse_mode=parse_mode,
                    disable_web_page_preview=disable_web_page_preview
                )

                # If it's a coroutine (async), run it with asyncio
                if inspect.iscoroutine(send_result):
                    try:
                        loop = asyncio.get_event_loop()
                        if loop.is_closed():
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                        message = loop.run_until_complete(send_result)
                    except RuntimeError:
                        # No event loop, create new one
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        message = loop.run_until_complete(send_result)
                else:
                    message = send_result

                logger.info(f"Telegram message sent successfully: {message.message_id}")
                return str(message.message_id)

            except RetryAfter as e:
                # Rate limiting - wait the required time
                wait_time = e.retry_after
                logger.warning(f"Rate limited. Waiting {wait_time} seconds...")
                time.sleep(wait_time)

            except TimedOut:
                # Timeout - retry with exponential backoff
                wait_time = self.retry_delay * (2 ** attempt)
                logger.warning(f"Request timed out. Retrying in {wait_time}s...")
                time.sleep(wait_time)

            except NetworkError as e:
                # Network error - retry with exponential backoff
                wait_time = self.retry_delay * (2 ** attempt)
                logger.warning(f"Network error: {e}. Retrying in {wait_time}s...")
                time.sleep(wait_time)

            except TelegramError as e:
                # Other Telegram errors - log and return None
                logger.error(f"Telegram error: {e}")
                return None

            except Exception as e:
                # Unexpected error - log and return None
                logger.error(f"Unexpected error sending Telegram message: {e}")
                return None

        logger.error(f"Failed to send message after {self.max_retries} attempts")
        return None

    def _is_available(self) -> bool:
        """
        Check if Telegram notifications are available and configured.

        Returns:
            True if available, False otherwise
        """
        if not self.enabled:
            logger.debug("Telegram notifications are disabled")
            return False

        if not self.bot:
            logger.debug("Telegram bot not initialized")
            return False

        return True

    @staticmethod
    def _format_currency(
        value: Optional[Any],
        include_sign: bool = False
    ) -> str:
        """
        Format a value as currency.

        Args:
            value: Numeric value to format
            include_sign: Include + sign for positive values

        Returns:
            Formatted currency string
        """
        if value is None:
            return "N/A"

        try:
            if isinstance(value, (int, float, Decimal)):
                num_value = float(value)
                if include_sign and num_value > 0:
                    return f"+${num_value:,.2f}"
                elif num_value < 0:
                    return f"-${abs(num_value):,.2f}"
                else:
                    return f"${num_value:,.2f}"
            return str(value)
        except (ValueError, TypeError):
            return str(value)

    @staticmethod
    def _format_percent(
        value: Optional[Any],
        include_sign: bool = False
    ) -> str:
        """
        Format a value as percentage.

        Args:
            value: Numeric value to format
            include_sign: Include + sign for positive values

        Returns:
            Formatted percentage string
        """
        if value is None:
            return "N/A"

        try:
            if isinstance(value, (int, float, Decimal)):
                num_value = float(value)
                if include_sign and num_value > 0:
                    return f"+{num_value:.2f}%"
                else:
                    return f"{num_value:.2f}%"
            return str(value)
        except (ValueError, TypeError):
            return str(value)

    @staticmethod
    def _format_date(value: Optional[Any]) -> str:
        """
        Format a date value.

        Args:
            value: Date or datetime to format

        Returns:
            Formatted date string
        """
        if value is None:
            return "N/A"

        try:
            if isinstance(value, datetime):
                return value.strftime("%Y-%m-%d")
            elif hasattr(value, 'strftime'):
                return value.strftime("%Y-%m-%d")
            return str(value)
        except (ValueError, AttributeError):
            return str(value)

    @staticmethod
    def _format_datetime(value: Optional[Any]) -> str:
        """
        Format a datetime value.

        Args:
            value: Datetime to format

        Returns:
            Formatted datetime string
        """
        if value is None:
            return "N/A"

        try:
            if isinstance(value, datetime):
                return value.strftime("%Y-%m-%d %I:%M %p")
            elif hasattr(value, 'strftime'):
                return value.strftime("%Y-%m-%d %I:%M %p")
            return str(value)
        except (ValueError, AttributeError):
            return str(value)

    def get_bot_info(self) -> Optional[Dict[str, Any]]:
        """
        Get information about the Telegram bot.

        Returns:
            Dictionary with bot information or None if unavailable
        """
        if not self._is_available():
            return None

        try:
            bot_info = self.bot.get_me()
            return {
                'id': bot_info.id,
                'username': bot_info.username,
                'first_name': bot_info.first_name,
                'is_bot': bot_info.is_bot
            }
        except Exception as e:
            logger.error(f"Error getting bot info: {e}")
            return None

    def test_connection(self) -> bool:
        """
        Test the Telegram connection by sending a test message.

        Returns:
            True if successful, False otherwise
        """
        if not self._is_available():
            logger.error("Telegram not available for testing")
            return False

        try:
            test_message = (
                "\u2705 *Telegram Connection Test*\n\n"
                f"Magnus Trading Dashboard is successfully connected!\n\n"
                f"\U0001F553 Test Time: `{self._format_datetime(datetime.now())}`"
            )

            message_id = self._send_message(test_message)
            if message_id:
                logger.info(f"Test message sent successfully: {message_id}")
                return True
            else:
                logger.error("Failed to send test message")
                return False

        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False


# Convenience function for quick access
def create_notifier(**kwargs) -> TelegramNotifier:
    """
    Create and return a configured TelegramNotifier instance.

    Args:
        **kwargs: Arguments to pass to TelegramNotifier constructor

    Returns:
        TelegramNotifier instance
    """
    return TelegramNotifier(**kwargs)


if __name__ == "__main__":
    # Example usage and testing
    print("Telegram Notifier - Example Usage\n")

    notifier = TelegramNotifier()

    # Test connection
    print("Testing connection...")
    if notifier.test_connection():
        print("Connection successful!")
    else:
        print("Connection failed or disabled")

    # Example: Send a test trade alert
    sample_trade = {
        'profile_username': 'testuser',
        'ticker': 'AAPL',
        'strategy': 'CSP',
        'action': 'STO',
        'entry_price': 2.50,
        'quantity': 1,
        'strike_price': 170.00,
        'expiration_date': datetime.now().date(),
        'alert_timestamp': datetime.now(),
        'alert_text': 'Test trade alert'
    }

    print("\nSending test trade alert...")
    message_id = notifier.send_new_trade_alert(sample_trade)
    if message_id:
        print(f"Alert sent! Message ID: {message_id}")
    else:
        print("Alert not sent (disabled or error)")
