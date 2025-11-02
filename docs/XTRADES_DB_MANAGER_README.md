# Xtrades Database Manager - Developer Guide

Complete CRUD operations for the Xtrades monitoring system in the Magnus Wheel Strategy Dashboard.

## Overview

The `XtradesDBManager` class provides a comprehensive interface for managing:
- **Profiles**: Xtrades.net traders to monitor
- **Trades**: Trading alerts and positions
- **Sync Logs**: Audit trail of synchronization operations
- **Notifications**: Tracking of sent notifications to prevent duplicates

## Quick Start

```python
from src.xtrades_db_manager import XtradesDBManager

# Initialize
db = XtradesDBManager()

# Add a profile to monitor
profile_id = db.add_profile(
    username="wheeltraderguru",
    display_name="Wheel Trader Guru"
)

# Add a trade
trade_data = {
    'profile_id': profile_id,
    'ticker': 'AAPL',
    'strategy': 'CSP',
    'entry_price': 3.50,
    'strike_price': 175.00,
    'alert_timestamp': datetime.now()
}
trade_id = db.add_trade(trade_data)

# Get statistics
stats = db.get_profile_stats(profile_id)
print(f"Win rate: {stats['win_rate']:.1f}%")
```

## API Reference

### Profile Management

#### `add_profile(username, display_name=None, notes=None) -> int`
Add or update a profile to monitor.

**Parameters:**
- `username` (str): Xtrades.net username (unique)
- `display_name` (str, optional): Friendly display name
- `notes` (str, optional): Notes about this trader

**Returns:** `profile_id` (int)

**Example:**
```python
profile_id = db.add_profile(
    username="optionsmaster",
    display_name="Options Master",
    notes="Focus on tech stocks, 45DTE entries"
)
```

---

#### `get_active_profiles() -> List[Dict]`
Get all active profiles being monitored.

**Returns:** List of profile dictionaries

**Example:**
```python
profiles = db.get_active_profiles()
for profile in profiles:
    print(f"{profile['username']}: {profile['total_trades_scraped']} trades")
```

---

#### `get_profile_by_id(profile_id) -> Dict | None`
Get a specific profile by ID.

**Parameters:**
- `profile_id` (int): Profile ID

**Returns:** Profile dictionary or None

---

#### `get_profile_by_username(username) -> Dict | None`
Get a specific profile by username.

**Parameters:**
- `username` (str): Xtrades username

**Returns:** Profile dictionary or None

---

#### `update_profile_sync_status(profile_id, status, trades_count=None) -> bool`
Update profile's sync status after a scrape operation.

**Parameters:**
- `profile_id` (int): Profile ID
- `status` (str): 'success', 'error', or 'pending'
- `trades_count` (int, optional): Number of new trades found (increments total)

**Returns:** True if successful

**Example:**
```python
db.update_profile_sync_status(
    profile_id=123,
    status='success',
    trades_count=5
)
```

---

#### `deactivate_profile(profile_id) -> bool`
Soft-delete a profile (sets active=False).

#### `reactivate_profile(profile_id) -> bool`
Reactivate a previously deactivated profile.

---

### Trade Management

#### `add_trade(trade_data: Dict) -> int`
Add a new trade from an Xtrades alert.

**Required Fields:**
- `profile_id` (int)
- `ticker` (str)
- `alert_timestamp` (datetime)

**Optional Fields:**
- `strategy` (str): 'CSP', 'CC', 'PCS', etc.
- `action` (str): 'STO', 'BTO', 'BTC', 'STC'
- `entry_price` (float)
- `entry_date` (datetime)
- `quantity` (int): Default 1
- `strike_price` (float)
- `expiration_date` (date)
- `alert_text` (str)
- `xtrades_alert_id` (str)
- `status` (str): Default 'open'

**Returns:** `trade_id` (int)

**Example:**
```python
trade_data = {
    'profile_id': 123,
    'ticker': 'TSLA',
    'strategy': 'CSP',
    'action': 'STO',
    'entry_price': 5.00,
    'entry_date': datetime.now(),
    'quantity': 2,
    'strike_price': 250.00,
    'expiration_date': datetime.now() + timedelta(days=45),
    'alert_text': 'STO 2 TSLA 45DTE 250P @ $5.00',
    'alert_timestamp': datetime.now()
}
trade_id = db.add_trade(trade_data)
```

---

#### `update_trade(trade_id, update_data: Dict) -> bool`
Update an existing trade.

**Allowed Fields:**
- `exit_price`, `exit_date`, `pnl`, `pnl_percent`, `status`
- `entry_price`, `entry_date`, `quantity`, `strategy`, `action`
- `strike_price`, `expiration_date`, `alert_text`

**Example:**
```python
db.update_trade(trade_id, {
    'exit_price': 2.00,
    'exit_date': datetime.now(),
    'status': 'closed'
})
```

---

#### `close_trade(trade_id, exit_price, exit_date=None, status='closed') -> bool`
Close a trade and automatically calculate P&L.

**Parameters:**
- `trade_id` (int)
- `exit_price` (float)
- `exit_date` (datetime, optional): Default now
- `status` (str): 'closed' or 'expired'

**Returns:** True if successful

**Example:**
```python
db.close_trade(
    trade_id=456,
    exit_price=1.50,
    status='closed'
)
```

---

#### `get_trade_by_id(trade_id) -> Dict | None`
Get a specific trade by ID.

---

#### `get_trades_by_profile(profile_id, status=None, limit=100) -> List[Dict]`
Get trades for a profile with optional status filter.

**Parameters:**
- `profile_id` (int)
- `status` (str, optional): 'open', 'closed', 'expired'
- `limit` (int): Default 100

**Example:**
```python
# Get all open positions
open_trades = db.get_trades_by_profile(123, status='open')

# Get recent closed trades
closed_trades = db.get_trades_by_profile(123, status='closed', limit=50)
```

---

#### `get_all_trades(status=None, ticker=None, limit=100) -> List[Dict]`
Get trades across all profiles with optional filters.

---

#### `find_existing_trade(profile_id, ticker, alert_timestamp) -> int | None`
Check if a trade already exists (to prevent duplicates).

**Returns:** `trade_id` if found, None otherwise

**Example:**
```python
existing_id = db.find_existing_trade(
    profile_id=123,
    ticker='AAPL',
    alert_timestamp=alert_time
)

if not existing_id:
    # Trade doesn't exist, safe to add
    trade_id = db.add_trade(trade_data)
```

---

#### `get_open_trades_by_profile(profile_id) -> List[Dict]`
Convenience method to get all open trades for a profile.

---

### Sync Logging

#### `log_sync_start() -> int`
Create a sync log entry at the start of a sync operation.

**Returns:** `sync_log_id` (int)

**Example:**
```python
sync_log_id = db.log_sync_start()
# ... perform sync operations ...
```

---

#### `log_sync_complete(sync_log_id, stats: Dict) -> bool`
Update sync log with completion statistics.

**Stats Dictionary:**
- `profiles_synced` (int): Number of profiles processed
- `trades_found` (int): Total trades found
- `new_trades` (int): New trades added
- `updated_trades` (int): Trades updated
- `errors` (str, optional): Error messages
- `duration_seconds` (float): Sync duration
- `status` (str): 'success', 'partial', or 'failed'

**Example:**
```python
stats = {
    'profiles_synced': 3,
    'trades_found': 15,
    'new_trades': 5,
    'updated_trades': 2,
    'errors': None,
    'duration_seconds': 12.5,
    'status': 'success'
}
db.log_sync_complete(sync_log_id, stats)
```

---

#### `get_sync_history(limit=50) -> List[Dict]`
Get recent sync operation history.

#### `get_latest_sync() -> Dict | None`
Get the most recent sync operation.

---

### Notifications

#### `log_notification(trade_id, notification_type, telegram_msg_id=None, status='sent', error_message=None) -> int`
Record a notification that was sent.

**Parameters:**
- `trade_id` (int)
- `notification_type` (str): 'new_trade', 'trade_update', 'trade_closed'
- `telegram_msg_id` (str, optional): For tracking/editing
- `status` (str): 'sent' or 'failed'
- `error_message` (str, optional)

**Returns:** `notification_id` (int)

**Example:**
```python
notif_id = db.log_notification(
    trade_id=789,
    notification_type='new_trade',
    telegram_msg_id='TG_12345',
    status='sent'
)
```

---

#### `get_unsent_notifications() -> List[Dict]`
Get trades that need notifications (no notification record exists).

**Example:**
```python
unsent = db.get_unsent_notifications()
for trade in unsent:
    # Send notification
    send_telegram_alert(trade)

    # Log it
    db.log_notification(trade['id'], 'new_trade', msg_id)
```

---

#### `get_notifications_for_trade(trade_id) -> List[Dict]`
Get all notifications sent for a specific trade.

---

### Analytics & Statistics

#### `get_profile_stats(profile_id) -> Dict`
Get comprehensive statistics for a profile.

**Returns Dictionary:**
- `total_trades` (int)
- `open_trades` (int)
- `closed_trades` (int)
- `total_pnl` (float)
- `avg_pnl` (float)
- `win_rate` (float): Percentage
- `best_trade` (dict): Ticker, P&L, percent
- `worst_trade` (dict): Ticker, P&L, percent

**Example:**
```python
stats = db.get_profile_stats(123)
print(f"Win Rate: {stats['win_rate']:.1f}%")
print(f"Total P&L: ${stats['total_pnl']:.2f}")
```

---

#### `get_overall_stats() -> Dict`
Get system-wide statistics across all profiles.

**Returns Dictionary:**
- `total_profiles` (int)
- `total_trades` (int)
- `open_trades` (int)
- `closed_trades` (int)
- `total_pnl` (float)
- `avg_pnl` (float)
- `win_rate` (float)
- `most_active_ticker` (dict)
- `top_profile` (dict)

---

#### `get_trades_by_ticker(ticker, limit=50) -> List[Dict]`
Get all trades for a specific ticker across all profiles.

**Example:**
```python
spy_trades = db.get_trades_by_ticker('SPY')
print(f"Found {len(spy_trades)} SPY trades")
```

---

#### `get_recent_activity(days=7, limit=100) -> List[Dict]`
Get recent trading activity with profile information.

**Example:**
```python
recent = db.get_recent_activity(days=7)
for trade in recent:
    print(f"{trade['username']}: {trade['ticker']} - {trade['strategy']}")
```

---

## Common Workflows

### 1. Monitor New Trader

```python
db = XtradesDBManager()

# Add trader
profile_id = db.add_profile("newtrader", "New Trader")

# Sync will add trades automatically
# Update sync status when done
db.update_profile_sync_status(profile_id, 'success', 10)
```

### 2. Process Alert

```python
# Check for duplicate
existing = db.find_existing_trade(profile_id, ticker, alert_time)

if not existing:
    # Add new trade
    trade_id = db.add_trade(trade_data)

    # Send and log notification
    send_telegram(trade_data)
    db.log_notification(trade_id, 'new_trade', telegram_id)
```

### 3. Close Position

```python
# Option 1: Auto-calculate P&L
db.close_trade(trade_id, exit_price=1.50)

# Option 2: Manual update
db.update_trade(trade_id, {
    'exit_price': 1.50,
    'exit_date': datetime.now(),
    'pnl': 150.00,
    'pnl_percent': 60.00,
    'status': 'closed'
})
```

### 4. Daily Sync Operation

```python
import time

# Start sync
sync_log_id = db.log_sync_start()
start_time = time.time()

# Process profiles
profiles = db.get_active_profiles()
new_trades = 0
updated_trades = 0

for profile in profiles:
    # Scrape Xtrades.net for this profile
    alerts = scrape_xtrades(profile['username'])

    for alert in alerts:
        existing = db.find_existing_trade(
            profile['id'], alert['ticker'], alert['timestamp']
        )

        if existing:
            # Update existing trade if needed
            updated_trades += 1
        else:
            # Add new trade
            db.add_trade(alert_to_trade_data(alert, profile['id']))
            new_trades += 1

    # Update profile sync status
    db.update_profile_sync_status(profile['id'], 'success', new_trades)

# Complete sync log
duration = time.time() - start_time
db.log_sync_complete(sync_log_id, {
    'profiles_synced': len(profiles),
    'trades_found': new_trades + updated_trades,
    'new_trades': new_trades,
    'updated_trades': updated_trades,
    'duration_seconds': duration,
    'status': 'success'
})
```

### 5. Performance Dashboard

```python
# Overall stats
overall = db.get_overall_stats()
print(f"System P&L: ${overall['total_pnl']:.2f}")
print(f"Win Rate: {overall['win_rate']:.1f}%")

# Top traders
profiles = db.get_active_profiles()
for profile in profiles:
    stats = db.get_profile_stats(profile['id'])
    print(f"{profile['display_name']}: ${stats['total_pnl']:.2f}")

# Recent activity
recent = db.get_recent_activity(days=7)
print(f"Trades this week: {len(recent)}")
```

## Database Schema Reference

### xtrades_profiles
- `id` SERIAL PRIMARY KEY
- `username` VARCHAR(255) UNIQUE NOT NULL
- `display_name` VARCHAR(255)
- `active` BOOLEAN DEFAULT TRUE
- `added_date` TIMESTAMP WITH TIME ZONE
- `last_sync` TIMESTAMP WITH TIME ZONE
- `last_sync_status` VARCHAR(50)
- `total_trades_scraped` INTEGER
- `notes` TEXT

### xtrades_trades
- `id` SERIAL PRIMARY KEY
- `profile_id` INTEGER REFERENCES xtrades_profiles(id)
- `ticker` VARCHAR(20) NOT NULL
- `strategy` VARCHAR(100)
- `action` VARCHAR(20)
- `entry_price` DECIMAL(10,2)
- `entry_date` TIMESTAMP WITH TIME ZONE
- `exit_price` DECIMAL(10,2)
- `exit_date` TIMESTAMP WITH TIME ZONE
- `quantity` INTEGER
- `pnl` DECIMAL(10,2)
- `pnl_percent` DECIMAL(10,2)
- `status` VARCHAR(20) DEFAULT 'open'
- `strike_price` DECIMAL(10,2)
- `expiration_date` DATE
- `alert_text` TEXT
- `alert_timestamp` TIMESTAMP WITH TIME ZONE NOT NULL
- `scraped_at` TIMESTAMP WITH TIME ZONE
- `updated_at` TIMESTAMP WITH TIME ZONE
- `xtrades_alert_id` VARCHAR(255)

### xtrades_sync_log
- `id` SERIAL PRIMARY KEY
- `sync_timestamp` TIMESTAMP WITH TIME ZONE
- `profiles_synced` INTEGER
- `trades_found` INTEGER
- `new_trades` INTEGER
- `updated_trades` INTEGER
- `errors` TEXT
- `duration_seconds` DECIMAL(10,2)
- `status` VARCHAR(50)

### xtrades_notifications
- `id` SERIAL PRIMARY KEY
- `trade_id` INTEGER REFERENCES xtrades_trades(id)
- `notification_type` VARCHAR(50) NOT NULL
- `sent_at` TIMESTAMP WITH TIME ZONE
- `telegram_message_id` VARCHAR(255)
- `status` VARCHAR(20)
- `error_message` TEXT

## Testing

Run the test suite:

```bash
# All tests
python -m pytest src/test_xtrades_db_manager.py -v

# Specific test class
python -m pytest src/test_xtrades_db_manager.py::TestProfileManagement -v

# With coverage
python -m pytest src/test_xtrades_db_manager.py --cov=src.xtrades_db_manager --cov-report=html
```

Run usage examples:

```bash
python src/xtrades_usage_examples.py
```

## Error Handling

All methods include proper error handling:

- Database errors are logged with `logger.error()`
- Failed operations rollback transactions
- Methods return appropriate types on failure (False, None, [], {})
- Exceptions are raised only for critical failures (add_trade, add_profile, etc.)

## Performance Considerations

- Uses `RealDictCursor` for dictionary results
- Proper indexing on foreign keys and frequently queried fields
- Connection pooling compatible (each method opens/closes connections)
- Parameterized queries prevent SQL injection
- Transaction support for data integrity

## Integration with Telegram Bot

```python
# When sending notification
def send_trade_alert(trade_data):
    # Send to Telegram
    msg = bot.send_message(chat_id, format_trade_alert(trade_data))

    # Log notification
    db.log_notification(
        trade_id=trade_data['id'],
        notification_type='new_trade',
        telegram_msg_id=str(msg.message_id),
        status='sent'
    )

# Check for unsent
def send_pending_notifications():
    unsent = db.get_unsent_notifications()
    for trade in unsent:
        try:
            send_trade_alert(trade)
        except Exception as e:
            db.log_notification(
                trade['id'],
                'new_trade',
                status='failed',
                error_message=str(e)
            )
```

## Best Practices

1. **Always check for duplicates** before adding trades
2. **Log sync operations** for audit trail
3. **Update profile sync status** after each scrape
4. **Use transactions** for multi-step operations
5. **Log all notifications** to prevent spam
6. **Deactivate profiles** instead of deleting
7. **Use proper type hints** for IDE support
8. **Handle None returns** from getter methods

## Support

For issues or questions:
- Check the usage examples in `src/xtrades_usage_examples.py`
- Review test cases in `src/test_xtrades_db_manager.py`
- See database schema in `src/xtrades_schema.sql`

---

**Version:** 1.0.0
**Author:** Magnus Wheel Strategy Dashboard
**License:** MIT
