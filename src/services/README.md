# Services Layer Documentation

A centralized external services layer for the trading dashboard that eliminates duplicate API client code.

## Overview

This package provides thread-safe singleton services for:
- **Robinhood API**: Stock positions, options, account data
- **LLM Providers**: Claude, DeepSeek, Gemini, OpenAI, and more
- **Rate Limiting**: Token bucket algorithm for API throttling
- **Configuration**: Centralized service configs with retry policies

## Key Features

- Thread-safe singleton pattern
- Automatic rate limiting (60 req/min for Robinhood)
- Exponential backoff retry logic
- Session/connection pooling
- Response caching (LLM only)
- Cost tracking (LLM only)
- Comprehensive error handling

## Architecture

```
src/services/
├── __init__.py              # Package exports
├── config.py                # Service configurations
├── rate_limiter.py          # Token bucket rate limiter
├── robinhood_client.py      # Robinhood API client
├── llm_service.py           # Multi-provider LLM service
└── README.md               # This file
```

## Quick Start

### 1. Robinhood Client

```python
from src.services import get_robinhood_client

# Get singleton client
client = get_robinhood_client()

# Login (automatic session caching)
client.login()

# Get account info
account = client.get_account_info()
print(f"Buying Power: ${account['buying_power']:,.2f}")

# Get positions
positions = client.get_positions()
for pos in positions:
    print(f"{pos['symbol']}: {pos['type']}")

# Get market data
data = client.get_market_data('AAPL')
print(f"AAPL: ${data['price']:.2f}")

# Logout
client.logout()
```

### 2. LLM Service

```python
from src.services import get_llm_service

# Get singleton service
llm = get_llm_service()

# Generate with auto-selected provider (free/cheap first)
result = llm.generate(
    "Analyze AAPL for options trading",
    max_tokens=500,
    temperature=0.7
)

print(f"Provider: {result['provider']}")
print(f"Response: {result['text']}")
print(f"Cost: ${result['cost']:.4f}")

# Generate with specific provider
result = llm.generate(
    "What is RSI indicator?",
    provider="deepseek",
    model="deepseek-chat"
)

# Generate with fallback
result = llm.generate_with_fallback(
    "Explain covered calls",
    providers=["groq", "deepseek", "gemini"]
)

# Get usage stats
stats = llm.get_usage_stats()
print(f"Total cost: ${stats['total_cost']:.4f}")
```

### 3. Rate Limiting

```python
from src.services import get_rate_limiter, rate_limit

# Get singleton rate limiter
limiter = get_rate_limiter()

# Check if request is allowed
if limiter.check_limit("robinhood"):
    # Make API call
    pass

# Wait if needed (blocking)
limiter.wait_if_needed("robinhood", timeout=30)

# Use decorator
@rate_limit("robinhood", tokens=1, timeout=30)
def get_positions():
    return rh.get_positions()

# Get stats
stats = limiter.get_stats("robinhood")
print(f"Available tokens: {stats['available_tokens']:.1f}")
print(f"Wait time: {stats['wait_time']:.2f}s")
```

## Detailed Documentation

### Robinhood Client

**File**: `robinhood_client.py`

Thread-safe singleton Robinhood client with automatic session management.

#### Configuration

```python
# Environment variables required:
ROBINHOOD_USERNAME=your_email@example.com
ROBINHOOD_PASSWORD=your_password
ROBINHOOD_MFA_CODE=your_totp_secret  # Optional
```

#### Rate Limits

- **60 requests per minute** (automatic)
- Token bucket algorithm
- Automatic backoff on 429 errors

#### Methods

| Method | Description | Rate Limit |
|--------|-------------|------------|
| `login()` | Login with session caching | N/A |
| `logout()` | Logout and clear session | N/A |
| `get_account_info()` | Get account details | 1 token |
| `get_positions()` | Get all positions | 1 token |
| `get_stock_positions()` | Get stock positions only | 1 token |
| `get_options_positions()` | Get options positions only | 1 token |
| `get_market_data(symbol)` | Get quote for symbol | 1 token |
| `get_options_chain(symbol)` | Get options chain | 2 tokens |
| `get_connection_status()` | Check connection status | N/A |

#### Error Handling

- Automatic retry with exponential backoff (3 attempts)
- Session auto-refresh on expiration
- Graceful degradation (returns empty dict/list on error)
- Comprehensive logging

#### Example: Replace Existing Code

**Before** (duplicate code in multiple files):
```python
import robin_stocks.robinhood as rh

# Login in each file
rh.login(username, password)

# Make API calls
positions = rh.account.get_open_stock_positions()

# No rate limiting, no retry logic
```

**After** (centralized service):
```python
from src.services import get_robinhood_client

# Get singleton (auto-login if needed)
client = get_robinhood_client()

# Rate limiting and retry logic automatic
positions = client.get_stock_positions()
```

### LLM Service

**File**: `llm_service.py`

Unified LLM service with multi-provider support and automatic fallback.

#### Supported Providers

| Provider | Cost | Speed | Quality | API Key |
|----------|------|-------|---------|---------|
| Ollama | Free (local) | Medium | Good | N/A |
| Groq | Free tier | Very Fast | Excellent | GROQ_API_KEY |
| DeepSeek | $0.14/$0.28 per 1M | Fast | Excellent | DEEPSEEK_API_KEY |
| Gemini | Flash: Very cheap | Very Fast | Excellent | GOOGLE_API_KEY |
| OpenAI | $0.15-$10 per 1M | Fast | Excellent | OPENAI_API_KEY |
| Claude | $3-$75 per 1M | Medium | Best | ANTHROPIC_API_KEY |

#### Features

- **Auto-selection**: Picks free/cheap providers first
- **Fallback**: Automatically tries next provider on failure
- **Caching**: In-memory cache with 1-hour TTL
- **Cost tracking**: Tracks tokens and cost per provider
- **Rate limiting**: Automatic per-provider rate limits

#### Methods

| Method | Description |
|--------|-------------|
| `generate(prompt, provider, model, ...)` | Generate text with options |
| `generate_with_fallback(prompt, providers)` | Auto-fallback on errors |
| `get_available_providers()` | List available providers |
| `get_usage_stats(provider)` | Get usage and cost stats |
| `clear_cache()` | Clear response cache |
| `reset_usage()` | Reset usage statistics |

#### Response Format

```python
{
    "text": "Generated response...",
    "provider": "deepseek",
    "model": "deepseek-chat",
    "input_tokens": 150,
    "output_tokens": 300,
    "cost": 0.000084,  # USD
    "cached": False
}
```

#### Example: Replace Existing Code

**Before** (using old LLM manager):
```python
from src.ai_options_agent.llm_manager import get_llm_manager

manager = get_llm_manager()
result = manager.generate(prompt, provider_id="deepseek")
text = result["text"]
```

**After** (using new service):
```python
from src.services import get_llm_service

llm = get_llm_service()
result = llm.generate_with_fallback(prompt)
text = result["text"]
cost = result["cost"]
```

### Rate Limiter

**File**: `rate_limiter.py`

Token bucket rate limiter with per-service limits.

#### Algorithm

- **Token Bucket**: Allows bursts, refills at steady rate
- **Thread-safe**: Uses locks for concurrent access
- **Configurable**: Per-service limits from config

#### Configuration

Rate limits are defined in `config.py`:

```python
ROBINHOOD_CONFIG = ServiceConfig(
    rate_limit=ServiceRateLimit(
        max_calls=60,      # 60 requests
        time_window=60     # per minute
    )
)
```

#### Usage Patterns

**1. Check and proceed**:
```python
limiter = get_rate_limiter()

if limiter.check_limit("robinhood"):
    # Make API call
    data = api_call()
else:
    # Rate limit exceeded
    wait_time = limiter.get_stats("robinhood")["wait_time"]
    print(f"Rate limited, wait {wait_time:.1f}s")
```

**2. Wait automatically**:
```python
# Blocks until tokens available
limiter.wait_if_needed("robinhood", timeout=30)
# Make API call
data = api_call()
```

**3. Use decorator**:
```python
@rate_limit("robinhood", tokens=1)
def get_data():
    return api_call()

# Automatic rate limiting
data = get_data()
```

**4. Async decorator**:
```python
@rate_limit_async("robinhood", tokens=1)
async def get_data_async():
    return await async_api_call()
```

### Configuration

**File**: `config.py`

Centralized configuration for all services.

#### Components

- **ServiceConfig**: Service configuration
- **ServiceRateLimit**: Rate limit settings
- **RetryPolicy**: Retry with exponential backoff
- **LLM_COSTS**: Cost per 1M tokens for each model

#### Service Registry

All services are registered in `SERVICE_CONFIGS`:

```python
from src.services import get_service_config

config = get_service_config("robinhood")
print(f"Rate limit: {config.rate_limit.max_calls}/{config.rate_limit.time_window}s")
print(f"Timeout: {config.timeout}s")
print(f"Max retries: {config.retry_policy.max_retries}")
```

#### Cost Calculation

```python
from src.services import calculate_cost

cost = calculate_cost(
    model="deepseek-chat",
    input_tokens=1000,
    output_tokens=500
)
print(f"Cost: ${cost:.6f}")
```

## Migration Guide

### Replacing Existing Robinhood Code

1. **Find all Robinhood imports**:
```bash
grep -r "import robin_stocks" src/
grep -r "from.*robinhood" src/
```

2. **Replace with service**:
```python
# Old
import robin_stocks.robinhood as rh
rh.login(username, password)
positions = rh.account.get_open_stock_positions()

# New
from src.services import get_robinhood_client
client = get_robinhood_client()
positions = client.get_stock_positions()
```

3. **Benefits**:
   - Single login across all modules
   - Automatic rate limiting
   - Retry logic on failures
   - Session persistence

### Replacing Existing LLM Code

1. **Find LLM manager usage**:
```bash
grep -r "llm_manager" src/
```

2. **Replace with service**:
```python
# Old
from src.ai_options_agent.llm_manager import get_llm_manager
manager = get_llm_manager()
result = manager.generate(prompt, provider_id="deepseek")

# New
from src.services import get_llm_service
llm = get_llm_service()
result = llm.generate_with_fallback(prompt)
```

3. **Benefits**:
   - Response caching (faster, cheaper)
   - Automatic fallback on errors
   - Cost tracking
   - Rate limiting

## Testing

Each service file includes a `__main__` block for testing:

```bash
# Test Robinhood client
python -m src.services.robinhood_client

# Test LLM service
python -m src.services.llm_service

# Test rate limiter
python -m src.services.rate_limiter
```

## Performance Impact

### Memory Usage

- **Robinhood Client**: ~1 MB (singleton)
- **LLM Service**: ~2-5 MB (includes cache)
- **Rate Limiter**: ~100 KB per service

### Latency

- **Rate limiting**: <0.1ms overhead per request
- **Retry logic**: Adds exponential backoff (1s, 2s, 4s)
- **Caching**: ~0.01ms for cache hits (LLM only)

### Code Reduction

Estimated lines of code saved by eliminating duplicates:

- **Robinhood code**: ~500 lines (across 10+ files)
- **LLM code**: ~300 lines (across 5+ files)
- **Rate limiting**: ~200 lines (across 8+ files)
- **Total**: ~1000 lines removed

## Best Practices

1. **Always use singletons**:
   ```python
   # Good
   client = get_robinhood_client()

   # Bad - creates duplicate instance
   client = RobinhoodClient()
   ```

2. **Let services handle retries**:
   ```python
   # Good - automatic retries
   positions = client.get_positions()

   # Bad - manual retry logic
   for i in range(3):
       try:
           positions = rh.get_positions()
           break
       except:
           time.sleep(2 ** i)
   ```

3. **Use fallback for LLM**:
   ```python
   # Good - automatic fallback
   result = llm.generate_with_fallback(prompt)

   # Bad - single provider
   result = llm.generate(prompt, provider="anthropic")
   ```

4. **Check connection status**:
   ```python
   client = get_robinhood_client()
   status = client.get_connection_status()
   if not status['logged_in']:
       client.login()
   ```

## Troubleshooting

### Robinhood: 429 Rate Limit Errors

**Problem**: Getting 429 errors from Robinhood API

**Solution**: The rate limiter should prevent this, but if it happens:
```python
from src.services import get_rate_limiter

limiter = get_rate_limiter()
limiter.reset("robinhood")  # Reset rate limiter

# Or wait manually
stats = limiter.get_stats("robinhood")
print(f"Wait {stats['wait_time']:.1f}s before next request")
```

### LLM: All Providers Failing

**Problem**: `RuntimeError: All providers failed`

**Solution**: Check available providers:
```python
llm = get_llm_service()
print(f"Available: {llm.get_available_providers()}")

# If none available, check API keys in .env
```

### Cache: Stale Responses

**Problem**: Getting outdated LLM responses from cache

**Solution**: Clear cache:
```python
llm = get_llm_service()
llm.clear_cache()

# Or disable caching
result = llm.generate(prompt, use_cache=False)
```

## Future Enhancements

- [ ] Redis-based distributed rate limiting
- [ ] Prometheus metrics export
- [ ] Circuit breaker pattern
- [ ] Request queuing for burst protection
- [ ] WebSocket support for real-time data
- [ ] Provider health monitoring
- [ ] Automatic cost alerts

## Contributing

When adding a new service:

1. Create service class with singleton pattern
2. Add configuration to `config.py`
3. Apply rate limiting using decorator
4. Add to `__init__.py` exports
5. Update this README
6. Add tests in `__main__` block

## License

Part of the WheelStrategy trading dashboard project.
