# Telegram Notifications - Quick Start Guide

Get up and running with Telegram notifications in 5 minutes.

## Installation

```bash
# Activate your virtual environment
cd C:\Code\WheelStrategy
.\venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install python-telegram-bot
```

## Setup (3 Steps)

### 1. Create Your Bot

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` and follow the prompts
3. Copy your bot token (looks like `123456789:ABCdef...`)

### 2. Get Your Chat ID

1. Search for `@userinfobot` in Telegram
2. Start a chat and send any message
3. Copy your Chat ID (a number like `123456789`)

### 3. Configure Environment

Edit your `.env` file:

```bash
# Add these lines
TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN_HERE
TELEGRAM_CHAT_ID=YOUR_CHAT_ID_HERE
TELEGRAM_ENABLED=true
```

## Test It

```python
from telegram_notifier import TelegramNotifier

# Test connection
notifier = TelegramNotifier()
notifier.test_connection()
# Check your Telegram - you should receive a test message!
```

## Basic Usage

### Send a New Trade Alert

```python
from telegram_notifier import TelegramNotifier
from datetime import datetime, date
from decimal import Decimal

notifier = TelegramNotifier()

trade = {
    'profile_username': 'traderJoe',
    'ticker': 'AAPL',
    'strategy': 'CSP',
    'action': 'STO',
    'entry_price': Decimal('2.50'),
    'quantity': 1,
    'strike_price': Decimal('170.00'),
    'expiration_date': date(2025, 12, 20),
    'alert_timestamp': datetime.now()
}

notifier.send_new_trade_alert(trade)
```

### Send a Trade Closed Alert

```python
closed_trade = {
    'profile_username': 'traderJoe',
    'ticker': 'AAPL',
    'strategy': 'CSP',
    'pnl': Decimal('125.00'),
    'pnl_percent': Decimal('50.00'),
    'entry_date': datetime(2025, 10, 1),
    'exit_date': datetime.now()
}

notifier.send_trade_closed_alert(closed_trade)
```

### Send Custom Message

```python
notifier.send_custom_message("*Important Update*\n\nMarket volatility detected!")
```

## Run Integration Service

```bash
# Test connection
python src/xtrades_telegram_integration.py --test

# Send daily summary
python src/xtrades_telegram_integration.py --summary

# Start monitoring (checks every 60 seconds)
python src/xtrades_telegram_integration.py

# Custom interval (check every 5 minutes)
python src/xtrades_telegram_integration.py --interval 300
```

## Run Tests

```bash
# Run all tests
pytest tests/test_telegram_notifier.py -v

# Run specific test
pytest tests/test_telegram_notifier.py::TestNewTradeAlert -v

# Run with coverage
pytest tests/test_telegram_notifier.py --cov=src.telegram_notifier
```

## Troubleshooting

### "Telegram not available"
```bash
pip install python-telegram-bot
```

### "Unauthorized" error
- Check your bot token is correct
- Make sure there are no extra spaces in `.env`

### "Chat not found"
- Send a message to your bot first
- Verify your chat ID with `@userinfobot`

### Test your configuration
```python
from telegram_notifier import TelegramNotifier

notifier = TelegramNotifier()
print(f"Enabled: {notifier.enabled}")
print(f"Bot: {notifier.bot is not None}")

if notifier.bot:
    info = notifier.get_bot_info()
    print(f"Bot username: @{info['username']}")
```

## Next Steps

- **Full Setup Guide**: See [TELEGRAM_SETUP.md](../TELEGRAM_SETUP.md)
- **Usage Examples**: See [TELEGRAM_USAGE_EXAMPLES.md](TELEGRAM_USAGE_EXAMPLES.md)
- **Source Code**: `src/telegram_notifier.py`
- **Tests**: `tests/test_telegram_notifier.py`
- **Integration**: `src/xtrades_telegram_integration.py`

## Common Use Cases

### Integrate with Database

```python
import psycopg2
from telegram_notifier import TelegramNotifier

notifier = TelegramNotifier()
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cursor = conn.cursor()

# Get new trades
cursor.execute("""
    SELECT * FROM xtrades_trades
    WHERE status = 'open'
    AND id NOT IN (
        SELECT trade_id FROM xtrades_notifications
        WHERE notification_type = 'new_trade'
    )
""")

for trade in cursor.fetchall():
    notifier.send_new_trade_alert(trade)
```

### Schedule Daily Summary

```python
from apscheduler.schedulers.blocking import BlockingScheduler
from telegram_notifier import TelegramNotifier

scheduler = BlockingScheduler()

@scheduler.scheduled_job('cron', hour=18, minute=0)
def daily_summary():
    notifier = TelegramNotifier()
    # Your summary logic here
    notifier.send_daily_summary(summary_data)

scheduler.start()
```

## Message Formatting

Telegram supports Markdown:

```python
message = """
*Bold text*
_Italic text_
`Code or monospace`
[Link](https://example.com)
"""

notifier.send_custom_message(message)
```

## Support

For detailed documentation and advanced features:
- Setup: [TELEGRAM_SETUP.md](../TELEGRAM_SETUP.md)
- Examples: [TELEGRAM_USAGE_EXAMPLES.md](TELEGRAM_USAGE_EXAMPLES.md)
- Tests: `pytest tests/test_telegram_notifier.py -v`

---

**Ready?** Start with [Setup Step 1](#setup-3-steps) above!
