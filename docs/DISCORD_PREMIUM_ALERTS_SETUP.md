# Discord Premium Alerts Setup Guide

Complete guide for setting up Discord premium alert notifications with AVA.

---

## Overview

The Discord Premium Alert system automatically:
- ✅ Syncs Discord messages every 5 minutes
- ✅ Prioritizes channel `990331623260180580` (premium alerts)
- ✅ Detects new trading alerts
- ✅ Sends notifications to your Discord bot channel
- ✅ Integrates with RAG knowledge base

---

## Quick Setup (5 Minutes)

### Step 1: Create Discord Webhook

1. Open Discord
2. Go to the channel where you want AVA to send notifications
3. Click the gear icon (Channel Settings)
4. Go to **Integrations** → **Webhooks**
5. Click **New Webhook**
6. Name it "Magnus Alert Bot"
7. Click **Copy Webhook URL**

### Step 2: Configure Environment

Add to your [`.env`](.env) file:

```env
# Discord Bot Webhook (for AVA notifications)
DISCORD_BOT_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_WEBHOOK_URL_HERE
```

**Important:** Keep your webhook URL secret! Don't commit it to Git.

### Step 3: Test the Webhook

Run the test script:

```bash
python test_discord_premium_alert.py
```

This will:
- ✅ Verify webhook connectivity
- ✅ Send test messages
- ✅ Show preview of premium alert format
- ✅ Test full embed formatting

Check your Discord channel - you should see 4 test messages!

### Step 4: Start Celery Worker

The sync runs automatically via Celery every 5 minutes:

```bash
# Start Celery worker
celery -A src.services.celery_app worker --loglevel=info

# Start Celery beat (scheduler)
celery -A src.services.celery_app beat --loglevel=info
```

Or use Docker:

```bash
docker-compose up -d
```

---

## How It Works

### Architecture

```
Premium Alerts Channel (990331623260180580)
           │
           ▼
    [Celery Task - Every 5 min]
           │
           ▼
   Discord Premium Alert Sync
           │
           ├──> Check for new messages (last 6 min)
           ├──> Filter for trading alerts
           ├──> Extract alert details
           │
           ▼
    Send to Discord Webhook
           │
           ▼
   Your Discord Bot Channel
   (Receives premium alert notifications)
```

### Alert Detection

The system identifies trading alerts by looking for keywords:
- Trade actions: buy, sell, entry, exit
- Options: call, put, strike, exp
- Prices: $, target, stop
- Sentiment: bullish, bearish, long, short

### Notification Format

Premium alerts are sent with rich embeds:

```
🚨 NEW PREMIUM ALERT 🚨

📈 Premium Trading Alert
━━━━━━━━━━━━━━━━━━━━━━

Ticker: NVDA
Action: BUY
Type: Call Option
Strike: $140
Expiration: 12/20/2025
Entry: $5.50
Target: $8.00
Stop Loss: $4.00

Rationale: Strong uptrend, technical breakout

👤 Posted by: Premium Trader
🕐 Time: 2:30 PM
📺 Channel: Premium Alerts (990331623260180580)
```

---

## Configuration

### Environment Variables

```env
# Required: Discord bot webhook for notifications
DISCORD_BOT_WEBHOOK_URL=https://discord.com/api/webhooks/...

# Required: Database connection (for Discord message storage)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=magnus
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password

# Optional: Discord user token (for message syncing with DiscordChatExporter)
DISCORD_USER_TOKEN=your_user_token_here
```

### Celery Schedule

Discord sync is configured in [`src/services/celery_app.py`](../src/services/celery_app.py):

```python
'sync-discord-messages': {
    'task': 'src.services.tasks.sync_discord_messages',
    'schedule': crontab(minute='*/5'),  # Every 5 minutes
    'options': {'queue': 'market_data'}
}
```

**To change frequency:**

Edit the schedule (e.g., every 2 minutes):
```python
'schedule': crontab(minute='*/2'),
```

Then restart Celery beat:
```bash
celery -A src.services.celery_app beat --loglevel=info
```

---

## Testing

### Manual Sync Test

Test the sync manually (without Celery):

```bash
python -m src.discord_premium_alert_sync
```

Optional: Check specific time window
```bash
python -m src.discord_premium_alert_sync 60  # Last 60 minutes
```

### Webhook Test

Test webhook only:

```bash
python test_discord_premium_alert.py
```

### End-to-End Test

1. **Post a test message** in the premium channel (990331623260180580):
   ```
   TEST ALERT: BUY NVDA 140C 12/20 @ $5.50
   Target: $8.00, Stop: $4.00
   ```

2. **Wait up to 5 minutes** for Celery to run

3. **Check your Discord bot channel** - you should see the alert!

4. **Check Celery logs**:
   ```bash
   # Windows
   type celery.log | findstr "Discord"

   # Linux/Mac
   tail -f celery.log | grep "Discord"
   ```

---

## Troubleshooting

### No notifications appearing

**Check 1: Webhook URL configured?**
```bash
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('✅' if os.getenv('DISCORD_BOT_WEBHOOK_URL') else '❌ Not configured')"
```

**Check 2: Celery running?**
```bash
celery -A src.services.celery_app inspect active
```

**Check 3: Test webhook manually**
```bash
python test_discord_premium_alert.py
```

**Check 4: Check Celery logs**
Look for errors in Celery worker output:
```bash
celery -A src.services.celery_app worker --loglevel=debug
```

### Messages syncing but no alerts

**Check 1: Are messages from premium channel?**

Query database:
```sql
SELECT COUNT(*)
FROM discord_messages
WHERE channel_id = '990331623260180580'
  AND timestamp > NOW() - INTERVAL '1 hour';
```

**Check 2: Do messages contain alert keywords?**

The message must contain trading keywords like:
- buy, sell, entry, exit
- call, put, strike
- $, target, stop

**Check 3: Test alert detection**

```python
from src.discord_premium_alert_sync import DiscordPremiumAlertSync

syncer = DiscordPremiumAlertSync()

# Test message
test_msg = {
    'content': 'BUY NVDA 140C @ $5.50',
    'author_name': 'Test',
    'timestamp': datetime.now()
}

is_alert = syncer.is_premium_alert(test_msg)
print(f"Is alert: {is_alert}")  # Should be True
```

### Webhook errors

**Error: 404 Not Found**
- Webhook URL is invalid or deleted
- Create a new webhook in Discord

**Error: 401 Unauthorized**
- Webhook URL is incorrect
- Copy the webhook URL again from Discord

**Error: 429 Too Many Requests**
- Rate limited by Discord
- Reduce sync frequency (e.g., every 10 minutes)
- Wait and try again

---

## Advanced Configuration

### Custom Alert Filters

Edit [`src/discord_premium_alert_sync.py`](../src/discord_premium_alert_sync.py):

```python
def is_premium_alert(self, message: Dict[str, Any]) -> bool:
    """Customize alert detection logic"""
    content = message.get('content', '').lower()

    # Add your custom keywords
    custom_keywords = ['moon', 'rocket', 'yolo']

    # Your custom logic
    return any(keyword in content for keyword in custom_keywords)
```

### Multiple Premium Channels

To monitor multiple premium channels, edit [`src/discord_premium_alert_sync.py`](../src/discord_premium_alert_sync.py):

```python
PREMIUM_CHANNELS = [
    '990331623260180580',  # Premium alerts
    '123456789012345678',  # VIP signals
    '987654321098765432',  # Day trading
]

# Then modify sync logic to loop through channels
for channel_id in PREMIUM_CHANNELS:
    result = syncer.sync_premium_channel(channel_id)
```

### Custom Notification Format

Edit the `send_discord_notification` method in [`src/discord_premium_alert_sync.py`](../src/discord_premium_alert_sync.py):

```python
payload = {
    'content': f'🚀 CUSTOM FORMAT 🚀\n\n{summary}',
    'username': 'Your Custom Bot Name',
    'avatar_url': 'https://your-custom-avatar.png',
    'embeds': [{
        'title': 'Your Custom Title',
        'description': message.get('content', ''),
        'color': 0x00FF00,  # Green color
        # ... customize further
    }]
}
```

---

## Performance

### Resource Usage

- **Sync frequency**: Every 5 minutes
- **CPU**: Minimal (~1-2% during sync)
- **Memory**: <100 MB
- **Database**: ~5 MB per 1,000 messages
- **Network**: ~50 KB per sync

### Scaling

For high-volume channels (>100 messages/min):

1. **Increase Celery workers**:
   ```bash
   celery -A src.services.celery_app worker --concurrency=4
   ```

2. **Optimize database queries** (already indexed):
   ```sql
   -- Index on channel_id + timestamp (already created)
   CREATE INDEX idx_discord_channel_timestamp
   ON discord_messages(channel_id, timestamp DESC);
   ```

3. **Reduce sync frequency** if needed:
   ```python
   'schedule': crontab(minute='*/10'),  # Every 10 minutes
   ```

---

## Security

### Webhook URL Security

**✅ DO:**
- Keep webhook URL in `.env` file
- Add `.env` to `.gitignore`
- Use environment variables in production
- Regenerate webhook if leaked

**❌ DON'T:**
- Commit webhook URL to Git
- Share webhook URL publicly
- Use same webhook for multiple purposes

### Rate Limiting

Discord webhooks are rate limited:
- **30 requests per minute** per webhook
- **Exceeded limit**: 429 error

Our system respects limits:
- 1 sync every 5 minutes = 12 requests/hour
- Well within Discord limits

---

## Monitoring

### Celery Flower Dashboard

Monitor Celery tasks via Flower UI:

```bash
celery -A src.services.celery_app flower
```

Open: [http://localhost:5555](http://localhost:5555)

View:
- ✅ Task execution history
- ✅ Success/failure rates
- ✅ Task timing
- ✅ Worker status

### Database Monitoring

Check sync status:

```sql
-- Recent messages count
SELECT
    channel_id,
    COUNT(*) as message_count,
    MAX(timestamp) as last_message
FROM discord_messages
WHERE timestamp > NOW() - INTERVAL '1 hour'
GROUP BY channel_id;

-- Premium channel activity
SELECT COUNT(*)
FROM discord_messages
WHERE channel_id = '990331623260180580'
  AND timestamp > NOW() - INTERVAL '24 hours';
```

### Logs

Check logs for sync activity:

```bash
# View recent syncs
tail -100 celery.log | grep "Discord sync"

# Count alerts sent
grep "premium alerts sent" celery.log | wc -l

# Check for errors
grep "ERROR" celery.log | grep "Discord"
```

---

## Production Deployment

### Docker Compose

Full stack deployment with Celery:

```yaml
version: '3.8'

services:
  celery_worker:
    build: .
    command: celery -A src.services.celery_app worker --loglevel=info
    environment:
      - DISCORD_BOT_WEBHOOK_URL=${DISCORD_BOT_WEBHOOK_URL}
      - POSTGRES_HOST=postgres
      - POSTGRES_DB=magnus
    depends_on:
      - postgres
      - redis

  celery_beat:
    build: .
    command: celery -A src.services.celery_app beat --loglevel=info
    environment:
      - DISCORD_BOT_WEBHOOK_URL=${DISCORD_BOT_WEBHOOK_URL}
    depends_on:
      - redis

  flower:
    build: .
    command: celery -A src.services.celery_app flower
    ports:
      - "5555:5555"
    depends_on:
      - redis
```

Deploy:
```bash
docker-compose up -d
```

### Health Checks

Add health check to Celery task:

```python
@shared_task
def health_check_discord_sync():
    """Health check for Discord sync"""
    try:
        # Check webhook
        webhook_url = os.getenv('DISCORD_BOT_WEBHOOK_URL')
        if not webhook_url:
            return {'status': 'error', 'message': 'Webhook not configured'}

        # Test webhook
        response = requests.post(webhook_url, json={
            'content': '✅ Health check passed',
            'username': 'Magnus Health Check'
        }, timeout=5)

        if response.status_code == 200:
            return {'status': 'healthy'}
        else:
            return {'status': 'unhealthy', 'code': response.status_code}

    except Exception as e:
        return {'status': 'error', 'message': str(e)}
```

---

## Support

**Issues?** Check:
1. [Troubleshooting section](#troubleshooting) above
2. Celery logs: `celery.log`
3. Test script: `python test_discord_premium_alert.py`

**Still stuck?**
- File issue: [GitHub Issues](https://github.com/your-repo/issues)
- Check docs: [Magnus Documentation](../docs/)

---

**Setup Complete!** 🎉

Your Discord premium alerts are now configured and running every 5 minutes!

---

**Last Updated**: 2025-11-21
**Magnus Trading Platform** • Discord Premium Alerts v1.0
