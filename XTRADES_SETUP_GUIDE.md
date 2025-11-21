# Xtrades Watchlist Scraping - Complete Setup Guide

## Overview

This system automatically scrapes trading alerts from Xtrades.net profiles and displays them in your Magnus dashboard. It logs in via Discord OAuth, scrapes alerts, stores them in PostgreSQL, and can send Telegram notifications.

**Key Features:**
- Discord OAuth authentication (automatic login)
- Multi-profile monitoring (add unlimited profiles)
- Automatic sync every 5 minutes
- Real-time alerts and position tracking
- Performance analytics by profile, strategy, and ticker

---

## Quick Start (5 Steps)

### Step 1: Configure Environment Variables

Edit your `.env` file and set these values:

```env
# Xtrades.net Login (Discord OAuth)
XTRADES_USERNAME=your_discord_email@example.com
XTRADES_PASSWORD=your_discord_password

# Optional: Telegram Notifications
TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN_HERE
TELEGRAM_CHAT_ID=YOUR_CHAT_ID_HERE
TELEGRAM_ENABLED=false  # Set to true to enable
```

**Finding Your Discord Credentials:**
1. These are your regular Discord account credentials
2. Use the email and password you use to log into Discord
3. The scraper uses Discord OAuth to log into Xtrades.net

### Step 2: Verify Database Connection

Run the test script to verify your database is set up:

```bash
python test_xtrades_complete.py
```

This will check:
- Database connection
- Profile management
- Discord login
- Profile scraping
- Data storage

**Expected Output:**
```
✅ PASS - DATABASE
✅ PASS - PROFILE
✅ PASS - LOGIN
✅ PASS - SCRAPING
✅ PASS - STORAGE
✅ PASS - RETRIEVAL
```

### Step 3: Add Profiles to Monitor

**Option A: Via Dashboard UI (Recommended)**

1. Run the dashboard:
   ```bash
   streamlit run dashboard.py
   ```

2. Navigate to: **Xtrades Watchlists → Manage Profiles**

3. Click "Add New Profile"
   - **Username**: `behappy` (or any Xtrades.net username)
   - **Display Name**: `BeHappy Trader` (optional)

4. Click "Sync Now" to test

**Option B: Via Script**

Run the helper script:
```bash
python add_behappy_profile_fixed.py
```

### Step 4: Set Up Automatic Sync (Windows Task Scheduler)

**Create Scheduled Task:**

1. Open Task Scheduler (Windows Key + search "Task Scheduler")

2. Click "Create Task" (not "Create Basic Task")

3. **General Tab:**
   - Name: `Xtrades Sync Service`
   - Description: `Syncs Xtrades.net profiles every 5 minutes`
   - Security Options: ✅ Run whether user is logged on or not
   - Configure for: Windows 10/11

4. **Triggers Tab:**
   - Click "New..."
   - Begin the task: `On a schedule`
   - Settings: `Daily`
   - Start: `9:00 AM` (before market open)
   - ✅ Repeat task every: `5 minutes`
   - For a duration of: `8 hours` (market hours)
   - ✅ Enabled

5. **Actions Tab:**
   - Click "New..."
   - Action: `Start a program`
   - Program/script: `C:\Code\WheelStrategy\xtrades_sync.bat`
   - Start in: `C:\Code\WheelStrategy`

6. **Conditions Tab:**
   - ✅ Start only if the following network connection is available: `Any connection`
   - ⬜ Uncheck "Start the task only if the computer is on AC power"

7. **Settings Tab:**
   - ✅ Allow task to be run on demand
   - ✅ Run task as soon as possible after a scheduled start is missed
   - If the task fails, restart every: `1 minute`, up to `3 times`
   - Stop the task if it runs longer than: `10 minutes`

8. Click "OK" and enter your Windows password if prompted

**Verify Task:**
```bash
# Test the task manually
schtasks /run /tn "Xtrades Sync Service"

# Check logs
type logs\xtrades_sync_%date:~10,4%%date:~4,2%%date:~7,2%.log
```

### Step 5: View Results in Dashboard

1. Start the dashboard:
   ```bash
   streamlit run dashboard.py
   ```

2. Go to: **Xtrades Watchlists**

3. You'll see tabs:
   - **Active Trades**: Current open positions
   - **Closed Trades**: Completed trades with P/L
   - **Performance Analytics**: Stats by profile, strategy, ticker
   - **Manage Profiles**: Add/edit/sync profiles
   - **Sync History**: View sync logs and errors
   - **Settings**: Configure sync intervals and notifications

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Xtrades.net Profiles                     │
│              (behappy, othertrader, etc.)                   │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ Discord OAuth Login
                            │ (xtrades_scraper.py)
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              Xtrades Sync Service                           │
│           (xtrades_sync_service.py)                         │
│                                                             │
│  • Logs in once per run                                    │
│  • Scrapes all active profiles                             │
│  • Parses alerts (CSP, CC, spreads, etc.)                 │
│  • Checks for duplicates                                   │
│  • Stores in database                                      │
│  • Sends Telegram notifications                            │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                PostgreSQL Database                          │
│                  (magnus database)                          │
│                                                             │
│  Tables:                                                    │
│  • xtrades_profiles - Monitored profiles                   │
│  • xtrades_trades - Trade data                             │
│  • xtrades_sync_log - Sync history                         │
│  • xtrades_notifications - Notification tracking           │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              Streamlit Dashboard UI                         │
│           (xtrades_watchlists_page.py)                      │
│                                                             │
│  • View active/closed trades                               │
│  • Filter by profile, strategy, ticker                     │
│  • Performance analytics                                   │
│  • Manage profiles                                         │
│  • Manual sync buttons                                     │
└─────────────────────────────────────────────────────────────┘
```

---

## Usage Examples

### Example 1: Monitor Multiple Traders

```python
from src.xtrades_db_manager import XtradesDBManager

db = XtradesDBManager()

# Add multiple profiles
profiles_to_add = [
    ('behappy', 'BeHappy Trader'),
    ('traderpro', 'Pro Trader'),
    ('options_guru', 'Options Guru')
]

for username, display_name in profiles_to_add:
    profile_id = db.add_profile(username, display_name)
    print(f"Added {username} (ID: {profile_id})")

# View all active profiles
active = db.get_active_profiles()
for profile in active:
    print(f"{profile['username']}: {profile['total_trades_scraped']} trades")
```

### Example 2: Analyze Performance by Profile

```python
from src.xtrades_db_manager import XtradesDBManager

db = XtradesDBManager()

# Get statistics for a profile
profile = db.get_profile_by_username('behappy')
stats = db.get_profile_stats(profile['id'])

print(f"Total Trades: {stats['total_trades']}")
print(f"Win Rate: {stats['win_rate']:.1f}%")
print(f"Total P/L: ${stats['total_pnl']:,.2f}")
print(f"Avg P/L: ${stats['avg_pnl']:,.2f}")

# Get best and worst trades
if stats['best_trade']:
    best = stats['best_trade']
    print(f"Best Trade: {best['ticker']} (+${best['pnl']:,.2f})")

if stats['worst_trade']:
    worst = stats['worst_trade']
    print(f"Worst Trade: {worst['ticker']} (${worst['pnl']:,.2f})")
```

### Example 3: Manual Sync (For Testing)

```python
from src.xtrades_scraper import XtradesScraper
from src.xtrades_db_manager import XtradesDBManager

# Initialize scraper and database
scraper = XtradesScraper(headless=False)  # Non-headless to see progress
db = XtradesDBManager()

try:
    # Login
    print("Logging in...")
    scraper.login()

    # Get profile
    profile = db.get_profile_by_username('behappy')

    # Scrape alerts
    print(f"Scraping {profile['username']}...")
    alerts = scraper.get_profile_alerts(profile['username'], max_alerts=50)

    print(f"Found {len(alerts)} alerts")

    # Store in database
    for alert in alerts:
        # Check for duplicate
        existing = db.find_existing_trade(
            profile['id'],
            alert['ticker'],
            alert['alert_timestamp']
        )

        if not existing:
            alert['profile_id'] = profile['id']
            trade_id = db.add_trade(alert)
            print(f"Added: {alert['ticker']} - {alert['strategy']}")

finally:
    scraper.close()
```

---

## Troubleshooting

### Issue: Login Fails

**Symptoms:**
```
❌ Login failed: Discord login button not found
```

**Solutions:**
1. Check credentials in `.env`:
   ```env
   XTRADES_USERNAME=your_discord_email
   XTRADES_PASSWORD=your_discord_password
   ```

2. Test with non-headless mode:
   ```python
   scraper = XtradesScraper(headless=False)
   ```
   Watch the browser to see where it fails

3. Clear cached cookies:
   ```bash
   # Delete cache directory
   rmdir /s %USERPROFILE%\.xtrades_cache
   ```

4. Verify Discord account works:
   - Log into Discord manually at discord.com
   - Log into Xtrades.net manually and verify Discord OAuth works

### Issue: No Alerts Found

**Symptoms:**
```
⚠️ No alerts found for username
```

**Solutions:**
1. Verify profile exists and is public:
   - Visit: https://app.xtrades.net/profile/behappy
   - Check if you can see alerts when logged in

2. Check if alerts tab is available:
   - Some profiles might not have alerts enabled
   - Try a different profile

3. Increase max_alerts:
   ```python
   alerts = scraper.get_profile_alerts('behappy', max_alerts=100)
   ```

4. Check scraper selectors:
   - Xtrades.net might have updated their HTML
   - Open an issue if selectors need updating

### Issue: Duplicate Detection Not Working

**Symptoms:**
```
Same trade appears multiple times in database
```

**Solutions:**
1. Check alert timestamps:
   ```python
   trade = db.get_trade_by_id(trade_id)
   print(trade['alert_timestamp'])
   ```

2. Adjust duplicate detection tolerance:
   - Currently uses 1-minute tolerance
   - Increase in `xtrades_db_manager.py` if needed

### Issue: Task Scheduler Not Running

**Symptoms:**
```
Sync logs not updating
```

**Solutions:**
1. Check task status:
   ```bash
   schtasks /query /tn "Xtrades Sync Service" /v /fo list
   ```

2. View last run result:
   - Open Task Scheduler
   - Find "Xtrades Sync Service"
   - Check "Last Run Result" (should be 0x0 for success)

3. Check logs:
   ```bash
   type logs\xtrades_sync_%date:~10,4%%date:~4,2%%date:~7,2%.log
   ```

4. Test manually:
   ```bash
   C:\Code\WheelStrategy\xtrades_sync.bat
   ```

---

## Advanced Configuration

### Custom Sync Schedule

Edit the trigger in Task Scheduler to customize sync frequency:

- **Every 10 minutes**: Repeat task every 10 minutes
- **Market hours only**: Set start time to 9:00 AM, duration 6.5 hours
- **After hours**: Create second task for 4:00 PM - 8:00 PM

### Headless vs. Non-Headless Mode

**Headless (Default for scheduled tasks):**
```python
scraper = XtradesScraper(headless=True)
```
- Faster execution
- Lower resource usage
- Runs in background
- Best for automation

**Non-Headless (Best for debugging):**
```python
scraper = XtradesScraper(headless=False)
```
- See browser in action
- Debug login issues
- Verify scraping works
- Manual intervention if needed

### Telegram Notifications

1. Create a Telegram bot:
   ```
   1. Message @BotFather on Telegram
   2. Send /newbot
   3. Follow instructions
   4. Copy bot token
   ```

2. Get your chat ID:
   ```
   1. Message @userinfobot
   2. Copy your chat ID
   ```

3. Update `.env`:
   ```env
   TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
   TELEGRAM_CHAT_ID=123456789
   TELEGRAM_ENABLED=true
   ```

4. Test notification:
   ```python
   from src.telegram_notifier import TelegramNotifier

   notifier = TelegramNotifier()
   notifier.send_message("Test notification from Magnus!")
   ```

---

## File Reference

### Core Files

- **`src/xtrades_scraper.py`**: Selenium scraper with Discord OAuth
- **`src/xtrades_db_manager.py`**: Database CRUD operations
- **`src/xtrades_schema.sql`**: Database schema definition
- **`xtrades_sync_service.py`**: Main sync service (runs every 5 min)
- **`xtrades_sync.bat`**: Windows batch file for Task Scheduler
- **`xtrades_watchlists_page.py`**: Streamlit UI page
- **`src/telegram_notifier.py`**: Telegram notification integration

### Helper Scripts

- **`add_behappy_profile_fixed.py`**: Add default profile
- **`test_xtrades_complete.py`**: Complete system test
- **`test_xtrades_behappy.py`**: Quick behappy profile test
- **`cleanup_xtrades_dummy_data.py`**: Clean test data

### Documentation

- **`XTRADES_SETUP_GUIDE.md`**: This file
- **`XTRADES_IMPLEMENTATION_PLAN.md`**: Original implementation plan
- **`XTRADES_SYNC_README.md`**: Sync service documentation
- **`docs/XTRADES_SCRAPER.md`**: Scraper technical docs

---

## Support & Contributing

### Getting Help

1. Check troubleshooting section above
2. Review error logs in `logs/` directory
3. Run test scripts to identify issues
4. Check database connection and credentials

### Reporting Bugs

When reporting issues, include:
- Error message and stack trace
- Relevant log entries from `logs/xtrades_sync_*.log`
- Steps to reproduce
- Environment (Windows version, Python version)

### Future Enhancements

Potential features to add:
- Email notifications
- Discord webhook integration
- Web dashboard for mobile
- Real-time WebSocket updates
- Machine learning for trade prediction
- Historical backtesting tools

---

## License & Disclaimer

**Educational Purposes Only**

This software is provided for educational and research purposes. Trading options involves substantial risk. Past performance does not guarantee future results. Always do your own research before making trading decisions.

**Rate Limiting**

Be respectful of Xtrades.net servers:
- Default sync interval: 5 minutes
- Don't scrape more frequently than necessary
- Use headless mode for scheduled tasks
- Cache session cookies to reduce login frequency

---

## Summary

You now have a complete automated system for:
1. ✅ Monitoring multiple Xtrades.net profiles
2. ✅ Automatic Discord OAuth login
3. ✅ Scraping alerts every 5 minutes
4. ✅ Storing data in PostgreSQL
5. ✅ Viewing in Streamlit dashboard
6. ✅ Optional Telegram notifications

**Next Steps:**
1. Run `python test_xtrades_complete.py` to verify setup
2. Add profiles via dashboard UI
3. Set up Windows Task Scheduler for automatic sync
4. Monitor results in Xtrades Watchlists page

Happy trading! 🚀
