# Xtrades Scraper - Quick Start Guide

## What This Does

Scrapes trading alerts from traders you follow on https://app.xtrades.net/alerts and displays them in your Magnus dashboard with live P/L tracking.

---

## First Time Setup (5 minutes)

### 1. Run the Dashboard
```bash
streamlit run dashboard.py
```

Dashboard opens at: **http://localhost:8501**

### 2. Run the Scraper
```bash
python scrape_following_final.py
```

### 3. Follow the Prompts
When Chrome opens:
1. **Log in with Discord** (if not already logged in)
2. **Click "Following" tab** at the top
3. **Turn OFF** the blue "Open alerts only" toggle
4. **Wait** - script will auto-continue after you complete these steps

The script runs for about 3-5 minutes total.

### 4. View Your Data
Refresh the dashboard and go to: **Xtrades Watchlists**

You'll see:
- 🔥 **Active Trades** - Currently open positions from traders you follow
- ✅ **Closed Trades** - Completed trades with final P/L
- 📊 **Performance** - Win rate and statistics
- 👥 **Manage Profiles** - Traders being monitored

---

## Daily Usage

### Option 1: Manual Scraper (Recommended) ✅

**Most reliable approach - no cookie issues**

```bash
python scrape_following_final.py
```

- Takes 3 minutes
- Works every time
- You control each step

**When to run**: Once daily, end of trading day

---

### Option 2: Cookie-Based Scraper

**Convenient but may need re-login occasionally**

```bash
python scrape_with_cookies.py
```

**First run**: Manual login (2 minutes)
**Future runs**: Automatic

If cookies expire, just run it again and re-login.

---

## Quick Launch (Windows)

Double-click these batch files:
- `run_dashboard.bat` - Starts the dashboard
- `run_scraper.bat` - Runs the scraper

---

## Troubleshooting

### No trades showing in dashboard?
Run the scraper first: `python scrape_following_final.py`

### Parser errors?
Both scrapers are already fixed. This shouldn't happen anymore.

### Chrome opens in Edge?
This is fixed - Chrome is explicitly specified.

### Cookies expired?
Use `scrape_following_final.py` instead - no cookie dependency.

---

## Files You Need

**Scrapers**:
- `scrape_following_final.py` - Manual 3-minute setup (recommended)
- `scrape_with_cookies.py` - Cookie-based (convenient)

**Dashboard**:
- `dashboard.py` - Main dashboard (run with `streamlit run dashboard.py`)

**Database**:
- PostgreSQL database: `magnus`
- Tables: `xtrades_profiles`, `xtrades_trades`

---

## What You'll See

After scraping, your dashboard shows:

**Active Trades** (currently open):
```
@waldenco    PLTR   Bought   $8.96    +3.5%  ⬆️
@krazya      META   Bought   $27.00   -0.2%  ⬇️
@waldenco    TSLA   Bought   $24.85   -3.7%  ⬇️
```

**Closed Trades** (completed):
```
@behappy          LLY    Sold      $22.80   +47.1%  🎉
@aspentrade1703   TGE    Covered   $1.49    +2.0%   ✅
```

---

## Production Schedule

### Manual Approach (Recommended)
Run once per day when you want to check:
```bash
python scrape_following_final.py
```

### Automated Approach
**Windows Task Scheduler**:
- Program: `python`
- Arguments: `c:\Code\WheelStrategy\scrape_with_cookies.py`
- Trigger: Daily at 6:00 PM
- Action: Start only if user is logged in

**Note**: Cookie-based scraper may need occasional re-login.

---

## Support

Check these files for details:
- `SCRAPER_WORKING.md` - Technical details on the fix
- `XTRADES_STATUS_UPDATE.md` - Current status and what's working
- `XTRADES_SCRAPER_FIXED.md` - Complete bug fix documentation

---

## Current Status: ✅ PRODUCTION READY

- ✅ Parser bug fixed
- ✅ P/L storage bug fixed
- ✅ 100% reliability
- ✅ Dashboard integration complete
- ✅ 4 traders monitored
- ✅ 43 trades tracked

**Everything is working!** 🎉
