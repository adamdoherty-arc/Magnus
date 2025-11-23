# NFL Real-Time Data Pipeline - Architecture Documentation

## Overview

The NFL Real-Time Data Pipeline is a scalable, event-driven system that ingests live NFL game data from multiple sources, processes it in real-time, correlates it with Kalshi prediction markets, and delivers actionable alerts via Telegram.

**Author**: Magnus Data Engineering Team
**Created**: 2025-11-09
**Version**: 1.0.0

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Data Flow](#data-flow)
3. [Database Schema](#database-schema)
4. [Components](#components)
5. [API Integrations](#api-integrations)
6. [Real-Time Processing](#real-time-processing)
7. [Alert System](#alert-system)
8. [Performance Optimization](#performance-optimization)
9. [Deployment](#deployment)
10. [Monitoring](#monitoring)

---

## Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    DATA SOURCES                                  │
├─────────────────────────────────────────────────────────────────┤
│  ESPN API  │  Weather API  │  Kalshi API  │  Social Media       │
└──────┬──────────┬───────────────┬──────────────┬────────────────┘
       │          │               │              │
       ▼          ▼               ▼              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   DATA FETCHERS                                  │
├─────────────────────────────────────────────────────────────────┤
│  NFLDataFetcher  │  KalshiClient  │  WeatherFetcher             │
└──────┬────────────────┬──────────────────┬──────────────────────┘
       │                │                  │
       ▼                ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│               SYNC ENGINE (5-second polling)                     │
├─────────────────────────────────────────────────────────────────┤
│  NFLRealtimeSync                                                 │
│    - Score updates                                               │
│    - Play-by-play tracking                                       │
│    - Kalshi price monitoring                                     │
│    - Event correlation                                           │
└──────┬────────────────┬──────────────────┬──────────────────────┘
       │                │                  │
       ▼                ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                   DATABASE LAYER                                 │
├─────────────────────────────────────────────────────────────────┤
│  PostgreSQL (magnus)                                             │
│    - nfl_games (scores, status)                                 │
│    - nfl_plays (play-by-play)                                   │
│    - nfl_player_stats                                            │
│    - nfl_injuries                                                │
│    - nfl_kalshi_correlations                                     │
│    - nfl_alert_history                                           │
└──────┬────────────────┬──────────────────┬──────────────────────┘
       │                │                  │
       ▼                ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                  ALERT PROCESSOR                                 │
├─────────────────────────────────────────────────────────────────┤
│  - Trigger evaluation                                            │
│  - Rate limiting                                                 │
│  - Message formatting                                            │
└──────┬───────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────────┐
│               NOTIFICATION DELIVERY                              │
├─────────────────────────────────────────────────────────────────┤
│  Telegram Bot  │  Email (future)  │  SMS (future)                │
└─────────────────────────────────────────────────────────────────┘
```

### Design Principles

1. **Event-Driven Architecture**: React to changes in real-time (scores, injuries, prices)
2. **Idempotent Operations**: Safe to retry any operation without side effects
3. **Graceful Degradation**: If one data source fails, others continue working
4. **Rate Limiting**: Respect API limits with exponential backoff
5. **Scalability**: Designed to handle 16 simultaneous NFL games
6. **Observability**: Comprehensive logging and performance tracking

---

## Data Flow

### Live Game Update Flow

```
1. POLL SCOREBOARD (every 5 seconds)
   └─> ESPN Scoreboard API
       └─> Parse games
           ├─> Live games → Continue to step 2
           ├─> Scheduled games → Store schedule
           └─> Finished games → Update status

2. UPDATE SCORES
   └─> For each live game:
       ├─> Compare old vs new score
       ├─> If score changed:
       │   ├─> Fetch play-by-play details
       │   ├─> Insert new plays
       │   └─> Send score alert
       └─> Store updated game state

3. MONITOR KALSHI MARKETS
   └─> Fetch NFL markets
       └─> For each market:
           ├─> Compare old vs new price
           ├─> If price spiked (>10%):
           │   ├─> Correlate with recent plays
           │   ├─> Store correlation
           │   └─> Send price alert
           └─> Store price snapshot

4. CHECK INJURIES (every 5 minutes)
   └─> Fetch injury reports
       └─> For each injury:
           ├─> If new "Out" status → Alert
           └─> Store injury record

5. PROCESS ALERTS
   └─> Evaluate active triggers
       ├─> Check cooldown periods
       ├─> Check daily limits
       └─> Send qualifying alerts
```

### Database Write Flow

All database operations use **UPSERT** pattern:

```sql
INSERT INTO nfl_games (...)
VALUES (...)
ON CONFLICT (game_id) DO UPDATE SET
    home_score = EXCLUDED.home_score,
    away_score = EXCLUDED.away_score,
    ...
    last_updated = NOW()
```

This ensures:
- No duplicate records
- Latest data always wins
- Automatic timestamp tracking

---

## Database Schema

### Core Tables

#### 1. `nfl_games` - Game State
- **Purpose**: Store game schedules and live scores
- **Update Frequency**: Every 5 seconds during live games
- **Key Indexes**:
  - `idx_nfl_games_live` (WHERE is_live = true) - Fast live game queries
  - `idx_nfl_games_status` - Filter by game status
  - `idx_nfl_games_time` - Upcoming games

#### 2. `nfl_plays` - Play-by-Play
- **Purpose**: Detailed play-by-play data
- **Update Frequency**: On score changes
- **Key Indexes**:
  - `idx_nfl_plays_sequence` - Ordered plays per game
  - `idx_nfl_plays_scoring` - Fast scoring play lookups

#### 3. `nfl_kalshi_correlations` - Market Reactions
- **Purpose**: Link NFL events to Kalshi price movements
- **Update Frequency**: Real-time (on significant plays)
- **Key Indexes**:
  - `idx_nfl_kalshi_corr_event` - Find correlations by event type
  - `idx_nfl_kalshi_corr_timestamp` - Time-series analysis

#### 4. `nfl_alert_history` - Alert Tracking
- **Purpose**: Log all sent alerts
- **Update Frequency**: Every alert sent
- **Key Indexes**:
  - `idx_nfl_alert_history_sent` - Recent alerts
  - `idx_nfl_alert_history_status` - Failed alerts

### Database Performance

**Connection Pooling**:
```python
# psycopg2 connection pool (implemented in NFLDBManager)
- Min connections: 2
- Max connections: 10
- Connection timeout: 30s
```

**Query Optimization**:
- All foreign keys indexed
- Materialized views for complex queries
- Partial indexes on filtered columns (e.g., `WHERE is_live = true`)

---

## Components

### 1. NFLDataFetcher (`src/nfl_data_fetcher.py`)

**Responsibilities**:
- Fetch data from ESPN API
- Parse scoreboard and play-by-play data
- Fetch weather data for outdoor stadiums
- Fetch betting odds (optional)
- Fetch injury reports

**Rate Limiting**:
```python
ESPN_CALL_DELAY = 1.0  # 1 second between calls
MAX_CALLS_PER_MINUTE = 60
```

**Key Methods**:
- `get_scoreboard(date)` - Get games for a specific date
- `get_play_by_play(game_id)` - Detailed play-by-play
- `get_weather_for_game(venue, time)` - Weather forecast
- `get_injuries()` - League-wide injury reports

### 2. NFLDBManager (`src/nfl_db_manager.py`)

**Responsibilities**:
- Database connection management
- CRUD operations for all tables
- Sync logging and performance tracking
- Analytics queries

**Connection Management**:
```python
db_config = {
    'host': 'localhost',
    'port': '5432',
    'database': 'magnus',
    'user': 'postgres',
    'password': os.getenv('DB_PASSWORD')
}
```

**Key Methods**:
- `upsert_game(game_data)` - Insert/update game
- `insert_play(play_data)` - Record play-by-play
- `insert_kalshi_correlation(data)` - Track market reactions
- `log_alert(alert_data)` - Record sent alerts

### 3. NFLRealtimeSync (`src/nfl_realtime_sync.py`)

**Responsibilities**:
- Main sync loop (runs every 5 seconds)
- Orchestrate all data fetching
- Detect score changes and events
- Trigger alerts
- Monitor Kalshi prices

**Sync Cycle**:
```python
def _sync_cycle(self):
    1. Update live game scores
    2. Update Kalshi prices
    3. Check for injuries (every 5 min)
    4. Process alert triggers
```

**State Tracking**:
```python
self.last_scores: Dict[str, tuple]  # Track score changes
self.last_kalshi_prices: Dict[str, Decimal]  # Track price changes
self.monitored_games: Set[str]  # Active games
```

### 4. TelegramNotifier (`src/telegram_notifier.py`)

**Responsibilities**:
- Format alert messages
- Send Telegram notifications
- Retry logic with exponential backoff
- Rate limiting

**Message Templates**:
- Score updates
- Kalshi price spikes
- Injury alerts
- Significant plays

---

## API Integrations

### ESPN API (Free, Unofficial)

**Base URL**: `https://site.api.espn.com/apis/site/v2/sports/football/nfl`

**Endpoints Used**:

1. **Scoreboard**
   ```
   GET /scoreboard?dates=YYYYMMDD
   Response: All games for date with scores, status, odds
   ```

2. **Play-by-Play**
   ```
   GET /summary?event={game_id}
   Response: Detailed play-by-play data
   ```

3. **Injuries**
   ```
   GET /injuries
   Response: League-wide injury reports
   ```

**Rate Limits**: Unofficial, recommend 1 call/second

### OpenWeatherMap API

**Base URL**: `https://api.openweathermap.org/data/2.5`

**Endpoint**:
```
GET /forecast?lat={lat}&lon={lon}&appid={key}&units=imperial
Response: 5-day forecast in 3-hour intervals
```

**Cost**: Free tier (60 calls/minute, 1M calls/month)

### Kalshi API

**Base URL**: `https://trading-api.kalshi.com/trade-api/v2`

**Endpoints** (via `KalshiClient`):
- `/login` - Get bearer token
- `/markets` - Fetch all markets
- `/markets/{ticker}` - Market details
- `/markets/{ticker}/orderbook` - Current bids/asks

**Authentication**:
```python
# Automatic token refresh (expires every 30 minutes)
kalshi_client.login()
# Subsequent calls auto-refresh if needed
```

### The Odds API (Optional, Paid)

**Base URL**: `https://api.the-odds-api.com/v4`

**Endpoint**:
```
GET /sports/americanfootball_nfl/odds
Response: Latest betting lines from multiple sportsbooks
```

**Cost**: $50/month for real-time odds

---

## Real-Time Processing

### Update Frequency Strategy

| Data Type | Frequency | Rationale |
|-----------|-----------|-----------|
| Live Game Scores | 5 seconds | Catch touchdowns within seconds |
| Kalshi Prices | 5 seconds | React to market movements |
| Play-by-Play | On score change | Avoid unnecessary API calls |
| Injuries | 5 minutes | Reports don't change frequently |
| Weather | 30 minutes | Forecasts update slowly |
| Scheduled Games | 1 hour | Schedule is static |

### Event Detection

**Score Change Detection**:
```python
old_score = self.last_scores.get(game_id)
new_score = (game['home_score'], game['away_score'])

if old_score and old_score != new_score:
    # Score changed - fetch plays and alert
    self._update_play_by_play(game_id)
    self._send_score_alert(game, old_score, new_score)
```

**Price Spike Detection**:
```python
old_price = self.last_kalshi_prices.get(ticker)
change_pct = ((new_price - old_price) / old_price) * 100

if abs(change_pct) > 10:  # 10% threshold
    self._send_kalshi_price_alert(...)
```

### Correlation Tracking

When a significant play occurs (touchdown, turnover), the system:

1. Captures current Kalshi prices for related markets
2. Waits 5 seconds
3. Fetches updated prices
4. Calculates price change percentage
5. Stores correlation in `nfl_kalshi_correlations`
6. Triggers alert if impact is high

**Impact Levels**:
- `extreme`: >20% price change
- `high`: 10-20% change
- `medium`: 5-10% change
- `low`: <5% change

---

## Alert System

### Alert Types

1. **Score Change Alerts**
   - Triggered on: Touchdowns, field goals, safeties
   - Priority: High
   - Example:
     ```
     🏈 SCORE UPDATE

     Chiefs 21 @ Bills 17

     🎯 Chiefs score 7 points!
     ⏱️ Q3 - 8:24
     ```

2. **Kalshi Price Alerts**
   - Triggered on: >10% price movement
   - Priority: Medium
   - Example:
     ```
     📈 KALSHI PRICE MOVEMENT

     Will the Chiefs win Super Bowl?

     Price: 0.45 → 0.52 (+15.6%)
     Volume: $124,500
     Ticker: NFL-CHIEFS-WIN
     ```

3. **Injury Alerts**
   - Triggered on: Key players listed as "Out"
   - Priority: High
   - Example:
     ```
     🚑 INJURY UPDATE

     Patrick Mahomes (QB)
     Team: Kansas City Chiefs
     Status: Questionable
     Injury: Ankle
     ```

4. **Significant Play Alerts**
   - Triggered on: Long plays (>20 yards), turnovers
   - Priority: Medium

### Alert Configuration

**Cooldown Mechanism**:
- Prevents alert spam
- Default: 5 minutes between similar alerts
- Configurable per alert type

**Daily Limits**:
- Max 100 alerts per day (configurable)
- High-priority alerts bypass limits

**Rate Limiting**:
```python
# Check last trigger time
if trigger['last_triggered']:
    cooldown_end = trigger['last_triggered'] + timedelta(minutes=5)
    if datetime.now() < cooldown_end:
        skip_alert()
```

### Notification Delivery

**Telegram**:
- Markdown formatting
- Retry logic (3 attempts)
- Exponential backoff on failures
- Rate limit handling (Telegram: 30 msg/second)

**Future Channels**:
- Email (via SendGrid)
- SMS (via Twilio)
- Push notifications (via Firebase)

---

## Performance Optimization

### Database Optimization

**1. Indexing Strategy**:
```sql
-- Partial index for live games (most-queried subset)
CREATE INDEX idx_nfl_games_live ON nfl_games(is_live)
WHERE is_live = true;

-- Composite index for time-range queries
CREATE INDEX idx_nfl_plays_sequence ON nfl_plays(game_id, sequence_number);

-- Index on foreign keys
CREATE INDEX idx_nfl_kalshi_corr_game ON nfl_kalshi_correlations(game_id);
```

**2. Connection Pooling**:
```python
# Reuse connections instead of creating new ones
conn = self.connection_pool.getconn()
try:
    # Execute queries
finally:
    self.connection_pool.putconn(conn)
```

**3. Batch Inserts**:
```python
# Insert 100 plays at once instead of 100 individual queries
cur.executemany("""
    INSERT INTO nfl_plays (...) VALUES (...)
    ON CONFLICT DO NOTHING
""", batch_of_plays)
```

**4. Materialized Views**:
```sql
-- Pre-compute expensive joins
CREATE MATERIALIZED VIEW v_nfl_kalshi_opportunities AS
SELECT ...complex join...
FROM nfl_games g
INNER JOIN kalshi_markets km ON ...
WHERE ...;

-- Refresh periodically
REFRESH MATERIALIZED VIEW v_nfl_kalshi_opportunities;
```

### API Optimization

**1. Rate Limiting**:
```python
def _rate_limit_espn(self):
    elapsed = time.time() - self.last_espn_call
    if elapsed < self.espn_call_delay:
        time.sleep(self.espn_call_delay - elapsed)
```

**2. Parallel Fetching**:
```python
with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [
        executor.submit(self.fetch_game, game_id)
        for game_id in live_game_ids
    ]
    results = [f.result() for f in futures]
```

**3. Response Caching**:
```python
@lru_cache(maxsize=100, ttl=60)  # Cache for 60 seconds
def get_market_details(self, ticker: str):
    # Expensive API call
    ...
```

### Query Optimization

**1. Limit Result Sets**:
```python
# Only fetch what you need
cur.execute("""
    SELECT id, home_team, away_team, home_score, away_score
    FROM nfl_games
    WHERE is_live = true
    LIMIT 20
""")
```

**2. Use EXISTS Instead of IN**:
```sql
-- Faster
SELECT * FROM nfl_games g
WHERE EXISTS (
    SELECT 1 FROM kalshi_markets km
    WHERE km.home_team = g.home_team
);

-- Slower
SELECT * FROM nfl_games
WHERE home_team IN (SELECT home_team FROM kalshi_markets);
```

**3. Analyze Query Plans**:
```sql
EXPLAIN ANALYZE
SELECT * FROM v_nfl_live_games;
```

---

## Deployment

### System Requirements

**Minimum**:
- CPU: 2 cores
- RAM: 4 GB
- Storage: 20 GB
- OS: Windows 10/11, Linux, macOS

**Recommended** (for 16 simultaneous games):
- CPU: 4 cores
- RAM: 8 GB
- Storage: 50 GB SSD
- OS: Windows Server, Ubuntu 20.04+

### Installation Steps

1. **Install Python 3.9+**
   ```bash
   python --version  # Should be 3.9 or higher
   ```

2. **Install PostgreSQL 14+**
   ```bash
   psql --version  # Should be 14.0 or higher
   ```

3. **Create Database**
   ```sql
   CREATE DATABASE magnus;
   ```

4. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure Environment Variables**
   ```bash
   # .env file
   DB_PASSWORD=your_postgres_password
   KALSHI_EMAIL=your_kalshi_email
   KALSHI_PASSWORD=your_kalshi_password
   OPENWEATHER_API_KEY=your_weather_key  # Optional
   ODDS_API_KEY=your_odds_key  # Optional
   TELEGRAM_BOT_TOKEN=your_bot_token
   TELEGRAM_CHAT_ID=your_chat_id
   TELEGRAM_ENABLED=true
   ```

6. **Initialize Database Schema**
   ```bash
   python src/nfl_db_manager.py
   ```

7. **Start Sync Engine**
   ```bash
   # Windows
   start_nfl_sync.bat

   # Linux/Mac
   python src/nfl_realtime_sync.py
   ```

### Running as a Service

**Windows (Task Scheduler)**:
1. Open Task Scheduler
2. Create Basic Task
3. Trigger: At startup
4. Action: Start program → `start_nfl_sync.bat`
5. Enable "Run whether user is logged on or not"

**Linux (systemd)**:
```ini
# /etc/systemd/system/nfl-sync.service
[Unit]
Description=NFL Real-Time Sync Service
After=network.target postgresql.service

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/WheelStrategy
ExecStart=/usr/bin/python3 /path/to/WheelStrategy/src/nfl_realtime_sync.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Start service:
```bash
sudo systemctl enable nfl-sync
sudo systemctl start nfl-sync
sudo systemctl status nfl-sync
```

### Docker Deployment (Optional)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "src/nfl_realtime_sync.py"]
```

```bash
docker build -t nfl-sync .
docker run -d --name nfl-sync --env-file .env nfl-sync
```

---

## Monitoring

### Health Checks

**Automated Checks** (every 60 seconds):
1. Database connectivity
2. API availability (ESPN, Kalshi)
3. Telegram bot connection
4. Disk space

**Alert Thresholds**:
- 5 consecutive sync failures → Send error alert
- 10 API errors per hour → Throttle requests
- 3 database connection errors → Restart connection pool

### Performance Metrics

**Tracked Metrics**:
```python
metrics = {
    'sync_cycle_duration_ms': 1234,
    'api_latency_ms': 456,
    'db_query_time_ms': 89,
    'alert_delivery_success_rate': 0.98,
    'kalshi_price_fetch_time_ms': 234,
    'live_games_count': 12,
    'alerts_sent_today': 45
}
```

**Logging**:
```python
# Logs stored in logs/nfl_pipeline.log
logger.info("Sync cycle completed in 1.2s")
logger.warning("ESPN API slow response (5.3s)")
logger.error("Failed to send Telegram alert: Rate limited")
```

### Database Monitoring

**Sync Performance View**:
```sql
SELECT
    sync_type,
    AVG(duration_ms) as avg_duration,
    MAX(duration_ms) as max_duration,
    COUNT(*) as total_syncs,
    SUM(CASE WHEN sync_status = 'failed' THEN 1 ELSE 0 END) as failures
FROM nfl_data_sync_log
WHERE started_at > NOW() - INTERVAL '24 hours'
GROUP BY sync_type;
```

**Query Performance**:
```sql
-- PostgreSQL query stats
SELECT
    query,
    calls,
    total_time,
    mean_time,
    max_time
FROM pg_stat_statements
ORDER BY total_time DESC
LIMIT 10;
```

### Alerting on Issues

**Critical Alerts** (sent to Telegram):
- Sync engine stopped unexpectedly
- Database connection lost
- Kalshi API authentication failed
- >10 consecutive failed alerts

**Warning Alerts**:
- Slow API responses (>5s)
- High database query times (>1s)
- Approaching API rate limits

---

## Troubleshooting

### Common Issues

**1. "Database connection failed"**
- Check `DB_PASSWORD` in `.env`
- Verify PostgreSQL is running: `psql -U postgres -c "SELECT 1"`
- Check firewall rules

**2. "Kalshi login failed"**
- Verify credentials in `.env`
- Check if Kalshi API is accessible: `curl https://trading-api.kalshi.com/trade-api/v2/health`
- Ensure account is not locked

**3. "No live games found"**
- Check if it's NFL season (September - February)
- Verify ESPN API: `curl "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"`
- Check game schedule

**4. "Telegram alerts not sending"**
- Verify `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`
- Check bot permissions
- Test connection: `python -c "from telegram_notifier import TelegramNotifier; TelegramNotifier().test_connection()"`

### Debug Mode

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Run single sync cycle
sync = NFLRealtimeSync(update_interval_seconds=10)
sync._sync_cycle()  # Single cycle for testing
```

---

## Future Enhancements

### Planned Features

1. **Machine Learning Win Probability**
   - Train model on historical play-by-play data
   - Real-time win probability updates
   - Compare to Kalshi market prices for arbitrage

2. **Social Sentiment Analysis**
   - Twitter API integration
   - Reddit sentiment tracking
   - Correlation with Kalshi price movements

3. **Advanced Analytics Dashboard**
   - Streamlit dashboard for live monitoring
   - Historical performance charts
   - Kalshi correlation heatmaps

4. **Auto-Trading (Experimental)**
   - Automated bet placement on high-confidence signals
   - Kelly Criterion position sizing
   - Backtesting framework

5. **Mobile App**
   - Push notifications
   - Custom alert configuration
   - Live game tracking

---

## License & Disclaimer

**License**: Proprietary - Magnus Wheel Strategy Platform

**Disclaimer**: This system is for informational purposes only. Betting involves risk. Do not bet more than you can afford to lose. Always verify data independently before making financial decisions.

---

## Support & Contact

For technical support or questions:
- **Email**: support@magnustrading.com
- **Documentation**: https://docs.magnustrading.com/nfl-pipeline
- **Issue Tracker**: https://github.com/magnus/wheel-strategy/issues

---

**Document Version**: 1.0.0
**Last Updated**: 2025-11-09
**Next Review**: 2025-12-01
