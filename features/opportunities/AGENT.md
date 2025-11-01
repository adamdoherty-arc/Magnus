# Opportunities Feature Agent

## Agent Identity

- **Feature Name**: Opportunities
- **Agent Version**: 1.0.0
- **Feature Version**: 1.0.0
- **Last Updated**: 2025-11-01
- **Owner**: Magnus Platform
- **Status**: ✅ Active & Production Ready

## Role & Responsibilities

The Opportunities Agent is responsible for **automated options discovery and market scanning** to identify optimal cash-secured put (CSP) opportunities for the wheel strategy. It serves as the intelligent assistant that automates hours of manual research into seconds of systematic analysis.

### Primary Responsibilities
1. Scan multiple stocks simultaneously for premium opportunities
2. Analyze options chains across different expiration dates
3. Calculate risk-adjusted returns and annualized projections
4. Filter opportunities by liquidity (volume, open interest)
5. Rank opportunities by multiple criteria (return, risk, efficiency)
6. Apply delta-based probability filtering
7. Provide pre-configured scanning strategies for different risk profiles
8. Display comprehensive opportunity analysis with all key metrics

### Data Sources
- **Yahoo Finance (yfinance)**: Primary source for option chains and stock prices
- **Robinhood API**: Secondary source for options data and verification
- **TradingView Watchlists**: Symbol lists for scanning
- **Database**: Pre-loaded stock universe and historical data
- **Local Calculations**: Greeks, returns, risk metrics, scoring algorithms

## Feature Capabilities

### What This Agent CAN Do
- ✅ Scan 100+ stocks for CSP opportunities in under 60 seconds
- ✅ Analyze multiple expiration dates simultaneously (7, 14, 21, 30, 45 DTE)
- ✅ Calculate premium percentages and annualized returns
- ✅ Filter by delta range (target 0.20-0.40 for optimal risk/reward)
- ✅ Validate liquidity (minimum volume and open interest thresholds)
- ✅ Rank opportunities by monthly/annual return potential
- ✅ Apply pre-configured strategies (Best Overall, High IV, Weekly, Monthly)
- ✅ Filter by maximum stock price for capital management
- ✅ Display bid-ask spreads and trading costs
- ✅ Calculate implied volatility rankings
- ✅ Show assignment probabilities based on delta
- ✅ Provide detailed analysis for top opportunities
- ✅ Export results to CSV for record keeping

### What This Agent CANNOT Do
- ❌ Execute trades (requires user action + broker interface)
- ❌ Track active positions (that's Positions Agent's role)
- ❌ Provide real-time price updates (uses 15-min delayed data)
- ❌ Store scan history automatically (unless saved to database)
- ❌ Predict earnings dates (that's Earnings Calendar Agent)
- ❌ Analyze calendar spreads (that's Calendar Spreads Agent)
- ❌ Change risk parameters globally (that's Settings Agent)
- ❌ Guarantee profitability (provides analysis, not recommendations)

## Dependencies

### Required Features
- **Yahoo Finance API**: For options chains and stock prices (free tier)
- **Symbol Lists**: From TradingView watchlists or database

### Optional Features
- **TradingView Watchlists Agent**: For curated symbol lists
- **Database Scanner Agent**: For stored premium data
- **Earnings Calendar Agent**: For earnings date filtering
- **Robinhood Integration**: For alternative options data source

### External APIs
- **Yahoo Finance (yfinance)**: Primary data provider
  - Options chains for all expirations
  - Stock quotes and basic company info
  - No authentication required, rate limited
- **Robinhood API**: Secondary/verification source
  - Options data with Greeks
  - Real-time quotes (requires login)

### Database Tables
- `opportunities` (optional): Stored scan results
- `stock_data`: Stock information and pricing
- `stock_premiums`: Options data for database scanning

## Key Files & Code

### Main Implementation
- `dashboard.py`: Lines 1122-1292 (Premium Scanner UI and orchestration)
- `src/premium_scanner.py`: Lines 9-203 (Core scanning engine)
- `src/tradingview_watchlist.py`: Watchlist integration and symbol management
- `src/enhanced_options_fetcher.py`: Options data retrieval with Greeks

### Critical Functions
```python
# Core Scanning (src/premium_scanner.py)
def scan_premiums(symbols, max_price, min_premium_pct, dte):
    """
    Main scanning orchestration
    - Filters symbols by price
    - Fetches options chains
    - Calculates returns
    - Applies liquidity filters
    - Ranks and returns results
    """

# Premium Calculation
def calculate_premium_metrics(put_option, strike, dte):
    """
    Calculates return metrics:
    - Premium percentage
    - Monthly return (normalized to 30 days)
    - Annual return (extrapolated)
    - Capital efficiency
    """

# Liquidity Validation
def validate_liquidity(volume, open_interest, bid, ask):
    """
    Ensures tradeable opportunities:
    - Minimum volume threshold (default 100)
    - Minimum open interest (default 50)
    - Acceptable bid-ask spread (<10% of mid)
    """

# Delta Calculation (enhanced_options_fetcher.py)
def calculate_delta(S, K, T, r, sigma, option_type='put'):
    """
    Black-Scholes delta for probability estimation
    """

# Opportunity Scoring
def calculate_opportunity_score(opportunity):
    """
    Multi-factor scoring:
    - Return metrics (40% weight)
    - Liquidity (30% weight)
    - Risk assessment (20% weight)
    - Time efficiency (10% weight)
    """
```

### Strategy Configurations
```python
STRATEGIES = {
    'Best Overall Premiums': {
        'max_price': 50,
        'min_premium_pct': 1.0,
        'target_dte': 30,
        'filters': 'balanced'
    },
    'High IV Plays (40%+)': {
        'max_price': 50,
        'min_premium_pct': 1.5,
        'min_iv': 40,
        'target_dte': 30
    },
    'Weekly Options (7-14 DTE)': {
        'max_price': 50,
        'min_premium_pct': 0.5,
        'target_dte': [7, 14]
    },
    'Monthly Options (30-45 DTE)': {
        'max_price': 50,
        'min_premium_pct': 1.0,
        'target_dte': [30, 45]
    }
}
```

## Current State

### Implemented Features
✅ Multi-stock scanning with parallel processing
✅ Multiple expiration date analysis
✅ Premium percentage and return calculations
✅ Delta-based filtering for probability management
✅ Liquidity validation (volume/OI thresholds)
✅ Pre-configured strategy templates
✅ Detailed top-5 opportunity analysis
✅ Summary metrics (average premium %, returns)
✅ Sortable results table
✅ Filter controls (price, premium %, DTE)
✅ Implied volatility display
✅ Annualized return projections
✅ CSV export functionality

### Known Limitations
⚠️ Uses 15-minute delayed data (Yahoo Finance free tier)
⚠️ No automatic earnings date filtering (requires manual check)
⚠️ Scanning 100+ symbols takes 2-3 minutes
⚠️ No real-time price updates during scan
⚠️ Limited to US equities (no international markets)
⚠️ Delta calculations use simplified Black-Scholes (no dividend adjustment)
⚠️ No historical performance tracking of recommendations

### Recent Changes
- Enhanced options fetcher with multi-expiration support
- Improved liquidity filtering with configurable thresholds
- Added strategy templates for different risk profiles
- Optimized scanning performance with caching
- Added detailed analysis for top opportunities

## Communication Patterns

### Incoming Requests

#### From Main Agent
```yaml
Request: "Find best CSP opportunities under $50"
Response:
  - Loads watchlist or default symbols
  - Scans for options meeting criteria
  - Returns ranked list of opportunities
```

#### From User
```yaml
Request: "Scan for weekly options with high IV"
Response:
  - Applies High IV strategy filter
  - Targets 7-14 DTE expirations
  - Returns opportunities with IV > 40%
  - Sorted by monthly return
```

### Outgoing Requests

#### To Yahoo Finance API
```yaml
Request: "Get option chain for {symbol} expiring {date}"
Purpose: Fetch all put options for analysis
Expected Response:
  - Strike prices
  - Bid/ask prices
  - Volume and open interest
  - Implied volatility
  - Last trade price
```

#### To TradingView Watchlists Agent
```yaml
Request: "Get symbols from watchlist"
Purpose: Load curated symbol list for scanning
Expected Response:
  - List of stock tickers
  - Filtered for stocks only (no crypto/forex)
```

## Data Flow

```
User Selects Strategy
       ↓
Load Symbol Universe
  - TradingView Watchlists
  - Database Stocks
  - Manual Input
       ↓
Apply Price Filter
  - Remove stocks > max_price
       ↓
For Each Symbol:
  ├─→ Fetch Current Stock Price
  ├─→ Get Options Chain (target DTE)
  ├─→ Filter Puts Only
  └─→ For Each Put Strike:
      ├─→ Check Liquidity (volume/OI)
      ├─→ Calculate Premium Metrics
      ├─→ Calculate Delta (if available)
      └─→ Score Opportunity
       ↓
Aggregate Results
  - Remove duplicates
  - Apply minimum premium filter
       ↓
Rank Opportunities
  - Sort by monthly return (primary)
  - Sort by premium % (secondary)
       ↓
Calculate Summary Metrics
  - Average premium %
  - Average monthly return
  - Average annual return
       ↓
Display Results
  - Summary cards
  - Top 5 detailed analysis
  - Full sortable table
  - Export option
```

## Error Handling

### API Failure (Yahoo Finance)
```python
try:
    ticker = yf.Ticker(symbol)
    options = ticker.option_chain(expiry_date)
except Exception as e:
    logger.error(f"Failed to fetch options for {symbol}: {e}")
    continue  # Skip to next symbol
```

### No Options Available
```python
if not options or len(options.puts) == 0:
    logger.warning(f"No options available for {symbol}")
    continue  # Skip symbol
```

### Rate Limiting
```python
if "Too many requests" in str(error):
    logger.warning("Rate limit hit, waiting 60 seconds")
    time.sleep(60)
    retry_fetch()
```

### Invalid Symbol
```python
def validate_symbol(symbol):
    """Ensure symbol is valid and options-eligible"""
    if not symbol or len(symbol) > 5:
        return False
    # Additional validation...
    return True
```

## Performance Considerations

### Optimization Strategies
- **Parallel Processing**: Can process multiple symbols concurrently
- **Caching**: Cache stock prices and options chains (5-min TTL)
- **Batch Requests**: Group API calls where possible
- **Early Filtering**: Eliminate ineligible symbols before fetching options
- **Lazy Loading**: Load detailed analysis only for top results

### Performance Metrics
| Operation | Target | Current |
|-----------|--------|---------|
| Single symbol scan | < 2s | ~2s |
| 10 symbol scan | < 20s | ~18s |
| 100 symbol scan | < 3min | ~2.5min |
| Results rendering | < 1s | ~800ms |
| Strategy switch | < 100ms | ~50ms |

### Resource Usage
- **Memory**: ~200MB for 100-symbol scan
- **CPU**: Moderate during calculations
- **Network**: ~10-50MB per full scan
- **API Calls**: ~2-5 per symbol (quotes + options)

## Testing Checklist

### Before Deployment
- [ ] Scan completes successfully with default strategy
- [ ] All 6 strategies return valid results
- [ ] Premium calculations match manual verification
- [ ] Liquidity filtering removes low-volume options
- [ ] Delta calculations are within reasonable ranges
- [ ] Summary metrics calculate correctly
- [ ] Top 5 detailed view displays all metrics
- [ ] Sort functionality works on all columns
- [ ] Export to CSV includes all data
- [ ] No crashes with zero results
- [ ] No crashes with 500+ results
- [ ] Error handling for invalid symbols

### Integration Tests
- [ ] TradingView watchlist integration works
- [ ] Database symbol loading functions correctly
- [ ] Yahoo Finance API handles rate limits
- [ ] Results persist in session state
- [ ] Filter changes update results immediately

## Maintenance

### When to Update This Agent

1. **User Request**: "Add filtering by sector/industry"
   - Enhance symbol loading with sector metadata
   - Add sector filter to UI controls
   - Update scanning logic to apply sector filter
   - Document in CHANGELOG.md

2. **Bug Report**: "Returns calculation incorrect for weekly options"
   - Debug calculate_returns() function
   - Verify DTE normalization logic
   - Fix annualization formula if needed
   - Add unit tests for edge cases
   - Document fix in CHANGELOG.md

3. **Feature Request**: "Include earnings date warnings"
   - Integrate with Earnings Calendar Agent
   - Add earnings date to opportunity data
   - Display warning for options expiring near earnings
   - Update SPEC.md and TODO.md

4. **API Change**: Yahoo Finance rate limits tightened
   - Implement more aggressive caching
   - Add backoff/retry logic
   - Consider alternative data sources
   - Alert users of potential delays
   - Document in CHANGELOG.md

### Monitoring
- Check scan completion rates (should be > 95%)
- Monitor average scan duration (track degradation)
- Track API error rates by source
- Review opportunity quality (user feedback)
- Monitor cache hit rates for performance

## Integration Points

### Yahoo Finance Integration
```python
import yfinance as yf

# Get stock quote
ticker = yf.Ticker(symbol)
info = ticker.info
current_price = info.get('regularMarketPrice')

# Get options chain
expirations = ticker.options
chain = ticker.option_chain(expiry_date)
puts = chain.puts  # DataFrame of all put options
```

### TradingView Watchlists
```python
from tradingview_watchlist import TradingViewWatchlist

tv = TradingViewWatchlist()
symbols = tv.get_watchlist_symbols_simple()
# Returns: ['AAPL', 'MSFT', ...] filtered for stocks only
```

### Database Scanner
```python
from database_scanner import DatabaseScanner

scanner = DatabaseScanner()
results = scanner.scan_stored_premiums(filters={
    'max_price': 50,
    'min_premium_pct': 1.0,
    'target_dte': 30
})
# Returns pre-computed opportunities from database
```

## Future Enhancements

### Planned Features (WISHLIST.md)
- **Real-Time Data**: WebSocket integration for live prices during scan
- **Earnings Filtering**: Automatic exclusion of options near earnings
- **Sector Analysis**: Group opportunities by sector/industry
- **Historical Performance**: Track recommendation success rate
- **Advanced Greeks**: Display full Greeks (gamma, theta, vega) for each opportunity
- **Custom Strategies**: User-defined scanning criteria and saved templates
- **Alert System**: Notify when new high-quality opportunities appear
- **Multi-Timeframe Comparison**: Side-by-side analysis of weekly vs monthly
- **Portfolio Optimization**: Suggest diversified opportunity mix
- **Backtesting**: Historical performance of scanning strategies

### Technical Improvements
- Implement caching layer (Redis) for faster rescans
- Add parallel processing for 10x scan speed improvement
- Create materialized views for database-first scanning
- Optimize Greek calculations with vectorization
- Add comprehensive unit test coverage
- Implement integration tests with mock APIs

## Questions This Agent Can Answer

1. "What are the best CSP opportunities right now?"
2. "Which stocks under $50 have the highest premium percentages?"
3. "Show me weekly options with good returns"
4. "What opportunities exist for monthly expirations?"
5. "Which high IV stocks are worth selling puts on?"
6. "What's the expected annual return for these opportunities?"
7. "Are there any liquid options on this stock?"
8. "What's the delta/assignment probability for this trade?"
9. "Compare premium opportunities across different expirations"
10. "Which opportunities have the best risk/reward ratio?"
11. "What stocks in my watchlist have good premiums?"
12. "Show me conservative opportunities with low assignment risk"
13. "What's the bid-ask spread on these options?"
14. "How much capital is required for each opportunity?"
15. "Which opportunities meet my return targets?"

## Questions This Agent CANNOT Answer

1. "What are my current positions?" → Positions Agent
2. "Should I close my existing trades?" → Positions Agent (AI analysis)
3. "When is the next earnings date?" → Earnings Calendar Agent
4. "Set up auto-scanning every hour" → Settings Agent
5. "Show me calendar spread opportunities" → Calendar Spreads Agent
6. "What's the market sentiment?" → Prediction Markets Agent
7. "Execute this trade for me" → User must use broker
8. "What's my account balance?" → Dashboard Agent
9. "Show my trade history" → Dashboard Agent
10. "Will this trade be profitable?" → Cannot predict future (shows probabilities only)

---

**For detailed architecture and specifications, see:**
- [ARCHITECTURE.md](./ARCHITECTURE.md)
- [SPEC.md](./SPEC.md)
- [README.md](./README.md)

**For current tasks and planned work, see:**
- [TODO.md](./TODO.md) (if exists)
- [WISHLIST.md](./WISHLIST.md) (if exists)
- [CHANGELOG.md](./CHANGELOG.md) (if exists)
