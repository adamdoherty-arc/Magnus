# Changelog

All notable changes to the Positions feature will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- **Chart Link Display Bug - FINAL FIX** (2025-11-01)
  - Fixed TradingView chart links appearing as plain URLs instead of clickable icons
  - Now displays as clickable chart emoji (📈) using Streamlit's LinkColumn display_text parameter
  - Updated positions_page_improved.py line 246: Added `display_text="📈"` to LinkColumn config
  - First attempt with markdown format didn't work with styled dataframes
  - Final solution: Plain URL in data + LinkColumn with display_text parameter
  - Fixes regression where link column showed full URL text

### Planned
- AI Research Assistant feature (Sprint 2) - Comprehensive stock analysis with LangChain + CrewAI
- Enhanced research links (News, Options Chain, Strategy Analyzer, Alerts) (Sprint 3)
- WebSocket real-time price updates (Sprint 4) - eliminate polling and scroll jump
- Full Greeks display (Delta, Gamma, Vega, Theta, Rho) (Sprint 3-4)
- Position grouping by strategy/expiration/underlying
- Historical P/L charting over time
- Export positions to CSV/Excel
- Multi-account support for multiple Robinhood accounts
- Custom alert thresholds and notification channels

## [1.2.0] - 2025-10-31

### Added
- **After-Hours Pricing Support**
  - Extended hours price data display
  - Clear indicators when showing after-hours prices
  - Separate market hours vs. extended hours handling

### Fixed
- **TradingView Chart Links** corrected for all symbols
  - Fixed URL construction for proper chart loading
  - Ensured all links open in new tabs correctly

## [1.1.0] - 2025-10-30

### Added
- **Stock Price Column** in active positions table
  - Real-time underlying stock price display
  - Helps assess ITM/OTM status at a glance
  - Color-coded based on position profitability

### Changed
- **P/L Color Coding** from cell backgrounds to text colors
  - Improved readability and visual hierarchy
  - Green text for profits, red text for losses
  - More subtle and professional appearance

### Fixed
- **CRITICAL: Robinhood Session Scope**
  - Fixed session variable scope issue causing connection failures
  - Moved `rh_session` to page-level scope for proper persistence
  - Eliminated random disconnection issues
- **CRITICAL: P/L Calculations**
  - Corrected P/L using `processed_premium_direction` field
  - Fixed datetime parsing errors in trade history
  - Accurate profit/loss calculations for all position types
- **Trade History Display**
  - Moved Robinhood login to page level for better reliability
  - Removed debug logging that cluttered output
  - Fixed scope issues causing missing data
- **Color Logic** for position table rows and cells
  - Consistent color application across all metrics
  - Fixed conditional formatting bugs

## [1.0.0] - 2025-10-30

### Added
- **Real-Time Position Tracking**
  - Live synchronization with Robinhood API
  - Automatic position type detection (CSP, CC, Long)
  - Contract quantity and strike price display
  - Days to expiration (DTE) countdown
- **Comprehensive P/L Calculations**
  - Real-time profit/loss in dollars and percentages
  - Cost to close calculations
  - Premium collected tracking
  - Unrealized gain/loss metrics
- **Auto-Refresh Capability**
  - Configurable refresh intervals (30s, 1m, 2m, 5m)
  - Enable/disable toggle for user control
  - Manual refresh button for on-demand updates
  - Last refresh timestamp display
- **Color-Coded Status Indicators**
  - Green for profitable positions (positive P/L)
  - Red for losing positions (negative P/L)
  - Bold highlighting for high-profit opportunities (>20%)
  - Visual alerts with balloons animation for profit milestones
- **Theta Decay Forecasting**
  - Daily profit projections using square root of time model
  - Expandable forecasts per position
  - Milestone tracking (3-day, 7-day profit estimates)
  - Average daily theta calculations
  - Acceleration visualization as expiration approaches
- **AI-Powered Trade Analysis**
  - Individual position recommendations
  - Portfolio-level insights and suggestions
  - Risk level assessment (LOW, MEDIUM, HIGH)
  - Action urgency classification
  - Multi-factor scoring for exit timing
- **Performance Analytics Dashboard**
  - Active position count
  - Total premium collected
  - Aggregate P/L across all positions
  - Account value tracking
  - CSP vs. CC position breakdown
- **TradingView Integration**
  - Direct chart links for each underlying symbol
  - One-click access to technical analysis
  - Opens in new tab for parallel analysis
- **Position Details Table**
  - Symbol, strategy type, strike price
  - Expiration date and DTE
  - Option price per share
  - Current position value
  - P/L absolute and percentage
  - Chart access link
- **Trade History Integration**
  - Closed positions from Robinhood
  - Complete trade lifecycle tracking
  - Historical performance metrics
  - Win rate and average returns

### Technical Details
- Multi-layer data fetching architecture
- Robinhood API integration with session caching
- Yahoo Finance for supplementary stock prices
- Session state management for data persistence
- Optimized query patterns for performance
- Client-side auto-refresh with meta tags
- Streamlit caching for resource initialization
- Parallel API calls for faster data retrieval
- Error handling with graceful degradation

### Performance
- Initial load: ~1.5 seconds
- Refresh time: ~0.8 seconds
- Theta calculation: <50ms per position
- AI analysis: ~300ms per position
- UI render: <150ms

[1.2.0]: https://github.com/yourusername/WheelStrategy/compare/positions-v1.1.0...positions-v1.2.0
[1.1.0]: https://github.com/yourusername/WheelStrategy/compare/positions-v1.0.0...positions-v1.1.0
[1.0.0]: https://github.com/yourusername/WheelStrategy/releases/tag/positions-v1.0.0
