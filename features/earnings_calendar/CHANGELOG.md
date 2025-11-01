# Changelog

All notable changes to the Earnings Calendar feature will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Real-time earnings alerts and notifications
- Historical earnings pattern analysis
- IV crush prediction models
- Integration with positions for automatic risk warnings
- Earnings whisper numbers from multiple sources
- Analyst consensus tracking
- Price movement correlation analysis
- Mobile push notifications for key earnings

## [1.0.0] - 2025-10-28

### Added
- **One-Click Database Initialization**
  - Automatic table creation with single button click
  - `earnings_events` table schema deployment
  - `earnings_history` table schema deployment
  - Index optimization automatically applied
  - Schema migration handling
  - Error recovery and graceful failure handling
  - No CLI commands required
- **Automated Earnings Synchronization**
  - Robinhood API integration for earnings data
  - Batch processing up to 100 stocks per sync
  - Real-time progress bar with status updates
  - Incremental updates for efficiency
  - Conflict resolution (duplicate handling)
  - Last 8 quarters of data per stock
  - EPS actual and estimate tracking
  - Revenue actual and estimate tracking
  - Report date and time capture
- **Advanced Filtering System**
  - **Date Range Filters**:
    - All Time view
    - This Week (current 7 days)
    - Next Week (upcoming 7 days)
    - This Month (current calendar month)
    - Next Month (upcoming calendar month)
  - **Time of Day Filters**:
    - All (BMO and AMC)
    - BMO (Before Market Open)
    - AMC (After Market Close)
  - **Result Filters**:
    - All events
    - Beat (EPS exceeded estimates)
    - Miss (EPS below estimates)
    - Meet (EPS matched estimates)
    - Pending (not yet reported)
- **Real-Time Metrics Dashboard**
  - Total earnings events count
  - Upcoming earnings today
  - Beat/miss/meet ratio display
  - Historical surprise percentages
  - Sector distribution statistics
- **Visual Indicators**
  - Color-coded results (green for beat, red for miss)
  - Percentage deltas with directional arrows
  - Time-based urgency indicators
  - Status badges for pending vs. reported
- **Data Export Capabilities**
  - One-click CSV download
  - Properly structured output with headers
  - Respects current filter settings
  - Preserves data types and formatting
- **Comprehensive Data Display**
  - Symbol and company name
  - Earnings date and time (BMO/AMC)
  - EPS estimate and actual
  - Revenue estimate and actual
  - Surprise percentage calculation
  - Pre/post earnings IV tracking
  - Pre/post earnings price tracking
  - Price move percentage
  - Volume ratio analysis
  - Options volume metrics
  - Whisper number (if available)
- **Database Schema**
  - `earnings_events` table with 18 fields
  - Unique constraint on symbol + earnings_date
  - Indexed queries on date and symbol
  - Automatic timestamp tracking (created_at, updated_at)
  - Support for IV crush analysis
  - Price movement correlation data
  - Volume spike detection fields
- **Integration Points**
  - TradingViewDBManager for connection pooling
  - Unified schema consistency across features
  - Transaction management coordination
  - Shared database infrastructure
- **Options Chain Analysis Integration**
  - Pre-earnings IV tracking for crush prediction
  - Post-earnings IV comparison
  - Strike selection awareness
  - Risk assessment for positions
- **Wheel Strategy Agent Integration**
  - Position timing recommendations
  - Avoid assignment during earnings
  - Premium optimization via IV expansion
  - Risk mitigation before announcements
- **Portfolio Dashboard Integration**
  - Event notifications for upcoming earnings
  - Performance attribution analysis
  - Earnings impact tracking
  - Risk metrics with earnings adjustment

### Technical Implementation
- **Database Tables**
  - `earnings_events`: Current and future events
  - `earnings_history`: Archived quarterly data
  - Indexes on symbol, date for performance
  - Composite indexes for common filters
- **Robinhood API Workflow**
  1. Authentication via login
  2. Stock selection from database
  3. Batch fetching (100 stocks)
  4. Last 8 quarters retrieval
  5. EPS and revenue extraction
  6. Upsert with conflict resolution
  7. Secure logout
- **Query Construction**
  - Dynamic SQL building based on filters
  - Date range parameterization
  - Time of day filtering
  - Result status filtering
  - JOIN with stocks table for enrichment
  - ORDER BY date DESC for relevance
- **Data Quality**
  - Type checking and validation
  - Range validation for percentages
  - Unique constraints prevent duplicates
  - NULL handling for missing data
  - Regular reconciliation with sources
- **Performance Optimizations**
  - Indexed columns for frequent queries
  - Prepared statements for repetitive operations
  - Connection pooling via manager
  - Session state caching for filters
  - Redis caching for frequently accessed data (planned)

### User Experience
- **No-Code Interface**
  - Zero CLI commands required
  - Button-driven initialization
  - Visual feedback for all operations
  - Clear error messages
  - Progressive disclosure design
- **Workflow Support**
  - Morning review of weekly earnings
  - Position planning around events
  - End-of-day analysis of results
  - Beat/miss trend identification
- **Security Features**
  - Environment variable credentials
  - No hardcoded passwords
  - Encrypted token storage
  - SSL/TLS connections
  - Input validation
  - SQL injection prevention via parameterized queries

### Configuration
- Database connection via `.env` file
- Robinhood credentials in environment
- Sync batch size: 100 stocks (configurable)
- Data retention: All historical quarters
- Refresh frequency: On-demand

### Use Cases
- **Risk Management**: Identify events impacting positions
- **Opportunity Discovery**: High-IV environments for premium selling
- **Historical Analysis**: Review past earnings performance
- **Portfolio Planning**: Schedule trades around earnings cycles
- **IV Crush Trading**: Capitalize on volatility expansion/contraction

[1.0.0]: https://github.com/yourusername/WheelStrategy/releases/tag/earnings-calendar-v1.0.0
