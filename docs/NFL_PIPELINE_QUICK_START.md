# NFL Pipeline - Quick Start Guide

Get the NFL real-time data pipeline running in 15 minutes.

---

## Prerequisites

✅ **Required**:
- Python 3.9+
- PostgreSQL 14+
- Internet connection
- Kalshi account (free to create)
- Telegram account

⚙️ **Optional** (for enhanced features):
- OpenWeatherMap API key (free)
- The Odds API key (paid)
- Twitter API key (for sentiment analysis)

---

## Step 1: Environment Setup (5 minutes)

### 1.1 Update `.env` File

Add these variables to your existing `c:/Code/WheelStrategy/.env`:

```bash
# NFL Pipeline Configuration
# ================================================

# Kalshi API (Required)
KALSHI_EMAIL=your_kalshi_email@example.com
KALSHI_PASSWORD=your_kalshi_password

# Weather API (Optional - for outdoor stadium weather)
OPENWEATHER_API_KEY=your_openweather_key_here

# Betting Odds API (Optional - paid service)
ODDS_API_KEY=your_odds_api_key_here

# Telegram (Already configured, just verify)
TELEGRAM_BOT_TOKEN=your_existing_bot_token
TELEGRAM_CHAT_ID=your_existing_chat_id
TELEGRAM_ENABLED=true
```

### 1.2 Get Free API Keys

**OpenWeatherMap** (Optional but recommended):
1. Go to https://openweathermap.org/api
2. Sign up for free account
3. Generate API key (60 calls/minute, free)
4. Add to `.env` as `OPENWEATHER_API_KEY`

**Kalshi Account** (Required):
1. Go to https://kalshi.com
2. Create free account
3. Verify email
4. Add credentials to `.env`

---

## Step 2: Database Setup (3 minutes)

### 2.1 Initialize NFL Schema

```bash
cd c:/Code/WheelStrategy
python src/nfl_db_manager.py
```

**Expected Output**:
```
NFL database tables initialized successfully
Database Stats:
  Total Games: 0
  Live Games: 0
  Total Plays: 0
  Active Injuries: 0
  Alerts Today: 0
Test Complete!
```

### 2.2 Verify Tables Created

```bash
psql -U postgres -d magnus -c "\dt nfl_*"
```

**Expected Output**:
```
                   List of relations
 Schema |          Name           | Type  |  Owner
--------+-------------------------+-------+----------
 public | nfl_alert_history       | table | postgres
 public | nfl_alert_triggers      | table | postgres
 public | nfl_data_sync_log       | table | postgres
 public | nfl_games               | table | postgres
 public | nfl_injuries            | table | postgres
 public | nfl_kalshi_correlations | table | postgres
 public | nfl_plays               | table | postgres
 public | nfl_player_stats        | table | postgres
 public | nfl_social_sentiment    | table | postgres
```

---

## Step 3: Test Data Fetching (3 minutes)

### 3.1 Test ESPN API

```bash
python src/nfl_data_fetcher.py
```

**Expected Output**:
```
NFL DATA FETCHER - Test
Fetching today's scoreboard...
Found 12 games:

Denver Broncos @ Kansas City Chiefs
  Score: 17 - 24
  Status: live (Q3)
  Venue: Arrowhead Stadium (Outdoor)

...
```

If no games today (off-season), you'll see:
```
Found 0 games
```

### 3.2 Test Kalshi Connection

```bash
python -c "from kalshi_client import KalshiClient; client = KalshiClient(); print('✅ Login successful!' if client.login() else '❌ Login failed')"
```

**Expected Output**:
```
✅ Login successful!
```

### 3.3 Test Telegram

```bash
python -c "from telegram_notifier import TelegramNotifier; TelegramNotifier().test_connection()"
```

**Expected Output**:
```
Test message sent successfully: 123456789
✅ Connection successful!
```

You should receive a test message in Telegram:
```
✅ Telegram Connection Test

Magnus Trading Dashboard is successfully connected!

🕓 Test Time: 2025-11-09 02:30 PM
```

---

## Step 4: Start the Pipeline (2 minutes)

### 4.1 Run Sync Engine

**Option A: Windows**
```bash
start_nfl_sync.bat
```

**Option B: Command Line**
```bash
python src/nfl_realtime_sync.py
```

**Expected Output**:
```
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║       🏈 NFL REAL-TIME SYNC ENGINE 🏈                            ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝

Starting NFL real-time data pipeline...

Features:
- Live game scores (updates every 5 seconds)
- Play-by-play tracking
- Kalshi market monitoring
- Telegram notifications
- Injury reports

Press Ctrl+C to stop

2025-11-09 14:35:12 - INFO - NFL Real-Time Sync initialized (update interval: 5s)
2025-11-09 14:35:12 - INFO - Starting NFL real-time sync engine...
2025-11-09 14:35:15 - INFO - Live games sync: 0 inserted, 12 updated, 1 API calls
```

### 4.2 Verify It's Working

You should receive a Telegram message:
```
🏈 NFL Real-Time Sync Started

Update Interval: 5s
Monitoring live games and Kalshi markets...
```

Check the database:
```bash
psql -U postgres -d magnus -c "SELECT COUNT(*) FROM nfl_games"
```

---

## Step 5: Monitor & Configure (2 minutes)

### 5.1 View Live Games (if any)

```bash
psql -U postgres -d magnus -c "SELECT * FROM v_nfl_live_games"
```

### 5.2 Configure Alerts

Edit `config/nfl_pipeline.yaml` to customize:

```yaml
alerts:
  triggers:
    score_change:
      enabled: true
      teams_filter: ["Chiefs", "Bills"]  # Only alert for these teams

    price_movement:
      thresholds:
        min_price_change_pct: 15  # Only alert on 15%+ spikes
```

**Restart the sync engine** after changing config:
```bash
# Press Ctrl+C to stop
# Run start_nfl_sync.bat again
```

### 5.3 Check Logs

```bash
type logs\nfl_pipeline.log  # Windows
tail -f logs/nfl_pipeline.log  # Linux/Mac
```

---

## What Happens During a Live Game?

Here's what you'll see when a game is live:

### 1. Score Update Alert

When a team scores:
```
🏈 SCORE UPDATE

Kansas City Chiefs 24 @ Denver Broncos 17

🎯 Chiefs score 7 points!
⏱️ Q3 - 8:24
```

### 2. Kalshi Price Spike Alert

When Kalshi market reacts:
```
📈 KALSHI PRICE MOVEMENT

Will the Chiefs win this game?

Price: 0.67 → 0.78 (+16.4%)
Volume: $45,230
Ticker: NFL-KC-WIN-20251109
```

### 3. Injury Alert

When a key player is injured:
```
🚑 INJURY UPDATE

Patrick Mahomes (QB)
Team: Kansas City Chiefs
Status: Questionable
Injury: Ankle

Mahomes left the game in Q2 with an ankle injury. Return is questionable.
```

### 4. Database Updates

Every 5 seconds:
```sql
-- Check latest updates
SELECT
    away_team,
    home_team,
    away_score,
    home_score,
    quarter,
    time_remaining,
    last_updated
FROM nfl_games
WHERE is_live = true
ORDER BY last_updated DESC;
```

---

## Troubleshooting

### Issue: "No module named 'nfl_data_fetcher'"

**Solution**:
```bash
# Make sure you're in the project directory
cd c:/Code/WheelStrategy

# Run with explicit path
python c:/Code/WheelStrategy/src/nfl_realtime_sync.py
```

### Issue: "Kalshi login failed"

**Solution**:
1. Check credentials in `.env`
2. Verify account is not locked
3. Test manually:
   ```bash
   python src/kalshi_client.py
   ```

### Issue: "Database connection failed"

**Solution**:
```bash
# Check PostgreSQL is running
psql -U postgres -c "SELECT 1"

# Verify DB_PASSWORD in .env
echo %DB_PASSWORD%  # Windows
echo $DB_PASSWORD   # Linux/Mac

# Test connection
psql -U postgres -d magnus -c "SELECT COUNT(*) FROM nfl_games"
```

### Issue: "No live games found"

**Cause**: NFL games only occur:
- Regular season: September - December
- Playoffs: January
- Super Bowl: Early February
- Sunday: 1pm ET, 4pm ET, 8pm ET
- Monday: 8pm ET
- Thursday: 8pm ET

**Solution**: Wait for game day, or test with historical data:
```bash
# Fetch a specific past date
python -c "
from nfl_data_fetcher import NFLDataFetcher
fetcher = NFLDataFetcher()
scoreboard = fetcher.get_scoreboard('20240908')  # Sept 8, 2024 (Week 1)
print(f'Found {len(scoreboard.get(\"events\", []))} games')
"
```

### Issue: "Telegram alerts not sending"

**Solution**:
```bash
# Test Telegram connection
python -c "from telegram_notifier import TelegramNotifier; TelegramNotifier().test_connection()"

# Check .env
type .env | findstr TELEGRAM  # Windows
cat .env | grep TELEGRAM      # Linux/Mac

# Verify bot token
# Should look like: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz
```

---

## Performance Expectations

### Normal Operation

**CPU Usage**: 5-10% (during live games)
**RAM Usage**: 200-500 MB
**Database Size**: ~1 GB per season
**API Calls**:
- ESPN: ~12 calls/minute (1 per live game per 5 seconds)
- Kalshi: ~20 calls/minute
- Weather: ~2 calls/hour

### During Peak (16 simultaneous games)

**CPU Usage**: 20-30%
**RAM Usage**: 1-2 GB
**API Calls**:
- ESPN: ~200 calls/minute
- Kalshi: ~50 calls/minute

---

## Next Steps

### Recommended Enhancements

1. **Create Alert Triggers**
   ```sql
   INSERT INTO nfl_alert_triggers (
       alert_name, alert_type, trigger_conditions,
       teams_filter, notification_priority
   ) VALUES (
       'Chiefs Touchdown Alert',
       'score_change',
       '{"min_points": 6}',
       ARRAY['Kansas City Chiefs'],
       'high'
   );
   ```

2. **View Historical Data**
   ```sql
   -- See all scoring plays
   SELECT * FROM v_nfl_significant_plays
   WHERE is_scoring_play = true
   ORDER BY created_at DESC
   LIMIT 20;

   -- Kalshi correlations
   SELECT * FROM nfl_kalshi_correlations
   WHERE price_change_pct > 10
   ORDER BY event_timestamp DESC;
   ```

3. **Create Custom Dashboard**
   ```bash
   # Add to dashboard.py
   streamlit run dashboard.py
   ```

4. **Schedule Automatic Start**
   - Windows: Task Scheduler
   - Linux: systemd service (see architecture docs)

---

## Support

**Common Commands**:
```bash
# Start sync
start_nfl_sync.bat

# Stop sync
Ctrl+C

# Check database
psql -U postgres -d magnus

# View logs
type logs\nfl_pipeline.log

# Test components
python src/nfl_data_fetcher.py
python src/nfl_db_manager.py
```

**Need Help?**
- Check `docs/NFL_PIPELINE_ARCHITECTURE.md` for detailed documentation
- Review logs in `logs/nfl_pipeline.log`
- Test individual components with the test scripts above

---

**You're all set! 🚀**

The pipeline will now:
- ✅ Monitor live NFL games every 5 seconds
- ✅ Track Kalshi market prices
- ✅ Send Telegram alerts for significant events
- ✅ Store all data in PostgreSQL for analysis

Enjoy your real-time NFL data pipeline!
