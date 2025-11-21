# AVA Enhanced Telegram Bot - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies
```bash
pip install python-telegram-bot matplotlib numpy psycopg2-binary
```

### Step 2: Run the Bot
```bash
python src/ava/telegram_bot_enhanced.py
```

You should see:
```
╔══════════════════════════════════════════════════════════════════╗
║       🤖 AVA Telegram Bot - Enhanced Production Version 🤖       ║
╚══════════════════════════════════════════════════════════════════╝

AVA is connecting to Telegram...
✅ AVA Telegram Bot is running!
```

### Step 3: Get Your User ID
1. Open Telegram
2. Find your AVA bot
3. Send: `/start`
4. You'll receive:
```
👋 Hi [Your Name]!

I'm AVA (Automated Vector Agent)...

Your Chat ID: 123456789
Your User ID: 123456789
Status: 🚫 Unauthorized
```

5. **Copy your User ID** (the number shown)

### Step 4: Authorize Yourself
1. Open `.env` file
2. Find this line:
```env
TELEGRAM_AUTHORIZED_USERS=
```
3. Add your User ID:
```env
TELEGRAM_AUTHORIZED_USERS=123456789
```
4. **Restart the bot** (Ctrl+C, then run again)

### Step 5: Test Features
Send these commands:
- `/start` - Should now show "✅ Authorized"
- `/portfolio` - View portfolio with interactive buttons
- `/positions` - View options positions
- `/opportunities` - See CSP opportunities
- `/status` - Check system health
- `/help` - See all commands

## 🎯 Key Features to Try

### Interactive Buttons
After `/portfolio`, click:
- 🔄 Refresh - Update data
- 📈 Balance Chart - See 30-day chart
- 📊 Detailed View - More details
- 📋 Positions - View all positions

### Voice Messages
1. Record a voice message: "How's my portfolio?"
2. Send to AVA
3. AVA will transcribe and respond

### Natural Language
Just type questions:
- "Show me NVDA analysis"
- "Any new Xtrades alerts?"
- "What are you working on?"

## 📊 Available Commands

### Portfolio & Trading
- `/portfolio` - Portfolio balance and performance
- `/positions` - Active options positions
- `/opportunities` - Best CSP opportunities

### Integrations
- `/tradingview` - TradingView watchlists
- `/xtrades` - Followed traders

### System
- `/tasks` - AVA's task status
- `/status` - System health
- `/help` - Full command list

## 🔒 Security Notes

### Rate Limits
- 10 requests per minute
- 1000 requests per day
- System will tell you if you hit the limit

### Authorization
- Only authorized users can use sensitive commands
- Add users by their User ID in `.env`
- Multiple users: `TELEGRAM_AUTHORIZED_USERS=123,456,789`

## 🐛 Troubleshooting

### "Unauthorized Access"
**Solution:** Add your User ID to `.env` and restart

### "Rate limit exceeded"
**Solution:** Wait the specified time (shown in error)

### "Database connection failed"
**Solution:**
1. Check PostgreSQL is running
2. Verify `DATABASE_URL` in `.env`
3. Send `/status` to check connection

### Charts not generating
**Solution:**
```bash
pip install matplotlib numpy
```

## 📚 More Information

- **Full Documentation:** `src/ava/README_ENHANCED.md`
- **Complete Summary:** `AVA_TELEGRAM_BOT_ENHANCEMENT_COMPLETE.md`
- **Original Bot:** `src/ava/telegram_bot.py` (preserved)

## ✅ You're Ready!

Your AVA Telegram Bot is now a production-ready 24/7 trading assistant with:
- ✅ User authentication
- ✅ Rate limiting
- ✅ Interactive keyboards
- ✅ Chart generation
- ✅ Magnus platform integration
- ✅ Voice message support
- ✅ Comprehensive error handling

**Start exploring and enjoy your AI trading assistant!** 🎉
