# Xtrades Watchlists Database Schema Documentation

## Overview

The Xtrades Watchlists feature tracks and analyzes options trades from monitored Xtrades.net profiles. This system scrapes trade alerts, stores them in a normalized database schema, and provides analytics on trading performance.

**Database**: `magnus` (PostgreSQL)
**Schema Version**: 1.0.0
**Created**: 2025-11-02

---

## Architecture

### Entity Relationship Diagram

```
xtrades_profiles (1) ----< (N) xtrades_trades (1) ----< (N) xtrades_notifications
                                      |
                                   (references)
                                      |
                          xtrades_sync_log (audit log)
```

### Data Flow

1. **Profile Management**: Add Xtrades.net profiles to monitor
2. **Data Scraping**: Periodic scraping of trade alerts from profiles
3. **Trade Storage**: Parse and store trade details
4. **Sync Logging**: Record all sync operations for monitoring
5. **Notifications**: Send alerts for new/updated trades
6. **Analytics**: Query performance metrics and trends

---

## Table Definitions

### 1. `xtrades_profiles`

Stores Xtrades.net profiles to monitor for trading alerts.

**Purpose**: Central registry of traders we're tracking

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique profile identifier |
| username | VARCHAR(255) | UNIQUE NOT NULL | Xtrades.net username |
| display_name | VARCHAR(255) | | Friendly display name |
| active | BOOLEAN | DEFAULT TRUE | Whether actively monitoring |
| added_date | TIMESTAMP | DEFAULT NOW() | When profile was added |
| last_sync | TIMESTAMP | | Last successful sync timestamp |
| last_sync_status | VARCHAR(50) | CHECK constraint | 'success', 'error', or 'pending' |
| total_trades_scraped | INTEGER | DEFAULT 0 | Running count of trades |
| notes | TEXT | | Admin notes about profile |

**Indexes**:
- `idx_xtrades_profiles_username` - Fast username lookups
- `idx_xtrades_profiles_active` - Filter active profiles
- `idx_xtrades_profiles_last_sync` - Sort by sync time

**Sample Query**:
```sql
-- Get all active profiles with sync status
SELECT username, display_name, last_sync, last_sync_status
FROM xtrades_profiles
WHERE active = TRUE
ORDER BY last_sync DESC NULLS LAST;
```

---

### 2. `xtrades_trades`

Stores individual trades scraped from Xtrades profiles.

**Purpose**: Central repository of all trade data

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique trade identifier |
| profile_id | INTEGER | FK, NOT NULL | References xtrades_profiles(id) |
| ticker | VARCHAR(20) | NOT NULL | Stock ticker symbol |
| strategy | VARCHAR(100) | | Options strategy (CSP, CC, etc.) |
| action | VARCHAR(20) | CHECK constraint | BTO, STC, BTC, STO, etc. |
| entry_price | DECIMAL(10,2) | | Entry premium price |
| entry_date | TIMESTAMP | | When position opened |
| exit_price | DECIMAL(10,2) | | Exit premium price |
| exit_date | TIMESTAMP | | When position closed |
| quantity | INTEGER | | Number of contracts |
| pnl | DECIMAL(10,2) | | Profit/Loss in dollars |
| pnl_percent | DECIMAL(10,2) | | Profit/Loss percentage |
| status | VARCHAR(20) | CHECK, DEFAULT 'open' | open, closed, expired |
| strike_price | DECIMAL(10,2) | | Option strike price |
| expiration_date | DATE | | Option expiration date |
| alert_text | TEXT | | Full alert text from Xtrades |
| alert_timestamp | TIMESTAMP | NOT NULL | When alert was posted |
| scraped_at | TIMESTAMP | DEFAULT NOW() | When we scraped this data |
| updated_at | TIMESTAMP | DEFAULT NOW() | Last update timestamp |
| xtrades_alert_id | VARCHAR(255) | | Unique ID from Xtrades |

**Indexes**:
- `idx_xtrades_trades_profile_id` - Trades by profile
- `idx_xtrades_trades_ticker` - Trades by ticker
- `idx_xtrades_trades_status` - Filter by status
- `idx_xtrades_trades_alert_timestamp` - Sort by alert time
- `idx_xtrades_trades_entry_date` - Sort by entry date
- `idx_xtrades_trades_strategy` - Filter by strategy
- `idx_xtrades_trades_alert_id` - Prevent duplicates
- `idx_xtrades_trades_profile_status` - Composite for profile+status
- `idx_xtrades_trades_ticker_status` - Composite for ticker+status

**Foreign Keys**:
- `profile_id` → `xtrades_profiles(id)` ON DELETE CASCADE

**Sample Queries**:
```sql
-- Get all open positions
SELECT p.username, t.ticker, t.strategy, t.strike_price, t.expiration_date
FROM xtrades_trades t
JOIN xtrades_profiles p ON t.profile_id = p.id
WHERE t.status = 'open'
ORDER BY t.expiration_date;

-- Get closed trades with profit/loss
SELECT ticker, strategy, entry_date, exit_date, pnl, pnl_percent
FROM xtrades_trades
WHERE status = 'closed'
ORDER BY exit_date DESC;
```

---

### 3. `xtrades_sync_log`

Tracks synchronization history and errors.

**Purpose**: Audit trail for all sync operations

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique log identifier |
| sync_timestamp | TIMESTAMP | DEFAULT NOW() | When sync occurred |
| profiles_synced | INTEGER | DEFAULT 0 | Number of profiles processed |
| trades_found | INTEGER | DEFAULT 0 | Total trades discovered |
| new_trades | INTEGER | DEFAULT 0 | New trades added |
| updated_trades | INTEGER | DEFAULT 0 | Existing trades updated |
| errors | TEXT | | Error messages if any |
| duration_seconds | DECIMAL(10,2) | | How long sync took |
| status | VARCHAR(50) | CHECK, DEFAULT 'success' | success, partial, failed |

**Indexes**:
- `idx_xtrades_sync_log_timestamp` - Sort by sync time
- `idx_xtrades_sync_log_status` - Filter by status

**Sample Queries**:
```sql
-- Recent sync history
SELECT sync_timestamp, profiles_synced, new_trades, status, duration_seconds
FROM xtrades_sync_log
ORDER BY sync_timestamp DESC
LIMIT 10;

-- Failed syncs
SELECT sync_timestamp, errors
FROM xtrades_sync_log
WHERE status = 'failed'
ORDER BY sync_timestamp DESC;
```

---

### 4. `xtrades_notifications`

Tracks notifications sent via Telegram or other channels.

**Purpose**: Prevent duplicate notifications and provide audit trail

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique notification identifier |
| trade_id | INTEGER | FK, NOT NULL | References xtrades_trades(id) |
| notification_type | VARCHAR(50) | CHECK, NOT NULL | new_trade, trade_update, trade_closed |
| sent_at | TIMESTAMP | DEFAULT NOW() | When notification sent |
| telegram_message_id | VARCHAR(255) | | Telegram message ID |
| status | VARCHAR(20) | CHECK, DEFAULT 'sent' | sent or failed |
| error_message | TEXT | | Error message if failed |

**Indexes**:
- `idx_xtrades_notifications_trade_id` - Notifications by trade
- `idx_xtrades_notifications_sent_at` - Sort by sent time
- `idx_xtrades_notifications_type` - Filter by type
- `idx_xtrades_notifications_trade_type` - Check for duplicates

**Foreign Keys**:
- `trade_id` → `xtrades_trades(id)` ON DELETE CASCADE

**Sample Queries**:
```sql
-- Recent notifications
SELECT n.sent_at, n.notification_type, p.username, t.ticker
FROM xtrades_notifications n
JOIN xtrades_trades t ON n.trade_id = t.id
JOIN xtrades_profiles p ON t.profile_id = p.id
ORDER BY n.sent_at DESC
LIMIT 20;

-- Check if notification already sent for a trade
SELECT COUNT(*) > 0 as already_sent
FROM xtrades_notifications
WHERE trade_id = 123 AND notification_type = 'new_trade';
```

---

## Relationships and Constraints

### Foreign Key Cascade Behavior

All foreign keys use `ON DELETE CASCADE` to maintain referential integrity:

- Deleting a profile automatically deletes all its trades
- Deleting a trade automatically deletes all its notifications

### Check Constraints

The schema enforces data quality through CHECK constraints:

```sql
-- Profile sync status must be valid
last_sync_status IN ('success', 'error', 'pending', NULL)

-- Trade status must be valid
status IN ('open', 'closed', 'expired')

-- Trade action must be valid
action IN ('BTO', 'STC', 'BTC', 'STO', 'OPEN', 'CLOSE', NULL)

-- Sync log status must be valid
status IN ('success', 'partial', 'failed')

-- Notification type must be valid
notification_type IN ('new_trade', 'trade_update', 'trade_closed')

-- Notification status must be valid
status IN ('sent', 'failed')
```

---

## Performance Optimization

### Indexing Strategy

1. **Primary Keys**: Automatic B-tree indexes on all SERIAL primary keys
2. **Foreign Keys**: Explicit indexes on all foreign key columns for JOIN performance
3. **Query Patterns**: Composite indexes for common multi-column queries
4. **Timestamps**: DESC indexes for time-based ordering

### Query Performance Tips

1. Always filter by `active = TRUE` on profiles when relevant
2. Use `status` filters on trades to reduce result sets
3. Leverage composite indexes when querying by profile+status or ticker+status
4. Use EXPLAIN ANALYZE to verify index usage on complex queries

---

## Installation and Testing

### 1. Create Schema

```bash
# Execute schema creation
psql -h localhost -U postgres -d magnus -f src/xtrades_schema.sql
```

Or use the Python test script:

```bash
python test_xtrades_schema.py
```

### 2. Verify Installation

```sql
-- Check tables exist
SELECT table_name,
       (SELECT COUNT(*) FROM information_schema.columns
        WHERE table_name = t.table_name) as column_count
FROM information_schema.tables t
WHERE table_schema = 'public' AND table_name LIKE 'xtrades_%'
ORDER BY table_name;

-- Check indexes
SELECT tablename, indexname
FROM pg_indexes
WHERE schemaname = 'public' AND tablename LIKE 'xtrades_%'
ORDER BY tablename, indexname;
```

### 3. Rollback (if needed)

```bash
# Remove all Xtrades tables
psql -h localhost -U postgres -d magnus -f src/xtrades_schema_rollback.sql
```

---

## Usage Examples

### Adding a Profile

```sql
INSERT INTO xtrades_profiles (username, display_name, active, notes)
VALUES ('traderJoe', 'Joe the Trader', TRUE, 'Focuses on CSP strategy')
RETURNING id;
```

### Recording a New Trade

```sql
INSERT INTO xtrades_trades (
    profile_id, ticker, strategy, action, entry_price, entry_date,
    quantity, status, strike_price, expiration_date, alert_text, alert_timestamp
)
VALUES (
    1, 'AAPL', 'CSP', 'STO', 2.50, NOW(),
    1, 'open', 170.00, '2025-12-15', 'AAPL CSP alert text', NOW()
)
RETURNING id;
```

### Updating Trade on Close

```sql
UPDATE xtrades_trades
SET
    exit_price = 1.25,
    exit_date = NOW(),
    pnl = (2.50 - 1.25) * 100 * 1,  -- (entry - exit) * 100 * quantity
    pnl_percent = ((2.50 - 1.25) / 2.50) * 100,
    status = 'closed',
    updated_at = NOW()
WHERE id = 123;
```

### Logging a Sync Operation

```sql
INSERT INTO xtrades_sync_log (
    profiles_synced, trades_found, new_trades, updated_trades,
    duration_seconds, status
)
VALUES (3, 15, 10, 5, 12.5, 'success');
```

### Recording a Notification

```sql
INSERT INTO xtrades_notifications (
    trade_id, notification_type, telegram_message_id, status
)
VALUES (123, 'new_trade', '987654321', 'sent');
```

---

## Common Analytics Queries

### Performance by Strategy

```sql
SELECT
    strategy,
    COUNT(*) as total_trades,
    SUM(pnl) as total_pnl,
    AVG(pnl_percent) as avg_pnl_percent,
    ROUND(
        (SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END)::DECIMAL /
         COUNT(*)) * 100, 2
    ) as win_rate_percent
FROM xtrades_trades
WHERE status = 'closed' AND pnl IS NOT NULL
GROUP BY strategy
ORDER BY total_pnl DESC;
```

### Open Positions by Expiration

```sql
SELECT
    ticker,
    strategy,
    strike_price,
    expiration_date,
    EXTRACT(DAY FROM (expiration_date - CURRENT_DATE)) as days_to_expiration
FROM xtrades_trades
WHERE status = 'open'
ORDER BY expiration_date;
```

### Profile Leaderboard

```sql
SELECT
    p.username,
    COUNT(*) as total_trades,
    SUM(t.pnl) as total_pnl,
    AVG(t.pnl_percent) as avg_return_pct
FROM xtrades_profiles p
JOIN xtrades_trades t ON p.id = t.profile_id
WHERE t.status = 'closed' AND t.pnl IS NOT NULL
GROUP BY p.id, p.username
ORDER BY total_pnl DESC;
```

---

## Data Quality Monitoring

### Trades Missing Critical Data

```sql
SELECT
    'Missing Strategy' as issue, COUNT(*) as count
FROM xtrades_trades WHERE strategy IS NULL
UNION ALL
SELECT 'Missing Entry Price', COUNT(*)
FROM xtrades_trades WHERE entry_price IS NULL AND status IN ('open', 'closed')
UNION ALL
SELECT 'Missing Exit Price (Closed)', COUNT(*)
FROM xtrades_trades WHERE status = 'closed' AND exit_price IS NULL;
```

### Stale Data Check

```sql
-- Profiles not synced in 24 hours
SELECT username, last_sync, NOW() - last_sync as time_since_sync
FROM xtrades_profiles
WHERE active = TRUE AND last_sync < NOW() - INTERVAL '24 hours';

-- Expired but still open trades
SELECT ticker, expiration_date, CURRENT_DATE - expiration_date as days_past_expiration
FROM xtrades_trades
WHERE status = 'open' AND expiration_date < CURRENT_DATE;
```

---

## Maintenance Operations

### Archive Old Closed Trades

```sql
-- Move trades older than 1 year to archive table (create if needed)
CREATE TABLE IF NOT EXISTS xtrades_trades_archive (LIKE xtrades_trades INCLUDING ALL);

INSERT INTO xtrades_trades_archive
SELECT * FROM xtrades_trades
WHERE status = 'closed' AND exit_date < NOW() - INTERVAL '1 year';

DELETE FROM xtrades_trades
WHERE status = 'closed' AND exit_date < NOW() - INTERVAL '1 year';
```

### Clean Up Failed Notifications

```sql
-- Remove old failed notifications (after investigation)
DELETE FROM xtrades_notifications
WHERE status = 'failed' AND sent_at < NOW() - INTERVAL '30 days';
```

### Vacuum and Analyze

```sql
-- Optimize table storage and update statistics
VACUUM ANALYZE xtrades_profiles;
VACUUM ANALYZE xtrades_trades;
VACUUM ANALYZE xtrades_sync_log;
VACUUM ANALYZE xtrades_notifications;
```

---

## Files Reference

| File | Purpose |
|------|---------|
| `src/xtrades_schema.sql` | Main schema creation script |
| `src/xtrades_schema_rollback.sql` | Rollback/cleanup script |
| `src/xtrades_schema_queries.sql` | Collection of useful queries |
| `test_xtrades_schema.py` | Automated testing script |
| `docs/XTRADES_DATABASE_SCHEMA.md` | This documentation file |

---

## Next Steps

1. **Backend API**: Create Python/Node.js endpoints for CRUD operations
2. **Scraper Service**: Build Xtrades.net scraping service
3. **Notification Service**: Implement Telegram bot integration
4. **Analytics Dashboard**: Create frontend for data visualization
5. **Automated Sync**: Set up cron job or scheduled task for regular syncing

---

## Support and Maintenance

- **Database**: PostgreSQL 12+
- **Schema Version**: 1.0.0
- **Last Updated**: 2025-11-02
- **Maintainer**: Magnus Wheel Strategy Team

For issues or enhancements, refer to the main project documentation.
