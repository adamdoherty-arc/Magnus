# Earnings Calendar Feature Agent

## Agent Identity

- **Feature Name**: Earnings Calendar
- **Agent Version**: 1.0.0
- **Feature Version**: 1.0.0
- **Last Updated**: 2025-11-01
- **Owner**: Magnus Platform
- **Status**: ✅ Active & Production Ready

## Role & Responsibilities

The Earnings Calendar Agent is responsible for **earnings event tracking and analysis** to help traders avoid assignment risk and capitalize on volatility opportunities around earnings announcements. It provides a comprehensive, button-driven interface (no CLI required) for managing earnings data.

### Primary Responsibilities
1. Track upcoming and historical earnings events
2. Sync earnings data from Robinhood API automatically
3. Display earnings dates, times (BMO/AMC), and EPS estimates/actuals
4. Filter by date ranges, time periods, and result types
5. Manage database tables with one-click initialization
6. Calculate beat/miss/meet status automatically
7. Provide exportable data for analysis
8. Alert traders to positions with upcoming earnings

### Data Sources
- **Robinhood API**: Real-time earnings dates and historical EPS data
- **PostgreSQL Database**: Earnings events and history storage
- **Internal Database**: Stock master data for enrichment

## Feature Capabilities

### What This Agent CAN Do
- ✅ Initialize database tables with one button click
- ✅ Sync earnings data from Robinhood automatically
- ✅ Display upcoming earnings with dates and times
- ✅ Show historical earnings with EPS actuals vs estimates
- ✅ Filter by date range (This Week, Next Week, This Month, etc.)
- ✅ Filter by time (All, BMO, AMC)
- ✅ Filter by result (All, Beat, Miss, Meet, Pending)
- ✅ Calculate beat/miss/meet status automatically
- ✅ Show IV changes pre/post earnings
- ✅ Display price movement percentages
- ✅ Export earnings data to CSV
- ✅ Track up to 100 stocks per sync
- ✅ Store quarterly earnings history (8 quarters)

### What This Agent CANNOT Do
- ❌ Predict earnings outcomes
- ❌ Execute trades automatically
- ❌ Track options positions (that's Positions Agent)
- ❌ Manage watchlists (that's TradingView Watchlists Agent)
- ❌ Provide real-time news/analysis
- ❌ Alert via email/SMS (UI-only notifications)
- ❌ Sync more than 100 stocks per batch

## Dependencies

### Required Features
- **PostgreSQL Database**: For earnings data storage
- **Robinhood API**: For earnings data fetching
- **Settings Agent**: For Robinhood credentials

### Optional Features
- **Positions Agent**: For position/earnings correlation
- **TradingView Watchlists Agent**: For watchlist-based sync

### Database Tables
```sql
CREATE TABLE earnings_events (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    earnings_date TIMESTAMP WITH TIME ZONE,
    earnings_time VARCHAR(10),  -- 'BMO' or 'AMC'
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
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(symbol, earnings_date)
);

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

## Key Files & Code

### Main Implementation
- `dashboard.py`: Earnings Calendar UI and button-driven interface
- `src/earnings_calendar_manager.py`: Database operations and sync logic
- `src/robinhood_integration.py`: Earnings data fetching from Robinhood

### Critical Functions
```python
# Database Initialization
def initialize_earnings_tables():
    """
    One-click table creation
    - Creates earnings_events table
    - Creates earnings_history table
    - Adds indexes for performance
    - Returns success status
    """

# Earnings Synchronization
def sync_earnings_from_robinhood(symbols, limit=100):
    """
    Batch sync from Robinhood API
    - Fetches last 8 quarters per symbol
    - Extracts EPS actual/estimate
    - Calculates beat/miss/meet
    - Upserts to database
    - Returns sync count
    """

# Filtering and Display
def get_filtered_earnings(date_filter, time_filter, result_filter):
    """
    Query earnings with filters
    - Applies date range logic
    - Filters by BMO/AMC
    - Filters by beat/miss/meet status
    - Joins with stocks table
    - Returns formatted results
    """
```

## Current State

### Implemented Features
✅ One-click database initialization
✅ Automated Robinhood sync (batch processing)
✅ Advanced filtering system (date, time, result)
✅ Real-time metrics dashboard
✅ Beat/miss/meet calculation
✅ CSV export capability
✅ Progress tracking for sync operations
✅ Historical earnings storage (8 quarters)
✅ Upcoming earnings visibility
✅ Stock enrichment (sector, name)

### Known Limitations
⚠️ Limited to 100 stocks per sync batch
⚠️ Requires active Robinhood connection
⚠️ No automatic email/SMS alerts
⚠️ No earnings call transcript integration
⚠️ Manual sync required (no auto-schedule)
⚠️ IV tracking requires manual update

## Performance Metrics

| Operation | Target | Current |
|-----------|--------|---------|
| Database initialization | < 2s | ~1s |
| Sync 100 stocks | < 5min | ~3min |
| Filter/display results | < 500ms | ~200ms |
| CSV export | < 1s | ~500ms |

## Questions This Agent CAN Answer

1. "When is the next earnings date for AAPL?"
2. "Show me all earnings this week"
3. "Which stocks beat earnings estimates?"
4. "What earnings are before market open?"
5. "Export earnings calendar to CSV"
6. "How many earnings events are next month?"
7. "Show historical earnings performance for MSFT"
8. "Which stocks have pending earnings?"

## Questions This Agent CANNOT Answer

1. "What positions do I have?" → Positions Agent
2. "Find new CSP opportunities" → Opportunities Agent
3. "Manage my watchlists" → TradingView Watchlists Agent
4. "Will this stock beat earnings?" → Cannot predict
5. "Execute a trade before earnings" → User must use broker
6. "Send me alerts when earnings are announced" → No alert system yet

---

**For detailed information, see:**
- [README.md](./README.md)
- [ARCHITECTURE.md](./ARCHITECTURE.md) (if exists)
- [SPEC.md](./SPEC.md) (if exists)
