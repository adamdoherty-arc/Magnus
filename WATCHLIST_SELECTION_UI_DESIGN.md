# Watchlist Selection UI Design
## Comprehensive Strategy Page Enhancement

**Created**: 2025-11-06
**Author**: Frontend Developer Agent
**Target File**: `comprehensive_strategy_page.py`

---

## 1. UI MOCKUP / DESIGN DESCRIPTION

### Visual Layout

```
┌─────────────────────────────────────────────────────────────┐
│  🎯 Comprehensive Options Strategy Analysis                 │
│  Analyze ALL 10 strategies with multi-model AI consensus    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  📊 Stock Data Source                                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  ○ Manual Input (current)                            │  │
│  │  ○ TradingView Watchlist                             │  │
│  │  ○ Database Watchlist                                │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  [Content changes based on selection]                       │
│                                                              │
│  MANUAL INPUT MODE:                                          │
│  ┌────────────┬────────────┬────────────┐                  │
│  │ Symbol     │ Price      │ IV         │                  │
│  │ [AAPL__]   │ [175.50_]  │ [0.35___]  │                  │
│  └────────────┴────────────┴────────────┘                  │
│                                                              │
│  TRADINGVIEW WATCHLIST MODE:                                 │
│  ┌────────────────────────────────────────┐                │
│  │ Select Watchlist: [Tech Leaders ▼]     │                │
│  └────────────────────────────────────────┘                │
│  ┌────────────────────────────────────────┐                │
│  │ Select Stock: [AAPL - Apple Inc. ▼]    │                │
│  │                                         │                │
│  │ ✓ Auto-populated data:                 │                │
│  │   Price: $175.50                        │                │
│  │   Market Cap: $2.75T                    │                │
│  │   52W High/Low: $195.00 / $155.00      │                │
│  └────────────────────────────────────────┘                │
│                                                              │
│  DATABASE WATCHLIST MODE:                                    │
│  ┌────────────────────────────────────────┐                │
│  │ Select Data Source: [Stock Premiums ▼] │                │
│  └────────────────────────────────────────┘                │
│  ┌────────────────────────────────────────┐                │
│  │ Search & Select Stock:                  │                │
│  │ [🔍 Search...____________]              │                │
│  │                                         │                │
│  │ AAPL - Apple Inc. ($175.50)            │                │
│  │ MSFT - Microsoft Corp ($380.25)        │                │
│  │ GOOGL - Alphabet Inc ($142.85)         │                │
│  └────────────────────────────────────────┘                │
│                                                              │
│  [🚀 Analyze ALL Strategies]                                │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. USER EXPERIENCE FLOW

### Flow Diagram

```
┌─────────────────┐
│  Page Load      │
└────────┬────────┘
         │
         v
┌─────────────────┐
│ Default: Manual │
│ Input Selected  │
└────────┬────────┘
         │
         v
┌──────────────────────────────────┐
│ User Selects Data Source:        │
│ 1. Manual Input                  │
│ 2. TradingView Watchlist         │
│ 3. Database Watchlist            │
└────────┬─────────────────────────┘
         │
    ┌────┴───────────────────┐
    │                        │
    v                        v
┌─────────────┐    ┌──────────────────┐
│  Manual     │    │  TradingView     │
│  Input      │    │  Watchlist       │
└─────────────┘    └────────┬─────────┘
                            │
                            v
                   ┌────────────────────┐
                   │ Load Watchlists    │
                   │ from TV API/DB     │
                   └────────┬───────────┘
                            │
                            v
                   ┌────────────────────┐
                   │ User Selects       │
                   │ Watchlist          │
                   └────────┬───────────┘
                            │
                            v
                   ┌────────────────────┐
                   │ Load Stocks in     │
                   │ Selected Watchlist │
                   └────────┬───────────┘
                            │
                            v
                   ┌────────────────────┐
                   │ User Selects Stock │
                   └────────┬───────────┘
                            │
                            v
                   ┌────────────────────┐
                   │ Auto-Populate:     │
                   │ - Current Price    │
                   │ - Market Cap       │
                   │ - 52W High/Low     │
                   │ - IV (if avail)    │
                   │ - Sector           │
                   └────────┬───────────┘
                            │
         ┌──────────────────┴──────────────────┐
         │                                     │
         v                                     v
┌─────────────────┐              ┌─────────────────────┐
│  Database       │              │  User Reviews       │
│  Watchlist      │              │  Auto-Populated     │
└────────┬────────┘              │  Data               │
         │                       └──────────┬──────────┘
         v                                  │
┌─────────────────┐                        │
│ Select Data     │                        │
│ Source Table    │                        │
└────────┬────────┘                        │
         │                                  │
         v                                  │
┌─────────────────┐                        │
│ Load Stocks     │                        │
│ with Premium    │                        │
│ Data            │                        │
└────────┬────────┘                        │
         │                                  │
         v                                  │
┌─────────────────┐                        │
│ Searchable      │                        │
│ Stock Dropdown  │                        │
└────────┬────────┘                        │
         │                                  │
         v                                  │
┌─────────────────┐                        │
│ Auto-Populate   │                        │
│ from Database   │                        │
└────────┬────────┘                        │
         │                                  │
         └──────────────────┬───────────────┘
                            │
                            v
                   ┌────────────────────┐
                   │ User Clicks        │
                   │ "Analyze ALL       │
                   │  Strategies"       │
                   └────────┬───────────┘
                            │
                            v
                   ┌────────────────────┐
                   │ Run Comprehensive  │
                   │ Strategy Analysis  │
                   └────────────────────┘
```

---

## 3. COMPONENT BREAKDOWN

### 3.1 Data Source Selector
- **Type**: Radio buttons (st.radio)
- **Options**:
  1. "📝 Manual Input (Current)"
  2. "📺 TradingView Watchlist"
  3. "💾 Database Watchlist"
- **Default**: Manual Input
- **Behavior**: Triggers UI reflow on selection change

### 3.2 Manual Input Section (DEFAULT)
- **Current Implementation**: No changes required
- **Fields**: Symbol, Price, IV, 52W High/Low, etc.

### 3.3 TradingView Watchlist Section
**Components**:
1. **Watchlist Dropdown** (st.selectbox)
   - Loads from: `TradingViewDBManager.get_all_watchlists()`
   - Displays: Watchlist name + symbol count
   - Example: "Tech Leaders (15 stocks)"

2. **Stock Dropdown** (st.selectbox)
   - Loads from: `TradingViewDBManager.get_watchlist_details(watchlist_name)`
   - Displays: Symbol - Company Name (Price)
   - Example: "AAPL - Apple Inc. ($175.50)"

3. **Auto-Populated Data Display**
   - Read-only fields showing fetched data
   - Uses `st.info()` to display confirmation
   - Data sources: TradingView DB + yfinance fallback

### 3.4 Database Watchlist Section
**Components**:
1. **Data Source Dropdown** (st.selectbox)
   - Options:
     - "Stock Premiums (CSP Options Data)"
     - "Stocks Table (All Stocks)"
     - "Stock Data (Daily Prices)"
   - Maps to actual table names

2. **Stock Search/Select** (st.selectbox with filter)
   - Searchable dropdown using `st.selectbox`
   - Loads from selected table
   - Format: "SYMBOL - Name ($Price)"
   - Query: Based on selected data source

3. **Auto-Populated Fields**
   - Fetches directly from database
   - Falls back to yfinance if data missing
   - Shows data freshness timestamp

---

## 4. DATA INTEGRATION POINTS

### 4.1 TradingView Integration

#### Functions to Import:
```python
from src.tradingview_db_manager import TradingViewDBManager
```

#### Methods Used:
```python
# Get all watchlists
tv_manager = TradingViewDBManager()
watchlists = tv_manager.get_all_watchlists()
# Returns: [{'name': 'Tech Leaders', 'symbol_count': 15, ...}, ...]

# Get stocks in watchlist
stocks = tv_manager.get_watchlist_details(watchlist_name)
# Returns: [{'symbol': 'AAPL', 'company_name': '...', 'last_price': 175.50, ...}, ...]

# Get just symbols
symbols = tv_manager.get_watchlist_symbols(watchlist_name)
# Returns: ['AAPL', 'MSFT', 'GOOGL', ...]
```

### 4.2 Database Integration

#### Database Connection:
```python
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432'),
        database=os.getenv('DB_NAME', 'magnus'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'postgres123!')
    )
```

#### Query Examples:

**From stock_premiums table:**
```python
conn = get_db_connection()
cur = conn.cursor(cursor_factory=RealDictCursor)

# Get distinct stocks with premium data
cur.execute("""
    SELECT DISTINCT
        sp.symbol,
        sd.company_name,
        sd.current_price,
        sd.sector,
        sd.market_cap,
        MAX(sp.implied_volatility) as avg_iv
    FROM stock_premiums sp
    LEFT JOIN stock_data sd ON sp.symbol = sd.symbol
    WHERE sp.premium > 0
    GROUP BY sp.symbol, sd.company_name, sd.current_price, sd.sector, sd.market_cap
    ORDER BY sp.symbol
""")
stocks = cur.fetchall()
```

**From stocks table:**
```python
cur.execute("""
    SELECT
        ticker as symbol,
        name as company_name,
        price as current_price,
        sector,
        market_cap
    FROM stocks
    WHERE price > 0
    ORDER BY ticker
""")
stocks = cur.fetchall()
```

**From stock_data table:**
```python
cur.execute("""
    SELECT
        symbol,
        company_name,
        current_price,
        sector,
        market_cap,
        price_52w_high,
        price_52w_low,
        updated_at
    FROM stock_data
    WHERE current_price > 0
    ORDER BY symbol
""")
stocks = cur.fetchall()
```

### 4.3 Auto-Population Logic

#### Data to Populate:
1. **symbol** → From selection
2. **current_price** → From DB or yfinance
3. **iv** → From stock_premiums table or calculated
4. **price_52w_high** → From yfinance or stock_data
5. **price_52w_low** → From yfinance or stock_data
6. **market_cap** → From DB or yfinance
7. **pe_ratio** → From yfinance only
8. **sector** → From DB or yfinance

#### Priority Order:
1. **Primary Source**: Database (faster, cached)
2. **Fallback Source**: yfinance API (real-time)

#### Implementation:
```python
def auto_populate_stock_data(symbol: str, source: str) -> dict:
    """
    Auto-populate stock data from selected source

    Args:
        symbol: Stock ticker symbol
        source: 'tradingview', 'database', or 'manual'

    Returns:
        dict with all required fields for analysis
    """
    import yfinance as yf

    data = {
        'symbol': symbol.upper(),
        'current_price': 0,
        'iv': 0.35,  # Default fallback
        'price_52w_high': 0,
        'price_52w_low': 0,
        'market_cap': 0,
        'pe_ratio': 0,
        'sector': 'Unknown'
    }

    # Try database first
    if source in ['tradingview', 'database']:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Try stock_data table first (most complete)
        cur.execute("""
            SELECT
                current_price,
                sector,
                market_cap,
                price_52w_high,
                price_52w_low
            FROM stock_data
            WHERE symbol = %s
            LIMIT 1
        """, (symbol,))

        db_data = cur.fetchone()

        if db_data:
            data['current_price'] = float(db_data['current_price'] or 0)
            data['sector'] = db_data['sector'] or 'Unknown'
            data['market_cap'] = float(db_data['market_cap'] or 0)
            data['price_52w_high'] = float(db_data['price_52w_high'] or 0)
            data['price_52w_low'] = float(db_data['price_52w_low'] or 0)

        # Get IV from stock_premiums
        cur.execute("""
            SELECT AVG(implied_volatility) as avg_iv
            FROM stock_premiums
            WHERE symbol = %s
              AND implied_volatility > 0
        """, (symbol,))

        iv_data = cur.fetchone()
        if iv_data and iv_data['avg_iv']:
            data['iv'] = float(iv_data['avg_iv'])

        cur.close()
        conn.close()

    # Fallback to yfinance if data is missing
    if data['current_price'] == 0:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            data['current_price'] = info.get('currentPrice', info.get('regularMarketPrice', 0))
            data['market_cap'] = info.get('marketCap', 0)
            data['pe_ratio'] = info.get('trailingPE', 0)
            data['sector'] = info.get('sector', 'Unknown')

            # Get 52-week data
            hist = ticker.history(period='1y')
            if not hist.empty:
                data['price_52w_high'] = hist['High'].max()
                data['price_52w_low'] = hist['Low'].min()
        except Exception as e:
            print(f"Error fetching yfinance data: {e}")

    return data
```

---

## 5. STATE MANAGEMENT

### Session State Variables:
```python
# Initialize in st.session_state
if 'data_source' not in st.session_state:
    st.session_state.data_source = 'manual'

if 'selected_watchlist' not in st.session_state:
    st.session_state.selected_watchlist = None

if 'selected_stock' not in st.session_state:
    st.session_state.selected_stock = None

if 'auto_populated_data' not in st.session_state:
    st.session_state.auto_populated_data = {}
```

---

## 6. ERROR HANDLING

### Common Errors & Solutions:

1. **Database Connection Failed**
   - Display: Warning message with retry button
   - Fallback: Switch to manual input mode

2. **TradingView Watchlist Empty**
   - Display: Info message explaining how to sync watchlists
   - Fallback: Show link to watchlist sync page

3. **Stock Data Not Found**
   - Display: Warning with stock symbol
   - Fallback: Try yfinance API
   - Last Resort: Allow manual input

4. **yfinance API Timeout**
   - Display: Loading spinner with timeout (10 seconds)
   - Fallback: Use cached database values
   - Error Message: "Could not fetch real-time data, using cached values"

---

## 7. ACCESSIBILITY CONSIDERATIONS

- **Keyboard Navigation**: All dropdowns and radio buttons are keyboard accessible
- **Screen Readers**: Proper labels on all form fields
- **Color Contrast**: Use Streamlit's default theme (WCAG AA compliant)
- **Loading States**: Clear loading indicators for async operations
- **Error Messages**: Descriptive and actionable error messages

---

## 8. PERFORMANCE OPTIMIZATION

### Caching Strategy:
```python
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_tradingview_watchlists():
    """Cache watchlist data to avoid repeated DB queries"""
    tv_manager = TradingViewDBManager()
    return tv_manager.get_all_watchlists()

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_watchlist_stocks(watchlist_name: str):
    """Cache stock list for selected watchlist"""
    tv_manager = TradingViewDBManager()
    return tv_manager.get_watchlist_details(watchlist_name)

@st.cache_data(ttl=60)  # Cache for 1 minute
def load_database_stocks(table_name: str):
    """Cache database stock list"""
    # Query based on table_name
    pass
```

### Database Query Optimization:
- Use indexed columns (symbol, ticker)
- Limit results to active stocks only
- Use LEFT JOINs for optional data
- Fetch only required columns

---

## 9. TESTING CHECKLIST

### Unit Tests:
- [ ] Test data source selector toggle
- [ ] Test TradingView watchlist loading
- [ ] Test database stock loading
- [ ] Test auto-population function
- [ ] Test error handling for missing data

### Integration Tests:
- [ ] Test full flow: Select TradingView → Select Watchlist → Select Stock → Analyze
- [ ] Test full flow: Select Database → Select Table → Select Stock → Analyze
- [ ] Test fallback from database to yfinance
- [ ] Test with empty watchlists
- [ ] Test with invalid stock symbols

### UI/UX Tests:
- [ ] Verify responsive layout on different screen sizes
- [ ] Test keyboard navigation
- [ ] Test screen reader compatibility
- [ ] Verify loading states display correctly
- [ ] Test error message clarity

---

## 10. DEPLOYMENT CHECKLIST

### Pre-Deployment:
- [ ] Environment variables configured (.env file)
- [ ] Database connection tested
- [ ] TradingView API credentials verified
- [ ] yfinance fallback tested
- [ ] All dependencies installed (requirements.txt)

### Post-Deployment:
- [ ] Verify watchlist data loads correctly
- [ ] Test auto-population with multiple stocks
- [ ] Monitor error logs for database issues
- [ ] Verify caching is working (check load times)
- [ ] Test with real user workflow

---

## 11. FUTURE ENHANCEMENTS

### Phase 2 Features:
1. **Bulk Analysis**: Select multiple stocks from watchlist
2. **Watchlist Creation**: Create custom watchlists from UI
3. **Data Refresh**: Manual refresh button for cached data
4. **Favorites**: Save frequently used stocks for quick access
5. **Comparison Mode**: Compare multiple stocks side-by-side
6. **Advanced Filters**: Filter watchlists by sector, price range, etc.
7. **Export Results**: Export analysis results to CSV/PDF

---

## INTEGRATION SUMMARY

### Files to Modify:
- `comprehensive_strategy_page.py` (main implementation)

### Files to Import:
- `src/tradingview_db_manager.py` (TradingView integration)
- `src/database_scanner.py` (Database queries - optional)

### New Dependencies:
- None (all existing dependencies)

### Database Tables Used:
- `tv_watchlists` (TradingView watchlists)
- `tv_watchlist_symbols` (TradingView stocks)
- `stock_premiums` (Options data)
- `stock_data` (Stock fundamentals)
- `stocks` (Basic stock info)

---

**END OF DESIGN DOCUMENT**
