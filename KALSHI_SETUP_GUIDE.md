# Kalshi Integration - Complete Setup Guide

**Quick Setup Time:** 10 minutes
**Difficulty:** Easy
**Status:** Required for betting market data

---

## Why Setup Kalshi?

**Currently:** ESPN live scores only (working great!)
**With Kalshi:** Real betting markets + AI predictions + win probabilities

**What You Get:**
- Real-time betting odds
- Market liquidity data
- AI-powered predictions
- Expected value calculations
- Edge analysis
- Historical accuracy tracking

---

## Step 1: Create Kalshi Account (5 minutes)

### Option A: Demo Account (Recommended for Testing)

1. Visit https://demo.kalshi.com
2. Click "Sign Up"
3. Use any email/password (no verification needed)
4. Done! You can browse markets immediately

### Option B: Real Account (For Real Trading)

1. Visit https://kalshi.com
2. Click "Sign Up"
3. Provide:
   - Email address
   - Strong password
   - Phone number
4. Verify email (check inbox)
5. Complete KYC if trading (ID verification)

**Cost:** Free to browse, deposits optional

---

## Step 2: Add Credentials to .env (2 minutes)

### Windows

```bash
# Open .env file in notepad
notepad .env
```

### Add These Lines

Scroll to the bottom and add:

```ini
# Kalshi API Configuration
KALSHI_EMAIL=your@email.com
KALSHI_PASSWORD=your_password
```

**Replace** `your@email.com` and `your_password` with your actual credentials.

**Save and close** the file.

### Verify

```bash
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('Email:', os.getenv('KALSHI_EMAIL')); print('Password:', 'SET' if os.getenv('KALSHI_PASSWORD') else 'NOT SET')"
```

**Expected Output:**
```
Email: your@email.com
Password: SET
```

---

## Step 3: Test Connection (1 minute)

```bash
python -c "
from src.kalshi_integration import KalshiIntegration

print('Testing Kalshi connection...')
kalshi = KalshiIntegration()
markets = kalshi.get_markets(limit=5, status='active')
print(f'[OK] Connected! Found {len(markets)} sample markets')

if markets:
    print('\nSample market:')
    m = markets[0]
    print(f'  Title: {m.get(\"title\", \"N/A\")}')
    print(f'  Ticker: {m.get(\"ticker\", \"N/A\")}')
    print(f'  Status: {m.get(\"status\", \"N/A\")}')
"
```

**Expected Output:**
```
Testing Kalshi connection...
[OK] Connected! Found 5 sample markets

Sample market:
  Title: Will...
  Ticker: NFLGAME-...
  Status: active
```

**If you see an error:**
- Check email/password are correct
- Verify .env file saved properly
- Try demo account if real account has issues

---

## Step 4: Sync Markets (2 minutes)

### Option A: Quick Sync (Recommended)

```bash
python pull_nfl_games.py
```

**What it does:**
- Fetches all NFL markets from Kalshi
- Fetches all NCAA markets (if available)
- Stores in database
- Generates AI predictions

**Expected Output:**
```
================================================================================
KALSHI NFL GAMES - AI-POWERED ANALYSIS
================================================================================
Started: 2025-11-14 16:00:00

[1/6] Initializing components...
    [OK] API client ready
    [OK] Database ready
    [OK] AI evaluator ready

[2/6] Fetching markets from Kalshi...
    [OK] Retrieved 500 total active markets

[3/6] Filtering for football markets...
    [OK] Found 150 NFL markets
    [OK] Found 25 college football markets

[4/6] Storing markets in database...
    [OK] Stored 150 NFL markets
    [OK] Stored 25 college markets

[5/6] Running AI predictions...
    [OK] Analyzing 175 active markets
    [OK] Generated 175 predictions

[6/6] Completed
    Success! Data ready for dashboard
```

**Time:** 2-3 minutes depending on # of markets

---

### Option B: Complete Sync (All Sports)

```bash
python sync_kalshi_complete.py
```

Syncs NFL + NCAA + all other Kalshi markets.

---

### Option C: Via Dashboard UI

1. Open dashboard: http://localhost:8501
2. Navigate to "Prediction Markets" page
3. Click "🔄 Sync Kalshi Markets"
4. Wait for progress bar
5. Done!

---

## Step 5: Verify Data (1 minute)

```bash
python -c "
from src.kalshi_db_manager import KalshiDBManager

db = KalshiDBManager()
conn = db.get_connection()
cur = conn.cursor()

# Check markets
cur.execute(\"SELECT COUNT(*) FROM kalshi_markets WHERE status = 'active'\")
markets = cur.fetchone()[0]

# Check predictions
cur.execute('SELECT COUNT(*) FROM kalshi_predictions')
predictions = cur.fetchone()[0]

print('='*80)
print('DATABASE STATUS')
print('='*80)
print(f'Active markets: {markets:,}')
print(f'AI predictions: {predictions:,}')

if markets > 0:
    print('\n[OK] Kalshi data ready!')
else:
    print('\n[WARNING] No markets found. Try syncing again.')

cur.close()
conn.close()
print('='*80)
"
```

**Expected Output:**
```
================================================================================
DATABASE STATUS
================================================================================
Active markets: 175
AI predictions: 175

[OK] Kalshi data ready!
================================================================================
```

---

## Step 6: View in Dashboard

1. Open http://localhost:8501
2. Navigate to "🏟️ Sports Game Cards"
3. Click "NFL" tab

**You should see:**
```
✅ Found 150 NFL game markets from Kalshi

[Grid of NFL games with:]
- Team logos
- Win probabilities
- Expected value (EV)
- Edge analysis
- Confidence scores
- AI reasoning
```

---

## Troubleshooting

### Error: "Invalid credentials"

**Problem:** Email or password incorrect

**Solution:**
1. Double-check .env file
2. Try logging into Kalshi website with same credentials
3. If website works, .env has a typo
4. Re-save .env and restart Python

---

### Error: "Connection timeout"

**Problem:** Network issue or Kalshi API down

**Solution:**
1. Check internet connection
2. Visit https://status.kalshi.com
3. Try again in 5 minutes
4. Use demo.kalshi.com if main site down

---

### Error: "No markets found"

**Problem:** Either no markets active or sync failed

**Solution:**
1. Run sync again: `python pull_nfl_games.py`
2. Check Kalshi website - do they have NFL markets?
3. It might be off-season (normal)
4. ESPN data still works without Kalshi!

---

### AI Predictions Look Wrong

**Problem:** Unrealistic confidence scores or edges

**Current State:**
- Database has player prop parlays
- AI evaluator designed for simple team markets
- Mismatch causes unrealistic predictions

**Solution:**
- This is known and documented
- ESPN data is accurate and reliable
- Kalshi markets are real but AI evaluation needs tuning
- See [SYSTEM_STATUS_REVIEW.md](SYSTEM_STATUS_REVIEW.md) for details

**Options:**
1. Use ESPN data only (current, works great)
2. Wait for Kalshi team-based markets
3. Contribute to AI evaluator improvements

---

## What Data Looks Like

### ESPN Data (Current - Always Works)

```
NFL Games:
  Buffalo Bills @ Kansas City Chiefs
  Live Score: 21-17 (Q3 2:45)
  TV: CBS
  Venue: Arrowhead Stadium
```

### Kalshi Market (After Setup)

```
Market: Will Buffalo beat Kansas City?
Yes Price: $0.45 (45% implied probability)
No Price: $0.55 (55% implied probability)
Volume: 12,450 contracts
Open Interest: 8,200

AI Analysis:
  Predicted: YES
  Confidence: 62%
  Edge: +12%
  EV: +8.5%
  Reasoning: Buffalo's defense trending up, KC injuries...
```

---

## Automated Sync (Optional)

### Windows Task Scheduler

Create a batch file `sync_kalshi_daily.bat`:

```batch
@echo off
cd C:\Code\Legion\repos\ava
call venv\Scripts\activate
python sync_kalshi_complete.py
```

Schedule to run daily at 8am:
1. Open Task Scheduler
2. Create Basic Task
3. Name: "Kalshi Daily Sync"
4. Trigger: Daily, 8:00 AM
5. Action: Start Program
6. Program: `C:\Code\Legion\repos\ava\sync_kalshi_daily.bat`
7. Done!

---

### Linux/Mac Cron

Add to crontab:

```cron
0 8 * * * cd /path/to/ava && ./venv/bin/python sync_kalshi_complete.py
```

---

## API Rate Limits

**Kalshi Limits:**
- 60 requests/minute (free tier)
- 300 requests/minute (with trading activity)

**Our Implementation:**
- Built-in rate limiting
- Automatic retry with backoff
- Won't exceed limits

---

## Security Best Practices

### ✅ DO:
- Use strong password
- Enable 2FA on Kalshi account
- Keep .env file private
- Use .gitignore (already configured)

### ❌ DON'T:
- Commit .env to git
- Share credentials
- Use same password as other sites
- Store in plain text elsewhere

---

## Cost

**Kalshi Account:**
- Free to browse markets
- No cost for API access
- Only pay if you trade

**Trading (Optional):**
- Deposit money to trade
- Buy contracts at market price
- Profit/loss based on outcomes
- $1 max price per contract

**Our App:**
- Free to use
- No hidden costs
- API calls are free

---

## Support

### Kalshi Support
- Email: support@kalshi.com
- Discord: https://discord.gg/kalshi
- Help Center: https://help.kalshi.com

### Technical Issues
- Check [SYSTEM_STATUS_REVIEW.md](SYSTEM_STATUS_REVIEW.md)
- Review error messages
- Test with demo account first

---

## Summary Checklist

- [ ] Create Kalshi account
- [ ] Add credentials to .env
- [ ] Test connection
- [ ] Run sync script
- [ ] Verify data in database
- [ ] View in dashboard
- [ ] (Optional) Set up automated sync

**Time:** 10 minutes total
**Difficulty:** Easy
**Result:** Full betting market integration!

---

## Next Steps

After setup:
1. Explore Prediction Markets page
2. Review AI predictions
3. Test game cards with Kalshi data
4. Set up automated daily sync
5. Monitor accuracy over time

---

**Last Updated:** November 14, 2025
**Status:** Ready to use
**Questions?** See [SYSTEM_STATUS_REVIEW.md](SYSTEM_STATUS_REVIEW.md)
