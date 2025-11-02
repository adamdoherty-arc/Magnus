# Telegram Notifier - Usage Examples

Comprehensive examples for using the Telegram notification system in the Magnus Wheel Strategy Trading Dashboard.

## Table of Contents

1. [Basic Usage](#basic-usage)
2. [Trade Notifications](#trade-notifications)
3. [Integration with Xtrades Sync](#integration-with-xtrades-sync)
4. [Database Integration](#database-integration)
5. [Scheduled Notifications](#scheduled-notifications)
6. [Error Handling](#error-handling)
7. [Advanced Patterns](#advanced-patterns)

---

## Basic Usage

### Simple Initialization

```python
from telegram_notifier import TelegramNotifier

# Initialize with environment variables
notifier = TelegramNotifier()

# Test the connection
if notifier.test_connection():
    print("Connected to Telegram!")
```

### Custom Configuration

```python
# Initialize with custom settings
notifier = TelegramNotifier(
    bot_token='your_bot_token',
    chat_id='your_chat_id',
    enabled=True,
    max_retries=5,
    retry_delay=3.0
)
```

### Check Configuration

```python
# Verify bot information
bot_info = notifier.get_bot_info()
if bot_info:
    print(f"Bot: @{bot_info['username']}")
    print(f"Name: {bot_info['first_name']}")
```

---

## Trade Notifications

### New Trade Alert

```python
from datetime import datetime, date
from decimal import Decimal

# Prepare trade data
trade_data = {
    'profile_username': 'traderJoe',
    'ticker': 'AAPL',
    'strategy': 'CSP',
    'action': 'STO',
    'entry_price': Decimal('2.50'),
    'quantity': 1,
    'strike_price': Decimal('170.00'),
    'expiration_date': date(2025, 12, 20),
    'alert_timestamp': datetime.now(),
    'alert_text': 'AAPL CSP: STO 1x $170 PUT @ $2.50'
}

# Send notification
message_id = notifier.send_new_trade_alert(trade_data)
if message_id:
    print(f"Alert sent! Message ID: {message_id}")
```

### Trade Update Alert

```python
# Trade data
trade_data = {
    'profile_username': 'traderJoe',
    'ticker': 'AAPL',
    'strategy': 'CSP'
}

# Define what changed
changes = {
    'exit_price': {
        'before': None,
        'after': Decimal('1.25')
    },
    'status': {
        'before': 'open',
        'after': 'closing'
    },
    'pnl': {
        'before': Decimal('0'),
        'after': Decimal('125.00')
    }
}

# Send update notification
message_id = notifier.send_trade_update_alert(trade_data, changes)
```

### Trade Closed Alert

```python
from datetime import datetime, timedelta

# Complete trade data with P&L
closed_trade = {
    'profile_username': 'traderJoe',
    'ticker': 'AAPL',
    'strategy': 'CSP',
    'pnl': Decimal('125.00'),
    'pnl_percent': Decimal('50.00'),
    'entry_date': datetime.now() - timedelta(days=30),
    'exit_date': datetime.now()
}

# Send closure notification
message_id = notifier.send_trade_closed_alert(closed_trade)
```

### Multiple Notification Types

```python
def notify_trade_lifecycle(trade_id):
    """Send notifications for all stages of a trade."""

    # Get trade from database
    trade = get_trade_from_db(trade_id)

    # New trade notification
    if trade['status'] == 'open' and not was_notified(trade_id, 'new_trade'):
        notifier.send_new_trade_alert(trade)
        mark_notified(trade_id, 'new_trade')

    # Update notification
    if has_changes(trade_id):
        changes = get_changes(trade_id)
        notifier.send_trade_update_alert(trade, changes)
        mark_notified(trade_id, 'trade_update')

    # Closure notification
    if trade['status'] == 'closed' and not was_notified(trade_id, 'trade_closed'):
        notifier.send_trade_closed_alert(trade)
        mark_notified(trade_id, 'trade_closed')
```

---

## Integration with Xtrades Sync

### Basic Sync with Notifications

```python
import psycopg2
from telegram_notifier import TelegramNotifier

def sync_xtrades_profiles():
    """Sync Xtrades profiles and send notifications for new trades."""

    notifier = TelegramNotifier()
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cursor = conn.cursor()

    try:
        # Get active profiles
        cursor.execute("""
            SELECT id, username FROM xtrades_profiles
            WHERE active = TRUE
        """)
        profiles = cursor.fetchall()

        for profile_id, username in profiles:
            # Scrape new trades (your scraping logic here)
            new_trades = scrape_xtrades_profile(username)

            for trade in new_trades:
                # Insert trade
                cursor.execute("""
                    INSERT INTO xtrades_trades
                    (profile_id, ticker, strategy, action, entry_price, ...)
                    VALUES (%s, %s, %s, %s, %s, ...)
                    RETURNING id
                """, (profile_id, trade['ticker'], ...))

                trade_id = cursor.fetchone()[0]

                # Send notification
                trade['profile_username'] = username
                message_id = notifier.send_new_trade_alert(trade)

                # Log notification
                if message_id:
                    cursor.execute("""
                        INSERT INTO xtrades_notifications
                        (trade_id, notification_type, telegram_message_id, status)
                        VALUES (%s, %s, %s, %s)
                    """, (trade_id, 'new_trade', message_id, 'sent'))

        conn.commit()

    except Exception as e:
        conn.rollback()
        notifier.send_sync_error_alert(str(e), [p[1] for p in profiles])

    finally:
        conn.close()
```

### Detect and Notify Trade Changes

```python
def check_and_notify_updates():
    """Check for trade updates and send notifications."""

    notifier = TelegramNotifier()
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cursor = conn.cursor()

    try:
        # Get trades that might have updates
        cursor.execute("""
            SELECT t.id, t.ticker, t.strategy, t.exit_price, t.status,
                   p.username
            FROM xtrades_trades t
            JOIN xtrades_profiles p ON t.profile_id = p.id
            WHERE t.status IN ('open', 'closing')
            AND t.updated_at > NOW() - INTERVAL '1 hour'
        """)

        for trade in cursor.fetchall():
            trade_id = trade[0]

            # Check for changes (your change detection logic)
            changes = detect_changes(trade_id)

            if changes:
                trade_data = {
                    'profile_username': trade[5],
                    'ticker': trade[1],
                    'strategy': trade[2]
                }

                # Send update notification
                message_id = notifier.send_trade_update_alert(
                    trade_data,
                    changes
                )

                # Log notification
                if message_id:
                    cursor.execute("""
                        INSERT INTO xtrades_notifications
                        (trade_id, notification_type, telegram_message_id, status)
                        VALUES (%s, %s, %s, %s)
                    """, (trade_id, 'trade_update', message_id, 'sent'))

        conn.commit()

    except Exception as e:
        conn.rollback()
        notifier.send_sync_error_alert(f"Update check failed: {e}")

    finally:
        conn.close()
```

---

## Database Integration

### Complete Integration Example

```python
import psycopg2
from psycopg2.extras import RealDictCursor
from telegram_notifier import TelegramNotifier
from datetime import datetime

class XtradesNotificationManager:
    """Manages Xtrades trade notifications with database tracking."""

    def __init__(self):
        self.notifier = TelegramNotifier()
        self.db_url = os.getenv('DATABASE_URL')

    def get_connection(self):
        """Get database connection."""
        return psycopg2.connect(
            self.db_url,
            cursor_factory=RealDictCursor
        )

    def notify_new_trades(self):
        """Send notifications for new trades not yet notified."""

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Get trades without notifications
            cursor.execute("""
                SELECT t.*, p.username as profile_username
                FROM xtrades_trades t
                JOIN xtrades_profiles p ON t.profile_id = p.id
                LEFT JOIN xtrades_notifications n
                    ON t.id = n.trade_id
                    AND n.notification_type = 'new_trade'
                WHERE n.id IS NULL
                AND t.status = 'open'
                ORDER BY t.alert_timestamp DESC
            """)

            trades = cursor.fetchall()

            for trade in trades:
                try:
                    # Send notification
                    message_id = self.notifier.send_new_trade_alert(dict(trade))

                    # Log success or failure
                    self._log_notification(
                        cursor,
                        trade['id'],
                        'new_trade',
                        message_id,
                        'sent' if message_id else 'failed'
                    )

                except Exception as e:
                    self._log_notification(
                        cursor,
                        trade['id'],
                        'new_trade',
                        None,
                        'failed',
                        str(e)
                    )

            conn.commit()

    def notify_closed_trades(self):
        """Send notifications for recently closed trades."""

        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT t.*, p.username as profile_username
                FROM xtrades_trades t
                JOIN xtrades_profiles p ON t.profile_id = p.id
                LEFT JOIN xtrades_notifications n
                    ON t.id = n.trade_id
                    AND n.notification_type = 'trade_closed'
                WHERE n.id IS NULL
                AND t.status = 'closed'
                AND t.exit_date > NOW() - INTERVAL '24 hours'
            """)

            trades = cursor.fetchall()

            for trade in trades:
                try:
                    message_id = self.notifier.send_trade_closed_alert(dict(trade))

                    self._log_notification(
                        cursor,
                        trade['id'],
                        'trade_closed',
                        message_id,
                        'sent' if message_id else 'failed'
                    )

                except Exception as e:
                    self._log_notification(
                        cursor,
                        trade['id'],
                        'trade_closed',
                        None,
                        'failed',
                        str(e)
                    )

            conn.commit()

    def _log_notification(self, cursor, trade_id, notification_type,
                          message_id, status, error_message=None):
        """Log notification to database."""

        cursor.execute("""
            INSERT INTO xtrades_notifications
            (trade_id, notification_type, telegram_message_id, status, error_message)
            VALUES (%s, %s, %s, %s, %s)
        """, (trade_id, notification_type, message_id, status, error_message))

# Usage
manager = XtradesNotificationManager()
manager.notify_new_trades()
manager.notify_closed_trades()
```

---

## Scheduled Notifications

### Daily Summary

```python
from apscheduler.schedulers.blocking import BlockingScheduler
from telegram_notifier import TelegramNotifier
import psycopg2

def send_daily_summary():
    """Send daily trading summary at end of day."""

    notifier = TelegramNotifier()
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cursor = conn.cursor()

    # Get today's statistics
    cursor.execute("""
        SELECT
            COUNT(*) FILTER (WHERE entry_date::date = CURRENT_DATE) as new_trades,
            COUNT(*) FILTER (WHERE exit_date::date = CURRENT_DATE) as closed_trades,
            COUNT(*) FILTER (WHERE status = 'open') as total_trades,
            COALESCE(SUM(pnl) FILTER (WHERE exit_date::date = CURRENT_DATE), 0) as total_pnl,
            ROUND(
                100.0 * COUNT(*) FILTER (WHERE pnl > 0 AND exit_date::date = CURRENT_DATE) /
                NULLIF(COUNT(*) FILTER (WHERE exit_date::date = CURRENT_DATE), 0),
                2
            ) as win_rate,
            (SELECT COUNT(DISTINCT id) FROM xtrades_profiles WHERE active = TRUE) as active_profiles
        FROM xtrades_trades
    """)

    stats = cursor.fetchone()

    summary_data = {
        'new_trades': stats[0],
        'closed_trades': stats[1],
        'total_trades': stats[2],
        'total_pnl': stats[3],
        'win_rate': stats[4] or 0,
        'active_profiles': stats[5]
    }

    # Send summary
    notifier.send_daily_summary(summary_data)

    conn.close()

# Schedule daily at 6 PM
scheduler = BlockingScheduler()
scheduler.add_job(send_daily_summary, 'cron', hour=18, minute=0)
scheduler.start()
```

### Periodic Trade Checks

```python
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

def check_trades_every_15_minutes():
    """Check for new trades and updates every 15 minutes."""

    notifier = TelegramNotifier()

    try:
        # Your sync logic here
        sync_xtrades_profiles()

        # Check for updates
        check_and_notify_updates()

    except Exception as e:
        notifier.send_sync_error_alert(f"Periodic check failed: {e}")

# Run every 15 minutes
scheduler = BackgroundScheduler()
scheduler.add_job(
    check_trades_every_15_minutes,
    'interval',
    minutes=15
)
scheduler.start()
```

---

## Error Handling

### Sync Error Notifications

```python
def sync_with_error_handling():
    """Sync with comprehensive error handling and notifications."""

    notifier = TelegramNotifier()
    failed_profiles = []

    profiles = get_active_profiles()

    for profile in profiles:
        try:
            # Attempt to sync profile
            trades = scrape_profile(profile['username'])
            save_trades(trades)

        except ConnectionError as e:
            failed_profiles.append(profile['username'])
            logger.error(f"Connection error for {profile['username']}: {e}")

        except Exception as e:
            failed_profiles.append(profile['username'])
            logger.error(f"Error syncing {profile['username']}: {e}")

    # Send error notification if any failures
    if failed_profiles:
        notifier.send_sync_error_alert(
            f"Failed to sync {len(failed_profiles)} profile(s)",
            failed_profiles
        )
```

### Retry on Failure

```python
import time
from functools import wraps

def retry_notification(max_attempts=3, delay=5):
    """Decorator to retry failed notifications."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    result = func(*args, **kwargs)
                    if result:
                        return result

                    if attempt < max_attempts - 1:
                        time.sleep(delay * (attempt + 1))

                except Exception as e:
                    logger.error(f"Attempt {attempt + 1} failed: {e}")
                    if attempt < max_attempts - 1:
                        time.sleep(delay * (attempt + 1))

            return None

        return wrapper
    return decorator

@retry_notification(max_attempts=3, delay=5)
def send_important_notification(trade_data):
    """Send important notification with retry."""
    notifier = TelegramNotifier()
    return notifier.send_new_trade_alert(trade_data)
```

---

## Advanced Patterns

### Conditional Notifications

```python
def send_conditional_notifications(trade_data):
    """Send notifications based on conditions."""

    notifier = TelegramNotifier()

    # Only notify for large trades
    if trade_data.get('quantity', 0) >= 5:
        notifier.send_new_trade_alert(trade_data)

    # Only notify for specific strategies
    if trade_data.get('strategy') in ['CSP', 'Put Credit Spread']:
        notifier.send_new_trade_alert(trade_data)

    # Only notify for high-value trades
    entry_value = (
        float(trade_data.get('entry_price', 0)) *
        trade_data.get('quantity', 0) * 100
    )
    if entry_value >= 1000:
        notifier.send_new_trade_alert(trade_data)
```

### Batched Notifications

```python
def send_batched_summary(trades):
    """Send a single notification for multiple trades."""

    notifier = TelegramNotifier()

    message = "*Multiple New Trades*\n\n"

    for i, trade in enumerate(trades, 1):
        message += (
            f"{i}. {trade['ticker']} - {trade['strategy']}\n"
            f"   Entry: ${trade['entry_price']:.2f} x {trade['quantity']}\n\n"
        )

    message += f"Total: {len(trades)} new trades"

    notifier.send_custom_message(message)
```

### Custom Message Formats

```python
def send_formatted_alert(trade_data):
    """Send custom formatted alert."""

    notifier = TelegramNotifier()

    # Build custom message
    message = f"""
🎯 *PREMIUM TRADE ALERT*

📊 **{trade_data['ticker']}** | {trade_data['strategy']}

💰 *Entry Details:*
  • Price: ${trade_data['entry_price']:.2f}
  • Strike: ${trade_data['strike_price']:.2f}
  • Quantity: {trade_data['quantity']} contracts
  • Premium: ${float(trade_data['entry_price']) * 100 * trade_data['quantity']:.2f}

📅 *Timeline:*
  • Expiration: {trade_data['expiration_date']}
  • DTE: {calculate_dte(trade_data['expiration_date'])} days

👤 *Trader:* {trade_data['profile_username']}

[View Profile](https://app.xtrades.net/profile/{trade_data['profile_username']})
"""

    notifier.send_custom_message(message)
```

### Performance Alerts

```python
def send_performance_alert(profile_username):
    """Send performance summary for a profile."""

    notifier = TelegramNotifier()
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cursor = conn.cursor()

    # Get performance stats
    cursor.execute("""
        SELECT
            COUNT(*) as total_trades,
            COUNT(*) FILTER (WHERE pnl > 0) as winning_trades,
            COALESCE(SUM(pnl), 0) as total_pnl,
            COALESCE(AVG(pnl_percent), 0) as avg_return,
            MAX(pnl) as best_trade,
            MIN(pnl) as worst_trade
        FROM xtrades_trades t
        JOIN xtrades_profiles p ON t.profile_id = p.id
        WHERE p.username = %s
        AND t.status = 'closed'
    """, (profile_username,))

    stats = cursor.fetchone()

    win_rate = (stats[1] / stats[0] * 100) if stats[0] > 0 else 0

    message = f"""
📊 *Performance Report: {profile_username}*

📈 *Overall Stats:*
  • Total Trades: {stats[0]}
  • Win Rate: {win_rate:.1f}%
  • Total P&L: ${stats[2]:,.2f}
  • Avg Return: {stats[3]:.2f}%

🏆 *Best Trade:* ${stats[4]:,.2f}
📉 *Worst Trade:* ${stats[5]:,.2f}

Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""

    notifier.send_custom_message(message)
    conn.close()
```

---

## Complete Integration Example

```python
#!/usr/bin/env python3
"""
Complete Xtrades integration with Telegram notifications.
"""

import os
import logging
from datetime import datetime
from decimal import Decimal
import psycopg2
from psycopg2.extras import RealDictCursor
from telegram_notifier import TelegramNotifier
from apscheduler.schedulers.background import BackgroundScheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class XtradesIntegration:
    """Complete Xtrades integration with Telegram notifications."""

    def __init__(self):
        self.notifier = TelegramNotifier()
        self.db_url = os.getenv('DATABASE_URL')
        self.scheduler = BackgroundScheduler()

    def start(self):
        """Start the integration and schedule jobs."""

        logger.info("Starting Xtrades integration...")

        # Test Telegram connection
        if not self.notifier.test_connection():
            logger.warning("Telegram not available")

        # Schedule jobs
        self.scheduler.add_job(
            self.sync_and_notify,
            'interval',
            minutes=15,
            id='sync_trades'
        )

        self.scheduler.add_job(
            self.send_daily_summary,
            'cron',
            hour=18,
            minute=0,
            id='daily_summary'
        )

        self.scheduler.start()
        logger.info("Integration started successfully")

    def sync_and_notify(self):
        """Sync trades and send notifications."""

        logger.info("Starting sync...")

        try:
            # Sync new trades
            new_count = self.notify_new_trades()

            # Check for updates
            update_count = self.notify_updates()

            # Check for closures
            closed_count = self.notify_closures()

            logger.info(
                f"Sync complete: {new_count} new, "
                f"{update_count} updates, {closed_count} closed"
            )

        except Exception as e:
            logger.error(f"Sync failed: {e}")
            self.notifier.send_sync_error_alert(str(e))

    def notify_new_trades(self):
        """Notify about new trades."""

        with psycopg2.connect(self.db_url, cursor_factory=RealDictCursor) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT t.*, p.username as profile_username
                FROM xtrades_trades t
                JOIN xtrades_profiles p ON t.profile_id = p.id
                LEFT JOIN xtrades_notifications n
                    ON t.id = n.trade_id
                    AND n.notification_type = 'new_trade'
                WHERE n.id IS NULL
                AND t.status = 'open'
            """)

            trades = cursor.fetchall()

            for trade in trades:
                message_id = self.notifier.send_new_trade_alert(dict(trade))

                cursor.execute("""
                    INSERT INTO xtrades_notifications
                    (trade_id, notification_type, telegram_message_id, status)
                    VALUES (%s, %s, %s, %s)
                """, (trade['id'], 'new_trade', message_id,
                     'sent' if message_id else 'failed'))

            conn.commit()
            return len(trades)

    def notify_updates(self):
        """Notify about trade updates."""
        # Implementation similar to notify_new_trades
        return 0

    def notify_closures(self):
        """Notify about closed trades."""

        with psycopg2.connect(self.db_url, cursor_factory=RealDictCursor) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT t.*, p.username as profile_username
                FROM xtrades_trades t
                JOIN xtrades_profiles p ON t.profile_id = p.id
                LEFT JOIN xtrades_notifications n
                    ON t.id = n.trade_id
                    AND n.notification_type = 'trade_closed'
                WHERE n.id IS NULL
                AND t.status = 'closed'
                AND t.exit_date > NOW() - INTERVAL '24 hours'
            """)

            trades = cursor.fetchall()

            for trade in trades:
                message_id = self.notifier.send_trade_closed_alert(dict(trade))

                cursor.execute("""
                    INSERT INTO xtrades_notifications
                    (trade_id, notification_type, telegram_message_id, status)
                    VALUES (%s, %s, %s, %s)
                """, (trade['id'], 'trade_closed', message_id,
                     'sent' if message_id else 'failed'))

            conn.commit()
            return len(trades)

    def send_daily_summary(self):
        """Send daily summary."""

        with psycopg2.connect(self.db_url) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    COUNT(*) FILTER (WHERE entry_date::date = CURRENT_DATE) as new_trades,
                    COUNT(*) FILTER (WHERE exit_date::date = CURRENT_DATE) as closed_trades,
                    COUNT(*) FILTER (WHERE status = 'open') as total_trades,
                    COALESCE(SUM(pnl) FILTER (WHERE exit_date::date = CURRENT_DATE), 0) as total_pnl,
                    ROUND(100.0 * COUNT(*) FILTER (WHERE pnl > 0 AND exit_date::date = CURRENT_DATE) /
                          NULLIF(COUNT(*) FILTER (WHERE exit_date::date = CURRENT_DATE), 0), 2) as win_rate,
                    (SELECT COUNT(*) FROM xtrades_profiles WHERE active = TRUE) as active_profiles
                FROM xtrades_trades
            """)

            stats = cursor.fetchone()

            summary_data = {
                'new_trades': stats[0],
                'closed_trades': stats[1],
                'total_trades': stats[2],
                'total_pnl': stats[3],
                'win_rate': stats[4] or 0,
                'active_profiles': stats[5]
            }

            self.notifier.send_daily_summary(summary_data)


if __name__ == '__main__':
    integration = XtradesIntegration()
    integration.start()

    # Keep running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        integration.scheduler.shutdown()
```

---

## Best Practices

1. **Always check notification status** before marking as sent
2. **Log all notifications** to the database for audit trail
3. **Handle errors gracefully** and send error notifications
4. **Avoid duplicate notifications** by checking the notifications table
5. **Use connection pooling** for database operations
6. **Schedule summaries** during low-activity times
7. **Test thoroughly** before deploying to production
8. **Monitor notification failures** and investigate patterns
9. **Respect rate limits** - don't spam notifications
10. **Keep messages concise** but informative

---

For more information, see [TELEGRAM_SETUP.md](../TELEGRAM_SETUP.md) for setup instructions.
