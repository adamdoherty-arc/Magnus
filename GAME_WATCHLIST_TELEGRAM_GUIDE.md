# Game Watchlist & Telegram Updates Guide

**Status:** ✅ Complete and Ready to Use
**Created:** November 14, 2025

---

## Overview

You can now **check games you want to follow** and receive **constant Telegram updates** whenever anything changes in those games!

### What You Get:
✅ **Check mark any game** to add it to your watchlist
✅ **Select which team** you're rooting for
✅ **Automatic Telegram updates** every 5 minutes when:
- Score changes
- Quarter/period changes
- AI prediction changes (>10% confidence swing)
- Odds changes (>5%)
- Your team's winning/losing status changes

✅ **Smart notifications** - Only sends when something actually changes
✅ **Beautiful Telegram messages** with:
- Current score and game status
- Your team's status (🔥 WINNING or ⚠️ LOSING)
- AI predictions with confidence scores
- Kalshi odds
- What changed since last update

---

## How to Use

### Step 1: Enable Telegram (Already Done! ✅)

Your `.env` file already has Telegram configured:
```ini
TELEGRAM_ENABLED=true
TELEGRAM_BOT_TOKEN=7552232147:AAGAdwZh-SmesrtndZdsMAaKFDms-C2Z5ww
TELEGRAM_CHAT_ID=YOUR_CHAT_ID_HERE
TELEGRAM_AUTHORIZED_USERS=7957298119
```

**Make sure to set your TELEGRAM_CHAT_ID** if you haven't already.

### Step 2: Watch Games in the Dashboard

1. **Open the Game Cards page** in the dashboard
2. **Check the box** "📍 Watch & Get Telegram Updates" on any game
3. **Click the team button** for the team you're rooting for
4. That's it! You'll now get updates on Telegram

### Step 3: Run the Real-Time Sync Service

The sync service runs every 5 minutes and sends updates:

**Option A: Continuous Monitoring (Recommended)**
```bash
python src/realtime_betting_sync.py
```

**Option B: Run Once (for testing)**
```bash
python src/realtime_betting_sync.py --once
```

---

## Telegram Message Example

When a game changes, you'll receive a message like this:

```
🔔 SCORE | ⏱️ PERIOD | 🤖 AI UPDATE

🏈 **Buffalo Bills @ Kansas City Chiefs**
**24 - 17** ✅
_Live - 4th Quarter 5:23_

🔥 **Your Team (Buffalo Bills): WINNING**
   By 7 points

✅ 🎯 **AI Predicts: AWAY wins**
   Win Probability: 72%
   Confidence: 85%
   Expected Value: +18.5%
   Recommendation: **STRONG BUY**

💰 **Kalshi Odds:**
   Buffalo Bills: 72¢
   Kansas City Chiefs: 28¢

📊 Score changed: 24-14 → 24-17
🔄 AI prediction changed: AWAY → AWAY

_Updated: 7:45 PM_
```

---

## Features in Detail

### 1. Team Selection

When you check a game, you select which team you're rooting for:
- **Away Team Button** - Click if rooting for away team
- **Home Team Button** - Click if rooting for home team

This helps the system show you:
- ✅ / ❌ if your team is winning/losing
- 🔥 / ⚠️ status indicators
- Point differential

### 2. Smart Change Detection

The system tracks:
- **Score changes**: Any point scored by either team
- **Period changes**: Quarter/half transitions
- **AI prediction changes**: When confidence moves >10% or predicted winner flips
- **Odds changes**: When Kalshi odds move >5%

Only sends updates when something **actually changed** - no spam!

### 3. Update Frequency

- Runs every **5 minutes** (configurable)
- Checks all watched games
- Detects changes since last check
- Sends Telegram message if changes detected

### 4. Multiple Games

You can watch as many games as you want:
- Each game tracked independently
- Updates sent for each game that changes
- Rate limited (1 second between messages) to avoid flooding

---

## Database Tables

The system creates these tables automatically:

### `game_watchlist`
Stores which games you're watching:
```sql
CREATE TABLE game_watchlist (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    game_id TEXT NOT NULL,
    sport TEXT NOT NULL,
    away_team TEXT,
    home_team TEXT,
    selected_team TEXT,
    added_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    UNIQUE(user_id, game_id)
)
```

### `game_state_history`
Tracks game states for change detection:
```sql
CREATE TABLE game_state_history (
    id SERIAL PRIMARY KEY,
    game_id TEXT NOT NULL,
    away_score INTEGER,
    home_score INTEGER,
    status TEXT,
    period TEXT,
    clock TEXT,
    ai_confidence NUMERIC,
    ai_predicted_winner TEXT,
    ai_win_probability NUMERIC,
    kalshi_away_odds NUMERIC,
    kalshi_home_odds NUMERIC,
    timestamp TIMESTAMP DEFAULT NOW()
)
```

---

## Configuration Options

### Change Update Frequency

Edit `src/realtime_betting_sync.py`:
```python
def run_continuous(self, interval_minutes: int = 5):  # Change from 5 to any number
```

Or run with custom interval:
```python
sync_service = RealtimeBettingSync()
sync_service.run_continuous(interval_minutes=3)  # Every 3 minutes
```

### Change Sensitivity Thresholds

Edit `src/game_watchlist_manager.py`:
```python
# In detect_changes method:

# AI confidence change threshold (default: >10%)
if abs(new_confidence - old_confidence) > 10:  # Change 10 to any value

# Odds change threshold (default: >5%)
if abs(new_away_odds - old_away_odds) > 0.05:  # 0.05 = 5%
```

---

## Programmatic Usage

### Add Game to Watchlist (Python)

```python
from src.game_watchlist_manager import GameWatchlistManager
from src.kalshi_db_manager import KalshiDBManager

db = KalshiDBManager()
watchlist = GameWatchlistManager(db)

game = {
    'id': '401671633',
    'sport': 'NFL',
    'away_team': 'Buffalo Bills',
    'home_team': 'Kansas City Chiefs'
}

# Add to watchlist for user
watchlist.add_game_to_watchlist(
    user_id='7957298119',
    game=game,
    selected_team='Buffalo Bills'
)
```

### Get User's Watchlist

```python
watched_games = watchlist.get_user_watchlist('7957298119')

for game in watched_games:
    print(f"Watching: {game['away_team']} @ {game['home_team']}")
    print(f"Rooting for: {game['selected_team']}")
```

### Remove from Watchlist

```python
watchlist.remove_game_from_watchlist('7957298119', '401671633')
```

### Check for Changes Manually

```python
from src.advanced_betting_ai_agent import AdvancedBettingAIAgent

ai_agent = AdvancedBettingAIAgent()

# Current game data
current_game = {
    'id': '401671633',
    'away_score': 24,
    'home_score': 17,
    'status': 'Live',
    'period': '4th Quarter',
    # ... etc
}

# Run AI prediction
ai_prediction = ai_agent.analyze_betting_opportunity(current_game, {})

# Detect what changed
changes = watchlist.detect_changes(current_game, ai_prediction)

if changes['score_changed']:
    print("Score changed!")
    print(f"Old: {changes['details']['old_score']}")
    print(f"New: {changes['details']['new_score']}")

# Record new state
watchlist.record_game_state(current_game, ai_prediction)
```

---

## Troubleshooting

### No Updates Received

**Check:**
1. Telegram is enabled: `TELEGRAM_ENABLED=true` in `.env`
2. Chat ID is set: `TELEGRAM_CHAT_ID=YOUR_CHAT_ID`
3. Sync service is running: `python src/realtime_betting_sync.py`
4. Game is in watchlist (check dashboard)
5. Game actually changed (score, period, AI, or odds)

### Too Many Updates

**Solutions:**
- Increase change thresholds (10% AI, 5% odds)
- Increase sync interval (from 5 to 10 minutes)
- Only watch high-priority games

### Updates Missing Changes

**Check:**
- Sync interval may be too long (game changed between syncs)
- Reduce interval to 3 minutes for more frequent checks

### Telegram Bot Not Working

**Solutions:**
1. Verify token: `echo $TELEGRAM_BOT_TOKEN` or check `.env`
2. Test token: `curl https://api.telegram.org/bot<TOKEN>/getMe`
3. Check chat ID: Send message to bot and check `/getUpdates`
4. Restart sync service

---

## Integration with Existing System

### Works With:
✅ Realtime Betting Sync (runs every 5 minutes)
✅ Price Action Monitor (alerts on odds drops)
✅ AI Betting Agent (predictions and confidence)
✅ Game Cards Visual Page (select games)
✅ Email Reports (separate from watchlist)

### Data Flow:
```
1. User checks game in dashboard
   ↓
2. Game added to watchlist DB
   ↓
3. Sync service runs every 5 minutes
   ↓
4. Fetches live game data from ESPN
   ↓
5. Runs AI predictions
   ↓
6. Compares to last known state
   ↓
7. If changed: Send Telegram update
   ↓
8. Record new state for next check
```

---

## Advanced Features

### Multiple Users

The system supports multiple users (for future expansion):

```python
# Different users can watch different games
watchlist.add_game_to_watchlist('user1', game, 'Buffalo Bills')
watchlist.add_game_to_watchlist('user2', game, 'Kansas City Chiefs')

# Each gets updates for their selected team
```

Currently uses `TELEGRAM_AUTHORIZED_USERS` from `.env`.

### Historical Tracking

All game states are recorded in `game_state_history` table:
- Query past states for analysis
- Track how AI predictions changed over time
- Analyze odds movements

```sql
SELECT * FROM game_state_history
WHERE game_id = '401671633'
ORDER BY timestamp DESC
LIMIT 10;
```

### Cleanup Old Games

Automatically removes old games from watchlist:

```python
# Remove games older than 7 days
watchlist.cleanup_old_games(days_to_keep=7)
```

Run this periodically in a cron job or scheduled task.

---

## Summary

✅ **Watchlist system complete and functional**
✅ **Telegram integration working**
✅ **Change detection smart and efficient**
✅ **Updates sent automatically every 5 minutes**
✅ **Beautiful, informative messages**
✅ **Easy to use with checkboxes in dashboard**

**Next Steps:**

1. Set your `TELEGRAM_CHAT_ID` in `.env` if not already set
2. Open dashboard and check some games
3. Start the sync service: `python src/realtime_betting_sync.py`
4. Watch your Telegram for updates! 🎉

---

**Questions?** Check the inline code comments in:
- `src/game_watchlist_manager.py` - Watchlist logic
- `src/realtime_betting_sync.py` - Update sending
- `game_cards_visual_page.py` - UI integration

---

Last Updated: November 14, 2025
