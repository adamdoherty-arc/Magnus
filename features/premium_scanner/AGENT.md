# Premium Scanner Feature Agent

## Agent Identity

- **Feature Name**: Premium Scanner
- **Agent Version**: 2.0.0
- **Feature Version**: 2.0.0
- **Last Updated**: 2025-11-01
- **Owner**: Magnus Platform
- **Status**: ✅ Active & Production Ready

## Role & Responsibilities

The Premium Scanner Agent is responsible for **multi-expiration options analysis and delta-based opportunity discovery**. It represents the core intelligence of the wheel strategy platform, simultaneously analyzing 6 different expiration periods to identify optimal premium-generating opportunities while managing assignment risk through sophisticated delta filtering.

### Primary Responsibilities
1. Scan options across multiple expiration dates simultaneously (7, 14, 21, 30, 45, 60 DTE)
2. Calculate Black-Scholes delta for probability-based filtering (target 0.20-0.40 range)
3. Fetch real-time options chains from Robinhood API
4. Calculate comprehensive return metrics (premium %, monthly, annual)
5. Validate liquidity through volume and open interest thresholds
6. Store options data in PostgreSQL for historical tracking
7. Provide background synchronization for watchlist symbols
8. Integrate with TradingView watchlists for symbol management
9. Support both interactive scanning and database-first queries

### Data Sources
- **Robinhood API**: Primary source for options chains (free, unlimited)
- **Polygon API**: Stock prices and market data (premium service)
- **Yahoo Finance**: Fallback for stock prices and basic data
- **PostgreSQL Database**: Stored premium data and historical tracking
- **TradingView**: Watchlist integration for symbol curation
- **Local Calculations**: Black-Scholes Greeks, return projections

## Feature Capabilities

### What This Agent CAN Do
- ✅ Analyze 6 expiration dates per symbol simultaneously (7, 14, 21, 30, 45, 60 DTE)
- ✅ Calculate Black-Scholes delta with 4 decimal precision
- ✅ Filter options by delta range for optimal probability management
- ✅ Fetch real-time options data from Robinhood (15-min delayed for free tier)
- ✅ Store complete options data in PostgreSQL database
- ✅ Calculate premium percentage, monthly return, and annual return
- ✅ Validate liquidity (min volume: 100, min OI: 50, configurable)
- ✅ Rank opportunities by multiple criteria
- ✅ Support background sync for continuous data updates
- ✅ Integrate with TradingView watchlists (auto-import symbols)
- ✅ Provide database scanner for pre-computed results
- ✅ Export results to CSV
- ✅ Display bid-ask spreads and implied volatility
- ✅ Calculate break-even prices and probability of profit
- ✅ Show Greeks (delta, gamma, theta, vega) when available

### What This Agent CANNOT Do
- ❌ Execute trades (view-only analysis)
- ❌ Track active positions (that's Positions Agent's role)
- ❌ Provide real-time streaming updates (uses periodic refresh)
- ❌ Predict earnings dates (that's Earnings Calendar Agent)
- ❌ Analyze calendar spreads specifically (that's Calendar Spreads Agent)
- ❌ Modify Robinhood settings (that's Settings Agent)
- ❌ Guarantee profitability (provides analysis and probabilities only)
- ❌ Scan international markets (US equities only)

## Dependencies

### Required Features
- **Robinhood API**: For options chains and Greeks
- **PostgreSQL Database**: For data storage and retrieval
- **Settings Agent**: For Robinhood credentials and connection management

### Optional Features
- **TradingView Watchlists Agent**: For curated symbol lists
- **Earnings Calendar Agent**: For earnings date awareness
- **Database Scanner Agent**: For stored premium queries
- **Polygon API**: For enhanced stock price data

### External APIs
- **Robinhood API**:
  - Options chains with full Greeks
  - Real-time quotes during market hours
  - Unlimited API calls (with rate limiting)
- **Polygon API**:
  - Stock prices and quotes
  - Market data aggregates
  - Rate limited (5 req/min free tier)
- **Yahoo Finance**:
  - Fallback stock prices
  - Basic company info
  - No authentication required

### Database Tables
```sql
-- Primary options data storage
CREATE TABLE stock_premiums (
    symbol VARCHAR(10),
    expiration_date DATE,
    strike_price DECIMAL(10,2),
    dte INTEGER,
    premium DECIMAL(10,2),
    delta DECIMAL(5,4),
    gamma DECIMAL(5,4),
    theta DECIMAL(5,4),
    vega DECIMAL(5,4),
    implied_volatility DECIMAL(5,2),
    volume INTEGER,
    open_interest INTEGER,
    monthly_return DECIMAL(10,2),
    annual_return DECIMAL(10,2),
    updated_at TIMESTAMP,
    UNIQUE(symbol, expiration_date, strike_price)
);

-- Stock data caching
CREATE TABLE stock_data (
    symbol VARCHAR(10) PRIMARY KEY,
    current_price DECIMAL(10,2),
    volume BIGINT,
    market_cap BIGINT,
    updated_at TIMESTAMP
);
```

## Key Files & Code

### Main Implementation
- `dashboard.py`: Lines 1122-1292 (Premium Scanner UI)
- `dashboard.py`: Lines 2019-2218 (Database Scanner UI)
- `dashboard.py`: Lines 1293-1899 (TradingView Watchlists integration)
- `src/premium_scanner.py`: Core scanning logic
- `src/enhanced_options_fetcher.py`: Multi-expiration fetching with Greeks
- `src/watchlist_sync_service.py`: Background synchronization
- `src/database_scanner.py`: Database query optimization

### Critical Functions
```python
# Multi-Expiration Fetching (enhanced_options_fetcher.py)
def get_all_expirations_data(symbol, target_dtes=[7,14,21,30,45,60]):
    """
    Fetches options for multiple expiration dates
    - Finds closest actual expiration to each target DTE
    - Calculates Black-Scholes delta for each strike
    - Filters by delta range (0.20-0.40)
    - Returns aggregated results for all expirations
    """

# Black-Scholes Delta Calculation
def calculate_delta(S, K, T, r, sigma, option_type='put'):
    """
    Precise delta calculation using Black-Scholes model
    Parameters:
      S: Current stock price
      K: Strike price
      T: Time to expiration (years)
      r: Risk-free rate (default 0.045)
      sigma: Implied volatility
    Returns: Delta with 4 decimal precision
    """

# Return Calculations
def calculate_returns(strike_price, premium, dte):
    """
    Comprehensive return metrics:
    - Premium % = (Premium / Strike) × 100
    - Monthly Return = (Premium % / DTE) × 30
    - Annual Return = Monthly Return × 12
    - Break-even = Strike - Premium
    """

# Background Sync (watchlist_sync_service.py)
def sync_watchlist_symbols(symbols, batch_size=10):
    """
    Background synchronization process:
    - Batches symbols for API efficiency
    - Fetches prices and options
    - Calculates Greeks
    - Upserts to database
    - Updates cache
    """

# Database Scanner
def scan_stored_premiums(filters):
    """
    Query pre-computed premiums from database
    - Fast response (< 200ms)
    - Complex filtering support
    - Historical comparison capability
    """
```

### Configuration Parameters
```python
# Target expiration dates (in days)
TARGET_DTES = [7, 14, 21, 30, 45, 60]

# Delta filtering range
DELTA_RANGE = (0.20, 0.40)  # 60-80% probability of keeping premium

# Liquidity thresholds
MIN_VOLUME = 100
MIN_OPEN_INTEREST = 50

# Risk-free rate for Greek calculations
RISK_FREE_RATE = 0.045  # 4.5% annual

# Cache TTL
CACHE_TTL = 900  # 15 minutes

# Batch processing
BATCH_SIZE = 10  # symbols per batch
```

## Current State

### Implemented Features
✅ Multi-expiration scanning (6 target DTEs)
✅ Black-Scholes delta calculation
✅ Delta-based filtering (configurable range)
✅ Robinhood API integration
✅ PostgreSQL database storage
✅ Background sync service
✅ TradingView watchlist integration
✅ Database scanner with optimized queries
✅ Premium %, monthly, and annual return calculations
✅ Liquidity validation (volume/OI)
✅ Implied volatility tracking
✅ Greeks display (delta, gamma, theta, vega)
✅ Break-even price calculations
✅ Probability of profit estimation
✅ CSV export functionality

### Known Limitations
⚠️ 15-minute delayed data for Robinhood free tier
⚠️ Scanning 100 symbols takes 3-5 minutes
⚠️ No real-time WebSocket updates (uses periodic refresh)
⚠️ Delta calculations don't account for dividends
⚠️ Background sync runs independently (not visible in UI)
⚠️ Database can grow large (requires periodic cleanup)
⚠️ Limited to US equities only

### Recent Changes
- Implemented multi-expiration support (v2.0 feature)
- Added Black-Scholes delta calculations
- Enhanced database schema with Greeks columns
- Optimized scanning with parallel processing
- Added background sync service
- Improved TradingView integration

## Communication Patterns

### Incoming Requests

#### From Main Agent
```yaml
Request: "Scan for 30-day CSP opportunities with delta 0.25-0.35"
Response:
  - Loads symbols from watchlist
  - Fetches options chains for 30 DTE
  - Calculates delta for each strike
  - Filters to 0.25-0.35 range
  - Returns ranked opportunities
```

#### From User
```yaml
Request: "Show me all expirations for AAPL"
Response:
  - Fetches AAPL options for all 6 target DTEs
  - Calculates Greeks for each expiration
  - Returns comprehensive analysis
  - Displays in multi-expiration table
```

### Outgoing Requests

#### To Robinhood API
```yaml
Request: "Get options chain for {symbol}"
Purpose: Fetch all put options with Greeks
Expected Response:
  - All available expirations
  - Complete options chain for each
  - Bid/ask prices
  - Volume and open interest
  - Greeks (delta, gamma, theta, vega)
  - Implied volatility
```

#### To Database
```yaml
Request: "Upsert premium data for {symbol}"
Purpose: Store/update options data
Data:
  - Symbol, strike, expiration
  - Premium metrics
  - Greeks
  - Liquidity data
  - Timestamp
```

## Data Flow

```
User Initiates Scan
       ↓
Load Symbol List
  - TradingView Watchlist
  - Database Stocks
  - Manual Input
       ↓
For Each Symbol:
  ├─→ Fetch Current Stock Price (Polygon/Yahoo)
  ├─→ Login to Robinhood (cached session)
  ├─→ Get Available Expirations
  └─→ For Each Target DTE (7,14,21,30,45,60):
      ├─→ Find Closest Actual Expiration
      ├─→ Fetch Options Chain
      ├─→ For Each Put Strike:
      │   ├─→ Calculate Delta (Black-Scholes)
      │   ├─→ Filter by Delta Range (0.20-0.40)
      │   ├─→ Validate Liquidity (vol/OI)
      │   ├─→ Calculate Returns (%, monthly, annual)
      │   └─→ Create Opportunity Object
      └─→ Select Optimal Strike per Expiration
       ↓
Aggregate All Results
  - Deduplicate
  - Apply filters
       ↓
Store in Database (async)
  - Upsert stock_premiums
  - Update stock_data
  - Refresh cache
       ↓
Rank and Display
  - Sort by monthly return
  - Group by expiration
  - Show top opportunities
  - Enable table sorting
```

## Error Handling

### Robinhood API Errors
```python
try:
    options_chain = rh.options.get_chains(symbol)
except AuthenticationError:
    logger.error("Robinhood authentication failed")
    st.error("Please reconnect to Robinhood in Settings")
except RateLimitError as e:
    logger.warning(f"Rate limit hit: {e}")
    time.sleep(2)  # Brief pause then retry
except Exception as e:
    logger.error(f"API error for {symbol}: {e}")
    continue  # Skip symbol
```

### Missing Expiration
```python
def find_closest_expiration(symbol, target_dte):
    """Find nearest available expiration to target DTE"""
    expirations = get_available_expirations(symbol)
    if not expirations:
        logger.warning(f"No expirations available for {symbol}")
        return None
    # Find closest match with tolerance
    closest = min(expirations, key=lambda x: abs(x.dte - target_dte))
    return closest if abs(closest.dte - target_dte) <= TOLERANCE else None
```

### Database Errors
```python
try:
    db.upsert_premium(premium_data)
except IntegrityError as e:
    logger.error(f"Database constraint violation: {e}")
    # Skip duplicate, continue processing
except Exception as e:
    logger.error(f"Database error: {e}")
    # Fallback to session state cache
```

### Delta Calculation Errors
```python
def safe_calculate_delta(S, K, T, r, sigma):
    """Calculate delta with error handling"""
    try:
        if T <= 0 or sigma <= 0:
            return None
        delta = calculate_delta(S, K, T, r, sigma, 'put')
        return delta if -1 <= delta <= 0 else None
    except Exception as e:
        logger.error(f"Delta calculation error: {e}")
        return None
```

## Performance Considerations

### Optimization Strategies
1. **Parallel Processing**: Process multiple symbols concurrently
2. **Caching**: 15-minute cache for stock prices and options chains
3. **Database First**: Query pre-computed data for instant results
4. **Batch Processing**: Group API calls to reduce overhead
5. **Lazy Calculation**: Calculate Greeks only for displayed results
6. **Materialized Views**: Pre-aggregate common queries

### Performance Metrics
| Operation | Target | Current |
|-----------|--------|---------|
| Single symbol (all DTEs) | < 3s | ~2.5s |
| 10 symbols | < 30s | ~25s |
| 100 symbols | < 5min | ~3-4min |
| Database query | < 200ms | ~150ms |
| Background sync (10 symbols) | < 60s | ~45s |
| Delta calculation | < 10ms | ~5ms |

### Resource Usage
- **Memory**: 200-500MB for full scan
- **CPU**: Moderate (Black-Scholes calculations)
- **Network**: 10-50MB per scan
- **Database**: ~100MB for complete dataset
- **Disk I/O**: Minimal (efficient upserts)

## Testing Checklist

### Before Deployment
- [ ] Multi-expiration fetching works for all 6 DTEs
- [ ] Delta calculations match Bloomberg/ThinkorSwim values ±0.01
- [ ] Delta filtering correctly excludes out-of-range options
- [ ] Liquidity validation removes low-volume options
- [ ] Return calculations verified against manual spreadsheet
- [ ] Database upserts handle duplicates correctly
- [ ] Background sync completes without errors
- [ ] TradingView watchlist import works
- [ ] Database scanner returns accurate results
- [ ] Greeks display correctly when available
- [ ] No crashes with missing data
- [ ] No crashes with 500+ symbols
- [ ] CSV export includes all columns

### Integration Tests
- [ ] Robinhood authentication persists across scans
- [ ] Database connection pool handles concurrent requests
- [ ] Background sync doesn't block UI
- [ ] TradingView symbols sync correctly
- [ ] Polygon API fallback works when Robinhood fails
- [ ] Cache invalidation works on manual refresh

## Maintenance

### When to Update This Agent

1. **User Request**: "Add gamma filtering"
   - Enhance filtering logic to include gamma range
   - Add UI controls for gamma min/max
   - Update database queries
   - Document in CHANGELOG.md

2. **Bug Report**: "Delta calculations off for deep OTM options"
   - Review Black-Scholes implementation
   - Check edge cases (T→0, σ→0)
   - Verify risk-free rate accuracy
   - Add unit tests for edge cases
   - Document fix in CHANGELOG.md

3. **Feature Request**: "Support multiple delta ranges simultaneously"
   - Redesign filtering to handle multiple ranges
   - Update UI for range selection
   - Optimize database queries
   - Update SPEC.md

4. **API Change**: Robinhood API updates Greeks format
   - Update parsing logic in enhanced_options_fetcher.py
   - Verify all Greek calculations still work
   - Test backward compatibility
   - Document breaking changes
   - Alert users via CHANGELOG.md

### Monitoring
- Check background sync success rate (> 95%)
- Monitor database growth (alert if > 10GB)
- Track scan completion times (flag if > 2x normal)
- Review delta calculation accuracy (spot check)
- Monitor API error rates by source
- Track cache hit rates for performance

## Integration Points

### Robinhood Integration
```python
# Login and session management
rh.login(username, password, expiresIn=86400, store_session=True)

# Fetch options chain
chain_data = rh.options.find_options_for_stock_by_expiration(
    symbol,
    expirationDate=expiry_date,
    optionType='put'
)

# Get Greeks
greeks = chain_data[0].get('greeks', {})
delta = greeks.get('delta')
```

### Database Integration
```python
# Upsert premium data
INSERT INTO stock_premiums (
    symbol, expiration_date, strike_price, dte, premium,
    delta, gamma, theta, vega, implied_volatility,
    volume, open_interest, monthly_return, annual_return
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (symbol, expiration_date, strike_price)
DO UPDATE SET
    premium = EXCLUDED.premium,
    delta = EXCLUDED.delta,
    updated_at = CURRENT_TIMESTAMP;
```

### TradingView Integration
```python
from tradingview_watchlist import TradingViewWatchlist

tv = TradingViewWatchlist()
tv.login(username, password)
symbols = tv.get_watchlist_symbols()
# Returns list of symbols for scanning
```

## Future Enhancements

### Planned Features
- **Real-Time Updates**: WebSocket integration for live Greeks
- **Advanced Filtering UI**: Multi-dimensional sliders and filters
- **Machine Learning**: Predict optimal strike selection
- **Portfolio Optimization**: Suggest diversified opportunity mix
- **Earnings Integration**: Automatic filtering around earnings dates
- **Dividend Adjustment**: Account for dividends in delta calculations
- **International Markets**: Support non-US equities
- **Options Strategies**: Expand beyond CSP (verticals, iron condors)
- **Mobile App**: Native iOS/Android with push notifications
- **API Access**: RESTful API for programmatic access

### Technical Improvements
- Implement Redis caching for 10x performance boost
- Add WebSocket streaming for real-time updates
- Optimize database with partitioning by expiration
- Implement distributed processing with Celery workers
- Add comprehensive unit test suite (> 80% coverage)
- Create integration test framework with mock APIs
- Implement GraphQL API layer
- Add Prometheus metrics and Grafana dashboards

## Questions This Agent Can Answer

1. "What options are available across all expirations for AAPL?"
2. "Show me CSP opportunities with delta between 0.25 and 0.35"
3. "Which symbols have the highest monthly returns for 30 DTE?"
4. "What's the delta for this specific strike and expiration?"
5. "Compare premiums across different expirations for the same symbol"
6. "Which options have sufficient liquidity (volume > 100)?"
7. "What's the implied volatility for these options?"
8. "Show me all Greeks for this option"
9. "What's my probability of profit based on delta?"
10. "Which expiration offers the best risk/reward ratio?"
11. "How do premiums compare between weekly and monthly options?"
12. "What's stored in the database for my watchlist?"
13. "When was this premium data last updated?"
14. "What's the bid-ask spread on this option?"
15. "How much capital is required for each opportunity?"

## Questions This Agent CANNOT Answer

1. "What are my current positions?" → Positions Agent
2. "Should I close this trade?" → Positions Agent (AI analysis)
3. "When is the next earnings date?" → Earnings Calendar Agent
4. "What's the best calendar spread?" → Calendar Spreads Agent
5. "Change my Robinhood password" → Settings Agent
6. "What's the market sentiment?" → Prediction Markets Agent
7. "Execute this trade" → User must use broker
8. "Will this be profitable?" → Cannot predict (shows probabilities)
9. "What's my account balance?" → Dashboard Agent
10. "Sync my watchlist now" → Background service (not interactive)

---

**For detailed architecture and specifications, see:**
- [ARCHITECTURE.md](./ARCHITECTURE.md)
- [SPEC.md](./SPEC.md)
- [README.md](./README.md)

**For current tasks and planned work, see:**
- [TODO.md](./TODO.md) (if exists)
- [WISHLIST.md](./WISHLIST.md)
- [CHANGELOG.md](./CHANGELOG.md) (if exists)
