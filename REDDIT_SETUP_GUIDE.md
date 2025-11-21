# Reddit API Setup - Quick Guide

## Getting Your Client ID

1. **Go to:** https://www.reddit.com/prefs/apps

2. **Look for your app** (or create one if you haven't):
   - Click "Create App" or "Create Another App"
   - Name: "Magnus Trading Research"
   - Type: Select "script"
   - Description: "AI research agent for trading platform"
   - Redirect URI: http://localhost:8080
   - Click "Create app"

3. **Find Your Credentials:**

```
Your app will look like this:

┌─────────────────────────────────────────┐
│  Magnus Trading Research                 │
│  [personal use script]                   │
│                                          │
│  YOUR_CLIENT_ID_HERE  ← This is Client ID (short string like "abc123xyz")
│                                          │
│  secret: Hxrx_WzunMh0pOdP9mnmSZGZnioD0Q │  ← This is what you have!
│                                          │
│  [edit] [delete]                         │
└─────────────────────────────────────────┘
```

4. **Add Both to .env:**

```bash
# Reddit API
REDDIT_CLIENT_ID=abc123xyz  # ← Short string from above
REDDIT_CLIENT_SECRET=Hxrx_WzunMh0pOdP9mnmSZGZnioD0Q  # ← You have this!
REDDIT_USER_AGENT=MagnusTradingPlatform/1.0
```

5. **Test it:**

```bash
python -c "import praw; r=praw.Reddit(client_id='YOUR_ID', client_secret='Hxrx_WzunMh0pOdP9mnmSZGZnioD0Q', user_agent='Magnus/1.0'); print('Success!' if r.read_only else 'Failed')"
```

## What You'll Be Able to Do

Once configured, the research agent will:
- Scan r/options, r/algotrading, r/thetagang, r/wallstreetbets
- Find interesting trading strategies and improvements
- AI-score relevance (0-100)
- Auto-add high-value findings (>80) to your enhancement database
- Autonomous agent will then implement them!

**Cost:** FREE! Reddit API is free for reasonable use (60 requests/minute).
