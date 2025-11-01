# Prediction Markets Feature

## Overview

The Prediction Markets feature integrates with Kalshi's event contract marketplace to provide AI-powered analysis of trading opportunities across politics, sports, economics, and more. It complements the Magnus platform's options trading capabilities by offering access to binary outcome markets where users can trade on real-world events.

Unlike traditional options, prediction markets allow you to trade contracts that pay $1.00 if a specific event occurs (e.g., "Will the Fed raise rates in March?"). The feature uses a quantitative scoring algorithm to identify the best opportunities based on liquidity, time value, risk-reward ratio, and bid-ask spreads.

## Key Capabilities

- **AI-Powered Market Scoring**
  - Quantitative analysis scoring each market 0-100
  - Multi-factor evaluation: liquidity, time value, risk-reward, spread quality
  - Automated recommendation engine (Yes/No/Skip)
  - Risk level assessment (Low/Medium/High)

- **Comprehensive Market Coverage**
  - Politics: Elections, legislation, appointments
  - Sports: NFL, NBA, MLB, MMA, Tennis, Golf
  - Economics: Fed rates, CPI, GDP, employment
  - Crypto: Bitcoin price levels, ETF approvals
  - Companies: Earnings, M&A, product launches
  - Tech & Science: AI milestones, space launches
  - Climate: Temperature records, weather events
  - World: International events, geopolitics

- **Real-Time Market Data**
  - Current Yes/No pricing from Kalshi orderbook
  - 24-hour trading volume and open interest
  - Bid-ask spread analysis
  - Days to market close
  - Contract resolution dates

- **Intelligent Filtering**
  - Filter by category (All, Politics, Sports, etc.)
  - Minimum AI score threshold
  - Maximum days to close
  - High-quality market identification (Score >75)

## How to Use

### Step 1: Access Prediction Markets

1. Launch the Magnus application:
   ```bash
   streamlit run dashboard.py
   ```

2. Navigate to **Prediction Markets** from the sidebar menu
3. The page will automatically fetch and score markets from Kalshi

### Step 2: Understanding the Interface

The main interface displays:

- **Filter Controls** (top row):
  - Category dropdown (All, Politics, Sports, Economics, etc.)
  - Min Score slider (default: 60)
  - Max Days input (default: 90)
  - Refresh button to reload data

- **Summary Metrics** (4 columns):
  - Total Markets: All fetched markets
  - High Quality (>75): Premium opportunities
  - Avg Score: Average across filtered markets
  - Showing: Count of displayed markets

### Step 3: Interpreting Market Cards

Each market opportunity displays as an expandable card:

**Card Header** shows:
- Color-coded emoji (Green/Yellow/Red)
- AI Score (0-100)
- Category and days to close
- Market title

**Inside the card** (when expanded):

**Pricing Section:**
- Yes Price: Cost to buy Yes contract (pays $1 if event occurs)
- No Price: Cost to buy No contract (pays $1 if event doesn't occur)

**Volume & Liquidity:**
- 24h Volume: Trading activity (higher = more liquid)
- Spread: Bid-ask spread (tighter = lower trading costs)

**Recommendation:**
- Position: Yes/No/Skip/Maybe
- Risk Level: Low/Medium/High

**AI Analysis:**
- Detailed reasoning explaining the score
- Factors considered: liquidity, timeframe, risk-reward, spread

**Expected Value:**
- Positive percentage indicates favorable odds
- Calculated based on risk-reward analysis

**Action Buttons:**
- View on Robinhood: Opens Robinhood app (if available)
- View on Kalshi: Opens Kalshi market page

**Market Details:**
- Full ticker, category, close date
- Market description and rules

### Step 4: Evaluating Opportunities

**AI Score Interpretation:**
- **85-100** (Fire Emoji): Exceptional opportunity
  - Excellent liquidity
  - Optimal timeframe
  - Strong risk-reward
  - Tight spread

- **75-84** (Star Emoji): High quality
  - Good liquidity
  - Reasonable timeframe
  - Acceptable risk-reward
  - Competitive spread

- **60-74** (Thumbs Up): Worth considering
  - Moderate liquidity
  - Decent timeframe
  - Fair risk-reward
  - Average spread

- **<60** (Thumbs Down): Skip
  - Low liquidity
  - Poor timeframe
  - Weak risk-reward
  - Wide spread

### Step 5: Making Trading Decisions

**Position Recommendations:**

- **Yes**: AI suggests buying Yes contracts
  - Market is priced below fair value
  - High upside if event occurs
  - Risk-reward favors Yes side

- **No**: AI suggests buying No contracts
  - Market is priced above fair value
  - Good probability event won't occur
  - Better risk-reward on No side

- **Maybe**: Consider but not strong recommendation
  - Moderate opportunity
  - Medium risk-reward
  - Requires manual analysis

- **Skip**: Avoid this market
  - Poor liquidity
  - Weak fundamentals
  - Better opportunities available

### Step 6: Executing Trades

Magnus displays opportunities but **does not execute trades** directly. To trade:

1. Click "View on Robinhood" or "View on Kalshi"
2. Review the full market details on the platform
3. Execute trades manually through your brokerage account
4. Magnus provides analysis; you maintain full trading control

### Step 7: Using Filters Effectively

**By Category:**
- Select specific categories for focused analysis
- "All" shows cross-category opportunities
- Useful for specialization (e.g., only sports markets)

**By Score:**
- Increase min score to see only premium opportunities
- Lower for broader market coverage
- Default 60 balances quality and quantity

**By Time:**
- Shorter timeframes (7-30 days) typically more predictable
- Longer timeframes (>90 days) have more uncertainty
- Adjust based on your trading horizon

## Screenshots

### Main Prediction Markets View
![Prediction Markets Overview](./screenshots/prediction-markets-overview.png)
*AI-scored opportunities with filtering controls and summary metrics*

### Market Card (Expanded)
![Market Card Detail](./screenshots/market-card-expanded.png)
*Detailed market information with AI analysis and recommendations*

### High-Score Opportunities
![High Quality Markets](./screenshots/high-quality-markets.png)
*Premium opportunities (Score >75) with strong fundamentals*

### Category Filtering
![Category Filter](./screenshots/category-filter.png)
*Filter markets by specific categories for targeted analysis*

### AI Analysis Detail
![AI Reasoning](./screenshots/ai-analysis-detail.png)
*Detailed AI reasoning showing scoring factors*

## Tips and Best Practices

### Market Selection
1. **Focus on High Scores**: Markets >75 have the best fundamentals
2. **Check Liquidity**: Volume >1000 contracts ensures easy entry/exit
3. **Monitor Spreads**: Spreads <2% minimize trading costs
4. **Consider Timeframe**: 7-30 day windows balance certainty and return
5. **Diversify Categories**: Don't concentrate in single category

### Risk Management
1. **Start Small**: Begin with 1-2 contracts to learn mechanics
2. **Use Position Sizing**: Never risk more than 5% of capital per market
3. **Set Limits**: Know maximum loss before entering
4. **Track Performance**: Monitor wins vs losses over time
5. **Avoid FOMO**: Skip markets with low scores even if popular

### Analysis Approach
1. **Read AI Reasoning**: Understand why score was assigned
2. **Check Expected Value**: Positive EV indicates favorable odds
3. **Review Market Details**: Read full description and rules
4. **Consider External Factors**: News, polls, expert analysis
5. **Validate Assumptions**: AI is a tool, not a guarantee

### Trading Strategy
1. **Buy Underpriced**: Look for Yes <30% or No <30% with high scores
2. **Sell Expensive**: Markets often misprice certain outcomes
3. **Time Decay**: Prices adjust as expiration approaches
4. **Event Catalysts**: Trade before major announcements
5. **Exit Strategy**: Set profit targets and stop losses

### Platform Usage
1. **Refresh Regularly**: Markets update hourly (use refresh button)
2. **Compare Platforms**: Cross-check Robinhood vs Kalshi pricing
3. **Use Filters**: Narrow results to match your interests
4. **Track Top Picks**: Revisit high-scoring markets over time
5. **Learn Patterns**: Study which markets perform best

## Understanding Prediction Markets

### How They Work

Prediction markets are binary outcome contracts that settle at $1.00 or $0.00:

- **Yes Contract**: Pays $1.00 if event occurs, $0.00 if not
- **No Contract**: Pays $1.00 if event doesn't occur, $0.00 if it does

**Example:**
- Market: "Will Fed raise rates in March?"
- Yes Price: $0.65 (65 cents)
- No Price: $0.35 (35 cents)

**If you buy Yes at $0.65:**
- Event occurs → You receive $1.00 (profit: $0.35)
- Event doesn't occur → Contract expires worthless (loss: $0.65)

**If you buy No at $0.35:**
- Event doesn't occur → You receive $1.00 (profit: $0.65)
- Event occurs → Contract expires worthless (loss: $0.35)

### Pricing Mechanics

Prices represent market consensus probability:
- $0.75 Yes = Market thinks 75% chance event occurs
- $0.25 No = Market thinks 25% chance event doesn't occur
- Yes + No prices always equal $1.00

### Trading Strategies

**1. Buy Undervalued Outcomes**
- Find markets where AI score is high but price is low
- Example: 70% probability priced at 50% = buy Yes

**2. Fade Overreactions**
- Markets often overreact to news
- Buy the opposite side when panic/euphoria sets in

**3. Arbitrage Opportunities**
- Rare but possible: Yes + No < $1.00 on different platforms
- Buy both sides for guaranteed profit

**4. Time-Based Trading**
- Early entry: Prices more uncertain, bigger moves possible
- Late entry: Prices more efficient, smaller profit margins

### Risk Factors

**Market Risks:**
- Low liquidity: Difficulty entering/exiting positions
- Wide spreads: High transaction costs
- Information asymmetry: Others may have better data

**Operational Risks:**
- Settlement disputes: Market resolution may be unclear
- Platform issues: Exchange downtime or errors
- Regulatory changes: CFTC oversight may affect markets

**Behavioral Risks:**
- Overconfidence: AI scores are probabilities, not certainties
- Recency bias: Recent events don't predict future outcomes
- Confirmation bias: Seeking data that supports your position

## Troubleshooting

### Common Issues

**Markets not loading:**
- Check internet connection
- Verify Kalshi API is accessible (https://api.elections.kalshi.com)
- Click refresh button to retry
- Clear browser cache and reload page

**AI scores show as 0:**
- Insufficient pricing data from Kalshi
- Market may be new or illiquid
- Orderbook data unavailable
- Skip these markets

**"Rate Limited" warning:**
- Kalshi allows 100 requests/minute
- Wait 60 seconds and click refresh
- Markets are cached for 1 hour to prevent rate limiting

**Expected value shows as 0 or negative:**
- Market is efficiently priced
- No clear edge identified
- Consider skipping unless you have additional insight

**Stale data (timestamps old):**
- Click refresh button to fetch latest
- Cache TTL is 1 hour by default
- Check "last_updated" in market details

**Categories missing markets:**
- Kalshi may not have active markets in that category
- Try "All" to see what's available
- Some categories are seasonal (e.g., elections)

**Spreads seem very wide:**
- Low liquidity markets naturally have wider spreads
- Filter for higher volume markets
- Avoid trading illiquid markets

### Error Messages

**"No markets found. Kalshi API may be unavailable":**
- Kalshi API is temporarily down
- Network connectivity issue
- Try again in a few minutes

**"Failed to fetch markets: [error]":**
- API request failed
- Check console logs for details
- Report persistent errors to developers

**"Insufficient pricing data":**
- Orderbook is empty
- Market recently opened or closed
- Skip this market

## Frequently Asked Questions

**Q: Do I need a Kalshi account?**
A: No, Magnus displays public market data. To trade, you need a Robinhood or Kalshi account.

**Q: Are AI scores guaranteed to be accurate?**
A: No, scores are quantitative assessments based on market fundamentals. They indicate quality, not certainty of outcomes.

**Q: Can I execute trades through Magnus?**
A: No, Magnus is an analysis tool. Use the platform links to trade on Robinhood or Kalshi.

**Q: How often are markets updated?**
A: Markets are cached for 1 hour. Click refresh for latest data.

**Q: What's the difference between Robinhood and Kalshi?**
A: Same markets, potentially different pricing. Robinhood has simpler UX; Kalshi has more markets and features.

**Q: Why do some markets show "Skip" recommendation?**
A: Low score indicates poor fundamentals (low liquidity, wide spread, or weak risk-reward).

**Q: Can I filter by expected value?**
A: Not currently, but markets are sorted by AI score which incorporates expected value.

**Q: Are there fees for trading prediction markets?**
A: Yes, check your brokerage. Kalshi charges transaction fees; Robinhood may vary.

**Q: What happens if a market doesn't resolve clearly?**
A: Kalshi has dispute resolution rules. Magnus doesn't handle settlement.

**Q: Can I trade on margin or short contracts?**
A: No, prediction markets are cash-settled. Maximum loss is your purchase price.

## Related Documentation

- [Architecture Documentation](./ARCHITECTURE.md) - Technical implementation details
- [Specifications](./SPEC.md) - Detailed feature specifications
- [Wishlist](./WISHLIST.md) - Planned enhancements and future features
- [Agent Documentation](./AGENT.md) - Agent coordination and responsibilities

## Additional Resources

- [Kalshi Documentation](https://kalshi.com/docs) - Official API documentation
- [Prediction Market Theory](https://en.wikipedia.org/wiki/Prediction_market) - Academic background
- [CFTC Guidance](https://www.cftc.gov/) - Regulatory framework
- [Magnus Main Documentation](../../README.md) - Platform overview
