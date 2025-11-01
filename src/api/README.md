# AI Research API

FastAPI-based research API with multi-agent analysis, Redis caching, and rate limiting.

## Features

- **Multi-Agent Analysis**: Coordinates 4 specialist agents using CrewAI
  - Fundamental Analyst: Company financials, earnings, valuation
  - Technical Analyst: Price action, indicators, chart patterns
  - Sentiment Analyst: News, social media, insider trades, analyst ratings
  - Options Strategist: IV analysis, options flow, strategy recommendations

- **LLM Synthesis**: Uses Ollama (local) or OpenAI GPT to synthesize agent outputs into coherent recommendations

- **Redis Caching**: 30-minute TTL cache to reduce API calls and improve response times

- **Rate Limiting**: Token bucket algorithm (10 req/min per user by default)

- **Adaptive Rate Limiting**: Support for tiered rate limits (free/premium/enterprise)

## Architecture

```
┌─────────────────┐
│  FastAPI API    │
│  (Endpoints)    │
└────────┬────────┘
         │
    ┌────┴────┐
    │  Cache  │  ◄── Redis (30min TTL)
    └────┬────┘
         │
    ┌────┴────────────┐
    │  Orchestrator   │  ◄── CrewAI + LLM
    └────┬────────────┘
         │
    ┌────┴──────────────────────────────┐
    │                                   │
┌───┴────────┐  ┌────────────┐  ┌──────┴──────┐  ┌──────────────┐
│Fundamental │  │ Technical  │  │  Sentiment  │  │   Options    │
│   Agent    │  │   Agent    │  │    Agent    │  │    Agent     │
└────────────┘  └────────────┘  └─────────────┘  └──────────────┘
```

## API Endpoints

### 1. Get Research Report (Cached)

```http
GET /api/research/{symbol}
```

**Query Parameters:**
- `force_refresh` (bool): Bypass cache and generate fresh analysis
- `include_fundamental` (bool): Include fundamental analysis (default: true)
- `include_technical` (bool): Include technical analysis (default: true)
- `include_sentiment` (bool): Include sentiment analysis (default: true)
- `include_options` (bool): Include options analysis (default: true)

**Example:**
```bash
curl http://localhost:8000/api/research/AAPL
```

**Response:**
```json
{
  "symbol": "AAPL",
  "timestamp": "2025-11-01T14:30:00",
  "cached": false,
  "overall_rating": 4.2,
  "quick_summary": "AAPL shows strong fundamentals with moderate technical signals...",
  "analysis": {
    "fundamental": { ... },
    "technical": { ... },
    "sentiment": { ... },
    "options": { ... },
    "recommendation": {
      "action": "BUY",
      "confidence": 0.75,
      "reasoning": "...",
      "time_sensitive_factors": [...],
      "specific_position_advice": {...}
    }
  },
  "metadata": {
    "api_calls_used": 15,
    "processing_time_ms": 3250,
    "agents_executed": 4,
    "agents_failed": [],
    "cache_expires_at": "2025-11-01T15:00:00",
    "llm_model": "llama3.2",
    "llm_tokens_used": 2500
  }
}
```

**Headers:**
- `X-Cache`: `HIT` or `MISS` or `STALE`

### 2. Force Refresh Research

```http
GET /api/research/{symbol}/refresh
```

Forces fresh analysis, bypassing cache.

### 3. Check Cache Status

```http
GET /api/research/{symbol}/status
```

Returns cache metadata without generating new analysis.

**Response:**
```json
{
  "symbol": "AAPL",
  "cached": true,
  "timestamp": "2025-11-01T14:30:00",
  "age_seconds": 450,
  "expires_in_seconds": 1350,
  "overall_rating": 4.2
}
```

### 4. Clear Cache

```http
DELETE /api/research/{symbol}/cache
```

Manually clear cached research for a symbol.

### 5. Health Check

```http
GET /health
```

Returns service health status.

## Rate Limiting

Default: **10 requests per minute** per user (identified by IP).

**Rate Limit Headers:**
When rate limit is exceeded, returns HTTP 429 with:
```json
{
  "error_code": "RATE_LIMIT_EXCEEDED",
  "error_message": "Rate limit exceeded. Maximum 10 requests per 60 seconds.",
  "retry_after_seconds": 45
}
```

### Adaptive Rate Limiting

Support for tiered rate limits:

```python
from src.api.rate_limiter import AdaptiveRateLimiter

limiter = AdaptiveRateLimiter(
    redis_cache=redis,
    tier_limits={
        'free': (10, 60),      # 10 req/min
        'premium': (100, 60),  # 100 req/min
        'enterprise': (1000, 60)  # 1000 req/min
    }
)

# Set user tier
await limiter.set_user_tier('user123', 'premium')
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install and Start Redis

**macOS (Homebrew):**
```bash
brew install redis
brew services start redis
```

**Ubuntu/Debian:**
```bash
sudo apt-get install redis-server
sudo systemctl start redis-server
```

**Windows (WSL or Docker):**
```bash
docker run -d -p 6379:6379 redis:latest
```

**Verify Redis:**
```bash
redis-cli ping
# Should return: PONG
```

### 3. Install Ollama (for local LLM)

**Option A: Ollama (Recommended - Free & Local)**

1. Install Ollama:
```bash
# macOS/Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Windows
# Download from https://ollama.ai/download
```

2. Pull model:
```bash
ollama pull llama3.2
```

3. Verify:
```bash
ollama run llama3.2
```

**Option B: OpenAI GPT**

Set environment variable:
```bash
export OPENAI_API_KEY="sk-..."
```

### 4. Configure Environment

Create `.env` file:
```bash
# LLM Configuration
LLM_PROVIDER=ollama  # or 'openai'
LLM_MODEL=llama3.2   # or 'gpt-4'

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Rate Limiting
RATE_LIMIT_MAX_REQUESTS=10
RATE_LIMIT_WINDOW_SECONDS=60

# API Keys (optional)
ALPHA_VANTAGE_API_KEY=your_key_here
REDDIT_CLIENT_ID=your_id_here
REDDIT_CLIENT_SECRET=your_secret_here
```

### 5. Run the API

```bash
# Development
uvicorn src.api.research_endpoints:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn src.api.research_endpoints:app --workers 4 --host 0.0.0.0 --port 8000
```

API will be available at `http://localhost:8000`

Interactive docs: `http://localhost:8000/docs`

## Usage Examples

### Python Client

```python
import requests

# Get research
response = requests.get('http://localhost:8000/api/research/AAPL')
report = response.json()

print(f"Rating: {report['overall_rating']}/5.0")
print(f"Summary: {report['quick_summary']}")
print(f"Action: {report['analysis']['recommendation']['action']}")

# Force refresh
response = requests.get('http://localhost:8000/api/research/AAPL/refresh')

# Check cache
response = requests.get('http://localhost:8000/api/research/AAPL/status')
status = response.json()
print(f"Cache age: {status['age_seconds']}s")
```

### cURL

```bash
# Get research
curl http://localhost:8000/api/research/AAPL | jq

# Force refresh
curl http://localhost:8000/api/research/AAPL/refresh | jq

# Clear cache
curl -X DELETE http://localhost:8000/api/research/AAPL/cache

# Health check
curl http://localhost:8000/health
```

### JavaScript/TypeScript

```typescript
const getResearch = async (symbol: string) => {
  const response = await fetch(`http://localhost:8000/api/research/${symbol}`);
  const data = await response.json();

  if (response.headers.get('X-Cache') === 'HIT') {
    console.log('Served from cache');
  }

  return data;
};

const report = await getResearch('AAPL');
console.log(report.overall_rating);
```

## Performance

### Typical Response Times

- **Cache Hit**: 10-50ms
- **Cache Miss (Fresh Analysis)**: 2-5 seconds
  - Fundamental: 500-800ms
  - Technical: 400-600ms
  - Sentiment: 600-1000ms
  - Options: 800-1200ms
  - LLM Synthesis: 500-1500ms

### Optimization Tips

1. **Use Cache**: Don't force refresh unless necessary
2. **Selective Sections**: Only request needed analysis sections
3. **Batch Requests**: Pre-fetch common symbols during off-hours
4. **Monitor Rate Limits**: Implement exponential backoff

## Redis Cache Management

### Manual Cache Operations

```python
from src.api.redis_cache import RedisCache

cache = RedisCache()
await cache.connect()

# Check if cached
exists = await cache.exists('research:AAPL')

# Get TTL
ttl = await cache.get_ttl('research:AAPL')
print(f"Expires in {ttl}s")

# Clear all research cache
deleted = await cache.clear_pattern('research:*')
print(f"Cleared {deleted} keys")

# Get cache stats
stats = await cache.get_stats()
print(stats)
```

### Cache Invalidation Strategy

- **TTL**: 30 minutes default
- **Manual Clear**: After earnings, major news
- **Stale-While-Revalidate**: Serve stale data if fresh generation fails

## Error Handling

### Common Errors

**429 Too Many Requests**
```json
{
  "error_code": "RATE_LIMIT_EXCEEDED",
  "error_message": "...",
  "retry_after_seconds": 45
}
```

**500 Internal Server Error**
```json
{
  "error_code": "ANALYSIS_FAILED",
  "error_message": "Fundamental analysis failed: API timeout",
  "cached_data_available": true
}
```

**400 Bad Request**
```json
{
  "error_code": "INVALID_SYMBOL",
  "error_message": "Symbol must be 1-10 characters"
}
```

### Graceful Degradation

1. **Agent Failure**: Other agents still run, LLM synthesizes partial results
2. **LLM Failure**: Falls back to rule-based synthesis
3. **All Failures**: Returns cached data (if available) with error headers

## Testing

```bash
# Run unit tests
pytest tests/test_research_api.py -v

# Load test
locust -f tests/locustfile.py --host http://localhost:8000
```

## Monitoring

### Key Metrics to Track

1. **Cache Hit Rate**: Target >80%
2. **Response Time**: P50 <100ms (cached), P99 <5s (fresh)
3. **Error Rate**: Target <1%
4. **Rate Limit Violations**: Monitor for abuse
5. **Agent Failures**: Track which agents fail most

### Logging

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Logs include:
# - Request details (symbol, user_id, cache status)
# - Agent execution times
# - API call counts
# - Errors and fallbacks
```

## Production Deployment

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "src.api.research_endpoints:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### Docker Compose

```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - REDIS_HOST=redis
      - LLM_PROVIDER=ollama
    depends_on:
      - redis

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  redis_data:
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: research-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: research-api
  template:
    metadata:
      labels:
        app: research-api
    spec:
      containers:
      - name: api
        image: research-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: REDIS_HOST
          value: redis-service
```

## Security Considerations

1. **API Authentication**: Add JWT/API key auth in production
2. **CORS**: Configure allowed origins
3. **Input Validation**: Symbol sanitization
4. **Rate Limiting**: Per-user or per-API-key
5. **Secrets Management**: Use environment variables or vault

## License

MIT
