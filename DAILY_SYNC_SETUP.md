# Daily Trade Sync - Automated Setup Guide

## Overview

The Daily Trade Sync service automatically synchronizes closed trades from Robinhood to your Magnus database at the end of each trading day (4:30 PM ET). This ensures:

- **Fast page loads** - Trade history loads from database instantly
- **No API delays** - Avoids slow Robinhood API calls on every page view
- **Historical data** - Maintains complete trade history in database
- **Automatic updates** - Syncs new trades daily without manual intervention

## Quick Setup (Windows)

### Method 1: Automated Setup (Recommended)

Run the PowerShell setup script as Administrator:

```powershell
# Right-click PowerShell and "Run as Administrator"
cd C:\Code\WheelStrategy
.\setup_daily_sync.ps1
```

This creates a Windows Task Scheduler task that runs daily at 4:30 PM ET.

### Method 2: Manual Task Creation

1. Open Task Scheduler (`taskschd.msc`)
2. Click "Create Task" (not "Create Basic Task")
3. **General Tab:**
   - Name: `Magnus_Daily_Trade_Sync`
   - Description: `Syncs closed trades from Robinhood to database`
   - Run whether user is logged on or not
   - Do not run with highest privileges
4. **Triggers Tab:**
   - New → Daily
   - Start time: 4:30 PM
   - Recur every: 1 day
5. **Actions Tab:**
   - New → Start a program
   - Program: `python` (or full path to python.exe)
   - Arguments: `daily_trade_sync.py`
   - Start in: `C:\Code\WheelStrategy`
6. **Settings Tab:**
   - ✅ Allow task to be run on demand
   - ✅ Run task as soon as possible after a scheduled start is missed
   - ✅ Start the task only if the network is available

## Testing

### Test the sync manually:

```bash
cd C:\Code\WheelStrategy
python daily_trade_sync.py
```

You should see output like:

```
============================================================
Starting daily trade sync
Timestamp: 2025-11-01 04:30:00 PM
============================================================
🔐 Logging into Robinhood...
✅ Login successful
📅 Last sync: 2025-10-31 04:30:15 PM
🔄 Syncing trades from Robinhood to database...
✅ Successfully synced 3 new closed trades
📊 Total closed trades in last 30 days: 42
💰 30-day P/L: $1,247.50
🔒 Logged out of Robinhood
============================================================
✅ Daily sync completed successfully
============================================================
```

## Logs

Logs are stored in `logs/` directory:
- Filename format: `trade_sync_YYYYMMDD.log`
- One log file per day
- Includes timestamps, sync status, and error details

View today's log:
```bash
cat logs/trade_sync_$(date +%Y%m%d).log
```

## Troubleshooting

### Task not running

1. Open Task Scheduler
2. Find "Magnus_Daily_Trade_Sync"
3. Right-click → "Run" to test manually
4. Check "Last Run Result" column:
   - `0x0` = Success
   - Other codes = Error (check logs)

### Missing credentials

Ensure `.env` file contains:
```
RH_USERNAME=your_robinhood_email
RH_PASSWORD=your_robinhood_password
```

### Database connection errors

Ensure database credentials in `.env`:
```
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
```

### Python not found

If Task Scheduler can't find Python:
1. Open Task and edit the Action
2. Use full path to python.exe:
   - Example: `C:\Python311\python.exe`
   - Find your path: `where python`

## Schedule Configuration

Default schedule: **Daily at 4:30 PM ET**

This is 30 minutes after market close (4:00 PM ET), allowing time for:
- Final trades to settle
- Robinhood to update order status
- All closing prices to finalize

### Change sync time:

Option 1: Edit in Task Scheduler
- Open Task Scheduler
- Right-click task → Properties
- Triggers tab → Edit trigger
- Change time

Option 2: Re-run setup script
- Edit time in `setup_daily_sync.ps1` (line with `-At "4:30 PM"`)
- Run script again

## Manual Sync

You can manually sync trades anytime:

1. **From command line:**
   ```bash
   python daily_trade_sync.py
   ```

2. **From Positions page:**
   - Click "🔄 Sync Now" button
   - Located in Trade History section header

3. **From Task Scheduler:**
   - Right-click task → Run

## Sync Service Files

- `daily_trade_sync.py` - Main sync script
- `src/trade_history_sync.py` - Sync service class
- `setup_daily_sync.ps1` - Windows setup script
- `logs/` - Daily sync logs

## Database Table

Trades are stored in the `trade_history` table:

```sql
-- View all closed trades
SELECT * FROM trade_history WHERE status = 'closed' ORDER BY close_date DESC;

-- View today's synced trades
SELECT * FROM trade_history WHERE DATE(updated_at) = CURRENT_DATE;

-- 30-day performance
SELECT
    COUNT(*) as trades,
    SUM(profit_loss) as total_pl,
    AVG(profit_loss) as avg_pl
FROM trade_history
WHERE close_date >= CURRENT_DATE - INTERVAL '30 days'
AND status = 'closed';
```

## Performance Benefits

**Before (Robinhood API):**
- Trade History load time: 5-10 seconds
- Every page load calls API
- Rate limited by Robinhood

**After (Database):**
- Trade History load time: <0.1 seconds
- Instant page loads
- No API rate limits
- Historical data preserved

## Support

For issues:
1. Check logs in `logs/` directory
2. Test manual sync: `python daily_trade_sync.py`
3. Verify database connection
4. Verify Robinhood credentials
5. Check Task Scheduler "Last Run Result"
