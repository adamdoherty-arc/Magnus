# Telegram Bot Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Test the Fixes (1 minute)
```bash
python test_telegram_bot_fixes.py
```

This will verify all 8 query handlers are working:
- ✅ Portfolio queries
- ✅ Xtrades alerts
- ✅ Position listings
- ✅ CSP opportunities
- ✅ Top traders
- ✅ Trader-specific queries
- ✅ Market updates
- ✅ Default greeting

### Step 2: Start Background Sync (30 seconds)
```bash
# Windows - just double-click
run_xtrades_sync.bat

# Or run manually
python src/ava/xtrades_background_sync.py
```

The service will:
- Sync all active Xtrades profiles every 5 minutes
- Log operations to database
- Handle errors gracefully
- Show real-time progress

### Step 3: Run the Telegram Bot (30 seconds)
```bash
python src/ava/telegram_bot_enhanced.py
```

### Step 4: Test in Telegram (2 minutes)

Send these voice messages to your bot:

**Test 1: Portfolio**
🎤 "How's my portfolio?"

Expected: Real balance from `portfolio_balances` table

**Test 2: Alerts**
🎤 "Any new alerts?"

Expected: Recent Xtrades alerts from last 24 hours

**Test 3: Positions**
🎤 "Show my positions"

Expected: Current Robinhood holdings

**Test 4: CSP Opportunities**
🎤 "Any CSP opportunities?"

Expected: Top 5 CSP opportunities from scanner

**Test 5: Top Traders**
🎤 "Who are the top traders?"

Expected: List of followed traders with trade counts

**Test 6: Specific Trader**
🎤 "Show me trades from behappy"

Expected: Recent trades from behappy

## 📊 What Got Fixed

### ❌ BEFORE (Broken)
```
User: "How's my portfolio?"
Bot: ❌ Error: cannot access local variable 'cursor'

User: "Any alerts?"
Bot: "No urgent alerts" (hardcoded placeholder)

Background Sync: ❌ Not implemented
```

### ✅ AFTER (Working)
```
User: "How's my portfolio?"
Bot: "Your portfolio balance is $45,234.67 as of 02:30 PM.
      Portfolio up 3.2% today with strong performance."

User: "Any alerts?"
Bot: "📊 Latest Xtrades Alerts (5 in last 24h):
      🔔 behappy: BTO NVDA (CSP) $140 11/15 @ $2.85 (01:45 PM)
      🔔 optionsguru: STC TSLA (CC) $250 11/22 @ $3.20..."

Background Sync: ✅ Running every 5 minutes automatically
```

## 🔧 Files Changed

1. **c:\Code\WheelStrategy\src\ava\voice_handler.py**
   - Fixed: `_handle_portfolio_query()` - Now uses direct psycopg2
   - Fixed: `_handle_alerts()` - Real database queries
   - Added: `_handle_positions_query()` - Robinhood positions
   - Added: `_handle_csp_opportunities()` - CSP scanner results
   - Added: `_handle_top_traders()` - Top followed traders
   - Added: `_handle_trader_specific()` - Specific trader trades
   - Enhanced: Natural language processing

2. **c:\Code\WheelStrategy\src\ava\xtrades_background_sync.py** (NEW)
   - Background sync service
   - 5-minute automatic updates
   - Database logging
   - Error handling

3. **c:\Code\WheelStrategy\run_xtrades_sync.bat** (NEW)
   - Windows launcher
   - Easy one-click startup
   - Automatic dependency check

4. **c:\Code\WheelStrategy\TELEGRAM_BOT_FIXES.md** (NEW)
   - Complete documentation
   - Example outputs
   - Troubleshooting guide

5. **c:\Code\WheelStrategy\test_telegram_bot_fixes.py** (NEW)
   - Test suite for all handlers
   - Verification script

## 🎯 Key Features Implemented

### 1. Direct PostgreSQL Connections
All handlers use `psycopg2.connect()` with proper try/finally blocks:
```python
conn = psycopg2.connect(os.getenv("DATABASE_URL"))
cursor = conn.cursor()
try:
    cursor.execute("SELECT ...")
    result = cursor.fetchall()
finally:
    cursor.close()
    conn.close()
```

### 2. Real Database Queries
- Portfolio: `SELECT * FROM portfolio_balances`
- Alerts: `SELECT * FROM xtrades_trades JOIN xtrades_profiles`
- Positions: `SELECT * FROM rh_positions`
- CSP: `SELECT * FROM csp_opportunities`
- Traders: `SELECT * FROM xtrades_profiles`

### 3. Background Sync Service
- Automatic updates every 5 minutes
- Syncs all active profiles
- Logs to `xtrades_sync_log` table
- Error recovery
- Performance tracking

### 4. Enhanced NLP
Bot now understands:
- Portfolio: "balance", "account", "p&l", "portfolio"
- Positions: "positions", "holdings", "what do i own"
- Alerts: "alerts", "xtrades", "notifications"
- CSP: "csp", "opportunities", "sell put"
- Traders: "top traders", "who", "from [name]"

## 🛠️ Troubleshooting

### No Alerts Showing?
```sql
-- Check if profiles are active
SELECT * FROM xtrades_profiles WHERE active = TRUE;

-- Activate a profile
UPDATE xtrades_profiles SET active = TRUE WHERE username = 'behappy';
```

### Database Connection Error?
```bash
# Test connection
psql -U postgres -d magnus -c "SELECT 1;"

# Check .env file
cat .env | grep DATABASE_URL
```

### Background Sync Not Working?
```bash
# Check sync logs
psql -U postgres -d magnus -c "SELECT * FROM xtrades_sync_log ORDER BY sync_timestamp DESC LIMIT 5;"

# Run manual sync
python src/ava/xtrades_background_sync.py --once
```

## 📈 Monitoring

### View Recent Syncs
```sql
SELECT
    sync_timestamp,
    profiles_synced,
    new_trades,
    duration_seconds,
    status
FROM xtrades_sync_log
ORDER BY sync_timestamp DESC
LIMIT 10;
```

### View Recent Alerts
```sql
SELECT
    p.username,
    t.ticker,
    t.action,
    t.strategy,
    t.alert_timestamp
FROM xtrades_trades t
JOIN xtrades_profiles p ON t.profile_id = p.id
WHERE t.alert_timestamp > NOW() - INTERVAL '24 hours'
ORDER BY t.alert_timestamp DESC;
```

## ✅ Success Checklist

- [ ] Test script runs successfully
- [ ] Background sync is running
- [ ] Telegram bot is running
- [ ] Voice messages work
- [ ] Portfolio query returns real data
- [ ] Alerts show database records
- [ ] All 8 handlers work correctly

## 🎉 You're Ready!

Your Telegram bot now has:
- ✅ Working portfolio queries
- ✅ Real Xtrades alerts
- ✅ Automatic background sync
- ✅ 6+ query handlers
- ✅ Robust error handling
- ✅ Natural language processing

**Enjoy your fully functional AVA Telegram bot!** 🤖

---

**Need Help?**
- Documentation: `TELEGRAM_BOT_FIXES.md`
- Test Script: `python test_telegram_bot_fixes.py`
- Logs: `SELECT * FROM xtrades_sync_log;`
