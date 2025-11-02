# Xtrades DB Manager - Quick Reference Card

## Import & Initialize
```python
from src.xtrades_db_manager import XtradesDBManager
db = XtradesDBManager()
```

## Profile Operations

### Add/Update Profile
```python
profile_id = db.add_profile("username", "Display Name", "Notes")
```

### Get Profiles
```python
profiles = db.get_active_profiles()                    # All active
profile = db.get_profile_by_id(123)                    # By ID
profile = db.get_profile_by_username("trader")         # By username
```

### Update Sync Status
```python
db.update_profile_sync_status(profile_id, 'success', trades_count=10)
```

### Deactivate/Reactivate
```python
db.deactivate_profile(profile_id)     # Soft delete
db.reactivate_profile(profile_id)     # Undo deactivate
```

## Trade Operations

### Add Trade
```python
trade_data = {
    'profile_id': 123,
    'ticker': 'AAPL',
    'strategy': 'CSP',
    'action': 'STO',
    'entry_price': 3.50,
    'entry_date': datetime.now(),
    'quantity': 1,
    'strike_price': 175.00,
    'expiration_date': datetime.now() + timedelta(days=45),
    'alert_text': 'STO AAPL 175P @ $3.50',
    'alert_timestamp': datetime.now()
}
trade_id = db.add_trade(trade_data)
```

### Update Trade
```python
db.update_trade(trade_id, {
    'exit_price': 1.50,
    'status': 'closed'
})
```

### Close Trade (Auto P&L)
```python
db.close_trade(trade_id, exit_price=1.50, status='closed')
```

### Get Trades
```python
trade = db.get_trade_by_id(456)                                # By ID
trades = db.get_trades_by_profile(123, status='open')          # By profile
trades = db.get_all_trades(ticker='AAPL')                      # By ticker
trades = db.get_open_trades_by_profile(123)                    # Open only
```

### Check Duplicate
```python
existing_id = db.find_existing_trade(profile_id, 'AAPL', alert_timestamp)
if not existing_id:
    # Safe to add
```

## Sync Logging

### Complete Sync Operation
```python
# Start
sync_id = db.log_sync_start()

# ... do scraping ...

# Complete
db.log_sync_complete(sync_id, {
    'profiles_synced': 3,
    'trades_found': 15,
    'new_trades': 5,
    'updated_trades': 2,
    'duration_seconds': 12.5,
    'status': 'success'
})
```

### Get History
```python
history = db.get_sync_history(limit=10)
latest = db.get_latest_sync()
```

## Notifications

### Log Notification
```python
notif_id = db.log_notification(
    trade_id=789,
    notification_type='new_trade',
    telegram_msg_id='TG_12345',
    status='sent'
)
```

### Get Unsent
```python
unsent = db.get_unsent_notifications()
for trade in unsent:
    # Send notification
    # Then log it
```

### Get Notifications for Trade
```python
notifications = db.get_notifications_for_trade(trade_id)
```

## Analytics

### Profile Stats
```python
stats = db.get_profile_stats(profile_id)
# Returns: total_trades, open_trades, closed_trades, total_pnl,
#          avg_pnl, win_rate, best_trade, worst_trade
```

### Overall Stats
```python
stats = db.get_overall_stats()
# Returns: total_profiles, total_trades, open_trades, closed_trades,
#          total_pnl, avg_pnl, win_rate, most_active_ticker, top_profile
```

### Get by Ticker
```python
trades = db.get_trades_by_ticker('SPY', limit=50)
```

### Recent Activity
```python
recent = db.get_recent_activity(days=7, limit=100)
```

## Common Workflows

### Daily Sync
```python
sync_id = db.log_sync_start()

for profile in db.get_active_profiles():
    alerts = scrape_xtrades(profile['username'])

    for alert in alerts:
        if not db.find_existing_trade(profile['id'], alert['ticker'], alert['time']):
            trade_id = db.add_trade(alert_to_trade_data(alert))
            send_telegram_notification(trade_id)
            db.log_notification(trade_id, 'new_trade', telegram_msg_id)

    db.update_profile_sync_status(profile['id'], 'success')

db.log_sync_complete(sync_id, stats)
```

### Check for Unsent Notifications
```python
unsent = db.get_unsent_notifications()
for trade in unsent:
    msg = send_telegram(trade)
    db.log_notification(trade['id'], 'new_trade', msg.message_id)
```

### Close Positions
```python
# Manual close
db.close_trade(trade_id, exit_price=1.50)

# Update notification
db.log_notification(trade_id, 'trade_closed', telegram_msg_id)
```

### Performance Report
```python
overall = db.get_overall_stats()
print(f"System P&L: ${overall['total_pnl']:.2f}")
print(f"Win Rate: {overall['win_rate']:.1f}%")

for profile in db.get_active_profiles():
    stats = db.get_profile_stats(profile['id'])
    print(f"{profile['display_name']}: ${stats['total_pnl']:.2f}")
```

## Return Types

| Method | Success | Failure |
|--------|---------|---------|
| `add_profile()` | `int` (profile_id) | `Exception` |
| `add_trade()` | `int` (trade_id) | `Exception` |
| `update_trade()` | `True` | `False` |
| `close_trade()` | `True` | `False` |
| `get_*_by_id()` | `Dict` | `None` |
| `get_*()` (list) | `List[Dict]` | `[]` (empty list) |
| `get_*_stats()` | `Dict` | `Dict` (with zeros) |
| `log_notification()` | `int` (notif_id) | `Exception` |
| `log_sync_start()` | `int` (sync_id) | `Exception` |
| `log_sync_complete()` | `True` | `False` |

## Status Values

### Profile Sync Status
- `'success'` - Sync completed successfully
- `'error'` - Sync failed
- `'pending'` - Sync in progress

### Trade Status
- `'open'` - Position is open
- `'closed'` - Position closed normally
- `'expired'` - Option expired

### Notification Type
- `'new_trade'` - New trade opened
- `'trade_update'` - Trade was updated
- `'trade_closed'` - Trade was closed

### Notification Status
- `'sent'` - Successfully sent
- `'failed'` - Send failed

### Sync Log Status
- `'success'` - All profiles synced
- `'partial'` - Some profiles synced
- `'failed'` - Sync failed

## Testing

```bash
# Run all tests
pytest src/test_xtrades_db_manager.py -v

# Run specific test class
pytest src/test_xtrades_db_manager.py::TestProfileManagement -v

# With coverage
pytest src/test_xtrades_db_manager.py --cov=src.xtrades_db_manager

# Run examples
python src/xtrades_usage_examples.py
```

## Files

| File | Purpose |
|------|---------|
| `src/xtrades_db_manager.py` | Main implementation (900 LOC) |
| `src/test_xtrades_db_manager.py` | Test suite (750 LOC) |
| `src/xtrades_usage_examples.py` | Usage examples (600 LOC) |
| `docs/XTRADES_DB_MANAGER_README.md` | Full documentation |
| `docs/XTRADES_QUICK_REFERENCE.md` | This file |

## Database Tables

- `xtrades_profiles` - Traders to monitor
- `xtrades_trades` - Trade data
- `xtrades_sync_log` - Sync audit trail
- `xtrades_notifications` - Notification tracking

## Error Handling

All methods handle errors gracefully:
- Database errors are logged
- Transactions rollback on failure
- Appropriate return values (False, None, [], {})
- Exceptions only for critical failures

## Best Practices

✓ Check for duplicates before adding trades
✓ Log all sync operations
✓ Update profile sync status after scraping
✓ Track all notifications
✓ Use soft deletes (deactivate)
✓ Handle None returns from getters
✓ Use type hints for IDE support

---

**Quick help:** See `docs/XTRADES_DB_MANAGER_README.md` for complete documentation
