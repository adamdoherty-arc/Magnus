# Calendar Spreads Feature - User Guide

## Table of Contents
1. [What Are Calendar Spreads?](#what-are-calendar-spreads)
2. [Why Use Calendar Spreads?](#why-use-calendar-spreads)
3. [Feature Overview](#feature-overview)
4. [Getting Started](#getting-started)
5. [Understanding the Analysis](#understanding-the-analysis)
6. [Risk Management](#risk-management)
7. [Best Practices](#best-practices)
8. [FAQ](#faq)

## What Are Calendar Spreads?

A calendar spread (also known as a time spread or horizontal spread) is an options strategy that involves simultaneously:
- **Selling** a near-term option (front month)
- **Buying** a longer-term option (back month)
- Both options have the **same strike price** and are on the same underlying stock

### The Core Concept
Calendar spreads profit from the differential rate of time decay (theta) between options with different expiration dates. The near-term option loses value faster than the longer-term option, creating profit potential when the stock price remains relatively stable.

### Example Trade
- Stock: AAPL trading at $150
- Sell: AAPL $150 Call expiring in 30 days for $3.00
- Buy: AAPL $150 Call expiring in 60 days for $5.00
- Net Debit: $2.00 (max loss)
- Max Profit: Achieved if AAPL is exactly at $150 when front month expires

## Why Use Calendar Spreads?

### Advantages
1. **Limited Risk**: Maximum loss is capped at the net premium paid
2. **Time Decay Profit**: Benefit from accelerated time decay of near-term options
3. **Lower Capital Requirements**: Less expensive than buying options outright
4. **Volatility Expansion Benefit**: Can profit from increases in implied volatility
5. **Flexible Management**: Can be rolled, adjusted, or converted to other strategies

### Ideal Market Conditions
- **Low to Moderate Implied Volatility** (IV < 30%)
- **Range-bound or Slowly Trending Markets**
- **Stable Price Action** near the strike price
- **No Major Events** before front-month expiration

## Feature Overview

### Automated Analysis Pipeline
1. **Watchlist Integration**: Pulls stocks from your TradingView watchlists
2. **Market Scanning**: Analyzes each stock for calendar spread opportunities
3. **AI-Powered Selection**: Uses machine learning to score and rank spreads
4. **Risk/Reward Calculation**: Computes max profit, max loss, and breakeven points
5. **Visual Dashboard**: Displays top opportunities with key metrics

### Key Metrics Displayed
- **Score** (0-100): AI-generated quality score
- **Max Profit**: Theoretical maximum gain
- **Max Loss**: Net premium paid (your risk)
- **Breakeven Points**: Upper and lower profitable ranges
- **Probability of Profit**: Statistical likelihood of profitable outcome
- **Greeks**: Delta, Theta, Vega, Gamma for the spread

## Getting Started

### Step 1: Connect TradingView
1. Navigate to Settings → Integrations
2. Enter your TradingView API credentials
3. Select watchlists to monitor
4. Set refresh frequency (recommended: every 15 minutes)

### Step 2: Configure Analysis Parameters
```json
{
  "max_iv": 30,
  "min_dte_front": 30,
  "max_dte_front": 45,
  "min_dte_back": 60,
  "max_dte_back": 90,
  "strike_selection": "atm",
  "min_volume": 100,
  "min_open_interest": 500
}
```

### Step 3: Review Opportunities
1. Open the Calendar Spreads dashboard
2. Sort by Score, Max Profit, or other metrics
3. Click on any spread for detailed analysis
4. Review the profit/loss diagram
5. Execute trades through your broker integration

## Understanding the Analysis

### Scoring Algorithm (0-100)
The AI scoring system evaluates each calendar spread based on:

#### Time Decay Score (30 points)
- Theta ratio between front and back month
- Optimal range: 1.5x to 2.5x faster decay in front month
- Higher differential = higher score

#### Volatility Score (25 points)
- Current IV percentile (lower is better)
- IV skew between months
- Historical volatility trends
- Target: IV < 30% percentile

#### Price Stability Score (25 points)
- Standard deviation over past 20 days
- Support/resistance levels
- Trend strength indicators
- Preference for range-bound stocks

#### Liquidity Score (10 points)
- Bid-ask spreads
- Volume and open interest
- Market depth

#### Risk/Reward Score (10 points)
- Max profit to max loss ratio
- Probability of profit
- Expected value calculation

### Profit/Loss Calculations

#### Maximum Loss
```
Max Loss = Net Premium Paid = Back Month Premium - Front Month Premium
```

#### Maximum Profit
Maximum profit occurs when the stock is at the strike price at front-month expiration:
```
Max Profit = Value of Back Month Option at Front Expiration - Net Premium Paid
```

#### Breakeven Points
Breakeven points vary with time and volatility but typically form a "tent" shape around the strike price.

### Greeks Analysis

#### Delta
- Near-neutral at initiation (typically -0.10 to +0.10)
- Indicates directional risk

#### Theta
- Positive (you collect time decay)
- Target: +$5 to +$20 per day per contract

#### Vega
- Negative in low IV environments
- Positive in high IV environments
- Indicates volatility risk

#### Gamma
- Near-zero at initiation
- Increases as front-month expiration approaches

## Risk Management

### Position Sizing
- **Conservative**: Risk 1-2% of account per trade
- **Moderate**: Risk 2-4% of account per trade
- **Aggressive**: Risk 4-6% of account per trade

### Exit Strategies

#### Profit Targets
- **Conservative**: Exit at 25% of max profit
- **Moderate**: Exit at 40-50% of max profit
- **Aggressive**: Hold until 1 week before expiration

#### Stop Losses
- Set stop at 50% of max loss
- Or exit if stock moves beyond expected range (±1.5 standard deviations)

### Adjustment Techniques
1. **Rolling**: Move front month to next expiration if profitable
2. **Strike Adjustment**: Shift strikes if stock moves significantly
3. **Conversion**: Transform into diagonal or vertical spread
4. **Hedge Addition**: Add protective positions if needed

## Best Practices

### Entry Timing
1. **Enter 30-45 days before front-month expiration**
2. **Avoid entering before earnings or major events**
3. **Best days**: Monday-Wednesday (avoid Friday gamma risk)
4. **Best time**: First 2 hours or last hour of trading day

### Stock Selection Criteria
- **Market Cap**: > $10 billion (liquid options)
- **Average Volume**: > 1 million shares/day
- **Options Volume**: > 1,000 contracts/day
- **IV Rank**: < 30th percentile
- **Price Range**: $50-$500 (optimal strikes available)

### Spread Selection
1. **At-the-Money (ATM)**: Maximum time decay, ideal for neutral outlook
2. **Slightly Out-of-the-Money**: Lower cost, good for mild directional bias
3. **Call vs Put**: Calls for bullish bias, puts for bearish bias

### Portfolio Allocation
- Maximum 20% of portfolio in calendar spreads
- Diversify across 5-10 different underlying stocks
- Balance between sectors and correlation

## FAQ

### Q: What happens if the stock moves significantly?
A: Large moves reduce profitability. The strategy works best when the stock stays near the strike price. Consider closing if stock moves beyond ±10% of strike.

### Q: Can I lose more than my initial investment?
A: No. Maximum loss is limited to the net premium paid when opening the position.

### Q: What happens at front-month expiration?
A: You have three choices:
1. Close both legs before expiration
2. Let front month expire, keep back month as long position
3. Roll the front month to a new expiration

### Q: How does implied volatility affect my position?
A: Rising IV generally helps calendar spreads (back month gains more than front month). Falling IV can reduce profitability.

### Q: Should I use calls or puts?
A: Both work similarly. Choose based on:
- Calls: Slightly bullish or neutral outlook
- Puts: Slightly bearish or neutral outlook
- Consider put-call parity and liquidity

### Q: What's the ideal holding period?
A: Typically 50-75% of the time until front-month expiration. Many traders exit when 40-50% of maximum profit is achieved.

### Q: How do dividends affect calendar spreads?
A: Dividends can cause early assignment risk on short calls. Avoid calendar spreads with calls if dividend date falls before front-month expiration.

### Q: Can I trade calendar spreads in an IRA?
A: Yes, most brokers allow calendar spreads in IRAs as they're considered a limited-risk strategy.

## Support and Resources

### Educational Resources
- Video Tutorial: "Mastering Calendar Spreads" (in-app)
- Webinar: Weekly calendar spread analysis (Thursdays 4 PM EST)
- Discord Community: #calendar-spreads channel

### Technical Support
- Email: support@wheelstrategy.com
- Live Chat: Available Monday-Friday 9 AM - 5 PM EST
- Knowledge Base: help.wheelstrategy.com/calendar-spreads

### Disclaimer
Options trading involves significant risk and is not suitable for all investors. Calendar spreads can result in losses equal to the net premium paid. Past performance does not guarantee future results. Always consult with a qualified financial advisor before making investment decisions.

---
*Last Updated: January 2025*
*Version: 1.0.0*