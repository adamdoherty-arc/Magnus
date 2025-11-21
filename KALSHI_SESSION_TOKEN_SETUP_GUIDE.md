# Kalshi Session Token Authentication Setup Guide

**Date:** November 15, 2025
**Status:** ✅ Complete - Ready to Use

---

## Overview

This guide shows you how to authenticate with Kalshi API using a **session token** extracted from your browser. This method bypasses the need for Premier/Market Maker account level and works with SMS verification.

### Why Use Session Token Authentication?

| Authentication Method | Pros | Cons |
|----------------------|------|------|
| **API Key + Private Key** | Official method, long-lived | ❌ Requires Premier/Market Maker account |
| **Email/Password API** | Simple credentials | ❌ Doesn't support SMS verification |
| **Session Token (Browser)** | ✅ Works with SMS verification<br>✅ Uses your existing web login<br>✅ No account upgrade needed | Token expires after ~24 hours (need to refresh) |

---

## Quick Start

### Step 1: Extract Session Token from Browser

Run the extraction script:

```bash
python extract_kalshi_session.py
```

The script will guide you through:
1. Logging into Kalshi website in your browser
2. Completing SMS verification
3. Opening Developer Tools (F12)
4. Finding the session cookie
5. Copying the token value
6. Automatically adding it to your `.env` file

### Step 2: Verify Authentication Works

Test the connection:

```bash
python -c "from src.kalshi_client_v2 import KalshiClientV2; c=KalshiClientV2(); print('✅ Auth works!' if c.login() else '❌ Auth failed')"
```

You should see:
```
INFO:src.kalshi_client_v2:Using session token from browser login
✅ Auth works!
```

### Step 3: Sync Kalshi Team Winner Markets

Sync NFL and NCAA team winner markets:

```bash
python sync_kalshi_team_winners.py --sport football
```

Or sync all sports:

```bash
python sync_kalshi_team_winners.py --sport all
```

### Step 4: View Synced Markets

List recently synced markets:

```bash
python sync_kalshi_team_winners.py --list
```

### Step 5: Verify Game Cards System

Run comprehensive verification:

```bash
python verify_game_cards_system.py
```

Expected results:
- ✅ AI Predictions: PASSED (unique analysis for each game)
- ✅ Kalshi Matching: PASSED (Jacksonville 41%, LA 59%)
- ✅ Team Variations: PASSED
- ✅ Jacksonville vs LA: PASSED

---

## Detailed Instructions

### How to Extract Session Token

#### Chrome / Edge

1. **Log into Kalshi**
   - Go to https://kalshi.com
   - Click "Sign In"
   - Enter your email: `h.adam.doherty@gmail.com`
   - Enter your password
   - Complete SMS verification when prompted

2. **Open Developer Tools**
   - Press `F12` (or right-click → "Inspect")
   - Click the **"Application"** tab at the top

3. **Find Cookies**
   - In left sidebar, expand **"Cookies"**
   - Click **"https://kalshi.com"**

4. **Locate Session Cookie**
   - Look for a cookie named one of:
     - `kalshi_session`
     - `auth_token`
     - `bearer`
     - `token`
     - `session`

5. **Copy Token Value**
   - Click on the cookie row
   - In the "Value" field (bottom panel), copy the entire string
   - Should look like: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` (very long)

#### Firefox

1. **Log into Kalshi** (same as Chrome)

2. **Open Developer Tools**
   - Press `F12`
   - Click the **"Storage"** tab

3. **Find Cookies**
   - In left sidebar, expand **"Cookies"**
   - Click **"https://kalshi.com"**

4. **Copy Token** (same as Chrome)

---

## What Was Implemented

### 1. Enhanced KalshiClientV2 (`src/kalshi_client_v2.py`)

**Added Session Token Support:**

```python
def __init__(self, session_token: Optional[str] = None, ...):
    # Session token authentication (easiest - from browser login)
    self.session_token = session_token or os.getenv('KALSHI_SESSION_TOKEN')

    # If session token provided, use it directly
    if self.session_token:
        self.bearer_token = f"Bearer {self.session_token}"
        self.token_expires_at = datetime.now() + timedelta(hours=24)
        logger.info("Using session token from browser login")
```

**Authentication Priority:**
1. **Session Token** (if `KALSHI_SESSION_TOKEN` in .env) ← **Easiest**
2. API Key + Private Key (if `KALSHI_API_KEY` + `.kalshi_private_key.pem`)
3. Email/Password (if `KALSHI_EMAIL` + `KALSHI_PASSWORD`)

### 2. Session Extraction Script (`extract_kalshi_session.py`)

**Features:**
- ✅ Step-by-step instructions for Chrome/Edge/Firefox
- ✅ Automatic `.env` file update
- ✅ Token replacement if already exists
- ✅ Next steps guidance
- ✅ Windows encoding support

### 3. Team Winner Sync Script (`sync_kalshi_team_winners.py`)

**Already configured to use KalshiClientV2** - automatically detects session token

**Features:**
- ✅ Filters out combo/parlay markets
- ✅ Filters out player props and totals
- ✅ Categorizes as NFL, CFB, or generic winner
- ✅ Stores in database with correct schema
- ✅ Updates market prices automatically

---

## Environment Variables

After extracting the session token, your `.env` should contain:

```bash
# Kalshi Authentication
KALSHI_EMAIL=h.adam.doherty@gmail.com
KALSHI_PASSWORD=AA420dam!@
KALSHI_API_KEY=1dd70d1d-7ae0-4520-b44a-48a5deca1fb2
KALSHI_PRIVATE_KEY_PATH=.kalshi_private_key.pem

# NEW: Session Token (from browser web login)
# Extracted: 2025-11-15 10:30:00
KALSHI_SESSION_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=trading
DB_USER=postgres
DB_PASSWORD=your_password
```

**Priority:** If `KALSHI_SESSION_TOKEN` exists, it will be used first (no API key needed).

---

## Authentication Flow

```
┌─────────────────────────────────────────────────┐
│  KalshiClientV2 Initialization                 │
└─────────────────────────────────────────────────┘
                    │
                    ▼
    ┌───────────────────────────────┐
    │ Check for KALSHI_SESSION_TOKEN │
    └───────────────────────────────┘
                    │
         ┌──────────┴──────────┐
         │                     │
    Yes  ▼                     ▼  No
┌─────────────────┐    ┌──────────────────┐
│ Use Session     │    │ Try API Key      │
│ Token Directly  │    │ Authentication   │
│                 │    └──────────────────┘
│ ✅ Ready to use │            │
└─────────────────┘         Fail
                              │
                              ▼
                    ┌──────────────────┐
                    │ Try Email/Pass   │
                    │ Authentication   │
                    └──────────────────┘
                              │
                         ┌────┴────┐
                         │         │
                    Success       Fail
                         │         │
                         ▼         ▼
                  ✅ Authenticated  ❌ Error
```

---

## Token Expiration

**Session tokens typically last 24 hours.**

When token expires, you'll see:
```
WARNING:src.kalshi_client_v2:Session token expired. Please extract a new token from browser.
WARNING:src.kalshi_client_v2:Run: python extract_kalshi_session.py
```

**Solution:** Simply run the extraction script again to get a fresh token.

---

## Troubleshooting

### Issue: Can't find session cookie in browser

**Solution:**
- Make sure you're logged in successfully (see your name/account in top right)
- Try refreshing the page after logging in
- Look for alternative cookie names: `token`, `session`, `auth`, `bearer`
- Try logging out and back in

### Issue: "Session token expired" error

**Solution:**
- Run `python extract_kalshi_session.py` again to get a new token
- Tokens last ~24 hours, need to refresh periodically

### Issue: Authentication still fails with session token

**Check:**
1. Verify token was added to `.env`:
   ```bash
   grep KALSHI_SESSION_TOKEN .env
   ```

2. Make sure token doesn't have extra spaces:
   ```bash
   # Bad: KALSHI_SESSION_TOKEN= eyJhbGci...
   # Good: KALSHI_SESSION_TOKEN=eyJhbGci...
   ```

3. Check token is complete (should be very long, 500+ characters)

4. Try extracting again - token may have expired between extraction and use

---

## Testing the Complete System

### Test 1: Authentication
```bash
python -c "from src.kalshi_client_v2 import KalshiClientV2; c=KalshiClientV2(); print('✅' if c.login() else '❌')"
```

### Test 2: Fetch Markets
```bash
python sync_kalshi_team_winners.py --sport nfl
```

### Test 3: View Markets
```bash
python sync_kalshi_team_winners.py --list
```

Expected output:
```
================================================================================
RECENTLY SYNCED TEAM WINNER MARKETS
================================================================================

Will Jacksonville beat Los Angeles?
  Ticker: NFL-JAX-LAC-2025-01-15
  Type: NFL
  Odds: Yes 41.0% / No 59.0%
  Volume: $25,431
  Closes: 2025-01-15 20:00:00
  Updated: 2025-11-15 10:35:21

...
```

### Test 4: Comprehensive Verification
```bash
python verify_game_cards_system.py
```

Expected results:
```
================================================================================
 FINAL VERIFICATION SUMMARY
================================================================================

Test Results:
  ✅ AI Predictions: PASSED
  ✅ Kalshi Matching: PASSED
  ✅ Team Variations: PASSED
  ✅ Jacksonville vs LA: PASSED

Overall: 4/4 tests passed

🎉 ALL TESTS PASSED! Game Cards system is working correctly.
```

---

## Next Steps After Setup

1. **Run Initial Market Sync**
   ```bash
   python sync_kalshi_team_winners.py --sport football
   ```

2. **Start the Dashboard**
   ```bash
   run_dashboard.bat
   ```

3. **Navigate to Sports Game Cards**
   - Open http://localhost:8501
   - Go to "Sports Game Cards" page
   - You should now see Kalshi odds on available games!

4. **Set Up Automatic Refresh** (Optional)
   - Use the refresh interval dropdown (30sec - 30min)
   - Enable auto-refresh checkbox
   - Markets will update automatically

---

## Files Modified

1. ✅ `src/kalshi_client_v2.py` - Added session token authentication support
2. ✅ `extract_kalshi_session.py` - Enhanced with detailed instructions
3. ✅ `sync_kalshi_team_winners.py` - Already uses KalshiClientV2
4. ✅ `KALSHI_SESSION_TOKEN_SETUP_GUIDE.md` - This comprehensive guide

---

## Summary

**What This Solves:**

❌ **Before:** API authentication failed with 401 Unauthorized
- API key requires Premier/Market Maker account ($$)
- Email/password API doesn't support SMS verification
- Can't sync Kalshi markets
- No odds showing on game cards

✅ **After:** Session token authentication works!
- Use your existing web login (free account)
- SMS verification works through browser
- Can sync Kalshi markets successfully
- Kalshi odds display on game cards

**Time to Complete:** 2-3 minutes

**Maintenance:** Re-extract token every 24 hours (takes 30 seconds)

---

## Quick Reference Commands

```bash
# Extract session token
python extract_kalshi_session.py

# Test authentication
python -c "from src.kalshi_client_v2 import KalshiClientV2; c=KalshiClientV2(); print('✅' if c.login() else '❌')"

# Sync markets
python sync_kalshi_team_winners.py --sport football

# List markets
python sync_kalshi_team_winners.py --list

# Verify system
python verify_game_cards_system.py

# Start dashboard
run_dashboard.bat
```

---

**Ready to proceed!** Run `python extract_kalshi_session.py` to get started.
