# TradingView Watchlists - User Guide

## Table of Contents
1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Feature Components](#feature-components)
4. [Current Positions](#current-positions)
5. [Trade History Management](#trade-history-management)
6. [Watchlist Management](#watchlist-management)
7. [Premium Analysis](#premium-analysis)
8. [Theta Decay Visualization](#theta-decay-visualization)
9. [Database Integration](#database-integration)
10. [Common Workflows](#common-workflows)
11. [Tips and Best Practices](#tips-and-best-practices)
12. [Troubleshooting](#troubleshooting)

## Overview

The TradingView Watchlists feature is a comprehensive option trading management system that integrates with Robinhood to provide real-time position tracking, premium analysis, and trade history management. It serves as your central hub for monitoring cash-secured puts (CSPs), covered calls (CCs), and other option strategies.

### Key Capabilities
- **Live Position Monitoring**: Real-time synchronization with Robinhood option positions
- **Trade History Tracking**: Comprehensive logging and analysis of closed trades
- **Watchlist Synchronization**: Auto-sync with TradingView and database storage
- **Premium Analysis**: 30-day option premium calculations with delta targeting
- **Performance Metrics**: Win rate, average returns, and P&L tracking
- **Theta Decay Charts**: Visual representation of time decay profits

## Quick Start

### Initial Setup

1. **Navigate to TradingView Watchlists**
   - Open the dashboard at `http://localhost:8501`
   - Select "TradingView Watchlists" from the sidebar menu

2. **Automatic Robinhood Connection**
   - The system automatically logs into Robinhood using stored credentials
   - Current positions load immediately upon page access

3. **First-Time Watchlist Sync**
   - If no watchlists are found, run: `python src/tradingview_api_sync.py`
   - Or use the Import Watchlist tab to manually add symbols

## Feature Components

### 1. Current Option Positions Section

This section displays all your active option positions from Robinhood in real-time.

#### Position Information Displayed:
- **Symbol**: Stock ticker
- **Strategy Type**:
  - CSP (Cash-Secured Put)
  - CC (Covered Call)
  - Long Call/Put
- **Strike Price**: Option strike price
- **Expiration Date**: Option expiration
- **DTE (Days to Expiration)**: Calculated automatically
- **Contracts**: Number of contracts held
- **Premium Collected**: Total premium received
- **Current Value**: Market value of position
- **P/L**: Profit/Loss calculation
- **P/L %**: Percentage return

#### Key Metrics Dashboard:
- **Active Positions**: Total number of open positions
- **Total Premium**: Sum of all premiums collected
- **Total P/L**: Current profit/loss across all positions
- **CSPs Count**: Number of cash-secured puts

### 2. Log Closed Trades Forms

Each position has an expandable form for logging when you close a trade.

#### Form Fields:
- **Close Price**: The price per contract you paid to close
- **Close Reason**:
  - `early_close`: Closed before expiration
  - `expiration`: Held to expiration
  - `assignment`: Stock was assigned
- **Open Date**: When the position was opened

#### Automatic Calculations:
- Profit/Loss amount and percentage
- Days held
- Annualized return

### 3. Trade History Section

Comprehensive historical record of all closed trades with advanced analytics.

#### Statistics Displayed:
- **Total Closed Trades**: Lifetime count
- **Total P/L**: Cumulative profit/loss
- **Win Rate**: Percentage of profitable trades
- **Average Days Held**: Mean holding period

#### Filtering Options:
- **Symbol Filter**: Search for specific stocks
- **Limit Selection**: Show last 20, 50, 100, or 200 trades

#### Data Export:
- Download CSV of trade history for tax reporting or analysis

## Watchlist Management

### Auto-Sync Tab

Automated synchronization with your TradingView watchlists stored in the database.

#### Features:
- **Refresh Watchlists**: Load all watchlists from database
- **Manual Import**: Switch to import tab for new symbols
- **Last Sync Timer**: Shows time since last refresh
- **Background Sync**: Non-blocking price and premium updates

#### Watchlist Selector:
- Dropdown showing all available watchlists
- Symbol count for each watchlist
- Automatic filtering of non-stock symbols (crypto, indices)

### Import Watchlist Tab

Manual symbol import for creating new watchlists.

#### Input Methods:
1. **Text Area Import**:
   - Comma-separated: `NVDA, AMD, AAPL, MSFT`
   - Line-separated: One symbol per line
   - Direct paste from TradingView

2. **Named Watchlist Creation**:
   - Custom naming for organization
   - Automatic database storage

3. **Load Existing**:
   - Dropdown of saved watchlists
   - Quick loading into analysis

### My Watchlist Analysis Tab

Comprehensive analysis of imported watchlist with real-time market data.

#### Analysis Features:
- **Real-time Price Data**: Current prices via yfinance
- **Premium Calculations**: ~5% OTM put premiums
- **Market Statistics**:
  - Stocks up/down today
  - Best/average returns
  - Options availability

#### Data Table Columns:
- Stock price and daily change
- Strike prices for puts
- Premium amounts
- Return percentages
- Volume indicators

### Saved Watchlists Tab

Management interface for stored watchlists.

#### Actions Available:
- **Load**: Set as current watchlist
- **Analyze**: Direct analysis navigation
- **Delete**: Remove from database

## Premium Analysis

### 30-Day Options Focus

The system specializes in analyzing 30-day options with optimal delta targeting.

#### Default Parameters:
- **DTE Range**: 28-32 days
- **Delta Target**: 0.25-0.40 (25-30% probability ITM)
- **Strike Selection**: ~5% OTM for puts

#### Premium Table Display:
- **Symbol**: Stock ticker
- **Stock Price**: Current market price
- **Strike**: Selected strike price
- **Premium**: Option premium in dollars
- **Delta**: Option delta value
- **Monthly %**: Monthly return percentage
- **IV**: Implied volatility
- **Bid/Ask**: Current market spread
- **Volume/OI**: Liquidity indicators

### Filtering Options

#### Price Filters:
- **Min Stock Price**: Filter out penny stocks
- **Max Stock Price**: Stay within budget
- **Min Premium**: Minimum acceptable premium

#### DTE Selection:
- 10, 17, 24, 31, 38, 52 days
- Automatic ±2 day range for flexibility

## Theta Decay Visualization

### Daily Profit Forecast

For each CSP/CC position, view projected daily profits from theta decay.

#### Decay Calculations:
- **Square Root Time Decay**: `decay_factor = sqrt(days_remaining) / sqrt(initial_dte)`
- **Accelerating Theta**: Increases as expiration approaches
- **Daily Profit Charts**: Visual representation of expected profits

#### Milestone Predictions:
- **7-Day Forecast**: Expected profit in one week
- **3-Day Forecast**: Short-term profit projection
- **Expiration Value**: Maximum profit potential

#### Recommendations:
- **>50% Captured**: "Already captured X% of max profit. Theta decay slowing."
- **<7 DTE**: "Maximum theta decay period! Earning ~$X/day"
- **>7 DTE**: "Theta will accelerate in X days when < 1 week remains"

## Database Integration

### PostgreSQL Schema

The feature uses three main database tables:

#### stock_data Table:
- Current prices
- Market metrics
- Last update timestamps

#### stock_premiums Table:
- Strike prices
- Premium amounts
- Greeks (delta, theta, etc.)
- Bid/ask spreads
- Volume/open interest

#### trade_history Table:
- Complete trade lifecycle
- P/L calculations
- Performance metrics

### Database Scan Tab

Access to full database of 1,200+ stocks with option data.

#### Features:
- **Overview Statistics**: Total stocks, sectors, price distribution
- **Add Stocks**: Bulk import with Yahoo Finance data
- **Premium Scanner**: Find opportunities across all database stocks
- **Analytics**: Sector distribution, price ranges, market stats

## Common Workflows

### Workflow 1: Daily Position Review

1. **Check Current Positions**
   - Review P/L status
   - Note positions approaching expiration
   - Check assignment risk (ITM positions)

2. **Log Closed Trades**
   - Use expandable forms for each closed position
   - Enter actual close prices
   - System calculates P/L automatically

3. **Review Trade History**
   - Check win rate trend
   - Analyze average holding periods
   - Export data if needed

### Workflow 2: Finding New Opportunities

1. **Import/Load Watchlist**
   - Use Import tab or load saved list
   - Ensure symbols are valid stocks

2. **Sync Prices & Premiums**
   - Click sync button for background update
   - Wait for data population

3. **Analyze Options**
   - Sort by Monthly % for best returns
   - Check delta for probability
   - Verify liquidity (Volume/OI)

4. **Place Trade**
   - Note selected strikes and premiums
   - Execute in Robinhood
   - Return to log when filled

### Workflow 3: Weekly Planning

1. **Review Theta Decay Charts**
   - Check positions with <7 DTE
   - Plan early closes for 50%+ profit

2. **Scan Database**
   - Use Database Scan for broader opportunities
   - Filter by your criteria
   - Add promising stocks to watchlist

3. **Update Watchlists**
   - Remove underperformers
   - Add new discoveries
   - Organize by strategy/sector

## Tips and Best Practices

### Position Management
- **Log Trades Immediately**: Record trades as soon as closed for accurate tracking
- **Use Correct Close Reason**: Helps analyze strategy effectiveness
- **Monitor Delta**: Positions with delta > 0.40 have higher assignment risk

### Watchlist Organization
- **Sector Diversification**: Create watchlists by sector
- **Size Limits**: Keep watchlists under 50 symbols for performance
- **Regular Updates**: Refresh weekly to maintain current data

### Premium Optimization
- **Sweet Spot**: 30-45 DTE offers best theta decay curve
- **Delta Targeting**: 0.25-0.30 balances premium and risk
- **Liquidity Check**: Ensure Volume > 100 and OI > 50

### Database Maintenance
- **Regular Syncs**: Run background sync daily for fresh data
- **Clean Old Data**: Remove stocks no longer traded
- **Monitor Performance**: Large databases may slow queries

## Troubleshooting

### Common Issues and Solutions

#### "No open option positions found"
- **Cause**: No active options in Robinhood
- **Solution**: Verify positions exist in Robinhood app

#### "No watchlists found"
- **Cause**: Database not synchronized
- **Solution**: Run `python src/tradingview_api_sync.py` or use Import tab

#### "No 30-day options found"
- **Cause**: Data not synced for watchlist
- **Solution**: Click "Sync Prices & Premiums" button

#### Slow Performance
- **Cause**: Large watchlist or database
- **Solution**: Reduce watchlist size, use filters, clean database

#### Login Failures
- **Cause**: Robinhood credentials incorrect
- **Solution**: Update credentials in `.env` file

#### Missing Premium Data
- **Cause**: Options not available or low liquidity
- **Solution**: Check different DTE ranges or more liquid stocks

### Data Accuracy
- **Price Delays**: Free data may have 15-minute delay
- **Greeks Calculation**: Based on Black-Scholes model
- **P/L Tracking**: Depends on accurate trade logging

### Performance Tips
- **Limit Watchlist Size**: 20-30 symbols optimal
- **Use Filters**: Reduce data processing
- **Background Sync**: Don't wait for updates
- **Database Indexes**: Ensure proper indexing

## Advanced Features

### Multi-Strategy Support
- Track different option strategies simultaneously
- Separate analytics for CSPs vs CCs
- Combined P/L reporting

### Risk Metrics
- Position-level risk assessment
- Portfolio delta exposure
- Sector concentration warnings

### Integration Points
- Robinhood API for live data
- TradingView for watchlist management
- PostgreSQL for persistence
- Yahoo Finance for market data

### Automation Capabilities
- Background price synchronization
- Automatic P/L calculations
- Trade history aggregation
- Performance metric computation

## Support and Resources

### Getting Help
- Check error messages in UI
- Review PostgreSQL logs
- Verify API connections
- Consult technical documentation

### Related Documentation
- [ARCHITECTURE.md](ARCHITECTURE.md) - Technical design details
- [SPEC.md](SPEC.md) - Detailed requirements
- [WISHLIST.md](WISHLIST.md) - Future enhancements

### External Resources
- [Robinhood API Documentation](https://robin-stocks.readthedocs.io/)
- [TradingView Pine Script](https://www.tradingview.com/pine-script-docs/)
- [Options Greeks Explained](https://www.investopedia.com/trading/using-the-greeks-to-understand-options/)