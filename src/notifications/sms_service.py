"""
SMS Notification Service for Magnus Wheel Strategy Trading Dashboard

This module provides comprehensive SMS notification capabilities for critical earnings events
using the Twilio API. It follows the same patterns as the existing Telegram notification system
with robust error handling, retry logic, and rate limiting.

Usage:
    from src.notifications.sms_service import SMSNotifier

    notifier = SMSNotifier()
    notifier.send_earnings_alert(earnings_data)

Requirements:
    - TWILIO_ACCOUNT_SID: Twilio Account SID
    - TWILIO_AUTH_TOKEN: Twilio Auth Token
    - TWILIO_PHONE_NUMBER: Twilio phone number (from)
    - SMS_ENABLED: Set to 'true' to enable SMS notifications
    - pip install twilio

Author: Magnus Trading Dashboard
Created: 2025-11-06
Task ID: 653
"""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from decimal import Decimal
import time

from dotenv import load_dotenv

try:
    from twilio.rest import Client
    from twilio.base.exceptions import TwilioRestException
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    Client = None
    TwilioRestException = Exception


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SMSNotifier:
    """
    SMS notification handler for critical earnings events.

    This class manages all SMS notifications for the Magnus trading dashboard,
    including earnings alerts, guidance changes, and beat/miss notifications.
    It includes robust error handling, retry logic, rate limiting, and graceful
    degradation when Twilio is unavailable.

    Attributes:
        account_sid (str): Twilio account SID
        auth_token (str): Twilio auth token
        from_phone (str): Twilio phone number (sender)
        enabled (bool): Whether notifications are enabled
        client (Client): Twilio client instance
        max_retries (int): Maximum number of retry attempts
        retry_delay (float): Base delay between retries in seconds
        rate_limit_per_hour (int): Maximum SMS messages per hour
    """

    def __init__(
        self,
        account_sid: Optional[str] = None,
        auth_token: Optional[str] = None,
        from_phone: Optional[str] = None,
        enabled: Optional[bool] = None,
        max_retries: int = 3,
        retry_delay: float = 2.0,
        rate_limit_per_hour: int = 10
    ):
        """
        Initialize the SMS notifier.

        Args:
            account_sid: Twilio Account SID (defaults to TWILIO_ACCOUNT_SID env var)
            auth_token: Twilio Auth Token (defaults to TWILIO_AUTH_TOKEN env var)
            from_phone: Twilio phone number (defaults to TWILIO_PHONE_NUMBER env var)
            enabled: Enable/disable notifications (defaults to SMS_ENABLED env var)
            max_retries: Maximum number of retry attempts for failed sends
            retry_delay: Base delay between retries in seconds
            rate_limit_per_hour: Maximum SMS messages per hour (default 10)
        """
        # Load environment variables
        load_dotenv()

        # Configuration
        self.account_sid = account_sid or os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = auth_token or os.getenv('TWILIO_AUTH_TOKEN')
        self.from_phone = from_phone or os.getenv('TWILIO_PHONE_NUMBER')
        self.enabled = enabled if enabled is not None else \
            os.getenv('SMS_ENABLED', 'false').lower() == 'true'
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.rate_limit_per_hour = rate_limit_per_hour

        # Rate limiting tracking
        self._message_timestamps: List[datetime] = []

        # Check if twilio is installed
        if not TWILIO_AVAILABLE:
            logger.warning(
                "twilio package not installed. "
                "Install with: pip install twilio"
            )
            self.client = None
            self.enabled = False
            return

        # Initialize Twilio client if enabled and configured
        if self.enabled and self.account_sid and self.auth_token and self.from_phone:
            try:
                self.client = Client(self.account_sid, self.auth_token)
                logger.info("SMS notifier initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Twilio client: {e}")
                self.client = None
                self.enabled = False
        else:
            self.client = None
            if self.enabled:
                logger.warning(
                    "SMS enabled but missing credentials. "
                    "Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_PHONE_NUMBER in .env"
                )
                self.enabled = False

    def send_earnings_alert(
        self,
        earnings_data: Dict[str, Any],
        to_phone: str
    ) -> Optional[str]:
        """
        Send SMS notification for upcoming earnings event.

        Args:
            earnings_data: Dictionary containing earnings information with keys:
                - symbol (str): Stock ticker symbol
                - earnings_date (date): Earnings announcement date
                - earnings_time (str): BMO or AMC
                - eps_estimate (Decimal): EPS estimate
                - current_price (Decimal): Current stock price
                - expected_move (Decimal): Expected price move
            to_phone: Phone number to send to (E.164 format: +1234567890)

        Returns:
            Twilio message SID if successful, None otherwise
        """
        if not self._is_available():
            return None

        if not self._check_rate_limit():
            logger.warning(f"Rate limit exceeded ({self.rate_limit_per_hour}/hour)")
            return None

        try:
            # Extract data with safe defaults
            symbol = earnings_data.get('symbol', 'N/A')
            earnings_date = self._format_date(earnings_data.get('earnings_date'))
            earnings_time = earnings_data.get('earnings_time', 'N/A')
            eps_estimate = self._format_currency(earnings_data.get('eps_estimate'))
            current_price = self._format_currency(earnings_data.get('current_price'))
            expected_move = self._format_currency(earnings_data.get('expected_move'))

            # Build concise SMS message (160 char limit for single SMS)
            message = (
                f"EARNINGS ALERT: {symbol}\n"
                f"Date: {earnings_date} {earnings_time}\n"
                f"EPS Est: {eps_estimate}\n"
                f"Price: {current_price}\n"
                f"Expected Move: {expected_move}"
            )

            return self._send_sms(to_phone, message)

        except Exception as e:
            logger.error(f"Error formatting earnings alert: {e}")
            return None

    def send_guidance_change_alert(
        self,
        guidance_data: Dict[str, Any],
        to_phone: str
    ) -> Optional[str]:
        """
        Send SMS notification for guidance changes.

        Args:
            guidance_data: Dictionary containing guidance change information
            to_phone: Phone number to send to

        Returns:
            Twilio message SID if successful, None otherwise
        """
        if not self._is_available():
            return None

        if not self._check_rate_limit():
            logger.warning(f"Rate limit exceeded ({self.rate_limit_per_hour}/hour)")
            return None

        try:
            symbol = guidance_data.get('symbol', 'N/A')
            change_type = guidance_data.get('change_type', 'N/A')
            old_guidance = guidance_data.get('old_guidance', 'N/A')
            new_guidance = guidance_data.get('new_guidance', 'N/A')

            message = (
                f"GUIDANCE CHANGE: {symbol}\n"
                f"Type: {change_type}\n"
                f"Old: {old_guidance}\n"
                f"New: {new_guidance}"
            )

            return self._send_sms(to_phone, message)

        except Exception as e:
            logger.error(f"Error formatting guidance change alert: {e}")
            return None

    def send_beat_miss_alert(
        self,
        earnings_result: Dict[str, Any],
        to_phone: str
    ) -> Optional[str]:
        """
        Send SMS notification for earnings beat/miss results.

        Args:
            earnings_result: Dictionary containing earnings results
            to_phone: Phone number to send to

        Returns:
            Twilio message SID if successful, None otherwise
        """
        if not self._is_available():
            return None

        if not self._check_rate_limit():
            logger.warning(f"Rate limit exceeded ({self.rate_limit_per_hour}/hour)")
            return None

        try:
            symbol = earnings_result.get('symbol', 'N/A')
            status = earnings_result.get('status', 'N/A')  # beat, miss, inline
            eps_actual = self._format_currency(earnings_result.get('eps_actual'))
            eps_estimate = self._format_currency(earnings_result.get('eps_estimate'))
            surprise_pct = earnings_result.get('surprise_pct', 0)
            price_move = earnings_result.get('price_move_percent', 0)

            # Determine emoji/indicator
            if status == 'beat':
                indicator = "BEAT"
            elif status == 'miss':
                indicator = "MISS"
            else:
                indicator = "INLINE"

            message = (
                f"EARNINGS {indicator}: {symbol}\n"
                f"Actual: {eps_actual} (Est: {eps_estimate})\n"
                f"Surprise: {surprise_pct:+.1f}%\n"
                f"Price Move: {price_move:+.1f}%"
            )

            return self._send_sms(to_phone, message)

        except Exception as e:
            logger.error(f"Error formatting beat/miss alert: {e}")
            return None

    def send_custom_message(
        self,
        message: str,
        to_phone: str
    ) -> Optional[str]:
        """
        Send a custom SMS message.

        Args:
            message: Message text to send
            to_phone: Phone number to send to

        Returns:
            Twilio message SID if successful, None otherwise
        """
        if not self._is_available():
            return None

        if not self._check_rate_limit():
            logger.warning(f"Rate limit exceeded ({self.rate_limit_per_hour}/hour)")
            return None

        return self._send_sms(to_phone, message)

    def _send_sms(self, to_phone: str, message: str) -> Optional[str]:
        """
        Internal method to send SMS with retry logic and error handling.

        Args:
            to_phone: Destination phone number (E.164 format)
            message: Message text to send

        Returns:
            Message SID if successful, None otherwise
        """
        if not self._is_available():
            return None

        for attempt in range(self.max_retries):
            try:
                message_obj = self.client.messages.create(
                    body=message,
                    from_=self.from_phone,
                    to=to_phone
                )

                # Track for rate limiting
                self._message_timestamps.append(datetime.now())

                logger.info(f"SMS sent successfully: {message_obj.sid}")
                return message_obj.sid

            except TwilioRestException as e:
                logger.error(f"Twilio error: {e.msg} (Code: {e.code})")

                # Don't retry on certain errors
                if e.code in [21211, 21606, 21614]:  # Invalid phone number errors
                    logger.error(f"Invalid phone number: {to_phone}")
                    return None

                # Retry on other errors
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2 ** attempt)
                    logger.warning(f"Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    return None

            except Exception as e:
                logger.error(f"Unexpected error sending SMS: {e}")

                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2 ** attempt)
                    logger.warning(f"Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    return None

        logger.error(f"Failed to send SMS after {self.max_retries} attempts")
        return None

    def _check_rate_limit(self) -> bool:
        """
        Check if we're within the rate limit.

        Returns:
            True if within limit, False otherwise
        """
        # Clean up old timestamps (older than 1 hour)
        cutoff_time = datetime.now() - timedelta(hours=1)
        self._message_timestamps = [
            ts for ts in self._message_timestamps if ts > cutoff_time
        ]

        # Check if we're under the limit
        return len(self._message_timestamps) < self.rate_limit_per_hour

    def _is_available(self) -> bool:
        """
        Check if SMS notifications are available and configured.

        Returns:
            True if available, False otherwise
        """
        if not self.enabled:
            logger.debug("SMS notifications are disabled")
            return False

        if not self.client:
            logger.debug("Twilio client not initialized")
            return False

        return True

    @staticmethod
    def _format_currency(value: Optional[Any]) -> str:
        """
        Format a value as currency.

        Args:
            value: Numeric value to format

        Returns:
            Formatted currency string
        """
        if value is None:
            return "N/A"

        try:
            if isinstance(value, (int, float, Decimal)):
                num_value = float(value)
                return f"${num_value:.2f}"
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
                return value.strftime("%m/%d")
            elif hasattr(value, 'strftime'):
                return value.strftime("%m/%d")
            return str(value)
        except (ValueError, AttributeError):
            return str(value)

    def get_client_info(self) -> Optional[Dict[str, Any]]:
        """
        Get information about the Twilio account.

        Returns:
            Dictionary with account information or None if unavailable
        """
        if not self._is_available():
            return None

        try:
            account = self.client.api.accounts(self.account_sid).fetch()
            return {
                'sid': account.sid,
                'friendly_name': account.friendly_name,
                'status': account.status,
                'type': account.type
            }
        except Exception as e:
            logger.error(f"Error getting account info: {e}")
            return None

    def test_connection(self, test_phone: str) -> bool:
        """
        Test the Twilio connection by sending a test message.

        Args:
            test_phone: Phone number to send test message to

        Returns:
            True if successful, False otherwise
        """
        if not self._is_available():
            logger.error("SMS not available for testing")
            return False

        try:
            test_message = (
                f"Magnus Trading Dashboard SMS Test\n"
                f"Time: {datetime.now().strftime('%m/%d %I:%M%p')}"
            )

            message_sid = self._send_sms(test_phone, test_message)
            if message_sid:
                logger.info(f"Test message sent successfully: {message_sid}")
                return True
            else:
                logger.error("Failed to send test message")
                return False

        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False


# Convenience function for quick access
def create_notifier(**kwargs) -> SMSNotifier:
    """
    Create and return a configured SMSNotifier instance.

    Args:
        **kwargs: Arguments to pass to SMSNotifier constructor

    Returns:
        SMSNotifier instance
    """
    return SMSNotifier(**kwargs)


if __name__ == "__main__":
    # Example usage and testing
    print("SMS Notifier - Example Usage\n")

    notifier = SMSNotifier()

    # Test connection (requires TEST_PHONE_NUMBER env var)
    test_phone = os.getenv('TEST_PHONE_NUMBER')

    if test_phone:
        print("Testing connection...")
        if notifier.test_connection(test_phone):
            print("Connection successful!")
        else:
            print("Connection failed or disabled")

        # Example: Send a test earnings alert
        sample_earnings = {
            'symbol': 'NVDA',
            'earnings_date': datetime.now().date(),
            'earnings_time': 'AMC',
            'eps_estimate': Decimal('5.50'),
            'current_price': Decimal('485.50'),
            'expected_move': Decimal('24.00')
        }

        print("\nSending test earnings alert...")
        message_sid = notifier.send_earnings_alert(sample_earnings, test_phone)
        if message_sid:
            print(f"Alert sent! Message SID: {message_sid}")
        else:
            print("Alert not sent (disabled or error)")
    else:
        print("SMS not configured. To enable:")
        print("1. Get Twilio credentials: https://www.twilio.com/try-twilio")
        print("2. Add to .env:")
        print("   TWILIO_ACCOUNT_SID=your_account_sid")
        print("   TWILIO_AUTH_TOKEN=your_auth_token")
        print("   TWILIO_PHONE_NUMBER=+1234567890")
        print("   SMS_ENABLED=true")
        print("   TEST_PHONE_NUMBER=+1234567890")
