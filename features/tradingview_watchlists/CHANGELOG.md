# Changelog

All notable changes to the TradingView Watchlists feature will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Real-time watchlist synchronization via WebSocket
- Custom watchlist grouping and tagging
- Automated premium alerts for watchlist symbols
- Historical performance tracking per watchlist
- Advanced filtering by sector/market cap
- Watchlist sharing and collaboration features
- Mobile app watchlist management

## [1.1.0] - 2025-10-28

### Added
- **Complete Feature Cleanup and Optimization**
  - Code refactoring for improved performance
  - Enhanced error handling and user feedback
  - Streamlined UI components
  - Optimized database queries

### Fixed
- **Trade History Display Issues**
  - Robinhood closed positions now properly displayed
  - Historical trade data synchronized correctly
  - P/L calculations verified against actual trades
  - Trade lifecycle tracking improved

## [1.0.0] - 2025-10-28

### Added
- **Live Position Monitoring System**
  - Real-time Robinhood position synchronization
  - Automatic position detection (CSP, CC, Long Call/Put)
  - Contract quantity and strike price display
  - Days to expiration (DTE) calculation
  - Premium collected tracking
  - Current market value display
  - Profit/loss calculations (absolute and percentage)
- **Trade History Management**
  - Comprehensive closed trade logging
  - Manual trade entry forms for each position
  - Close price recording with multiple close reasons
  - Automatic P/L calculation on closure
  - Days held computation
  - Annualized return calculations
  - Trade statistics dashboard
  - Win rate tracking
  - Average days held metrics
- **Watchlist Synchronization**
  - Auto-sync with TradingView watchlists
  - Database storage for persistent watchlists
  - Import watchlist tab for manual entry
  - Multiple watchlist support
  - Symbol filtering (stocks only, no crypto)
  - Watchlist selector dropdown
  - Symbol count per watchlist
  - Last sync timestamp display
- **Premium Analysis Engine**
  - 30-day options focus (28-32 DTE range)
  - Delta targeting (0.25-0.40 range)
  - Strike selection (~5% OTM for puts)
  - Comprehensive premium table display
  - Real-time market data via yfinance
  - Greeks calculation (Delta, IV)
  - Monthly return percentage
  - Bid/ask spread display
  - Volume and open interest metrics
- **Theta Decay Visualization**
  - Daily profit forecast charts
  - Square root of time decay model
  - Accelerating theta visualization
  - Milestone predictions (3-day, 7-day)
  - Expected profit calculations
  - Recommendations based on profit captured
  - Maximum theta decay period highlighting
- **Database Integration**
  - PostgreSQL schema for 3 main tables
  - `stock_data`: Current prices and market metrics
  - `stock_premiums`: Options chain with Greeks
  - `trade_history`: Complete trade lifecycle
  - Indexed columns for performance
  - Prepared statements for queries
  - Connection pooling via TradingViewDBManager
- **Advanced Filtering System**
  - Price range filters (min/max stock price)
  - Premium threshold filtering
  - DTE selection (10, 17, 24, 31, 38, 52 days)
  - ±2 day range for flexibility
  - Automatic ±2 day adjustment
- **Background Sync Service**
  - Non-blocking price updates
  - Progress tracking with status display
  - Batch processing of symbols
  - Error recovery mechanisms
  - Automatic retry logic
- **Key Metrics Dashboard**
  - Active positions count
  - Total premium collected
  - Total P/L across positions
  - CSP position count
  - Stocks up/down today
  - Best/average returns
  - Options availability stats
- **Export Capabilities**
  - CSV download for trade history
  - Filtered data export
  - Symbol-based filtering
  - Trade limit selection (20, 50, 100, 200)
- **Watchlist Management Interface**
  - Saved watchlists tab
  - Load/analyze/delete actions
  - Named watchlist creation
  - Direct paste from TradingView
  - Comma or line-separated input
  - Automatic stock validation

### Technical Implementation
- **API Integrations**
  - Robinhood API for live positions
  - TradingView for watchlist management
  - Yahoo Finance for market data
  - PostgreSQL for persistence
- **Data Flow**
  - Real-time position fetching
  - Background price synchronization
  - Options chain analysis
  - Premium calculations
  - Database updates
- **Performance Optimizations**
  - Lazy loading for position details
  - Expandable sections for reduced render
  - Selective reruns for targeted updates
  - Database connection pooling
  - Indexed queries
- **UI Components**
  - Streamlit-based responsive interface
  - Tab-based navigation (4 tabs)
  - Auto-sync with progress tracking
  - Import/export interfaces
  - Interactive data tables
  - Color-coded metrics
- **Security**
  - Environment variables for credentials
  - Secure token storage
  - Session-based authentication
  - Input validation and sanitization

### Supported Workflows
- **Daily Position Review**: Check P/L status and assignment risk
- **Finding New Opportunities**: Import/load watchlists, sync, analyze
- **Weekly Planning**: Review theta decay, scan database, update watchlists
- **Trade Logging**: Immediate recording of closed trades

### Configuration
- Default DTE range: 28-32 days
- Default delta range: 0.25-0.40
- Minimum option volume: 100
- Strike selection: ~5% OTM
- Risk-free rate: 4.5% for Greeks

[1.1.0]: https://github.com/yourusername/WheelStrategy/compare/tradingview-v1.0.0...tradingview-v1.1.0
[1.0.0]: https://github.com/yourusername/WheelStrategy/releases/tag/tradingview-v1.0.0
