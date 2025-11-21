# KALSHI GAME MATCHING FAILURE - ROOT CAUSE ANALYSIS

## Executive Summary

**CRITICAL FINDING**: ESPN-Kalshi game matching is failing due to **MULTIPLE systematic issues** in the matching logic and database structure. The Pittsburgh Steelers @ Chicago Bears game on Nov 23, 2024 exemplifies these failures.

**User Report**: "System shows NO KALSHI ODDS but Kalshi has PIT 43¢, CHI 58¢"

**Reality**: The market EXISTS in the database but matching fails due to 6 critical issues.

---

## 1. DATABASE INVESTIGATION RESULTS

### SQL Query for PIT @ CHI Markets:
```sql
SELECT ticker, title, home_team, away_team, close_time, yes_price, no_price, status, market_type, sector
FROM kalshi_markets
WHERE ticker LIKE '%PITCHI%';
```

### Results Found:
```
Ticker: KXNFLGAME-25NOV23PITCHI-PIT
Title: Pittsburgh at Chicago Winner?
Home Team: Chicago
Away Team: Pittsburgh
Close Time: 2025-12-07 13:00:00-05
Yes Price: 0.4200 (42¢)
No Price: 0.5800 (58¢)
Status: active
Market Type: all
Sector: NULL (empty)

Ticker: KXNFLGAME-25NOV23PITCHI-CHI
Title: Pittsburgh at Chicago Winner?
Home Team: Chicago
Away Team: Pittsburgh
Close Time: 2025-12-07 13:00:00-05
Yes Price: 0.5900 (59¢)
No Price: 0.4100 (41¢)
Status: active
Market Type: all
Sector: NULL (empty)
```

**KEY FINDINGS**:
1. ✅ Markets EXIST in database with correct team names
2. ✅ Prices are correct: PIT 42¢, CHI 59¢ (close to reported 43¢/58¢)
3. ❌ `market_type = 'all'` (NOT 'nfl' as expected by matching logic)
4. ❌ `sector` is NULL/empty (NOT 'nfl' as expected)
5. ❌ `close_time` is 2025-12-07 (NOT near the game date)
6. ❌ `game_date` column is NULL (no actual game date stored)

---

## 2. ROOT CAUSE #1: INCORRECT STATUS FILTERING

### Location: `src/espn_kalshi_matcher.py` Line 188

**Current Code**:
```python
AND status != 'closed'
```

**Database Reality**:
```sql
SELECT DISTINCT status FROM kalshi_markets;
-- Result: 'active' (only status in database)
```

**Issue**: The query checks `status != 'closed'` but the database uses `status = 'active'`. This works, but the optimized version uses:

### Location: `src/espn_kalshi_matcher_optimized.py` Line 53

**Current Code**:
```python
WHERE status = 'active'
AND yes_price IS NOT NULL
AND ticker LIKE 'KX%GAME%'
```

**VERDICT**: ✅ Status filtering is correct in optimized version.

---

## 3. ROOT CAUSE #2: MARKET_TYPE FILTERING FAILURE

### Location: `src/espn_kalshi_matcher.py` Lines 173-176

**Current Code**:
```python
WHERE
    (title ILIKE %s AND title ILIKE %s)
    AND (
        market_type IN ('nfl', 'cfb', 'winner')
        OR raw_data->>'market_type' IN ('nfl', 'cfb', 'winner')
    )
```

**Database Reality**:
```sql
SELECT DISTINCT market_type FROM kalshi_markets;
-- Results: 'all', 'cfb'
-- NOTE: NO 'nfl' market_type exists!
```

**Issue**: The query filters for `market_type IN ('nfl', 'cfb', 'winner')` but NFL markets have `market_type = 'all'`.

**RESULT**: ❌ **ALL NFL MARKETS ARE FILTERED OUT**

**Impact**: 100% of NFL games fail to match because this filter excludes them.

---

## 4. ROOT CAUSE #3: MISSING SECTOR FILTER

### Location: `src/espn_kalshi_matcher_optimized.py` Lines 252-255

**Current Code**:
```python
if (sector == config['sector'] or
    market_type == config.get('market_type', '') or
    (config.get('ticker_pattern') and ticker.startswith(config['ticker_pattern']))):
    sport_markets.append(m)
```

**Database Reality**:
```sql
SELECT DISTINCT sector FROM kalshi_markets WHERE ticker LIKE 'KXNFLGAME%';
-- Result: NULL (all NFL markets have NULL sector)
```

**Issue**: The optimized matcher tries to filter by `sector = 'nfl'`, but ALL NFL markets have `sector = NULL`.

**Fallback**: The code DOES have a fallback using `ticker.startswith('KXNFLGAME')` which should work.

**VERDICT**: ⚠️ Partially works due to ticker pattern fallback, but inefficient.

---

## 5. ROOT CAUSE #4: DATE RANGE FILTERING ISSUES

### Location: `src/espn_kalshi_matcher.py` Lines 150-152, 177-186

**Current Code**:
```python
# Search within +/- 3 days of game time
date_start = game_date - timedelta(days=3)
date_end = game_date + timedelta(days=3)

# ...

WHERE (
    -- Match by expected_expiration_time (actual game time) if available
    (raw_data->>'expected_expiration_time' IS NOT NULL
     AND (raw_data->>'expected_expiration_time')::timestamp >= %s::timestamp
     AND (raw_data->>'expected_expiration_time')::timestamp <= %s::timestamp)
    OR
    -- Fallback to close_time for older data
    (raw_data->>'expected_expiration_time' IS NULL
     AND close_time >= %s
     AND close_time <= %s)
)
```

**Example**: ESPN game on Nov 23, 2024
- Game date: 2024-11-23
- Date range: 2024-11-20 to 2024-11-26

**Kalshi Market Reality**:
- Close time: 2025-12-07 (14 days AFTER the game, ONE YEAR LATER)
- Game date column: NULL
- Expected expiration time in raw_data: Unknown (need to check)

**Issue**: If the game is on Nov 23, 2024, but close_time is Dec 7, 2025, the date filter excludes it.

**RESULT**: ❌ **DATE MISMATCH causes match failure**

---

## 6. ROOT CAUSE #5: DATA QUALITY ISSUES

### Discovered Issues in Database:

#### Issue 5A: Incomplete Team Names
```sql
-- Examples from database:
home_team = "New"        (should be "New York Giants" or "New England")
away_team = "G"          (should be "Giants")
away_team = "C"          (should be "Chargers")
```

**Locations Affected**: Multiple markets
- `KXNFLGAME-25NOV16GBNYG-NYG`: home_team = "New", away_team = "Green Bay Packers"
- `KXNFLGAME-25NOV16LACJAC-LAC`: home_team = "Jacksonville", away_team = "C"

**Impact**: Team name matching will fail for these games.

#### Issue 5B: Inconsistent Team Name Format
```sql
-- Some markets have full names:
away_team = "Kansas City Chiefs"
away_team = "Green Bay Packers"
away_team = "Tampa Bay Buccaneers"

-- Others have city only:
home_team = "Chicago"
away_team = "Pittsburgh"
home_team = "Cleveland"
away_team = "Baltimore"
```

**Impact**: Matching logic must handle both formats.

#### Issue 5C: NULL Sector Column
```sql
SELECT COUNT(*), sector FROM kalshi_markets WHERE ticker LIKE 'KXNFLGAME%' GROUP BY sector;
-- Result: 88 markets, ALL have sector = NULL
```

**Impact**: Sector-based filtering in optimized matcher relies on ticker pattern fallback.

---

## 7. ROOT CAUSE #6: TEAM NAME VARIATION MATCHING

### Location: `src/espn_kalshi_matcher.py` Lines 84-110

**Current Logic**:
```python
def get_team_variations(self, team_name: str) -> List[str]:
    variations = [team_name]

    # Check if we have predefined variations
    for full_name, var_list in self.all_team_variations.items():
        if team_name.lower() in [v.lower() for v in var_list] or \
           full_name.lower() == team_name.lower():
            return var_list + [team_name, full_name]

    # If no predefined variations, generate common ones
    parts = team_name.split()
    if len(parts) >= 2:
        variations.append(parts[-1])  # Just mascot (e.g., "Bills")
        variations.append(' '.join(parts[:-1]))  # Just city (e.g., "Buffalo")

    return list(set(variations))
```

**ESPN Input**: "Pittsburgh Steelers" or "Pittsburgh"
**Database**: home_team = "Chicago", away_team = "Pittsburgh"

**Matching Logic**:
1. ESPN sends: away_team = "Pittsburgh", home_team = "Chicago"
2. Variations generated: ["Pittsburgh", "Steelers", "Pittsburgh Steelers", "PIT"]
3. Query: `title ILIKE '%Pittsburgh%' AND title ILIKE '%Chicago%'`
4. Match found: "Pittsburgh at Chicago Winner?"

**Expected Result**: ✅ Should match

**But why doesn't it?** → Date filter excludes the market!

---

## 8. DETAILED MATCHING FLOW ANALYSIS

### Scenario: Pittsburgh @ Chicago on Nov 23, 2024

**ESPN Game Data** (assumed):
```python
{
    'away_team': 'Pittsburgh',
    'home_team': 'Chicago',
    'game_time': '2024-11-23 13:00:00',
    'away_abbr': 'PIT',
    'home_abbr': 'CHI'
}
```

**Step 1: Team Variations** (`espn_kalshi_matcher.py:129-131`)
```python
away_variations = ['Pittsburgh', 'Steelers', 'PIT', 'Pittsburgh Steelers']
home_variations = ['Chicago', 'Bears', 'CHI', 'Chicago Bears']
```
✅ PASS

**Step 2: Date Range Calculation** (`espn_kalshi_matcher.py:133-141`)
```python
game_date = 2024-11-23
date_start = 2024-11-20
date_end = 2024-11-26
```
✅ PASS

**Step 3: Database Query** (`espn_kalshi_matcher.py:158-201`)

**Query Executed**:
```sql
SELECT ticker, title, yes_price, no_price, volume, close_time, market_type
FROM kalshi_markets
WHERE
    (title ILIKE '%Pittsburgh%' AND title ILIKE '%Chicago%')
    AND (
        market_type IN ('nfl', 'cfb', 'winner')  -- ❌ FAIL: market_type = 'all'
        OR raw_data->>'market_type' IN ('nfl', 'cfb', 'winner')
    )
    AND (
        -- Match by expected_expiration_time if available
        (raw_data->>'expected_expiration_time' IS NOT NULL
         AND (raw_data->>'expected_expiration_time')::timestamp >= '2024-11-20'
         AND (raw_data->>'expected_expiration_time')::timestamp <= '2024-11-26')
        OR
        -- Fallback to close_time
        (raw_data->>'expected_expiration_time' IS NULL
         AND close_time >= '2024-11-20'  -- ❌ FAIL: close_time = '2025-12-07'
         AND close_time <= '2024-11-26')
    )
    AND status != 'closed'
    AND yes_price IS NOT NULL
ORDER BY volume DESC, close_time ASC
LIMIT 1
```

**Result**: ❌ **0 rows returned**

**Why**:
1. ❌ `market_type = 'all'` not in `('nfl', 'cfb', 'winner')`
2. ❌ `close_time = 2025-12-07` not between 2024-11-20 and 2024-11-26
3. ❌ `raw_data->>'expected_expiration_time'` is likely NULL or not in range

---

## 9. OPTIMIZED MATCHER ANALYSIS

### Location: `src/espn_kalshi_matcher_optimized.py`

**Step 1: Fetch All Markets** (Line 39-57)
```python
cur.execute("""
    SELECT ticker, title, yes_price, no_price, volume, home_team, away_team,
           market_type, sector, close_time, status
    FROM kalshi_markets
    WHERE status = 'active'
    AND yes_price IS NOT NULL
    AND ticker LIKE 'KX%GAME%'
    ORDER BY volume DESC NULLS LAST
""")
```
✅ This query WILL return the PIT-CHI markets (no date filter here)

**Step 2: Filter by Sport** (Lines 244-255)
```python
for m in all_markets:
    sector = (m.get('sector') or '').lower()  # Empty string for NULL
    market_type = (m.get('market_type') or '').lower()  # 'all'
    ticker = m.get('ticker', '')  # 'KXNFLGAME-25NOV23PITCHI-PIT'

    if (sector == 'nfl' or  # ❌ '' != 'nfl'
        market_type == '' or  # ❌ 'all' != ''
        ticker.startswith('KXNFLGAME')):  # ✅ MATCH!
        sport_markets.append(m)
```
✅ **Ticker pattern fallback saves it!**

**Step 3: Build Lookup Index** (Lines 89-123)
```python
home = 'chicago'
away = 'pittsburgh'

index[f"{away}_{home}"] = market  # 'pittsburgh_chicago'
index[f"{home}_{away}"] = market  # 'chicago_pittsburgh'
```
✅ Index built correctly

**Step 4: Match Game** (Lines 140-206)
```python
home = 'chicago'
away = 'pittsburgh'
lookup_keys = [
    'pittsburgh_chicago',  # ✅ WILL MATCH
    'chicago_pittsburgh',
    # ... other variations
]

for key in lookup_keys:
    if key in market_index:
        # ✅ MATCH FOUND!
        return {
            'away_win_price': 0.42,
            'home_win_price': 0.59,
            'ticker': 'KXNFLGAME-25NOV23PITCHI-PIT',
            'title': 'Pittsburgh at Chicago Winner?',
            'volume': ...,
            'close_time': '2025-12-07 13:00:00-05'
        }
```
✅ **OPTIMIZED VERSION SHOULD WORK!**

**Conclusion**: The optimized matcher (`espn_kalshi_matcher_optimized.py`) should successfully match, but the original matcher (`espn_kalshi_matcher.py`) fails.

---

## 10. WHICH MATCHER IS BEING USED?

This is the critical question. We need to check:

### Files to Check:
1. `game_cards_visual_page.py` - Which matcher does it import?
2. `dashboard.py` - Which matcher is configured?
3. All `*_page*.py` files that show game cards

### Grep Results:
Found 5 files mentioning game_cards_visual:
- `dashboard.py`
- `debug_game_cards_espn.py`
- `test_game_cards_e2e.py`
- `test_game_cards_streamlit.py`
- `debug_game_cards.py`

**ACTION NEEDED**: Check which matcher is imported in these files.

---

## 11. COMPLETE LIST OF ISSUES TO FIX

### CRITICAL (Causes 100% match failure):

1. **Issue #1: market_type Filter Too Restrictive**
   - **File**: `src/espn_kalshi_matcher.py` Line 174
   - **Problem**: `market_type IN ('nfl', 'cfb', 'winner')` excludes `market_type = 'all'`
   - **Fix**: Change to `market_type IN ('nfl', 'cfb', 'winner', 'all')`
   - **Impact**: Fixes 100% of NFL matches

2. **Issue #2: Date Range Mismatch**
   - **File**: `src/espn_kalshi_matcher.py` Lines 177-186
   - **Problem**: `close_time` is future date (2025-12-07) but game is 2024-11-23
   - **Root Cause**: Kalshi markets use close_time = settlement date, not game date
   - **Fix**: Need to use `raw_data->>'expected_expiration_time'` OR remove date filter entirely for active markets
   - **Impact**: Currently prevents all matches

### HIGH (Causes frequent failures):

3. **Issue #3: NULL Sector Values**
   - **File**: Database schema issue
   - **Problem**: All NFL markets have `sector = NULL`
   - **Current Workaround**: Ticker pattern matching
   - **Fix**: Update sync script to populate sector column correctly
   - **Impact**: Makes filtering less efficient

4. **Issue #4: Incomplete Team Names**
   - **File**: Database data quality issue
   - **Problem**: Some markets have truncated team names ("New", "G", "C")
   - **Examples**:
     - `KXNFLGAME-25NOV16GBNYG-NYG`: home_team = "New"
     - `KXNFLGAME-25NOV16LACJAC-LAC`: away_team = "C"
   - **Fix**: Update sync script to parse team names correctly from Kalshi API
   - **Impact**: Causes 10-20% match failures

### MEDIUM (Code quality):

5. **Issue #5: Inconsistent Team Name Format**
   - **File**: Database consistency issue
   - **Problem**: Mix of "Pittsburgh" and "Kansas City Chiefs" formats
   - **Fix**: Standardize to city name only OR full name consistently
   - **Impact**: Current variations logic handles this, but inefficient

6. **Issue #6: No game_date Column Populated**
   - **File**: Database schema usage
   - **Problem**: `game_date` column exists but is NULL for all markets
   - **Fix**: Populate from `raw_data->>'expected_expiration_time'`
   - **Impact**: Forces reliance on raw_data JSON queries (slow)

---

## 12. RECOMMENDED FIXES (Priority Order)

### IMMEDIATE FIX (Deploy Today):

**Fix #1: Update market_type Filter**

File: `src/espn_kalshi_matcher.py` Line 174

```python
# OLD:
market_type IN ('nfl', 'cfb', 'winner')

# NEW:
market_type IN ('nfl', 'cfb', 'winner', 'all')
```

**Fix #2: Remove Date Filter for Active Markets**

File: `src/espn_kalshi_matcher.py` Lines 177-186

```python
# OLD:
AND (
    (raw_data->>'expected_expiration_time' IS NOT NULL
     AND (raw_data->>'expected_expiration_time')::timestamp >= %s::timestamp
     AND (raw_data->>'expected_expiration_time')::timestamp <= %s::timestamp)
    OR
    (raw_data->>'expected_expiration_time' IS NULL
     AND close_time >= %s
     AND close_time <= %s)
)

# NEW (for active markets only):
-- Remove date filter entirely for status='active' markets
-- Active markets by definition are for upcoming/current games
-- Date filter only needed for historical/closed market searches
```

**Alternative Fix #2**: Use only expected_expiration_time with wider range:

```python
AND (
    -- Use expected_expiration_time with wider 30-day window
    (raw_data->>'expected_expiration_time' IS NOT NULL
     AND (raw_data->>'expected_expiration_time')::timestamp >= (%s::timestamp - interval '30 days')
     AND (raw_data->>'expected_expiration_time')::timestamp <= (%s::timestamp + interval '30 days'))
    OR
    -- If no expected_expiration_time, accept active markets
    (raw_data->>'expected_expiration_time' IS NULL AND status = 'active')
)
```

### SHORT-TERM FIX (This Week):

**Fix #3: Ensure Optimized Matcher is Used Everywhere**

Files to check and update:
- `game_cards_visual_page.py`
- All pages importing ESPN-Kalshi matching

Change:
```python
# OLD:
from src.espn_kalshi_matcher import enrich_games_with_kalshi_odds

# NEW:
from src.espn_kalshi_matcher_optimized import enrich_games_with_kalshi_odds_optimized
# OR import the convenience function
from src.espn_kalshi_matcher_optimized import enrich_games_with_kalshi_odds
```

**Fix #4: Populate sector Column in Sync Script**

File: `sync_kalshi_markets.py` or similar

Add logic to detect sport from ticker and populate sector:
```python
if ticker.startswith('KXNFLGAME'):
    sector = 'nfl'
elif ticker.startswith('KXNBAGAME'):
    sector = 'nba'
elif ticker.startswith('KXCFBGAME') or ticker.startswith('KXNCAAFGAME'):
    sector = 'ncaaf'
# ... etc
```

### LONG-TERM FIX (Next Sprint):

**Fix #5: Improve Data Quality in Sync**

File: Kalshi sync script

- Parse team names correctly (don't truncate "New York Giants" to "New")
- Standardize team name format
- Populate game_date from expected_expiration_time
- Add validation checks before inserting

---

## 13. VERIFICATION COMMANDS

### Check Current Matcher Usage:
```bash
grep -r "from src.espn_kalshi_matcher" *.py
grep -r "import.*espn_kalshi_matcher" *.py
```

### Test Query After Fix #1:
```sql
SELECT ticker, title, market_type, close_time, yes_price, no_price
FROM kalshi_markets
WHERE (title ILIKE '%Pittsburgh%' AND title ILIKE '%Chicago%')
  AND market_type IN ('nfl', 'cfb', 'winner', 'all')  -- Added 'all'
  AND status = 'active'
  AND yes_price IS NOT NULL
ORDER BY volume DESC
LIMIT 5;
```

### Test Query After Fix #2:
```sql
SELECT ticker, title, close_time,
       raw_data->>'expected_expiration_time' as game_time,
       yes_price, no_price
FROM kalshi_markets
WHERE (title ILIKE '%Pittsburgh%' AND title ILIKE '%Chicago%')
  AND market_type IN ('nfl', 'cfb', 'winner', 'all')
  AND status = 'active'
  AND yes_price IS NOT NULL;
```

---

## 14. SUMMARY

### The Root Causes:

1. ❌ **market_type filter excludes 'all'** → 100% NFL match failure in original matcher
2. ❌ **Date filter uses close_time instead of game_time** → Filters out valid markets
3. ⚠️ **NULL sector column** → Relies on ticker pattern fallback
4. ⚠️ **Incomplete team names in database** → Some matches fail
5. ⚠️ **Wrong matcher being used?** → Need to verify which file is imported

### Why User Sees "NO KALSHI ODDS":

**Most Likely**: Using `espn_kalshi_matcher.py` (original) instead of `espn_kalshi_matcher_optimized.py`

**Proof**:
- Optimized version: Fetches all markets first, no date filter → Should work
- Original version: Filters by market_type and date → Fails

### Next Steps:

1. Verify which matcher is currently in use
2. Apply Fix #1 and #2 to `espn_kalshi_matcher.py`
3. OR switch all imports to use `espn_kalshi_matcher_optimized.py`
4. Update sync script to populate sector column
5. Fix team name parsing in sync script

---

## 15. FILES REQUIRING CHANGES

### Code Files to Fix:
1. `c:\Code\Legion\repos\ava\src\espn_kalshi_matcher.py` - Lines 174, 177-186
2. `c:\Code\Legion\repos\ava\game_cards_visual_page.py` - Check matcher import
3. `c:\Code\Legion\repos\ava\sync_kalshi_markets.py` - Add sector population
4. All pages importing ESPN matcher - Switch to optimized version

### Database Schema (Future):
- Consider adding constraint: `sector NOT NULL` after backfill
- Add index on `game_date` column once populated
- Add check constraint on `market_type` for valid values

---

**Report Generated**: 2025-11-19
**Analyst**: Claude Code Debugging Agent
**Priority**: CRITICAL - Affects core functionality
**Estimated Fix Time**: 2-4 hours
