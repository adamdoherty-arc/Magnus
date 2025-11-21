# ESPN + Kalshi Integration - Quick Reference

**Quick links to implementation patterns and code snippets**

---

## ESPN NFL API - Quick Start

### Basic Implementation
```python
# Endpoint
https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard

# Response Structure
events[].status.type.name  # STATUS_IN_PROGRESS, STATUS_FINAL, etc.
events[].competitions[].competitors[]  # Teams and scores

# Recommended: 30-60 second polling for live games
```

### Code Template
```python
import requests

class ESPNNFLLiveData:
    BASE_URL = "https://site.api.espn.com/apis/site/v2/sports/football/nfl"

    def get_scoreboard(self, week=None):
        url = f"{self.BASE_URL}/scoreboard"
        params = {'seasontype': 2, 'week': week} if week else {}
        response = requests.get(url, params=params, timeout=10)
        return response.json()['events']
```

---

## Kalshi API - Quick Start

### Authentication (30-min Token)
```python
# Login
POST https://trading-api.kalshi.com/trade-api/v2/login
Body: {"email": "...", "password": "..."}
Response: {"token": "..."}

# Use token
Headers: {"Authorization": "Bearer TOKEN"}

# Refresh before 30 minutes (recommended: 25 min)
```

### Get NFL Markets
```python
GET /trade-api/v2/markets?status=open&limit=1000

# Filter by team codes: KC, BUF, SF, etc.
```

---

## Streamlit Auto-Refresh

### Option 1: streamlit-autorefresh
```python
from streamlit_autorefresh import st_autorefresh

count = st_autorefresh(interval=30000, key="refresh")  # 30 seconds
# Your data fetching here
```

### Option 2: Fragments (Built-in)
```python
@st.fragment(run_every="30s")
def live_section():
    games = fetch_games()
    display_games(games)
```

---

## Caching Strategy

### ESPN Data
```python
@st.cache_data(ttl=60)  # 60 seconds for live
def get_live_scores():
    return espn_client.get_scoreboard()

@st.cache_data(ttl=3600)  # 1 hour for completed
def get_completed_games():
    return espn_client.get_scoreboard()
```

### Kalshi Data
```python
@st.cache_data(ttl=60)  # Markets change frequently
def get_nfl_markets():
    return kalshi_client.get_nfl_markets()

@st.cache_data(ttl=30)  # Live prices
def get_market_prices(ticker):
    return kalshi_client.get_market_orderbook(ticker)
```

---

## Database Schema

### NFL Scores Table
```sql
CREATE TABLE nfl_live_scores (
    game_id VARCHAR(50) PRIMARY KEY,
    home_team VARCHAR(100),
    away_team VARCHAR(100),
    home_score INTEGER DEFAULT 0,
    away_score INTEGER DEFAULT 0,
    status VARCHAR(50),
    is_live BOOLEAN,
    last_updated TIMESTAMP DEFAULT NOW()
);
```

### Kalshi Markets Table
```sql
CREATE TABLE kalshi_nfl_markets (
    ticker VARCHAR(100) PRIMARY KEY,
    title TEXT,
    yes_price INTEGER,
    no_price INTEGER,
    game_id VARCHAR(50) REFERENCES nfl_live_scores(game_id),
    last_updated TIMESTAMP DEFAULT NOW()
);
```

---

## Real-Time Sync Service

### Background Service
```python
import schedule
import time

def sync_scores():
    games = espn.get_scoreboard()
    db.upsert_games(games)

schedule.every(30).seconds.do(sync_scores)

while True:
    schedule.run_pending()
    time.sleep(1)
```

---

## Market Matching

### Team Name Mapping
```python
NFL_TEAMS = {
    'Kansas City Chiefs': ['KC', 'CHIEFS'],
    'Buffalo Bills': ['BUF', 'BILLS'],
    # ... all 32 teams
}

def match_market_to_game(game, markets):
    home = game['home_abbr']
    away = game['away_abbr']

    matched = []
    for market in markets:
        ticker = market['ticker'].upper()
        if home in ticker and away in ticker:
            matched.append(market)
    return matched
```

---

## Common Issues

### ESPN API Returns Empty
**Solution:** Don't specify week during off-season
```python
games = client.get_scoreboard()  # Auto-detects current week
```

### Kalshi Token Expired
**Solution:** Refresh at 25-minute mark
```python
if datetime.now() >= (token_expires - timedelta(minutes=5)):
    client.login()
```

### Streamlit Flickering
**Solution:** Use fragments instead of full page refresh
```python
@st.fragment(run_every="30s")
def live_only():
    # Only this refreshes
    pass
```

---

## Rate Limits

### ESPN (Unofficial)
- No official limits
- Recommended: 30-60s polling
- Be respectful, don't hammer

### Kalshi (Official)
- Tiered by subscription
- 429 status when exceeded
- Use exponential backoff

```python
# Exponential backoff
for attempt in range(3):
    try:
        return api_call()
    except RateLimitError:
        time.sleep(2 ** attempt)
```

---

## Performance Optimization

### Parallel Fetching
```python
from concurrent.futures import ThreadPoolExecutor

def fetch_all():
    with ThreadPoolExecutor(max_workers=2) as executor:
        espn_future = executor.submit(get_espn_data)
        kalshi_future = executor.submit(get_kalshi_data)
        return espn_future.result(), kalshi_future.result()
```

### Database Indexes
```sql
CREATE INDEX idx_nfl_is_live ON nfl_live_scores(is_live);
CREATE INDEX idx_nfl_status ON nfl_live_scores(status);
CREATE INDEX idx_kalshi_game_id ON kalshi_nfl_markets(game_id);
```

---

## Testing Commands

### Test ESPN Client
```bash
python src/espn_nfl_live_data.py
```

### Test Kalshi Client
```bash
python src/kalshi_client.py
```

### Run Dashboard
```bash
streamlit run nfl_live_dashboard_page.py
```

### Start Background Sync
```bash
# Windows
start_nfl_sync.bat

# Linux/Mac
python src/nfl_realtime_sync.py &
```

---

## Key Files to Create

1. `src/espn_nfl_live_data.py` - ESPN NFL client
2. `src/nfl_db_manager.py` - Database operations
3. `src/nfl_realtime_sync.py` - Background sync service
4. `nfl_live_dashboard_page.py` - Streamlit page
5. `start_nfl_sync.bat` - Windows service launcher

---

## Dependencies

```bash
pip install requests espn-scraper streamlit-autorefresh schedule
```

---

## Configuration (config/default.yaml)

```yaml
espn:
  cache_ttl_live: 30
  cache_ttl_completed: 3600
  timeout: 10

kalshi:
  token_refresh_buffer: 300
  rate_limit_delay: 0.5
  cache_ttl_markets: 60

realtime_sync:
  espn_interval: 30
  kalshi_interval: 60
  enabled: true
```

---

## Useful Links

- ESPN Endpoints: https://gist.github.com/nntrn/ee26cb2a0716de0947a0a4e9a157bc1c
- Kalshi API Docs: https://docs.kalshi.com/
- Streamlit Auto-Refresh: https://github.com/kmcgrady/streamlit-autorefresh

---

**See ESPN_KALSHI_INTEGRATION_RESEARCH_2025.md for full documentation**
