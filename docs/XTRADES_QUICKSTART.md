# Xtrades Watchlists - Quick Start Guide

## Overview

This guide will help you quickly get started with the Xtrades Watchlists database schema.

---

## Installation

### Step 1: Install the Schema

Run the automated test script (recommended):

```bash
python test_xtrades_schema.py
```

Or manually execute the SQL:

```bash
psql -h localhost -U postgres -d magnus -f src/xtrades_schema.sql
```

### Step 2: Verify Installation

```bash
python verify_xtrades_installation.py
```

You should see:
- 4 tables created
- 19+ indexes created
- Sample data inserted
- System statistics

---

## Quick Reference

### Table Summary

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `xtrades_profiles` | Traders to monitor | username, active, last_sync |
| `xtrades_trades` | Individual trades | ticker, strategy, status, pnl |
| `xtrades_sync_log` | Sync audit trail | sync_timestamp, status |
| `xtrades_notifications` | Notification tracking | trade_id, notification_type |

### Common Operations

#### Add a Profile to Monitor

```python
import psycopg2
conn = psycopg2.connect(**db_config)
cur = conn.cursor()

cur.execute("""
    INSERT INTO xtrades_profiles (username, display_name, active, notes)
    VALUES (%s, %s, %s, %s)
    RETURNING id
""", ('traderJoe', 'Joe the Trader', True, 'Focuses on wheel strategy'))

profile_id = cur.fetchone()[0]
conn.commit()
print(f"Created profile with ID: {profile_id}")
```

#### Record a New Trade

```python
cur.execute("""
    INSERT INTO xtrades_trades (
        profile_id, ticker, strategy, action, entry_price, entry_date,
        quantity, status, strike_price, expiration_date,
        alert_text, alert_timestamp
    )
    VALUES (%s, %s, %s, %s, %s, NOW(), %s, %s, %s, %s, %s, NOW())
    RETURNING id
""", (
    profile_id, 'AAPL', 'CSP', 'STO', 2.50,
    1, 'open', 170.00, '2025-12-15',
    'AAPL CSP: STO 1x $170 PUT @ $2.50 exp 12/15/2025'
))

trade_id = cur.fetchone()[0]
conn.commit()
print(f"Created trade with ID: {trade_id}")
```

#### Close a Trade

```python
entry_price = 2.50
exit_price = 1.25
quantity = 1

pnl = (entry_price - exit_price) * 100 * quantity  # $125
pnl_percent = ((entry_price - exit_price) / entry_price) * 100  # 50%

cur.execute("""
    UPDATE xtrades_trades
    SET exit_price = %s,
        exit_date = NOW(),
        pnl = %s,
        pnl_percent = %s,
        status = 'closed',
        updated_at = NOW()
    WHERE id = %s
""", (exit_price, pnl, pnl_percent, trade_id))

conn.commit()
print(f"Closed trade {trade_id} with ${pnl:.2f} profit")
```

#### Log a Sync Operation

```python
import time

start_time = time.time()
# ... perform sync operations ...
duration = time.time() - start_time

cur.execute("""
    INSERT INTO xtrades_sync_log (
        profiles_synced, trades_found, new_trades, updated_trades,
        duration_seconds, status, errors
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s)
""", (3, 15, 10, 5, duration, 'success', None))

conn.commit()
```

#### Record a Notification

```python
cur.execute("""
    INSERT INTO xtrades_notifications (
        trade_id, notification_type, telegram_message_id, status
    )
    VALUES (%s, %s, %s, %s)
""", (trade_id, 'new_trade', '987654321', 'sent'))

conn.commit()
```

---

## Essential Queries

### Get All Open Positions

```sql
SELECT
    p.username,
    t.ticker,
    t.strategy,
    t.strike_price,
    t.expiration_date,
    t.entry_price,
    EXTRACT(DAY FROM (t.expiration_date - CURRENT_DATE)) as days_to_exp
FROM xtrades_trades t
JOIN xtrades_profiles p ON t.profile_id = p.id
WHERE t.status = 'open'
ORDER BY t.expiration_date;
```

### Performance by Profile

```sql
SELECT
    p.username,
    COUNT(*) as total_trades,
    SUM(t.pnl) as total_pnl,
    AVG(t.pnl_percent) as avg_return_pct,
    COUNT(CASE WHEN t.pnl > 0 THEN 1 END) as winning_trades
FROM xtrades_profiles p
JOIN xtrades_trades t ON p.id = t.profile_id
WHERE t.status = 'closed'
GROUP BY p.id, p.username
ORDER BY total_pnl DESC;
```

### Recent Trades (Last 24 Hours)

```sql
SELECT
    p.username,
    t.ticker,
    t.strategy,
    t.action,
    t.status,
    t.alert_timestamp
FROM xtrades_trades t
JOIN xtrades_profiles p ON t.profile_id = p.id
WHERE t.alert_timestamp >= NOW() - INTERVAL '24 hours'
ORDER BY t.alert_timestamp DESC;
```

### System Health Check

```sql
SELECT
    (SELECT COUNT(*) FROM xtrades_profiles WHERE active = TRUE) as active_profiles,
    (SELECT COUNT(*) FROM xtrades_trades WHERE status = 'open') as open_positions,
    (SELECT COUNT(*) FROM xtrades_trades WHERE status = 'closed') as closed_trades,
    (SELECT COALESCE(SUM(pnl), 0) FROM xtrades_trades WHERE status = 'closed') as total_pnl,
    (SELECT MAX(sync_timestamp) FROM xtrades_sync_log) as last_sync;
```

---

## Python Helper Class

Here's a simple Python class to make database operations easier:

```python
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, List, Dict
from datetime import datetime
import os
from dotenv import load_dotenv

class XtradesDB:
    """Helper class for Xtrades database operations"""

    def __init__(self):
        load_dotenv()
        self.config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'database': os.getenv('DB_NAME', 'magnus'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'postgres123!')
        }

    def get_connection(self):
        """Get database connection"""
        return psycopg2.connect(**self.config)

    def add_profile(self, username: str, display_name: str = None,
                   active: bool = True, notes: str = None) -> int:
        """Add a new profile to monitor"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO xtrades_profiles (username, display_name, active, notes)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (username) DO UPDATE
                    SET display_name = EXCLUDED.display_name,
                        active = EXCLUDED.active,
                        notes = EXCLUDED.notes
                    RETURNING id
                """, (username, display_name, active, notes))
                return cur.fetchone()[0]

    def add_trade(self, profile_id: int, ticker: str, strategy: str,
                 action: str, entry_price: float, strike_price: float,
                 expiration_date: str, alert_text: str, **kwargs) -> int:
        """Add a new trade"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO xtrades_trades (
                        profile_id, ticker, strategy, action, entry_price,
                        strike_price, expiration_date, alert_text, alert_timestamp,
                        quantity, status
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), %s, %s)
                    RETURNING id
                """, (
                    profile_id, ticker, strategy, action, entry_price,
                    strike_price, expiration_date, alert_text,
                    kwargs.get('quantity', 1), kwargs.get('status', 'open')
                ))
                return cur.fetchone()[0]

    def close_trade(self, trade_id: int, exit_price: float,
                   exit_date: datetime = None):
        """Close a trade and calculate P&L"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Get entry price and quantity
                cur.execute("""
                    SELECT entry_price, quantity, action
                    FROM xtrades_trades
                    WHERE id = %s
                """, (trade_id,))
                trade = cur.fetchone()

                if not trade:
                    raise ValueError(f"Trade {trade_id} not found")

                # Calculate P&L
                # For credit strategies (STO), profit when exit < entry
                # For debit strategies (BTO), profit when exit > entry
                if trade['action'] in ('STO', 'CLOSE'):
                    pnl = (trade['entry_price'] - exit_price) * 100 * trade['quantity']
                else:
                    pnl = (exit_price - trade['entry_price']) * 100 * trade['quantity']

                pnl_percent = (pnl / (trade['entry_price'] * 100 * trade['quantity'])) * 100

                # Update trade
                cur.execute("""
                    UPDATE xtrades_trades
                    SET exit_price = %s,
                        exit_date = COALESCE(%s, NOW()),
                        pnl = %s,
                        pnl_percent = %s,
                        status = 'closed',
                        updated_at = NOW()
                    WHERE id = %s
                """, (exit_price, exit_date, pnl, pnl_percent, trade_id))

    def get_open_positions(self, profile_id: Optional[int] = None) -> List[Dict]:
        """Get all open positions"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                query = """
                    SELECT
                        t.*,
                        p.username,
                        EXTRACT(DAY FROM (t.expiration_date - CURRENT_DATE)) as days_to_exp
                    FROM xtrades_trades t
                    JOIN xtrades_profiles p ON t.profile_id = p.id
                    WHERE t.status = 'open'
                """
                if profile_id:
                    query += " AND t.profile_id = %s"
                    cur.execute(query + " ORDER BY t.expiration_date", (profile_id,))
                else:
                    cur.execute(query + " ORDER BY t.expiration_date")
                return cur.fetchall()

    def get_profile_performance(self, profile_id: int) -> Dict:
        """Get performance stats for a profile"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT
                        COUNT(*) as total_trades,
                        COUNT(CASE WHEN status = 'closed' THEN 1 END) as closed_trades,
                        COUNT(CASE WHEN status = 'open' THEN 1 END) as open_trades,
                        COALESCE(SUM(pnl), 0) as total_pnl,
                        COALESCE(AVG(pnl_percent), 0) as avg_return_pct,
                        COUNT(CASE WHEN pnl > 0 THEN 1 END) as winning_trades,
                        COUNT(CASE WHEN pnl < 0 THEN 1 END) as losing_trades
                    FROM xtrades_trades
                    WHERE profile_id = %s AND status = 'closed'
                """, (profile_id,))
                return cur.fetchone()

# Usage example:
if __name__ == '__main__':
    db = XtradesDB()

    # Add profile
    profile_id = db.add_profile('traderJoe', 'Joe the Trader', notes='Test profile')
    print(f"Profile ID: {profile_id}")

    # Add trade
    trade_id = db.add_trade(
        profile_id=profile_id,
        ticker='AAPL',
        strategy='CSP',
        action='STO',
        entry_price=2.50,
        strike_price=170.00,
        expiration_date='2025-12-15',
        alert_text='AAPL CSP alert',
        quantity=1
    )
    print(f"Trade ID: {trade_id}")

    # Get open positions
    positions = db.get_open_positions(profile_id)
    print(f"Open positions: {len(positions)}")

    # Close trade
    db.close_trade(trade_id, exit_price=1.25)
    print(f"Trade {trade_id} closed")

    # Get performance
    perf = db.get_profile_performance(profile_id)
    print(f"Performance: {perf}")
```

---

## Next Steps

1. **Integrate Scraper**: Build the Xtrades.net scraping service
2. **Add API Endpoints**: Create REST API for frontend
3. **Build Dashboard**: Create React/Vue dashboard for visualization
4. **Set Up Notifications**: Implement Telegram bot integration
5. **Schedule Syncs**: Add automated sync cron job

---

## Troubleshooting

### Tables Not Created

Check if the SQL file executed successfully:
```bash
python test_xtrades_schema.py
```

### Connection Errors

Verify your `.env` file has correct database credentials:
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=magnus
DB_USER=postgres
DB_PASSWORD=your_password
```

### Data Quality Issues

Run the verification script:
```bash
python verify_xtrades_installation.py
```

Check for data issues:
```sql
-- See queries in src/xtrades_schema_queries.sql under "DATA QUALITY CHECKS"
```

---

## Resources

- **Full Documentation**: `docs/XTRADES_DATABASE_SCHEMA.md`
- **Schema SQL**: `src/xtrades_schema.sql`
- **Useful Queries**: `src/xtrades_schema_queries.sql`
- **Rollback Script**: `src/xtrades_schema_rollback.sql`
- **Test Script**: `test_xtrades_schema.py`

---

## Support

For questions or issues, refer to the main documentation or check the database logs.
