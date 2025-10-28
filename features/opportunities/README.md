# Opportunities Feature - User Guide

## Table of Contents
1. [Overview](#overview)
2. [Understanding Premium Opportunities](#understanding-premium-opportunities)
3. [Using the Premium Scanner](#using-the-premium-scanner)
4. [Interpreting Results](#interpreting-results)
5. [Trading Strategies](#trading-strategies)
6. [Best Practices](#best-practices)
7. [Common Scenarios](#common-scenarios)
8. [Troubleshooting](#troubleshooting)

## Overview

The Opportunities feature is your intelligent options trading assistant, designed to identify the most profitable cash-secured put (CSP) opportunities for the wheel strategy. It systematically scans the market to find options with optimal risk-reward ratios, helping you maximize returns while managing risk effectively.

### What It Does

The feature performs three core functions:

1. **Market Scanning**: Analyzes multiple stocks to find those with attractive option premiums
2. **Opportunity Ranking**: Evaluates and ranks opportunities based on return potential
3. **Risk Assessment**: Filters opportunities based on liquidity and assignment risk

### Key Benefits

- **Time Efficiency**: Automates hours of manual research into seconds
- **Objective Analysis**: Removes emotional bias from trade selection
- **Return Optimization**: Identifies the highest-yielding opportunities within your risk parameters
- **Liquidity Focus**: Ensures you only see tradable opportunities with sufficient volume

## Understanding Premium Opportunities

### The Wheel Strategy Context

In the wheel strategy, finding the right entry point is crucial. The Opportunities feature focuses on:

1. **Cash-Secured Puts (CSPs)**: The foundation of the wheel strategy
2. **Premium Collection**: Maximizing income while waiting for assignment
3. **Strike Selection**: Balancing premium income with assignment probability

### What Makes a Good Opportunity

The system evaluates opportunities based on multiple factors:

#### 1. Premium Percentage
- **Definition**: Premium received as a percentage of strike price
- **Target Range**: 1-3% for monthly options (30 DTE)
- **Significance**: Higher percentages mean better capital efficiency

#### 2. Annualized Return
- **Calculation**: (Premium % / Days to Expiry) × 365
- **Good Range**: 12-36% annually
- **Reality Check**: Consider assignment risk at higher returns

#### 3. Implied Volatility (IV)
- **Sweet Spot**: 30-60% IV
- **Too Low (<20%)**: Minimal premiums
- **Too High (>80%)**: Excessive risk, possible underlying issues

#### 4. Liquidity Metrics
- **Volume**: Minimum 100 contracts daily
- **Open Interest**: At least 50 contracts
- **Bid-Ask Spread**: Should be less than 10% of premium

### Delta and Strike Selection

The system focuses on out-of-the-money (OTM) puts with specific characteristics:

- **Target Delta**: -0.20 to -0.30 (20-30% probability of assignment)
- **Strike Range**: 5-10% below current stock price
- **Rationale**: Balances premium income with assignment probability

## Using the Premium Scanner

### Step-by-Step Guide

#### 1. Accessing the Scanner
Navigate to the "Premium Scanner" page in the dashboard. You'll see:
- Strategy selection dropdown
- Filter parameters
- Scan button
- Results table

#### 2. Selecting a Strategy

Choose from predefined scanning strategies:

**Best Overall Premiums**
- Balanced approach for steady income
- Scans all liquid stocks under your price limit
- Best for beginners

**High IV Plays (40%+)**
- Targets volatile stocks with rich premiums
- Higher returns but increased risk
- Suitable for experienced traders

**Weekly Options (7-14 DTE)**
- Short-term plays for active traders
- Requires more frequent management
- Higher annualized returns potential

**Monthly Options (30-45 DTE)**
- Standard wheel strategy timeframe
- Better time decay characteristics
- Lower maintenance requirements

**Tech Stocks Under $50**
- Focus on technology sector
- Generally higher IV and premiums
- Sector concentration risk

**All Stocks Under $50**
- Broadest scan for capital-efficient plays
- Maximum diversification potential
- Includes all sectors

#### 3. Setting Parameters

Configure your scan filters:

**Max Stock Price**
- Default: $50
- Range: $10-200
- Purpose: Matches your available capital per position

**Minimum Premium %**
- Default: 1.0%
- Range: 0.5-5.0%
- Higher values = fewer but better opportunities

**Target Days to Expiration**
- Options: 7, 14, 21, 30, 45 days
- Default: 30 days (optimal for wheel strategy)
- Shorter = higher annualized returns, more management

#### 4. Running the Scan

Click "Scan for Premiums" to initiate the search. The system will:
1. Query current market data
2. Filter stocks by price
3. Analyze options chains
4. Calculate returns
5. Rank opportunities

**Expected Duration**: 30-60 seconds depending on market conditions

### Understanding Scan Results

#### Results Table Columns

**Symbol**
- Stock ticker symbol
- Click to research the underlying company

**Stock Price**
- Current market price
- Used to calculate capital requirements

**Strike**
- Recommended put strike price
- Usually 5-10% below current price

**DTE (Days to Expiry)**
- Time until option expiration
- Affects annualized return calculations

**Premium/Contract**
- Dollar amount received per contract (100 shares)
- Your immediate income if trade executes

**Premium %**
- Premium as percentage of strike
- Key efficiency metric

**Monthly Return**
- Normalized 30-day return
- Allows comparison across different DTEs

**Annual Return**
- Extrapolated yearly return if repeatedly successful
- Assumes continuous premium collection

**IV (Implied Volatility)**
- Market's expectation of price movement
- Higher IV = higher premiums but more risk

**Volume**
- Contracts traded today
- Indicates current interest and liquidity

#### Summary Metrics

At the top of results, you'll see three key averages:
1. **Average Premium %**: Overall premium efficiency
2. **Average Monthly Return**: Expected monthly income potential
3. **Average Annual Return**: Long-term return projection

## Interpreting Results

### Reading the Opportunities Table

The table is sorted by monthly return by default, but consider multiple factors:

#### High Return Opportunities (>3% Monthly)
- **Pros**: Excellent income potential
- **Cons**: Higher assignment risk, possible underlying issues
- **Action**: Research the company for news/events

#### Moderate Return Opportunities (1.5-3% Monthly)
- **Pros**: Sustainable returns, reasonable risk
- **Cons**: Requires more capital for meaningful income
- **Action**: Core positions for wheel strategy

#### Lower Return Opportunities (<1.5% Monthly)
- **Pros**: Very low assignment risk, stable stocks
- **Cons**: Limited income potential
- **Action**: Conservative positions or skip

### Top 5 Detailed Analysis

The expanded view for top opportunities shows:

**Left Column - Pricing**
- Stock Price: Current market value
- Strike Price: Your obligation level if assigned
- Premium/Contract: Immediate income

**Middle Column - Timing**
- Days to Expiry: Time value component
- Premium %: Capital efficiency
- Monthly Return: Standardized comparison

**Right Column - Risk Metrics**
- Annual Return: Long-term potential
- Implied Volatility: Risk indicator
- Volume: Liquidity confirmation

### Red Flags to Avoid

Watch for these warning signs:

1. **Extremely High Returns (>5% Monthly)**
   - Often indicates distressed companies
   - Check for bankruptcy risk or major issues

2. **Very Low Volume (<50 contracts)**
   - Difficult to enter/exit positions
   - Wide bid-ask spreads eat into profits

3. **Excessive IV (>100%)**
   - Indicates extreme uncertainty
   - Possible binary events (FDA approval, earnings)

4. **Minimal Open Interest (<25 contracts)**
   - No market depth
   - May face significant slippage

## Trading Strategies

### Conservative Approach

**Target Returns**: 1-2% monthly (12-24% annually)

**Selection Criteria**:
- Established companies with steady business
- IV between 25-40%
- Delta around -0.20 (20% assignment probability)
- Minimum 200 volume, 100 open interest

**Best For**:
- Beginning traders
- Retirement accounts
- Risk-averse investors

**Example Trade**:
- Stock: AAPL at $150
- Sell: $140 Put, 30 DTE
- Premium: $1.50 (1.07%)
- Monthly Return: 1.07%
- Annual Return: 12.8%

### Balanced Approach

**Target Returns**: 2-3% monthly (24-36% annually)

**Selection Criteria**:
- Mix of growth and value stocks
- IV between 35-55%
- Delta around -0.25 to -0.30
- Minimum 100 volume, 50 open interest

**Best For**:
- Experienced traders
- Moderate risk tolerance
- Active portfolio management

**Example Trade**:
- Stock: SQ at $65
- Sell: $60 Put, 30 DTE
- Premium: $1.20 (2.0%)
- Monthly Return: 2.0%
- Annual Return: 24%

### Aggressive Approach

**Target Returns**: 3-5% monthly (36-60% annually)

**Selection Criteria**:
- High-growth or volatile stocks
- IV above 50%
- Delta around -0.30 to -0.35
- Accept lower liquidity for higher returns

**Best For**:
- Risk-tolerant traders
- Small position sizes
- Speculation allocation

**Example Trade**:
- Stock: RIOT at $12
- Sell: $11 Put, 30 DTE
- Premium: $0.45 (4.1%)
- Monthly Return: 4.1%
- Annual Return: 49%

### Portfolio Construction

**Diversification Guidelines**:
1. **Sector Allocation**: No more than 30% in one sector
2. **Position Sizing**: 5-10% of portfolio per position
3. **Stock Correlation**: Avoid multiple positions in similar companies
4. **Expiration Laddering**: Spread expirations across weeks

**Sample Portfolio (Conservative)**:
- 20% Technology (MSFT, AAPL)
- 20% Finance (JPM, BAC)
- 20% Consumer (DIS, NKE)
- 20% Healthcare (JNJ, PFE)
- 20% Industrial (BA, CAT)

## Best Practices

### 1. Pre-Trade Checklist

Before entering any opportunity:

- [ ] Check recent company news
- [ ] Verify earnings date (avoid if <2 weeks)
- [ ] Confirm dividend dates
- [ ] Review 3-month price chart
- [ ] Calculate capital requirements
- [ ] Ensure diversification rules met

### 2. Position Management

**Entry Rules**:
- Only sell puts on stocks you want to own
- Ensure adequate capital for assignment
- Start with 50% of intended position size

**Monitoring**:
- Check positions daily at minimum
- Set alerts for 50% profit
- Track days to expiration

**Exit Strategies**:
- Close at 50% profit if >50% time remaining
- Roll down and out if challenged
- Accept assignment if fundamentals unchanged

### 3. Risk Management

**Capital Allocation**:
- Never use more than 50% of available capital
- Keep 30% cash for opportunities
- Reserve 20% for assignments

**Loss Limits**:
- Maximum 3% portfolio loss per position
- Stop if down 10% in a month
- Reassess strategy after 3 losing trades

### 4. Record Keeping

Track for each trade:
- Entry date and price
- Premium collected
- Expiration date
- Exit date and result
- Actual vs. expected return
- Lessons learned

## Common Scenarios

### Scenario 1: High Premium, Low Volume

**Situation**: Found 4% monthly return but only 20 contracts volume

**Analysis**:
- Attractive premium suggests high risk
- Low volume means poor liquidity
- Likely wide bid-ask spread

**Action**: Skip or enter with limit order at mid-price

### Scenario 2: Earnings Coming Up

**Situation**: Great premium but earnings in 10 days

**Analysis**:
- IV inflated due to earnings
- Binary event risk
- Potential for large move

**Options**:
1. Skip the trade
2. Trade after earnings with lower IV
3. Reduce position size significantly

### Scenario 3: Stock Dropped After Entry

**Situation**: Stock fell 5% day after selling put

**Analysis**:
- Put is now in-the-money
- Assignment more likely
- Unrealized loss on option

**Actions**:
1. Do nothing if you want the stock
2. Roll down and out for credit
3. Close position if fundamentals changed

### Scenario 4: Quick Profit Opportunity

**Situation**: Position up 40% profit in 3 days (27 DTE remaining)

**Analysis**:
- Captured significant profit quickly
- Much time value remaining
- Opportunity cost of holding

**Best Practice**: Close position and redeploy capital

## Troubleshooting

### No Results Found

**Possible Causes**:
1. Filters too restrictive
2. Market conditions unfavorable
3. Low volatility environment

**Solutions**:
- Lower minimum premium to 0.5%
- Increase max stock price
- Try different strategy selection

### Results Loading Slowly

**Possible Causes**:
1. Market data delays
2. High market volatility
3. Network issues

**Solutions**:
- Wait 60 seconds for complete results
- Try scanning during market hours
- Reduce number of symbols scanned

### Unexpected High Returns

**Investigation Steps**:
1. Check for special dividends
2. Look for merger/acquisition news
3. Verify no data errors
4. Research company fundamentals

**Action**: Usually indicates elevated risk - proceed with caution

### Data Freshness Concerns

**Indicators**:
- Last scan time shows old timestamp
- Prices seem outdated
- Volume numbers very low

**Solutions**:
- Click scan button to refresh
- Clear browser cache
- Verify market is open

## Advanced Features

### Custom Watchlists

While the scanner uses predefined lists, you can:
1. Focus on specific sectors
2. Create mental filters for results
3. Track favorite opportunities

### Multi-Timeframe Analysis

Compare opportunities across different expirations:
- Weekly (7-14 DTE): Higher frequency, more management
- Bi-weekly (14-21 DTE): Balance of return and time
- Monthly (30-45 DTE): Standard wheel timeframe

### Opportunity Patterns

Learn to recognize:
- **Pre-earnings Elevation**: IV rises 1-2 weeks before
- **Post-earnings Crush**: IV drops dramatically after
- **Friday Effect**: Weekly options often cheaper on Friday
- **Monthly Cycles**: Best premiums early in expiration cycle

## Conclusion

The Opportunities feature transforms complex market data into actionable trading ideas. By following this guide, you'll be able to:
- Identify high-quality premium opportunities
- Make informed trading decisions
- Manage risk effectively
- Build a profitable wheel strategy portfolio

Remember: The tool provides opportunities, but your judgment on company quality, risk tolerance, and portfolio fit determines success. Always do additional research before trading, and never risk more than you can afford to lose.

**Happy Trading!**