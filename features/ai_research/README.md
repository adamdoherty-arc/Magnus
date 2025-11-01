# AI Research Assistant

## Overview

The AI Research Assistant provides comprehensive, AI-powered stock analysis for every position in your portfolio. Using a multi-agent system powered by LangChain and CrewAI, it delivers fundamental analysis, technical insights, sentiment tracking, and options-specific intelligence.

## Quick Start

### Access AI Research

1. Navigate to the **Positions** page
2. Find any position in your portfolio
3. Click the **🤖 AI Research** icon next to the position
4. View comprehensive analysis in modal/sidebar

### What You Get

- **⭐ Quick Summary** - Overall rating and recommendation (4/5 stars)
- **📊 Fundamental Score** - Company financials, earnings, valuation (0-100)
- **📈 Technical Score** - Chart patterns, indicators, support/resistance (0-100)
- **💬 Sentiment Score** - News, social media, institutional activity (0-100)
- **🎯 Options Insights** - IV rank, earnings moves, probability calculations
- **💡 Trade Recommendation** - Specific guidance for your position

## Features

### Fundamental Analysis
- Company overview and business model
- Financial statements (revenue, earnings, cash flow)
- Valuation metrics (P/E, P/B, PEG, DCF)
- Earnings trends and analyst ratings
- Competitive positioning

### Technical Analysis
- Price trend identification
- Chart pattern recognition
- Technical indicators (RSI, MACD, Bollinger Bands)
- Support and resistance levels
- Volume analysis

### Sentiment Analysis
- News sentiment (last 7 days)
- Reddit/StockTwits social sentiment
- Institutional buying/selling activity
- Insider trading alerts
- Analyst upgrades/downgrades

### Options Intelligence
- Implied volatility (IV) rank and percentile
- Historical earnings price movements
- Options flow (unusual activity)
- Probability of profit calculations
- Best strike/expiration suggestions

## Multi-Agent Architecture

The AI Research system uses 4 specialized agents:

```
Main Research Orchestrator
├── Fundamental Analyst Agent (financials, valuation)
├── Technical Analyst Agent (charts, indicators)
├── Sentiment Analyst Agent (news, social media)
└── Options Strategist Agent (Greeks, IV, probabilities)
```

Each agent specializes in its domain and collaborates to provide comprehensive analysis.

## Data Sources

### Free Tier APIs (No Cost)
- **Alpha Vantage** - 500 calls/day, financial fundamentals
- **Yahoo Finance** - Unlimited, price data and charts
- **Reddit API** - Free tier, social sentiment
- **yfinance** - Unlimited, options chains and Greeks

### LLM Providers (Choose One)
- **Groq** - Fast inference, free tier (recommended)
- **Ollama** - Local LLMs, unlimited and private
- **OpenAI** - Pay-per-use, highest quality (optional upgrade)

## Caching Strategy

To stay within free tier limits:
- Analysis cached for **30 minutes**
- Refresh during market hours (9:30 AM - 4:00 PM ET)
- Static cache after hours
- Manual refresh available anytime

## Example Usage

### Cash-Secured Put Holder

```
Position: AAPL $170 CSP, expires in 15 days
You: Click 🤖 AI Research

AI Analysis:
⭐⭐⭐⭐☆ (4/5) - HOLD

Fundamental: 85/100 - Strong earnings growth, solid balance sheet
Technical: 60/100 - Sideways trend, RSI neutral at 52
Sentiment: 75/100 - Positive news, neutral social media
Options: IV Rank 45 (moderate), earnings in 23 days

💡 Recommendation for your CSP:
HOLD - Fundamentals strong, IV moderate.
Stock trading above your strike with good support.
Consider rolling up and out if you want more premium.

Risk: Earnings announcement in 23 days may increase volatility.
```

### Covered Call Writer

```
Position: TSLA shares + $250 CC, expires in 7 days
You: Click 🤖 AI Research

AI Analysis:
⭐⭐⭐☆☆ (3/5) - MONITOR CLOSELY

Fundamental: 70/100 - Revenue growing, but valuation stretched
Technical: 80/100 - Strong uptrend, momentum positive
Sentiment: 65/100 - Mixed news, high social media buzz
Options: IV Rank 72 (elevated), recent unusual call buying

💡 Recommendation for your CC:
MONITOR - Strong technical momentum + high IV suggests
potential for assignment. Stock at $245, approaching your
$250 strike. Consider rolling out if you want to keep shares.

Risk: High probability of assignment (68%). Prepare exit plan.
```

## Performance

- **Cached Analysis**: <3 seconds
- **Fresh Analysis**: <30 seconds
- **API Calls**: ~10 per stock
- **Daily Limit**: ~50 unique stocks (500 API calls / 10 per stock)

## Configuration

### Setup (One-Time)

1. **Get API Keys** (free):
   ```bash
   # Alpha Vantage
   https://www.alphavantage.co/support/#api-key

   # Groq (optional, for cloud LLM)
   https://console.groq.com/keys
   ```

2. **Add to .env**:
   ```env
   ALPHA_VANTAGE_API_KEY=your_key_here
   GROQ_API_KEY=your_key_here  # Optional
   LLM_PROVIDER=groq  # or 'ollama' for local
   ```

3. **Install Dependencies**:
   ```bash
   pip install langchain crewai alpha-vantage groq yfinance redis
   ```

4. **Start Redis** (for caching):
   ```bash
   # Windows (using Docker)
   docker run -d -p 6379:6379 redis

   # Or use Windows Subsystem for Linux
   sudo service redis-server start
   ```

### Usage Limits

**Free Tier**:
- Alpha Vantage: 500 calls/day
- Groq: 30 requests/minute
- Reddit: 60 requests/minute

**Tips to Stay Within Limits**:
- Research is cached for 30 minutes
- Limit to ~50 unique stocks per day
- Use manual refresh sparingly
- Consider Ollama for unlimited local inference

## Troubleshooting

### "API rate limit exceeded"
**Solution**: Wait 1 minute or switch to cached data

### "Analysis taking too long"
**Solution**: Check Redis cache service, may need restart

### "LLM connection error"
**Solution**:
- Groq: Verify API key in .env
- Ollama: Ensure ollama service running (`ollama serve`)

### "No data available"
**Solution**: Symbol may not be supported by data providers

## Privacy & Security

- **API keys**: Stored securely in .env (never committed to git)
- **Data**: Cached locally in Redis (not shared externally)
- **LLM**: Choose Ollama for fully local, private analysis
- **Logs**: Redacted API keys in application logs

## Future Enhancements

See [WISHLIST.md](WISHLIST.md) for planned features:
- Earnings calendar integration
- Real-time alerts for significant changes
- Portfolio-level risk analysis
- Backtesting trade recommendations
- Custom analysis templates

## Related Features

- **Positions** - View all positions with AI research buttons
- **Opportunities** - AI-powered screening for new trades
- **Premium Scanner** - AI recommendations for optimal strikes

## Support

For issues or questions:
1. Check logs: `logs/ai_research_YYYYMMDD.log`
2. Verify API keys in `.env`
3. Test API connections: `python src/agents/test_ai_connections.py`
4. Review [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

**Version**: 1.0.0
**Status**: ✅ Active Development
**Last Updated**: 2025-11-01
