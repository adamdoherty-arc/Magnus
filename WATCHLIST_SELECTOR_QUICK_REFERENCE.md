# Watchlist Selector - Quick Reference Card
## One-Page Reference for Developers

---

## QUICK INTEGRATION (3 STEPS)

### 1. Import Component
```python
from comprehensive_strategy_page_watchlist_component import WatchlistSelector
```

### 2. Initialize & Render
```python
selector = WatchlistSelector()
analysis_data = selector.render()
```

### 3. Use Data
```python
if analyze_button and analysis_data:
    stock_data = analysis_data['stock_data']
    options_data = analysis_data['options_data']
    # Use for analysis
```

---

## DATA STRUCTURE

### Input (None) → Output (Dict)

```python
{
    'stock_data': {
        'symbol': 'AAPL',           # str
        'current_price': 175.50,    # float
        'iv': 0.35,                 # float (0.0-1.0)
        'price_52w_high': 195.00,   # float
        'price_52w_low': 155.00,    # float
        'market_cap': 2750000000000,# float (in dollars)
        'pe_ratio': 28.5,           # float
        'sector': 'Technology'      # str
    },
    'options_data': {
        'strike_price': 170.00,     # float
        'dte': 30,                  # int (days)
        'delta': -0.30,             # float (-1.0 to 0.0)
        'premium': 250              # int (cents)
    }
}
```

---

## UI MODES

### 1. Manual Input (Default)
- User enters all fields manually
- No database/API calls
- Fastest for one-off analysis

### 2. TradingView Watchlist
- Select watchlist → Select stock → Auto-populate
- Data from: `tv_watchlists` + `tv_watchlist_symbols` tables
- Fallback: yfinance API

### 3. Database Watchlist
- Select table → Search stock → Auto-populate
- Tables: `stock_premiums`, `stock_data`, `stocks`
- Fallback: yfinance API

---

## KEY METHODS

### Main Render Method
```python
def render(self) -> Optional[Dict[str, Any]]:
    # Returns data dict or None
```

### Auto-Populate Method
```python
def auto_populate_stock_data(
    symbol: str,
    source: str  # 'manual', 'tradingview', 'database'
) -> Dict[str, Any]:
    # Returns populated stock data
```

### Load Methods (Cached)
```python
load_tradingview_watchlists()  # TTL: 3600s (1 hour)
load_watchlist_stocks(name)    # TTL: 300s (5 minutes)
load_database_stocks(table)    # TTL: 60s (1 minute)
```

---

## SESSION STATE

### Variables Used
```python
st.session_state.data_source           # 'manual', 'tradingview', 'database'
st.session_state.selected_watchlist    # Watchlist name
st.session_state.selected_stock_symbol # Stock ticker
st.session_state.auto_populated_data   # Dict with stock data
st.session_state.selected_db_table     # Database table name
```

### Clear State
```python
# Reset all session state
st.session_state.clear()

# Or use Streamlit UI
# Settings → Clear cache → Rerun
```

---

## DATABASE QUERIES

### TradingView Watchlists
```sql
SELECT * FROM tv_watchlists WHERE is_active = TRUE;
SELECT * FROM tv_watchlist_symbols WHERE watchlist_id = ?;
```

### Stock Data
```sql
-- Primary source
SELECT * FROM stock_data WHERE symbol = ?;

-- IV data
SELECT AVG(implied_volatility) FROM stock_premiums WHERE symbol = ?;

-- Alternative tables
SELECT * FROM stocks WHERE ticker = ?;
SELECT DISTINCT symbol FROM stock_premiums WHERE premium > 0;
```

---

## ERROR HANDLING

### Common Errors

| Error | Solution |
|-------|----------|
| Database connection failed | Check .env credentials |
| No watchlists found | Sync TradingView data first |
| Stock not in database | Uses yfinance fallback |
| yfinance timeout | Retry or use manual input |
| Session state error | Clear cache & restart |

### Graceful Degradation

```
Database Error → yfinance API → Manual Input
     ↓              ↓              ↓
  (auto)        (semi-auto)    (manual)
```

---

## PERFORMANCE

### Caching
- **Watchlists**: 1 hour (rarely change)
- **Stocks in watchlist**: 5 minutes (moderate)
- **Database stocks**: 1 minute (frequent)

### Optimization Tips
1. Use database sources when possible (faster)
2. yfinance as fallback only (slower)
3. Cache clears automatically on TTL expiry
4. Manual cache clear: `st.cache_data.clear()`

---

## FILE LOCATIONS

```
c:\Code\WheelStrategy\
├── comprehensive_strategy_page.py (MODIFY THIS)
├── comprehensive_strategy_page_watchlist_component.py (NEW)
├── WATCHLIST_SELECTION_UI_DESIGN.md (REFERENCE)
├── WATCHLIST_INTEGRATION_GUIDE.md (DETAILED GUIDE)
└── WATCHLIST_SELECTOR_QUICK_REFERENCE.md (THIS FILE)
```

---

## TESTING

### Quick Test Commands
```bash
# Test component standalone
streamlit run comprehensive_strategy_page_watchlist_component.py

# Test integrated page
streamlit run comprehensive_strategy_page.py

# Run unit tests
python test_watchlist_integration.py
```

### Manual Test Checklist
- [ ] Manual input works
- [ ] TradingView selector loads watchlists
- [ ] Database selector loads stocks
- [ ] Auto-populate fills fields correctly
- [ ] Analysis runs with populated data
- [ ] Error messages display properly

---

## DEPENDENCIES

### Python Packages
```python
streamlit           # UI framework
psycopg2           # PostgreSQL connection
yfinance           # Stock data fallback
python-dotenv      # Environment variables
```

### Database Tables
```sql
tv_watchlists           -- TradingView watchlists
tv_watchlist_symbols    -- Stocks in watchlists
stock_data              -- Stock fundamentals
stock_premiums          -- Options data
stocks                  -- Basic stock info
```

### Environment Variables
```bash
DB_HOST=localhost
DB_PORT=5432
DB_NAME=magnus
DB_USER=postgres
DB_PASSWORD=postgres123!
```

---

## COMMON PATTERNS

### Pattern 1: Basic Integration
```python
# In your Streamlit page
selector = WatchlistSelector()
data = selector.render()

if st.button("Analyze"):
    if data:
        # Use data
        result = analyze(data['stock_data'], data['options_data'])
```

### Pattern 2: With Validation
```python
data = selector.render()

if st.button("Analyze"):
    if not data:
        st.error("Please select data first")
    elif data['stock_data']['current_price'] <= 0:
        st.error("Invalid stock price")
    else:
        # Proceed with analysis
```

### Pattern 3: Custom Post-Processing
```python
data = selector.render()

if data:
    # Modify data before analysis
    stock_data = data['stock_data']
    stock_data['iv'] = min(stock_data['iv'], 1.0)  # Cap IV
    stock_data['market_cap'] = stock_data['market_cap'] / 1e9  # Convert to billions

    # Then analyze
    result = analyze(stock_data, data['options_data'])
```

---

## KEYBOARD SHORTCUTS

When using the UI:

| Key | Action |
|-----|--------|
| Tab | Navigate between fields |
| Enter | Submit form / Click button |
| ↑↓ | Navigate dropdown options |
| Esc | Close dropdown / modal |
| Ctrl+R | Rerun Streamlit app |

---

## TROUBLESHOOTING ONE-LINERS

```bash
# Check database connection
psql -h localhost -U postgres -d magnus -c "SELECT 1"

# List watchlists in database
psql -h localhost -U postgres -d magnus -c "SELECT * FROM tv_watchlists LIMIT 5"

# Clear Streamlit cache
streamlit cache clear

# Check component file exists
ls -la comprehensive_strategy_page_watchlist_component.py

# View environment variables
cat .env | grep DB_

# Test yfinance
python -c "import yfinance as yf; print(yf.Ticker('AAPL').info['currentPrice'])"
```

---

## VERSION INFO

- **Component Version**: 1.0
- **Created**: 2025-11-06
- **Compatible With**: Streamlit 1.28+
- **Python Version**: 3.8+
- **Database**: PostgreSQL 12+

---

## SUPPORT LINKS

- **Design Doc**: `WATCHLIST_SELECTION_UI_DESIGN.md`
- **Integration Guide**: `WATCHLIST_INTEGRATION_GUIDE.md`
- **Database Schema**: `database_schema.sql`
- **TradingView Manager**: `src/tradingview_db_manager.py`

---

**END OF QUICK REFERENCE**

*Print this page and keep it handy while developing!*
