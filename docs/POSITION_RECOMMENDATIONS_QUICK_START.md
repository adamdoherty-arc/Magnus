# Position Recommendations - Quick Start Guide

**For Developers:** Fast implementation reference for the position-specific recommendations engine.

---

## Quick Setup (5 minutes)

### 1. Install Dependencies

```bash
pip install yfinance redis hiredis aiohttp textblob
```

### 2. Start Redis (Local Development)

**Windows:**
```bash
# Download Redis for Windows from https://github.com/microsoftarchive/redis/releases
# Extract and run:
redis-server.exe
```

**macOS/Linux:**
```bash
brew install redis  # macOS
sudo apt install redis-server  # Ubuntu

# Start Redis
redis-server
```

**Verify Redis is running:**
```bash
redis-cli ping
# Should return: PONG
```

### 3. Create Database Tables

```sql
-- Run this in PostgreSQL
CREATE TABLE position_recommendations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    position_id VARCHAR(100) NOT NULL,
    symbol VARCHAR(10) NOT NULL,
    action VARCHAR(30) NOT NULL,
    risk_level VARCHAR(10) NOT NULL,
    confidence DECIMAL(3,2),
    short_summary TEXT,
    detailed_reasoning TEXT,
    greeks_data JSONB,
    news_data JSONB,
    recovery_data JSONB,
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    cache_expires_at TIMESTAMP WITH TIME ZONE,
    data_freshness VARCHAR(20),
    user_action VARCHAR(30),
    user_action_timestamp TIMESTAMP WITH TIME ZONE,
    position_closed_at TIMESTAMP WITH TIME ZONE,
    final_pnl DECIMAL(10,2),
    recommendation_accuracy DECIMAL(3,2)
);

CREATE INDEX idx_position_recommendations_position_id ON position_recommendations(position_id);
CREATE INDEX idx_position_recommendations_symbol ON position_recommendations(symbol);
CREATE INDEX idx_position_recommendations_generated_at ON position_recommendations(generated_at DESC);
```

---

## Basic Usage

### Get Recommendations for Positions

```python
from src.services.position_recommendation_service import PositionRecommendationService
from src.models.position_recommendation import Position
from datetime import datetime

# Initialize service
rec_service = PositionRecommendationService()

# Create position objects (normally from Robinhood API)
positions = [
    Position(
        position_id="NVDA-180P-2025-12-15",
        symbol="NVDA",
        strike=180.0,
        expiration=datetime(2025, 12, 15),
        option_type="put",
        position_type="short",
        quantity=2,
        avg_price=3.50,
        current_price=5.20,
        pl=-340.0,
        pl_pct=-15.5,
        dte=12,
        stock_price=175.30
    )
]

# Get recommendations (cached for 15 minutes)
recommendations = rec_service.get_recommendations_batch(positions)

# Access recommendation
rec = recommendations["NVDA-180P-2025-12-15"]
print(rec.action)  # RecommendationAction.ROLL_DOWN_OUT
print(rec.short_summary)  # "Roll to $175 strike, +30 days (+$45 credit)"
print(rec.confidence)  # 0.85
```

### Force Refresh (Bypass Cache)

```python
# Force fresh data fetch
recommendations = rec_service.get_recommendations_batch(
    positions,
    force_refresh=True
)
```

---

## UI Integration (Streamlit)

### Add Recommendation Column to Table

```python
import streamlit as st
from src.services.position_recommendation_service import PositionRecommendationService

# In positions_page_improved.py, after line 714:

def display_strategy_table(title, emoji, positions, section_key, expanded=False):
    if not positions:
        return

    with st.expander(f"{emoji} {title} ({len(positions)})", expanded=expanded):
        df = pd.DataFrame(positions)

        # === NEW: Fetch Recommendations ===
        rec_service = PositionRecommendationService()
        with st.spinner("Analyzing positions..."):
            recommendations = rec_service.get_recommendations_batch(positions)

        # Add recommendation column
        df['Action'] = df['symbol_raw'].map(
            lambda s: recommendations.get(s, None).short_summary if recommendations.get(s) else "N/A"
        )

        # Display table with recommendations
        st.dataframe(
            df,
            column_config={
                "Action": st.column_config.TextColumn(
                    "💡 Recommendation",
                    help="AI-powered action",
                    width="medium"
                )
            }
        )
```

### Display Detailed Recommendations

```python
# After the table, show detailed cards
st.markdown("### 💡 Detailed Recommendations")

for pos in positions:
    rec = recommendations.get(pos['symbol_raw'])
    if rec and rec.action != RecommendationAction.HOLD:
        with st.expander(f"{pos['Symbol']} - {rec.action.value}", expanded=False):
            # Header metrics
            col1, col2, col3 = st.columns(3)
            col1.metric("Risk Level", rec.risk_level.value)
            col2.metric("Confidence", f"{rec.confidence*100:.0f}%")
            col3.metric("Data Age", rec.data_freshness)

            # Reasoning
            st.info(rec.detailed_reasoning)

            # Greeks (if available)
            if rec.greeks:
                st.markdown("**Greeks:**")
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Delta", f"{rec.greeks.delta:.2f}")
                col2.metric("Theta", f"${rec.greeks.theta:.2f}/day")
                col3.metric("IV", f"{rec.greeks.iv:.1f}%")
                col4.metric("Risk", rec.greeks.assignment_risk)

            # News (if available)
            if rec.news and rec.news.key_events:
                st.markdown("**Recent News:**")
                for event in rec.news.key_events[:3]:
                    st.markdown(f"- {event}")

            # Action button
            if rec.recovery and rec.recovery.is_action_required:
                if st.button(f"Execute: {rec.recovery.action.value}", key=f"exec_{pos['symbol_raw']}"):
                    st.success("Opening Robinhood...")
```

---

## Service Architecture

### Service Hierarchy

```
PositionRecommendationService (Main Orchestrator)
├── GreeksAnalyzer (Fetch Options Greeks)
│   └── yfinance API
├── NewsAggregator (Fetch & Analyze News)
│   ├── Finnhub API
│   └── Polygon API
├── RecoveryAdvisor (Generate Recovery Strategies)
│   └── TradingView Database (Options Chain Data)
└── LLMReasoningService (AI-Powered Insights)
    ├── Groq API (Primary, free tier)
    └── DeepSeek API (Fallback, very cheap)
```

### Create Individual Service Instances

```python
from src.services.greeks_analyzer import GreeksAnalyzer
from src.services.news_aggregator import NewsAggregator
from src.services.recovery_advisor import RecoveryAdvisor

# Fetch Greeks only
greeks_service = GreeksAnalyzer()
greeks = greeks_service.fetch_greeks(
    symbol="NVDA",
    strike=180.0,
    expiration=datetime(2025, 12, 15),
    option_type="put"
)
print(f"Delta: {greeks.delta}, Theta: {greeks.theta}")

# Fetch News only
news_service = NewsAggregator()
news = news_service.get_position_news_summary(symbol="NVDA")
print(f"Sentiment: {news.sentiment.value}")
print(f"Key Events: {', '.join(news.key_events)}")

# Get Recovery Strategy
recovery_service = RecoveryAdvisor()
recovery = recovery_service.get_recovery_strategy(
    position=position,
    greeks=greeks,
    news=news
)
print(f"Recommended Action: {recovery.action.value}")
print(f"Target Strike: ${recovery.target_strike}")
```

---

## Caching Strategy

### Redis Cache Keys

```python
# Format: rec:{position_id}:{timestamp_bucket}
# Example: rec:NVDA-180P-2025-12-15:2025-11-10-14:00

from src.cache.redis_cache_manager import RedisCacheManager

cache = RedisCacheManager()

# Store recommendation
cache.set(
    key="NVDA-180P-2025-12-15",
    value=recommendation,
    ttl=900  # 15 minutes
)

# Retrieve recommendation
cached_rec = cache.get("NVDA-180P-2025-12-15")

# Check if cached
if cache.exists("NVDA-180P-2025-12-15"):
    print("Recommendation is cached")
```

### Dynamic TTL Based on Position State

```python
def calculate_cache_ttl(position: Position) -> int:
    """Determine cache TTL based on position urgency"""

    # Expiring soon = shorter TTL (5 minutes)
    if position.dte <= 7:
        return 300

    # Losing positions = shorter TTL (15 minutes)
    if position.pl_pct < -10:
        return 900

    # Winning positions = longer TTL (60 minutes)
    if position.pl_pct > 5:
        return 3600

    # Default: 30 minutes
    return 1800
```

---

## Recommendation Logic Reference

### CSP (Cash-Secured Put) Recommendations

```python
# Decision Tree for CSPs:

if position.pl_pct < -20 and position.dte < 7:
    if news.is_bullish:
        action = RecommendationAction.ROLL_OUT  # Same strike, extend expiration
    else:
        action = RecommendationAction.ROLL_DOWN_OUT  # Lower strike + extend

elif position.pl_pct < -50 and greeks.delta < -0.8:
    action = RecommendationAction.CLOSE  # Deep ITM, assignment imminent

elif position.dte <= 3 and position.is_itm:
    action = RecommendationAction.TAKE_ASSIGNMENT  # Let stock be assigned

else:
    action = RecommendationAction.HOLD  # Theta decay working
```

### Covered Call Recommendations

```python
# Decision Tree for Covered Calls:

if position.pl_pct < -20:  # Losing on CC (stock dropped)
    action = RecommendationAction.CLOSE  # Exit and reassess

elif greeks.delta > 0.7 and news.is_bullish:
    action = RecommendationAction.ROLL_UP  # Capture more upside

elif position.dte <= 7 and position.is_itm:
    action = RecommendationAction.WAIT_EXPIRATION  # Let shares be called away

else:
    action = RecommendationAction.HOLD
```

### Long Call/Put Recommendations

```python
# Decision Tree for Long Positions:

if position.pl_pct > 50:
    action = RecommendationAction.CLOSE  # Take profits

elif position.pl_pct < -30 and position.dte > 14:
    action = RecommendationAction.ROLL_OUT  # Extend to give more time

elif position.dte <= 7 and position.is_itm:
    action = RecommendationAction.CLOSE  # Secure intrinsic value

else:
    action = RecommendationAction.HOLD
```

---

## API Rate Limits

### Configured Limits (from src/services/config.py)

| API | Calls/Minute | Cost | Notes |
|-----|--------------|------|-------|
| **yfinance** | 60 | Free | Real-time Greeks |
| **Finnhub** | 60 | Free | News & sentiment |
| **Polygon** | 5 | Free | Additional news |
| **Groq** | 30 | Free | LLM reasoning |
| **DeepSeek** | Unlimited | ~$0.14/1M tokens | Fallback LLM |

### Rate Limiter Usage

```python
from src.services.rate_limiter import rate_limit

# Decorate functions with rate limiter
@rate_limit("yfinance", tokens=1, timeout=5)
def fetch_greeks(symbol: str, strike: float, exp: datetime):
    # yfinance API call here
    pass

# Rate limiter will automatically:
# 1. Wait if needed to respect limits
# 2. Log rate limit events
# 3. Raise TimeoutError if timeout exceeded
```

---

## Error Handling & Fallbacks

### Graceful Degradation Tiers

```python
# Tier 1: Full recommendation (all data sources)
try:
    return generate_full_recommendation(position)
except Exception:
    pass

# Tier 2: Greeks-only recommendation (no news)
try:
    greeks = fetch_greeks(position)
    return generate_greeks_only_recommendation(position, greeks)
except Exception:
    pass

# Tier 3: Rule-based recommendation (no APIs)
try:
    return generate_rule_based_recommendation(position)
except Exception:
    pass

# Tier 4: Return stale cache (with warning)
cached = get_stale_cache(position.position_id)
if cached:
    cached.data_freshness = "stale"
    return cached

# Tier 5: Default HOLD with error message
return PositionRecommendation(
    action=RecommendationAction.HOLD,
    short_summary="Unable to generate recommendation",
    detailed_reasoning="Please try again later.",
    data_freshness="unavailable"
)
```

---

## Testing

### Unit Test Example

```python
# tests/test_position_recommendation_service.py

import pytest
from src.services.position_recommendation_service import PositionRecommendationService
from src.models.position_recommendation import Position, RecommendationAction

def test_losing_csp_recommendation():
    """Test that losing CSP gets ROLL_DOWN recommendation"""
    service = PositionRecommendationService()

    position = Position(
        position_id="TEST-180P",
        symbol="NVDA",
        strike=180.0,
        expiration=datetime(2025, 12, 15),
        option_type="put",
        position_type="short",
        pl_pct=-15.5,
        dte=12,
        stock_price=175.0
    )

    rec = service._generate_single_recommendation(position, None, None)

    assert rec.action in [
        RecommendationAction.ROLL_DOWN,
        RecommendationAction.ROLL_DOWN_OUT
    ]
    assert rec.risk_level == RiskLevel.HIGH
```

### Run Tests

```bash
# Run all tests
pytest tests/

# Run specific test
pytest tests/test_position_recommendation_service.py -v

# Run with coverage
pytest --cov=src/services tests/
```

---

## Performance Optimization

### Batch API Calls

```python
# BAD: Sequential API calls (slow)
for position in positions:
    greeks = fetch_greeks(position.symbol)

# GOOD: Batch API calls (fast)
symbols = list(set([p.symbol for p in positions]))
greeks_batch = fetch_greeks_batch(symbols)  # Single API call
```

### Async Fetching

```python
import asyncio

async def fetch_all_data(positions):
    """Fetch Greeks and News in parallel"""
    tasks = []

    # Fetch all Greeks concurrently
    for pos in positions:
        tasks.append(fetch_greeks_async(pos.symbol, pos.strike, pos.expiration))

    # Fetch all news concurrently
    symbols = list(set([p.symbol for p in positions]))
    for symbol in symbols:
        tasks.append(fetch_news_async(symbol))

    # Wait for all to complete
    results = await asyncio.gather(*tasks)
    return results

# Use in service
greeks, news = asyncio.run(fetch_all_data(positions))
```

### Cache Warming (Background Job)

```python
from rq import Queue
from redis import Redis

# Schedule background job to pre-warm cache
redis_conn = Redis(host='localhost', port=6379)
queue = Queue('recommendations', connection=redis_conn)

def warm_cache_for_user(user_id: str):
    """Pre-fetch recommendations for all user positions"""
    positions = get_user_positions(user_id)
    rec_service = PositionRecommendationService()
    rec_service.get_recommendations_batch(positions)

# Schedule daily at 7 AM
queue.enqueue_at(
    datetime(2025, 11, 11, 7, 0, 0),
    warm_cache_for_user,
    user_id="user123"
)
```

---

## Database Queries

### Get Recommendation History

```sql
-- Get last 10 recommendations for a position
SELECT
    generated_at,
    action,
    risk_level,
    confidence,
    short_summary,
    user_action,
    final_pnl
FROM position_recommendations
WHERE position_id = 'NVDA-180P-2025-12-15'
ORDER BY generated_at DESC
LIMIT 10;
```

### Calculate Recommendation Accuracy

```sql
-- Which actions are most profitable?
SELECT
    action,
    COUNT(*) as total_recommendations,
    AVG(final_pnl) as avg_pnl,
    AVG(recommendation_accuracy) as avg_accuracy
FROM position_recommendations
WHERE position_closed_at IS NOT NULL
GROUP BY action
ORDER BY avg_pnl DESC;
```

### Track User Compliance

```sql
-- Did users follow recommendations?
SELECT
    action as recommended_action,
    user_action as actual_action,
    COUNT(*) as count,
    ROUND(AVG(final_pnl), 2) as avg_outcome
FROM position_recommendations
WHERE user_action IS NOT NULL
GROUP BY action, user_action
ORDER BY count DESC;
```

---

## Monitoring & Debugging

### Enable Debug Logging

```python
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Or use loguru (recommended)
from loguru import logger

logger.add("recommendations_{time}.log", rotation="1 day", level="DEBUG")

# Now all service logs will be captured
rec_service = PositionRecommendationService()
recommendations = rec_service.get_recommendations_batch(positions)
```

### Check Redis Cache Stats

```python
from src.cache.redis_cache_manager import RedisCacheManager

cache = RedisCacheManager()

# Get cache statistics
stats = cache.get_stats()
print(f"Total Keys: {stats['total_keys']}")
print(f"Hit Rate: {stats['hit_rate']}%")
print(f"Memory Used: {stats['memory_used_mb']} MB")
```

### Check Rate Limiter Status

```python
from src.services.rate_limiter import get_rate_limiter

limiter = get_rate_limiter()

# Get rate limit stats for each service
for service in ["yfinance", "finnhub", "polygon", "groq"]:
    stats = limiter.get_stats(service)
    print(f"{service}:")
    print(f"  Available Tokens: {stats['available_tokens']}")
    print(f"  Utilization: {stats['utilization']*100:.1f}%")
    print(f"  Wait Time: {stats['wait_time']:.2f}s")
```

---

## Common Issues & Solutions

### Issue: "Redis connection refused"

**Solution:**
```bash
# Check if Redis is running
redis-cli ping

# If not, start Redis
redis-server

# Or use cloud Redis (Redis Labs free tier)
# Update .env:
REDIS_URL=redis://username:password@host:port
```

### Issue: "yfinance rate limit exceeded"

**Solution:**
```python
# The rate limiter will automatically wait
# But you can also reduce concurrent requests:

from src.services.rate_limiter import get_rate_limiter

limiter = get_rate_limiter()
stats = limiter.get_stats("yfinance")

if stats['utilization'] > 0.8:
    print("Rate limit almost exceeded, waiting...")
    time.sleep(5)
```

### Issue: "Recommendations are stale"

**Solution:**
```python
# Force refresh to bypass cache
recommendations = rec_service.get_recommendations_batch(
    positions,
    force_refresh=True
)

# Or clear specific cache entry
cache = RedisCacheManager()
cache.delete("NVDA-180P-2025-12-15")
```

### Issue: "Missing Greeks data"

**Solution:**
```python
# yfinance may not have data for illiquid options
# Check option volume/open interest:
if position.volume < 10 or position.open_interest < 50:
    logger.warning(f"Low liquidity for {position.symbol}, Greeks may be unreliable")

# Use fallback calculation:
from src.services.greeks_analyzer import calculate_greeks_manual

greeks = calculate_greeks_manual(
    stock_price=position.stock_price,
    strike=position.strike,
    dte=position.dte,
    iv=0.30,  # Estimate 30% IV
    option_type=position.option_type
)
```

---

## Production Checklist

- [ ] Redis is running and accessible
- [ ] PostgreSQL `position_recommendations` table created
- [ ] Environment variables set (FINNHUB_API_KEY, POLYGON_API_KEY, GROQ_API_KEY)
- [ ] Rate limiters configured for all APIs
- [ ] Error logging enabled (loguru)
- [ ] Cache warming scheduled (optional, for auto-refresh users)
- [ ] Background worker running (optional, for RQ jobs)
- [ ] Database backups enabled
- [ ] Monitoring dashboard configured (Grafana/Prometheus)

---

## Next Steps

1. **Read Full Architecture:** See `docs/architecture/POSITION_RECOMMENDATIONS_ARCHITECTURE.md`
2. **Implement Core Services:** Start with `PositionRecommendationService`
3. **Test with Sample Positions:** Use unit tests to validate logic
4. **Integrate into UI:** Add recommendation column to positions table
5. **Monitor Performance:** Track cache hit rate and API latency
6. **Iterate:** Add ML model and advanced features

---

**Need Help?**

- Architecture Questions: See `docs/architecture/POSITION_RECOMMENDATIONS_ARCHITECTURE.md`
- Code Examples: See `src/models/position_recommendation.py`
- API Reference: See `src/services/position_recommendation_service.py`

**Happy Coding!**
