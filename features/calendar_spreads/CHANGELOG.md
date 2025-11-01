# Changelog

All notable changes to the Calendar Spreads feature will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Live profit/loss diagram visualization
- Real-time Greeks tracking for spreads
- Automatic adjustment recommendations
- Roll calculator for position management
- Historical spread performance tracking
- Multi-leg order preparation
- Broker integration for direct execution
- Alert system for optimal exit timing

## [1.0.0] - 2025-10-28

### Added
- **Automated Calendar Spread Analysis**
  - Intelligent identification of optimal calendar spread opportunities
  - Simultaneous front-month and back-month analysis
  - Same-strike spread construction
  - Multiple expiration combination evaluation
- **AI-Powered Scoring System (0-100)**
  - **Time Decay Score (30 points)**: Theta ratio analysis
  - **Volatility Score (25 points)**: IV percentile and skew
  - **Price Stability Score (25 points)**: Range-bound identification
  - **Liquidity Score (10 points)**: Bid-ask and volume analysis
  - **Risk/Reward Score (10 points)**: Max profit to max loss ratio
- **Comprehensive Spread Metrics**
  - Maximum profit calculation
  - Maximum loss (net debit) calculation
  - Breakeven point estimation
  - Probability of profit analysis
  - Expected value computation
  - Greeks for the spread (Delta, Theta, Vega, Gamma)
- **Strategic Expiration Selection**
  - Front month: 30-45 DTE (near-term)
  - Back month: 60-90 DTE (longer-term)
  - Optimal time decay differential
  - Configurable DTE ranges
- **Watchlist Integration**
  - TradingView watchlist synchronization
  - Automatic symbol import
  - Watchlist categorization
  - Real-time sync capability
  - 15-minute refresh frequency
- **Market Condition Analysis**
  - Low to moderate IV detection (IV < 30%)
  - Range-bound market identification
  - Stability scoring based on 20-day standard deviation
  - Support/resistance level consideration
  - Trend strength indicators
- **Risk Management Tools**
  - Position sizing guidelines
  - Conservative/Moderate/Aggressive strategies
  - Exit strategy recommendations
  - Stop loss calculation
  - Profit target suggestions
  - Adjustment technique guidance
- **Visual Dashboard**
  - Top opportunities display
  - Sortable by score/profit/risk metrics
  - Detailed spread analysis cards
  - Color-coded quality indicators
  - Quick-reference format
- **Greeks Analysis**
  - Delta: Near-neutral at initiation (-0.10 to +0.10)
  - Theta: Positive collection ($5-$20/day target)
  - Vega: Volatility risk indicator
  - Gamma: Directional risk tracking
- **Entry Timing Optimization**
  - Best entry: 30-45 days before front expiration
  - Event avoidance (earnings, dividends)
  - Optimal trading days (Monday-Wednesday)
  - Ideal trading times (first 2 hours, last hour)
- **Stock Selection Criteria**
  - Market cap > $10 billion for liquidity
  - Average volume > 1 million shares/day
  - Options volume > 1,000 contracts/day
  - IV rank < 30th percentile
  - Price range: $50-$500 for optimal strikes

### Strategy Templates
- **At-the-Money (ATM) Spreads**
  - Maximum time decay capture
  - Ideal for neutral outlook
  - Highest profit potential
- **Slightly Out-of-the-Money Spreads**
  - Lower cost entry
  - Directional bias accommodation
  - Reduced risk with lower max loss
- **Call vs. Put Selection**
  - Calls for bullish bias
  - Puts for bearish bias
  - Put-call parity consideration

### Configuration
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

### Risk Parameters
- **Position Sizing**
  - Conservative: 1-2% of account
  - Moderate: 2-4% of account
  - Aggressive: 4-6% of account
- **Profit Targets**
  - Conservative: Exit at 25% of max profit
  - Moderate: Exit at 40-50% of max profit
  - Aggressive: Hold until 1 week before expiration
- **Stop Losses**
  - 50% of max loss threshold
  - Exit if stock moves ±1.5 standard deviations

### Adjustment Techniques
1. **Rolling**: Move front month to next expiration
2. **Strike Adjustment**: Shift strikes if stock moves
3. **Conversion**: Transform to diagonal/vertical spread
4. **Hedge Addition**: Add protective positions

### Educational Resources
- Video tutorial: "Mastering Calendar Spreads"
- Weekly analysis webinar (Thursdays 4 PM EST)
- Discord community: #calendar-spreads channel
- Knowledge base integration

### Technical Implementation
- TradingView API integration for symbol sources
- Real-time options chain analysis
- Black-Scholes Greeks calculation
- IV percentile tracking
- Historical volatility analysis
- Market depth evaluation
- Bid-ask spread optimization

### Use Cases
- **Neutral Income**: Capitalize on time decay in range-bound markets
- **Volatility Harvesting**: Benefit from IV expansion
- **Low Capital Strategies**: Limited risk with defined max loss
- **Portfolio Diversification**: Non-directional position complement

### Portfolio Guidelines
- Maximum 20% allocation to calendar spreads
- Diversify across 5-10 different underlying stocks
- Balance between sectors
- Monitor correlation between positions

### Compliance & Disclaimers
- Options trading involves significant risk
- Not suitable for all investors
- Maximum loss: Net premium paid
- Past performance doesn't guarantee future results
- Consult qualified financial advisor

[1.0.0]: https://github.com/yourusername/WheelStrategy/releases/tag/calendar-spreads-v1.0.0
