# ESPN-Kalshi Matcher: IMMEDIATE FIX GUIDE

## CRITICAL: System is 100% Broken

**Current Status**: 0% match rate, all database queries fail

**Root Causes**:
1. Database connection pool error (AttributeError)
2. Kalshi team names truncated in database
3. No caching, inefficient queries

---

## FIX 1: Database Connection Pool (CRITICAL - 30 minutes)

### Problem
```python
# src/kalshi_db_manager.py line 58
conn = KalshiDBManager._connection_pool.getconn()
conn._from_pool = True  # ❌ ERROR!

# AttributeError: 'psycopg2.extensions.connection' object has no attribute '_from_pool'
```

### Solution A: Use Connection Tracking Set (Recommended)

**File**: `src/kalshi_db_manager.py`

```python
class KalshiDBManager:
    # Class-level connection pool (shared across all instances)
    _connection_pool = None
    _pool_connections = set()  # ADD THIS

    def get_connection(self):
        """Get database connection from pool"""
        if KalshiDBManager._connection_pool:
            try:
                conn = KalshiDBManager._connection_pool.getconn()
                if conn:
                    # Track connection by ID instead of attribute
                    KalshiDBManager._pool_connections.add(id(conn))  # CHANGE THIS
                return conn
            except psycopg2.pool.PoolError as e:
                logger.error(f"Connection pool exhausted: {e}")
                conn = psycopg2.connect(**self.db_config)
                return conn
            except Exception as e:
                logger.error(f"Error getting connection from pool: {e}")
                conn = psycopg2.connect(**self.db_config)
                return conn
        else:
            conn = psycopg2.connect(**self.db_config)
            return conn

    def release_connection(self, conn):
        """Release connection back to pool"""
        if not conn:
            return

        try:
            conn_id = id(conn)
            # Check if connection came from pool
            if conn_id in KalshiDBManager._pool_connections:  # CHANGE THIS
                if not conn.closed:
                    KalshiDBManager._connection_pool.putconn(conn)
                KalshiDBManager._pool_connections.remove(conn_id)  # CHANGE THIS
            else:
                # Direct connection - just close it
                if not conn.closed:
                    conn.close()
        except Exception as e:
            logger.error(f"Error releasing connection: {e}")
            try:
                if conn and not conn.closed:
                    conn.close()
            except:
                pass
```

### Test the Fix

```bash
cd c:/Code/Legion/repos/ava
python -c "
from src.kalshi_db_manager import KalshiDBManager

db = KalshiDBManager()
conn = db.get_connection()
print('Connection obtained:', conn)

cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM kalshi_markets')
count = cur.fetchone()[0]
print(f'Kalshi markets count: {count}')

cur.close()
db.release_connection(conn)
print('Connection released successfully')
"
```

**Expected Output**:
```
Connection obtained: <connection object>
Kalshi markets count: 127
Connection released successfully
```

---

## FIX 2: Verify Team Names in Database (15 minutes)

### Check for Truncation

```bash
psql -h localhost -U postgres -d magnus -c "
SELECT
  ticker,
  home_team,
  away_team,
  LENGTH(home_team) as home_len,
  LENGTH(away_team) as away_len
FROM kalshi_markets
WHERE status = 'active'
  AND ticker LIKE 'KXNFL%'
  AND (LENGTH(home_team) < 5 OR LENGTH(away_team) < 10)
ORDER BY LENGTH(home_team)
LIMIT 20;
"
```

**Problem Indicators**:
- `home_team = "New"` (should be "New York Giants" or "New England")
- `home_team = "Los"` (should be "Los Angeles")
- `away_team` with very short length

### Check Column Definition

```bash
psql -h localhost -U postgres -d magnus -c "
SELECT
  column_name,
  data_type,
  character_maximum_length
FROM information_schema.columns
WHERE table_name = 'kalshi_markets'
  AND column_name IN ('home_team', 'away_team', 'title');
"
```

**Expected**: `VARCHAR(200)` or larger
**If Problem**: `VARCHAR(20)` or `VARCHAR(50)` → Too small!

### Fix Column Size (If Needed)

```bash
psql -h localhost -U postgres -d magnus -c "
ALTER TABLE kalshi_markets
ALTER COLUMN home_team TYPE VARCHAR(200);

ALTER TABLE kalshi_markets
ALTER COLUMN away_team TYPE VARCHAR(200);

ALTER TABLE kalshi_markets
ALTER COLUMN title TYPE VARCHAR(500);
"
```

### Re-sync Kalshi Data

```bash
# Find the sync script
python sync_kalshi_markets.py
# Or
python sync_kalshi_complete.py
```

---

## FIX 3: Switch to Optimized Matcher (30 minutes)

### Problem
Current matcher makes 100+ database queries per page load.

### Solution
Use the already-written optimized matcher.

### Files to Update

**1. game_cards_visual_page.py**

Find this line (around line 400-500):
```python
from src.espn_kalshi_matcher import enrich_games_with_kalshi_odds
```

Change to:
```python
from src.espn_kalshi_matcher_optimized import enrich_games_with_kalshi_odds_optimized as enrich_games_with_kalshi_odds
```

**2. positions_page_improved.py**

Same change:
```python
# OLD:
from src.espn_kalshi_matcher import enrich_games_with_kalshi_odds

# NEW:
from src.espn_kalshi_matcher_optimized import enrich_games_with_kalshi_odds_optimized as enrich_games_with_kalshi_odds
```

**3. Any other files importing the matcher**

Search for all imports:
```bash
cd c:/Code/Legion/repos/ava
grep -r "from src.espn_kalshi_matcher import" *.py
```

Update all occurrences.

### Test Optimized Matcher

```bash
python -c "
from src.espn_live_data import get_espn_client
from src.espn_kalshi_matcher_optimized import enrich_games_with_kalshi_odds_optimized
import time

espn = get_espn_client()
games = espn.get_scoreboard()

start = time.time()
enriched = enrich_games_with_kalshi_odds_optimized(games, sport='nfl')
elapsed = time.time() - start

matched = sum(1 for g in enriched if g.get('kalshi_odds'))
print(f'Matched: {matched}/{len(enriched)} ({matched/len(enriched)*100:.1f}%)')
print(f'Time: {elapsed:.2f}s')
"
```

**Expected Output**:
```
Matched: 8/14 (57.1%)
Time: 0.25s
```

---

## FIX 4: Add Team Name Normalization (1 hour)

### Create Normalization Helper

**File**: `src/team_normalizer.py` (NEW FILE)

```python
"""
Team Name Normalization
Handles mapping between ESPN, Kalshi, and database team names
"""

# NFL Team Mappings
NFL_NORMALIZER = {
    # Format: canonical_key -> {espn_names, kalshi_names, abbreviation}
    'buffalo_bills': {
        'espn': ['Buffalo Bills', 'Buffalo', 'BUF'],
        'kalshi': ['Buffalo Bills', 'Buffalo', 'Bills', 'BUF'],
        'abbr': 'BUF'
    },
    'kansas_city_chiefs': {
        'espn': ['Kansas City Chiefs', 'Kansas City', 'KC', 'Chiefs'],
        'kalshi': ['Kansas City Chiefs', 'Kansas City', 'KC'],
        'abbr': 'KC'
    },
    'new_york_giants': {
        'espn': ['New York Giants', 'NY Giants', 'NYG', 'Giants'],
        'kalshi': ['New York Giants', 'New York G', 'NY Giants', 'Giants', 'NYG', 'New York', 'New'],  # Include "New" for broken data
        'abbr': 'NYG'
    },
    'los_angeles_chargers': {
        'espn': ['Los Angeles Chargers', 'LA Chargers', 'LAC', 'Chargers'],
        'kalshi': ['Los Angeles Chargers', 'Los Angeles C', 'LA Chargers', 'LAC', 'Los Angeles', 'Los'],  # Include "Los" for broken data
        'abbr': 'LAC'
    },
    # TODO: Add all 32 NFL teams
}

def normalize_team_name(team_name: str, source: str = 'espn') -> str:
    """
    Normalize team name to canonical form

    Args:
        team_name: Raw team name
        source: 'espn' or 'kalshi'

    Returns:
        Canonical team key (e.g., 'buffalo_bills')
    """
    team_lower = team_name.lower().strip()

    for canonical_key, mappings in NFL_NORMALIZER.items():
        source_names = mappings.get(source, [])
        if any(team_lower == name.lower() for name in source_names):
            return canonical_key

        # Partial match as fallback
        if any(team_lower in name.lower() or name.lower() in team_lower for name in source_names):
            return canonical_key

    return None

def get_kalshi_variations(team_name: str) -> list:
    """Get all Kalshi name variations for a team"""
    canonical = normalize_team_name(team_name, 'espn')
    if canonical and canonical in NFL_NORMALIZER:
        return NFL_NORMALIZER[canonical]['kalshi']
    return [team_name]
```

### Use in Matcher

Update `src/espn_kalshi_matcher.py`:

```python
from src.team_normalizer import get_kalshi_variations

def match_game_to_kalshi(self, espn_game: Dict) -> Optional[Dict]:
    away_team = espn_game.get('away_team', '')
    home_team = espn_game.get('home_team', '')

    # Use normalizer instead of hardcoded variations
    away_variations = get_kalshi_variations(away_team)
    home_variations = get_kalshi_variations(home_team)

    # Rest of matching logic...
```

---

## VERIFICATION CHECKLIST

After applying fixes, verify:

- [ ] Database connection pool works (no AttributeError)
- [ ] Can query kalshi_markets table successfully
- [ ] Team names in database are not truncated
- [ ] Optimized matcher is being used
- [ ] Match rate is >50%
- [ ] Page load time is <2 seconds
- [ ] No errors in console/logs

### Quick Verification Command

```bash
python -c "
from src.espn_live_data import get_espn_client
from src.espn_kalshi_matcher_optimized import enrich_games_with_kalshi_odds_optimized
import time

print('Testing ESPN-Kalshi Matcher...')
print('=' * 60)

espn = get_espn_client()
games = espn.get_scoreboard()
print(f'✓ Fetched {len(games)} ESPN games')

start = time.time()
enriched = enrich_games_with_kalshi_odds_optimized(games, sport='nfl')
elapsed = time.time() - start

matched = sum(1 for g in enriched if g.get('kalshi_odds'))
match_rate = matched / len(enriched) * 100 if enriched else 0

print(f'✓ Matched {matched}/{len(enriched)} games ({match_rate:.1f}%)')
print(f'✓ Time: {elapsed:.2f}s')

if match_rate > 50 and elapsed < 2:
    print('\\n✅ ALL CHECKS PASSED!')
else:
    print('\\n⚠️  Issues detected:')
    if match_rate <= 50:
        print(f'  - Match rate too low ({match_rate:.1f}% < 50%)')
    if elapsed >= 2:
        print(f'  - Too slow ({elapsed:.2f}s >= 2s)')
"
```

---

## ROLLBACK PLAN

If fixes cause issues:

### Rollback Connection Pool Fix

```bash
git diff src/kalshi_db_manager.py
git checkout src/kalshi_db_manager.py
```

### Rollback to Old Matcher

```python
# In game_cards_visual_page.py
from src.espn_kalshi_matcher import enrich_games_with_kalshi_odds
```

### Rollback Database Schema

```bash
# Only if you changed column types
psql -h localhost -U postgres -d magnus -c "
ALTER TABLE kalshi_markets
ALTER COLUMN home_team TYPE VARCHAR(50);

ALTER TABLE kalshi_markets
ALTER COLUMN away_team TYPE VARCHAR(50);
"
```

---

## MONITORING AFTER FIX

### Add Logging

```python
# In matcher
logger.info(f"Match rate: {matched}/{total} ({match_rate:.1f}%)")
logger.info(f"Performance: {elapsed:.2f}s for {total} games")

# In connection pool
logger.info(f"Pool status: {pool.getconn.__doc__}")
```

### Track Metrics

```python
# Store match results
match_history = []

def track_match_result(result):
    match_history.append({
        'timestamp': time.time(),
        'success': result.success,
        'confidence': result.confidence
    })
```

---

## EXPECTED RESULTS AFTER ALL FIXES

| Metric | Before | After |
|--------|--------|-------|
| Match Rate | 0% | 60-85% |
| Page Load | 10-30s | <1s |
| DB Queries | 100-1400 | 1 (cached) |
| Errors | 100% | <2% |
| Cache Hit | 0% | 95%+ |

---

## NEXT STEPS AFTER IMMEDIATE FIXES

1. **Add remaining team mappings** (all 32 NFL teams, 30 NBA teams, etc.)
2. **Create validation layer** (check price sums, date ranges, etc.)
3. **Build monitoring dashboard** (track match rates over time)
4. **Add fuzzy matching** for edge cases
5. **Create admin interface** for manual overrides

---

## GETTING HELP

If fixes don't work:

1. Check logs for specific errors
2. Verify database connection manually
3. Test each component in isolation
4. Review the full code review document: `ESPN_KALSHI_MATCHER_CODE_REVIEW.md`
5. Check architecture diagram: `ESPN_KALSHI_MATCHER_ARCHITECTURE_DIAGRAM.md`

---

## TIME ESTIMATE

| Task | Time | Priority |
|------|------|----------|
| Fix connection pool | 30 min | CRITICAL |
| Verify team names | 15 min | CRITICAL |
| Switch to optimized matcher | 30 min | HIGH |
| Add team normalizer | 60 min | MEDIUM |
| **TOTAL** | **2.25 hours** | |

**Minimum to get working**: 45 minutes (connection pool + verify database)
**Recommended full fix**: 2.25 hours
