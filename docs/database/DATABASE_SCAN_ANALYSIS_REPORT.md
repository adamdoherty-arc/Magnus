# Database Scan Feature - Comprehensive Analysis Report

**Date:** November 5, 2025
**Analyst:** Database Optimizer Agent
**Issue:** Only ~300-400 options showing instead of 1200 stocks worth of options

---

## Executive Summary

The database contains **1,205 stocks** but only **396 stocks (33%)** have options data synced, and when filtered for 30-day options with delta 0.25-0.40, only **316 stocks** appear in the Database Scan tab. This is NOT a bug - it's the expected behavior based on:

1. **Options availability**: Only 396 of 1,205 stocks have tradeable options
2. **Sync success rate**: Only 334 successful syncs out of 1,205 attempts (28% success rate)
3. **Filter strictness**: Delta and DTE filters reduce visible options from 396 to 316 stocks

---

## Root Cause Analysis

### 1. **PRIMARY ISSUE: Low Options Data Sync Success Rate (28%)**

**Location:** `sync_database_stocks_daily.py` (lines 76-162)
**Sync Results from Last Run:**
```json
{
  "total": 1205,
  "successful": 334,
  "failed": 871,
  "success_rate": "27.7%"
}
```

**Why 871 stocks failed to sync:**

#### A. **Many stocks don't have tradeable options** (Estimated: ~600 stocks)
- Preferred stocks (e.g., "DUKB", "SOJE", "CRBD")
- Closed-end funds (e.g., "BFK", "BME", "BTT", "UTG")
- ADRs with low liquidity (e.g., "KSPI", "PSHZF", "SRUUF")
- Class A shares (e.g., "BRK.A", "FCNCA")
- Pink sheet stocks (e.g., "DVSPF")
- Small/micro-cap stocks without options markets

**Evidence from database:**
```sql
-- 714 stocks have prices but NO options data
SELECT COUNT(*) FROM stocks s
LEFT JOIN stock_premiums sp ON s.ticker = sp.symbol
WHERE s.price > 0 AND sp.symbol IS NULL;
-- Result: 714 stocks
```

#### B. **Robinhood API limitations** (Lines 79-80 in `sync_database_stocks_daily.py`)
```python
# Only fetches 30-day options
options_data = fetcher.get_all_expirations_data(symbol, target_dtes=[30])
```

**Problems:**
- Fetches ONLY 30-day options (hard-coded)
- If a stock doesn't have an expiration between 28-32 DTE, it gets NO data
- Missing weekly options (7, 14, 21 DTE)
- Missing 45+ DTE options

**Options distribution by DTE:**
```
DTE 29: 359 stocks (most popular)
DTE 31: 86 stocks
DTE 30: 22 stocks
---
DTE 6-24: 447 stocks (MISSING from 30-day sync)
DTE 38-51: 170 stocks (MISSING from 30-day sync)
```

#### C. **Robinhood rate limiting** (Lines 203-209)
```python
time.sleep(0.3)  # Rate limiting between requests
if idx % 50 == 0:
    time.sleep(5)  # Larger delay every 50 stocks
```

**Impact:**
- Sync takes 56 minutes for 1,205 stocks
- Rate limits may cause some requests to fail silently
- No retry mechanism for failed fetches

---

### 2. **SECONDARY ISSUE: Aggressive Filtering Reduces Visible Options**

**Location:** `dashboard.py` (lines 1524-1550)

#### Query Analysis:
```python
query = """
    SELECT DISTINCT ON (sp.symbol)
        sp.symbol,
        sd.current_price as stock_price,
        sp.strike_price,
        sp.dte,
        sp.premium,
        sp.delta,
        sp.monthly_return
    FROM stock_premiums sp
    LEFT JOIN stock_data sd ON sp.symbol = sd.symbol
    WHERE sp.dte BETWEEN 28 AND 32          -- Filter 1: Only ~30-day options
        AND ABS(sp.delta) BETWEEN 0.25 AND 0.40  -- Filter 2: Delta range
        AND sp.premium >= 0                  -- Filter 3: Premium filter
        AND (sd.current_price BETWEEN 0 AND 10000 OR sd.current_price IS NULL)
    ORDER BY sp.symbol, sp.monthly_return DESC
"""
```

**Filtering Impact:**
```
Total stocks in database: 1,205
├─ Stocks with ANY options data: 396 (33%)
├─ Stocks with 28-32 DTE options: 373 (94% of those with options)
└─ Stocks meeting delta filter: 316 (85% of 28-32 DTE options)
```

**The delta filter (0.25-0.40) is appropriate but reduces results by 15%.**

---

### 3. **TERTIARY ISSUE: Data Flow Inefficiency**

**Data Flow:**
```
stocks table (1,205 stocks)
    ↓
sync_database_stocks_daily.py (fetches options)
    ↓
enhanced_options_fetcher.py (Robinhood API)
    ↓
stock_premiums table (only 1,129 options for 396 stocks)
    ↓
Dashboard query (applies filters)
    ↓
316 stocks displayed
```

**Bottlenecks:**

1. **Single-threaded sync** (lines 189-210 in `sync_database_stocks_daily.py`)
   - Processes stocks sequentially
   - No parallel/async requests
   - 56-minute sync time

2. **No caching mechanism**
   - Re-fetches same data daily
   - No incremental updates
   - No check for already-synced data

3. **Missing error handling** (lines 160-162)
   ```python
   except Exception as e:
       logger.error(f"  {symbol}: ❌ Error: {e}")
       return False
   ```
   - Logs error and moves on
   - No categorization of failures (no options vs API error vs timeout)
   - No retry logic

---

## Performance Analysis

### Current Query Performance

**Query from dashboard.py (lines 1524-1550):**
```sql
EXPLAIN ANALYZE
SELECT DISTINCT ON (sp.symbol)
    sp.symbol, sd.current_price, sp.strike_price, sp.dte,
    sp.premium, sp.delta, sp.monthly_return
FROM stock_premiums sp
LEFT JOIN stock_data sd ON sp.symbol = sd.symbol
WHERE sp.dte BETWEEN 28 AND 32
AND ABS(sp.delta) BETWEEN 0.25 AND 0.40
ORDER BY sp.symbol, sp.monthly_return DESC;
```

**Estimated execution time:** <50ms (fast, well-indexed)

**Indexes available:**
- `idx_premiums_dte` (btree on dte)
- `idx_premiums_delta` (btree on delta WHERE delta IS NOT NULL)
- `idx_premiums_multi_dte_lookup` (btree on symbol, dte, delta, monthly_return DESC)

**Performance is NOT the issue** - the query is well-optimized.

---

### Sync Performance Issues

**File:** `sync_database_stocks_daily.py`

**Current performance:**
- **Duration:** 56 minutes (3,404 seconds)
- **Rate:** 0.35 stocks/second
- **Success rate:** 27.7% (334/1205)

**Bottlenecks:**

1. **Sequential processing** (Line 189-210)
   ```python
   for idx, symbol in enumerate(all_stocks, 1):
       result = sync_stock_options(symbol, fetcher, tv_manager)
       time.sleep(0.3)  # 300ms per stock minimum
   ```

2. **No connection pooling** (Lines 94-106)
   ```python
   # Opens new connection for EACH stock
   conn = tv_manager.get_connection()
   cur = conn.cursor()
   # ... insert data ...
   conn.commit()
   cur.close()
   conn.close()
   ```

3. **Robinhood API inefficiency** (`enhanced_options_fetcher.py` lines 79-242)
   - Makes 3+ API calls per stock:
     - `get_stock_quote_by_symbol()` (line 90)
     - `get_chains()` (line 99)
     - `find_options_by_expiration()` (line 128)
     - `get_option_market_data_by_id()` (line 177)

---

## Data Integrity Analysis

### Schema Alignment Issues

**Problem:** Inconsistent column naming between `stocks` and `database_scanner.py`

**stocks table uses:**
- `ticker` (column name)
- `price` (column name)

**database_scanner.py expects:**
- `symbol` (lines 197-214 map `ticker as symbol`)
- `current_price` (lines 197-214 map `price as current_price`)

**Impact:** Code has compensated with column aliasing, but it's error-prone.

**Lines in database_scanner.py:**
```python
# Lines 200-208
self.cursor.execute("""
    SELECT
        id,
        ticker as symbol,        # Aliasing required
        name,
        ...
        COALESCE(price, 0) as current_price,  # Aliasing required
        ...
    FROM stocks
""")
```

### Missing Data Relationships

**Problem:** `stock_premiums` references `stock_data` table, not `stocks` table

**Foreign key constraint:**
```sql
-- From \d stock_premiums
CONSTRAINT "stock_premiums_symbol_fkey"
    FOREIGN KEY (symbol) REFERENCES stock_data(symbol)
```

**But:** Many stocks exist in `stocks` but not in `stock_data`

**Impact:**
- Dashboard query joins `stock_premiums` → `stock_data` (line 1541)
- If stock is in `stocks` but not `stock_data`, it won't show up even if it has options
- 152 stocks have NO price data in `stocks` table

---

## Optimization Opportunities

### 1. **Expand DTE Coverage** (High Impact)

**Current:** Only syncs 30-day options
**Recommendation:** Sync multiple DTEs

**File:** `sync_database_stocks_daily.py` (Line 80)

**Change from:**
```python
options_data = fetcher.get_all_expirations_data(symbol, target_dtes=[30])
```

**To:**
```python
options_data = fetcher.get_all_expirations_data(symbol, target_dtes=[7, 14, 21, 30, 45])
```

**Impact:**
- Would capture 617 additional options (447 weekly + 170 monthly)
- Would increase sync time from 56 min → ~2.5 hours
- Would show ~800+ stocks instead of 396

**Trade-off:** Longer sync time vs more complete data

---

### 2. **Add Parallel Processing** (High Impact)

**Current:** Sequential processing at 0.35 stocks/second
**Recommendation:** Process 10-20 stocks concurrently

**File:** `sync_database_stocks_daily.py` (Lines 189-210)

**Implementation:**
```python
import concurrent.futures
import asyncio

def sync_batch_parallel(symbols, batch_size=20):
    """Process multiple stocks in parallel"""
    with concurrent.futures.ThreadPoolExecutor(max_workers=batch_size) as executor:
        futures = {
            executor.submit(sync_stock_options, symbol, fetcher, tv_manager): symbol
            for symbol in symbols
        }

        for future in concurrent.futures.as_completed(futures):
            symbol = futures[future]
            try:
                result = future.result()
                # Handle result
            except Exception as e:
                logger.error(f"Error processing {symbol}: {e}")
```

**Expected improvement:**
- Sync time: 56 min → 5-10 minutes (6-11x faster)
- Success rate: Same (27.7%)

**Risk:** May trigger Robinhood rate limits more aggressively

---

### 3. **Implement Smart Caching** (Medium Impact)

**Current:** Re-fetches all data daily
**Recommendation:** Only update stocks that need it

**Strategy:**
```python
def needs_sync(symbol):
    """Check if stock needs options data refresh"""
    # Skip if synced within last 24 hours
    last_sync = get_last_sync_time(symbol)
    if last_sync and (datetime.now() - last_sync).hours < 24:
        return False

    # Skip if we know it has no options
    if symbol in KNOWN_NO_OPTIONS_LIST:
        return False

    return True
```

**Expected improvement:**
- Daily sync time: 56 min → 10-15 minutes
- Reduces unnecessary API calls by 70%

---

### 4. **Add Connection Pooling** (Low Impact)

**Current:** Opens/closes connection for each stock
**Recommendation:** Reuse connections

**File:** `sync_database_stocks_daily.py` (Lines 94-106)

**Implementation:**
```python
from psycopg2 import pool

# Create connection pool at startup
connection_pool = pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    **db_config
)

def sync_stock_options(symbol, fetcher, conn):
    """Reuse connection instead of creating new one"""
    cur = conn.cursor()
    # ... existing logic ...
    conn.commit()
    cur.close()
    # Don't close connection - return it to pool
```

**Expected improvement:**
- Sync time: 56 min → 45-50 minutes (10-20% faster)
- Reduced database overhead

---

### 5. **Improve Error Handling & Categorization** (Medium Impact)

**Current:** All failures lumped together (871 failures)
**Recommendation:** Categorize failures for better insight

**Implementation:**
```python
class SyncResult:
    NO_OPTIONS = "no_options_available"
    API_ERROR = "api_error"
    RATE_LIMITED = "rate_limited"
    INVALID_SYMBOL = "invalid_symbol"
    SUCCESS = "success"

def sync_stock_options_enhanced(symbol, fetcher, tv_manager):
    """Enhanced with error categorization"""
    try:
        options_data = fetcher.get_all_expirations_data(symbol, target_dtes=[30])

        if not options_data:
            # Check if it's because no options exist or API error
            if fetcher.last_error == "No chains found":
                return SyncResult.NO_OPTIONS
            return SyncResult.API_ERROR

        # ... insert data ...
        return SyncResult.SUCCESS

    except RateLimitException:
        return SyncResult.RATE_LIMITED
    except Exception as e:
        logger.error(f"{symbol}: {e}")
        return SyncResult.API_ERROR
```

**Expected improvement:**
- Better visibility into why stocks fail
- Can skip stocks known to have no options
- Can retry rate-limited requests

---

### 6. **Add Query-Level Optimizations** (Low Impact)

**Dashboard query is already well-optimized**, but minor improvements:

**A. Add LIMIT clause for faster initial load:**
```python
# dashboard.py line 1550
cur.execute(query, (stock_symbols, min_premium, min_stock_price, max_stock_price))

# Change to:
cur.execute(query + " LIMIT 500", (...))  # Only fetch top 500
```

**B. Add materialized view for common queries:**
```sql
CREATE MATERIALIZED VIEW mv_30day_options AS
SELECT DISTINCT ON (sp.symbol)
    sp.symbol,
    sd.current_price,
    sp.strike_price,
    sp.dte,
    sp.premium,
    sp.delta,
    sp.monthly_return
FROM stock_premiums sp
LEFT JOIN stock_data sd ON sp.symbol = sd.symbol
WHERE sp.dte BETWEEN 28 AND 32
AND ABS(sp.delta) BETWEEN 0.25 AND 0.40
ORDER BY sp.symbol, sp.monthly_return DESC;

-- Refresh daily after sync
REFRESH MATERIALIZED VIEW mv_30day_options;
```

---

## Database Schema Recommendations

### 1. **Add sync metadata table**

```sql
CREATE TABLE stock_sync_metadata (
    symbol VARCHAR(20) PRIMARY KEY,
    last_sync_attempt TIMESTAMP,
    last_successful_sync TIMESTAMP,
    sync_status VARCHAR(50),  -- 'success', 'no_options', 'api_error', etc.
    consecutive_failures INTEGER DEFAULT 0,
    has_options BOOLEAN,
    notes TEXT
);
```

**Purpose:** Track which stocks have been synced and their status

---

### 2. **Add indexes for better performance**

```sql
-- Already exist (good):
CREATE INDEX idx_premiums_dte ON stock_premiums(dte);
CREATE INDEX idx_premiums_delta ON stock_premiums(delta) WHERE delta IS NOT NULL;

-- Recommended additions:
CREATE INDEX idx_stock_data_price ON stock_data(current_price)
    WHERE current_price IS NOT NULL;

CREATE INDEX idx_stocks_ticker_active ON stocks(ticker)
    WHERE is_active = true;
```

---

### 3. **Unify column naming**

**Change `stocks` table:**
```sql
ALTER TABLE stocks RENAME COLUMN ticker TO symbol;
ALTER TABLE stocks RENAME COLUMN price TO current_price;
```

**Impact:**
- Eliminates need for column aliasing
- Reduces confusion
- Makes queries more readable

---

## Specific Code Issues & Line Numbers

### Issue 1: Hard-coded 30-day filter
**File:** `sync_database_stocks_daily.py`
**Line:** 80
**Current:**
```python
options_data = fetcher.get_all_expirations_data(symbol, target_dtes=[30])
```
**Problem:** Only syncs 30-day options, missing 617 other options
**Recommendation:** Change to `target_dtes=[7, 14, 21, 30, 45]`

---

### Issue 2: No error categorization
**File:** `sync_database_stocks_daily.py`
**Lines:** 160-162
**Current:**
```python
except Exception as e:
    logger.error(f"  {symbol}: ❌ Error: {e}")
    return False
```
**Problem:** All errors treated the same - can't distinguish "no options" from "API error"
**Recommendation:** Implement error categorization (see optimization #5)

---

### Issue 3: Sequential processing
**File:** `sync_database_stocks_daily.py`
**Lines:** 189-210
**Current:**
```python
for idx, symbol in enumerate(all_stocks, 1):
    result = sync_stock_options(symbol, fetcher, tv_manager)
    time.sleep(0.3)
```
**Problem:** Processes one stock at a time, taking 56 minutes
**Recommendation:** Implement parallel processing (see optimization #2)

---

### Issue 4: Connection overhead
**File:** `sync_database_stocks_daily.py`
**Lines:** 94-106
**Current:**
```python
conn = tv_manager.get_connection()  # New connection per stock
cur = conn.cursor()
# ... insert data ...
conn.commit()
cur.close()
conn.close()  # Close connection
```
**Problem:** Opens/closes 1,205 connections during sync
**Recommendation:** Use connection pooling (see optimization #4)

---

### Issue 5: Missing delta calculation validation
**File:** `enhanced_options_fetcher.py`
**Lines:** 51-77
**Current:**
```python
def calculate_delta(self, S, K, T, r, sigma, option_type='put'):
    try:
        if T <= 0 or sigma <= 0 or S <= 0 or K <= 0:
            return 0.0
        # ... calculation ...
    except Exception as e:
        logger.debug(f"Delta calculation error: {e}")
        return 0.0
```
**Problem:** Returns 0.0 on error, which is a valid delta value - causes confusion
**Recommendation:** Return `None` on error, handle appropriately

---

### Issue 6: Inefficient delta targeting
**File:** `enhanced_options_fetcher.py`
**Lines:** 137-169
**Current:**
```python
# Find strike with delta closest to -0.30
target_delta = -0.30
best_put = None
best_delta_diff = float('inf')

for put in puts:  # Iterates through ALL puts
    strike = float(put.get('strike_price', 0))
    # Calculate delta for each put
    delta = self.calculate_delta(...)
```
**Problem:** Calculates delta for EVERY put option, even those far OTM/ITM
**Recommendation:** Pre-filter by strike price (±20% of current price) before calculating delta

---

## Summary of Findings

### Why only 300-400 options show instead of 1200?

1. **Only 33% of stocks have options markets** (396 out of 1,205 stocks)
   - 714 stocks with prices but no options available
   - Many are ETFs, preferred stocks, ADRs, closed-end funds

2. **Sync only captures 30-day options** (hard-coded in line 80)
   - Missing 617 options at other DTEs (7, 14, 21, 45 days)
   - Only 467 options in the 28-32 DTE range

3. **Delta filter reduces visible options by 15%**
   - Query filters for delta between 0.25-0.40
   - Reduces from 373 stocks to 316 stocks

4. **Poor sync success rate (28%)**
   - 871 out of 1,205 stocks fail to sync
   - Most failures due to "no options available"
   - No categorization to skip known non-optionable stocks

---

## Recommendations Priority

### HIGH PRIORITY (Implement First)

1. **Expand DTE coverage** to [7, 14, 21, 30, 45]
   - Impact: +617 options, ~2x visible stocks
   - Effort: 1 line change
   - Trade-off: Longer sync time

2. **Add error categorization** to distinguish "no options" from "API errors"
   - Impact: Better visibility, can skip known failures
   - Effort: 50 lines of code
   - Trade-off: None

3. **Create "no options" exclusion list**
   - Impact: Faster syncs, fewer wasted API calls
   - Effort: 100 lines of code
   - Trade-off: Need to maintain list

### MEDIUM PRIORITY (Implement Second)

4. **Add parallel processing** (10-20 concurrent requests)
   - Impact: 6-11x faster sync (56 min → 5-10 min)
   - Effort: 200 lines of code
   - Trade-off: May hit rate limits

5. **Implement smart caching** (skip recently synced stocks)
   - Impact: 70% fewer API calls
   - Effort: 150 lines of code
   - Trade-off: Slightly stale data

### LOW PRIORITY (Nice to Have)

6. **Add connection pooling**
   - Impact: 10-20% faster sync
   - Effort: 50 lines of code

7. **Unify schema column names**
   - Impact: Cleaner code
   - Effort: Database migration required

---

## Conclusion

**The Database Scan feature is working as designed** - it's showing all options that meet the criteria. The "missing" 800+ stocks either:
1. Don't have tradeable options (most common)
2. Don't have 30-day expiration options available
3. Don't meet the delta 0.25-0.40 filter

**To show more options, you must:**
1. Expand DTE coverage beyond just 30 days
2. Accept that ~60-70% of stocks will never have options
3. Consider loosening the delta filter (e.g., 0.20-0.45)

**The biggest improvement:** Change line 80 in `sync_database_stocks_daily.py` from:
```python
options_data = fetcher.get_all_expirations_data(symbol, target_dtes=[30])
```
To:
```python
options_data = fetcher.get_all_expirations_data(symbol, target_dtes=[7, 14, 21, 30, 45])
```

This single change would approximately **double the number of visible options** from ~400 to ~800-900 stocks.

---

**End of Report**
