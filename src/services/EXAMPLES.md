# Services Layer - Usage Examples

Practical examples of using the centralized services layer.

## Table of Contents

1. [Robinhood Client Examples](#robinhood-client-examples)
2. [LLM Service Examples](#llm-service-examples)
3. [Rate Limiter Examples](#rate-limiter-examples)
4. [Integration Examples](#integration-examples)

---

## Robinhood Client Examples

### Example 1: Basic Account Information

```python
from src.services import get_robinhood_client
from loguru import logger

def display_account_summary():
    """Display account summary with error handling"""
    client = get_robinhood_client()

    # Login (cached session if available)
    if not client.login():
        logger.error("Failed to login to Robinhood")
        return

    # Get account info
    account = client.get_account_info()

    if account:
        print("=" * 60)
        print("ROBINHOOD ACCOUNT SUMMARY")
        print("=" * 60)
        print(f"Buying Power:    ${account['buying_power']:>12,.2f}")
        print(f"Cash:            ${account['cash']:>12,.2f}")
        print(f"Portfolio Value: ${account['portfolio_value']:>12,.2f}")
        print(f"Day Trades:      {account['day_trade_count']:>12}")
        print("=" * 60)
    else:
        logger.error("Failed to fetch account info")

    # Logout
    client.logout()

if __name__ == "__main__":
    display_account_summary()
```

### Example 2: Portfolio Analysis

```python
from src.services import get_robinhood_client
from typing import Dict, List
import pandas as pd

def analyze_portfolio() -> Dict:
    """Analyze portfolio with position breakdown"""
    client = get_robinhood_client()

    # Ensure logged in
    client.login()

    # Get all positions
    positions = client.get_positions()

    # Separate stocks and options
    stocks = [p for p in positions if p['type'] == 'stock']
    options = [p for p in positions if p['type'] == 'option']

    # Calculate totals
    total_stock_value = sum(p['market_value'] for p in stocks)
    total_options_value = sum(p['market_value'] for p in options)
    total_value = total_stock_value + total_options_value

    # Find winners and losers
    winners = [p for p in positions if p.get('total_return', 0) > 0]
    losers = [p for p in positions if p.get('total_return', 0) < 0]

    analysis = {
        'total_positions': len(positions),
        'stocks': len(stocks),
        'options': len(options),
        'total_value': total_value,
        'total_stock_value': total_stock_value,
        'total_options_value': total_options_value,
        'winners': len(winners),
        'losers': len(losers),
        'positions': positions
    }

    # Display summary
    print("\nPortfolio Analysis")
    print("=" * 60)
    print(f"Total Positions: {analysis['total_positions']}")
    print(f"  Stocks: {analysis['stocks']}")
    print(f"  Options: {analysis['options']}")
    print(f"\nTotal Value: ${analysis['total_value']:,.2f}")
    print(f"  Stocks: ${analysis['total_stock_value']:,.2f} "
          f"({analysis['total_stock_value']/analysis['total_value']*100:.1f}%)")
    print(f"  Options: ${analysis['total_options_value']:,.2f} "
          f"({analysis['total_options_value']/analysis['total_value']*100:.1f}%)")
    print(f"\nPerformance:")
    print(f"  Winners: {analysis['winners']}")
    print(f"  Losers: {analysis['losers']}")

    return analysis

if __name__ == "__main__":
    analyze_portfolio()
```

### Example 3: Wheel Strategy Scanner

```python
from src.services import get_robinhood_client
from datetime import datetime, timedelta

def find_wheel_opportunities():
    """Find stocks suitable for wheel strategy"""
    client = get_robinhood_client()
    client.login()

    # Get stock positions
    stocks = client.get_stock_positions()

    # Filter for wheel candidates (100+ shares)
    wheel_candidates = []

    for stock in stocks:
        if stock['quantity'] >= 100:
            # Calculate number of covered calls possible
            contracts_available = int(stock['quantity'] / 100)

            # Get options chain
            options = client.get_options_chain(
                stock['symbol'],
                expiration_date=None  # All expirations
            )

            wheel_candidates.append({
                'symbol': stock['symbol'],
                'shares': stock['quantity'],
                'current_price': stock['current_price'],
                'cost_basis': stock['avg_cost'],
                'contracts_available': contracts_available,
                'options_available': len(options) > 0
            })

    # Display results
    print("\nWheel Strategy Candidates")
    print("=" * 80)
    print(f"{'Symbol':<8} {'Shares':>8} {'Price':>8} {'Cost':>8} {'Contracts':>10} {'Options':>8}")
    print("-" * 80)

    for candidate in wheel_candidates:
        print(f"{candidate['symbol']:<8} "
              f"{candidate['shares']:>8.0f} "
              f"${candidate['current_price']:>7.2f} "
              f"${candidate['cost_basis']:>7.2f} "
              f"{candidate['contracts_available']:>10} "
              f"{'Yes' if candidate['options_available'] else 'No':>8}")

    return wheel_candidates

if __name__ == "__main__":
    find_wheel_opportunities()
```

---

## LLM Service Examples

### Example 1: Stock Analysis

```python
from src.services import get_llm_service

def analyze_stock(symbol: str) -> str:
    """Get AI analysis of a stock"""
    llm = get_llm_service()

    prompt = f"""
    Analyze {symbol} stock for options trading:

    1. Current market sentiment (bullish/bearish/neutral)
    2. Key support and resistance levels
    3. Suitable options strategies (covered calls, CSPs, spreads)
    4. Risk factors to consider

    Keep analysis concise (3-4 paragraphs).
    """

    # Use free/cheap providers first
    result = llm.generate_with_fallback(
        prompt,
        providers=["ollama", "groq", "deepseek"],
        max_tokens=500,
        temperature=0.7
    )

    print(f"\n{symbol} Analysis")
    print("=" * 60)
    print(f"Provider: {result['provider']} ({result['model']})")
    print(f"Cost: ${result['cost']:.6f}")
    print(f"Cached: {result['cached']}")
    print("-" * 60)
    print(result['text'])
    print("=" * 60)

    return result['text']

if __name__ == "__main__":
    analyze_stock("AAPL")
```

### Example 2: Multi-Provider Comparison

```python
from src.services import get_llm_service
import time

def compare_providers(prompt: str):
    """Compare response from different providers"""
    llm = get_llm_service()

    providers_to_test = ["ollama", "groq", "deepseek", "gemini"]
    results = []

    print("\nComparing LLM Providers")
    print("=" * 80)

    for provider in providers_to_test:
        if provider not in llm.get_available_providers():
            print(f"⊘ {provider:10} - Not available")
            continue

        try:
            start_time = time.time()

            result = llm.generate(
                prompt,
                provider=provider,
                max_tokens=200,
                temperature=0.7,
                use_cache=False  # Disable cache for fair comparison
            )

            elapsed = time.time() - start_time

            results.append({
                'provider': provider,
                'model': result['model'],
                'time': elapsed,
                'tokens': result['output_tokens'],
                'cost': result['cost'],
                'response': result['text'][:100] + "..."
            })

            print(f"✓ {provider:10} - {elapsed:.2f}s, ${result['cost']:.6f}, "
                  f"{result['output_tokens']} tokens")

        except Exception as e:
            print(f"✗ {provider:10} - Error: {e}")

    # Display detailed results
    print("\n" + "=" * 80)
    print("Detailed Results:")
    print("=" * 80)

    for r in results:
        print(f"\n{r['provider']} ({r['model']})")
        print(f"  Time: {r['time']:.2f}s")
        print(f"  Cost: ${r['cost']:.6f}")
        print(f"  Tokens: {r['tokens']}")
        print(f"  Response: {r['response']}")

    return results

if __name__ == "__main__":
    compare_providers("Explain the wheel strategy in 2 sentences.")
```

### Example 3: Cost-Efficient Batch Processing

```python
from src.services import get_llm_service
from typing import List

def batch_analyze_stocks(symbols: List[str]) -> Dict[str, str]:
    """Analyze multiple stocks cost-efficiently"""
    llm = get_llm_service()

    results = {}
    total_cost = 0.0

    print(f"\nAnalyzing {len(symbols)} stocks...")
    print("=" * 60)

    for symbol in symbols:
        prompt = f"Is {symbol} bullish or bearish? Answer in 1 sentence."

        # Use cheapest available provider
        result = llm.generate_with_fallback(
            prompt,
            providers=["ollama", "groq", "deepseek"],  # Free/cheap first
            max_tokens=100,
            temperature=0.5
        )

        results[symbol] = result['text']
        total_cost += result['cost']

        print(f"✓ {symbol:6} - ${result['cost']:.6f} - {result['provider']}")

    print("-" * 60)
    print(f"Total cost: ${total_cost:.6f}")
    print(f"Avg cost per stock: ${total_cost/len(symbols):.6f}")

    return results

if __name__ == "__main__":
    symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
    batch_analyze_stocks(symbols)
```

### Example 4: Using Cache for Repeated Queries

```python
from src.services import get_llm_service
import time

def demonstrate_caching():
    """Show the benefit of response caching"""
    llm = get_llm_service()

    prompt = "What are the Greeks in options trading?"

    # First call (no cache)
    print("\nFirst call (no cache):")
    start = time.time()
    result1 = llm.generate(prompt, max_tokens=200)
    elapsed1 = time.time() - start

    print(f"  Time: {elapsed1:.3f}s")
    print(f"  Cost: ${result1['cost']:.6f}")
    print(f"  Cached: {result1['cached']}")

    # Second call (cached)
    print("\nSecond call (should be cached):")
    start = time.time()
    result2 = llm.generate(prompt, max_tokens=200)
    elapsed2 = time.time() - start

    print(f"  Time: {elapsed2:.3f}s")
    print(f"  Cost: ${result2['cost']:.6f}")
    print(f"  Cached: {result2['cached']}")

    # Compare
    print("\nSpeedup:")
    print(f"  {elapsed1/elapsed2:.1f}x faster")
    print(f"  Saved: ${result1['cost']:.6f}")

if __name__ == "__main__":
    demonstrate_caching()
```

---

## Rate Limiter Examples

### Example 1: Basic Rate Limiting

```python
from src.services import get_rate_limiter
import time

def demonstrate_rate_limiting():
    """Show rate limiter in action"""
    limiter = get_rate_limiter()

    # Configure test service (5 calls per second)
    from src.services.config import SERVICE_CONFIGS, ServiceConfig, ServiceRateLimit, RetryPolicy
    SERVICE_CONFIGS["test_api"] = ServiceConfig(
        name="test_api",
        rate_limit=ServiceRateLimit(max_calls=5, time_window=1),
        timeout=10,
        retry_policy=RetryPolicy()
    )

    print("\nRate Limiter Demo (5 calls/second)")
    print("=" * 60)

    # Try to make 10 calls
    for i in range(10):
        start = time.time()

        # Check if allowed
        allowed = limiter.check_limit("test_api")

        if allowed:
            elapsed = time.time() - start
            print(f"Call {i+1:2}: ✓ Allowed  ({elapsed*1000:.1f}ms)")
        else:
            # Wait if needed
            limiter.wait_if_needed("test_api", timeout=5)
            elapsed = time.time() - start
            print(f"Call {i+1:2}: ⏱ Waited  ({elapsed*1000:.1f}ms)")

if __name__ == "__main__":
    demonstrate_rate_limiting()
```

### Example 2: Decorator Pattern

```python
from src.services import rate_limit
import time

# Decorate function with rate limiting
@rate_limit("robinhood", tokens=1, timeout=30)
def get_robinhood_data(symbol: str):
    """Get data with automatic rate limiting"""
    print(f"Fetching data for {symbol}...")
    time.sleep(0.1)  # Simulate API call
    return {"symbol": symbol, "price": 150.0}

def main():
    """Demonstrate decorator usage"""
    symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]

    print("\nFetching data with rate limiting...")
    print("=" * 60)

    for symbol in symbols:
        start = time.time()
        data = get_robinhood_data(symbol)
        elapsed = time.time() - start

        print(f"{symbol}: ${data['price']:.2f} ({elapsed:.3f}s)")

if __name__ == "__main__":
    main()
```

### Example 3: Monitoring Rate Limits

```python
from src.services import get_rate_limiter
import time

def monitor_rate_limits():
    """Monitor rate limiter statistics"""
    limiter = get_rate_limiter()

    services = ["robinhood", "groq", "deepseek"]

    print("\nRate Limiter Statistics")
    print("=" * 80)
    print(f"{'Service':<15} {'Available':>12} {'Capacity':>10} {'Wait':>8} {'Usage':>8}")
    print("-" * 80)

    for service in services:
        try:
            stats = limiter.get_stats(service)

            print(f"{service:<15} "
                  f"{stats['available_tokens']:>12.1f} "
                  f"{stats['capacity']:>10.0f} "
                  f"{stats['wait_time']:>7.2f}s "
                  f"{stats['utilization']*100:>7.1f}%")

        except Exception as e:
            print(f"{service:<15} Error: {e}")

    print("=" * 80)

if __name__ == "__main__":
    monitor_rate_limits()
```

---

## Integration Examples

### Example 1: Dashboard Data Fetcher

```python
from src.services import get_robinhood_client, get_llm_service
from typing import Dict, Any

def fetch_dashboard_data() -> Dict[str, Any]:
    """Fetch all dashboard data using centralized services"""

    # Get services
    rh = get_robinhood_client()
    llm = get_llm_service()

    # Login to Robinhood
    rh.login()

    # Fetch data
    data = {
        'account': rh.get_account_info(),
        'positions': rh.get_positions(),
        'market_analysis': {}
    }

    # Get AI analysis for top 3 positions
    stocks = [p for p in data['positions'] if p['type'] == 'stock']
    top_stocks = sorted(stocks, key=lambda x: x['market_value'], reverse=True)[:3]

    for stock in top_stocks:
        symbol = stock['symbol']
        prompt = f"Brief market outlook for {symbol} (1 sentence)"

        result = llm.generate_with_fallback(
            prompt,
            providers=["ollama", "groq"],
            max_tokens=100
        )

        data['market_analysis'][symbol] = result['text']

    # Logout
    rh.logout()

    return data

if __name__ == "__main__":
    data = fetch_dashboard_data()
    print(f"Account Value: ${data['account']['portfolio_value']:,.2f}")
    print(f"Positions: {len(data['positions'])}")
    print(f"AI Analysis: {len(data['market_analysis'])} stocks")
```

### Example 2: Automated Trading Signal Generator

```python
from src.services import get_robinhood_client, get_llm_service
from datetime import datetime

def generate_trading_signals():
    """Generate trading signals using AI and market data"""

    rh = get_robinhood_client()
    llm = get_llm_service()

    # Login
    rh.login()

    # Get positions
    positions = rh.get_positions()

    signals = []

    for position in positions:
        if position['type'] != 'stock':
            continue

        symbol = position['symbol']

        # Get current market data
        market_data = rh.get_market_data(symbol)

        # Ask AI for recommendation
        prompt = f"""
        Stock: {symbol}
        Current Price: ${market_data['price']:.2f}
        Position: {position['quantity']} shares @ ${position['avg_cost']:.2f}

        Should I sell covered calls? Reply with Yes/No and brief reason.
        """

        result = llm.generate_with_fallback(
            prompt,
            providers=["deepseek", "groq"],
            max_tokens=100
        )

        signals.append({
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'recommendation': result['text'],
            'provider': result['provider'],
            'cost': result['cost']
        })

    # Display signals
    print("\nTrading Signals")
    print("=" * 80)

    for signal in signals:
        print(f"\n{signal['symbol']}:")
        print(f"  {signal['recommendation']}")
        print(f"  (via {signal['provider']}, ${signal['cost']:.6f})")

    return signals

if __name__ == "__main__":
    generate_trading_signals()
```

### Example 3: Cost-Efficient Research Pipeline

```python
from src.services import get_llm_service
from typing import List, Dict

def research_pipeline(symbols: List[str]) -> Dict[str, Dict]:
    """
    Multi-stage research pipeline:
    1. Quick screen (free/cheap provider)
    2. Detailed analysis (premium provider for top picks)
    """

    llm = get_llm_service()

    # Stage 1: Quick screen using free providers
    print("\nStage 1: Quick Screening")
    print("=" * 60)

    quick_scores = {}

    for symbol in symbols:
        prompt = f"Rate {symbol} for options trading: Good/OK/Bad. One word only."

        result = llm.generate_with_fallback(
            prompt,
            providers=["ollama", "groq"],  # Free only
            max_tokens=10,
            temperature=0.3
        )

        rating = result['text'].strip().lower()
        quick_scores[symbol] = rating

        print(f"{symbol}: {rating}")

    # Stage 2: Detailed analysis of "good" stocks
    good_stocks = [s for s, r in quick_scores.items() if 'good' in r]

    print(f"\nStage 2: Detailed Analysis ({len(good_stocks)} stocks)")
    print("=" * 60)

    detailed_analysis = {}

    for symbol in good_stocks:
        prompt = f"""
        Detailed options trading analysis for {symbol}:
        - Best strategy (covered calls, CSPs, spreads)
        - Strike selection
        - Risk level
        Keep it under 100 words.
        """

        # Use better model for detailed analysis
        result = llm.generate_with_fallback(
            prompt,
            providers=["deepseek", "gemini"],  # Cheap but good quality
            max_tokens=200,
            temperature=0.7
        )

        detailed_analysis[symbol] = result['text']

        print(f"\n{symbol}:")
        print(result['text'])
        print(f"(Cost: ${result['cost']:.6f})")

    # Show total costs
    stats = llm.get_usage_stats()
    print(f"\nTotal Cost: ${stats['total_cost']:.6f}")

    return {
        'quick_screen': quick_scores,
        'detailed_analysis': detailed_analysis,
        'total_cost': stats['total_cost']
    }

if __name__ == "__main__":
    symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA",
               "NVDA", "META", "NFLX", "AMD", "INTC"]
    research_pipeline(symbols)
```

### Example 4: Error-Resilient Data Sync

```python
from src.services import get_robinhood_client
from loguru import logger
import time

def sync_portfolio_data(max_retries: int = 3):
    """Sync portfolio data with automatic retry and error handling"""

    client = get_robinhood_client()

    # Check connection
    status = client.get_connection_status()
    logger.info(f"Connection status: {status}")

    # Login with retry
    for attempt in range(max_retries):
        try:
            if client.login():
                logger.info("Login successful")
                break
        except Exception as e:
            logger.warning(f"Login attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                logger.error("All login attempts failed")
                return None

    # Fetch data with automatic retry (built into client)
    try:
        data = {
            'account': client.get_account_info(),
            'positions': client.get_positions(),
            'timestamp': time.time()
        }

        logger.info(f"Synced {len(data['positions'])} positions")
        return data

    except Exception as e:
        logger.error(f"Data sync failed: {e}")
        return None

    finally:
        # Always logout
        client.logout()

if __name__ == "__main__":
    data = sync_portfolio_data()
    if data:
        print(f"Success! Synced {len(data['positions'])} positions")
    else:
        print("Sync failed")
```

---

## Best Practices Summary

1. **Always use singleton getters** (`get_*_client()`, `get_*_service()`)
2. **Let services handle retries** (don't add manual retry logic)
3. **Use fallback for LLM** (automatic provider switching)
4. **Check connection status** before critical operations
5. **Monitor costs** for LLM usage
6. **Clear cache** when you need fresh data
7. **Use rate limiting decorators** for cleaner code
8. **Handle errors gracefully** (services return empty dict/list on error)

## Performance Tips

1. **Cache frequently accessed data** (LLM responses auto-cached)
2. **Batch operations** when possible
3. **Use cheap providers** for simple tasks
4. **Disable cache** for real-time data
5. **Monitor rate limits** to avoid delays
