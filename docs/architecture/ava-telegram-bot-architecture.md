# AVA Telegram Bot - Enhanced Architecture Design

**Document Version:** 2.0
**Date:** 2025-11-06
**Status:** Production Enhancement Proposal
**System:** AVA (Automated Vector Agent) - 24/7 Trading Assistant

---

## Executive Summary

This document proposes comprehensive architectural enhancements to the AVA Telegram bot to transform it from a simple polling-based notification system into a highly reliable, scalable, production-grade 24/7 trading assistant capable of handling high message volumes, maintaining conversation state, and seamlessly integrating with trading platform APIs (Robinhood, TradingView).

### Key Technology Recommendations

**Current Stack:**
- Python 3.10+ with python-telegram-bot library (polling mode)
- Direct database connections (no pooling)
- No conversation state management
- No message queuing
- No retry mechanisms beyond basic telegram library features
- Whisper (local) for voice transcription
- Single-threaded synchronous processing

**Proposed Stack:**
- **Webhooks:** FastAPI + Uvicorn for webhook handling
- **Message Queue:** Redis + RQ (Redis Queue) or Celery
- **Database:** PostgreSQL with connection pooling (PGBouncer or asyncpg pool)
- **Cache:** Redis for session state, rate limiting, and API response caching
- **State Management:** Redis-backed finite state machine (FSM)
- **Monitoring:** Prometheus + Grafana for metrics
- **Error Tracking:** Sentry for exception monitoring
- **Deployment:** Docker + Docker Compose for 24/7 uptime

---

## 1. Architecture Overview

### 1.1 Current Architecture (As-Is)

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Telegram Platform                             │
└────────────────────┬────────────────────────────────────────────────┘
                     │ Long Polling (Update.ALL_TYPES)
                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    AVA Telegram Bot (telegram_bot.py)                │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Application (python-telegram-bot)                           │  │
│  │  - CommandHandler: /start, /help, /portfolio, /tasks, /status│  │
│  │  - MessageHandler: Voice messages, Text messages             │  │
│  └──────────────────────┬───────────────────────────────────────┘  │
│                         │                                            │
│                         ▼                                            │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  AVAVoiceHandler (voice_handler.py)                          │  │
│  │  - Whisper (tiny model) for voice transcription              │  │
│  │  - Query routing based on keywords                           │  │
│  │  - Direct database queries (psycopg2)                        │  │
│  └──────────────────────┬───────────────────────────────────────┘  │
└─────────────────────────┼────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   PostgreSQL Database (magnus)                       │
│  - portfolio_balances                                                │
│  - ci_enhancements (autonomous agent tasks)                          │
│  - xtrades_profiles, xtrades_alerts (trading signals)               │
│  - robinhood_positions (if synced)                                   │
└─────────────────────────────────────────────────────────────────────┘

LIMITATIONS:
❌ No conversation state tracking (single-turn interactions only)
❌ No message queue (messages processed synchronously)
❌ No connection pooling (new DB connection per query)
❌ No retry logic for failed database queries
❌ No rate limiting protection
❌ Polling mode wastes resources and has latency (~1-5 seconds)
❌ No error recovery or circuit breaker patterns
❌ No metrics or observability
❌ Single point of failure (crashes on unhandled exceptions)
```

### 1.2 Proposed Architecture (To-Be)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                            Telegram Platform                                  │
└────────────────────────┬─────────────────────────────────────────────────────┘
                         │ HTTPS Webhook (TLS 1.2+)
                         ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                      Reverse Proxy (Nginx/Caddy)                              │
│  - TLS termination                                                            │
│  - Request buffering                                                          │
│  - DDoS protection (rate limiting)                                            │
└────────────────────────┬─────────────────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                     FastAPI Webhook Server (webhook_server.py)                │
│                                                                                │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │  POST /webhook/{bot_token}                                             │  │
│  │  - Validate Telegram signature                                         │  │
│  │  - Parse Update object                                                 │  │
│  │  - Enqueue message to Redis Queue                                      │  │
│  │  - Return 200 OK immediately (async processing)                        │  │
│  └────────────────────────┬───────────────────────────────────────────────┘  │
│                           │                                                    │
│  ┌────────────────────────▼───────────────────────────────────────────────┐  │
│  │  Middleware Stack                                                       │  │
│  │  - Request logging (correlation IDs)                                   │  │
│  │  - Error handling (global exception handler)                           │  │
│  │  - Metrics collection (Prometheus)                                     │  │
│  └─────────────────────────────────────────────────────────────────────────┘ │
└────────────────────────┬─────────────────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                          Redis Message Queue                                  │
│                                                                                │
│  Queues:                                                                       │
│  - ava:messages:high (priority commands, /status, /portfolio)                │
│  - ava:messages:normal (text queries, voice messages)                        │
│  - ava:messages:low (background tasks, analytics)                            │
│  - ava:messages:dead_letter (failed messages for retry)                      │
│                                                                                │
│  State Storage:                                                                │
│  - ava:state:{chat_id} → FSM state (JSON)                                    │
│  - ava:session:{chat_id} → User session data (TTL: 1 hour)                   │
│  - ava:ratelimit:{chat_id} → Rate limit counters (TTL: 60s)                  │
│  - ava:cache:portfolio:{user_id} → Cached portfolio data (TTL: 5 min)        │
└────────────────────────┬─────────────────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                      Message Worker Pool (RQ Workers)                         │
│                                                                                │
│  Worker 1-4 (Parallel Processing):                                            │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │  AVAMessageProcessor (message_processor.py)                            │  │
│  │                                                                         │  │
│  │  1. Load conversation state from Redis                                 │  │
│  │  2. Check rate limits                                                  │  │
│  │  3. Route message to appropriate handler                               │  │
│  │  4. Execute handler with retry logic                                   │  │
│  │  5. Update conversation state                                          │  │
│  │  6. Send response via Telegram API                                     │  │
│  │  7. Log metrics                                                        │  │
│  └────────────────────────┬───────────────────────────────────────────────┘  │
│                           │                                                    │
│  ┌────────────────────────▼───────────────────────────────────────────────┐  │
│  │  Message Handlers                                                       │  │
│  │  - CommandHandler (commands like /start, /portfolio)                   │  │
│  │  - VoiceHandler (Whisper transcription → query processing)             │  │
│  │  - TextQueryHandler (natural language processing)                      │  │
│  │  - WorkflowHandler (multi-step conversations)                          │  │
│  └────────────────────────┬───────────────────────────────────────────────┘  │
└─────────────────────────┼────────────────────────────────────────────────────┘
                          │
              ┌───────────┴───────────┬──────────────────┬────────────────┐
              ▼                       ▼                  ▼                ▼
┌──────────────────────┐  ┌─────────────────┐  ┌────────────────┐  ┌────────────┐
│  Database Layer      │  │  External APIs  │  │  AI Services   │  │ Monitoring │
│  (db_manager.py)     │  │                 │  │                │  │            │
│                      │  │  - Robinhood    │  │  - Anthropic   │  │ Prometheus │
│  - Connection Pool   │  │  - TradingView  │  │  - DeepSeek    │  │  Metrics   │
│  - Query caching     │  │  - Xtrades      │  │  - Gemini      │  │            │
│  - Retry logic       │  │  - Market Data  │  │                │  │  Grafana   │
│  - Health checks     │  │                 │  │  - Whisper     │  │ Dashboards │
│                      │  │  Rate Limited   │  │    (local)     │  │            │
│  PostgreSQL (magnus) │  │  Circuit Breaker│  │                │  │  Sentry    │
│  via PGBouncer       │  │                 │  │                │  │  Errors    │
└──────────────────────┘  └─────────────────┘  └────────────────┘  └────────────┘
```

---

## 2. Service Definitions

### 2.1 Webhook Server (webhook_server.py)

**Core Responsibilities:**
- Receive and validate HTTPS webhook requests from Telegram
- Authenticate requests using secret token
- Parse Update objects
- Enqueue messages to appropriate Redis queue based on priority
- Health check endpoints for monitoring

**Technology:** FastAPI + Uvicorn (ASGI server)

**API Endpoints:**

```python
POST /webhook/{bot_secret_token}
  - Validates Telegram signature
  - Returns 200 OK immediately
  - Body: Telegram Update JSON

GET /health
  - Returns: {"status": "healthy", "redis": "connected", "db": "connected"}

GET /metrics
  - Returns: Prometheus metrics
```

### 2.2 Message Worker (message_processor.py)

**Core Responsibilities:**
- Dequeue messages from Redis queues
- Load conversation state from Redis
- Route to appropriate handler based on message type
- Execute handlers with retry and timeout logic
- Update conversation state
- Send responses via Telegram API
- Log metrics and errors

**Technology:** RQ (Redis Queue) workers

**Handler Routing:**
```
/start, /help → CommandHandler
/portfolio, /tasks, /status → QueryHandler (with caching)
Voice message → VoiceHandler (Whisper transcription)
Text message → TextQueryHandler (NLP intent detection)
Callback query → CallbackHandler (inline button responses)
```

### 2.3 Database Manager (db_manager.py)

**Core Responsibilities:**
- Manage PostgreSQL connection pool
- Execute queries with automatic retry logic
- Cache frequently accessed data in Redis
- Provide health check interface
- Transaction management

**Technology:** asyncpg (async PostgreSQL driver)

**Connection Pool Configuration:**
```python
min_size: 5 connections
max_size: 20 connections
max_inactive_connection_lifetime: 300s
timeout: 10s
command_timeout: 30s
```

### 2.4 State Manager (state_manager.py)

**Core Responsibilities:**
- Manage conversation state using finite state machine (FSM)
- Store/retrieve user session data
- Handle multi-step workflows
- Timeout idle conversations

**Technology:** Redis + Custom FSM implementation

**States:**
```
IDLE → User has no active conversation
AWAITING_TICKER → Waiting for user to provide ticker symbol
AWAITING_CONFIRMATION → Waiting for yes/no confirmation
PROCESSING → Bot is processing request
ERROR → Error state, waiting for recovery
```

### 2.5 External API Clients

#### RobinhoodClient (robinhood_client.py)
- Rate limited API wrapper
- Connection pooling for HTTP requests
- Circuit breaker pattern (fail fast after 3 consecutive errors)
- Response caching (portfolio data: 5 minutes, positions: 30 seconds)

#### TradingViewClient (tradingview_client.py)
- WebSocket connection for real-time data
- Session management with automatic reconnection
- Rate limiting (max 5 requests/second)

#### XtradesClient (xtrades_client.py)
- Scraping with retry logic
- Cookie-based session management
- Alert monitoring with webhook callbacks

---

## 3. API Contracts

### 3.1 Webhook Endpoint

**Request:**
```json
POST /webhook/7552232147:AAGAdwZh-SmesrtndZdsMAaKFDms-C2Z5ww

Headers:
  X-Telegram-Bot-Api-Secret-Token: <secret_token>
  Content-Type: application/json

Body:
{
  "update_id": 123456789,
  "message": {
    "message_id": 123,
    "from": {
      "id": 987654321,
      "first_name": "Adam",
      "username": "adam_trader"
    },
    "chat": {
      "id": 987654321,
      "type": "private"
    },
    "date": 1699200000,
    "text": "/portfolio"
  }
}
```

**Response (Success):**
```json
HTTP 200 OK
{
  "ok": true,
  "message_id": "msg_abc123",
  "queued_at": "2025-11-06T15:30:00Z"
}
```

**Response (Error):**
```json
HTTP 400 Bad Request
{
  "ok": false,
  "error": "Invalid signature",
  "timestamp": "2025-11-06T15:30:00Z"
}
```

### 3.2 Message Queue Format

**Redis Queue Entry:**
```json
{
  "message_id": "msg_abc123",
  "update_id": 123456789,
  "chat_id": 987654321,
  "user_id": 987654321,
  "message_type": "text",
  "content": "/portfolio",
  "timestamp": "2025-11-06T15:30:00Z",
  "priority": "high",
  "retry_count": 0,
  "metadata": {
    "user_name": "Adam",
    "chat_type": "private"
  }
}
```

### 3.3 State Management API

**Get State:**
```python
GET ava:state:987654321

Response:
{
  "current_state": "AWAITING_TICKER",
  "previous_state": "IDLE",
  "context": {
    "workflow": "stock_analysis",
    "step": 1,
    "data": {}
  },
  "updated_at": "2025-11-06T15:30:00Z",
  "expires_at": "2025-11-06T16:30:00Z"
}
```

**Update State:**
```python
SET ava:state:987654321 '{"current_state": "PROCESSING", ...}' EX 3600
```

### 3.4 Response Format

**Text Response:**
```json
{
  "method": "sendMessage",
  "chat_id": 987654321,
  "text": "Your portfolio balance is $125,430.50...",
  "parse_mode": "Markdown",
  "reply_markup": {
    "inline_keyboard": [
      [
        {"text": "📊 Positions", "callback_data": "show_positions"},
        {"text": "📈 Performance", "callback_data": "show_performance"}
      ]
    ]
  }
}
```

---

## 4. Data Schema Changes

### 4.1 New Tables

#### telegram_users
```sql
CREATE TABLE telegram_users (
    id SERIAL PRIMARY KEY,
    chat_id BIGINT UNIQUE NOT NULL,
    user_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(100),
    first_name VARCHAR(100),
    last_name VARCHAR(100),

    -- Preferences
    notifications_enabled BOOLEAN DEFAULT TRUE,
    language_code VARCHAR(10) DEFAULT 'en',
    timezone VARCHAR(50) DEFAULT 'UTC',

    -- Security
    is_authorized BOOLEAN DEFAULT FALSE,
    authorization_code VARCHAR(10),
    authorized_at TIMESTAMP WITH TIME ZONE,

    -- State tracking
    conversation_state JSONB DEFAULT '{"state": "IDLE"}',
    session_data JSONB DEFAULT '{}',

    -- Rate limiting
    message_count_today INTEGER DEFAULT 0,
    last_message_at TIMESTAMP WITH TIME ZONE,
    rate_limited_until TIMESTAMP WITH TIME ZONE,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_seen_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_telegram_users_chat_id ON telegram_users(chat_id);
CREATE INDEX idx_telegram_users_authorized ON telegram_users(is_authorized);
```

#### telegram_message_log
```sql
CREATE TABLE telegram_message_log (
    id SERIAL PRIMARY KEY,
    message_id BIGINT NOT NULL,
    update_id BIGINT UNIQUE NOT NULL,
    chat_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,

    -- Message details
    message_type VARCHAR(50) NOT NULL, -- 'text', 'voice', 'command', 'callback_query'
    direction VARCHAR(10) NOT NULL, -- 'incoming', 'outgoing'
    content TEXT,

    -- Processing
    handler VARCHAR(100),
    processing_time_ms INTEGER,
    status VARCHAR(50), -- 'queued', 'processing', 'completed', 'failed'
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,

    -- Context
    conversation_state VARCHAR(50),
    session_id VARCHAR(100),

    -- Timestamps
    received_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT fk_telegram_message_user
        FOREIGN KEY (chat_id) REFERENCES telegram_users(chat_id)
);

CREATE INDEX idx_telegram_message_log_chat ON telegram_message_log(chat_id, received_at DESC);
CREATE INDEX idx_telegram_message_log_status ON telegram_message_log(status);
CREATE INDEX idx_telegram_message_log_update ON telegram_message_log(update_id);
```

#### telegram_rate_limits
```sql
CREATE TABLE telegram_rate_limits (
    id SERIAL PRIMARY KEY,
    chat_id BIGINT NOT NULL,

    -- Rate limit tracking
    window_start TIMESTAMP WITH TIME ZONE NOT NULL,
    window_duration_seconds INTEGER NOT NULL, -- 60, 3600, 86400
    request_count INTEGER DEFAULT 0,
    limit_exceeded_at TIMESTAMP WITH TIME ZONE,

    -- Limits
    max_requests_per_window INTEGER NOT NULL,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    UNIQUE(chat_id, window_start, window_duration_seconds)
);

CREATE INDEX idx_telegram_rate_limits_chat ON telegram_rate_limits(chat_id);
CREATE INDEX idx_telegram_rate_limits_window ON telegram_rate_limits(window_start);
```

#### telegram_workflows
```sql
CREATE TABLE telegram_workflows (
    id SERIAL PRIMARY KEY,
    workflow_name VARCHAR(100) NOT NULL,
    chat_id BIGINT NOT NULL,

    -- Workflow state
    current_step INTEGER DEFAULT 1,
    total_steps INTEGER NOT NULL,
    status VARCHAR(50) DEFAULT 'active', -- 'active', 'completed', 'cancelled', 'timeout'

    -- Data
    workflow_data JSONB DEFAULT '{}',
    collected_inputs JSONB DEFAULT '{}',

    -- Timestamps
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '1 hour'),

    CONSTRAINT fk_telegram_workflow_user
        FOREIGN KEY (chat_id) REFERENCES telegram_users(chat_id)
);

CREATE INDEX idx_telegram_workflows_chat ON telegram_workflows(chat_id);
CREATE INDEX idx_telegram_workflows_status ON telegram_workflows(status);
CREATE INDEX idx_telegram_workflows_expires ON telegram_workflows(expires_at);
```

### 4.2 Schema Migration Script

**File:** `c:\Code\WheelStrategy\src\ava\migrations\001_telegram_enhancements.sql`

```sql
-- Migration: Add Telegram bot state management tables
-- Version: 001
-- Date: 2025-11-06

BEGIN;

-- Create telegram_users table
CREATE TABLE IF NOT EXISTS telegram_users (...);

-- Create telegram_message_log table
CREATE TABLE IF NOT EXISTS telegram_message_log (...);

-- Create telegram_rate_limits table
CREATE TABLE IF NOT EXISTS telegram_rate_limits (...);

-- Create telegram_workflows table
CREATE TABLE IF NOT EXISTS telegram_workflows (...);

-- Add trigger for updated_at
CREATE OR REPLACE FUNCTION update_telegram_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER telegram_users_updated_at
    BEFORE UPDATE ON telegram_users
    FOR EACH ROW
    EXECUTE FUNCTION update_telegram_updated_at();

-- Insert migration record
INSERT INTO schema_migrations (version, name, applied_at)
VALUES (1, 'telegram_enhancements', NOW());

COMMIT;
```

---

## 5. Technology Stack Rationale

### 5.1 Webhooks vs Polling

**Recommendation: Webhooks**

**Justification:**
- **Latency:** Webhooks provide near-instant delivery (< 100ms) vs polling (1-5 seconds)
- **Resource Efficiency:** No continuous polling = 99% reduction in CPU usage
- **Scalability:** Telegram servers push updates only when they occur
- **Reliability:** Built-in retry mechanism from Telegram (up to 3 attempts)

**Trade-offs:**
- **Complexity:** Requires public HTTPS endpoint (solved with Ngrok for dev, Caddy for prod)
- **Security:** Must validate webhook signatures (mitigated with secret token)
- **Deployment:** Needs 24/7 uptime (solved with Docker + systemd)

**Alternative Considered:** Long Polling
- **Pros:** Simpler setup, no public endpoint required
- **Cons:** Higher latency, wasteful resource usage, not suitable for 24/7 production

**Decision:** Use webhooks for production, provide polling fallback for development.

### 5.2 Message Queue (Redis + RQ)

**Recommendation: Redis Queue (RQ)**

**Justification:**
- **Simplicity:** RQ is pure Python, no complex broker configuration
- **Async Processing:** Decouple webhook response (< 100ms) from processing (1-30s)
- **Priority Queues:** Critical commands (/status) process faster than background tasks
- **Reliability:** Failed jobs move to dead letter queue for retry
- **Monitoring:** Built-in dashboard (rq-dashboard) for queue inspection

**Trade-offs:**
- **Single Redis Dependency:** Redis failure = queue failure (mitigated with Redis replication)
- **Limited Features:** No complex routing (acceptable for this use case)

**Alternative Considered:** Celery
- **Pros:** More features, battle-tested
- **Cons:** Overkill for this scale, requires RabbitMQ/Redis broker, complex configuration

**Decision:** RQ for simplicity, migrate to Celery if we exceed 10,000 messages/day.

### 5.3 Database Connection Pooling (asyncpg)

**Recommendation: asyncpg with connection pooling**

**Justification:**
- **Performance:** 3-5x faster than psycopg2 for async workloads
- **Connection Reuse:** Pool of 5-20 connections shared across workers
- **Automatic Retry:** Reconnects on connection failure
- **Async/Await:** Native async support for FastAPI integration

**Configuration:**
```python
min_size=5  # Always maintain 5 warm connections
max_size=20  # Scale up to 20 under load
max_inactive_connection_lifetime=300  # Refresh connections every 5 min
timeout=10  # Connection acquisition timeout
command_timeout=30  # Query timeout
```

**Trade-offs:**
- **Async Complexity:** Requires async/await throughout codebase
- **Learning Curve:** Different API from psycopg2

**Alternative Considered:** PGBouncer (external connection pooler)
- **Pros:** No code changes, works with psycopg2
- **Cons:** Additional infrastructure, transaction vs session pooling trade-offs

**Decision:** asyncpg for new code, PGBouncer as backup for psycopg2 legacy code.

### 5.4 Caching Strategy (Redis)

**Recommendation: Multi-tier caching with Redis**

**Cache Tiers:**

| Data Type | TTL | Invalidation Strategy |
|-----------|-----|----------------------|
| Portfolio Balance | 5 minutes | Time-based + Manual on trade |
| Stock Positions | 30 seconds | Time-based |
| User Session State | 1 hour | Activity-based extension |
| Market Data | 15 seconds | Time-based |
| Conversation State | 1 hour | Manual on completion |
| Rate Limit Counters | 60 seconds | Time-based sliding window |

**Benefits:**
- **Database Load Reduction:** 80-90% fewer queries
- **Response Time:** < 10ms for cached data vs 50-200ms for DB queries
- **Cost Savings:** Reduced API calls to Robinhood, TradingView

**Implementation:**
```python
@cached(ttl=300, key="portfolio:{user_id}")
async def get_portfolio_balance(user_id: int):
    return await db.fetch_one(...)
```

### 5.5 Rate Limiting (Token Bucket Algorithm)

**Recommendation: Sliding window rate limiting with Redis**

**Rate Limits:**
```python
# Per user limits
USER_LIMITS = {
    "messages_per_minute": 5,
    "messages_per_hour": 50,
    "messages_per_day": 200,
    "api_calls_per_hour": 100,  # Robinhood, TradingView
}

# Global limits
GLOBAL_LIMITS = {
    "messages_per_second": 30,  # Telegram limit
    "database_queries_per_second": 100,
}
```

**Implementation:**
```python
async def check_rate_limit(chat_id: int, window: str = "minute") -> bool:
    key = f"ava:ratelimit:{chat_id}:{window}"
    current = await redis.incr(key)

    if current == 1:
        await redis.expire(key, get_window_seconds(window))

    return current <= get_limit(window)
```

**Benefits:**
- **User Protection:** Prevents accidental spam
- **API Protection:** Avoids exceeding Robinhood/TradingView rate limits
- **Cost Control:** Limits expensive AI API calls
- **DDoS Protection:** Mitigates abuse

---

## 6. Key Considerations

### 6.1 Scalability

**Current Capacity:**
- 1 bot instance
- Polling mode: ~20 messages/second max
- Single DB connection per request
- No caching

**Target Capacity (Enhanced):**
- 4 RQ workers (parallel processing)
- Webhook mode: 100+ messages/second
- 20 pooled DB connections
- Redis caching: 1000+ req/s

**Scaling Strategy:**

**Vertical Scaling (0-1000 users):**
- Increase worker count: 4 → 8 → 16
- Increase connection pool: 20 → 50
- Add more RAM for Redis cache

**Horizontal Scaling (1000+ users):**
- Load balancer for webhook servers
- Redis Cluster for queue distribution
- Read replicas for PostgreSQL
- Sharding by chat_id if needed

**Bottlenecks Identified:**
1. **Voice Transcription:** Whisper model (tiny) = 5-10s/message
   - **Solution:** Queue voice messages separately, use GPU acceleration
2. **Robinhood API:** 5 req/s rate limit
   - **Solution:** Cache responses, batch requests, circuit breaker
3. **Database Writes:** Message logging creates write load
   - **Solution:** Batch inserts, use TimescaleDB for time-series data

### 6.2 Security

**Threat Model:**

| Threat | Mitigation |
|--------|-----------|
| Unauthorized access | Authorization code system, whitelist chat IDs |
| Webhook spoofing | Validate X-Telegram-Bot-Api-Secret-Token header |
| SQL injection | Parameterized queries with asyncpg |
| Rate limit bypass | Multi-tier rate limiting (IP + chat_id) |
| Credential exposure | Encrypt .env, use AWS Secrets Manager in prod |
| Man-in-the-middle | TLS 1.2+ for all external connections |
| Session hijacking | Short-lived Redis sessions (1 hour TTL) |

**Authentication Flow:**
```
1. User sends /start
2. Bot generates 6-digit code
3. Bot DMs code to user's Telegram
4. User confirms code via dashboard
5. chat_id marked as authorized in DB
6. All subsequent requests validated against authorized list
```

**PII Protection:**
- No credit card data stored
- Portfolio balances aggregated (no individual holdings exposed)
- Message logs purged after 30 days
- Voice recordings deleted after transcription

### 6.3 Observability

**Metrics Collection (Prometheus):**
```python
# Counter metrics
telegram_messages_total{type="text", status="success"}
telegram_messages_total{type="voice", status="failed"}

# Histogram metrics
telegram_message_processing_duration_seconds{handler="portfolio"}
database_query_duration_seconds{table="positions"}

# Gauge metrics
telegram_active_conversations
redis_queue_length{priority="high"}
database_connection_pool_size
```

**Grafana Dashboards:**
1. **Bot Health Dashboard**
   - Message throughput (req/s)
   - Error rate (% failed)
   - Average response time
   - Queue length
   - Worker utilization

2. **User Engagement Dashboard**
   - Active users (daily/weekly/monthly)
   - Most used commands
   - Conversation completion rate
   - Voice vs text usage ratio

3. **Infrastructure Dashboard**
   - Database connection pool usage
   - Redis memory usage
   - API rate limit status (Robinhood, TradingView)
   - Cache hit ratio

**Logging Strategy:**
```python
# Structured logging with correlation IDs
logger.info(
    "Message processed",
    extra={
        "correlation_id": "abc123",
        "chat_id": 987654321,
        "handler": "PortfolioHandler",
        "duration_ms": 150,
        "cache_hit": True
    }
)
```

**Error Tracking (Sentry):**
- Capture all unhandled exceptions
- Group by error type and handler
- Alert on error rate spike (>5% failure rate)
- Weekly digest of top errors

### 6.4 Deployment & CI/CD

**Docker Compose Stack:**
```yaml
version: '3.8'

services:
  webhook:
    image: ava-telegram-webhook:latest
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379
      - DATABASE_URL=postgresql://...
    depends_on:
      - redis
      - postgres
    restart: unless-stopped

  worker:
    image: ava-telegram-worker:latest
    command: rq worker -c worker_config
    replicas: 4
    depends_on:
      - redis
      - postgres
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped

  postgres:
    image: postgres:15-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3001:3000"
    depends_on:
      - prometheus

volumes:
  redis_data:
  postgres_data:
```

**Systemd Service (for bare metal deployment):**
```ini
[Unit]
Description=AVA Telegram Bot
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=ava
WorkingDirectory=/opt/ava-telegram
ExecStart=/usr/bin/docker-compose up
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Health Checks:**
```python
# /health endpoint
{
  "status": "healthy",
  "version": "2.0.0",
  "uptime_seconds": 86400,
  "components": {
    "redis": {"status": "up", "latency_ms": 2},
    "database": {"status": "up", "latency_ms": 15},
    "telegram_api": {"status": "up", "latency_ms": 50},
    "robinhood_api": {"status": "degraded", "error": "rate_limited"}
  },
  "queue_stats": {
    "high": {"length": 0, "processing": 1},
    "normal": {"length": 5, "processing": 2},
    "low": {"length": 20, "processing": 1}
  }
}
```

---

## 7. Conversation State Management (Multi-Step Workflows)

### 7.1 Finite State Machine Design

**States:**
```python
class ConversationState(Enum):
    IDLE = "idle"

    # Stock analysis workflow
    AWAITING_TICKER = "awaiting_ticker"
    AWAITING_STRATEGY_TYPE = "awaiting_strategy_type"
    AWAITING_CONFIRMATION = "awaiting_confirmation"

    # Trade execution workflow
    REVIEWING_TRADE = "reviewing_trade"
    AWAITING_TRADE_APPROVAL = "awaiting_trade_approval"
    EXECUTING_TRADE = "executing_trade"

    # Portfolio review workflow
    SHOWING_POSITIONS = "showing_positions"
    POSITION_DETAIL = "position_detail"

    # Error states
    ERROR = "error"
    TIMEOUT = "timeout"
```

**Transitions:**
```python
transitions = [
    {"trigger": "start_analysis", "source": "idle", "dest": "awaiting_ticker"},
    {"trigger": "ticker_provided", "source": "awaiting_ticker", "dest": "awaiting_strategy_type"},
    {"trigger": "strategy_selected", "source": "awaiting_strategy_type", "dest": "awaiting_confirmation"},
    {"trigger": "confirm", "source": "awaiting_confirmation", "dest": "executing_trade"},
    {"trigger": "cancel", "source": "*", "dest": "idle"},
    {"trigger": "timeout", "source": "*", "dest": "timeout"},
]
```

### 7.2 Example Workflow: Stock Analysis

**Flow:**
```
User: "Analyze a stock for me"
  ↓
State: IDLE → AWAITING_TICKER
Bot: "Sure! Which ticker would you like me to analyze? (e.g., AAPL, NVDA)"
  ↓
User: "NVDA"
  ↓
State: AWAITING_TICKER → AWAITING_STRATEGY_TYPE
Bot: "Got it, NVDA. What strategy?
     1. Cash-Secured Put
     2. Covered Call
     3. Wheel Strategy
     (Reply with number or name)"
  ↓
User: "1"
  ↓
State: AWAITING_STRATEGY_TYPE → AWAITING_CONFIRMATION
Bot: "Great! Analyzing NVDA for Cash-Secured Put...

     📊 Analysis Results:
     Current Price: $495.50
     IV Rank: 32.5% (moderate)
     Support Level: $480

     💡 Recommendation:
     Sell NVDA Dec 15 $470 Put
     Premium: $5.80 ($580 per contract)
     Probability of Profit: 68%

     Would you like to:
     1. ✅ Execute this trade
     2. 📊 See more details
     3. 🔄 Try different strike
     4. ❌ Cancel"
  ↓
User: "2"
  ↓
State: AWAITING_CONFIRMATION → SHOWING_POSITION_DETAIL
Bot: "📈 Detailed Analysis:
     [Greeks, technicals, news, etc.]

     Ready to execute? (yes/no)"
  ↓
User: "yes"
  ↓
State: EXECUTING_TRADE
Bot: "🔄 Sending order to Robinhood...
     ✅ Order placed successfully!
     Order ID: #12345

     I'll monitor this position for you."
  ↓
State: EXECUTING_TRADE → IDLE
```

**Implementation:**
```python
class StockAnalysisWorkflow:
    def __init__(self, chat_id: int, state_manager: StateManager):
        self.chat_id = chat_id
        self.state = state_manager

    async def handle_message(self, message: str):
        current_state = await self.state.get_state(self.chat_id)

        if current_state == ConversationState.AWAITING_TICKER:
            ticker = self.extract_ticker(message)
            if ticker:
                await self.state.set_context(self.chat_id, {"ticker": ticker})
                await self.state.transition_to(self.chat_id, ConversationState.AWAITING_STRATEGY_TYPE)
                return self.render_strategy_menu()
            else:
                return "I didn't recognize that ticker. Please try again (e.g., AAPL, MSFT)"

        elif current_state == ConversationState.AWAITING_STRATEGY_TYPE:
            strategy = self.parse_strategy(message)
            if strategy:
                await self.state.set_context(self.chat_id, {"strategy": strategy})
                analysis = await self.analyze_stock()
                await self.state.transition_to(self.chat_id, ConversationState.AWAITING_CONFIRMATION)
                return self.render_analysis(analysis)
            else:
                return "Please select a valid strategy (1-3)"

        # ... more state handlers
```

### 7.3 Timeout Handling

**Configuration:**
```python
STATE_TIMEOUTS = {
    "awaiting_ticker": timedelta(minutes=5),
    "awaiting_strategy_type": timedelta(minutes=3),
    "awaiting_confirmation": timedelta(minutes=10),
    "executing_trade": timedelta(minutes=2),
}
```

**Background Job:**
```python
# Run every minute
async def cleanup_expired_conversations():
    expired = await redis.zrangebyscore(
        "ava:state:timeouts",
        min=0,
        max=int(datetime.now().timestamp())
    )

    for chat_id in expired:
        await state_manager.transition_to(chat_id, ConversationState.TIMEOUT)
        await bot.send_message(
            chat_id,
            "⏱️ Your conversation timed out due to inactivity. "
            "Send /start to begin again."
        )
        await redis.zrem("ava:state:timeouts", chat_id)
```

---

## 8. Error Recovery and Retry Mechanisms

### 8.1 Retry Strategy

**Exponential Backoff Configuration:**
```python
RETRY_CONFIG = {
    "max_retries": 3,
    "base_delay": 1.0,  # seconds
    "max_delay": 60.0,
    "exponential_base": 2,
    "jitter": True,
}

def calculate_retry_delay(attempt: int) -> float:
    delay = min(
        RETRY_CONFIG["base_delay"] * (RETRY_CONFIG["exponential_base"] ** attempt),
        RETRY_CONFIG["max_delay"]
    )
    if RETRY_CONFIG["jitter"]:
        delay *= (0.5 + random.random() * 0.5)  # ±25% jitter
    return delay
```

**Retry Scenarios:**

| Failure Type | Retry? | Max Retries | Strategy |
|--------------|--------|-------------|----------|
| Network timeout | ✅ Yes | 3 | Exponential backoff |
| Rate limit (429) | ✅ Yes | 5 | Wait + exponential |
| Database deadlock | ✅ Yes | 3 | Immediate retry |
| Invalid input | ❌ No | 0 | Return error to user |
| Authentication failure | ❌ No | 0 | Alert admin |
| Out of memory | ❌ No | 0 | Fail fast + alert |

### 8.2 Circuit Breaker Pattern

**Implementation:**
```python
class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.state = "closed"  # closed, open, half_open
        self.last_failure_time = None

    async def call(self, func, *args, **kwargs):
        if self.state == "open":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "half_open"
            else:
                raise CircuitBreakerOpenError("Circuit breaker is open")

        try:
            result = await func(*args, **kwargs)
            if self.state == "half_open":
                self.state = "closed"
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.failure_count >= self.failure_threshold:
                self.state = "open"
                logger.error(f"Circuit breaker opened: {func.__name__}")

            raise

# Usage
robinhood_breaker = CircuitBreaker(failure_threshold=3, timeout=120)

async def get_positions():
    return await robinhood_breaker.call(
        robinhood_client.get_positions
    )
```

### 8.3 Dead Letter Queue

**Flow:**
```
Message → Queue (Normal) → Worker
                              ↓ (failure)
Message → Queue (Normal) → Worker (retry 1)
                              ↓ (failure)
Message → Queue (Normal) → Worker (retry 2)
                              ↓ (failure)
Message → Queue (Normal) → Worker (retry 3)
                              ↓ (failure)
Message → Queue (DLQ) → Manual Review
```

**DLQ Processing:**
```python
# Monitor DLQ
async def monitor_dead_letter_queue():
    while True:
        dlq_length = await redis.llen("ava:messages:dead_letter")

        if dlq_length > 10:
            # Alert admin via Telegram
            await bot.send_message(
                ADMIN_CHAT_ID,
                f"⚠️ Dead Letter Queue Alert\n"
                f"Messages in DLQ: {dlq_length}\n"
                f"Last error: {await get_last_dlq_error()}"
            )

        await asyncio.sleep(300)  # Check every 5 minutes
```

### 8.4 Graceful Degradation

**Priority Levels:**
```python
# If external APIs fail, fall back to cached data
async def get_portfolio_balance(user_id: int) -> dict:
    try:
        # Try fresh data from Robinhood
        balance = await robinhood_client.get_balance()
        await cache.set(f"portfolio:{user_id}", balance, ttl=300)
        return balance
    except RobinhoodAPIError:
        # Fall back to cached data
        cached = await cache.get(f"portfolio:{user_id}")
        if cached:
            logger.warning("Using cached portfolio data (Robinhood unavailable)")
            return {**cached, "stale": True, "cached_at": cached["timestamp"]}
        else:
            # Last resort: database
            return await db.get_last_known_balance(user_id)
```

---

## 9. Integration Patterns

### 9.1 Robinhood Integration

**Architecture:**
```
Telegram Bot → RobinhoodClient (Wrapper)
                    ↓
               robin_stocks
                    ↓
               Robinhood API
```

**Rate Limiting:**
```python
class RateLimitedRobinhoodClient:
    def __init__(self):
        self.limiter = AsyncLimiter(max_rate=5, time_period=1)  # 5 req/s

    @retry(max_attempts=3, backoff=exponential)
    @circuit_breaker(threshold=5, timeout=120)
    async def get_positions(self):
        async with self.limiter:
            return await asyncio.to_thread(rh.get_open_stock_positions)
```

**Response Caching:**
```python
# Cache portfolio data for 5 minutes
@cached(ttl=300, key="rh:portfolio:{user_id}")
async def get_portfolio(user_id: int):
    return await robinhood_client.get_account_info()

# Cache positions for 30 seconds (more volatile)
@cached(ttl=30, key="rh:positions:{user_id}")
async def get_positions(user_id: int):
    return await robinhood_client.get_all_positions()
```

**Error Handling:**
```python
try:
    positions = await robinhood_client.get_positions()
except RobinhoodLoginError:
    # Session expired, re-login
    await robinhood_client.login()
    positions = await robinhood_client.get_positions()
except RobinhoodRateLimitError as e:
    # Wait and retry
    await asyncio.sleep(e.retry_after)
    positions = await robinhood_client.get_positions()
except RobinhoodMaintenanceError:
    # Use cached data
    positions = await cache.get("rh:positions:{user_id}")
```

### 9.2 TradingView Integration

**Architecture:**
```
Telegram Bot → TradingViewClient (WebSocket)
                    ↓
               TradingView API
                    ↓
               Real-time Market Data
```

**WebSocket Connection:**
```python
class TradingViewWebSocket:
    async def connect(self):
        self.ws = await websockets.connect(
            "wss://data.tradingview.com/socket.io/...",
            extra_headers={"Authorization": f"Bearer {token}"}
        )

        # Send authentication
        await self.ws.send(json.dumps({
            "m": "auth",
            "p": [self.session_id]
        }))

        # Subscribe to quotes
        await self.ws.send(json.dumps({
            "m": "quote_add_symbols",
            "p": [self.session, ["NASDAQ:AAPL", "NASDAQ:NVDA"]]
        }))

        # Start listening
        asyncio.create_task(self.listen())

    async def listen(self):
        async for message in self.ws:
            data = json.loads(message)
            if data["m"] == "qsd":  # Quote data
                await self.handle_quote_update(data["p"])
```

**Auto-Reconnect:**
```python
async def maintain_connection(self):
    while True:
        try:
            await self.connect()
        except websockets.ConnectionClosed:
            logger.warning("TradingView connection lost, reconnecting in 5s...")
            await asyncio.sleep(5)
        except Exception as e:
            logger.error(f"TradingView connection error: {e}")
            await asyncio.sleep(30)
```

### 9.3 Xtrades Integration

**Scraping Strategy:**
```python
class XtradesClient:
    def __init__(self):
        self.session = httpx.AsyncClient()
        self.cookies = None

    async def login(self):
        # Discord OAuth flow
        response = await self.session.post(
            "https://app.xtrades.net/api/auth/discord",
            json={"email": XTRADES_USERNAME, "password": XTRADES_PASSWORD}
        )
        self.cookies = response.cookies

    @retry(max_attempts=3)
    async def get_alerts(self, profile_username: str):
        response = await self.session.get(
            f"https://app.xtrades.net/api/profiles/{profile_username}/alerts",
            cookies=self.cookies
        )
        return response.json()
```

**Webhook Alternative:**
```python
# If Xtrades provides webhook support
@app.post("/webhooks/xtrades")
async def xtrades_webhook(payload: dict, signature: str):
    # Validate signature
    if not verify_xtrades_signature(payload, signature):
        raise HTTPException(401, "Invalid signature")

    # Process alert
    alert = payload["alert"]
    await process_trade_alert(alert)

    return {"status": "received"}
```

### 9.4 Database Query Optimization

**Connection Pooling:**
```python
# Global pool
pool = await asyncpg.create_pool(
    dsn=DATABASE_URL,
    min_size=5,
    max_size=20,
    max_inactive_connection_lifetime=300,
    command_timeout=30
)

# Usage
async def get_user(chat_id: int):
    async with pool.acquire() as conn:
        return await conn.fetchrow(
            "SELECT * FROM telegram_users WHERE chat_id = $1",
            chat_id
        )
```

**Query Caching:**
```python
# Cache expensive aggregations
@cached(ttl=600, key="stats:daily_pnl")
async def get_daily_pnl_summary():
    return await db.fetch_one("""
        SELECT
            SUM(pnl) as total_pnl,
            AVG(pnl_percent) as avg_return,
            COUNT(*) FILTER (WHERE pnl > 0) as winning_trades
        FROM xtrades_alerts
        WHERE created_at::date = CURRENT_DATE
    """)
```

---

## 10. Implementation Roadmap

### Phase 1: Foundation (Week 1-2)
- ✅ Set up Docker Compose environment
- ✅ Implement webhook server with FastAPI
- ✅ Set up Redis for message queue
- ✅ Create database schema migrations
- ✅ Implement basic RQ workers
- ✅ Add health check endpoints

**Deliverable:** Webhook server processing basic text messages

### Phase 2: State Management (Week 3)
- ✅ Implement state manager with Redis FSM
- ✅ Create workflow classes (stock analysis, trade execution)
- ✅ Add timeout handling for conversations
- ✅ Build conversation context storage

**Deliverable:** Multi-step stock analysis workflow

### Phase 3: Reliability (Week 4)
- ✅ Add retry logic with exponential backoff
- ✅ Implement circuit breaker for external APIs
- ✅ Set up dead letter queue
- ✅ Add rate limiting (per-user and global)
- ✅ Implement connection pooling

**Deliverable:** Robust error handling and recovery

### Phase 4: Performance (Week 5)
- ✅ Implement Redis caching layer
- ✅ Add cache invalidation strategies
- ✅ Optimize database queries with indexes
- ✅ Profile and optimize bottlenecks

**Deliverable:** < 100ms response time for cached queries

### Phase 5: Observability (Week 6)
- ✅ Set up Prometheus metrics collection
- ✅ Create Grafana dashboards
- ✅ Add structured logging with correlation IDs
- ✅ Integrate Sentry for error tracking
- ✅ Set up alerting (PagerDuty or Telegram)

**Deliverable:** Comprehensive monitoring and alerting

### Phase 6: Integration (Week 7-8)
- ✅ Enhance Robinhood client with rate limiting
- ✅ Implement TradingView WebSocket client
- ✅ Add Xtrades webhook handling
- ✅ Build trade execution workflow
- ✅ Add position monitoring

**Deliverable:** End-to-end trade workflow from Telegram to Robinhood

### Phase 7: Production Hardening (Week 9-10)
- ✅ Load testing (1000 concurrent users)
- ✅ Security audit (OWASP Top 10)
- ✅ Disaster recovery testing
- ✅ Documentation and runbooks
- ✅ Production deployment

**Deliverable:** Production-ready 24/7 system

---

## 11. Success Metrics

### 11.1 Performance Targets

| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| **Average Response Time** | 1-5s | < 500ms | 95th percentile |
| **Message Throughput** | 20 msg/s | 100 msg/s | Sustained load |
| **Uptime** | Unknown | 99.9% | Monthly |
| **Error Rate** | Unknown | < 0.5% | Per 1000 messages |
| **Cache Hit Rate** | 0% | > 80% | Portfolio/positions |
| **Database Query Time** | 50-200ms | < 20ms | With caching |
| **Voice Transcription** | 5-10s | < 3s | Whisper tiny model |

### 11.2 Reliability Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Mean Time Between Failures (MTBF)** | > 30 days | Crash frequency |
| **Mean Time To Recovery (MTTR)** | < 5 minutes | Auto-restart |
| **Data Loss on Failure** | 0 messages | Message durability |
| **Concurrent Conversations** | 100+ | Simultaneous users |

### 11.3 User Experience Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Conversation Completion Rate** | > 85% | Users finishing workflows |
| **Command Success Rate** | > 95% | /portfolio, /tasks, etc. |
| **User Satisfaction** | > 4.5/5 | In-app rating |
| **Daily Active Users** | Track growth | Engagement |

---

## 12. Cost Analysis

### 12.1 Infrastructure Costs (Monthly)

| Component | Provider | Cost |
|-----------|----------|------|
| **VPS (4 vCPU, 8GB RAM)** | DigitalOcean | $48 |
| **Redis (Managed)** | Redis Cloud | $10 |
| **PostgreSQL (Managed)** | DigitalOcean | $15 |
| **Domain + SSL** | Cloudflare | $0 |
| **Monitoring (Grafana Cloud)** | Grafana | $0 (free tier) |
| **Error Tracking (Sentry)** | Sentry | $0 (free tier) |
| **Telegram API** | Telegram | $0 |
| **Total Infrastructure** | | **$73/month** |

### 12.2 API Costs (Monthly, 1000 users)

| Service | Calls/Month | Cost/Call | Total |
|---------|-------------|-----------|-------|
| **Anthropic Claude (queries)** | 10,000 | $0.01 | $100 |
| **Whisper (local)** | 5,000 | $0 | $0 |
| **Robinhood API** | 50,000 | $0 | $0 |
| **TradingView API** | 100,000 | $0 | $0 |
| **Total API** | | | **$100/month** |

**Grand Total: ~$175/month for 1000 active users**

---

## 13. Appendix

### 13.1 File Structure

```
c:\Code\WheelStrategy\
├── src/
│   ├── ava/
│   │   ├── __init__.py
│   │   ├── telegram_bot.py (legacy polling bot)
│   │   ├── webhook_server.py (NEW: FastAPI webhook)
│   │   ├── message_processor.py (NEW: RQ worker)
│   │   ├── state_manager.py (NEW: FSM state management)
│   │   ├── db_manager.py (NEW: asyncpg connection pool)
│   │   ├── cache_manager.py (NEW: Redis caching)
│   │   ├── rate_limiter.py (NEW: Rate limiting)
│   │   ├── voice_handler.py (existing, enhanced)
│   │   ├── workflows/
│   │   │   ├── __init__.py
│   │   │   ├── base_workflow.py
│   │   │   ├── stock_analysis_workflow.py
│   │   │   ├── trade_execution_workflow.py
│   │   │   └── portfolio_review_workflow.py
│   │   ├── handlers/
│   │   │   ├── __init__.py
│   │   │   ├── command_handler.py
│   │   │   ├── text_handler.py
│   │   │   ├── voice_handler.py
│   │   │   └── callback_handler.py
│   │   ├── integrations/
│   │   │   ├── __init__.py
│   │   │   ├── robinhood_client.py (enhanced)
│   │   │   ├── tradingview_client.py (NEW: WebSocket)
│   │   │   └── xtrades_client.py (enhanced)
│   │   ├── migrations/
│   │   │   └── 001_telegram_enhancements.sql
│   │   └── schema.sql (existing, updated)
│   └── telegram_notifier.py (existing, unchanged)
├── docker/
│   ├── Dockerfile.webhook
│   ├── Dockerfile.worker
│   └── docker-compose.yml
├── config/
│   ├── webhook_config.yaml
│   ├── worker_config.py
│   ├── prometheus.yml
│   └── grafana_dashboards/
│       ├── bot_health.json
│       └── user_engagement.json
├── tests/
│   ├── test_webhook_server.py
│   ├── test_message_processor.py
│   ├── test_state_manager.py
│   └── test_integrations.py
├── docs/
│   └── architecture/
│       └── ava-telegram-bot-architecture.md (this file)
└── .env (enhanced with new variables)
```

### 13.2 Environment Variables

**New variables to add to `.env`:**
```bash
# Webhook Configuration
TELEGRAM_WEBHOOK_URL=https://your-domain.com/webhook/7552232147:AAGAdwZh-SmesrtndZdsMAaKFDms-C2Z5ww
TELEGRAM_WEBHOOK_SECRET_TOKEN=<random_64_char_string>
TELEGRAM_USE_WEBHOOKS=true  # Set to false for polling mode

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
REDIS_MAX_CONNECTIONS=50
REDIS_SOCKET_KEEPALIVE=true

# Database Pool Configuration
DB_POOL_MIN_SIZE=5
DB_POOL_MAX_SIZE=20
DB_POOL_TIMEOUT=10

# Rate Limiting
RATE_LIMIT_MESSAGES_PER_MINUTE=5
RATE_LIMIT_MESSAGES_PER_HOUR=50
RATE_LIMIT_MESSAGES_PER_DAY=200

# Monitoring
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
PROMETHEUS_PORT=9090
GRAFANA_ADMIN_PASSWORD=<secure_password>

# Security
AUTHORIZED_CHAT_IDS=987654321,123456789  # Comma-separated list
ADMIN_CHAT_ID=987654321  # For error alerts
```

### 13.3 Key Dependencies

**New dependencies to add to `requirements.txt`:**
```
# Webhook server
fastapi==0.104.1
uvicorn[standard]==0.24.0

# Message queue
rq==1.15.1
rq-dashboard==0.6.1

# Async database
asyncpg==0.29.0

# Caching
redis==5.0.1
hiredis==2.2.3  # C parser for speed

# Rate limiting
redis-rate-limit==0.0.4

# Monitoring
prometheus-client==0.19.0
sentry-sdk==1.38.0

# HTTP clients
httpx==0.25.2  # Async HTTP

# WebSockets
websockets==12.0

# Existing dependencies (keep)
python-telegram-bot==20.7
openai-whisper==20231117
psycopg2-binary==2.9.9
python-dotenv==1.0.0
```

---

## Conclusion

This architecture transforms the AVA Telegram bot from a simple notification tool into a production-grade 24/7 trading assistant with:

1. **Scalability:** Handle 100+ messages/second with horizontal scaling
2. **Reliability:** 99.9% uptime with auto-recovery and circuit breakers
3. **State Management:** Multi-step workflows with timeout handling
4. **Performance:** < 100ms response time with Redis caching
5. **Observability:** Comprehensive metrics, logging, and alerting
6. **Security:** Rate limiting, authentication, PII protection

**Next Steps:**
1. Review and approve architecture
2. Begin Phase 1 implementation (webhook server)
3. Set up staging environment for testing
4. Plan production cutover strategy

**Questions or feedback?** Please reach out to the architecture team.

---

**Document End**
