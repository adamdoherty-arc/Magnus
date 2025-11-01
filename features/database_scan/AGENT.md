# Database Scan Feature Agent

## Agent Identity

- **Feature Name**: Database Scan
- **Agent Version**: 1.0.0
- **Feature Version**: 1.0.0
- **Last Updated**: 2025-11-01
- **Owner**: Magnus Platform
- **Status**: ✅ Active & Production Ready

## Role & Responsibilities

The Database Scan Agent is responsible for **comprehensive market-wide options discovery** across the entire stock universe stored in the PostgreSQL database. Unlike the TradingView Watchlists Agent which focuses on curated lists, this agent enables broad market scanning to discover high-yield opportunities across all 1,200+ stocks in the system.

### Primary Responsibilities
1. Scan entire database (1,200+ stocks) for premium opportunities
2. Query pre-computed options data efficiently
3. Filter by price range, premium thresholds, and DTE
4. Display real-time premium analysis with Greeks
5. Provide database-wide analytics and statistics
6. Enable bulk stock addition and data management
7. Support sector-based filtering and analysis
8. Maintain database health and synchronization status

### Data Sources
- **PostgreSQL Database**: Primary source for all stock and premium data
- **Yahoo Finance**: Stock price updates and company information
- **Robinhood API**: Options chain data (via sync service)
- **Local Calculations**: Return metrics, filtering, ranking

## Feature Capabilities

### What This Agent CAN Do
- ✅ Scan all 1,200+ stocks in database simultaneously
- ✅ Query pre-computed premium data for instant results
- ✅ Filter by stock price range ($min to $max)
- ✅ Filter by minimum premium thresholds
- ✅ Filter by DTE range (7-60 days)
- ✅ Display delta-filtered options (0.25-0.40 range)
- ✅ Show sector distribution and analytics
- ✅ Add bulk stocks to database with Yahoo Finance data
- ✅ Display summary statistics (options found, average returns)
- ✅ Sort by any column (symbol, premium %, monthly return)
- ✅ Show bid/ask spreads and liquidity metrics
- ✅ Export results to CSV

### What This Agent CANNOT Do
- ❌ Scan stocks not in database (use Opportunities Agent)
- ❌ Track active positions (that's Positions Agent's role)
- ❌ Manage watchlists (that's TradingView Watchlists Agent)
- ❌ Execute trades (view-only analysis)
- ❌ Provide earnings date filtering (that's Earnings Calendar Agent)
- ❌ Analyze calendar spreads (that's Calendar Spreads Agent)
- ❌ Update premium data (requires background sync service)

## Dependencies

### Required Features
- **PostgreSQL Database**: For stock and premium data storage
- **Background Sync Service**: For options data updates

### Optional Features
- **TradingView Watchlists Agent**: Can add discovered stocks to watchlists
- **Earnings Calendar Agent**: For earnings-aware filtering
- **Opportunities Agent**: For live scanning outside database

### External APIs
- **Yahoo Finance**: Stock data and basic company info
- **Robinhood API**: Options chains (via sync service)

### Database Tables
```sql
CREATE TABLE stocks (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(255),
    sector VARCHAR(100),
    industry VARCHAR(100),
    market_cap BIGINT,
    current_price DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE stock_premiums (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    strike_price DECIMAL(10,2),
    dte INTEGER,
    premium DECIMAL(10,2),
    delta DECIMAL(5,4),
    theta DECIMAL(10,4),
    implied_volatility DECIMAL(5,2),
    bid DECIMAL(10,2),
    ask DECIMAL(10,2),
    volume INTEGER,
    open_interest INTEGER,
    monthly_return DECIMAL(5,2),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_symbol_dte (symbol, dte),
    INDEX idx_delta (delta)
);

CREATE TABLE stock_data (
    symbol VARCHAR(10) PRIMARY KEY,
    current_price DECIMAL(10,2),
    volume BIGINT,
    market_cap BIGINT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Key Files & Code

### Main Implementation
- `dashboard.py`: Lines 2019-2218 (Database Scanner UI)
- `src/database_scanner.py`: Core scanning engine with optimized queries
- `src/tradingview_db_manager.py`: Database interface layer
- `src/watchlist_sync_service.py`: Background sync processor

### Critical Functions
```python
# Database-First Scanning (database_scanner.py)
def scan_stored_premiums(min_price=0, max_price=10000, min_premium=0, dte_target=30):
    """
    Query pre-computed premiums from database
    - Fast response (< 200ms)
    - Optimized SQL with DISTINCT ON
    - Delta filtering built-in (0.25-0.40)
    - Returns one best option per symbol
    """

# Optimized Query
query = """
    SELECT DISTINCT ON (sp.symbol)
        sp.symbol,
        sd.current_price as stock_price,
        sp.strike_price,
        sp.dte,
        sp.premium,
        sp.delta,
        sp.monthly_return,
        sp.implied_volatility as iv,
        sp.bid,
        sp.ask,
        sp.volume,
        sp.open_interest,
        s.name,
        s.sector
    FROM stock_premiums sp
    LEFT JOIN stock_data sd ON sp.symbol = sd.symbol
    LEFT JOIN stocks s ON sp.symbol = s.ticker
    WHERE sp.dte BETWEEN %s AND %s
        AND ABS(sp.delta) BETWEEN 0.25 AND 0.40
        AND sp.premium >= %s
        AND (sd.current_price BETWEEN %s AND %s OR sd.current_price IS NULL)
    ORDER BY sp.symbol, sp.monthly_return DESC
"""

# Bulk Stock Addition
def add_stocks_to_database(symbols_list):
    """
    Add multiple stocks to database
    - Fetch data from Yahoo Finance
    - Extract sector, industry, market cap
    - Upsert to stocks table
    - Return success count
    """
```

## Current State

### Implemented Features
✅ Full database scanning (1,200+ stocks)
✅ Optimized queries with sub-second response
✅ Price range filtering
✅ Minimum premium filtering
✅ DTE range selection (7-60 days)
✅ Delta-based filtering (0.25-0.40)
✅ Sector distribution analytics
✅ Database overview statistics
✅ Bulk stock addition with Yahoo Finance
✅ CSV export functionality
✅ Sortable results table
✅ Summary metrics (count, averages)

### Known Limitations
⚠️ Data freshness depends on background sync schedule
⚠️ Database scan shows only pre-computed data (not live)
⚠️ Limited to stocks already in database
⚠️ Full database sync takes 10-15 minutes
⚠️ No earnings date filtering built-in
⚠️ No real-time price updates during viewing

### Recent Changes
- Optimized query performance with better indexing
- Added sector distribution visualization
- Improved bulk import functionality
- Enhanced error handling for missing data

## Communication Patterns

### Incoming Requests

#### From Main Agent
```yaml
Request: "Scan entire database for 30-day CSPs under $50"
Response:
  - Queries stock_premiums table
  - Applies price and DTE filters
  - Returns ranked opportunities
  - Shows summary statistics
```

#### From User
```yaml
Request: "Show me all opportunities with >1% monthly return"
Response:
  - Filters by monthly_return >= 1.0
  - Sorts by highest return first
  - Displays in table format
  - Updates summary metrics
```

### Outgoing Requests

#### To Database
```yaml
Request: "Query stock_premiums with filters"
Purpose: Retrieve matching opportunities
Expected Response:
  - List of premium opportunities
  - With stock data joined
  - Filtered and sorted
  - One best option per symbol
```

#### To Yahoo Finance
```yaml
Request: "Get stock data for bulk import"
Purpose: Add new stocks to database
Expected Response:
  - Company name
  - Sector and industry
  - Market cap
  - Current price
```

## Data Flow

```
User Opens Database Scan Page
       ↓
Load Database Overview
  - Total stock count (1,205)
  - Stocks with options (~500)
  - Sector distribution
  - Price range distribution
       ↓
User Navigates to "Scan Premiums" Tab
       ↓
Apply Default Filters
  - DTE: 28-32 days
  - Delta: 0.25-0.40
  - Min Premium: $0
  - Price Range: $0-$10,000
       ↓
Execute Database Query
  - DISTINCT ON (symbol)
  - JOIN stock_data, stocks
  - WHERE clauses for filters
  - ORDER BY monthly_return DESC
       ↓
Process Results (< 200ms)
  - Format prices and percentages
  - Calculate summary metrics
  - Prepare for display
       ↓
Render Results Table
  - Symbol, Price, Strike, Premium
  - Delta, Monthly %, IV
  - Bid/Ask, Volume, OI
  - Company Name, Sector
       ↓
Display Summary
  - Options found: 387
  - Avg Premium %: 1.2%
  - Avg Monthly Return: 1.3%
       ↓
User Interaction
  - Sort by columns
  - Adjust filters
  - Export to CSV
```

## Error Handling

### Database Connection Errors
```python
try:
    conn = db_manager.get_connection()
    results = execute_scan_query(conn, filters)
except psycopg2.OperationalError:
    st.error("Database connection failed. Check PostgreSQL service.")
except Exception as e:
    logger.error(f"Scan error: {e}")
    st.error("Unable to complete scan. Try refreshing.")
```

### Missing Data Handling
```python
# Handle NULL values gracefully
query = """
    SELECT ...,
        COALESCE(sd.current_price, 0) as stock_price,
        COALESCE(s.name, sp.symbol) as name
    ...
"""
```

### Query Timeout Protection
```python
# Set statement timeout
cursor.execute("SET statement_timeout = '30s'")
try:
    results = cursor.fetchall()
except psycopg2.extensions.QueryCanceledError:
    st.warning("Query took too long. Try narrowing filters.")
```

## Performance Considerations

### Optimization Strategies
- **Materialized Views**: For common queries (future enhancement)
- **Composite Indexes**: On (symbol, dte) and delta columns
- **Query Optimization**: DISTINCT ON instead of GROUP BY
- **Connection Pooling**: Reuse database connections
- **Lazy Loading**: Load results on tab activation

### Performance Metrics
| Operation | Target | Current |
|-----------|--------|---------|
| Database overview | < 500ms | ~300ms |
| Premium scan (all stocks) | < 1s | ~600ms |
| Filter application | < 200ms | ~150ms |
| Bulk stock import (100) | < 2min | ~90s |
| CSV export | < 1s | ~500ms |

### Scalability
- **Current**: 1,200 stocks, ~5,000 options
- **Tested**: 5,000 stocks, ~25,000 options
- **Limit**: Database size limited by disk space
- **Recommendation**: Archive old data quarterly

## Questions This Agent Can Answer

1. "What opportunities exist across the entire database?"
2. "Show me all stocks under $50 with good premiums"
3. "Which sectors have the most premium opportunities?"
4. "What's the average monthly return across all database stocks?"
5. "How many stocks in the database have options data?"
6. "What's the price distribution of stocks in the database?"
7. "Show me high-IV stocks in the technology sector"
8. "Which stocks have the best liquidity (volume/OI)?"
9. "Add these 50 stocks to the database"
10. "Export database scan results to CSV"

## Questions This Agent CANNOT Answer

1. "What are my current positions?" → Positions Agent
2. "Scan stocks not in database" → Opportunities Agent
3. "When is the next earnings date?" → Earnings Calendar Agent
4. "Manage my watchlists" → TradingView Watchlists Agent
5. "Analyze calendar spreads" → Calendar Spreads Agent
6. "Update Robinhood settings" → Settings Agent
7. "Show real-time live prices" → Uses cached data
8. "Execute this trade" → User must use broker
9. "Predict future profitability" → Shows probabilities only
10. "Sync options data now" → Background service (not interactive)

---

**For detailed information, see:**
- [README.md](./README.md)
- Additional documentation in other feature folders
