# Performance Enhancements Quick Reference

## Overview

This guide provides quick examples for using the new performance enhancements implemented in the AVA trading platform.

## 1. Pagination Component

### Basic Usage

```python
from src.components.pagination_component import paginate_dataframe

# Paginate any DataFrame
paginated_df = paginate_dataframe(
    df=your_dataframe,
    page_size=50,
    key_prefix="my_unique_key"  # Must be unique per page/component
)

# Display the paginated data
st.dataframe(paginated_df)
```

### Full Example

```python
import streamlit as st
import pandas as pd
from src.components.pagination_component import paginate_dataframe

# Your data
df = pd.DataFrame({
    'Symbol': ['AAPL', 'GOOGL', 'MSFT'] * 100,
    'Price': [150.0, 2800.0, 350.0] * 100
})

st.title("Stock Prices")

# Add filters if needed
min_price = st.number_input("Min Price", value=0.0)
filtered_df = df[df['Price'] >= min_price]

# Paginate and display
paginated_df = paginate_dataframe(
    df=filtered_df,
    page_size=50,
    key_prefix="stock_prices",
    show_info=True  # Shows "Page 1 of 3 | Showing rows 1-50 of 150"
)

st.dataframe(paginated_df, use_container_width=True)
```

### Key Parameters

- `df`: The pandas DataFrame to paginate
- `page_size`: Number of rows per page (default: 50)
- `key_prefix`: Unique identifier for this pagination component (required)
- `show_info`: Show page information (default: True)

### Important Notes

- `key_prefix` MUST be unique across your entire page
- Session state is managed automatically
- Navigation buttons appear only when needed (multiple pages)

---

## 2. Error Handling Utilities

### Basic Error Handling Decorator

```python
from src.utils.error_handling import with_error_handling

@with_error_handling(fallback_value=[], show_error=True)
def fetch_api_data():
    """Function that might fail"""
    response = requests.get("https://api.example.com/data")
    return response.json()

# Usage
data = fetch_api_data()  # Returns [] on error, shows user-friendly message
```

### Safe Cached Data

```python
from src.utils.error_handling import safe_cache_data

@safe_cache_data(ttl=300)  # 5 minutes cache
def get_stock_data(symbol):
    """Cached function with automatic error handling"""
    return database.query(f"SELECT * FROM stocks WHERE symbol = '{symbol}'")

# Usage
data = get_stock_data("AAPL")  # Cached, error-safe
```

### Custom Error Messages

```python
from src.utils.error_handling import with_error_handling

@with_error_handling(
    fallback_value=pd.DataFrame(),
    show_error=True,
    error_message="Unable to fetch positions. Please try again later."
)
def get_positions():
    return api.fetch_positions()
```

### Raising Custom Exceptions

```python
from src.utils.error_handling import APIRateLimitError, DataNotAvailableError

def fetch_data():
    if rate_limit_exceeded:
        raise APIRateLimitError("API rate limit exceeded")

    if service_down:
        raise DataNotAvailableError("Service temporarily unavailable")

    return data
```

### Full Example

```python
import streamlit as st
from src.utils.error_handling import with_error_handling, safe_cache_data, APIRateLimitError

@safe_cache_data(ttl=300)
def get_cached_positions():
    """Get positions with caching and error handling"""
    return database.query_positions()

@with_error_handling(fallback_value=[], show_error=True)
def fetch_live_prices(symbols):
    """Fetch live prices with error handling"""
    if api.rate_limit_reached():
        raise APIRateLimitError("Rate limit reached")

    return api.get_prices(symbols)

# Usage in your page
st.title("Positions")

positions = get_cached_positions()  # Cached and error-safe
if positions:
    prices = fetch_live_prices([p['symbol'] for p in positions])
    st.dataframe(positions)
else:
    st.info("No positions found")
```

---

## 3. Cache Metrics Dashboard

### Accessing the Dashboard

1. Navigate to AVA Platform
2. Click "AVA Management" in the sidebar
3. Click "Cache Metrics"

### Key Metrics

- **Cache Hit Rate**: Percentage of requests served from cache (target: 85%+)
- **Time Saved**: Total time saved by cache hits this session
- **Queries Eliminated**: Number of database queries avoided
- **Uptime**: How long the system has been running

### Actions Available

- **Clear All Caches**: Force-clear all cached data (use sparingly)
- **Reset Metrics**: Reset performance metrics to zero
- **Warm Caches Now**: Pre-load critical caches for instant access

### Best Practices

1. Monitor cache hit rate regularly (target: 85%+)
2. Clear caches only when data seems stale
3. Use "Warm Caches" before heavy analysis sessions
4. Report consistently slow pages for optimization

---

## 4. Cache Warming System

### How It Works

Cache warming runs automatically on dashboard startup:

```python
# Happens automatically - no code needed
# Located in dashboard.py lines 63-121

# Warms these caches in background:
# 1. Positions (7 days of closed trades)
# 2. XTrades (100 active trades + profiles)
# 3. Kalshi markets (all markets)
```

### Manual Cache Warming

If you need to warm additional caches:

```python
# In your page file
@st.cache_data(ttl=300)
def get_my_data():
    return expensive_operation()

# Manually trigger warming (optional)
if st.button("Pre-load Data"):
    with st.spinner("Loading..."):
        get_my_data()  # Warms the cache
    st.success("Data ready!")
```

### Benefits

- First page visit is instant (no waiting)
- Background execution (non-blocking)
- Graceful error handling (won't crash app)
- Reduces API/database load

---

## 5. Integration Examples

### Example 1: Paginated Table with Error Handling

```python
import streamlit as st
import pandas as pd
from src.components.pagination_component import paginate_dataframe
from src.utils.error_handling import safe_cache_data

@safe_cache_data(ttl=300)
def get_trade_history(days_back):
    """Get trade history with caching and error handling"""
    return database.query_trades(days_back)

st.title("Trade History")

days = st.selectbox("Days", [7, 30, 90])
trades = get_trade_history(days)

if trades and len(trades) > 0:
    df = pd.DataFrame(trades)

    # Paginate large datasets
    paginated = paginate_dataframe(
        df=df,
        page_size=50,
        key_prefix="trade_history"
    )

    st.dataframe(paginated, use_container_width=True)
else:
    st.info("No trades found")
```

### Example 2: API Integration with Rate Limit Handling

```python
import streamlit as st
from src.utils.error_handling import with_error_handling, APIRateLimitError

@with_error_handling(
    fallback_value=None,
    show_error=True,
    error_message="API temporarily unavailable. Showing cached data."
)
def fetch_market_data():
    """Fetch market data with rate limit handling"""
    if api_client.is_rate_limited():
        raise APIRateLimitError("Rate limit exceeded")

    return api_client.get_market_data()

# Usage
data = fetch_market_data()
if data:
    st.success("Live data loaded")
    display_data(data)
else:
    st.warning("Using cached data")
    display_cached_data()
```

### Example 3: Complete Page with All Features

```python
import streamlit as st
import pandas as pd
from src.components.pagination_component import paginate_dataframe
from src.utils.error_handling import safe_cache_data, with_error_handling

# Cached data fetching with error handling
@safe_cache_data(ttl=300)
def get_options_data(min_premium):
    """Get options data with caching and error handling"""
    return database.query_options(min_premium)

@with_error_handling(fallback_value={})
def get_account_info():
    """Get account info with error handling"""
    return api.get_account()

# Page
st.title("Options Analysis")

# Filters
min_premium = st.number_input("Min Premium", value=1.0, min_value=0.0)

# Fetch data (cached and error-safe)
options = get_options_data(min_premium)
account = get_account_info()

# Display account info
if account:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Balance", f"${account.get('balance', 0):,.2f}")
    with col2:
        st.metric("Buying Power", f"${account.get('buying_power', 0):,.2f}")
    with col3:
        st.metric("Positions", account.get('positions', 0))

# Display options with pagination
if options and len(options) > 0:
    df = pd.DataFrame(options)

    st.markdown(f"### Found {len(df):,} Options")

    # Paginate for performance
    paginated = paginate_dataframe(
        df=df,
        page_size=50,
        key_prefix="options_table"
    )

    st.dataframe(
        paginated.style.background_gradient(subset=['Premium'], cmap='RdYlGn'),
        use_container_width=True
    )
else:
    st.info("No options found. Try adjusting filters.")

# Cache metrics link
st.caption("View performance metrics in [Cache Metrics](/Cache_Metrics) page")
```

---

## Performance Tips

### 1. Caching Strategy

- Use `@st.cache_data(ttl=300)` for database queries (5 minutes)
- Use `@st.cache_data(ttl=60)` for real-time data (1 minute)
- Use `@st.cache_resource` for connections/models (persistent)

### 2. Pagination Strategy

- Paginate any table with 50+ rows
- Use page_size=50 for most cases
- Use page_size=25 for complex calculations
- Use page_size=100 for simple data

### 3. Error Handling Strategy

- Use `@safe_cache_data` for all database queries
- Use `@with_error_handling` for all API calls
- Always provide meaningful fallback values
- Set show_error=True for user-facing functions

### 4. Monitoring Strategy

- Check Cache Metrics weekly
- Aim for 85%+ cache hit rate
- Clear caches only when truly needed
- Report slow pages for optimization

---

## Common Issues & Solutions

### Issue: Pagination not working

**Solution**: Ensure `key_prefix` is unique
```python
# Bad (duplicate keys)
paginate_dataframe(df1, key_prefix="table")
paginate_dataframe(df2, key_prefix="table")  # Conflict!

# Good (unique keys)
paginate_dataframe(df1, key_prefix="trades_table")
paginate_dataframe(df2, key_prefix="positions_table")
```

### Issue: Cache not updating

**Solution**: Check TTL or clear cache
```python
# Option 1: Reduce TTL
@st.cache_data(ttl=60)  # Cache for 1 minute instead of 5

# Option 2: Add cache clear button
if st.button("Refresh Data"):
    st.cache_data.clear()
    st.rerun()
```

### Issue: Error messages not showing

**Solution**: Ensure show_error=True
```python
# Bad (silent failures)
@with_error_handling(fallback_value=[], show_error=False)

# Good (user feedback)
@with_error_handling(fallback_value=[], show_error=True)
```

---

## Migration Guide

### Before (Old Code)

```python
# Manual pagination (inconsistent)
start = st.session_state.get('page', 0) * 50
end = start + 50
st.dataframe(df.iloc[start:end])

# No error handling (crashes on error)
def get_data():
    return api.fetch()  # Crashes if API fails

# No caching (slow)
positions = database.query()  # Hits database every time
```

### After (New Code)

```python
from src.components.pagination_component import paginate_dataframe
from src.utils.error_handling import safe_cache_data, with_error_handling

# Consistent pagination
paginated = paginate_dataframe(df, page_size=50, key_prefix="my_table")
st.dataframe(paginated)

# Graceful error handling
@with_error_handling(fallback_value=[])
def get_data():
    return api.fetch()  # Returns [] if API fails

# Fast caching
@safe_cache_data(ttl=300)
def get_positions():
    return database.query()  # Cached for 5 minutes
```

---

## Additional Resources

- **Full Documentation**: See `PERFORMANCE_ENHANCEMENTS_IMPLEMENTATION_COMPLETE.md`
- **Source Code**:
  - Pagination: `src/components/pagination_component.py`
  - Error Handling: `src/utils/error_handling.py`
  - Cache Metrics: `cache_metrics_page.py`
  - Cache Warming: `dashboard.py` lines 63-121

- **Support**: Check Cache Metrics dashboard for performance insights
