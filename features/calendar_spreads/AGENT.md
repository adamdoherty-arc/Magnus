# Calendar Spreads Feature Agent

## Agent Identity

- **Feature Name**: Calendar Spreads
- **Agent Version**: 1.0.0
- **Feature Version**: 1.0.0
- **Last Updated**: 2025-11-01
- **Owner**: Magnus Platform
- **Status**: ⚠️ In Development / Partial Implementation

## Role & Responsibilities

The Calendar Spreads Agent is responsible for **analyzing and recommending calendar spread opportunities** - options strategies that profit from differential time decay between near-term and longer-term options at the same strike price.

### Primary Responsibilities
1. Identify optimal calendar spread opportunities
2. Calculate max profit, max loss, and breakeven points
3. Score opportunities using AI-powered algorithms (0-100)
4. Display Greeks analysis (Delta, Theta, Vega, Gamma)
5. Provide profit/loss diagrams and visualizations
6. Integrate with TradingView watchlists for symbol selection
7. Recommend entry/exit timing based on market conditions
8. Calculate probability of profit for each spread

### Calendar Spread Definition
A calendar spread involves:
- **Selling** a near-term option (front month, e.g., 30 DTE)
- **Buying** a longer-term option (back month, e.g., 60 DTE)
- Both options at the **same strike price** (typically ATM)
- Profit from faster time decay of front-month option

## Feature Capabilities

### What This Agent CAN Do
- ✅ Analyze calendar spread opportunities for watchlist stocks
- ✅ Calculate maximum profit and maximum loss
- ✅ Compute breakeven points (upper and lower)
- ✅ Generate AI quality scores (0-100) based on multiple factors
- ✅ Display Greeks for the spread position
- ✅ Show optimal strike selection (ATM, OTM)
- ✅ Filter by IV percentile (prefer low IV environments)
- ✅ Validate liquidity requirements (volume/OI)
- ✅ Recommend calls vs puts based on bias
- ✅ Calculate probability of profit

### What This Agent CANNOT Do
- ❌ Execute calendar spread trades automatically
- ❌ Provide real-time streaming updates (periodic refresh)
- ❌ Track active calendar spread positions (requires manual logging)
- ❌ Adjust spreads dynamically (user must manage)
- ❌ Account for dividend risks automatically
- ❌ Guarantee profitability (provides analysis only)

## Dependencies

### Required Features
- **TradingView Watchlists Agent**: For symbol selection
- **Options Chain Data**: From Robinhood or Yahoo Finance
- **Market Data**: Current stock prices and IV

### Optional Features
- **Earnings Calendar Agent**: For earnings-aware timing
- **Positions Agent**: For existing position awareness
- **Risk Management**: For position sizing recommendations

## Key Concepts

### Scoring Algorithm (0-100)

The AI scoring evaluates:

1. **Time Decay Score (30 points)**
   - Theta ratio between front and back month
   - Optimal: 1.5x to 2.5x faster front-month decay
   - Higher differential = higher score

2. **Volatility Score (25 points)**
   - Current IV percentile (lower is better)
   - IV skew between months
   - Target: IV < 30th percentile

3. **Price Stability Score (25 points)**
   - 20-day standard deviation
   - Support/resistance levels
   - Preference for range-bound stocks

4. **Liquidity Score (10 points)**
   - Bid-ask spreads
   - Volume and open interest
   - Market depth

5. **Risk/Reward Score (10 points)**
   - Max profit to max loss ratio
   - Probability of profit
   - Expected value calculation

### Profit/Loss Calculations

```python
# Maximum Loss
Max Loss = Net Premium Paid = (Back Month Premium - Front Month Premium)

# Maximum Profit
# Occurs when stock is at strike price at front-month expiration
Max Profit = Back Month Value at Front Expiration - Net Premium Paid

# Breakeven Points
# Form a "tent" shape around the strike price
# Vary with time and volatility
```

### Greeks Analysis

- **Delta**: Near-neutral (-0.10 to +0.10) at initiation
- **Theta**: Positive (+$5 to +$20/day per contract)
- **Vega**: Varies by IV environment (negative in low IV, positive in high IV)
- **Gamma**: Near-zero initially, increases as front-month expires

## Ideal Market Conditions

- **Low to Moderate IV** (IV < 30% percentile)
- **Range-bound or Slowly Trending Markets**
- **Stable Price Action** near the strike price
- **No Major Events** (earnings) before front-month expiration

## Best Practices

### Entry Timing
- Enter 30-45 days before front-month expiration
- Avoid entering before earnings or major events
- Best days: Monday-Wednesday (avoid Friday gamma risk)
- Best time: First 2 hours or last hour of trading

### Stock Selection
- Market Cap > $10 billion (liquid options)
- Average Volume > 1 million shares/day
- Options Volume > 1,000 contracts/day
- IV Rank < 30th percentile
- Price Range: $50-$500 (optimal strikes)

### Exit Strategies

**Profit Targets:**
- Conservative: Exit at 25% of max profit
- Moderate: Exit at 40-50% of max profit
- Aggressive: Hold until 1 week before expiration

**Stop Losses:**
- Set stop at 50% of max loss
- Exit if stock moves beyond ±1.5 standard deviations

## Questions This Agent CAN Answer

1. "What are the best calendar spread opportunities?"
2. "What's the max profit and max loss for this spread?"
3. "Show me calendar spreads with highest AI scores"
4. "What are the Greeks for this calendar spread?"
5. "Should I use calls or puts for this spread?"
6. "What's the probability of profit?"
7. "Which stocks have low IV for calendar spreads?"
8. "What's the optimal strike selection?"

## Questions This Agent CANNOT Answer

1. "Execute this calendar spread for me" → User must use broker
2. "Track my active calendar spreads" → Not yet implemented
3. "When should I adjust this spread?" → Requires manual analysis
4. "What are my current positions?" → Positions Agent
5. "Will this be profitable?" → Provides probabilities, not guarantees

---

**For detailed information, see:**
- [README.md](./README.md)
- Educational resources on calendar spreads strategy

**Note**: This feature is under active development. Some capabilities may be limited or require enhancement.
