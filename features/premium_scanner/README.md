# Premium Scanner Feature

## Executive Summary

The Premium Scanner is a sophisticated options analysis system that identifies high-return cash-secured put (CSP) opportunities across multiple expiration dates. By analyzing options chains for 7, 14, 21, 30, 45, and 60-day expirations simultaneously, the scanner helps traders maximize premium income while managing risk through delta-based probability filtering.

## Overview

The Premium Scanner feature represents the core intelligence of the Wheel Strategy application, providing automated discovery and ranking of optimal premium-generating opportunities. It combines real-time market data from multiple sources (Robinhood, Polygon, Yahoo Finance) with advanced Greek calculations to present a comprehensive view of the options market.

### Key Capabilities

- **Multi-Expiration Analysis**: Simultaneous scanning of 6 different expiration periods (7, 14, 21, 30, 45, 60 DTE)
- **Delta-Based Filtering**: Focus on 0.20-0.40 delta range for optimal risk/reward balance
- **Premium Optimization**: Automatic ranking by monthly and annual return percentages
- **Liquidity Validation**: Volume and open interest thresholds ensure tradeable options
- **Real-Time Sync**: Background process updates prices and premiums continuously
- **Watchlist Integration**: Seamless connection with TradingView watchlists

## How It Works

### 1. Data Collection Pipeline

The scanner operates through a multi-stage data collection process:

```
TradingView Watchlists → Symbol Collection → Price Fetching → Options Chain Analysis → Greek Calculation → Database Storage
```

#### Symbol Sources
- **TradingView Integration**: Imports user watchlists via API
- **Database Stocks**: Pre-loaded universe of ~1,200 stocks
- **Manual Import**: Text/CSV input for custom lists
- **Robinhood Portfolio**: Current positions and watchlists

#### Data Providers
- **Stock Prices**: Polygon API (primary), Yahoo Finance (fallback)
- **Options Chains**: Robinhood API (free, unlimited)
- **Greeks Calculation**: Black-Scholes model implementation
- **IV Data**: Market data from options chains

### 2. Multi-Expiration Scanning Logic

The core innovation of the Premium Scanner is its ability to analyze multiple expiration dates simultaneously:

```python
TARGET_DTES = [7, 14, 21, 30, 45, 60]  # Days to expiration

For each symbol:
  For each target DTE:
    1. Find closest available expiration
    2. Get all puts for that expiration
    3. Calculate delta for each strike
    4. Filter to 0.20-0.40 delta range
    5. Select best premium/return combination
    6. Store in database with metrics
```

### 3. Delta Filtering Algorithm

Delta represents the probability that an option will expire in-the-money. The scanner targets the "sweet spot" of 0.20-0.40 delta (20-40% probability of assignment):

- **0.20 Delta**: 80% probability of keeping premium (lower premium, higher win rate)
- **0.30 Delta**: 70% probability of keeping premium (balanced approach)
- **0.40 Delta**: 60% probability of keeping premium (higher premium, more assignments)

### 4. Premium Optimization

The scanner calculates multiple return metrics for each option:

```
Premium Return % = (Premium / Strike Price) × 100
Monthly Return % = (Premium Return % / DTE) × 30
Annual Return % = Monthly Return % × 12
```

Options are then ranked by:
1. **Monthly Return %** (primary sort)
2. **Premium Amount** (secondary sort)
3. **Liquidity** (volume/OI threshold)

## User Interface

### Main Scanner Page (`dashboard.py` lines 1122-1292)

The UI provides three main interaction modes:

#### 1. Quick Scan Strategies
- **Best Overall Premiums**: All qualifying options sorted by return
- **High IV Plays (40%+)**: Focus on high volatility opportunities
- **Weekly Options (7-14 DTE)**: Short-term income generation
- **Monthly Options (30-45 DTE)**: Traditional monthly cycle
- **Tech Stocks Under $50**: Sector-specific scanning
- **All Stocks Under $50**: Comprehensive market scan

#### 2. Filter Controls
- **Max Stock Price**: Capital requirement limit
- **Min Premium %**: Return threshold
- **Target DTE**: Specific expiration targeting
- **Delta Range**: Risk tolerance adjustment

#### 3. Results Display
- **Summary Metrics**: Average premium %, monthly return, annual return
- **Sortable Table**: All opportunities with key metrics
- **Detailed Analysis**: Top 5 opportunities with expanded data
- **Trade Integration**: Direct links to broker execution

### Database Scanner Integration (`dashboard.py` lines 2019-2218)

The Database Scanner tab provides:
- Access to all stored options data
- Historical premium tracking
- Cross-expiration comparison
- Bulk analysis capabilities

### TradingView Watchlists Integration (`dashboard.py` lines 1293-1899)

Watchlist features include:
- **Auto-sync** with TradingView accounts
- **Background updates** for real-time data
- **Batch processing** of multiple watchlists
- **Symbol filtering** (stocks only, no crypto)

## Technical Implementation

### Core Components

#### 1. `PremiumScanner` Class (`src/premium_scanner.py`)
Primary scanner implementation with:
- `scan_premiums()`: Main scanning method
- `find_assignment_candidates()`: ITM position detection
- Liquidity filtering (min volume: 100, min OI: 50)

#### 2. `EnhancedOptionsFetcher` Class (`src/enhanced_options_fetcher.py`)
Advanced options data retrieval:
- `get_all_expirations_data()`: Multi-expiration fetching
- `calculate_delta()`: Black-Scholes delta calculation
- Robinhood API integration
- Greeks computation

#### 3. `WatchlistSyncService` (`src/watchlist_sync_service.py`)
Background synchronization:
- Batch processing of symbols
- Parallel data fetching
- Database updates
- Error recovery

#### 4. `DatabaseScanner` (`src/database_scanner.py`)
Database operations:
- PostgreSQL integration
- Optimized queries
- Data caching
- Performance monitoring

### Database Schema

```sql
-- Main options data table
CREATE TABLE stock_premiums (
    symbol VARCHAR(10),
    expiration_date DATE,
    strike_price DECIMAL(10,2),
    dte INTEGER,
    premium DECIMAL(10,2),
    delta DECIMAL(5,4),
    monthly_return DECIMAL(10,2),
    implied_volatility DECIMAL(5,2),
    bid DECIMAL(10,2),
    ask DECIMAL(10,2),
    volume INTEGER,
    open_interest INTEGER,
    updated_at TIMESTAMP,
    UNIQUE(symbol, expiration_date, strike_price)
);

-- Stock data table
CREATE TABLE stock_data (
    symbol VARCHAR(10) PRIMARY KEY,
    current_price DECIMAL(10,2),
    volume BIGINT,
    market_cap BIGINT,
    updated_at TIMESTAMP
);
```

## Performance Characteristics

### Scanning Speed
- **Single Symbol**: ~2-3 seconds (all expirations)
- **10 Symbols**: ~20-30 seconds
- **100 Symbols**: ~3-5 minutes (with caching)
- **Full Database**: ~15-20 minutes (background sync)

### Data Freshness
- **Stock Prices**: Real-time during market hours
- **Options Data**: 15-minute delayed (Robinhood free tier)
- **Greeks**: Calculated on-demand
- **Database Cache**: 15-minute TTL

### Resource Usage
- **Memory**: ~200-500MB for full scan
- **CPU**: Moderate (Black-Scholes calculations)
- **Network**: ~10-50MB per full scan
- **Database**: ~100MB for complete dataset

## Configuration

### Environment Variables
```bash
# Required for data sources
POLYGON_API_KEY=your_polygon_key
ROBINHOOD_USERNAME=your_username
ROBINHOOD_PASSWORD=your_password
TRADINGVIEW_USERNAME=your_tv_username
TRADINGVIEW_PASSWORD=your_tv_password

# Database connection
DATABASE_URL=postgresql://user:pass@host:port/dbname

# Optional settings
MIN_OPTION_VOLUME=100
MIN_OPEN_INTEREST=50
DEFAULT_RISK_FREE_RATE=0.045
```

### Tunable Parameters
```python
# In premium_scanner.py
MIN_VOLUME = 100        # Minimum option volume
MIN_OI = 50            # Minimum open interest
MAX_PRICE = 50         # Default max stock price
MIN_PREMIUM_PCT = 1.0  # Minimum premium percentage

# In enhanced_options_fetcher.py
TARGET_DTES = [7, 14, 21, 30, 45]  # Expiration targets
DELTA_RANGE = (0.20, 0.40)         # Delta filter range
RISK_FREE_RATE = 0.045             # For Greeks calculation
```

## Best Practices

### 1. Optimal Scanning Strategy
- Start with 30-day options for baseline
- Compare weekly (7-14 DTE) for higher turnover
- Use 45-60 DTE for more conservative approach
- Always check liquidity (volume > 100)

### 2. Delta Selection Guidelines
- **Conservative**: 0.20-0.25 delta (80% win rate)
- **Balanced**: 0.25-0.35 delta (70% win rate)
- **Aggressive**: 0.35-0.40 delta (60% win rate)
- Avoid > 0.40 delta unless seeking assignment

### 3. Premium Filtering
- **Minimum 1% monthly**: Basic threshold
- **Target 2-3% monthly**: Optimal range
- **> 5% monthly**: High risk, verify IV/earnings
- Consider annualized returns (12-36% target)

### 4. Risk Management
- Diversify across sectors
- Limit position size to 5% of capital
- Keep 50% cash for assignments
- Monitor earnings dates

## Common Use Cases

### 1. Weekly Income Generation
Focus on 7-14 DTE options with:
- Higher delta (0.35-0.40) for premium
- Liquid weekly chains (SPY, QQQ, major stocks)
- Quick turnover strategy

### 2. Monthly Premium Collection
Traditional 30-45 DTE approach:
- Balanced delta (0.25-0.35)
- Monthly expiration cycles
- Time decay optimization

### 3. High IV Harvesting
Target volatility spikes:
- Filter IV > 40%
- Earnings plays (with caution)
- Event-driven opportunities

### 4. Assignment Preparation
When seeking stock ownership:
- Higher delta (0.40-0.50)
- Quality companies only
- Plan for covered call transition

## Troubleshooting

### Common Issues

#### 1. No Options Found
- **Cause**: Symbol has no options or insufficient liquidity
- **Solution**: Check major stocks, verify market hours

#### 2. Slow Scanning
- **Cause**: Rate limiting or network issues
- **Solution**: Reduce batch size, use background sync

#### 3. Stale Data
- **Cause**: Cache not refreshing
- **Solution**: Click "Sync Prices & Premiums" button

#### 4. Missing Expirations
- **Cause**: No options chain for target DTE
- **Solution**: Scanner auto-selects nearest available

### Data Validation

Always verify:
- Current stock price accuracy
- Bid/ask spreads reasonable
- Volume/OI sufficient for exit
- Delta calculations sensible

## Integration Points

### 1. TradingView Watchlists
- Automatic symbol import
- Watchlist categorization
- Real-time sync capability

### 2. Robinhood Execution
- Direct option chain access
- Position monitoring
- Order preparation

### 3. Database Storage
- PostgreSQL for persistence
- Historical tracking
- Performance analytics

### 4. Background Services
- `watchlist_sync_service.py`: Continuous updates
- `enhanced_options_fetcher.py`: Options data
- Process management via subprocess

## Security Considerations

### API Credentials
- Store in `.env` file (never commit)
- Use environment variables
- Implement token refresh

### Data Privacy
- No sensitive data in logs
- Secure database connections
- Encrypted credential storage

### Rate Limiting
- Respect API limits
- Implement exponential backoff
- Use caching strategically

## Future Enhancements

See [WISHLIST.md](WISHLIST.md) for detailed roadmap including:
- Real-time Greeks updates
- Advanced filtering UI
- Machine learning predictions
- Portfolio optimization
- Mobile app integration

## Related Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) - System design and data flow
- [SPEC.md](SPEC.md) - Technical specifications
- [WISHLIST.md](WISHLIST.md) - Future improvements
- [Database Schema](../database_scan/ARCHITECTURE.md) - Data structure details

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review error logs in console
3. Verify API credentials
4. Ensure database connectivity

---

*Last Updated: October 2024*
*Version: 2.0.0*