# AI Research Specialist Agents

Production-ready specialist agents for comprehensive stock analysis. Each agent focuses on a specific domain and provides structured, actionable insights.

## Architecture

```
ai_research/
├── fundamental_agent.py  # Financial metrics & valuation (Alpha Vantage)
├── technical_agent.py    # Technical indicators & price action (yfinance + pandas_ta)
├── sentiment_agent.py    # Market sentiment & social data (praw + yfinance)
├── options_agent.py      # Options strategies & Greeks (yfinance + mibian)
├── models.py             # Shared data models and enums
├── example_usage.py      # Comprehensive usage examples
└── README.md             # This file
```

## Quick Start

### Installation

```bash
# Install required dependencies
pip install -r requirements.txt
```

### Environment Variables

```bash
# Required for Fundamental Agent
export ALPHA_VANTAGE_API_KEY="your_key_here"

# Optional for Sentiment Agent (Reddit data)
export REDDIT_CLIENT_ID="your_client_id"
export REDDIT_CLIENT_SECRET="your_secret"
export REDDIT_USER_AGENT="stock_analyzer/1.0"
```

### Basic Usage

```python
import asyncio
from fundamental_agent import FundamentalAgent
from technical_agent import TechnicalAgent
from sentiment_agent import SentimentAgent
from options_agent import OptionsAgent

async def analyze_stock(symbol: str):
    # Initialize agents
    fundamental = FundamentalAgent()
    technical = TechnicalAgent()
    sentiment = SentimentAgent()
    options = OptionsAgent()

    # Run analyses in parallel
    results = await asyncio.gather(
        fundamental.analyze(symbol),
        technical.analyze(symbol),
        sentiment.analyze(symbol),
        options.analyze(symbol)
    )

    fundamental_data, technical_data, sentiment_data, options_data = results

    # Use the structured data
    print(f"Fundamental Score: {fundamental_data.score}/100")
    print(f"Technical Score: {technical_data.score}/100")
    print(f"P/E Ratio: {fundamental_data.pe_ratio}")
    print(f"RSI: {technical_data.rsi}")

    return results

# Run it
asyncio.run(analyze_stock("AAPL"))
```

## Agent Details

### 1. FundamentalAgent

**Purpose**: Analyzes financial health and valuation metrics.

**Data Source**: Alpha Vantage API

**Key Features**:
- P/E, P/B, Debt/Equity ratios
- Revenue growth and profitability metrics
- Sector comparison and valuation assessment
- Free cash flow analysis
- Dividend yield
- Key strengths and risks identification
- Overall score (0-100)

**Returns**: `FundamentalAnalysis` object

**Example**:
```python
agent = FundamentalAgent(api_key="your_key")  # or uses env var
result = await agent.analyze("AAPL")

print(f"P/E Ratio: {result.pe_ratio}")
print(f"Valuation: {result.valuation_assessment}")
print(f"Score: {result.score}/100")
```

**Scoring Methodology**:
- Valuation (30 points): P/E vs sector average
- Profitability (25 points): ROE
- Growth (25 points): Revenue growth YoY
- Financial health (20 points): Debt levels, FCF

**Error Handling**:
- Automatic retry with exponential backoff
- Rate limit detection and handling
- Fallback to neutral analysis on failure
- Comprehensive logging

---

### 2. TechnicalAgent

**Purpose**: Analyzes price action and technical indicators.

**Data Source**: yfinance + pandas_ta

**Key Features**:
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Multiple moving averages (MA20, MA50, MA200)
- Bollinger Bands
- Support and resistance levels
- Volume analysis
- Chart pattern detection
- Trend determination
- Overall score (0-100)

**Returns**: `TechnicalAnalysis` object

**Example**:
```python
agent = TechnicalAgent()
result = await agent.analyze("MSFT")

print(f"RSI: {result.rsi}")
print(f"Trend: {result.trend}")  # UPTREND, DOWNTREND, or SIDEWAYS
print(f"MACD Signal: {result.macd_signal}")  # BULLISH, BEARISH, or NEUTRAL
print(f"Recommendation: {result.recommendation}")
```

**Indicators**:
- **RSI**: 14-period, values 0-100 (>70 overbought, <30 oversold)
- **MACD**: 12/26/9 standard settings
- **Bollinger Bands**: 20-period, 2 standard deviations
- **Support/Resistance**: Calculated using pivot points

**Scoring Methodology**:
- Trend strength (30 points)
- RSI position (25 points) - optimal 40-60 range
- MACD signal (25 points)
- MA alignment (20 points)

**Pattern Detection**:
- Golden Cross / Death Cross
- Bollinger Band squeeze
- Overbought/oversold conditions
- RSI divergence (basic)

---

### 3. SentimentAgent

**Purpose**: Analyzes market sentiment from multiple sources.

**Data Sources**:
- Reddit API (praw) - r/wallstreetbets, r/stocks, r/investing
- yfinance - Analyst ratings and insider trades

**Key Features**:
- Reddit sentiment analysis (weighted by post score)
- Analyst ratings consensus
- Insider trading activity
- Institutional flow indicators
- Social mention tracking
- Overall score (0-100)

**Returns**: `SentimentAnalysis` object

**Example**:
```python
agent = SentimentAgent()
result = await agent.analyze("GME")

print(f"Social Sentiment: {result.social_sentiment}")
print(f"Reddit Mentions (24h): {result.reddit_mentions_24h}")
print(f"Analyst Rating: {result.analyst_rating}")
print(f"Institutional Flow: {result.institutional_flow}")

# Check insider trades
for trade in result.insider_trades:
    print(f"{trade.insider_name} {trade.transaction_type} {trade.shares} shares")
```

**Sentiment Categories**:
- **Social**: POSITIVE, NEGATIVE, NEUTRAL
- **Analyst Rating**: STRONG_BUY, BUY, HOLD, SELL, STRONG_SELL
- **Institutional Flow**: HEAVY_BUYING, MODERATE_BUYING, NEUTRAL, MODERATE_SELLING, HEAVY_SELLING

**Scoring Methodology**:
- Analyst consensus (40 points)
- Social sentiment (30 points)
- Institutional flow (20 points)
- Insider activity (10 points)

**Keyword-Based Sentiment**:
- Positive: bullish, buy, calls, moon, rocket, gain, profit
- Negative: bearish, sell, puts, crash, dump, loss

---

### 4. OptionsAgent

**Purpose**: Analyzes options strategies and calculates Greeks.

**Data Sources**: yfinance (options chains) + mibian (Greeks)

**Key Features**:
- IV Rank and IV Percentile
- Implied volatility tracking
- Earnings impact analysis
- Put/Call ratio
- Max pain calculation
- Unusual options activity detection
- Strategy recommendations (CSP, covered calls, spreads)
- Greeks calculation (Delta, Gamma, Theta, Vega)

**Returns**: `OptionsAnalysis` object

**Example**:
```python
agent = OptionsAgent()
result = await agent.analyze("NVDA")

print(f"IV Rank: {result.iv_rank}/100")
print(f"Current IV: {result.current_iv*100:.2f}%")
print(f"Days to Earnings: {result.days_to_earnings}")
print(f"Put/Call Ratio: {result.put_call_ratio}")

# Strategy recommendations
for strategy in result.recommended_strategies:
    print(f"{strategy.strategy}: Strike ${strategy.strike}, Premium ${strategy.premium}")
    print(f"  Probability of Profit: {strategy.probability_of_profit*100:.1f}%")
    print(f"  {strategy.rationale}")
```

**IV Metrics**:
- **IV Rank**: Current IV relative to 52-week range (0-100)
- **IV Percentile**: Percentage of days IV was below current level
- Higher IV = Better for selling premium
- Lower IV = Better for buying options

**Strategy Types**:
- `cash_secured_put` - Sell puts to acquire stock at discount
- `covered_call` - Sell calls against existing shares
- `long_call` - Buy calls for leveraged upside
- `long_put` - Buy puts for downside protection
- `iron_condor` - Neutral earnings play with defined risk
- `wheel_strategy` - Systematic CSP + covered call rotation

**Unusual Activity Criteria**:
- Volume > 2x Open Interest
- Volume > 1,000 contracts
- Premium > $100,000

**Greeks** (if mibian available):
- **Delta**: Rate of change in option price vs stock price
- **Gamma**: Rate of change in delta
- **Theta**: Time decay per day
- **Vega**: Sensitivity to IV changes

---

## Data Models

All agents return structured data using Pydantic-style dataclasses:

```python
@dataclass
class FundamentalAnalysis:
    score: int  # 0-100
    revenue_growth_yoy: float
    pe_ratio: float
    sector_avg_pe: float
    pb_ratio: float
    debt_to_equity: float
    roe: float
    free_cash_flow: float
    dividend_yield: float
    valuation_assessment: str
    key_strengths: List[str]
    key_risks: List[str]
    # ... more fields
```

See `models.py` for complete definitions.

## Error Handling

All agents implement production-ready error handling:

1. **Retry Logic**: Automatic retries with exponential backoff
2. **Fallback Data**: Returns neutral/default analysis if APIs fail
3. **Rate Limiting**: Detects and handles API rate limits
4. **Timeouts**: 30-second timeout on all HTTP requests
5. **Logging**: Comprehensive logging via loguru
6. **Exceptions**: Graceful handling of missing data

Example:
```python
try:
    result = await agent.analyze("INVALID")
except ValueError as e:
    print(f"Invalid symbol: {e}")
except RuntimeError as e:
    print(f"API failure: {e}")
```

## Caching

- **FundamentalAgent**: 6-hour TTL (fundamental data changes slowly)
- **TechnicalAgent**: No caching (real-time price data)
- **SentimentAgent**: No caching (sentiment changes rapidly)
- **OptionsAgent**: No caching (options data changes frequently)

## Performance

All agents support parallel execution:

```python
# Sequential (slow)
f = await fundamental.analyze("AAPL")
t = await technical.analyze("AAPL")
s = await sentiment.analyze("AAPL")
o = await options.analyze("AAPL")

# Parallel (4x faster)
results = await asyncio.gather(
    fundamental.analyze("AAPL"),
    technical.analyze("AAPL"),
    sentiment.analyze("AAPL"),
    options.analyze("AAPL")
)
```

**Typical Analysis Times** (parallel):
- Fundamental: 1-2 seconds (with caching)
- Technical: 0.5-1 second
- Sentiment: 2-5 seconds (with Reddit)
- Options: 1-3 seconds
- **Total**: ~5-8 seconds for complete analysis

## API Keys & Rate Limits

### Alpha Vantage (Fundamental Agent)
- **Free Tier**: 5 API calls per minute, 500 per day
- **Get Key**: https://www.alphavantage.co/support/#api-key
- **Caching**: Essential to stay within limits (6-hour cache implemented)

### Reddit API (Sentiment Agent - Optional)
- **Free Tier**: 60 requests per minute
- **Get Credentials**: https://www.reddit.com/prefs/apps
- **Required**: client_id, client_secret, user_agent

### yfinance (No API Key Required)
- Used by Technical and Options agents
- No official rate limits, but be respectful
- Occasional connection issues (handled with retries)

## Testing

Run the example script:
```bash
cd src/agents/ai_research
python example_usage.py
```

Set environment variables for full functionality:
```bash
export ALPHA_VANTAGE_API_KEY="your_key"
export REDDIT_CLIENT_ID="your_id"
export REDDIT_CLIENT_SECRET="your_secret"
python example_usage.py
```

## Integration Example

```python
from agents.ai_research import (
    FundamentalAgent,
    TechnicalAgent,
    SentimentAgent,
    OptionsAgent,
    ResearchReport,
    TradeRecommendation,
    TradeAction
)

async def generate_research_report(symbol: str) -> ResearchReport:
    """Generate complete research report for a symbol."""

    # Initialize agents
    agents = {
        "fundamental": FundamentalAgent(),
        "technical": TechnicalAgent(),
        "sentiment": SentimentAgent(),
        "options": OptionsAgent()
    }

    # Run all analyses
    fundamental, technical, sentiment, options = await asyncio.gather(
        agents["fundamental"].analyze(symbol),
        agents["technical"].analyze(symbol),
        agents["sentiment"].analyze(symbol),
        agents["options"].analyze(symbol)
    )

    # Calculate overall rating (1-5 stars)
    avg_score = (fundamental.score + technical.score + sentiment.score) / 3
    overall_rating = (avg_score / 100) * 5

    # Generate recommendation
    if avg_score >= 70:
        action = TradeAction.BUY
        confidence = 0.8
    elif avg_score >= 50:
        action = TradeAction.HOLD
        confidence = 0.6
    else:
        action = TradeAction.SELL
        confidence = 0.7

    recommendation = TradeRecommendation(
        action=action,
        confidence=confidence,
        reasoning=f"Overall score: {avg_score:.1f}/100",
        time_sensitive_factors=[],
        specific_position_advice={},
        suggested_adjustments=[]
    )

    # Build complete report
    report = ResearchReport(
        symbol=symbol,
        timestamp=datetime.now(),
        cached=False,
        overall_rating=overall_rating,
        quick_summary=f"{symbol} rated {overall_rating:.1f}/5 stars",
        fundamental=fundamental,
        technical=technical,
        sentiment=sentiment,
        options=options,
        recommendation=recommendation,
        metadata=AnalysisMetadata(
            api_calls_used=4,
            processing_time_ms=5000,
            agents_executed=4,
            agents_failed=[],
            cache_expires_at=datetime.now() + timedelta(hours=1),
            llm_model="N/A",
            llm_tokens_used=0
        )
    )

    return report
```

## Logging

All agents use loguru for structured logging:

```python
from loguru import logger

# Configure logging
logger.add(
    "ai_research.log",
    rotation="10 MB",
    retention="1 week",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
)
```

**Log Levels**:
- `DEBUG`: Detailed API responses, calculations
- `INFO`: Agent initialization, analysis completion
- `WARNING`: Fallback data usage, missing optional fields
- `ERROR`: API failures, exceptions

## Production Considerations

1. **Database Integration**: Cache results in Redis/PostgreSQL
2. **Rate Limiting**: Implement request queuing for API limits
3. **Monitoring**: Track agent success rates and latency
4. **Alerting**: Set up alerts for API failures or data quality issues
5. **Scaling**: Use Celery or similar for distributed agent execution
6. **Data Quality**: Validate API responses before processing
7. **Cost Management**: Monitor Alpha Vantage usage, upgrade if needed

## Troubleshooting

**Issue**: `ValueError: ALPHA_VANTAGE_API_KEY environment variable must be set`
- **Solution**: Set the environment variable or pass `api_key` parameter

**Issue**: `praw not installed, Reddit sentiment will be unavailable`
- **Solution**: `pip install praw` or use fallback sentiment (analysts only)

**Issue**: `pandas_ta not installed, will use custom indicator calculations`
- **Solution**: `pip install pandas-ta` for more accurate indicators

**Issue**: `mibian not installed, Greeks calculations will use Black-Scholes approximation`
- **Solution**: `pip install mibian` for precise Greeks via Black-Scholes

**Issue**: `Rate limit exceeded` (Alpha Vantage)
- **Solution**: Wait 60 seconds or use cached data (6-hour TTL)

**Issue**: Empty options chain or "No options available"
- **Solution**: Stock may not have options trading (ETFs, small caps)

## Contributing

To add a new agent:

1. Create new agent file following existing pattern
2. Implement `async analyze(symbol: str)` method
3. Return structured dataclass from `models.py`
4. Add comprehensive error handling and logging
5. Update `__init__.py` to export new agent
6. Add tests and documentation

## License

See project root LICENSE file.

## Support

For issues or questions:
1. Check logs in `ai_research.log`
2. Review API key configuration
3. Verify network connectivity to APIs
4. Check API status pages for outages

---

**Version**: 1.0.0
**Last Updated**: 2024
**Maintainer**: WheelStrategy Project
