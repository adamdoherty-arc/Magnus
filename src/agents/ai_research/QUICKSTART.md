# Quick Start Guide - AI Research Agents

Get up and running with the AI Research Agents in 5 minutes.

## Step 1: Install Dependencies

```bash
# Core dependencies (required)
pip install yfinance pandas numpy aiohttp loguru

# Optional but recommended
pip install pandas-ta mibian praw
```

Or use the project requirements:
```bash
pip install -r requirements.txt
```

## Step 2: Set API Keys

### Alpha Vantage (Required for Fundamental Agent)
Get free API key: https://www.alphavantage.co/support/#api-key

**Windows:**
```cmd
set ALPHA_VANTAGE_API_KEY=YOUR_KEY_HERE
```

**Linux/Mac:**
```bash
export ALPHA_VANTAGE_API_KEY=YOUR_KEY_HERE
```

### Reddit (Optional for Sentiment Agent)
Get credentials: https://www.reddit.com/prefs/apps (create "script" app)

**Windows:**
```cmd
set REDDIT_CLIENT_ID=YOUR_ID
set REDDIT_CLIENT_SECRET=YOUR_SECRET
```

**Linux/Mac:**
```bash
export REDDIT_CLIENT_ID=YOUR_ID
export REDDIT_CLIENT_SECRET=YOUR_SECRET
```

## Step 3: Basic Usage

Create a file `test_agents.py`:

```python
import asyncio
from agents.ai_research import (
    FundamentalAgent,
    TechnicalAgent,
    SentimentAgent,
    OptionsAgent
)

async def analyze_stock(symbol):
    """Analyze a stock with all 4 agents."""

    # Initialize agents
    fundamental = FundamentalAgent()
    technical = TechnicalAgent()
    sentiment = SentimentAgent()
    options = OptionsAgent()

    # Run all agents in parallel (faster!)
    print(f"Analyzing {symbol}...")
    results = await asyncio.gather(
        fundamental.analyze(symbol),
        technical.analyze(symbol),
        sentiment.analyze(symbol),
        options.analyze(symbol)
    )

    fund, tech, sent, opts = results

    # Display key metrics
    print(f"\n{'='*60}")
    print(f"Analysis Results for {symbol}")
    print(f"{'='*60}")

    print(f"\nFundamental Score: {fund.score}/100")
    print(f"  P/E Ratio: {fund.pe_ratio:.2f}")
    print(f"  Valuation: {fund.valuation_assessment}")

    print(f"\nTechnical Score: {tech.score}/100")
    print(f"  Trend: {tech.trend.value}")
    print(f"  RSI: {tech.rsi:.2f}")

    print(f"\nSentiment Score: {sent.score}/100")
    print(f"  Analyst Rating: {sent.analyst_rating.value}")
    print(f"  Social Sentiment: {sent.social_sentiment.value}")

    print(f"\nOptions Analysis:")
    print(f"  IV Rank: {opts.iv_rank}/100")
    print(f"  Days to Earnings: {opts.days_to_earnings}")

    # Overall recommendation
    avg_score = (fund.score + tech.score + sent.score) / 3
    print(f"\n{'='*60}")
    print(f"Overall Score: {avg_score:.1f}/100")

    if avg_score >= 70:
        print("Recommendation: BULLISH")
    elif avg_score >= 50:
        print("Recommendation: NEUTRAL")
    else:
        print("Recommendation: BEARISH")
    print(f"{'='*60}\n")

# Run it
if __name__ == "__main__":
    asyncio.run(analyze_stock("AAPL"))
```

Run from the project root:
```bash
cd c:\Code\WheelStrategy\src
python test_agents.py
```

## Step 4: Advanced Usage

### Analyze Multiple Stocks

```python
async def analyze_multiple(symbols):
    """Analyze multiple stocks in parallel."""
    tasks = [analyze_stock(symbol) for symbol in symbols]
    await asyncio.gather(*tasks)

# Analyze FAANG stocks
asyncio.run(analyze_multiple(["AAPL", "MSFT", "GOOGL", "META", "AMZN"]))
```

### Use Individual Agents

```python
# Just fundamental analysis
async def quick_fundamental(symbol):
    agent = FundamentalAgent()
    result = await agent.analyze(symbol)

    print(f"P/E: {result.pe_ratio}")
    print(f"P/B: {result.pb_ratio}")
    print(f"ROE: {result.roe*100:.2f}%")
    print(f"Debt/Equity: {result.debt_to_equity}")

    for strength in result.key_strengths:
        print(f"+ {strength}")

    for risk in result.key_risks:
        print(f"- {risk}")

asyncio.run(quick_fundamental("TSLA"))
```

### Access Detailed Data

```python
async def detailed_options_analysis(symbol):
    agent = OptionsAgent()
    result = await agent.analyze(symbol)

    # Show strategy recommendations
    print(f"\nRecommended Strategies for {symbol}:")
    for i, strategy in enumerate(result.recommended_strategies, 1):
        print(f"\n{i}. {strategy.strategy.upper()}")
        print(f"   Strike: ${strategy.strike:.2f}")
        print(f"   Expiration: {strategy.expiration}")
        print(f"   Premium: ${strategy.premium:.2f}")
        print(f"   P(Profit): {strategy.probability_of_profit*100:.1f}%")
        print(f"   Max Profit: ${strategy.max_profit:.2f}")
        print(f"   Rationale: {strategy.rationale}")

    # Show unusual activity
    if result.unusual_options_activity:
        print(f"\nUnusual Activity:")
        for activity in result.unusual_options_activity:
            print(f"  {activity.option_type} ${activity.strike} - "
                  f"Vol: {activity.volume:,}, Premium: ${activity.premium:,.0f}")

asyncio.run(detailed_options_analysis("NVDA"))
```

## Common Patterns

### 1. Error Handling

```python
async def safe_analysis(symbol):
    agent = FundamentalAgent()

    try:
        result = await agent.analyze(symbol)
        return result
    except ValueError as e:
        print(f"Invalid symbol: {e}")
        return None
    except RuntimeError as e:
        print(f"API error: {e}")
        return None
```

### 2. Custom Scoring

```python
async def custom_score(symbol):
    """Calculate custom weighted score."""
    agents = [FundamentalAgent(), TechnicalAgent(), SentimentAgent()]
    results = await asyncio.gather(*[a.analyze(symbol) for a in agents])

    # Custom weights
    weights = [0.5, 0.3, 0.2]  # 50% fundamental, 30% technical, 20% sentiment
    weighted_score = sum(r.score * w for r, w in zip(results, weights))

    print(f"Custom Score: {weighted_score:.1f}/100")
    return weighted_score
```

### 3. Filtering Stocks

```python
async def filter_undervalued_stocks(symbols):
    """Find stocks with P/E below sector average."""
    agent = FundamentalAgent()
    undervalued = []

    for symbol in symbols:
        result = await agent.analyze(symbol)
        if result.pe_ratio > 0 and result.pe_ratio < result.sector_avg_pe:
            undervalued.append((symbol, result.pe_ratio, result.sector_avg_pe))

    print("Undervalued Stocks:")
    for symbol, pe, sector_pe in undervalued:
        discount = ((sector_pe - pe) / sector_pe) * 100
        print(f"  {symbol}: P/E {pe:.2f} vs Sector {sector_pe:.2f} ({discount:.1f}% discount)")

    return undervalued

symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "META"]
asyncio.run(filter_undervalued_stocks(symbols))
```

## Tips & Tricks

### 1. Speed Up Analysis
- Run agents in parallel with `asyncio.gather()`
- Cache is automatic for FundamentalAgent (6 hours)
- Use `return_exceptions=True` to handle errors gracefully

### 2. Handle Rate Limits
- Alpha Vantage: 5 calls/min, 500/day
- Caching helps stay under limits
- Run sequential for many stocks: `await asyncio.sleep(12)` between calls

### 3. Interpret Scores
- 70+: Strong signal (consider buying/holding)
- 50-70: Neutral (mixed signals, be cautious)
- <50: Weak signal (avoid or consider shorting)

### 4. Combine Signals
```python
def make_decision(fundamental, technical, sentiment):
    """Simple decision logic combining all agents."""
    scores = [fundamental.score, technical.score, sentiment.score]
    avg = sum(scores) / 3

    # All agents agree (bullish)
    if all(s >= 70 for s in scores):
        return "STRONG BUY"

    # Most agents bullish
    elif avg >= 70:
        return "BUY"

    # Fundamental strong, but technical weak (wait for entry)
    elif fundamental.score >= 70 and technical.score < 50:
        return "WAIT FOR DIP"

    # Mixed signals
    elif 50 <= avg < 70:
        return "HOLD"

    # Bearish
    else:
        return "AVOID"
```

## Troubleshooting

### Import Error: "No module named 'agents'"
Run from `src` directory:
```bash
cd c:\Code\WheelStrategy\src
python your_script.py
```

### Warning: "pandas_ta not installed"
Install it:
```bash
pip install pandas-ta
```
Or ignore - manual calculations are still accurate.

### Warning: "Using fallback fundamental analysis"
- Check if ALPHA_VANTAGE_API_KEY is set
- Check if you've hit rate limit (wait 60 seconds)
- Check if symbol is valid (use yfinance to verify)

### Error: "No options available for SYMBOL"
Some stocks don't have options:
- Check if it's a small-cap or ETF
- Use other agents (fundamental, technical, sentiment)

## Next Steps

1. Read the full README.md for detailed documentation
2. Check example_usage.py for comprehensive examples
3. Review models.py to understand data structures
4. Integrate agents into your application
5. Add tests for your use cases

## Support

- Check logs in `ai_research.log`
- Review agent docstrings
- See IMPLEMENTATION_SUMMARY.md for technical details

---

Happy analyzing!
