# Changelog

All notable changes to the Dashboard feature will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- WebSocket integration for real-time position updates
- Multi-account portfolio aggregation
- Advanced charting with historical P/L trends
- Mobile-responsive design improvements
- Export trade history to CSV/Excel

## [1.0.0] - 2025-10-28

### Added
- **Portfolio Status Overview** with real-time metrics
  - Account balance and buying power display
  - Total premium collected tracking
  - Capital at risk calculations
  - Active position counter
- **Trade History Management System**
  - Complete trade lifecycle tracking (open, close, assignment)
  - Automatic P&L calculations with annualized returns
  - Cumulative profit/loss visualization
  - Manual trade entry interface
  - Trade closing workflow with reason tracking
- **Balance Forecast Timeline**
  - Expiration date projections
  - Best/expected/worst case scenario modeling
  - Monthly return calculations
  - Capital deployment analysis
- **Individual Position Forecasts**
  - Position-specific P&L tracking
  - Real-time theta decay calculations
  - Assignment probability estimates
  - Breakeven price analysis
- **Theta Decay Profit Forecast**
  - Daily profit projections with square root of time model
  - Accelerating theta visualization charts
  - Milestone profit targets (3-day, 7-day)
  - Average daily theta calculations
- **AI Trade Analysis Engine**
  - Smart exit recommendations with multi-factor scoring
  - Profit-taking alerts (20%, 50%, 75% thresholds)
  - Risk assessment (HIGH/MEDIUM/LOW)
  - Portfolio-wide action suggestions
  - Individual position analysis with urgency levels
- **Database Integration**
  - PostgreSQL trade_history table with full schema
  - Indexed queries for performance
  - Automatic timestamp tracking
  - Trade statistics aggregation
- **Robinhood Integration**
  - Real-time position data synchronization
  - Account summary retrieval
  - Options position identification
  - Cash-secured put (CSP) and covered call (CC) detection
- **UI Components**
  - Streamlit-based responsive interface
  - Interactive expandable sections
  - Color-coded profit/loss indicators
  - Real-time metric cards
  - Trade entry/closing forms with validation

### Technical Details
- Core file: `c:/Code/WheelStrategy/dashboard.py` (lines 92-1100+)
- Trade history manager: `c:/Code/WheelStrategy/src/trade_history_manager.py`
- AI analyzer: `c:/Code/WheelStrategy/src/ai_trade_analyzer.py`
- Robinhood client: `c:/Code/WheelStrategy/src/robinhood_fixed.py`
- Database schema with 4 indexes for optimal performance
- Session-based authentication with encrypted token storage
- Black-Scholes inspired theta decay modeling
- Multi-scenario forecasting algorithm (3 scenarios per expiration)

[1.0.0]: https://github.com/yourusername/WheelStrategy/releases/tag/dashboard-v1.0.0
