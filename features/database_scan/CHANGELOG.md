# Changelog

All notable changes to the Database Scan feature will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Advanced sector rotation analysis
- Historical options pricing trends
- Correlation matrix for stock selection
- Automated weekly opportunity reports
- Custom screening criteria builder
- Backtesting for historical premium data
- Integration with earnings calendar for filtering

## [1.0.0] - 2025-10-28

### Added
- **Complete Market Coverage**
  - Access to full universe of 1,205+ stocks
  - No watchlist limitations
  - Comprehensive market scanning capability
  - Discovery tool for new opportunities
- **Four-Tab Interface**
  - Database Overview tab with statistics
  - Add Stocks tab for bulk import
  - Scan Premiums tab (primary interface)
  - Analytics tab for insights
- **Database Overview Tab**
  - Total stock count display
  - Sector distribution visualization
  - Price range distribution charts
  - Quick price update button for all stocks
  - Market-wide statistics
- **Add Stocks Functionality**
  - Manual stock addition interface
  - Bulk import capability
  - Yahoo Finance data integration
  - Automatic sector classification
  - Market cap retrieval
  - Stock validation before insertion
- **Premium Scanning System**
  - All stocks with options display
  - Focus on 30-day expirations (±2 days)
  - Delta range filtering (0.25-0.40)
  - Real-time filtering controls
  - Sortable columns for all metrics
  - Color-coded data formatting
- **Comprehensive Data Display**
  - Symbol and company name
  - Current stock price
  - Strike price recommendation
  - Days to expiration (DTE)
  - Premium amount in dollars
  - Delta value (risk metric)
  - Monthly return percentage
  - Implied volatility (IV)
  - Bid and ask prices
  - Daily trading volume
  - Open interest
  - Sector classification
- **Advanced Filtering**
  - Price range filters (min/max)
  - Minimum premium threshold
  - DTE selection flexibility
  - Delta range hardcoded for safety
  - Real-time filter application
- **Summary Metrics**
  - Total options found count
  - Average premium percentage
  - Average monthly return
  - Distribution statistics
- **Data Synchronization**
  - One-click sync for all database stocks
  - Background processing for 1,000+ symbols
  - Automatic options chain updates
  - Progress tracking with status display
  - 10-15 minute sync time for full database
- **Analytics Dashboard**
  - Database-wide statistics
  - Sector performance analysis
  - Price distribution charts
  - Market overview metrics
  - Visual data representations
- **Database Schema Integration**
  - `stocks` table: Master list (1,205 stocks)
  - `stock_premiums` table: Options chain with Greeks
  - `stock_data` table: Real-time price data
  - `tv_watchlists` table: Watchlist system integration
- **Performance Optimizations**
  - Indexed SQL queries
  - DISTINCT ON for one option per symbol
  - LEFT JOINs for graceful missing data handling
  - Client-side sorting for instant feedback
  - Query optimization for large datasets

### Technical Implementation
- **SQL Query Structure**
  - Complex multi-table joins
  - Optimized filtering logic
  - One best option per symbol
  - Ordered by monthly return DESC
  - Handles missing data gracefully
- **Key Design Decisions**
  - Delta range: 0.25-0.40 (balanced risk/reward)
  - Default DTE: 30 days (optimal theta decay)
  - DISTINCT ON: Reduces noise
  - LEFT JOINs: Graceful null handling
  - Client-side sorting: Better UX
- **Services Integration**
  - `DatabaseScanner`: Core scanning engine
  - `TradingViewDBManager`: Database interface
  - `watchlist_sync_service`: Background sync processor
- **Data Flow**
  - PostgreSQL `stocks` table (source)
  - `stock_premiums` table (synced options)
  - `stock_data` table (enrichment)
  - Formatted, sortable UI presentation
- **Performance Characteristics**
  - Initial load: <2 seconds for 500 stocks
  - Filtering: Real-time (no lag)
  - Sorting: Client-side JavaScript (instant)
  - Full sync: 10-15 minutes for 1,205 stocks
  - Query performance: <100ms for filtered results

### Comparison with TradingView Watchlists
- **Scope**: All 1,205 stocks vs. selected watchlist (~150)
- **Purpose**: Market discovery vs. tracking known stocks
- **Filtering**: No symbol filter vs. watchlist-specific
- **Sync**: All stocks vs. watchlist only
- **Use Case**: Find new opportunities vs. monitor favorites

### Use Cases
- **Broad Market Discovery**: Find opportunities across all sectors
- **Sector-Specific Analysis**: Filter by specific industries
- **High-Yield Hunting**: Sort by monthly return for best premiums
- **Liquidity Screening**: Filter by volume and open interest
- **Cross-Sector Comparison**: Analyze premium efficiency by sector
- **New Stock Discovery**: Find stocks not in existing watchlists

### Data Quality
- 1,205+ stocks tracked
- 400-500 stocks with available options
- ~5,000+ option contracts analyzed
- Real-time pricing during market hours
- Automated data validation
- Deduplication via unique constraints

### Configuration
- Default DTE: 30 days (28-32 range)
- Default delta: 0.25-0.40
- Minimum premium: Configurable
- Price range: Configurable min/max
- Sync frequency: On-demand

[1.0.0]: https://github.com/yourusername/WheelStrategy/releases/tag/database-scan-v1.0.0
