# KALSHI MATCHING FIX - QUICK REFERENCE

**Problem**: Games not matching to Kalshi markets despite markets existing
**Example**: Pittsburgh @ Chicago showing "NO KALSHI ODDS" but market exists with PIT 42¢, CHI 59¢

---

## Root Cause (Simple Version)

The old matcher has 2 bugs:
1. Filters for `market_type = 'nfl'` but database has `market_type = 'all'`
2. Uses `close_time` (settlement date) instead of `expected_expiration_time` (game date)

---

## The Fix (3 Options)

### Option 1: Use Optimized Matcher (RECOMMENDED)

**Already works! Just need to use it everywhere.**

Change this:
```python
from src.espn_kalshi_matcher import enrich_games_with_kalshi_odds
```

To this:
```python
from src.espn_kalshi_matcher_optimized import enrich_games_with_kalshi_odds_optimized as enrich_games_with_kalshi_odds
```

**Files to update**:
- `ava_betting_recommendations_page.py` (line 17)
- `game_watchlist_monitor.py` (line 35)
- `src/ava/core/tools.py` (line 353)

---

### Option 2: Quick Patch to Old Matcher

**File**: `src/espn_kalshi_matcher.py`

**Line 174** - Add 'all' to list:
```python
market_type IN ('nfl', 'cfb', 'winner', 'all')  # Added 'all'
```

**Line 175** - Same for raw_data fallback:
```python
OR raw_data->>'market_type' IN ('nfl', 'cfb', 'winner', 'all')  # Added 'all'
```

---

### Option 3: Fix Database (Long-term)

Update sync script to populate `market_type` column correctly:

```python
# In sync_kalshi_markets.py or similar
if raw_data and 'market_type' in raw_data:
    market_type = raw_data['market_type']  # Use raw_data value
else:
    # Fallback: detect from ticker
    if ticker.startswith('KXNFLGAME'):
        market_type = 'nfl'
    elif ticker.startswith('KXNBAGAME'):
        market_type = 'nba'
    # ... etc
```

---

## Verification

### Test Query:
```sql
-- This query should return 2 rows after fix
SELECT ticker, title, yes_price, no_price
FROM kalshi_markets
WHERE title ILIKE '%Pittsburgh%' AND title ILIKE '%Chicago%'
  AND market_type IN ('nfl', 'cfb', 'winner', 'all')  -- Added 'all'
  AND status = 'active';
```

Expected:
```
KXNFLGAME-25NOV23PITCHI-PIT | Pittsburgh at Chicago Winner? | 0.4200 | 0.5800
KXNFLGAME-25NOV23PITCHI-CHI | Pittsburgh at Chicago Winner? | 0.5900 | 0.4100
```

### Test in Python:
```python
from src.espn_kalshi_matcher_optimized import enrich_games_with_kalshi_odds_optimized

test_game = [{
    'away_team': 'Pittsburgh',
    'home_team': 'Chicago',
    'away_abbr': 'PIT',
    'home_abbr': 'CHI'
}]

result = enrich_games_with_kalshi_odds_optimized(test_game, sport='nfl')
print(result[0].get('kalshi_odds'))
```

Expected output:
```python
{
    'away_win_price': 0.42,
    'home_win_price': 0.59,
    'ticker': 'KXNFLGAME-25NOV23PITCHI-PIT',
    'title': 'Pittsburgh at Chicago Winner?',
    'volume': ...,
    'close_time': ...
}
```

---

## Quick Diagnosis

**If you see "NO KALSHI ODDS"**:

1. Check which page/feature you're using
2. Check which matcher that page imports:
   ```bash
   grep "espn_kalshi_matcher" your_page.py
   ```
3. If it imports `espn_kalshi_matcher` → use Option 1 or 2
4. If it imports `espn_kalshi_matcher_optimized` → different issue (report to dev)

---

## Files Reference

**Main matcher files**:
- `c:\Code\Legion\repos\ava\src\espn_kalshi_matcher.py` (OLD - has bugs)
- `c:\Code\Legion\repos\ava\src\espn_kalshi_matcher_optimized.py` (NEW - works)

**Pages using OLD matcher** (need to update):
- `c:\Code\Legion\repos\ava\ava_betting_recommendations_page.py`
- `c:\Code\Legion\repos\ava\game_watchlist_monitor.py`
- `c:\Code\Legion\repos\ava\src\ava\core\tools.py`

**Pages using NEW matcher** (already fixed):
- `c:\Code\Legion\repos\ava\game_cards_visual_page.py` ✅

---

## Time Estimate

- **Option 1** (migrate to optimized): 1-2 hours
- **Option 2** (patch old matcher): 30 minutes
- **Option 3** (fix database): 2-4 hours

**Recommended**: Do Option 1 now (fast), then Option 3 later (thorough).

---

## Complete Details

See these files for full analysis:
- `KALSHI_MATCHING_DEBUG_REPORT.md` - Complete technical analysis
- `KALSHI_MATCHING_FAILURE_EXECUTIVE_SUMMARY.md` - Executive summary

---

**Report Date**: 2025-11-19
**Status**: Root cause identified, fixes documented, ready to implement
