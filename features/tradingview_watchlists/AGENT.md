# TradingView Watchlists Feature Agent

## Agent Identity

- **Feature Name**: TradingView Watchlists
- **Agent Version**: 1.0.0
- **Feature Version**: 1.0.0
- **Last Updated**: 2025-11-01
- **Owner**: Magnus Platform
- **Status**: ✅ Active & Production Ready

## Role & Responsibilities

The TradingView Watchlists Agent is responsible for **comprehensive option trading management and portfolio tracking**. It serves as the central hub for monitoring active positions, managing watchlists, analyzing premiums, tracking trade history, and providing intelligent position insights. This agent orchestrates the integration of Robinhood positions, TradingView symbol lists, and market data to provide a unified trading experience.

### Primary Responsibilities
1. Display real-time option positions from Robinhood with P/L calculations
2. Manage curated watchlists for systematic opportunity tracking
3. Analyze 30-day option premiums with delta targeting (0.25-0.40)
4. Track comprehensive trade history with performance metrics
5. Synchronize watchlist data from TradingView exports and database
6. Provide theta decay visualizations for position timing
7. Calculate win rates, average returns, and annualized performance
8. Enable CSV export for tax reporting and analysis

### Data Sources
- **Robinhood API**: Real-time position data, option prices, account values
- **TradingView**: Watchlist exports and symbol management
- **PostgreSQL Database**: Watchlists, trade history, premium data, stock information
- **Yahoo Finance**: Stock prices, option chains, market data
- **Local Calculations**: P/L metrics, theta projections, Greeks, returns

## Feature Capabilities

### What This Agent CAN Do
- ✅ Display all active CSP and CC positions from Robinhood
- ✅ Calculate real-time P/L with current market prices
- ✅ Log closed trades with full detail tracking
- ✅ Import watchlists from TradingView or manual input
- ✅ Store and manage multiple watchlists in database
- ✅ Analyze 30-day option premiums for watchlist symbols
- ✅ Calculate monthly and annual return percentages
- ✅ Display option Greeks (delta, theta, IV)
- ✅ Validate liquidity (bid/ask spreads, volume, open interest)
- ✅ Track trade history with win rate and average days held
- ✅ Generate theta decay forecasts for positions
- ✅ Export trade history to CSV
- ✅ Background synchronization for price and premium updates
- ✅ Calculate annualized returns and profit percentages
- ✅ Show sector distribution and stock analytics

### What This Agent CANNOT Do
- ❌ Execute trades (requires Robinhood interface)
- ❌ Scan entire database (that's Database Scanner Agent's role)
- ❌ Find opportunities outside watchlists (that's Opportunities Agent)
- ❌ Track earnings dates automatically (that's Earnings Calendar Agent)
- ❌ Analyze calendar spreads (that's Calendar Spreads Agent)
- ❌ Manage Robinhood credentials (that's Settings Agent)
- ❌ Provide real-time streaming updates (uses periodic refresh)

## Dependencies

### Required Features
- **Settings Agent**: For Robinhood connection and credentials
- **Robinhood API**: For position data and authentication
- **PostgreSQL Database**: For watchlists, trade history, premium data

### Optional Features
- **Database Scanner Agent**: For broader market analysis
- **Earnings Calendar Agent**: For earnings date awareness
- **Opportunities Agent**: For discovery outside watchlists
- **Dashboard Agent**: For portfolio-level aggregation

### External APIs
- **Robinhood API**: Position data, option prices, account information
- **Yahoo Finance (yfinance)**: Stock prices, option chains, company info
- **TradingView**: Watchlist exports (manual import)

### Database Tables
```sql
-- Watchlist Management
CREATE TABLE tv_watchlists (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_refresh TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    symbol_count INTEGER DEFAULT 0
);

CREATE TABLE tv_watchlist_symbols (
    id SERIAL PRIMARY KEY,
    watchlist_id INTEGER REFERENCES tv_watchlists(id) ON DELETE CASCADE,
    symbol VARCHAR(20) NOT NULL,
    company_name VARCHAR(255),
    sector VARCHAR(100),
    industry VARCHAR(100),
    market_cap BIGINT,
    last_price DECIMAL(10,2),
    volume BIGINT,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(watchlist_id, symbol)
);

-- Premium Data
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
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Trade History
CREATE TABLE trade_history (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    strike_price DECIMAL(10,2),
    expiration_date DATE,
    premium_collected DECIMAL(10,2),
    contracts INTEGER DEFAULT 1,
    open_date DATE,
    close_date DATE,
    close_price DECIMAL(10,2),
    close_reason VARCHAR(50),
    dte_at_open INTEGER,
    days_held INTEGER,
    profit_loss DECIMAL(10,2),
    profit_loss_percent DECIMAL(5,2),
    annualized_return DECIMAL(5,2),
    strategy_type VARCHAR(50),
    status VARCHAR(20) DEFAULT 'open',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Key Files & Code

### Main Implementation
- `dashboard.py`: Lines 1293-1937 (TradingView Watchlists page rendering)
- `src/tradingview_db_manager.py`: Database interface for watchlist operations
- `src/trade_history_manager.py`: Trade lifecycle and P/L calculations
- `src/watchlist_sync_service.py`: Background synchronization service
- `src/robinhood_integration.py`: Position fetching from Robinhood

### Critical Functions
```python
# Position Fetching and Display (dashboard.py: 1306-1473)
def display_current_positions():
    """
    Fetches and displays active option positions from Robinhood
    - Logs into Robinhood with cached session
    - Retrieves open option positions
    - Calculates P/L metrics
    - Displays in formatted table
    """

# Trade Logging (dashboard.py: 1412-1463)
def log_closed_trade(symbol, strike, expiration, premium, close_price, reason, open_date):
    """
    Records closed trade in database
    - Calculates profit/loss
    - Computes days held and annualized return
    - Stores in trade_history table
    - Returns confirmation
    """

# Watchlist Import (tradingview_db_manager.py)
def import_from_text(text_input, watchlist_name):
    """
    Imports watchlist from text or TradingView export
    - Parses comma or line-separated symbols
    - Validates symbol format
    - Stores in database with metadata
    - Returns symbol list
    """

# Premium Analysis (dashboard.py: 1773-1897)
def analyze_watchlist_premiums(symbols, dte=30):
    """
    Analyzes option premiums for watchlist symbols
    - Fetches 30-day option chains
    - Targets delta 0.25-0.40 range
    - Calculates monthly returns
    - Filters by liquidity thresholds
    - Returns ranked opportunities
    """

# Theta Decay Forecast
def forecast_theta_decay(position):
    """
    Projects time decay profit timeline
    - Uses square root time decay model
    - Calculates daily profit projections
    - Shows milestones (7-day, 3-day, expiration)
    - Provides hold/close recommendations
    """
```

### Key Data Structures
```python
# Position Object
{
    'symbol': 'AAPL',
    'strategy': 'CSP' | 'CC' | 'Long Call' | 'Long Put',
    'strike_price': 150.00,
    'expiration_date': '2024-02-16',
    'dte': 15,
    'contracts': 1,
    'premium_collected': 250.00,
    'current_value': 120.00,
    'profit_loss': 130.00,
    'profit_loss_pct': 52.0
}

# Trade History Record
{
    'id': 1,
    'symbol': 'MSFT',
    'strike_price': 350.00,
    'premium_collected': 300.00,
    'close_price': 100.00,
    'profit_loss': 200.00,
    'profit_loss_percent': 66.67,
    'days_held': 21,
    'annualized_return': 1158.73,
    'close_reason': 'early_close' | 'expiration' | 'assignment'
}

# Watchlist Premium Analysis
{
    'symbol': 'NVDA',
    'stock_price': 450.00,
    'strike': 425.00,
    'dte': 30,
    'premium': 5.50,
    'delta': -0.30,
    'monthly_return': 1.29,
    'iv': 45.2,
    'bid': 5.40,
    'ask': 5.60,
    'volume': 5000,
    'open_interest': 10000
}
```

## Current State

### Implemented Features
✅ Real-time position monitoring from Robinhood
✅ Comprehensive P/L calculations (dollar and percentage)
✅ Trade history logging with performance tracking
✅ Watchlist import from TradingView or manual input
✅ Multiple watchlist management in database
✅ 30-day option premium analysis
✅ Delta-based filtering (0.25-0.40 target range)
✅ Theta decay visualization and forecasting
✅ CSV export for trade history
✅ Background synchronization for prices/premiums
✅ Win rate and performance statistics
✅ Annualized return calculations
✅ Sector and stock analytics
✅ Liquidity validation (volume/OI thresholds)

### Known Limitations
⚠️ Requires active Robinhood connection for positions
⚠️ Watchlist sync can take 5-10 minutes for 100+ symbols
⚠️ 15-minute delayed data (Yahoo Finance free tier)
⚠️ Theta forecast uses simplified model (not full Black-Scholes)
⚠️ No automatic earnings date filtering
⚠️ Manual TradingView watchlist import (no direct API)
⚠️ Limited to US equities only

### Recent Changes
- Enhanced trade logging with automatic calculations
- Added theta decay visualization with recommendations
- Improved watchlist synchronization performance
- Added sector distribution analytics
- Enhanced error handling for API failures

## Communication Patterns

### Incoming Requests

#### From Main Agent
```yaml
Request: "Show active positions with P/L"
Response:
  - Logs into Robinhood
  - Fetches open positions
  - Calculates current P/L
  - Returns formatted position list
```

#### From User
```yaml
Request: "Import my TradingView watchlist"
Response:
  - Displays import interface
  - Parses text input
  - Validates symbols
  - Stores in database
  - Returns confirmation with symbol count
```

### Outgoing Requests

#### To Robinhood API
```yaml
Request: "Get all open option positions"
Purpose: Fetch active positions for display
Expected Response:
  - List of option positions
  - Instrument details
  - Current market prices
  - Quantity and cost basis
```

#### To Yahoo Finance
```yaml
Request: "Get 30-day option chain for {symbol}"
Purpose: Analyze premium opportunities
Expected Response:
  - Available expirations
  - Put options with prices
  - Greeks (delta, IV)
  - Volume and open interest
```

#### To Database
```yaml
Request: "Upsert trade history"
Purpose: Store closed trade record
Data:
  - Symbol, strike, expiration
  - Premium collected, close price
  - Profit/loss calculations
  - Performance metrics
```

## Data Flow

```
User Opens TradingView Watchlists Page
       ↓
Check Robinhood Connection (via Settings)
       ↓
   Connected?
       ↓
    Yes → Fetch Active Positions
       ↓
Calculate P/L for Each Position
  - Premium vs Current Value
  - Percentage Captured
  - Days to Expiration
       ↓
Display Position Forms
  - Log Closed Trade Interface
  - Theta Decay Forecasts
  - P/L Summary Metrics
       ↓
       ↓
Watchlist Management Section
       ↓
Load Watchlists from Database
  ├─→ Auto-Sync Tab: Refresh watchlists
  ├─→ Import Tab: Add new watchlist
  ├─→ Analysis Tab: Premium analysis
  └─→ Saved Tab: Manage existing
       ↓
Premium Analysis (if requested)
  - Fetch stock prices (Yahoo Finance)
  - Get 30-day option chains
  - Calculate delta and returns
  - Filter by liquidity
  - Rank by monthly return
       ↓
Background Sync (optional)
  - Update stock prices
  - Refresh option chains
  - Calculate new premiums
  - Update database
       ↓
Trade History Display
  - Query trade_history table
  - Apply filters (symbol, limit)
  - Calculate statistics
  - Format for display
  - Enable CSV export
```

## Error Handling

### Robinhood Connection Errors
```python
try:
    positions = rh.get_open_option_positions()
except AuthenticationError:
    st.warning("Robinhood session expired. Please reconnect in Settings.")
    st.session_state['rh_connected'] = False
except Exception as e:
    logger.error(f"Failed to fetch positions: {e}")
    st.error("Unable to load positions. Try refreshing the page.")
```

### Watchlist Import Errors
```python
try:
    symbols = parse_watchlist_input(text)
    validate_symbols(symbols)
    store_in_database(watchlist_name, symbols)
except ValidationError as e:
    st.warning(f"Invalid symbols found: {e}")
except DatabaseError as e:
    st.error("Failed to save watchlist. Check database connection.")
```

### Premium Analysis Errors
```python
try:
    option_chain = yf.Ticker(symbol).option_chain(expiry)
except Exception as e:
    logger.warning(f"No options available for {symbol}: {e}")
    continue  # Skip to next symbol
```

### Database Errors
```python
try:
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
except psycopg2.IntegrityError:
    logger.warning("Duplicate entry, skipping")
    conn.rollback()
except psycopg2.Error as e:
    logger.error(f"Database error: {e}")
    st.error("Database operation failed")
    conn.rollback()
finally:
    cursor.close()
    conn.close()
```

## Performance Considerations

### Optimization Strategies
- **Position Caching**: Cache Robinhood positions in session state
- **Lazy Loading**: Load trade history on-demand
- **Batch Processing**: Sync watchlist symbols in batches of 10
- **Database Indexing**: Indexes on symbol, date, watchlist_id
- **Query Optimization**: Use DISTINCT ON for best option per symbol

### Performance Metrics
| Operation | Target | Current |
|-----------|--------|---------|
| Load positions | < 2s | ~1.5s |
| Import watchlist | < 1s | ~500ms |
| Premium analysis (50 symbols) | < 60s | ~45s |
| Trade history query | < 500ms | ~200ms |
| Background sync (100 symbols) | < 10min | ~6min |

### Resource Usage
- **Memory**: 200-400MB for full feature
- **Database**: ~50MB for 10 watchlists
- **Network**: Moderate (API calls for prices/options)
- **CPU**: Low except during sync operations

## Testing Checklist

### Before Deployment
- [ ] Positions load correctly with Robinhood connection
- [ ] Empty state displays when not connected
- [ ] Trade logging calculates P/L correctly
- [ ] Watchlist import handles various formats
- [ ] Premium analysis returns valid results
- [ ] Theta forecasts calculate accurately
- [ ] Trade history displays and filters work
- [ ] CSV export includes all data
- [ ] Background sync completes without errors
- [ ] No crashes with 0 positions
- [ ] No crashes with 100+ watchlist symbols

### Integration Tests
- [ ] Robinhood authentication works
- [ ] Database connection pool handles concurrent requests
- [ ] Watchlist sync doesn't block UI
- [ ] Trade history persists across sessions
- [ ] Premium data updates correctly

## Maintenance

### When to Update This Agent

1. **User Request**: "Add new watchlist source integration"
   - Implement new import method
   - Update database schema if needed
   - Add UI controls
   - Document in CHANGELOG.md

2. **Bug Report**: "P/L calculations incorrect for covered calls"
   - Debug P/L logic in position display
   - Verify premium direction handling
   - Add unit tests
   - Document fix

3. **Feature Request**: "Add Greeks display for all positions"
   - Fetch Greeks from Robinhood API
   - Add columns to position table
   - Update data structures
   - Update SPEC.md

4. **API Change**: Yahoo Finance updates option chain format
   - Update parsing logic
   - Test backward compatibility
   - Handle edge cases
   - Document breaking changes

### Monitoring
- Check position load success rate (> 95%)
- Monitor watchlist sync completion (< 10min for 100 symbols)
- Track database growth (alert if > 5GB)
- Review trade history accuracy (spot check)
- Monitor API error rates

## Integration Points

### Robinhood Integration
```python
# Position fetching
import robin_stocks.robinhood as rh
rh.login(username, password, expiresIn=86400, store_session=True)
positions = rh.get_open_option_positions()
```

### Database Integration
```python
# Watchlist operations
from tradingview_db_manager import TradingViewDBManager
manager = TradingViewDBManager()
watchlists = manager.get_all_symbols_dict()
premiums = manager.get_premiums_for_symbols(symbols, dte=30)
```

### Trade History Integration
```python
# Trade logging
from trade_history_manager import TradeHistoryManager
th_manager = TradeHistoryManager()
trade_id = th_manager.add_trade(symbol, strike, expiration, premium)
th_manager.close_trade(trade_id, close_price, reason)
```

## Future Enhancements

### Planned Features
- **Direct TradingView API Integration**: Auto-sync without manual export
- **WebSocket Updates**: Real-time price and P/L updates
- **Advanced Trade Analytics**: Sharpe ratio, max drawdown, profit factor
- **Multi-Account Support**: Track positions across multiple brokerages
- **Custom Alerts**: Email/SMS notifications for profit targets
- **Calendar Integration**: Sync earnings dates automatically
- **Tax Reporting**: Automated tax form generation
- **Position Sizing Calculator**: Risk-based position recommendations
- **Watchlist Sharing**: Export/import watchlists with community

### Technical Improvements
- Implement connection pooling for database
- Add Redis caching for frequently accessed data
- Optimize watchlist sync with parallel processing
- Implement full Black-Scholes for Greeks
- Add comprehensive unit test coverage
- Create integration test suite

## Questions This Agent Can Answer

1. "What are my current active positions?"
2. "How much profit am I making on each position?"
3. "What's my overall win rate and average return?"
4. "Which positions should I consider closing?"
5. "Show me theta decay for my CSPs"
6. "What premiums are available on my watchlist?"
7. "Which symbols have the best monthly returns?"
8. "How many days have I held this position?"
9. "What's my annualized return on closed trades?"
10. "Export my trade history for tax reporting"
11. "Which options have sufficient liquidity?"
12. "What's the delta on this premium opportunity?"
13. "Add this TradingView watchlist to my database"
14. "Show me all trades for AAPL"
15. "What sectors are in my watchlist?"

## Questions This Agent CANNOT Answer

1. "Scan the entire stock database" → Database Scanner Agent
2. "Find opportunities outside my watchlists" → Opportunities Agent
3. "When is the next earnings date?" → Earnings Calendar Agent
4. "Analyze calendar spread opportunities" → Calendar Spreads Agent
5. "Update my Robinhood password" → Settings Agent
6. "What's my total account value?" → Dashboard Agent
7. "Execute this trade automatically" → User must use broker
8. "Predict future stock prices" → Cannot predict (shows probabilities only)
9. "Show prediction market sentiment" → Prediction Markets Agent (when available)
10. "Real-time streaming quotes" → Uses periodic refresh, not streaming

---

**For detailed architecture and specifications, see:**
- [ARCHITECTURE.md](./ARCHITECTURE.md)
- [SPEC.md](./SPEC.md)
- [README.md](./README.md)

**For current tasks and planned work, see:**
- [WISHLIST.md](./WISHLIST.md) (if exists)
- [CHANGELOG.md](./CHANGELOG.md) (if exists)
