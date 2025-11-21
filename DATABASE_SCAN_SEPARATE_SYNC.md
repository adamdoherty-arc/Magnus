# Database Scan - Separate Daily Sync Implementation

## Summary

Database Scan is now **completely separate** from TradingView Watchlists. It has its own automatic daily sync that runs AFTER market opens (10 AM ET) and syncs options data for ALL stocks in the `stocks` table.

---

## The Problem (Before)

❌ Database Scan relied on `stock_premiums` table
❌ Only populated by TradingView watchlist syncs
❌ Showed only 146 of 1,205 database stocks
❌ Required manual TradingView sync to add more stocks

---

## The Solution (After)

✅ Database Scan has its OWN daily automatic sync
✅ Runs AFTER market opens (10 AM ET) for fresh data
✅ Syncs options for ALL 1,205 stocks in `stocks` table
✅ Completely independent from TradingView activities
✅ Manual "Sync Now" button for immediate sync

---

## How It Works

### Automatic Daily Sync

```
Time: 10:00 AM ET (after market opens)
Trigger: First page load after 10 AM
Action: Launches sync_database_stocks_daily.py in background
Duration: 5-10 minutes for 1,205 stocks
Frequency: Once per day
```

### What Gets Synced

For EACH stock in the `stocks` table:
1. Fetches current stock price
2. Fetches all available option chains
3. Calculates Greeks (delta, IV, etc.)
4. Stores in `stock_premiums` table
5. Updates `stock_data` table with current price

### Manual Sync

**Location**: Database Scan → Premium Scanner tab
**Button**: "🔄 Sync Now"
**When to use**:
- Before 10 AM ET (before automatic sync)
- If automatic sync failed
- To get immediate fresh data

---

## Files Created

### 1. sync_database_stocks_daily.py

**Purpose**: Background sync script for all database stocks

**Key Features**:
- Gets all stocks from `stocks` table
- Uses `EnhancedOptionsFetcher` to fetch options data
- Stores results in `stock_premiums` and `stock_data`
- Rate limiting (0.3s delay between stocks, 5s every 50 stocks)
- Progress logging to `database_sync.log`
- Creates `database_sync_log` table to track sync history

**What it syncs**:
```python
- symbol
- strike_price
- expiration_date
- dte (days to expiration)
- premium
- delta
- implied_volatility
- bid/ask
- volume
- open_interest
- strike_type (e.g., "30_delta")
- monthly_return
- annual_return
```

---

## Dashboard Changes

### Page Load Auto-Sync ([dashboard.py:1184-1212](dashboard.py:1184-1212))

```python
# Auto-sync options data AFTER market opens (10 AM ET) if not done today
if last_db_sync_date != today and current_time_et >= sync_start_time:
    st.info("🔄 Starting daily database options sync (after market open)...")

    # Launch background sync
    subprocess.Popen(["python", "sync_database_stocks_daily.py"])

    st.session_state['last_db_options_sync_date'] = today
    st.session_state['db_sync_start_time'] = datetime.now()
    st.success("✅ Daily database options sync started in background!")
```

### Premium Scanner Info ([dashboard.py:1398-1401](dashboard.py:1398-1401))

Shows different messages based on sync status:

**After sync runs**:
```
💡 Showing 146 of 1,205 database stocks.
   Options data syncs daily at 10 AM ET after market opens.
```

**Before sync runs**:
```
⚠️ Showing 146 of 1,205 database stocks.
   Daily options sync will run at 10 AM ET.
   Click 'Sync Now' below to sync immediately.
```

### Manual Sync Button ([dashboard.py:1413-1432](dashboard.py:1413-1432))

```python
if st.button("🔄 Sync Now", type="primary"):
    subprocess.Popen(["python", "sync_database_stocks_daily.py"])
    st.success("✅ Sync started in background!
               Check database_sync.log for progress.
               Refresh page in 5-10 minutes.")
```

---

## Sync Timeline

### Typical Daily Flow

```
9:30 AM ET  → Market opens
10:00 AM ET → Database Scan auto-sync triggers
              (if user visits Database Scan page)
10:05 AM ET → Sync completes for ~1,205 stocks
10:06 AM ET → Premium Scanner shows ALL database stocks
```

### Manual Flow (Anytime)

```
User visits Database Scan → Premium Scanner
Clicks "🔄 Sync Now" button
Sync runs in background (5-10 minutes)
User refreshes page
Premium Scanner shows updated data
```

---

## Sync Performance

### Expected Timing

| Stocks | Time | Rate |
|--------|------|------|
| 100 | ~1 min | 100/min |
| 500 | ~5 min | 100/min |
| 1,205 | ~10 min | 120/min |

### Rate Limiting

- **Per-stock delay**: 0.3 seconds
- **Batch delay**: 5 seconds every 50 stocks
- **Purpose**: Avoid API rate limits

---

## Monitoring & Logs

### Log File: database_sync.log

**Location**: `c:\Code\WheelStrategy\database_sync.log`

**Sample Output**:
```
2025-11-04 10:00:15 - INFO - DATABASE STOCKS DAILY OPTIONS SYNC
2025-11-04 10:00:15 - INFO - [1] Fetching all stocks from database...
2025-11-04 10:00:15 - INFO -     Found 1205 stocks in database
2025-11-04 10:00:16 - INFO - [3] Syncing options data for 1205 stocks...
2025-11-04 10:00:16 - INFO -   AAPL: ✅ Synced 48 options
2025-11-04 10:00:17 - INFO -   ABBV: ✅ Synced 52 options
2025-11-04 10:00:18 - INFO -   ABNB: ✅ Synced 41 options
...
2025-11-04 10:10:05 - INFO - SYNC COMPLETE!
2025-11-04 10:10:05 - INFO - Total stocks: 1205
2025-11-04 10:10:05 - INFO - Successfully synced: 1180
2025-11-04 10:10:05 - INFO - Failed/No options: 25
2025-11-04 10:10:05 - INFO - Duration: 9.8 minutes
```

### Sync History Table: database_sync_log

**Schema**:
```sql
CREATE TABLE database_sync_log (
    id SERIAL PRIMARY KEY,
    sync_date DATE NOT NULL,
    sync_time TIMESTAMP NOT NULL,
    total_stocks INTEGER,
    successful_syncs INTEGER,
    failed_syncs INTEGER,
    duration_seconds INTEGER
)
```

**Query recent syncs**:
```sql
SELECT sync_date, sync_time,
       successful_syncs, failed_syncs,
       duration_seconds / 60 as duration_minutes
FROM database_sync_log
ORDER BY sync_time DESC
LIMIT 7;
```

---

## Separation from TradingView

### Database Scan (NEW)

| Aspect | Details |
|--------|---------|
| **Data Source** | `stocks` table (all 1,205 stocks) |
| **Sync Time** | 10 AM ET (after market opens) |
| **Sync Script** | `sync_database_stocks_daily.py` |
| **Frequency** | Once per day |
| **Manual Trigger** | "Sync Now" button in Premium Scanner |
| **Purpose** | Scan ALL database stocks for CSP opportunities |

### TradingView Watchlists (EXISTING)

| Aspect | Details |
|--------|---------|
| **Data Source** | `tv_symbols_api` table (watchlist symbols) |
| **Sync Time** | Pre-market (<9:30 AM ET) |
| **Sync Script** | `src/watchlist_sync_service.py` |
| **Frequency** | Every 5 minutes during market hours |
| **Manual Trigger** | "Sync Prices & Premiums" button |
| **Purpose** | Track specific watchlists you're monitoring |

**Key Difference**: Completely independent data sources and sync schedules!

---

## User Experience

### First Time Use

1. **Visit Database Scan → Premium Scanner**
2. **See message**: "⚠️ Showing 146 of 1,205 database stocks. Daily options sync will run at 10 AM ET. Click 'Sync Now' below to sync immediately."
3. **Click "Sync Now"** button
4. **See message**: "✅ Sync started in background! Check database_sync.log for progress. Refresh page in 5-10 minutes."
5. **Wait 5-10 minutes**
6. **Refresh page**
7. **See ALL 1,205 stocks** in Premium Scanner

### Daily Use (After 10 AM)

1. **Visit Database Scan → Premium Scanner**
2. **Automatic sync already ran** at 10 AM
3. **See message**: "💡 Showing 1,180 of 1,205 database stocks. Options data syncs daily at 10 AM ET after market opens."
4. **All stocks available** with today's fresh data
5. **Filter and sort** to find best CSP opportunities

---

## What Gets Populated

### Before Sync

**Database Count**:
- Total stocks in database: 1,205
- Stocks with options data: 146
- Premium Scanner shows: 120 (filtered by delta/DTE)

### After Sync

**Database Count**:
- Total stocks in database: 1,205
- Stocks with options data: ~1,180 (some have no options)
- Premium Scanner shows: ~800-1,000 (filtered by delta/DTE)

**Why not all 1,205?**
Some stocks don't have options available (too small, too new, delisted, etc.)

---

## Premium Scanner Query

The Premium Scanner still queries the same `stock_premiums` table, but now it's populated by:
1. ✅ Database daily sync (ALL database stocks)
2. ✅ TradingView watchlist syncs (watchlist stocks)

Both can coexist in the same table!

**Query**:
```sql
SELECT DISTINCT ON (sp.symbol)
    sp.symbol,
    sd.current_price as stock_price,
    sp.strike_price,
    sp.dte,
    sp.premium,
    sp.delta,
    sp.monthly_return,
    sp.implied_volatility as iv,
    sp.bid, sp.ask, sp.volume, sp.open_interest as oi,
    s.name, s.sector
FROM stock_premiums sp
LEFT JOIN stock_data sd ON sp.symbol = sd.symbol
LEFT JOIN stocks s ON sp.symbol = s.ticker
WHERE sp.dte BETWEEN 29 AND 33
    AND ABS(sp.delta) BETWEEN 0.25 AND 0.40
    AND sp.premium >= 0
ORDER BY sp.symbol, sp.monthly_return DESC
```

---

## Troubleshooting

### Problem: Sync not running automatically

**Check**:
1. Time is after 10:00 AM ET
2. You visited the Database Scan page today
3. Check `database_sync.log` for errors

**Solution**:
Click "Sync Now" button manually

### Problem: Sync running but no new stocks appear

**Check**:
1. Wait 5-10 minutes for sync to complete
2. Check `database_sync.log` for progress
3. Refresh the dashboard page

**Solution**:
```bash
# Check if sync is still running
tasklist | findstr python

# Check last sync
tail -n 50 database_sync.log
```

### Problem: Some stocks still missing

**Possible Reasons**:
1. Stock doesn't have options (too small, delisted, etc.)
2. API rate limit hit during sync
3. Stock ticker changed

**Check**:
```sql
-- Find stocks without options data
SELECT s.ticker
FROM stocks s
LEFT JOIN stock_premiums sp ON s.ticker = sp.symbol
WHERE sp.symbol IS NULL
LIMIT 20;
```

---

## Session State Variables

| Variable | Type | Purpose |
|----------|------|---------|
| `last_db_options_sync_date` | `date` | Date of last automatic sync |
| `db_sync_start_time` | `datetime` | When sync started (for display) |

---

## Future Enhancements

### Potential Improvements

1. **Progress Bar**: Real-time progress in dashboard
2. **Email Notification**: When sync completes
3. **Selective Sync**: Only sync stocks you're interested in
4. **Parallel Processing**: Speed up sync with concurrency
5. **Options Volume Filter**: Only sync liquid options
6. **Sector Filtering**: Sync specific sectors first

### Scheduling Options

Current: Manual trigger or page load at 10 AM

**Alternative 1**: Windows Task Scheduler
```batch
# Schedule to run at 10 AM daily
schtasks /create /tn "Database Options Sync" /tr "python c:\Code\WheelStrategy\sync_database_stocks_daily.py" /sc daily /st 10:00
```

**Alternative 2**: Python Scheduler
```python
import schedule
schedule.every().day.at("10:00").do(run_sync)
```

---

## Summary

✅ **Database Scan is now independent** from TradingView Watchlists
✅ **Automatic daily sync** runs at 10 AM ET after market opens
✅ **Syncs ALL 1,205 stocks** from database
✅ **Manual "Sync Now"** button for immediate sync
✅ **Background processing** doesn't block dashboard
✅ **Comprehensive logging** for monitoring
✅ **Sync history** tracked in database

---

## Testing

### Test Automatic Sync

1. Set system time to 10:05 AM ET
2. Open Dashboard → Database Scan
3. Should see: "🔄 Starting daily database options sync..."
4. Check `database_sync.log` for progress

### Test Manual Sync

1. Open Dashboard → Database Scan → Premium Scanner
2. Click "🔄 Sync Now" button
3. Check `database_sync.log` for progress
4. Wait 5-10 minutes
5. Refresh page
6. Verify stock count increased

---

## Files Modified

| File | Lines | Changes |
|------|-------|---------|
| [dashboard.py](dashboard.py) | 1184-1212 | Added auto-sync logic (10 AM ET) |
| [dashboard.py](dashboard.py) | 1398-1401 | Updated Premium Scanner info message |
| [dashboard.py](dashboard.py) | 1413-1432 | Added manual "Sync Now" button |

## Files Created

| File | Purpose |
|------|---------|
| [sync_database_stocks_daily.py](sync_database_stocks_daily.py) | Background sync script for all database stocks |
| database_sync.log | Sync progress and error log |

---

## Conclusion

Database Scan now has its own dedicated daily sync process that runs AFTER market opens and syncs options data for ALL database stocks. This is completely separate from TradingView Watchlists and gives you a comprehensive view of ALL stocks in your database for finding the best CSP opportunities.

**Next Steps**:
1. Click "Sync Now" to run initial sync
2. Wait 5-10 minutes
3. Refresh page
4. See ALL 1,205 stocks in Premium Scanner!
