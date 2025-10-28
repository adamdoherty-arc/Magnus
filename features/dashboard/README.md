# Dashboard Feature

## Overview

The Dashboard is the central hub of the WheelStrategy trading application, providing real-time portfolio insights, comprehensive trade history tracking, and AI-powered analysis for options trading strategies. It serves as the main landing page where traders can monitor their cash-secured put positions, track performance metrics, and make data-driven decisions about their wheel strategy trades.

## Key Capabilities

- **Portfolio Status Overview**
  - Real-time account balance and buying power
  - Total premium collected across all positions
  - Capital at risk calculation
  - Active position count

- **Trade History Management**
  - Complete trade lifecycle tracking (open, close, assignment)
  - Automatic P&L calculations with annualized returns
  - Cumulative profit/loss visualization
  - Manual trade entry and closing interface

- **Balance Forecast Timeline**
  - Expiration date projections
  - Best/expected/worst case scenarios
  - Monthly return calculations
  - Capital deployment analysis

- **Individual Position Forecasts**
  - Position-specific P&L tracking
  - Real-time theta decay calculations
  - Assignment probability estimates
  - Breakeven price analysis

- **Theta Decay Profit Forecast**
  - Daily profit projections
  - Accelerating theta visualization
  - Milestone profit targets (3-day, 7-day)
  - Average daily theta calculations

- **AI Trade Analysis**
  - Smart exit recommendations
  - Profit-taking alerts (20%, 50%, 75% thresholds)
  - Risk assessment (HIGH/MEDIUM/LOW)
  - Portfolio-wide action suggestions

## How to Use

### Step 1: Access the Dashboard

1. Launch the WheelStrategy application:
   ```bash
   streamlit run dashboard.py
   ```

2. The Dashboard loads automatically as the default page
3. If not connected to Robinhood, you'll see a prompt to connect in Settings

### Step 2: Connect to Robinhood (Optional)

1. Navigate to Settings page using the sidebar
2. Enter your Robinhood credentials:
   - Username/Email
   - Password
   - MFA Secret (if two-factor authentication is enabled)
3. Click "Connect to Robinhood"
4. Return to Dashboard to see live portfolio data

### Step 3: Track Your Trades

#### Adding a New Trade Manually:

1. Click the **"+ Add Trade"** button in the Trade History section
2. Fill in the trade details:
   - **Symbol**: Stock ticker (e.g., NVDA)
   - **Strike Price**: Option strike price
   - **Premium Collected**: Total premium received
   - **Expiration Date**: Option expiration date
   - **Contracts**: Number of contracts
   - **Open Date**: When the trade was opened
   - **Notes**: Optional trade notes
3. Click **"Save Trade"** to record the position

#### Closing an Open Trade:

1. Scroll to the "Open Positions" section
2. Expand the position you want to close
3. Enter the closing details:
   - **Close Price**: Amount paid to buy back the option
   - **Reason**: Select from dropdown (early_close, expiration, assignment)
4. Click **"Close Trade"** to finalize

### Step 4: Monitor Performance Metrics

The dashboard displays five key metrics at the top:

- **Total Trades**: Number of completed trades
- **Total P/L**: Cumulative profit/loss with win rate
- **Best Trade**: Most profitable trade details
- **Worst Trade**: Least profitable trade details
- **Avg Days Held**: Average position duration

### Step 5: Analyze Balance Forecasts

The Balance Forecast Timeline shows:

- **Expiration Date Projections**: Grouped by expiration date
- **Premium Income**: Total premium potential per date
- **Capital at Risk**: Maximum capital deployment
- **Three Scenarios**:
  - Best Case: All options expire worthless (keep all premium)
  - Expected: 70% expire worthless (statistical average)
  - Worst Case: All options assigned (deploy capital)

### Step 6: Review Position-Specific Forecasts

For each active CSP position, view:

- **Current Status**: P&L, daily theta, cost to close
- **Forecast**: Max profit, return on risk, annualized return
- **Risk Analysis**: Capital required, breakeven price, assignment probability

### Step 7: Monitor Theta Decay

The Theta Decay section provides:

- **Daily Profit Forecast**: See expected profits day-by-day
- **Acceleration Visualization**: Theta increases near expiration
- **Profit Milestones**: Track progress toward profit targets
- **Recommendations**: Timing guidance for maximum theta capture

### Step 8: Follow AI Recommendations

The AI Trade Analysis section offers:

- **Portfolio-Level Actions**: Overall strategy recommendations
- **High-Profit Exit Alerts**: Positions ready for profit-taking
- **Individual Analysis**: Position-specific guidance with urgency levels
  - BUY_BACK_IMMEDIATELY: 75%+ profit captured
  - BUY_BACK_RECOMMENDED: 50%+ profit with time remaining
  - MONITOR_CLOSELY: 25%+ profit, approaching target
  - PREPARE_FOR_ASSIGNMENT: ITM with <7 days
  - HOLD_TO_EXPIRY: <3 days, maximum theta
  - HOLD_POSITION: Continue collecting theta

## Screenshots

### Main Dashboard View
![Dashboard Overview](./screenshots/dashboard-overview.png)
*Complete portfolio overview with key metrics and trade history*

### Trade Entry Form
![Add Trade Form](./screenshots/add-trade-form.png)
*Manual trade entry interface for tracking positions*

### Balance Forecast Timeline
![Balance Forecast](./screenshots/balance-forecast.png)
*Projected account balance across expiration dates*

### Theta Decay Analysis
![Theta Decay](./screenshots/theta-decay.png)
*Daily profit projections showing accelerating theta*

### AI Recommendations
![AI Analysis](./screenshots/ai-recommendations.png)
*Smart recommendations for profit-taking and risk management*

## Tips and Best Practices

1. **Regular Updates**: Add trades immediately after execution for accurate tracking
2. **Profit Targets**: Follow the 50% profit rule for optimal returns
3. **AI Guidance**: Pay attention to HIGH urgency recommendations
4. **Theta Monitoring**: Focus on positions with <7 days for maximum decay
5. **Risk Management**: Monitor assignment probabilities for ITM positions
6. **Documentation**: Use the Notes field to record trade rationale

## Troubleshooting

### Common Issues:

**Dashboard not loading:**
- Ensure PostgreSQL database is running
- Check database connection in `.env` file
- Verify Redis server is active (for caching)

**Robinhood connection fails:**
- Verify credentials are correct
- Check for MFA requirements
- Clear cached session: delete `.robinhood_token.pickle`

**Trade calculations incorrect:**
- Ensure all trade details are entered correctly
- Verify dates are in proper format (YYYY-MM-DD)
- Check that close price includes all fees

**Missing real-time data:**
- Confirm Robinhood connection is active
- Check internet connectivity
- Refresh positions using the refresh button

## Related Documentation

- [Architecture Documentation](./ARCHITECTURE.md) - Technical implementation details
- [Specifications](./SPEC.md) - Detailed feature specifications
- [Wishlist](./WISHLIST.md) - Planned enhancements and future features