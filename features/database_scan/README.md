# Database Scan Feature

## Overview

The Database Scan feature is a comprehensive stock options scanner that provides access to the entire universe of stocks stored in the PostgreSQL database. Unlike the TradingView Watchlists feature which focuses on curated lists, Database Scan enables users to discover high-yield cash-secured put opportunities across all 1,205+ stocks in the system.

## Purpose

The Database Scan feature serves as the primary discovery tool for options traders implementing the wheel strategy. It addresses the fundamental need to:

1. **Discover Opportunities**: Find the best premium-generating stocks across the entire market
2. **Filter Efficiently**: Apply sophisticated filters to narrow down thousands of stocks
3. **Analyze Options**: View real-time options data with focus on 30-day puts with delta 0.25-0.40
4. **Sync Data**: Keep options pricing current for the entire stock universe

## Key Capabilities

### 1. Complete Market Coverage
- Access to all 1,205 stocks in the PostgreSQL database
- No limitation to predefined watchlists
- Full market scan capability for discovering new opportunities

### 2. Options Premium Analysis
- Real-time options chain data for 30-day expirations
- Focus on cash-secured puts with delta range 0.25-0.40
- Monthly return percentage calculations
- Implied volatility (IV) metrics

### 3. Advanced Filtering
- **Price Range**: Min/max stock price filters
- **Premium Threshold**: Minimum premium requirements
- **Days to Expiration (DTE)**: Flexible expiration targeting
- **Delta Range**: Built-in safety with 0.25-0.40 delta filter

### 4. Data Synchronization
- One-click sync for all database stocks
- Background processing for 1,000+ symbols
- Automatic options chain updates
- Progress tracking and status monitoring

## User Interface

The Database Scan feature is organized into four distinct tabs:

### Tab 1: Database Overview
- Total stock count and statistics
- Sector distribution visualization
- Price range distribution
- Quick access to update all stock prices

### Tab 2: Add Stocks
- Manual stock addition interface
- Bulk import capability
- Yahoo Finance data integration
- Automatic sector and market cap retrieval

### Tab 3: Scan Premiums (Primary Interface)
- **Main scanning interface** showing all stocks with options
- Sortable columns for all metrics
- Real-time filtering controls
- Summary statistics (options found, average premium, average return)
- Interactive data table with formatting

### Tab 4: Analytics
- Database-wide statistics
- Sector performance analysis
- Price distribution charts
- Market overview metrics

## Core Functionality

### Data Flow
1. **Source**: PostgreSQL `stocks` table (1,205 stocks)
2. **Options Data**: `stock_premiums` table with synced options
3. **Enrichment**: Real-time data from `stock_data` table
4. **Presentation**: Formatted, sortable table with color coding

### Key Metrics Displayed
- **Symbol**: Stock ticker
- **Stock Price**: Current market price
- **Strike**: Put option strike price
- **DTE**: Days to expiration
- **Premium**: Option premium in dollars
- **Delta**: Option delta (risk metric)
- **Monthly %**: Annualized return percentage
- **IV**: Implied volatility percentage
- **Bid/Ask**: Current market quotes
- **Volume**: Daily trading volume
- **Open Interest**: Total open contracts
- **Name**: Company name
- **Sector**: Industry sector classification

## Integration Points

### Database Tables
- `stocks`: Master list of all tradeable stocks
- `stock_premiums`: Options chain data with Greeks
- `stock_data`: Real-time price and volume data
- `tv_watchlists`: Integration with watchlist system

### Services
- `DatabaseScanner`: Core scanning engine
- `TradingViewDBManager`: Database interface layer
- `watchlist_sync_service`: Background sync processor

## Usage Workflow

### Typical User Journey

1. **Initial Discovery**
   - Navigate to Database Scan from sidebar
   - View Database Overview for market snapshot
   - Check current sync status

2. **Data Synchronization**
   - Click "Sync All Database Stocks" button
   - Monitor background sync progress (10-15 minutes)
   - Verify increased stock count post-sync

3. **Premium Scanning**
   - Navigate to "Scan Premiums" tab
   - Apply filters (price range, minimum premium)
   - Sort by Monthly % to find highest returns
   - Review bid/ask spreads for liquidity

4. **Analysis & Selection**
   - Compare opportunities across sectors
   - Evaluate IV levels for volatility assessment
   - Check volume and open interest for liquidity
   - Export selected opportunities for execution

## Performance Characteristics

### Data Volume
- **Stocks Tracked**: 1,205 symbols
- **Options Synced**: ~400-500 stocks (with available options)
- **Data Points**: ~5,000+ option contracts
- **Refresh Rate**: On-demand with sync button

### Query Performance
- **Initial Load**: <2 seconds for 500 stocks
- **Filtering**: Real-time with no perceptible lag
- **Sorting**: Client-side JavaScript for instant response
- **Sync Time**: 10-15 minutes for full database

## Comparison with TradingView Watchlists

| Aspect | Database Scan | TradingView Watchlists |
|--------|--------------|------------------------|
| **Scope** | All 1,205 database stocks | Selected watchlist only (~150) |
| **Purpose** | Discovery across entire market | Track curated list |
| **Filtering** | No symbol filter | Filtered by watchlist |
| **Sync** | Syncs all stocks | Syncs watchlist only |
| **Use Case** | Find new opportunities | Monitor known stocks |

## Technical Implementation

### SQL Query Structure
```sql
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
    sp.open_interest as oi,
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
```

### Key Design Decisions

1. **Delta Range (0.25-0.40)**: Balanced risk/reward for wheel strategy
2. **30-Day Default**: Optimal theta decay period
3. **DISTINCT ON**: One best option per symbol to reduce noise
4. **LEFT JOINs**: Graceful handling of missing data
5. **Client-side Sorting**: Better UX with instant feedback

## Future Enhancements

See [WISHLIST.md](WISHLIST.md) for planned improvements and feature requests.

## Related Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) - Technical architecture details
- [SPEC.md](SPEC.md) - Complete specification
- [WISHLIST.md](WISHLIST.md) - Future enhancements