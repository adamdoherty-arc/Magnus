# Earnings Calendar Feature

## Executive Summary

The Earnings Calendar is a comprehensive, user-friendly feature within the Magnus Trading Platform that provides traders with real-time earnings event tracking, historical earnings analysis, and automated synchronization with Robinhood's earnings data. Designed with a **no-CLI-commands philosophy**, the entire feature is accessible through an intuitive button-driven UI, making it accessible to traders of all technical skill levels.

## Table of Contents

1. [Overview](#overview)
2. [Key Features](#key-features)
3. [User Interface](#user-interface)
4. [Getting Started](#getting-started)
5. [Core Functionality](#core-functionality)
6. [Data Sources](#data-sources)
7. [Database Schema](#database-schema)
8. [Integration Points](#integration-points)
9. [Performance Considerations](#performance-considerations)
10. [Troubleshooting](#troubleshooting)
11. [Best Practices](#best-practices)
12. [Security Considerations](#security-considerations)

## Overview

The Earnings Calendar feature provides a centralized hub for monitoring and analyzing corporate earnings events. It addresses the critical need for options traders to track earnings announcements, which often cause significant volatility and present both opportunities and risks for wheel strategy implementations.

### Purpose

- **Risk Management**: Identify upcoming earnings events that may impact existing positions
- **Opportunity Discovery**: Find high-IV environments for premium selling strategies
- **Historical Analysis**: Review past earnings performance and price movements
- **Portfolio Planning**: Schedule trades around earnings cycles

### Design Philosophy

The feature embodies three core principles:

1. **Zero Configuration Start**: Users can initialize and use the feature without any command-line interaction
2. **Progressive Disclosure**: Basic functionality is immediately accessible, with advanced features available on demand
3. **Visual First**: All data is presented in easily digestible visual formats with actionable insights

## Key Features

### 1. One-Click Database Initialization

- **Automatic Table Creation**: Single button creates all required database tables
- **Schema Migration**: Handles updates and modifications transparently
- **Index Optimization**: Creates performance indexes automatically
- **Error Recovery**: Graceful handling of initialization failures

### 2. Automated Earnings Synchronization

- **Robinhood Integration**: Direct API connection for earnings data
- **Batch Processing**: Efficiently syncs up to 100 stocks at once
- **Progress Tracking**: Real-time progress bar with status updates
- **Incremental Updates**: Only syncs changed data to minimize API calls
- **Conflict Resolution**: Handles duplicate entries automatically

### 3. Advanced Filtering System

- **Date Range Filters**:
  - All Time
  - This Week
  - Next Week
  - This Month
  - Next Month

- **Time Filters**:
  - All
  - BMO (Before Market Open)
  - AMC (After Market Close)

- **Result Filters**:
  - All
  - Beat (EPS exceeded estimates)
  - Miss (EPS below estimates)
  - Meet (EPS matched estimates)
  - Pending (Not yet reported)

### 4. Real-Time Metrics Dashboard

- **Summary Statistics**:
  - Total earnings events count
  - Upcoming earnings today
  - Beat/Miss/Meet ratios
  - Historical surprise percentages

- **Visual Indicators**:
  - Color-coded results (green for beat, red for miss)
  - Percentage deltas with directional arrows
  - Sector distribution charts

### 5. Data Export Capabilities

- **CSV Download**: One-click export of filtered data
- **Formatted Output**: Properly structured with headers and data types
- **Filter Preservation**: Exported data respects current filter settings

## User Interface

### Layout Structure

```
┌─────────────────────────────────────────────────┐
│             📅 Earnings Calendar                │
├─────────────────────────────────────────────────┤
│  ┌─────────┐  ┌──────────┐  ┌──────────────┐   │
│  │ Metrics │  │ Sync Btn │  │ Auto-sync    │   │
│  │  Count  │  │          │  │   Notice     │   │
│  └─────────┘  └──────────┘  └──────────────┘   │
├─────────────────────────────────────────────────┤
│              Filter Controls                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────────┐   │
│  │Date Range│ │   Time   │ │    Result    │   │
│  └──────────┘ └──────────┘ └──────────────┘   │
├─────────────────────────────────────────────────┤
│              Summary Metrics                     │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐              │
│  │Total│ │Beats│ │Miss │ │Pend │              │
│  └─────┘ └─────┘ └─────┘ └─────┘              │
├─────────────────────────────────────────────────┤
│           Earnings Data Table                    │
│  Symbol | Date | Time | EPS Est | EPS Act |...  │
│  ─────────────────────────────────────────────  │
│   AAPL  | ...  | AMC  |  1.23   |  1.45   |...  │
│   MSFT  | ...  | BMO  |  2.34   |  2.35   |...  │
└─────────────────────────────────────────────────┘
```

### Component Details

#### Initialization Interface

When tables are not yet created, users see:
- Warning message with clear instructions
- Primary action button for database initialization
- Progress spinner during creation
- Success confirmation with automatic page refresh

#### Main Dashboard

Post-initialization interface includes:
- **Metrics Bar**: Live count of earnings events
- **Action Buttons**: Sync earnings with visual feedback
- **Filter Controls**: Dropdown selectors with instant updates
- **Data Grid**: Scrollable, sortable table with formatting

## Getting Started

### Prerequisites

1. **Environment Variables** (`.env` file):
   ```env
   # Database Configuration
   DB_HOST=localhost
   DB_PORT=5432
   DB_USER=postgres
   DB_PASSWORD=postgres123!
   DB_NAME=magnus

   # Robinhood Credentials
   ROBINHOOD_USERNAME=your_username
   ROBINHOOD_PASSWORD=your_password
   ```

2. **Python Dependencies**:
   ```python
   streamlit
   pandas
   psycopg2
   robin-stocks
   python-dotenv
   ```

### First-Time Setup

1. **Navigate to Earnings Calendar**:
   - Open Magnus Trading Platform
   - Click "📅 Earnings Calendar" in sidebar

2. **Initialize Database**:
   - Click "🔧 Initialize Database" button
   - Wait for success confirmation

3. **Sync Initial Data**:
   - Click "🔄 Sync Earnings" button
   - Monitor progress bar
   - Review synced data

### Daily Usage Workflow

1. **Morning Review**:
   - Check "This Week" filter for upcoming earnings
   - Review beat/miss ratios for sector trends

2. **Position Planning**:
   - Filter by specific sectors or time periods
   - Export data for offline analysis

3. **End-of-Day Analysis**:
   - Review "Today's Events" for market impact
   - Update watchlists based on earnings results

## Core Functionality

### Database Initialization

The initialization process creates two primary tables:

#### `earnings_events` Table
- Stores current and future earnings events
- Tracks estimates vs. actuals
- Records price movements and IV changes
- Maintains unique constraints on symbol-date pairs

#### `earnings_history` Table
- Archives historical earnings data
- Preserves quarterly/annual patterns
- Links to earnings call replays
- Enables trend analysis

### Data Synchronization

#### Robinhood API Integration

The sync process follows this workflow:

1. **Authentication**:
   ```python
   rh.login(username, password)
   ```

2. **Stock Selection**:
   - Queries `stocks` table for active symbols
   - Limits to 100 stocks per sync batch

3. **Data Fetching**:
   - Retrieves last 8 quarters of earnings
   - Extracts EPS actual/estimate
   - Captures report dates and times

4. **Upsert Logic**:
   - INSERT with ON CONFLICT UPDATE
   - Preserves existing data integrity
   - Updates timestamps for tracking

5. **Cleanup**:
   ```python
   rh.logout()
   ```

### Filtering and Display

#### Query Construction

Dynamic SQL building based on filters:

```sql
SELECT e.*, s.name, s.sector
FROM earnings_events e
LEFT JOIN stocks s ON e.symbol = s.ticker
WHERE 1=1
  AND e.earnings_date >= [filter_date]
  AND e.earnings_time = [filter_time]
ORDER BY e.earnings_date DESC
```

#### Result Processing

1. **Data Enrichment**:
   - Joins with stocks table for company details
   - Calculates surprise percentages
   - Determines beat/miss/meet status

2. **Formatting**:
   - Date formatting for readability
   - Number formatting with appropriate precision
   - Color coding for visual distinction

## Data Sources

### Primary Sources

1. **Robinhood API**:
   - Real-time earnings dates
   - Historical EPS data
   - Revenue estimates and actuals
   - Earnings call information

2. **Internal Database**:
   - Stock master data
   - Sector/industry classifications
   - Market cap and price data
   - Options chain information

### Data Quality

- **Validation**: Type checking and range validation
- **Deduplication**: Unique constraints prevent duplicates
- **Completeness**: NULL handling for missing data
- **Accuracy**: Regular reconciliation with sources

## Database Schema

### earnings_events Table

```sql
CREATE TABLE earnings_events (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    earnings_date TIMESTAMP WITH TIME ZONE,
    earnings_time VARCHAR(10),
    eps_estimate DECIMAL(10, 2),
    eps_actual DECIMAL(10, 2),
    revenue_estimate DECIMAL(15, 2),
    revenue_actual DECIMAL(15, 2),
    surprise_percent DECIMAL(10, 2),
    pre_earnings_iv DECIMAL(10, 4),
    post_earnings_iv DECIMAL(10, 4),
    pre_earnings_price DECIMAL(10, 2),
    post_earnings_price DECIMAL(10, 2),
    price_move_percent DECIMAL(10, 2),
    volume_ratio DECIMAL(10, 2),
    options_volume INTEGER,
    whisper_number DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(symbol, earnings_date)
);
```

### earnings_history Table

```sql
CREATE TABLE earnings_history (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    report_date DATE NOT NULL,
    quarter INTEGER,
    year INTEGER,
    eps_actual NUMERIC(10, 4),
    eps_estimate NUMERIC(10, 4),
    call_datetime TIMESTAMP WITH TIME ZONE,
    call_replay_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(symbol, report_date)
);
```

### Indexes

```sql
CREATE INDEX idx_earnings_date ON earnings_events(earnings_date DESC);
CREATE INDEX idx_earnings_events_symbol ON earnings_events(symbol);
CREATE INDEX idx_earnings_history_symbol ON earnings_history(symbol);
```

## Integration Points

### 1. TradingView Database Manager

- **Connection Pooling**: Shared database connections
- **Transaction Management**: Coordinated commits/rollbacks
- **Schema Consistency**: Unified table structures

### 2. Options Chain Analysis

- **IV Tracking**: Pre/post earnings IV crush
- **Strike Selection**: Earnings-aware option pricing
- **Risk Assessment**: Volatility spike predictions

### 3. Wheel Strategy Agent

- **Position Timing**: Avoid assignment during earnings
- **Premium Optimization**: Capitalize on IV expansion
- **Risk Mitigation**: Reduce exposure before announcements

### 4. Portfolio Dashboard

- **Event Notifications**: Upcoming earnings alerts
- **Performance Attribution**: Earnings impact analysis
- **Risk Metrics**: Earnings-adjusted portfolio beta

## Performance Considerations

### Query Optimization

1. **Index Usage**:
   - Primary indexes on symbol and date
   - Composite indexes for common filter combinations
   - Partial indexes for active records

2. **Query Patterns**:
   - Limit clauses to prevent large result sets
   - Prepared statements for repeated queries
   - Connection pooling for concurrent access

3. **Caching Strategy**:
   - Session state for filter preferences
   - Redis caching for frequently accessed data
   - Incremental refresh for real-time updates

### Scalability

- **Batch Processing**: 100-stock sync batches
- **Async Operations**: Non-blocking UI updates
- **Pagination**: Large dataset handling
- **Data Archival**: Historical data compression

## Troubleshooting

### Common Issues and Solutions

#### 1. Database Initialization Fails

**Symptoms**: Error message during table creation

**Solutions**:
- Verify database credentials in `.env`
- Check PostgreSQL service is running
- Ensure user has CREATE TABLE permissions
- Review error logs for specific constraints

#### 2. Sync Earnings Hangs

**Symptoms**: Progress bar stuck, no updates

**Solutions**:
- Check Robinhood credentials validity
- Verify network connectivity
- Reduce batch size if timeout occurs
- Check for rate limiting from API

#### 3. Missing Data

**Symptoms**: Empty table despite successful sync

**Solutions**:
- Verify stocks table has valid symbols
- Check date ranges in filters
- Confirm Robinhood API returns data
- Review database constraints for conflicts

#### 4. Incorrect Calculations

**Symptoms**: Wrong beat/miss classifications

**Solutions**:
- Verify EPS data integrity
- Check for NULL values in calculations
- Review timezone handling for dates
- Validate data type conversions

## Best Practices

### For Users

1. **Regular Synchronization**:
   - Sync weekly for upcoming events
   - Daily sync during earnings season
   - Post-market sync for actuals

2. **Filter Usage**:
   - Start broad, then narrow
   - Save common filter combinations
   - Export filtered views for reports

3. **Data Interpretation**:
   - Consider sector context
   - Review historical patterns
   - Correlate with options data

### For Developers

1. **Code Maintenance**:
   - Keep sync logic modular
   - Handle API changes gracefully
   - Log all sync operations
   - Version database migrations

2. **Error Handling**:
   - Wrap all database operations
   - Provide user-friendly messages
   - Log technical details
   - Implement retry logic

3. **Testing**:
   - Unit test calculation functions
   - Integration test API calls
   - Load test with large datasets
   - Validate edge cases

## Security Considerations

### Credential Management

1. **Environment Variables**:
   - Never commit `.env` files
   - Rotate credentials regularly
   - Use separate dev/prod credentials
   - Implement credential encryption

2. **API Security**:
   - Rate limit API calls
   - Validate all inputs
   - Sanitize SQL queries
   - Log authentication attempts

3. **Data Privacy**:
   - Anonymize sensitive data
   - Implement access controls
   - Audit data access
   - Comply with regulations

### Database Security

1. **Access Control**:
   - Principle of least privilege
   - Role-based permissions
   - Network isolation
   - SSL/TLS connections

2. **Data Protection**:
   - Regular backups
   - Encryption at rest
   - Secure deletion
   - Audit logging

## Conclusion

The Earnings Calendar feature represents a cornerstone of the Magnus Trading Platform, providing traders with essential earnings intelligence through an intuitive, no-code interface. By combining robust data synchronization, intelligent filtering, and comprehensive visualization, it empowers users to make informed trading decisions around earnings events.

The feature's success lies in its balance of simplicity and power—accessible to beginners yet comprehensive enough for advanced traders. Through continuous refinement and user feedback integration, the Earnings Calendar will evolve to meet the changing needs of the options trading community.

---

*For technical implementation details, see [ARCHITECTURE.md](ARCHITECTURE.md)*
*For API specifications, see [SPEC.md](SPEC.md)*
*For future enhancements, see [WISHLIST.md](WISHLIST.md)*