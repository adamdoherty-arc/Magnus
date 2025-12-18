# Two-Mode Options Analysis System - Complete Guide

**Created:** 2025-01-21
**Status:** Production Ready

## Overview

The Options Analysis Hub provides TWO distinct analysis modes designed for different use cases:

1. **Batch Analysis Mode** - Scan and rank 100+ stocks with paginated results
2. **Individual Stock Deep Dive** - Detailed analysis of a single stock with all strategies

## Architecture

### Component Structure

```
Magnus/
├── options_analysis_page.py           # Main two-mode page
├── src/
│   ├── components/
│   │   ├── paginated_table.py         # Reusable pagination component
│   │   └── stock_dropdown.py          # Stock selector component
│   ├── ai_options_agent/
│   │   ├── options_analysis_agent.py  # Main AI agent
│   │   ├── scoring_engine.py          # 5-scorer MCDM system
│   │   └── ai_options_db_manager.py   # Database layer
```

### Key Features

#### Reusable Components

1. **PaginatedTable** (`src/components/paginated_table.py`)
   - Handles 100+ results efficiently
   - Column sorting (ascending/descending)
   - Page size selector (10, 20, 50, 100)
   - CSV export
   - Action buttons per row
   - Responsive design

2. **StockDropdown** (`src/components/stock_dropdown.py`)
   - Searchable stock selector
   - Metadata display (price, sector, market cap)
   - Watchlist filtering
   - Multi-select support

---

## MODE 1: Batch Analysis (Scan & Rank)

### Purpose

Scan 100+ stocks and rank them by AI score. Ideal for:
- Finding the best opportunities across your entire portfolio
- Screening by specific criteria (DTE, delta, premium)
- Comparing multiple opportunities side-by-side

### User Flow

```
1. Select Analysis Source
   └─> All Stocks OR TradingView Watchlist

2. Configure Filters
   ├─> DTE Range (20-40 days default)
   ├─> Delta Range (-0.45 to -0.15 default)
   ├─> Min Premium ($100 default)
   └─> Min Score to Display (50 default)

3. Run Analysis
   └─> AI Agent analyzes opportunities

4. View Paginated Results
   ├─> Sort by any column
   ├─> Export to CSV
   └─> Click "View Details" for deep dive

5. Review Details
   └─> Modal with full breakdown
```

### Results Table Columns

| Column | Description | Sortable |
|--------|-------------|----------|
| Symbol | Stock ticker | ✅ |
| Score | Final AI score (0-100) | ✅ |
| Recommendation | STRONG_BUY, BUY, HOLD, etc. | ✅ |
| Strike | Strike price | ✅ |
| DTE | Days to expiration | ✅ |
| Premium | Premium amount | ✅ |
| Monthly % | Monthly return | ✅ |
| Annual % | Annualized return | ✅ |
| Delta | Put delta | ✅ |
| Confidence | Confidence level | ✅ |
| Details | View button | N/A |

### Performance

- **Pagination:** 20 results per page (configurable)
- **Caching:** Database queries cached for 5 minutes
- **Export:** Full CSV export available
- **Sorting:** Client-side for instant response

---

## MODE 2: Individual Stock Deep Dive

### Purpose

Analyze a SINGLE stock in detail with all available strategies. Ideal for:
- Deep research on a specific stock
- Comparing multiple strikes/expirations
- Understanding detailed scoring breakdown
- Risk/opportunity analysis

### User Flow

```
1. Select Stock
   └─> Searchable dropdown with metadata

2. Configure Analysis Settings
   ├─> DTE Range
   ├─> Delta Range
   ├─> Min Premium
   └─> Optional: Enable LLM Reasoning

3. Run Analysis
   └─> AI Agent analyzes top 10 strategies

4. Review All Strategies
   ├─> Strategy #1 (highest score)
   ├─> Strategy #2
   └─> ... up to 10 strategies

5. For Each Strategy:
   ├─> 5 Score Breakdown (Fundamental, Technical, Greeks, Risk, Sentiment)
   ├─> Reasoning & Analysis
   ├─> Key Risks & Opportunities
   └─> Detailed Greeks
```

### 5-Scorer Breakdown

Each strategy displays detailed scores from the MCDM system:

#### 1. Fundamental Score (0-100)
- **Factors:**
  - P/E Ratio (20%)
  - EPS Growth (25%)
  - Market Cap (15%)
  - Sector Strength (20%)
  - Dividend Yield (10%)
  - Financial Health (10%)

#### 2. Technical Score (0-100)
- **Factors:**
  - Price vs Strike (30%)
  - Volume (20%)
  - Open Interest (20%)
  - Bid-Ask Spread (30%)

#### 3. Greeks Score (0-100)
- **Factors:**
  - Delta (30%) - Target: -0.20 to -0.35
  - Implied Volatility (30%)
  - Premium/Strike Ratio (25%)
  - DTE Range (15%)

#### 4. Risk Score (0-100)
- **Factors:**
  - Max Loss (35%)
  - Probability of Profit (30%)
  - Breakeven Distance (20%)
  - Annualized Return (15%)

#### 5. Sentiment Score (0-100)
- **Status:** Stub implementation (returns 70)
- **Planned:** News sentiment, social media, analyst ratings

### Final Score Calculation

```python
final_score = (
    fundamental_score * 0.20 +
    technical_score * 0.20 +
    greeks_score * 0.20 +
    risk_score * 0.25 +
    sentiment_score * 0.15
)
```

### Recommendation Mapping

| Final Score | Recommendation | Confidence |
|-------------|----------------|------------|
| 85-100 | STRONG_BUY | 90% |
| 75-84 | BUY | 80% |
| 60-74 | HOLD | 70% |
| 45-59 | CAUTION | 60% |
| 0-44 | AVOID | 50% |

---

## Component API Reference

### PaginatedTable

```python
from src.components.paginated_table import PaginatedTable

table = PaginatedTable(
    df=dataframe,
    key_prefix="unique_key",
    page_size=20,
    show_export=True,
    show_page_size_selector=True,
    sortable_columns=None,  # None = all columns sortable
    action_column={
        'label': 'Details',
        'button_label': '🔍 View',
        'callback': callback_function
    }
)

table.render()
```

### StockDropdown

```python
from src.components.stock_dropdown import StockDropdown

selector = StockDropdown(db_manager)

# Single select
symbol = selector.render(
    label="Select Stock",
    key="stock_select",
    show_metadata=True
)

# Multi-select
symbols = selector.render_multiselect(
    label="Select Stocks",
    key="multi_select",
    max_selections=10
)
```

### WatchlistSelector

```python
from src.components.stock_dropdown import WatchlistSelector

selector = WatchlistSelector(db_manager)

watchlist_name, symbols = selector.render(
    label="Select Watchlist",
    key="watchlist"
)
```

---

## Database Schema

### Required Tables

#### stock_premiums
```sql
CREATE TABLE stock_premiums (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20),
    strike_price NUMERIC(10,2),
    expiration_date DATE,
    dte INTEGER,
    delta NUMERIC(10,4),
    premium NUMERIC(10,2),
    bid NUMERIC(10,2),
    ask NUMERIC(10,2),
    volume INTEGER,
    open_interest INTEGER,
    implied_volatility NUMERIC(10,2),
    monthly_return NUMERIC(10,2),
    annual_return NUMERIC(10,2),
    strike_type VARCHAR(20),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### stock_data
```sql
CREATE TABLE stock_data (
    symbol VARCHAR(10) PRIMARY KEY,
    current_price NUMERIC(10,2),
    pe_ratio NUMERIC(10,2),
    market_cap BIGINT,
    sector VARCHAR(50),
    dividend_yield NUMERIC(5,2),
    eps NUMERIC(10,2)
);
```

#### ai_options_analyses
```sql
CREATE TABLE ai_options_analyses (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20),
    strike_price NUMERIC(10,2),
    expiration_date DATE,
    final_score INTEGER,
    fundamental_score INTEGER,
    technical_score INTEGER,
    greeks_score INTEGER,
    risk_score INTEGER,
    sentiment_score INTEGER,
    recommendation VARCHAR(20),
    confidence INTEGER,
    reasoning TEXT,
    key_risks TEXT,
    key_opportunities TEXT,
    llm_model VARCHAR(50),
    llm_tokens_used INTEGER,
    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Usage Examples

### Example 1: Batch Analysis - All Stocks

```python
# User selects:
- Analysis Source: All Stocks
- Min DTE: 20
- Max DTE: 40
- Min Delta: -0.45
- Max Delta: -0.15
- Min Premium: $100
- Min Score: 50
- Max Results: 200

# System:
1. Queries database for matching opportunities
2. Scores each using MCDM system
3. Filters by min score (50)
4. Displays paginated results (20 per page)
5. User sorts by "Score" descending
6. User clicks "View Details" on top result
7. Modal opens with full breakdown
```

### Example 2: Individual Stock - AAPL

```python
# User selects:
- Stock: AAPL
- Min DTE: 25
- Max DTE: 35
- Min Delta: -0.40
- Max Delta: -0.20
- Min Premium: $200

# System:
1. Gets all AAPL opportunities matching filters
2. Analyzes top 10 strategies
3. Displays each with:
   - 5 score breakdown
   - Reasoning
   - Risks/Opportunities
   - Greeks details
4. User reviews Strategy #1 (85/100 score)
5. Expands "Detailed Greeks" section
6. Makes informed decision
```

---

## Configuration

### Environment Variables

```bash
# Database
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your_password
DB_NAME=magnus

# LLM (Optional)
OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
```

### Default Settings

```python
# Batch Analysis Defaults
DEFAULT_MIN_DTE = 20
DEFAULT_MAX_DTE = 40
DEFAULT_MIN_DELTA = -0.45
DEFAULT_MAX_DELTA = -0.15
DEFAULT_MIN_PREMIUM = 100.0
DEFAULT_MIN_SCORE = 50
DEFAULT_MAX_RESULTS = 200
DEFAULT_PAGE_SIZE = 20

# Individual Analysis Defaults
DEFAULT_STRATEGIES_PER_STOCK = 10
```

---

## Performance Optimization

### Caching Strategy

1. **Database Manager:** Cached with `@st.cache_resource`
2. **Stock List:** Cached for 1 hour with `@st.cache_data(ttl=3600)`
3. **Analysis Results:** Stored in `st.session_state`
4. **Pagination State:** Session state per table instance

### Query Optimization

- Use `DISTINCT ON` for best opportunity per symbol
- Index on `(symbol, dte)` for fast filtering
- Index on `delta` range queries
- Limit results in database (not Python)

### Client-Side Performance

- Pagination: Only render 20 rows at a time
- Sorting: In-memory on current dataset
- Export: Generates CSV on-demand
- Action callbacks: Minimal state updates

---

## Troubleshooting

### Issue: No stocks in dropdown

**Cause:** Empty `stock_data` table

**Solution:**
```sql
-- Verify data
SELECT COUNT(*) FROM stock_data;

-- If empty, run data sync
python src/tradingview_api_sync.py
```

### Issue: Pagination not working

**Cause:** Missing session state initialization

**Solution:**
- Ensure unique `key_prefix` for each table
- Check browser console for errors
- Clear Streamlit cache: `st.cache_data.clear()`

### Issue: Slow analysis

**Cause:** Too many results or LLM enabled

**Solution:**
- Reduce `max_results` parameter
- Disable LLM reasoning for batch mode
- Use database indexes
- Filter by watchlist instead of all stocks

---

## Future Enhancements

### Phase 3 (Planned)

1. **Multi-Strategy Comparison**
   - Compare CSP vs Covered Calls vs Spreads
   - Side-by-side strategy metrics
   - Risk/reward visualization

2. **Advanced Sentiment Analysis**
   - News API integration (Finnhub)
   - Social media sentiment (Reddit, Twitter)
   - Insider trading data
   - Analyst ratings aggregation

3. **LLM-Powered Reasoning**
   - Claude 3.5 Sonnet integration
   - GPT-4 Turbo support
   - Custom prompt templates
   - Token usage tracking

4. **Portfolio Integration**
   - Link to existing positions
   - Position sizing recommendations
   - Diversification analysis
   - Risk allocation optimization

### Phase 4 (Advanced)

1. **Multi-Agent Orchestration**
   - 6 specialized AI agents
   - Parallel analysis
   - Consensus scoring
   - Conflict resolution

2. **RAG Knowledge Base**
   - Historical analysis retrieval
   - Pattern matching
   - Backtesting data
   - Learning from outcomes

3. **Real-Time Updates**
   - Live price monitoring
   - Greeks recalculation
   - Alert system
   - Push notifications

---

## Code Quality

### Type Hints

All functions use type hints for better IDE support:

```python
def render_batch_analysis_mode(
    agent: OptionsAnalysisAgent,
    db_manager: AIOptionsDBManager,
    llm_manager: Optional[Any]
) -> None:
    """MODE 1: Batch Analysis"""
```

### Error Handling

Graceful degradation with user-friendly messages:

```python
try:
    analyses = agent.analyze_all_stocks(...)
except Exception as e:
    logger.error(f"Analysis failed: {e}")
    st.error("Analysis failed. Please try again.")
    return
```

### Documentation

- Comprehensive docstrings
- Inline comments for complex logic
- User-facing help text
- Architecture documentation

---

## Testing

### Manual Testing Checklist

#### Batch Analysis Mode
- [ ] Select "All Stocks" source
- [ ] Adjust DTE range
- [ ] Adjust delta range
- [ ] Set min premium
- [ ] Run analysis
- [ ] Verify results display
- [ ] Test pagination (next, prev, first, last)
- [ ] Test sorting on each column
- [ ] Test CSV export
- [ ] Click "View Details" button
- [ ] Verify modal displays correctly
- [ ] Close modal

#### Individual Stock Mode
- [ ] Select stock from dropdown
- [ ] Search by typing symbol
- [ ] Adjust analysis settings
- [ ] Run analysis
- [ ] Verify strategies display
- [ ] Check 5-scorer breakdown
- [ ] Review reasoning section
- [ ] Expand Greeks details
- [ ] Test with different stocks

#### Watchlist Integration
- [ ] Select watchlist source
- [ ] Choose specific watchlist
- [ ] Verify symbol count
- [ ] Run analysis on watchlist
- [ ] Verify filtered results

---

## Support

For issues or questions:

1. Check this documentation
2. Review component docstrings
3. Check Streamlit logs
4. Verify database connectivity
5. Test with smaller datasets

---

## Summary

The Two-Mode Options Analysis System provides:

✅ **Clear Separation:** Batch vs Individual modes
✅ **Reusable Components:** Pagination, stock selection
✅ **Type Safety:** Full type hints throughout
✅ **Performance:** Caching, pagination, optimization
✅ **Extensibility:** Easy to add new features
✅ **User Experience:** Intuitive, responsive, fast

**Status:** Production Ready
**Version:** 1.0
**Last Updated:** 2025-01-21
