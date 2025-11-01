# Changelog

All notable changes to the Premium Scanner feature will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Real-time Greeks updates via WebSocket
- Advanced filtering UI with saved filter presets
- Machine learning-based opportunity predictions
- Portfolio optimization suggestions
- Mobile app integration
- Historical premium tracking charts
- Automated trade execution workflow
- Custom delta range selection per scan

## [2.0.0] - 2025-10-28

### Added
- **Multi-Expiration Scanning System**
  - Simultaneous analysis of 6 expiration periods: 7, 14, 21, 30, 45, 60 DTE
  - Automatic selection of closest available expiration
  - Comprehensive time-based opportunity comparison
  - Optimal DTE targeting for different strategies
- **Delta-Based Filtering Algorithm**
  - Intelligent delta range targeting (0.20-0.40)
  - Probability-based position selection
  - Risk-reward optimization through delta screening
  - Automatic ITM/OTM classification
- **Advanced Options Chain Analysis**
  - Complete options chain retrieval for all symbols
  - Black-Scholes delta calculation
  - Greeks computation (Delta, Theta, Vega, Gamma)
  - Implied volatility extraction
  - Bid/ask spread analysis
- **Premium Optimization Engine**
  - Multi-metric ranking system
  - Premium percentage calculations
  - Monthly return normalization (30-day standard)
  - Annual return extrapolation
  - Return on capital efficiency metrics
- **Liquidity Validation System**
  - Minimum volume threshold: 100 contracts
  - Minimum open interest requirement: 50 contracts
  - Bid-ask spread quality assessment
  - Market depth consideration
  - Tradability scoring
- **Quick Scan Strategies**
  - Best Overall Premiums (all-market scan)
  - High IV Plays (>40% implied volatility)
  - Weekly Options (7-14 DTE short-term)
  - Monthly Options (30-45 DTE traditional)
  - Tech Stocks Under $50 (sector-focused)
  - All Stocks Under $50 (capital-efficient)
- **Comprehensive Results Display**
  - Symbol, stock price, strike price
  - Days to expiration (DTE)
  - Premium amount per contract
  - Premium percentage (efficiency)
  - Monthly return percentage
  - Annual return percentage
  - Implied volatility (IV)
  - Delta value
  - Bid and ask prices
  - Volume and open interest
- **Summary Metrics Dashboard**
  - Average premium percentage
  - Average monthly return
  - Average annual return
  - Total opportunities count
  - Distribution by DTE
- **Database Integration**
  - PostgreSQL `stock_premiums` table
  - Optimized schema with unique constraints
  - Indexed queries for performance
  - Historical data tracking
  - Automatic timestamp management
- **Background Synchronization**
  - Non-blocking price updates
  - Batch processing for large symbol lists
  - Parallel data fetching
  - Error recovery and retry logic
  - Progress tracking

### Technical Architecture
- **Core Components**
  - `PremiumScanner` class: Main scanning engine
  - `EnhancedOptionsFetcher` class: Options data retrieval
  - `WatchlistSyncService`: Background synchronization
  - `DatabaseScanner`: PostgreSQL operations
- **Data Pipeline**
  - TradingView Watchlists → Symbol Collection
  - Symbol Collection → Price Fetching (Polygon/Yahoo Finance)
  - Price Fetching → Options Chain Analysis
  - Options Chain → Greek Calculation
  - Greek Calculation → Database Storage
- **Performance Metrics**
  - Single symbol scan: 2-3 seconds (all expirations)
  - 10 symbols: 20-30 seconds
  - 100 symbols: 3-5 minutes (with caching)
  - Full database: 15-20 minutes (background sync)
- **Data Sources**
  - Stock prices: Polygon API (primary), Yahoo Finance (fallback)
  - Options chains: Robinhood API (free, unlimited)
  - Greeks: Black-Scholes model calculation
  - IV data: Extracted from options chains
- **Caching Strategy**
  - Stock prices: Real-time during market hours
  - Options data: 15-minute delayed (Robinhood free tier)
  - Greeks: Calculated on-demand
  - Database cache: 15-minute TTL

### Filter Controls
- **Max Stock Price**: Capital requirement limiter
- **Min Premium %**: Return threshold filter
- **Target DTE**: Specific expiration targeting
- **Delta Range**: Automatic 0.20-0.40 safety filter

### Database Schema
```sql
CREATE TABLE stock_premiums (
    symbol VARCHAR(10),
    expiration_date DATE,
    strike_price DECIMAL(10,2),
    dte INTEGER,
    premium DECIMAL(10,2),
    delta DECIMAL(5,4),
    monthly_return DECIMAL(10,2),
    implied_volatility DECIMAL(5,2),
    bid DECIMAL(10,2),
    ask DECIMAL(10,2),
    volume INTEGER,
    open_interest INTEGER,
    updated_at TIMESTAMP,
    UNIQUE(symbol, expiration_date, strike_price)
);
```

### Configuration
- Tunable parameters in `premium_scanner.py`
- Environment variables for API keys
- Database connection settings
- Risk-free rate for Greeks (default: 4.5%)

### Use Cases
- **Weekly Income Generation**: 7-14 DTE with higher delta
- **Monthly Premium Collection**: 30-45 DTE balanced delta
- **High IV Harvesting**: >40% IV event-driven plays
- **Assignment Preparation**: 0.40-0.50 delta for ownership

### Integration Points
- TradingView watchlists for symbol sources
- Database scanner for historical analysis
- Opportunities feature for comparison
- Positions feature for portfolio tracking

[2.0.0]: https://github.com/yourusername/WheelStrategy/releases/tag/premium-scanner-v2.0.0
