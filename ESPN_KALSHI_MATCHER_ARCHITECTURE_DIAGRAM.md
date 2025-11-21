# ESPN-Kalshi Matcher: System Architecture Analysis

## Current Architecture (BROKEN)

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Game Cards UI                               │
│  (game_cards_visual_page.py, positions_page_improved.py)           │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    ESPN Live Data Fetcher                           │
│                    (src/espn_live_data.py)                          │
│                                                                      │
│  Returns: [                                                         │
│    {                                                                │
│      'away_team': 'Buffalo Bills',   ← Full team name              │
│      'away_abbr': 'BUF',             ← ESPN abbreviation            │
│      'home_team': 'Houston Texans',                                │
│      'home_abbr': 'HOU',                                            │
│      'game_time': '2025-11-19 19:00:00'                            │
│    }                                                                │
│  ]                                                                  │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│              ESPN-Kalshi Matcher (BROKEN)                          │
│              (src/espn_kalshi_matcher.py)                          │
│                                                                      │
│  for each game:                                                     │
│    for each away_variation:      ← UP TO 10 VARIATIONS            │
│      for each home_variation:    ← UP TO 10 VARIATIONS            │
│        ┌───────────────────────────────────────────┐              │
│        │  DATABASE QUERY (in nested loop!)         │              │
│        │  SELECT * FROM kalshi_markets             │              │
│        │  WHERE title ILIKE '%team1%'              │              │
│        │    AND title ILIKE '%team2%'              │              │
│        │    AND close_time BETWEEN ...             │              │
│        │  LIMIT 1                                  │              │
│        └───────────────────────────────────────────┘              │
│                                                                      │
│  Problem: 14 games × 10 × 10 = 1,400 potential queries!           │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼ getconn() ❌
┌─────────────────────────────────────────────────────────────────────┐
│            Kalshi Database Manager (BROKEN)                         │
│            (src/kalshi_db_manager.py)                               │
│                                                                      │
│  _connection_pool.getconn()                                        │
│    ↓                                                                │
│  conn = <psycopg2.connection object>   ← Immutable object          │
│  conn._from_pool = True  ❌ ERROR!                                 │
│                                                                      │
│  AttributeError: 'psycopg2.extensions.connection'                  │
│                  object has no attribute '_from_pool'               │
│                                                                      │
│  RESULT: ALL QUERIES FAIL                                          │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼ (Never reached due to error above)
┌─────────────────────────────────────────────────────────────────────┐
│                    PostgreSQL Database                              │
│                    (magnus.kalshi_markets)                          │
│                                                                      │
│  ticker          | title                    | home_team | away_team │
│  ─────────────────────────────────────────────────────────────────  │
│  KXNFLGAME-...   | Kansas City at Denver... | Denver    | Kansas... │
│  KXNFLGAME-...   | Green Bay at New York... | New ❌    | Green...  │
│  KXNFLGAME-...   | Las Vegas at Los...      | Los ❌    | Las...    │
│                                                                      │
│  Problem: Team names truncated! "New York" → "New", "Los Angeles"→"Los"│
└─────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow Analysis

### 1. ESPN API → System

```
ESPN API Response
─────────────────
{
  "competitions": [{
    "competitors": [
      {
        "homeAway": "home",
        "team": {
          "displayName": "Houston Texans",     ← Full name
          "abbreviation": "HOU"                 ← 3-letter code
        }
      },
      {
        "homeAway": "away",
        "team": {
          "displayName": "Buffalo Bills",
          "abbreviation": "BUF"
        }
      }
    ]
  }]
}

Transformed to:
─────────────────
{
  'away_team': 'Buffalo Bills',    ← Used for matching
  'away_abbr': 'BUF',              ← Could be used, but isn't consistently
  'home_team': 'Houston Texans',
  'home_abbr': 'HOU'
}
```

### 2. Matching Process (Current - Broken)

```
Step 1: Generate Variations
────────────────────────────
ESPN Input: "Buffalo Bills"

Hardcoded Variations (src/espn_kalshi_matcher.py lines 21-54):
NFL_TEAM_VARIATIONS = {
  'Buffalo Bills': ['Buffalo', 'Bills', 'BUF']
}

Generated: ['Buffalo Bills', 'Bills', 'Buffalo', 'BUF']  ← Duplicates!


Step 2: Database Query (in nested loop)
────────────────────────────────────────
for away_var in ['Buffalo Bills', 'Bills', 'Buffalo', 'BUF']:
  for home_var in ['Houston Texans', 'Texans', 'Houston', 'HOU']:

    SQL Query:
    ──────────
    SELECT ticker, title, yes_price, no_price, volume
    FROM kalshi_markets
    WHERE title ILIKE '%Buffalo%'        ← TOO BROAD!
      AND title ILIKE '%Houston%'        ← Matches wrong games
      AND close_time BETWEEN '2025-11-16' AND '2025-11-22'  ← 6-day window!
    ORDER BY volume DESC
    LIMIT 1

    Problems:
    - "Buffalo" matches "Buffalo Bills" but also "Buffalo Sabres" (NHL)
    - No sport filtering
    - First high-volume match wins (might be wrong game)
    - 6-day window catches multiple games

    Result: FAILS due to connection pool error before query runs


Step 3: Ticker Parsing (Never reached)
───────────────────────────────────────
IF query succeeded, would try to parse:

Kalshi Ticker: "KXNFLGAME-25NOV16TBBUF-BUF"
               └─ Split by '-'
                  ['KXNFLGAME', '25NOV16TBBUF', 'BUF']
                                               └─ ticker_suffix

Logic:
if ticker_suffix == 'buf' in away_variations:
  away_is_yes = True
  away_price = yes_price
  home_price = no_price

Problem: Fragile string matching, assumes ticker convention
```

### 3. Database Structure Issues

```
Kalshi Markets Table (kalshi_markets)
──────────────────────────────────────

Expected:
┌──────────────────┬────────────────────────────┬──────────────────┬─────────────────┐
│ ticker           │ title                      │ home_team        │ away_team       │
├──────────────────┼────────────────────────────┼──────────────────┼─────────────────┤
│ KXNFLGAME-...    │ Buffalo at Houston Winner? │ Houston Texans   │ Buffalo Bills   │
│ KXNFLGAME-...    │ NY Giants at NE Winner?    │ New England      │ New York Giants │
└──────────────────┴────────────────────────────┴──────────────────┴─────────────────┘


Actual:
┌──────────────────┬────────────────────────────┬──────────────────┬─────────────────┐
│ ticker           │ title                      │ home_team        │ away_team       │
├──────────────────┼────────────────────────────┼──────────────────┼─────────────────┤
│ KXNFLGAME-...KC  │ Kansas City at Denver...   │ Denver           │ Kansas City...  │
│ KXNFLGAME-...DEN │ Kansas City at Denver...   │ Denver           │ Kansas City...  │
│ KXNFLGAME-...NYG │ Green Bay at New York G... │ New ❌           │ Green Bay...    │
│ KXNFLGAME-...GB  │ Green Bay at New York G... │ New ❌           │ Green Bay...    │
│ KXNFLGAME-...LAC │ Las Vegas at Los Angeles...│ Los ❌           │ Las Vegas...    │
└──────────────────┴────────────────────────────┴──────────────────┴─────────────────┘

Observations:
1. DUPLICATE MARKETS: Each game has TWO entries (one per team as YES option)
2. TRUNCATED NAMES: "New York" → "New", "Los Angeles" → "Los"
3. INCONSISTENT FORMAT: Some full names, some city-only
4. NULL SECTORS: sector column is empty (should be 'nfl', 'nba', etc.)

Root Cause Hypothesis:
- Likely VARCHAR(20) or VARCHAR(50) column limit
- Or bug in Kalshi data sync script
- Need to check: src/sync_kalshi_markets.py or similar
```

---

## Matching Failure Modes

### Mode 1: Connection Pool Failure (Current)

```
Request: Match "Buffalo Bills @ Houston Texans"
  ↓
Generate variations
  ↓
Execute database query
  ↓
KalshiDBManager.get_connection()
  ↓
conn = pool.getconn()  ✅ Returns psycopg2.connection
  ↓
conn._from_pool = True  ❌ AttributeError
  ↓
Exception caught, return None
  ↓
Result: kalshi_odds = None
  ↓
UI shows: "No Kalshi market found" (misleading error!)
```

**Fix**: Remove `_from_pool` attribute, use tracking dict instead

---

### Mode 2: Team Name Mismatch (If DB worked)

```
ESPN Data:
  away_team: "Buffalo Bills"
  home_team: "Houston Texans"

Query Generated:
  WHERE title ILIKE '%Buffalo Bills%' AND title ILIKE '%Houston Texans%'

Kalshi Database:
  home_team: "Houston"  (not "Houston Texans")
  away_team: "Buffalo" or "Bills" or "Buffalo Bills"? (unknown)

Match Result: FAIL (if stored as just "Houston")

Alternative Query:
  WHERE title ILIKE '%Buffalo%' AND title ILIKE '%Houston%'

Kalshi Database:
  title: "Buffalo at Houston Winner?"  ✅ Would match!

BUT also matches:
  title: "Buffalo Sabres at Houston Rockets Winner?" ❌ (NHL/NBA)
  title: "Buffalo Wings Festival in Houston" ❌ (Not even a game)

Problem: No sport filtering, no validation
```

---

### Mode 3: Date Mismatch

```
ESPN Game:
  game_time: "2025-11-19 19:00:00"  (Tuesday Night Football)

Date Window:
  start: 2025-11-16 (3 days before)
  end: 2025-11-22 (3 days after)

Kalshi Markets in Window:
  - 2025-11-17 Sunday games (Week 11)
  - 2025-11-19 Tuesday game (target) ✅
  - 2025-11-21 Thursday game (Week 12)
  - 2025-11-24 Sunday games (Week 12)

SQL Query:
  WHERE close_time BETWEEN '2025-11-16' AND '2025-11-22'
  ORDER BY volume DESC
  LIMIT 1

Result: Might match Sunday game with higher volume instead of Tuesday!

Fix Needed:
  - Tighten window to ±1 day (or ±6 hours)
  - Use expected_expiration_time instead of close_time
  - Add timezone handling
```

---

### Mode 4: Ticker Ambiguity

```
Kalshi Returns TWO Markets:
────────────────────────────

Market 1:
  ticker: "KXNFLGAME-25NOV16TBBUF-TB"
  title: "Tampa Bay at Buffalo Winner?"
  yes_price: 0.35  (Tampa Bay wins)
  no_price: 0.65   (Buffalo wins)

Market 2:
  ticker: "KXNFLGAME-25NOV16TBBUF-BUF"
  title: "Tampa Bay at Buffalo Winner?"
  yes_price: 0.65  (Buffalo wins)
  no_price: 0.35   (Tampa Bay wins)

Current Matcher:
  - ORDER BY volume DESC LIMIT 1
  - Picks whichever has higher volume
  - Assumes ticker suffix indicates YES team

Problems:
1. Volume might be similar → arbitrary pick
2. If wrong ticker picked, prices are inverted!
3. No validation that Market1.yes_price = Market2.no_price

ESPN Game:
  away_team: "Tampa Bay Buccaneers"
  home_team: "Buffalo Bills"

Matcher picks Market 1 (higher volume):
  ticker_suffix = "TB"
  "tb" in "tampa bay buccaneers"? YES
  away_is_yes = True

  Result:
    away_price = 0.35  ✅ Correct
    home_price = 0.65  ✅ Correct

BUT if matcher picked Market 2:
  ticker_suffix = "BUF"
  "buf" in "tampa bay buccaneers"? NO
  "buf" in "buffalo bills"? YES
  away_is_yes = False (WRONG! Buffalo is home, not away)

  Result:
    away_price = 0.35  ❌ Should be 0.35, but logic might assign 0.65
    home_price = 0.65  ❌ Inverted!

Fix: Use BOTH markets, cross-validate prices
```

---

## Team Name Normalization Problem

### Current State: No Centralized Mapping

```
File 1: src/nfl_team_database.py
────────────────────────────────
NFL_TEAMS = {
  'Buffalo': {
    'abbr': 'buf',
    'full_name': 'Buffalo Bills'
  }
}

File 2: src/espn_kalshi_matcher.py
───────────────────────────────────
NFL_TEAM_VARIATIONS = {
  'Buffalo Bills': ['Buffalo', 'Bills', 'BUF']
}

File 3: ESPN API
────────────────
{
  "displayName": "Buffalo Bills",
  "abbreviation": "BUF"
}

File 4: Kalshi Database
───────────────────────
home_team: "Buffalo" (sometimes)
home_team: "Bills" (sometimes?)
home_team: "Buffalo Bills" (sometimes?)

NO SINGLE SOURCE OF TRUTH!
```

### Needed: Unified Team Mapping

```yaml
# config/team_mappings.yaml

nfl:
  buffalo_bills:
    canonical_name: "Buffalo Bills"
    espn:
      display_name: "Buffalo Bills"
      abbreviation: "BUF"
      alternate_names:
        - "Buffalo"
        - "Bills"
    kalshi:
      stored_names:
        - "Buffalo"
        - "Buffalo Bills"
        - "Bills"
      ticker_suffix: "BUF"
    database:
      primary_key: "buffalo"
      search_terms:
        - "buffalo"
        - "bills"
        - "buf"

  new_york_giants:
    canonical_name: "New York Giants"
    espn:
      display_name: "New York Giants"
      abbreviation: "NYG"
      alternate_names:
        - "New York"
        - "Giants"
        - "NY Giants"
    kalshi:
      stored_names:
        - "New York Giants"
        - "New York G"
        - "NY Giants"
        - "Giants"
      ticker_suffix: "NYG"
    database:
      primary_key: "nygiants"
      search_terms:
        - "new york giants"
        - "ny giants"
        - "giants"
        - "nyg"

    CRITICAL: Must distinguish from:
      - New York Jets (NYJ)
      - San Francisco Giants (MLB)
```

---

## Performance Bottlenecks

### Current Performance Profile

```
User loads game cards page
  ↓
Fetch ESPN scoreboard (14 games)  ────────────────── 500ms (API call)
  ↓
For each game:
  ├─ Generate team variations  ───────────────────── 1ms × 14 = 14ms
  ├─ Database query (nested loop) ─────────────────── 50ms × 14 = 700ms
  │  └─ Up to 100 queries per game (connection errors)
  └─ Parse ticker ──────────────────────────────────── 1ms × 14 = 14ms

Total: 500ms + 14ms + 700ms + 14ms = 1,228ms (1.2 seconds)

BUT connection pool errors add retries:
  └─ 14 games × 3 retry attempts × 100ms = 4,200ms

ACTUAL: 5-10 seconds (observed)

With 428 games (full season):
  428 × 100 queries × 50ms = 2,140 seconds (35 minutes!)
```

### Optimized Matcher Performance

```
src/espn_kalshi_matcher_optimized.py

User loads game cards page
  ↓
Fetch all Kalshi markets (cached) ─────────────────── 200ms (first time)
  ↓                                                    0ms (cached)
Build in-memory index ─────────────────────────────── 50ms
  ↓
For each game:
  └─ O(1) dictionary lookup ──────────────────────── 0.1ms × 14 = 1.4ms

Total (first load): 200ms + 50ms + 1.4ms = 251ms
Total (cached): 0ms + 0ms + 1.4ms = 1.4ms

Speedup: 1,228ms / 1.4ms = 877x faster (cached)
         1,228ms / 251ms = 4.9x faster (first load)

With 428 games:
  First load: 200ms + 50ms + 43ms = 293ms
  Cached: 43ms

Speedup: 2,140,000ms / 293ms = 7,303x faster!
```

---

## Recommended Architecture (Fixed)

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Game Cards UI                               │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   Matching Service Layer                            │
│                   (New - To Be Created)                             │
│                                                                      │
│  def match_game(espn_game) -> MatchingResult:                      │
│    1. Normalize team names                                          │
│    2. Fetch cached markets                                          │
│    3. Perform O(1) lookup                                           │
│    4. Validate match                                                │
│    5. Return rich result with confidence score                      │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐
│ Team Normalizer │  │ Market Cache    │  │ Validation Engine   │
│                 │  │                 │  │                     │
│ normalize()     │  │ get_markets()   │  │ validate_prices()   │
│ map_to_kalshi() │  │ (cached 5min)   │  │ validate_teams()    │
│ get_variations()│  │ build_index()   │  │ validate_dates()    │
└─────────────────┘  └─────────────────┘  └─────────────────────┘
        │                       │                       │
        └───────────────────────┼───────────────────────┘
                                ▼
                ┌───────────────────────────────┐
                │ Database Layer (Fixed Pool)   │
                │                               │
                │ ✅ Wrapper class for conns    │
                │ ✅ Proper pooling             │
                │ ✅ Error handling             │
                └───────────────────────────────┘
                                │
                                ▼
                ┌───────────────────────────────┐
                │ PostgreSQL (Fixed Schema)     │
                │                               │
                │ ✅ VARCHAR(200) for teams     │
                │ ✅ Proper indexes             │
                │ ✅ sector column populated    │
                └───────────────────────────────┘
```

---

## Data Flow (Fixed Architecture)

```
Request: Match ESPN game
  ↓
┌─────────────────────────────────────────┐
│ 1. Normalize Team Names                 │
│                                          │
│ Input: "Buffalo Bills", "Houston Texans" │
│   ↓                                      │
│ TeamNormalizer.normalize()               │
│   ↓                                      │
│ Output:                                  │
│   away_canonical: "buffalo_bills"        │
│   away_kalshi_names: ["Buffalo Bills",   │
│                       "Buffalo", "BUF"]  │
│   home_canonical: "houston_texans"       │
│   home_kalshi_names: ["Houston Texans",  │
│                       "Houston", "HOU"]  │
└─────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────┐
│ 2. Fetch Markets (Cached)               │
│                                          │
│ MarketCache.get_markets('nfl')           │
│   ↓                                      │
│ Check cache (5min TTL)                   │
│   ├─ HIT: Return cached data ✅          │
│   └─ MISS: Query database once           │
│                                          │
│ Result: List[Market] (all active NFL)   │
└─────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────┐
│ 3. Build Lookup Index (O(1))            │
│                                          │
│ index = {                                │
│   "buffalo_houston": Market(...),        │
│   "houston_buffalo": Market(...),        │
│   "buf_hou": Market(...),                │
│   ...                                    │
│ }                                        │
└─────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────┐
│ 4. Match Game (O(1) Lookup)             │
│                                          │
│ lookup_keys = [                          │
│   "buffalo_bills_houston_texans",        │
│   "buf_hou",                             │
│   "buffalo_houston"                      │
│ ]                                        │
│   ↓                                      │
│ for key in lookup_keys:                  │
│   if key in index:                       │
│     market = index[key]                  │
│     break                                │
│                                          │
│ Found: Market(ticker="KXNFL...-BUF")    │
└─────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────┐
│ 5. Validate Match                        │
│                                          │
│ ValidationEngine.validate(market, game)  │
│   ├─ Check: yes_price + no_price ≈ 1.0 ✅│
│   ├─ Check: game_date within ±1 day    ✅│
│   ├─ Check: sport = 'nfl'              ✅│
│   ├─ Check: teams make sense           ✅│
│   └─ Confidence score: 0.95             │
└─────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────┐
│ 6. Return Result                         │
│                                          │
│ MatchingResult(                          │
│   success=True,                          │
│   confidence=0.95,                       │
│   kalshi_odds={                          │
│     'away_win_price': 0.35,              │
│     'home_win_price': 0.65,              │
│     'ticker': 'KXNFLGAME-...'            │
│   },                                     │
│   debug_info={...}                       │
│ )                                        │
└─────────────────────────────────────────┘
```

---

## Migration Path

### Phase 1: Emergency (Fix Connection Pool)

```
BEFORE:
conn = pool.getconn()
conn._from_pool = True  ❌

AFTER Option A (Tracking Dict):
_pool_connections = set()

def get_connection():
  conn = pool.getconn()
  _pool_connections.add(id(conn))
  return conn

def release_connection(conn):
  if id(conn) in _pool_connections:
    pool.putconn(conn)
    _pool_connections.remove(id(conn))
  else:
    conn.close()

AFTER Option B (Wrapper Class):
class PooledConnection:
  def __init__(self, conn, from_pool=True):
    self._conn = conn
    self.from_pool = from_pool

  def cursor(self):
    return self._conn.cursor()

  def commit(self):
    return self._conn.commit()

Result: Database queries work ✅
```

### Phase 2: Switch to Optimized Matcher

```
BEFORE (game_cards_visual_page.py):
from src.espn_kalshi_matcher import enrich_games_with_kalshi_odds

AFTER:
from src.espn_kalshi_matcher_optimized import enrich_games_with_kalshi_odds_optimized

games = enrich_games_with_kalshi_odds_optimized(espn_games, sport='nfl')

Result: 400x faster, cached queries ✅
```

### Phase 3: Fix Kalshi Team Names

```
BEFORE (database):
home_team: "New"  ← Truncated
home_team: "Los"  ← Truncated

AFTER:
1. Check column definition:
   ALTER TABLE kalshi_markets
   ALTER COLUMN home_team TYPE VARCHAR(200);

2. Re-sync data from Kalshi API
   python sync_kalshi_markets.py --full-refresh

3. Verify:
   SELECT DISTINCT home_team FROM kalshi_markets
   WHERE LENGTH(home_team) < 5;

Result: Full team names stored ✅
```

---

## Success Metrics

### Current (Broken)
- Match Rate: 0%
- Page Load: 10-30 seconds
- Database Queries: 428 per load
- Cache Hit Rate: 0%
- Error Rate: 100%

### After Phase 1 (Emergency Fix)
- Match Rate: 40-60% (estimated)
- Page Load: 5-10 seconds
- Database Queries: 1-14 per load
- Cache Hit Rate: 0%
- Error Rate: <5%

### After Phase 2 (Optimized Matcher)
- Match Rate: 60-80% (estimated)
- Page Load: <1 second
- Database Queries: 1 per 5 minutes (cached)
- Cache Hit Rate: 95%
- Error Rate: <2%

### After Phase 3 (Full Fix)
- Match Rate: 90-95%
- Page Load: <500ms
- Database Queries: 1 per 5 minutes
- Cache Hit Rate: 98%
- Error Rate: <1%

---

## Conclusion

The matching system has **THREE critical failures**:

1. **Broken connection pool** (code error)
2. **Truncated team names** (database schema issue)
3. **Inefficient architecture** (performance issue)

All three must be fixed for the system to work properly.

**Priority Order**:
1. Fix connection pool (30 min) → System works at all
2. Fix team names (1 hour) → Matching works
3. Switch to optimized matcher (1 hour) → Performance acceptable

**Total Time to Working System**: 2.5 hours
**Total Time to Production-Ready**: 2-3 days (including testing and validation)
