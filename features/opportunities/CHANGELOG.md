# Changelog

All notable changes to the Opportunities feature will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Custom watchlist creation for opportunity scanning
- Historical opportunity tracking and performance
- Email/SMS alerts for high-quality opportunities
- Comparison tools for multiple opportunities
- IV percentile rankings for better timing
- Earnings date integration to avoid binary events
- Sector rotation analysis and recommendations

## [1.0.0] - 2025-10-28

### Added
- **Intelligent Premium Scanner**
  - Automated market-wide opportunity discovery
  - Multi-stock analysis with ranking algorithm
  - Real-time options chain evaluation
  - Liquidity-focused filtering
- **Predefined Scanning Strategies**
  - Best Overall Premiums (balanced approach)
  - High IV Plays (40%+ implied volatility)
  - Weekly Options (7-14 DTE for active traders)
  - Monthly Options (30-45 DTE for wheel strategy)
  - Tech Stocks Under $50 (sector-specific)
  - All Stocks Under $50 (capital-efficient plays)
- **Advanced Filter System**
  - Max stock price filter (default: $50)
  - Minimum premium percentage threshold (default: 1.0%)
  - Target days to expiration selection (7, 14, 21, 30, 45 days)
  - Delta range filtering (built-in safety with 0.20-0.40 delta)
- **Comprehensive Results Display**
  - Symbol and current stock price
  - Recommended strike price (typically 5-10% OTM)
  - Days to expiration (DTE)
  - Premium per contract in dollars
  - Premium percentage (efficiency metric)
  - Monthly return (normalized 30-day return)
  - Annual return (extrapolated yearly potential)
  - Implied volatility (IV) percentage
  - Option volume for liquidity assessment
- **Summary Metrics Dashboard**
  - Average premium percentage across all results
  - Average monthly return expectation
  - Average annual return projection
  - Total opportunities found count
- **Top 5 Detailed Analysis**
  - Expandable cards for highest-ranked opportunities
  - Three-column layout with pricing, timing, and risk metrics
  - Quick-reference format for rapid decision-making
  - Visual hierarchy for easy scanning
- **Risk Assessment Integration**
  - Liquidity metrics (volume and open interest)
  - Implied volatility as risk indicator
  - Delta-based probability assessment
  - Assignment risk evaluation
- **Time Efficiency Features**
  - 30-60 second scan duration for market-wide analysis
  - Automatic sorting by monthly return
  - Pre-filtered results for tradability
  - One-click access to detailed opportunity data

### Technical Implementation
- **Market Data Sources**
  - Real-time stock prices via market data API
  - Options chain data from Robinhood API
  - Greeks calculations (Delta, IV)
  - Volume and open interest tracking
- **Scanning Algorithm**
  - Query current market data
  - Filter stocks by price range
  - Analyze complete options chains
  - Calculate return metrics
  - Rank opportunities by multiple factors
- **Performance Characteristics**
  - Scan speed: 30-60 seconds for full market scan
  - Handles hundreds of stocks efficiently
  - Real-time data during market hours
  - Cached results for fast filtering
- **User Experience**
  - Streamlit-based responsive interface
  - Strategy dropdown for quick selection
  - Real-time progress indication during scans
  - Color-coded results for easy interpretation
  - Sortable results table for custom prioritization

### Use Cases Supported
- **Conservative Approach**: 1-2% monthly returns, established companies
- **Balanced Approach**: 2-3% monthly returns, mix of growth and value
- **Aggressive Approach**: 3-5% monthly returns, high IV opportunities
- **Portfolio Construction**: Diversification across sectors and correlations
- **Weekly Income**: Short-term plays with higher frequency
- **Monthly Premium Collection**: Standard 30-45 DTE wheel strategy

### Data Quality
- Minimum volume requirement: 100 contracts
- Minimum open interest: typically 50+ contracts
- IV range: Focus on 30-60% sweet spot
- Delta targeting: -0.20 to -0.30 for optimal balance
- Bid-ask spread consideration: <10% of premium

### Integration Points
- Database scanner for broader market access
- TradingView watchlists for symbol sources
- Premium scanner for detailed analysis
- Trade history for performance tracking

[1.0.0]: https://github.com/yourusername/WheelStrategy/releases/tag/opportunities-v1.0.0
