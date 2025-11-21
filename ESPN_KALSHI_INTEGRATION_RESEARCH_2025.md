# ESPN NFL & Kalshi Betting Integration - Research Report 2025

**Date:** November 15, 2025
**Purpose:** Comprehensive GitHub research for integrating ESPN NFL live scores and Kalshi betting odds into Streamlit dashboard

---

## Executive Summary

This research identifies best practices, libraries, and implementation patterns for integrating ESPN's unofficial API and Kalshi's prediction markets API into a real-time sports betting dashboard. The report covers authentication, rate limiting, data synchronization, caching strategies, and Streamlit-specific patterns.

**Key Findings:**
- ESPN's API is unofficial but reliable (15-60 second updates recommended)
- Kalshi tokens expire every 30 minutes (requires proactive refresh)
- Streamlit auto-refresh via `streamlit-autorefresh` or fragments
- PostgreSQL + Redis caching essential for performance
- File-based caching recommended for ESPN data

---

## 1. ESPN NFL API Integration

### 1.1 Primary Libraries & Resources

#### **Best Option: Direct ESPN API Calls**
- **Endpoint:** `https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard`
- **Status:** Unofficial/undocumented (no authentication required)
- **Update Frequency:** Live games update ~15 seconds on NFL.com feed, ESPN lags slightly
- **Recommended Poll Interval:** 30-60 seconds during live games

**GitHub Resources:**
1. **ESPN API Endpoint List** (Most Comprehensive)
   - URL: https://gist.github.com/nntrn/ee26cb2a0716de0947a0a4e9a157bc1c
   - Complete NFL endpoint reference with parameters

2. **ESPN Hidden API Documentation**
   - URL: https://gist.github.com/akeaswaran/b48b02f1c94f873c6655e7129910fc3b
   - Request patterns, response structures, best practices

3. **espn_scraper Package** (Recommended for Caching)
   - URL: https://github.com/andr3w321/espn_scraper
   - PyPI: `pip install espn-scraper`
   - Built-in file-based caching mechanism
   - Supports NFL, NCAA, NBA, MLB, NHL

#### **Alternative: espn-api Package** (Fantasy Football Only)
- **GitHub:** https://github.com/cwendt94/espn-api
- **PyPI:** `pip install espn_api`
- **Limitation:** Designed for Fantasy Football leagues, not live scores
- **Not Recommended** for your use case

### 1.2 ESPN API Structure

#### **Scoreboard Endpoint**
```python
# Base URL structure
https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard

# Parameters
?dates=YYYYMMDD          # Specific date
?dates=YYYY              # Full year
?seasontype=2&week=1     # Regular season, week 1
?limit=300               # Results limit
```

#### **Response Structure**
```json
{
  "events": [
    {
      "id": "401547404",
      "name": "Kansas City Chiefs at Buffalo Bills",
      "status": {
        "type": {
          "name": "STATUS_IN_PROGRESS",
          "completed": false,
          "shortDetail": "2nd Quarter"
        },
        "displayClock": "7:42",
        "period": 2
      },
      "competitions": [
        {
          "competitors": [
            {
              "homeAway": "home",
              "team": {
                "displayName": "Buffalo Bills",
                "abbreviation": "BUF",
                "logo": "https://...",
                "color": "00338D"
              },
              "score": "21"
            }
          ]
        }
      ]
    }
  ]
}
```

#### **Status Values**
- `STATUS_SCHEDULED` - Game not started
- `STATUS_IN_PROGRESS` - Game live
- `STATUS_HALFTIME` - Halftime
- `STATUS_END_PERIOD` - End of quarter
- `STATUS_FINAL` - Game completed

### 1.3 Implementation Pattern (Based on Your Code)

**Current Implementation Review:**
Your `src/espn_ncaa_live_data.py` is well-structured. Apply same pattern for NFL:

```python
# Create src/espn_nfl_live_data.py
class ESPNNFLLiveData:
    BASE_URL = "https://site.api.espn.com/apis/site/v2/sports/football/nfl"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        })

    def get_scoreboard(self, week: Optional[int] = None) -> List[Dict]:
        """Get current NFL scoreboard"""
        url = f"{self.BASE_URL}/scoreboard"
        params = {}
        if week:
            params['seasontype'] = 2  # Regular season
            params['week'] = week

        response = self.session.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        games = [self._parse_game(event) for event in data.get('events', [])]
        return [g for g in games if g]  # Filter None

    def _parse_game(self, event: Dict) -> Optional[Dict]:
        """Parse ESPN event into simplified format"""
        # Extract teams, scores, status
        # Return normalized dict matching NCAA pattern
```

### 1.4 Caching Strategy (Critical)

**Recommended: espn_scraper Pattern**
```python
import espn_scraper as espn

# Cache directory
CACHE_DIR = "cached_data/nfl"

# First call downloads and caches
data = espn.get_url(
    "https://www.espn.com/nfl/boxscore?gameId=401131040&_xhr=1",
    CACHE_DIR
)

# Subsequent calls use cache
data = espn.get_url(url, CACHE_DIR)  # Instant
```

**Your Implementation:**
```python
# In config/default.yaml
espn:
  cache_ttl: 60  # 60 seconds for live games
  cache_ttl_completed: 3600  # 1 hour for completed games

# Use Redis + File caching
@st.cache_data(ttl=60)
def get_live_nfl_scores():
    client = get_espn_nfl_client()
    return client.get_scoreboard()
```

### 1.5 Rate Limiting & Best Practices

**From Research:**
1. **No Official Rate Limits** - But be respectful
2. **Recommended:** 30-60 second polling for live games
3. **Avoid:** Polling completed games (cache indefinitely)
4. **Pattern:** Check game status, adjust polling based on `is_live`

```python
def get_optimal_refresh_interval(games: List[Dict]) -> int:
    """Dynamic refresh based on game status"""
    live_games = [g for g in games if g['is_live']]

    if live_games:
        return 30  # 30 seconds for live games

    scheduled_games = [g for g in games if g['status'] == 'STATUS_SCHEDULED']
    if scheduled_games:
        return 300  # 5 minutes for scheduled

    return 600  # 10 minutes if all completed
```

### 1.6 Known Issues & Solutions

**Issue 1: API Can Change Without Notice**
- **Solution:** Middleware pattern - wrap API calls, easy to swap data sources
- **Your Code:** Already using client classes (good!)

**Issue 2: Lag vs Live TV**
- **Solution:** Set user expectations ("Updates every 30s")
- **Note:** ESPN lags ~15-30 seconds behind live broadcasts

**Issue 3: College Football Returns Top 25 Only**
- **Solution:** Use `groups` parameter for FBS/FCS
- **Your Code:** Already implemented in NCAA client!

---

## 2. Kalshi API Integration

### 2.1 Primary Resources

#### **Official Kalshi Resources**
1. **Official Starter Code** (Recommended)
   - GitHub: https://github.com/Kalshi/kalshi-starter-code-python
   - Pure Python examples, no SDK
   - Includes rate limiting

2. **Official Docs**
   - URL: https://docs.kalshi.com/
   - Rate limits: https://docs.kalshi.com/getting_started/rate_limits

3. **Community Client** (Feature-Rich)
   - GitHub: https://github.com/AndrewNolte/KalshiPythonClient
   - PyPI: Auto-generated from OpenAPI spec
   - Full API coverage

#### **Unofficial Libraries**
1. **humz2k/kalshi-python-unofficial**
   - Lightweight wrapper
   - Full coverage as of Jan 2025

2. **kalshi-python (PyPI)**
   - Official package
   - `pip install kalshi-python`

### 2.2 Authentication (Critical Fix for Your Code)

**Token Lifecycle:**
- Tokens expire in **30 minutes**
- Must refresh before expiration
- Use proactive refresh (25 min mark)

**Your Current Implementation Review:**
`src/kalshi_client.py` - Lines 35-42 ✅ GOOD!
```python
def _needs_token_refresh(self) -> bool:
    if not self.bearer_token or not self.token_expires_at:
        return True
    # Refresh 5 minutes before expiration ✅
    return datetime.now() >= (self.token_expires_at - timedelta(minutes=5))
```

**Recommended Enhancement:**
```python
# Add to KalshiClient
def _make_request(self, method: str, endpoint: str, **kwargs):
    """Wrapper for all API calls with auto-refresh"""
    if self._needs_token_refresh():
        if not self.login():
            raise Exception("Failed to refresh Kalshi token")

    url = f"{self.BASE_URL}{endpoint}"
    headers = kwargs.pop('headers', {})
    headers['Authorization'] = self.bearer_token

    response = requests.request(method, url, headers=headers, **kwargs)

    # Handle rate limiting
    if response.status_code == 429:
        retry_after = int(response.headers.get('Retry-After', 60))
        time.sleep(retry_after)
        return self._make_request(method, endpoint, **kwargs)

    response.raise_for_status()
    return response.json()
```

### 2.3 Rate Limiting Strategy

**Official Kalshi Limits:**
- Tiered by subscription level
- Specific endpoints have additional limits
- 429 status code when exceeded

**Best Practices (from Research):**
1. **Exponential Backoff**
   ```python
   def exponential_backoff(attempt: int, base_delay: float = 1.0):
       return min(base_delay * (2 ** attempt), 60)  # Max 60s
   ```

2. **Request Queuing**
   ```python
   from queue import Queue
   from threading import Thread, Lock

   class RateLimitedKalshiClient(KalshiClient):
       def __init__(self, *args, **kwargs):
           super().__init__(*args, **kwargs)
           self.request_queue = Queue()
           self.rate_limit = 100  # requests per minute
           self.lock = Lock()
   ```

3. **Data Caching** (Most Important)
   ```python
   # Cache market definitions (change rarely)
   @st.cache_data(ttl=3600)  # 1 hour
   def get_all_markets():
       return client.get_all_markets()

   # Cache orderbook (live prices)
   @st.cache_data(ttl=30)  # 30 seconds
   def get_market_orderbook(ticker):
       return client.get_market_orderbook(ticker)
   ```

### 2.4 NFL Markets Discovery

**Your Current Code:** `filter_football_markets()` - Lines 143-183
**Issue:** Keyword matching not comprehensive

**Recommended Enhancement:**
```python
def get_nfl_markets(self) -> List[Dict]:
    """Get NFL-specific markets using series/event filters"""
    # Use event_ticker or series_ticker filters
    params = {
        'event_ticker': 'NFL',  # If Kalshi uses this
        'status': 'open'
    }

    # Or filter by category
    all_markets = self.get_all_markets(status='open')

    nfl_markets = []
    for market in all_markets:
        # Check category field
        category = market.get('category', '').lower()
        if 'sports' in category or 'football' in category:
            # Further filter for NFL
            ticker = market.get('ticker', '').upper()
            if any(team in ticker for team in NFL_TEAM_CODES):
                nfl_markets.append(market)

    return nfl_markets

# NFL team codes for filtering
NFL_TEAM_CODES = [
    'KC', 'BUF', 'CIN', 'BAL', 'MIA', 'JAX', 'TEN', 'HOU', 'IND', 'CLE',
    'PHI', 'DAL', 'NYG', 'WAS', 'SF', 'SEA', 'LAR', 'ARI', 'GB', 'MIN',
    'DET', 'CHI', 'TB', 'NO', 'CAR', 'ATL', 'LV', 'LAC', 'DEN', 'NE', 'NYJ'
]
```

### 2.5 WebSocket API (Advanced)

**For Real-Time Price Updates:**
```python
# From Kalshi docs
import websocket

def on_message(ws, message):
    data = json.loads(message)
    # Update prices in real-time
    st.session_state.orderbook = data

ws = websocket.WebSocketApp(
    "wss://trading-api.kalshi.com/trade-api/ws/v2",
    on_message=on_message,
    header={"Authorization": bearer_token}
)
```

**Recommendation:** Start with REST polling (30s), upgrade to WebSocket if needed

---

## 3. Streamlit Real-Time Dashboard Patterns

### 3.1 Auto-Refresh Solutions

#### **Option 1: streamlit-autorefresh (Recommended)**
```bash
pip install streamlit-autorefresh
```

```python
from streamlit_autorefresh import st_autorefresh

# Auto-refresh every 30 seconds
count = st_autorefresh(interval=30000, key="sports_refresh")

# Use count to track refreshes
if count > 0:
    st.caption(f"Auto-refreshed {count} times")

# Your data fetching
games = get_live_nfl_scores()
kalshi_markets = get_nfl_markets()
```

#### **Option 2: Streamlit Fragments (Modern, Built-in)**
```python
# Requires Streamlit >= 1.31
@st.fragment(run_every="30s")
def live_scoreboard():
    """This fragment auto-refreshes every 30s"""
    games = get_live_nfl_scores()

    for game in games:
        if game['is_live']:
            st.metric(
                label=f"{game['away_team']} @ {game['home_team']}",
                value=f"{game['away_score']} - {game['home_score']}",
                delta=game['status_detail']
            )

# Call the fragment
live_scoreboard()

# Rest of page doesn't refresh
st.header("Other Content")
```

#### **Option 3: Manual Refresh Button**
```python
col1, col2 = st.columns([3, 1])
with col1:
    st.header("Live Scores")
with col2:
    if st.button("🔄 Refresh", key="manual_refresh"):
        st.rerun()
```

### 3.2 State Management for Live Data

```python
# Initialize session state
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = datetime.now()
    st.session_state.games_cache = []

# Check if refresh needed
def should_refresh():
    elapsed = (datetime.now() - st.session_state.last_refresh).seconds
    return elapsed > 30  # 30 seconds

if should_refresh():
    st.session_state.games_cache = get_live_nfl_scores()
    st.session_state.last_refresh = datetime.now()

# Use cached data
games = st.session_state.games_cache
```

### 3.3 Performance Optimization

**Problem:** Fetching ESPN + Kalshi data is slow
**Solution:** Parallel fetching

```python
from concurrent.futures import ThreadPoolExecutor

def fetch_all_data():
    """Fetch ESPN and Kalshi data in parallel"""
    with ThreadPoolExecutor(max_workers=2) as executor:
        espn_future = executor.submit(get_live_nfl_scores)
        kalshi_future = executor.submit(get_nfl_markets)

        espn_data = espn_future.result()
        kalshi_data = kalshi_future.result()

    return espn_data, kalshi_data

# Cache the combined fetch
@st.cache_data(ttl=30)
def get_dashboard_data():
    return fetch_all_data()
```

### 3.4 Loading States

```python
# Show spinner during fetch
with st.spinner("Loading live scores..."):
    games = get_live_nfl_scores()

# Or use progress indicator
progress = st.progress(0)
status = st.empty()

status.text("Fetching ESPN scores...")
progress.progress(33)
espn_data = get_live_nfl_scores()

status.text("Fetching Kalshi markets...")
progress.progress(66)
kalshi_data = get_nfl_markets()

status.text("Rendering dashboard...")
progress.progress(100)

# Clear progress
progress.empty()
status.empty()
```

---

## 4. Database Schema Design

### 4.1 ESPN Scores Table

**Recommended Schema:**
```sql
-- Create table for NFL scores
CREATE TABLE nfl_live_scores (
    game_id VARCHAR(50) PRIMARY KEY,
    game_date TIMESTAMP NOT NULL,
    home_team VARCHAR(100) NOT NULL,
    home_abbr VARCHAR(10),
    home_score INTEGER DEFAULT 0,
    home_logo TEXT,
    away_team VARCHAR(100) NOT NULL,
    away_abbr VARCHAR(10),
    away_score INTEGER DEFAULT 0,
    away_logo TEXT,
    status VARCHAR(50) NOT NULL,  -- STATUS_IN_PROGRESS, STATUS_FINAL, etc.
    status_detail VARCHAR(200),
    is_live BOOLEAN DEFAULT FALSE,
    is_completed BOOLEAN DEFAULT FALSE,
    clock VARCHAR(20),
    period INTEGER,
    venue VARCHAR(200),
    tv_network VARCHAR(50),
    last_updated TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_nfl_scores_status ON nfl_live_scores(status);
CREATE INDEX idx_nfl_scores_is_live ON nfl_live_scores(is_live);
CREATE INDEX idx_nfl_scores_game_date ON nfl_live_scores(game_date);
CREATE INDEX idx_nfl_scores_updated ON nfl_live_scores(last_updated);
```

### 4.2 Kalshi Markets Table

**Recommended Schema:**
```sql
CREATE TABLE kalshi_nfl_markets (
    ticker VARCHAR(100) PRIMARY KEY,
    title TEXT NOT NULL,
    subtitle TEXT,
    series_ticker VARCHAR(100),
    event_ticker VARCHAR(100),
    market_type VARCHAR(50),  -- win, spread, total, etc.
    yes_price INTEGER,  -- In cents
    no_price INTEGER,
    volume BIGINT DEFAULT 0,
    open_interest BIGINT DEFAULT 0,
    status VARCHAR(50),  -- open, closed, settled
    close_time TIMESTAMP,
    expiration_time TIMESTAMP,
    -- Link to NFL game
    game_id VARCHAR(50) REFERENCES nfl_live_scores(game_id),
    home_team VARCHAR(100),
    away_team VARCHAR(100),
    -- Metadata
    last_updated TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_kalshi_status ON kalshi_nfl_markets(status);
CREATE INDEX idx_kalshi_game_id ON kalshi_nfl_markets(game_id);
CREATE INDEX idx_kalshi_close_time ON kalshi_nfl_markets(close_time);
```

### 4.3 Real-Time Sync Strategy

**Background Sync Service:**
```python
# Create src/nfl_realtime_sync.py
import schedule
import time
from src.espn_nfl_live_data import get_espn_nfl_client
from src.kalshi_client import KalshiClient
from src.nfl_db_manager import NFLDBManager

def sync_live_scores():
    """Sync ESPN scores to database"""
    espn = get_espn_nfl_client()
    db = NFLDBManager()

    games = espn.get_scoreboard()

    for game in games:
        db.upsert_game(game)

    print(f"Synced {len(games)} NFL games")

def sync_kalshi_markets():
    """Sync Kalshi markets to database"""
    kalshi = KalshiClient()
    db = NFLDBManager()

    markets = kalshi.get_nfl_markets()

    for market in markets:
        db.upsert_market(market)

    print(f"Synced {len(markets)} Kalshi markets")

# Schedule tasks
schedule.every(30).seconds.do(sync_live_scores)  # Every 30s for live games
schedule.every(60).seconds.do(sync_kalshi_markets)  # Every 60s for markets

if __name__ == "__main__":
    print("Starting NFL real-time sync service...")
    while True:
        schedule.run_pending()
        time.sleep(1)
```

**Run as Background Service:**
```bash
# Windows
start_nfl_sync.bat

# Linux/Mac
python src/nfl_realtime_sync.py &
```

---

## 5. Matching ESPN Games with Kalshi Markets

### 5.1 Team Name Normalization

**Problem:** ESPN uses "Kansas City Chiefs", Kalshi might use "KC" or "Chiefs"

**Solution: Team Mapping Table**
```python
NFL_TEAM_MAPPING = {
    # ESPN full name -> Kalshi abbreviations
    'Kansas City Chiefs': ['KC', 'CHIEFS', 'KAN'],
    'Buffalo Bills': ['BUF', 'BILLS'],
    'Baltimore Ravens': ['BAL', 'RAVENS'],
    'San Francisco 49ers': ['SF', '49ERS', 'SAN FRANCISCO'],
    # ... all 32 teams
}

def normalize_team_name(team_name: str) -> List[str]:
    """Get all possible variations of team name"""
    team_name = team_name.strip()

    # Check exact match
    if team_name in NFL_TEAM_MAPPING:
        return NFL_TEAM_MAPPING[team_name]

    # Check partial match
    for full_name, variations in NFL_TEAM_MAPPING.items():
        if team_name in full_name or full_name in team_name:
            return variations

    return [team_name]
```

### 5.2 Market Matching Algorithm

```python
def match_markets_to_games(
    games: List[Dict],
    markets: List[Dict]
) -> Dict[str, List[Dict]]:
    """
    Match Kalshi markets to ESPN games

    Returns:
        {game_id: [market1, market2, ...]}
    """
    matches = {}

    for game in games:
        game_id = game['game_id']
        home_team = game['home_team']
        away_team = game['away_team']
        game_date = game['game_date']

        # Get team variations
        home_variations = normalize_team_name(home_team)
        away_variations = normalize_team_name(away_team)

        # Find matching markets
        game_markets = []
        for market in markets:
            title = market.get('title', '').upper()
            ticker = market.get('ticker', '').upper()

            # Check if both teams mentioned
            home_found = any(var.upper() in title or var.upper() in ticker
                           for var in home_variations)
            away_found = any(var.upper() in title or var.upper() in ticker
                           for var in away_variations)

            if home_found and away_found:
                # Verify date proximity (within 1 day)
                market_time = market.get('close_time')
                if market_time and game_date:
                    time_diff = abs((market_time - game_date).days)
                    if time_diff <= 1:
                        game_markets.append(market)

        matches[game_id] = game_markets

    return matches
```

### 5.3 Combined Dashboard Data

```python
def get_combined_game_data() -> List[Dict]:
    """Get games with matched Kalshi markets"""
    # Fetch data
    espn = get_espn_nfl_client()
    kalshi = KalshiClient()

    games = espn.get_scoreboard()
    markets = kalshi.get_nfl_markets()

    # Match markets to games
    matches = match_markets_to_games(games, markets)

    # Combine data
    combined = []
    for game in games:
        game_id = game['game_id']
        game_markets = matches.get(game_id, [])

        combined.append({
            **game,
            'markets': game_markets,
            'market_count': len(game_markets)
        })

    return combined
```

---

## 6. Implementation Checklist

### 6.1 Phase 1: ESPN Integration (1-2 days)

- [ ] Create `src/espn_nfl_live_data.py` (mirror NCAA structure)
- [ ] Add NFL scoreboard endpoint
- [ ] Implement `_parse_game()` method
- [ ] Add status filtering (live, scheduled, completed)
- [ ] Test with current week games
- [ ] Add file-based caching (espn_scraper pattern)
- [ ] Create `nfl_live_scores` database table
- [ ] Build database manager class

### 6.2 Phase 2: Kalshi Enhancements (1-2 days)

- [ ] Fix token refresh in `src/kalshi_client.py`
- [ ] Add `_make_request()` wrapper with auto-refresh
- [ ] Implement exponential backoff for rate limits
- [ ] Enhance NFL market filtering (use team codes)
- [ ] Add orderbook fetching for live prices
- [ ] Create `kalshi_nfl_markets` database table
- [ ] Test authentication flow

### 6.3 Phase 3: Real-Time Sync (1 day)

- [ ] Create `src/nfl_realtime_sync.py`
- [ ] Implement sync_live_scores() (30s interval)
- [ ] Implement sync_kalshi_markets() (60s interval)
- [ ] Add schedule library for intervals
- [ ] Create Windows batch script `start_nfl_sync.bat`
- [ ] Test background service
- [ ] Add logging and error handling

### 6.4 Phase 4: Market Matching (1 day)

- [ ] Build NFL team mapping dictionary
- [ ] Create `normalize_team_name()` function
- [ ] Implement `match_markets_to_games()` algorithm
- [ ] Test matching accuracy with live data
- [ ] Add match confidence scores
- [ ] Store matches in database

### 6.5 Phase 5: Streamlit Dashboard (2-3 days)

- [ ] Install `streamlit-autorefresh`
- [ ] Create `nfl_live_dashboard_page.py`
- [ ] Add auto-refresh (30s for live, 5min for scheduled)
- [ ] Display live scores with status indicators
- [ ] Show matched Kalshi markets per game
- [ ] Add manual refresh button
- [ ] Implement loading states
- [ ] Add filters (live only, by team, etc.)
- [ ] Create visualizations (score charts, odds movement)
- [ ] Add navigation to main dashboard

### 6.6 Phase 6: Performance Optimization (1 day)

- [ ] Add Redis caching for live data
- [ ] Implement parallel fetching (ESPN + Kalshi)
- [ ] Optimize database queries (indexes)
- [ ] Add @st.cache_data decorators
- [ ] Test with multiple concurrent users
- [ ] Monitor API call frequency

---

## 7. Code Examples for Your Codebase

### 7.1 Create ESPN NFL Client

**File:** `src/espn_nfl_live_data.py`
```python
"""
ESPN NFL Live Game Data Integration
Mirrors the NCAA implementation with NFL-specific features
"""
import requests
from typing import Dict, Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ESPNNFLLiveData:
    """Fetch live NFL game data from ESPN"""

    BASE_URL = "https://site.api.espn.com/apis/site/v2/sports/football/nfl"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def get_scoreboard(self, week: Optional[int] = None) -> List[Dict]:
        """Get current NFL scoreboard"""
        try:
            url = f"{self.BASE_URL}/scoreboard"
            params = {}

            if week:
                params['seasontype'] = 2  # Regular season
                params['week'] = week

            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            games = []

            for event in data.get('events', []):
                game = self._parse_game(event)
                if game:
                    games.append(game)

            logger.info(f"Fetched {len(games)} NFL games")
            return games

        except requests.RequestException as e:
            logger.error(f"Error fetching NFL scoreboard: {e}")
            return []

    def _parse_game(self, event: Dict) -> Optional[Dict]:
        """Parse ESPN event - same structure as NCAA"""
        # Use exact same logic as NCAA parser
        # ESPN uses consistent format across sports
        pass  # Implementation same as NCAA

    def get_live_games(self) -> List[Dict]:
        """Get only live games"""
        all_games = self.get_scoreboard()
        return [g for g in all_games if g.get('is_live')]


# Singleton
_espn_nfl_client = None

def get_espn_nfl_client() -> ESPNNFLLiveData:
    global _espn_nfl_client
    if _espn_nfl_client is None:
        _espn_nfl_client = ESPNNFLLiveData()
    return _espn_nfl_client
```

### 7.2 Enhanced Kalshi Client

**Add to:** `src/kalshi_client.py`
```python
# Add these methods to your KalshiClient class

def _make_request(self, method: str, endpoint: str, **kwargs):
    """Wrapper for API calls with auto-refresh and rate limiting"""
    max_retries = 3

    for attempt in range(max_retries):
        # Ensure token is valid
        if self._needs_token_refresh():
            if not self.login():
                raise Exception("Failed to refresh Kalshi token")

        try:
            url = f"{self.BASE_URL}{endpoint}"
            headers = kwargs.pop('headers', {})
            headers['accept'] = 'application/json'
            headers['Authorization'] = self.bearer_token

            response = requests.request(
                method, url, headers=headers, timeout=10, **kwargs
            )

            # Handle rate limiting
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 60))
                logger.warning(f"Rate limited, waiting {retry_after}s")
                time.sleep(retry_after)
                continue

            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)  # Exponential backoff

    raise Exception("Max retries exceeded")

def get_nfl_markets(self) -> List[Dict]:
    """Get NFL-specific markets with better filtering"""
    all_markets = self.get_all_markets(status='open')

    nfl_markets = []
    for market in all_markets:
        # Check ticker and title for NFL team codes
        ticker = market.get('ticker', '').upper()
        title = market.get('title', '').upper()

        # NFL keywords
        if any(keyword in title.lower() for keyword in ['nfl', 'super bowl']):
            nfl_markets.append(market)
            continue

        # Check for NFL team abbreviations
        if any(team in ticker for team in NFL_TEAM_CODES):
            nfl_markets.append(market)

    logger.info(f"Found {len(nfl_markets)} NFL markets")
    return nfl_markets

# NFL team codes for filtering
NFL_TEAM_CODES = [
    'KC', 'BUF', 'CIN', 'BAL', 'MIA', 'JAX', 'TEN', 'HOU', 'IND', 'CLE',
    'PHI', 'DAL', 'NYG', 'WAS', 'SF', 'SEA', 'LAR', 'ARI', 'GB', 'MIN',
    'DET', 'CHI', 'TB', 'NO', 'CAR', 'ATL', 'LV', 'LAC', 'DEN', 'NE', 'NYJ', 'PIT'
]
```

### 7.3 Streamlit Page with Auto-Refresh

**File:** `nfl_live_dashboard_page.py`
```python
"""
NFL Live Scores + Kalshi Markets Dashboard
Real-time updates with auto-refresh
"""
import streamlit as st
from streamlit_autorefresh import st_autorefresh
from src.espn_nfl_live_data import get_espn_nfl_client
from src.kalshi_client import KalshiClient
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

st.set_page_config(page_title="NFL Live Dashboard", layout="wide")

# Auto-refresh every 30 seconds
refresh_count = st_autorefresh(interval=30000, key="nfl_refresh")

st.title("🏈 NFL Live Scores + Betting Markets")

# Show last update time
st.caption(f"Last updated: {datetime.now().strftime('%I:%M:%S %p')} (Auto-refresh #{refresh_count})")

# Fetch data in parallel
@st.cache_data(ttl=30)
def fetch_dashboard_data():
    """Fetch ESPN + Kalshi data in parallel"""
    with ThreadPoolExecutor(max_workers=2) as executor:
        espn_future = executor.submit(get_espn_nfl_client().get_scoreboard)
        kalshi_future = executor.submit(KalshiClient().get_nfl_markets)

        games = espn_future.result()
        markets = kalshi_future.result()

    return games, markets

# Fetch data
with st.spinner("Loading live data..."):
    games, markets = fetch_dashboard_data()

# Filter options
col1, col2, col3 = st.columns(3)
with col1:
    show_live_only = st.checkbox("Live Games Only", value=True)
with col2:
    show_markets = st.checkbox("Show Betting Markets", value=True)
with col3:
    if st.button("🔄 Refresh Now"):
        st.cache_data.clear()
        st.rerun()

# Filter games
if show_live_only:
    games = [g for g in games if g.get('is_live')]

# Display games
st.markdown("---")

if not games:
    st.info("No games currently in progress. Check back during game time!")
else:
    for game in games:
        with st.container():
            col1, col2, col3 = st.columns([2, 1, 2])

            # Away team
            with col1:
                st.markdown(f"### {game['away_team']}")
                st.metric("Score", game['away_score'])

            # Game status
            with col2:
                st.markdown(f"**{game['status_detail']}**")
                if game['is_live']:
                    st.markdown("🔴 **LIVE**")
                    st.caption(f"{game['clock']} Q{game['period']}")

            # Home team
            with col3:
                st.markdown(f"### {game['home_team']}")
                st.metric("Score", game['home_score'])

            # Show markets if enabled
            if show_markets:
                game_markets = match_markets_to_game(game, markets)
                if game_markets:
                    with st.expander(f"📊 {len(game_markets)} Betting Markets"):
                        for market in game_markets:
                            st.write(f"**{market['title']}**")
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("Yes", f"{market.get('yes_price', 0)}¢")
                            with col2:
                                st.metric("No", f"{market.get('no_price', 0)}¢")

            st.markdown("---")

def match_markets_to_game(game: dict, markets: list) -> list:
    """Simple market matching by team names"""
    home = game['home_abbr'].upper()
    away = game['away_abbr'].upper()

    matched = []
    for market in markets:
        ticker = market.get('ticker', '').upper()
        if home in ticker and away in ticker:
            matched.append(market)

    return matched
```

---

## 8. Testing Strategy

### 8.1 Unit Tests

```python
# tests/test_espn_nfl_client.py
import pytest
from src.espn_nfl_live_data import ESPNNFLLiveData

def test_get_scoreboard():
    client = ESPNNFLLiveData()
    games = client.get_scoreboard()

    assert isinstance(games, list)
    if games:  # If games exist
        assert 'game_id' in games[0]
        assert 'home_team' in games[0]
        assert 'status' in games[0]

def test_get_live_games():
    client = ESPNNFLLiveData()
    live_games = client.get_live_games()

    assert isinstance(live_games, list)
    for game in live_games:
        assert game['is_live'] == True
```

### 8.2 Integration Tests

```python
# tests/test_integration_espn_kalshi.py
from src.espn_nfl_live_data import get_espn_nfl_client
from src.kalshi_client import KalshiClient

def test_combined_data_fetch():
    """Test fetching ESPN + Kalshi data"""
    espn = get_espn_nfl_client()
    kalshi = KalshiClient()

    games = espn.get_scoreboard()
    markets = kalshi.get_nfl_markets()

    assert len(games) > 0, "Should fetch games"
    assert len(markets) >= 0, "Should fetch markets (may be 0)"

    # Test matching
    matches = match_markets_to_games(games, markets)
    assert isinstance(matches, dict)
```

### 8.3 Manual Testing Checklist

- [ ] Test during live games (Sunday afternoons)
- [ ] Verify score updates every 30 seconds
- [ ] Check token refresh after 30 minutes
- [ ] Test rate limiting with rapid requests
- [ ] Verify market matching accuracy
- [ ] Test with no live games (off-season)
- [ ] Check cache performance
- [ ] Test database sync service

---

## 9. Common Issues & Solutions

### Issue 1: ESPN API Returns Empty Events

**Cause:** Wrong week or date parameter
**Solution:**
```python
# Don't specify week during off-season
games = client.get_scoreboard()  # Get current week

# For specific week during season
games = client.get_scoreboard(week=10)
```

### Issue 2: Kalshi Token Keeps Expiring

**Cause:** Not refreshing proactively
**Solution:** Already fixed in your code at line 41 (5-minute buffer)

### Issue 3: Streamlit Auto-Refresh Causes Flickering

**Cause:** Entire page reruns
**Solution:** Use fragments for live sections only
```python
@st.fragment(run_every="30s")
def live_scores_section():
    # Only this section refreshes
    pass
```

### Issue 4: Markets Don't Match Games

**Cause:** Team name variations
**Solution:** Use comprehensive team mapping (Section 5.1)

### Issue 5: Rate Limiting Errors

**Cause:** Too frequent API calls
**Solution:**
- Increase cache TTL
- Use exponential backoff
- Implement request queuing

---

## 10. Recommended Dependencies

Add to `requirements.txt`:
```
# ESPN & Kalshi Integration
requests>=2.31.0
espn-scraper>=0.1.0  # File-based caching
streamlit-autorefresh>=1.0.1  # Auto-refresh component

# Scheduling for background sync
schedule>=1.2.0

# Already in your requirements:
# streamlit
# psycopg2-binary
# python-dotenv
```

---

## 11. Configuration Updates

Add to `config/default.yaml`:
```yaml
espn:
  cache_ttl_live: 30  # 30 seconds for live games
  cache_ttl_completed: 3600  # 1 hour for completed
  timeout: 10  # Request timeout
  user_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"

kalshi:
  token_refresh_buffer: 300  # 5 minutes before expiration
  rate_limit_delay: 0.5  # 500ms between requests
  max_retries: 3
  cache_ttl_markets: 60  # 60 seconds
  cache_ttl_orderbook: 30  # 30 seconds

realtime_sync:
  espn_interval: 30  # Sync every 30 seconds
  kalshi_interval: 60  # Sync every 60 seconds
  enabled: true
```

---

## 12. Next Steps

### Immediate Actions (This Week)
1. Create `src/espn_nfl_live_data.py` (copy NCAA structure)
2. Test ESPN API with current week NFL games
3. Fix Kalshi token refresh (add `_make_request()`)
4. Install `streamlit-autorefresh`
5. Create basic dashboard page

### Short-Term (Next 2 Weeks)
1. Implement database sync service
2. Build market matching algorithm
3. Add comprehensive testing
4. Deploy background sync service
5. Optimize performance with caching

### Long-Term (Future Enhancements)
1. Add WebSocket support for real-time Kalshi prices
2. Implement predictive analytics (combine scores + odds)
3. Add historical data analysis
4. Build alert system for bet opportunities
5. Create mobile-responsive design

---

## 13. Additional Resources

### GitHub Repositories
- **ESPN Endpoints:** https://gist.github.com/nntrn/ee26cb2a0716de0947a0a4e9a157bc1c
- **ESPN API Docs:** https://gist.github.com/akeaswaran/b48b02f1c94f873c6655e7129910fc3b
- **Kalshi Starter:** https://github.com/Kalshi/kalshi-starter-code-python
- **espn_scraper:** https://github.com/andr3w321/espn_scraper

### Documentation
- **Kalshi API Docs:** https://docs.kalshi.com/
- **Kalshi Rate Limits:** https://docs.kalshi.com/getting_started/rate_limits
- **Streamlit Fragments:** https://docs.streamlit.io/develop/api-reference/execution-flow/st.fragment

### Community Resources
- **ESPN API Guide:** https://zuplo.com/learning-center/espn-hidden-api-guide
- **Kalshi API Guide:** https://zuplo.com/learning-center/kalshi-api
- **Streamlit Auto-Refresh:** https://github.com/kmcgrady/streamlit-autorefresh

---

## Conclusion

This research provides a comprehensive foundation for integrating ESPN NFL live scores and Kalshi betting markets into your Streamlit dashboard. The key recommendations are:

1. **ESPN:** Use direct API calls with file-based caching, 30s refresh for live games
2. **Kalshi:** Fix token refresh, implement rate limiting, cache market data
3. **Streamlit:** Use `streamlit-autorefresh` or fragments for auto-updates
4. **Database:** Real-time sync service with 30s/60s intervals
5. **Matching:** Build team mapping system for accurate market-game linkage

**Estimated Implementation Time:** 7-10 days for full integration

Your existing codebase (`src/espn_ncaa_live_data.py` and `src/kalshi_client.py`) provides an excellent foundation. Most of the patterns are already in place—you just need to extend them for NFL and add the real-time sync layer.

Good luck with the implementation! Let me know if you need clarification on any section.
