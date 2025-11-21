# Watchlist Selection Integration Guide
## How to Integrate into comprehensive_strategy_page.py

**Created**: 2025-11-06
**Target File**: `comprehensive_strategy_page.py`

---

## QUICK START

### Step 1: Import the Component

Add this import at the top of `comprehensive_strategy_page.py`:

```python
from comprehensive_strategy_page_watchlist_component import WatchlistSelector
```

### Step 2: Replace Input Section

Find the current input section (lines ~50-80) and replace with:

```python
# Initialize watchlist selector
selector = WatchlistSelector()

# Render selector and get data
analysis_data = selector.render()
```

### Step 3: Update Analysis Section

Replace the data preparation section (lines ~85-103) with:

```python
if analyze_button and analysis_data:
    stock_data = analysis_data['stock_data']
    options_data = analysis_data['options_data']

    # Rest of analysis code remains the same
    with st.spinner(f"🔍 Analyzing ALL 10 strategies for {stock_data['symbol']}..."):
        result = analyzer.analyze(stock_data['symbol'], stock_data, options_data)
```

---

## DETAILED INTEGRATION

### Complete Modified Section

Replace **lines 48-104** in `comprehensive_strategy_page.py` with:

```python
st.markdown("---")

# ===============================================
# WATCHLIST SELECTOR INTEGRATION
# ===============================================

# Initialize watchlist selector
selector = WatchlistSelector()

# Render watchlist selector (replaces manual input)
analysis_data = selector.render()

# Show available AI models
with st.expander("🤖 AI Models Active", expanded=False):
    providers = llm_manager.get_available_providers()
    st.write(f"**{len(providers)} AI models ready:**")
    for p in providers:
        st.write(f"- ✅ **{p['name']}** - {p['description']} ({p['cost']})")

# Advanced options (moved here to apply to all data sources)
with st.expander("⚙️ Advanced AI Settings"):
    use_multi_model = st.checkbox(
        "Use Multi-Model AI Consensus (Claude + DeepSeek + Gemini)",
        value=True,
        help="Uses 3 AI models for consensus on top strategies"
    )

# Analysis button
st.markdown("---")
analyze_button = st.button("🚀 Analyze ALL Strategies", type="primary", use_container_width=True)

# ===============================================
# ANALYSIS EXECUTION
# ===============================================

if analyze_button:
    if not analysis_data:
        st.error("⚠️ Please select a stock and load data before analyzing")
    else:
        stock_data = analysis_data['stock_data']
        options_data = analysis_data['options_data']

        # Run comprehensive analysis
        with st.spinner(f"🔍 Analyzing ALL 10 strategies for {stock_data['symbol']}..."):
            result = analyzer.analyze(stock_data['symbol'], stock_data, options_data)

        st.success(f"✅ Analysis complete for {stock_data['symbol']}!")

        # Rest of display code continues unchanged from line 109...
```

---

## FILE STRUCTURE

### Before Integration:
```
comprehensive_strategy_page.py (370 lines)
├── Imports
├── Page config
├── Title
├── Initialize components
├── Show AI models
├── ❌ MANUAL INPUT SECTION (lines 50-80) ← REPLACE THIS
├── ❌ DATA PREPARATION (lines 85-103) ← REPLACE THIS
├── Analysis execution
├── Display results
└── Footer
```

### After Integration:
```
comprehensive_strategy_page.py (modified)
├── Imports
│   └── + from comprehensive_strategy_page_watchlist_component import WatchlistSelector
├── Page config
├── Title
├── Initialize components
├── ✅ WATCHLIST SELECTOR COMPONENT (new)
│   ├── Data source selector (radio)
│   ├── Manual input section
│   ├── TradingView section
│   └── Database section
├── Show AI models
├── Advanced settings
├── Analysis execution (modified)
├── Display results (unchanged)
└── Footer

comprehensive_strategy_page_watchlist_component.py (new file)
└── WatchlistSelector class with all functionality
```

---

## TESTING CHECKLIST

### Unit Tests

Run these tests after integration:

```bash
# Test 1: Manual input still works
python -m streamlit run comprehensive_strategy_page.py
# → Select "Manual Input"
# → Enter AAPL data
# → Click "Analyze ALL Strategies"
# → Should work as before

# Test 2: TradingView integration
# → Select "TradingView Watchlist"
# → Select a watchlist
# → Select a stock
# → Click "Load Stock Data"
# → Verify auto-populated fields
# → Click "Analyze ALL Strategies"

# Test 3: Database integration
# → Select "Database Watchlist"
# → Select "Stock Premiums"
# → Search for AAPL
# → Click "Load Stock Data"
# → Verify auto-populated fields
# → Click "Analyze ALL Strategies"

# Test 4: Error handling
# → Disconnect database
# → Try TradingView/Database options
# → Should show error messages
# → Should allow fallback to manual input
```

### Integration Tests

```python
# Test script: test_watchlist_integration.py

import streamlit as st
from comprehensive_strategy_page_watchlist_component import WatchlistSelector

def test_selector_initialization():
    """Test selector initializes without errors"""
    selector = WatchlistSelector()
    assert selector is not None
    print("✅ Selector initialization OK")

def test_manual_input():
    """Test manual input section renders"""
    selector = WatchlistSelector()
    data = selector.render_manual_input_section()
    assert 'stock_data' in data
    assert 'options_data' in data
    print("✅ Manual input OK")

def test_auto_populate():
    """Test auto-population function"""
    selector = WatchlistSelector()
    data = selector.auto_populate_stock_data('AAPL', 'database')
    assert data['symbol'] == 'AAPL'
    assert data['current_price'] > 0
    print("✅ Auto-populate OK")

if __name__ == "__main__":
    test_selector_initialization()
    test_manual_input()
    test_auto_populate()
    print("\n🎉 All tests passed!")
```

Run with:
```bash
python test_watchlist_integration.py
```

---

## TROUBLESHOOTING

### Issue 1: "Module not found: comprehensive_strategy_page_watchlist_component"

**Solution**:
```bash
# Ensure file is in the correct location
ls -la comprehensive_strategy_page_watchlist_component.py

# If not found, check current directory
pwd
# Should be: c:\Code\WheelStrategy
```

### Issue 2: "Database connection failed"

**Solution**:
```bash
# Check .env file has correct credentials
cat .env | grep DB_

# Should show:
# DB_HOST=localhost
# DB_PORT=5432
# DB_NAME=magnus
# DB_USER=postgres
# DB_PASSWORD=postgres123!

# Test database connection
psql -h localhost -U postgres -d magnus
```

### Issue 3: "No TradingView watchlists found"

**Solution**:
```python
# Sync watchlists first
from src.tradingview_db_manager import TradingViewDBManager

tv_manager = TradingViewDBManager()

# Create test watchlist
tv_manager.create_watchlist('Test Watchlist', 'Test description')
tv_manager.add_symbols_to_watchlist(1, ['AAPL', 'MSFT', 'GOOGL'])

# Verify
watchlists = tv_manager.get_all_watchlists()
print(f"Found {len(watchlists)} watchlists")
```

### Issue 4: "Auto-populate returns zeros"

**Solution**:
```python
# Check if stock exists in database
import psycopg2
conn = psycopg2.connect(...)
cur = conn.cursor()

cur.execute("SELECT * FROM stock_data WHERE symbol = 'AAPL' LIMIT 1")
result = cur.fetchone()

if not result:
    print("❌ Stock not in database - will use yfinance fallback")
else:
    print("✅ Stock found in database")

# If not found, trigger data sync
# Go to dashboard and click "Sync Stock Data"
```

### Issue 5: "Session state errors"

**Solution**:
```python
# Clear Streamlit cache
# In terminal:
streamlit cache clear

# Or add to code:
st.cache_data.clear()

# Or restart Streamlit server
# Ctrl+C then restart
```

---

## PERFORMANCE OPTIMIZATION

### Caching Strategy

The component uses Streamlit's `@st.cache_data` decorator with different TTLs:

```python
# Watchlists: Cache for 1 hour (rarely change)
@st.cache_data(ttl=3600)
def load_tradingview_watchlists():
    ...

# Watchlist stocks: Cache for 5 minutes (moderate changes)
@st.cache_data(ttl=300)
def load_watchlist_stocks(watchlist_name):
    ...

# Database stocks: Cache for 1 minute (frequent changes)
@st.cache_data(ttl=60)
def load_database_stocks(table_name):
    ...
```

### Database Connection Pooling

For high-traffic scenarios, consider connection pooling:

```python
from psycopg2 import pool

# In WatchlistSelector.__init__()
self.connection_pool = pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    **self.db_config
)

# In get_db_connection()
def get_db_connection(self):
    return self.connection_pool.getconn()

# After use
def return_connection(self, conn):
    self.connection_pool.putconn(conn)
```

---

## API REFERENCE

### WatchlistSelector Class

```python
class WatchlistSelector:
    """Main component class"""

    def __init__(self):
        """Initialize selector with database config"""

    def render(self) -> Optional[Dict[str, Any]]:
        """
        Render complete UI component

        Returns:
            {
                'stock_data': {
                    'symbol': str,
                    'current_price': float,
                    'iv': float,
                    'price_52w_high': float,
                    'price_52w_low': float,
                    'market_cap': float,
                    'pe_ratio': float,
                    'sector': str
                },
                'options_data': {
                    'strike_price': float,
                    'dte': int,
                    'delta': float,
                    'premium': int
                }
            }
        """

    def render_manual_input_section(self) -> Dict[str, Any]:
        """Render manual input UI (existing functionality)"""

    def render_tradingview_section(self) -> Optional[Dict[str, Any]]:
        """Render TradingView watchlist selection UI"""

    def render_database_section(self) -> Optional[Dict[str, Any]]:
        """Render database watchlist selection UI"""

    def auto_populate_stock_data(self, symbol: str, source: str) -> Dict[str, Any]:
        """
        Auto-populate stock data from source

        Args:
            symbol: Stock ticker
            source: 'manual', 'tradingview', or 'database'

        Returns:
            Dict with populated stock data fields
        """

    def load_tradingview_watchlists(self) -> List[Dict[str, Any]]:
        """Load TradingView watchlists (cached 1 hour)"""

    def load_watchlist_stocks(self, watchlist_name: str) -> List[Dict[str, Any]]:
        """Load stocks in watchlist (cached 5 minutes)"""

    def load_database_stocks(self, table_name: str) -> List[Dict[str, Any]]:
        """Load stocks from database table (cached 1 minute)"""

    def get_db_connection(self):
        """Get PostgreSQL database connection"""
```

---

## MIGRATION PATH

### Phase 1: Side-by-side Testing (Recommended)

Keep both old and new implementations:

```python
# Add at top of page
use_new_selector = st.sidebar.checkbox("Use New Watchlist Selector", value=False)

if use_new_selector:
    # New implementation
    selector = WatchlistSelector()
    analysis_data = selector.render()
else:
    # Old implementation (existing code)
    # ... manual input fields ...
```

### Phase 2: Gradual Rollout

1. Week 1: Deploy with toggle (default OFF)
2. Week 2: Set toggle default to ON
3. Week 3: Monitor for errors
4. Week 4: Remove toggle and old code

### Phase 3: Full Migration

Remove old code entirely once stable.

---

## ROLLBACK PLAN

If issues arise, quick rollback:

```bash
# 1. Comment out new import
# from comprehensive_strategy_page_watchlist_component import WatchlistSelector

# 2. Revert to git backup
git diff comprehensive_strategy_page.py > changes.patch
git checkout HEAD -- comprehensive_strategy_page.py

# 3. Verify old version works
streamlit run comprehensive_strategy_page.py

# 4. File bug report
echo "Bug details..." > WATCHLIST_SELECTOR_BUG.txt
```

---

## SUPPORT & DOCUMENTATION

### Additional Resources

- Design Document: `WATCHLIST_SELECTION_UI_DESIGN.md`
- Component Code: `comprehensive_strategy_page_watchlist_component.py`
- Database Schema: `database_schema.sql`
- TradingView Manager: `src/tradingview_db_manager.py`

### Contact

For issues or questions:
1. Check this guide first
2. Review design document
3. Test with provided test scripts
4. Check error logs in Streamlit console

---

**END OF INTEGRATION GUIDE**
