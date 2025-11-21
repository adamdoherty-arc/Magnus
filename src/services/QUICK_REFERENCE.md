# Services Layer - Quick Reference Card

## Import

```python
from src.services import (
    get_robinhood_client,
    get_llm_service,
    get_rate_limiter,
    rate_limit
)
```

## Robinhood Client

### Basic Usage
```python
client = get_robinhood_client()
client.login()                              # Auto-cached session
account = client.get_account_info()         # Get account details
positions = client.get_positions()          # All positions
stocks = client.get_stock_positions()       # Stocks only
options = client.get_options_positions()    # Options only
data = client.get_market_data('AAPL')       # Real-time quote
chain = client.get_options_chain('AAPL')    # Options chain
client.logout()                             # Logout
```

### Key Features
- ✓ 60 requests/minute (automatic)
- ✓ 3 retry attempts with exponential backoff
- ✓ Session caching
- ✓ Thread-safe singleton

## LLM Service

### Basic Usage
```python
llm = get_llm_service()

# Auto-select provider (free/cheap first)
result = llm.generate_with_fallback(
    "Your prompt here",
    max_tokens=500
)

# Specific provider
result = llm.generate(
    "Your prompt",
    provider="deepseek",
    model="deepseek-chat"
)

# Get stats
stats = llm.get_usage_stats()
print(f"Total cost: ${stats['total_cost']:.4f}")
```

### Response Format
```python
{
    "text": "Response...",
    "provider": "deepseek",
    "model": "deepseek-chat",
    "input_tokens": 150,
    "output_tokens": 300,
    "cost": 0.000084,
    "cached": False
}
```

### Providers
| Provider | Cost | Speed | Key |
|----------|------|-------|-----|
| Ollama | Free | Medium | N/A (local) |
| Groq | Free | Very Fast | GROQ_API_KEY |
| DeepSeek | $0.14/$0.28/1M | Fast | DEEPSEEK_API_KEY |
| Gemini | Cheap | Very Fast | GOOGLE_API_KEY |
| OpenAI | $0.15-$10/1M | Fast | OPENAI_API_KEY |
| Claude | $3-$75/1M | Medium | ANTHROPIC_API_KEY |

## Rate Limiter

### Using Decorator (Recommended)
```python
@rate_limit("robinhood", tokens=1, timeout=30)
def get_positions():
    return api_call()
```

### Manual Control
```python
limiter = get_rate_limiter()

# Check if allowed
if limiter.check_limit("robinhood"):
    make_api_call()

# Wait if needed
limiter.wait_if_needed("robinhood", timeout=30)
make_api_call()

# Get stats
stats = limiter.get_stats("robinhood")
print(f"Available: {stats['available_tokens']:.1f}")
print(f"Wait: {stats['wait_time']:.2f}s")
```

## Environment Variables

```bash
# Robinhood (required)
ROBINHOOD_USERNAME=your_email@example.com
ROBINHOOD_PASSWORD=your_password
ROBINHOOD_MFA_CODE=your_totp_secret  # Optional

# LLM (optional, add what you need)
GROQ_API_KEY=your_key
DEEPSEEK_API_KEY=your_key
GOOGLE_API_KEY=your_key
OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
```

## Common Patterns

### Dashboard Data Fetch
```python
client = get_robinhood_client()
client.login()

data = {
    'account': client.get_account_info(),
    'positions': client.get_positions()
}

client.logout()
```

### AI Analysis
```python
llm = get_llm_service()

result = llm.generate_with_fallback(
    f"Analyze {symbol} for options trading",
    providers=["ollama", "groq", "deepseek"]
)

print(result['text'])
print(f"Cost: ${result['cost']:.6f}")
```

### Batch Processing
```python
llm = get_llm_service()

for symbol in symbols:
    result = llm.generate_with_fallback(
        f"Quick rating for {symbol}",
        max_tokens=50
    )
    print(f"{symbol}: {result['text']}")

stats = llm.get_usage_stats()
print(f"Total: ${stats['total_cost']:.4f}")
```

## Status Checks

```python
# Robinhood
status = client.get_connection_status()
print(status['logged_in'])

# LLM
info = llm.get_service_info()
print(info['available_providers'])

# Rate Limiter
stats = limiter.get_stats("robinhood")
print(f"Usage: {stats['utilization']*100:.1f}%")
```

## Troubleshooting

### Rate Limit Exceeded
```python
limiter = get_rate_limiter()
limiter.reset("robinhood")
```

### Stale Cache
```python
llm = get_llm_service()
llm.clear_cache()
```

### Connection Issues
```python
client = get_robinhood_client()
if not client.logged_in:
    client.login(force_fresh=True)
```

## Testing

```bash
# Test each service
python -m src.services.robinhood_client
python -m src.services.llm_service
python -m src.services.rate_limiter
```

## Documentation

- **README.md** - Full documentation
- **EXAMPLES.md** - Code examples
- **QUICK_REFERENCE.md** - This file
- **SERVICES_LAYER_IMPLEMENTATION.md** - Implementation summary

## Performance

- **Memory**: ~3-6 MB total
- **Latency**: <0.1ms rate limiting overhead
- **Caching**: ~0.01ms for LLM cache hits
- **Retry**: 1s, 2s, 4s exponential backoff

## Best Practices

1. ✓ Always use singleton getters
2. ✓ Let services handle retries
3. ✓ Use fallback for LLM
4. ✓ Check connection status
5. ✓ Monitor costs
6. ✓ Use rate limit decorators
7. ✓ Handle errors gracefully

---

**Quick Start**: Copy the "Import" section and start using!
