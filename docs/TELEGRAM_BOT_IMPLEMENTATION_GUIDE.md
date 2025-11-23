# AVA Telegram Bot - Implementation Guide

**Version:** 2.0
**Status:** Ready for Implementation
**Estimated Time:** 8-10 weeks

---

## Quick Start

### Prerequisites

1. **Python 3.10+** installed
2. **PostgreSQL 15+** running (already set up as `magnus` database)
3. **Redis** installed or Docker available
4. **Telegram Bot Token** (you already have: `7552232147:...`)
5. **Public HTTPS endpoint** (use Ngrok for development)

### Installation

```bash
# 1. Install new dependencies
pip install -r requirements.txt

# New packages needed:
# - fastapi
# - uvicorn[standard]
# - rq
# - asyncpg
# - redis
# - websockets
# - prometheus-client
# - sentry-sdk

# 2. Run database migration
psql -U postgres -d magnus -f src/ava/migrations/001_telegram_enhancements.sql

# 3. Start Redis (if not already running)
docker run -d -p 6379:6379 --name ava-redis redis:7-alpine

# 4. Configure webhook (development)
# Install Ngrok: https://ngrok.com/download
ngrok http 8000
# Copy the HTTPS URL: https://abc123.ngrok.io

# 5. Update .env file
echo "TELEGRAM_WEBHOOK_URL=https://abc123.ngrok.io/webhook/7552232147:AAGAdwZh-SmesrtndZdsMAaKFDms-C2Z5ww" >> .env
echo "TELEGRAM_WEBHOOK_SECRET_TOKEN=$(openssl rand -hex 32)" >> .env
echo "TELEGRAM_USE_WEBHOOKS=true" >> .env
echo "REDIS_URL=redis://localhost:6379/0" >> .env

# 6. Set Telegram webhook
python -c "
import requests
BOT_TOKEN = '7552232147:AAGAdwZh-SmesrtndZdsMAaKFDms-C2Z5ww'
WEBHOOK_URL = 'https://abc123.ngrok.io/webhook/' + BOT_TOKEN
SECRET_TOKEN = 'your-secret-token-from-env'
response = requests.post(
    f'https://api.telegram.org/bot{BOT_TOKEN}/setWebhook',
    json={
        'url': WEBHOOK_URL,
        'secret_token': SECRET_TOKEN,
        'allowed_updates': ['message', 'edited_message', 'callback_query']
    }
)
print(response.json())
"

# 7. Start webhook server
uvicorn src.ava.webhook_server:app --host 0.0.0.0 --port 8000 --reload

# 8. Start RQ workers (in separate terminals)
rq worker ava:messages:high --url redis://localhost:6379/0
rq worker ava:messages:normal --url redis://localhost:6379/0
rq worker ava:messages:low --url redis://localhost:6379/0

# 9. Test the bot
# Open Telegram and send: /start
```

---

## Project Structure

```
c:\Code\WheelStrategy\
├── src/
│   ├── ava/
│   │   ├── telegram_bot.py (legacy - keep for fallback)
│   │   ├── webhook_server.py ✅ CREATED
│   │   ├── state_manager.py ✅ CREATED
│   │   ├── message_processor.py (TODO)
│   │   ├── db_manager.py (TODO)
│   │   ├── rate_limiter.py (TODO)
│   │   ├── voice_handler.py (existing, enhance)
│   │   ├── workflows/ (TODO)
│   │   │   ├── stock_analysis_workflow.py
│   │   │   └── trade_execution_workflow.py
│   │   ├── handlers/ (TODO)
│   │   │   ├── command_handler.py
│   │   │   ├── text_handler.py
│   │   │   └── callback_handler.py
│   │   ├── integrations/ (enhance existing)
│   │   │   ├── robinhood_client.py
│   │   │   ├── tradingview_client.py
│   │   │   └── xtrades_client.py
│   │   └── migrations/
│   │       └── 001_telegram_enhancements.sql ✅ CREATED
│   └── telegram_notifier.py (existing, unchanged)
├── docker/
│   └── docker-compose.ava.yml ✅ CREATED
├── config/
│   ├── prometheus.yml (TODO)
│   └── grafana/ (TODO)
├── docs/
│   ├── architecture/
│   │   └── ava-telegram-bot-architecture.md ✅ CREATED
│   └── TELEGRAM_BOT_IMPLEMENTATION_GUIDE.md ✅ THIS FILE
└── .env (update with new variables)
```

---

## Implementation Phases

### Phase 1: Foundation (Week 1-2) - PRIORITY

**Status:** 🟢 Ready to start

**Files Created:**
- ✅ `webhook_server.py` - FastAPI webhook endpoint
- ✅ `state_manager.py` - Redis-backed FSM
- ✅ `001_telegram_enhancements.sql` - Database schema
- ✅ `docker-compose.ava.yml` - Docker configuration

**TODO:**
1. Run database migration
2. Test webhook server locally with Ngrok
3. Verify state manager with Redis
4. Create `message_processor.py` (RQ worker)
5. Test end-to-end message flow

**Validation:**
```bash
# 1. Check database tables
psql -U postgres -d magnus -c "\dt telegram_*"

# 2. Test webhook health
curl http://localhost:8000/health

# 3. Test Redis connection
redis-cli ping

# 4. Send test message via Telegram
# Should appear in: http://localhost:9181 (RQ Dashboard)

# 5. Check message log
psql -U postgres -d magnus -c "SELECT * FROM telegram_message_log ORDER BY received_at DESC LIMIT 5;"
```

### Phase 2: Message Processing (Week 3)

**TODO:**
1. Create `message_processor.py`:
   - Dequeue messages from Redis
   - Load conversation state
   - Route to appropriate handler
   - Update state
   - Send response

2. Create handler classes:
   - `CommandHandler` - Handle /start, /help, /portfolio, /status
   - `TextQueryHandler` - Process text messages
   - `VoiceHandler` - Enhance existing voice handler
   - `CallbackHandler` - Handle inline button presses

3. Implement basic workflows:
   - Portfolio query (simple, no state)
   - Task status (simple, no state)

**Validation:**
```bash
# Test commands
/start → Should receive welcome message
/portfolio → Should show portfolio balance
/status → Should show AVA status

# Check logs
docker-compose -f docker/docker-compose.ava.yml logs -f worker
```

### Phase 3: State Management & Workflows (Week 4)

**TODO:**
1. Create workflow classes:
   - `StockAnalysisWorkflow` - Multi-step stock analysis
   - `TradeExecutionWorkflow` - Trade review and execution

2. Implement state transitions:
   - IDLE → AWAITING_TICKER → AWAITING_STRATEGY → AWAITING_CONFIRMATION

3. Add timeout handling:
   - Background job to expire conversations
   - Send timeout notification to user

4. Test multi-step conversations:
   ```
   User: "Analyze a stock"
   Bot: "Which ticker?"
   User: "NVDA"
   Bot: "Which strategy? 1) CSP 2) CC 3) Wheel"
   User: "1"
   Bot: "Here's the analysis... Execute? (yes/no)"
   User: "yes"
   Bot: "Order placed!"
   ```

**Validation:**
```python
# Test state management
import asyncio
from src.ava.state_manager import StateManager, ConversationState

async def test():
    manager = StateManager()
    await manager.set_state(123456, ConversationState.AWAITING_TICKER)
    state = await manager.get_state(123456)
    print(f"Current state: {state}")

asyncio.run(test())
```

### Phase 4: Reliability (Week 5)

**TODO:**
1. Add retry logic with exponential backoff
2. Implement circuit breaker for external APIs
3. Set up dead letter queue
4. Add per-user and global rate limiting
5. Implement connection pooling (asyncpg)

**Files to Create:**
- `rate_limiter.py` - Token bucket rate limiting
- `db_manager.py` - Connection pool management
- `circuit_breaker.py` - Circuit breaker pattern

**Validation:**
```bash
# Test rate limiting
# Send 10 messages in 1 second → Should be rate limited

# Test circuit breaker
# Kill Robinhood API → Circuit should open
# Check logs for "Circuit breaker opened"

# Test dead letter queue
# Cause a message to fail 3 times → Should move to DLQ
redis-cli LLEN ava:messages:dead_letter
```

### Phase 5: Performance (Week 6)

**TODO:**
1. Implement Redis caching layer:
   - Portfolio balance (5 min TTL)
   - Stock positions (30 sec TTL)
   - Market data (15 sec TTL)

2. Add cache invalidation:
   - Manual invalidation on trade execution
   - Time-based expiration

3. Optimize database queries:
   - Add missing indexes
   - Use connection pooling

4. Profile and optimize bottlenecks:
   - Use `cProfile` for Python profiling
   - Monitor with Prometheus

**Validation:**
```bash
# Check cache hit rate
redis-cli INFO stats | grep keyspace_hits

# Monitor response times
curl http://localhost:8000/metrics | grep processing_duration

# Profile code
python -m cProfile -o profile.stats src/ava/webhook_server.py
```

### Phase 6: Observability (Week 7)

**TODO:**
1. Set up Prometheus metrics:
   - Message throughput
   - Error rate
   - Response time (p50, p95, p99)
   - Queue length

2. Create Grafana dashboards:
   - Bot health dashboard
   - User engagement dashboard
   - Infrastructure dashboard

3. Set up alerting:
   - Error rate > 5%
   - Queue length > 100
   - Response time > 5s

4. Integrate Sentry for error tracking

**Files to Create:**
- `config/prometheus.yml`
- `config/grafana/dashboards/bot_health.json`
- `config/grafana/dashboards/user_engagement.json`

**Validation:**
```bash
# Access Prometheus
open http://localhost:9090

# Access Grafana
open http://localhost:3001
# Login: admin/admin

# View metrics
curl http://localhost:8000/metrics
```

### Phase 7: Integration (Week 8-9)

**TODO:**
1. Enhance Robinhood integration:
   - Add rate limiting (5 req/s)
   - Add circuit breaker
   - Cache responses

2. Add TradingView WebSocket client:
   - Real-time market data
   - Auto-reconnect on disconnect

3. Enhance Xtrades integration:
   - Webhook support (if available)
   - Better error handling

4. Build trade execution workflow:
   - Multi-step confirmation
   - Order preview
   - Risk checks
   - Execute via Robinhood API

**Validation:**
```bash
# Test Robinhood integration
python -c "from src.robinhood_integration import RobinhoodClient; client = RobinhoodClient(); client.login(); print(client.get_account_info())"

# Test TradingView WebSocket
# Should receive real-time quotes for subscribed symbols

# Test trade execution workflow
# Send: "Buy AAPL put"
# Should guide through multi-step flow
```

### Phase 8: Production Hardening (Week 10)

**TODO:**
1. Load testing:
   - Use Locust or k6
   - Simulate 1000 concurrent users
   - Measure response time and error rate

2. Security audit:
   - OWASP Top 10 check
   - SQL injection testing
   - Rate limit bypass testing
   - Webhook signature validation

3. Disaster recovery:
   - Database backup strategy
   - Redis persistence (AOF)
   - Backup webhook logs

4. Documentation:
   - API documentation (Swagger)
   - Runbook for common issues
   - Deployment guide

**Validation:**
```bash
# Load test with Locust
locust -f tests/load_test.py --host http://localhost:8000

# Security scan with OWASP ZAP
docker run -t owasp/zap2docker-stable zap-baseline.py -t http://localhost:8000

# Test backup/restore
pg_dump -U postgres magnus > backups/magnus_backup.sql
redis-cli BGSAVE
```

---

## Testing Strategy

### Unit Tests

```python
# tests/test_state_manager.py
import pytest
from src.ava.state_manager import StateManager, ConversationState

@pytest.mark.asyncio
async def test_state_transitions():
    manager = StateManager()
    chat_id = 123456

    await manager.set_state(chat_id, ConversationState.AWAITING_TICKER)
    state = await manager.get_state(chat_id)
    assert state == ConversationState.AWAITING_TICKER

    await manager.reset_state(chat_id)
    state = await manager.get_state(chat_id)
    assert state == ConversationState.IDLE
```

### Integration Tests

```python
# tests/test_webhook_integration.py
import pytest
from fastapi.testclient import TestClient
from src.ava.webhook_server import app

client = TestClient(app)

def test_webhook_endpoint():
    response = client.post(
        "/webhook/7552232147:AAGAdwZh-SmesrtndZdsMAaKFDms-C2Z5ww",
        json={
            "update_id": 123456,
            "message": {
                "message_id": 1,
                "from": {"id": 987654321, "first_name": "Test"},
                "chat": {"id": 987654321, "type": "private"},
                "date": 1699200000,
                "text": "/start"
            }
        },
        headers={"X-Telegram-Bot-Api-Secret-Token": "your-secret"}
    )
    assert response.status_code == 200
    assert response.json()["ok"] == True
```

### End-to-End Tests

```python
# tests/test_e2e_workflow.py
import pytest
from telegram import Bot

@pytest.mark.asyncio
async def test_stock_analysis_workflow():
    bot = Bot(token="YOUR_BOT_TOKEN")
    chat_id = 987654321

    # Send initial message
    await bot.send_message(chat_id, "Analyze a stock")

    # Wait for response
    await asyncio.sleep(1)

    # Check state
    state = await StateManager().get_state(chat_id)
    assert state == ConversationState.AWAITING_TICKER

    # Send ticker
    await bot.send_message(chat_id, "AAPL")

    # Verify analysis received
    # ... (check message log)
```

---

## Deployment

### Development (Local)

```bash
# 1. Start Redis
docker run -d -p 6379:6379 --name ava-redis redis:7-alpine

# 2. Start Ngrok
ngrok http 8000

# 3. Update .env with Ngrok URL

# 4. Start webhook server
uvicorn src.ava.webhook_server:app --reload

# 5. Start workers
rq worker ava:messages:high ava:messages:normal ava:messages:low --url redis://localhost:6379/0
```

### Production (Docker Compose)

```bash
# 1. Build images
docker-compose -f docker/docker-compose.ava.yml build

# 2. Start services
docker-compose -f docker/docker-compose.ava.yml up -d

# 3. Check logs
docker-compose -f docker/docker-compose.ava.yml logs -f

# 4. Scale workers
docker-compose -f docker/docker-compose.ava.yml up -d --scale worker=8

# 5. Monitor health
curl http://localhost:8000/health
```

### Production (Systemd)

```bash
# 1. Copy service file
sudo cp config/ava-telegram.service /etc/systemd/system/

# 2. Enable service
sudo systemctl enable ava-telegram

# 3. Start service
sudo systemctl start ava-telegram

# 4. Check status
sudo systemctl status ava-telegram

# 5. View logs
sudo journalctl -u ava-telegram -f
```

---

## Monitoring

### Key Metrics

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| **Uptime** | 99.9% | < 99% |
| **Response Time (p95)** | < 500ms | > 2s |
| **Error Rate** | < 0.5% | > 2% |
| **Queue Length** | < 10 | > 100 |
| **Cache Hit Rate** | > 80% | < 60% |
| **Database Pool Utilization** | < 80% | > 90% |

### Dashboards

**1. Bot Health Dashboard:**
- Message throughput (req/s)
- Error rate (%)
- Response time (p50, p95, p99)
- Queue length by priority
- Worker utilization

**2. User Engagement Dashboard:**
- Daily active users (DAU)
- Weekly active users (WAU)
- Most used commands
- Conversation completion rate
- Average messages per user

**3. Infrastructure Dashboard:**
- Redis memory usage
- Database connection pool
- CPU and memory usage
- API rate limit status
- Cache hit ratio

### Alerts

**Critical (PagerDuty):**
- Service down
- Error rate > 10%
- Response time > 10s

**Warning (Telegram):**
- Error rate > 2%
- Queue length > 100
- Response time > 2s
- Rate limit exceeded

**Info (Email):**
- Daily summary
- Weekly report
- Resource utilization trends

---

## Troubleshooting

### Common Issues

**1. Webhook not receiving messages**
```bash
# Check webhook info
curl https://api.telegram.org/bot<TOKEN>/getWebhookInfo

# Delete and reset webhook
curl https://api.telegram.org/bot<TOKEN>/deleteWebhook
curl -X POST https://api.telegram.org/bot<TOKEN>/setWebhook \
  -H "Content-Type: application/json" \
  -d '{"url": "https://your-domain.com/webhook/<TOKEN>"}'
```

**2. Messages stuck in queue**
```bash
# Check queue length
redis-cli LLEN ava:messages:normal

# Check workers
rq info --url redis://localhost:6379/0

# Flush queue (CAUTION: deletes messages)
redis-cli DEL ava:messages:normal
```

**3. High response time**
```bash
# Check cache hit rate
redis-cli INFO stats | grep keyspace_hits

# Check database connections
psql -U postgres -d magnus -c "SELECT count(*) FROM pg_stat_activity;"

# Profile code
python -m cProfile -o profile.stats src/ava/webhook_server.py
snakeviz profile.stats
```

**4. Rate limit exceeded**
```bash
# Check rate limit violations
psql -U postgres -d magnus -c "SELECT * FROM v_telegram_rate_limit_violations;"

# Reset rate limits for user
redis-cli DEL ava:ratelimit:987654321:minute
redis-cli DEL ava:ratelimit:987654321:hour
```

---

## Cost Estimate

### Monthly Costs (1000 active users)

| Component | Cost |
|-----------|------|
| **Infrastructure** | |
| VPS (4 vCPU, 8GB RAM) | $48 |
| Redis (Managed, 512MB) | $10 |
| PostgreSQL (1GB, included in magnus) | $0 |
| Domain + SSL (Cloudflare) | $0 |
| **APIs** | |
| Anthropic Claude (10k queries) | $100 |
| Whisper (local, free) | $0 |
| Robinhood API | $0 |
| TradingView API | $0 |
| **Monitoring** | |
| Grafana Cloud (free tier) | $0 |
| Sentry (free tier) | $0 |
| **Total** | **~$160/month** |

**Per User Cost:** $0.16/month

---

## Next Steps

1. ✅ **Review architecture document** - c:\Code\WheelStrategy\docs\architecture\ava-telegram-bot-architecture.md

2. ✅ **Review implementation files:**
   - `webhook_server.py` - Webhook endpoint
   - `state_manager.py` - State management
   - `001_telegram_enhancements.sql` - Database schema
   - `docker-compose.ava.yml` - Docker configuration

3. 🟡 **Start Phase 1 implementation:**
   - Run database migration
   - Test webhook server with Ngrok
   - Create message processor

4. 🟡 **Set up development environment:**
   - Install Redis
   - Set up Ngrok
   - Configure webhook

5. 🟡 **Begin testing:**
   - Send test messages
   - Monitor queue
   - Check logs

---

## Resources

### Documentation
- Architecture: `docs/architecture/ava-telegram-bot-architecture.md`
- API Reference: http://localhost:8000/docs (when running)
- RQ Dashboard: http://localhost:9181
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001

### External Links
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [RQ (Redis Queue)](https://python-rq.org/)
- [asyncpg](https://magicstack.github.io/asyncpg/)
- [Redis](https://redis.io/documentation)

### Support
- Telegram: @your_support_channel
- Email: support@your-domain.com
- GitHub Issues: https://github.com/your-repo/issues

---

**Ready to begin implementation? Start with Phase 1!**

Good luck! 🚀
