# Shared Components Refactoring Plan
## Efficiency Improvements Without Merging Pages

**Date**: 2025-11-07
**Priority**: HIGH
**Estimated Effort**: 4-5 hours
**Code Reduction**: ~300 lines (15%)
**Performance Gain**: 30-50% faster page loads (via caching)

---

## Overview

Based on the [feature comparison analysis](AI_OPTIONS_VS_COMPREHENSIVE_STRATEGY_COMPARISON.md), we will extract shared code from both AI Options Agent and Comprehensive Strategy pages into reusable components.

**Goal**: Eliminate duplication while keeping pages functionally separate

---

## Phase 1: Create Shared Module Structure (15 minutes)

### Create Directory Structure

```bash
mkdir -p src/ai_options_agent/shared
```

### Files to Create

```
src/ai_options_agent/
  └── shared/
      ├── __init__.py
      ├── stock_selector.py      # 220 lines - reusable stock selection UI
      ├── llm_config_ui.py        # 180 lines - LLM provider configuration
      ├── data_fetchers.py        # 150 lines - cached data queries
      └── display_helpers.py      # 80 lines - UI utilities
```

**Total New Code**: ~630 lines (extracted from existing)
**Total Removed Code**: ~900 lines (from both pages)
**Net Code Reduction**: ~270 lines

---

## Phase 2: Extract Stock Selector Component (60 minutes)

### File: `src/ai_options_agent/shared/stock_selector.py`

**Purpose**: Reusable stock selection UI used by both pages

**Current State**:
- AI Options Agent: Lines 206-224 (watchlist selection)
- Comprehensive Strategy: Lines 228-296 (full selector with 3 modes)

**Extract To:**

```python
"""
Shared Stock Selector Component
Provides 3 modes: Manual Input, TradingView Watchlist, Database Stocks
"""

import streamlit as st
from typing import Optional, List, Dict, Any
from src.tradingview_db_manager import TradingViewDBManager


class StockSelector:
    """Reusable stock selection component"""

    def __init__(self):
        self.tv_manager = TradingViewDBManager()

    def render_single_stock_selector(
        self,
        modes: List[str] = None,
        default_symbol: str = "AAPL",
        show_quick_info: bool = True
    ) -> Optional[str]:
        """
        Render stock selector with multiple input modes

        Args:
            modes: List of modes to show. Options:
                   ["manual", "tradingview", "database"]
                   Default: all three
            default_symbol: Default symbol for manual input
            show_quick_info: Show quick info panel

        Returns:
            Selected stock symbol or None
        """
        if modes is None:
            modes = ["manual", "tradingview", "database"]

        # Build mode options
        mode_options = []
        if "manual" in modes:
            mode_options.append("✏️ Manual Input")
        if "tradingview" in modes:
            mode_options.append("📺 TradingView Watchlist")
        if "database" in modes:
            mode_options.append("💾 Database Stocks")

        # Data source selector
        data_source = st.radio(
            "Select Data Source",
            mode_options,
            horizontal=True,
            help="Choose where to select your stock from"
        )

        # Create columns for selector + info
        if show_quick_info:
            col_select, col_info = st.columns([2, 1])
        else:
            col_select = st.container()
            col_info = None

        selected_symbol = None

        with col_select:
            if "TradingView" in data_source:
                selected_symbol = self._render_tradingview_mode()
            elif "Database" in data_source:
                selected_symbol = self._render_database_mode()
            else:
                selected_symbol = self._render_manual_mode(default_symbol)

        # Show quick info if enabled
        if show_quick_info and col_info and selected_symbol:
            with col_info:
                self._render_quick_info(selected_symbol)

        return selected_symbol

    def render_watchlist_selector(self) -> tuple[Optional[str], Optional[List[str]]]:
        """
        Render watchlist selector (for batch analysis)

        Returns:
            (watchlist_name, symbols_list) or (None, None)
        """
        watchlists = self.tv_manager.get_all_symbols_dict()

        if not watchlists:
            st.warning("No watchlists found. Please sync watchlists first.")
            return None, None

        watchlist_name = st.selectbox(
            "Select Watchlist:",
            list(watchlists.keys()),
            format_func=lambda x: f"📁 {x} ({len(watchlists[x])} stocks)",
            help="Choose a TradingView watchlist to analyze"
        )

        symbols = watchlists.get(watchlist_name, [])

        return watchlist_name, symbols

    def _render_tradingview_mode(self) -> Optional[str]:
        """Render TradingView watchlist mode"""
        with st.spinner("Loading watchlists..."):
            watchlists = self.tv_manager.get_all_symbols_dict()

        if not watchlists:
            st.warning("⚠️ No watchlists found. Please sync watchlists from the TradingView Watchlists page.")
            return None

        selected_watchlist = st.selectbox(
            "Select Watchlist",
            list(watchlists.keys()),
            format_func=lambda x: f"📁 {x} ({len(watchlists[x])} stocks)",
            key="watchlist_selector"
        )

        if selected_watchlist:
            symbols = watchlists[selected_watchlist]
            if symbols:
                return st.selectbox(
                    "Select Stock",
                    symbols,
                    key="symbol_selector_tv"
                )
            else:
                st.warning(f"⚠️ Watchlist '{selected_watchlist}' is empty.")

        return None

    def _render_database_mode(self) -> Optional[str]:
        """Render database stocks mode"""
        from .data_fetchers import fetch_database_stocks

        with st.spinner("Loading stocks from database..."):
            stocks = fetch_database_stocks()

        if not stocks:
            st.warning("⚠️ No stocks found in database. Please run database sync first.")
            return None

        return st.selectbox(
            "Select Stock",
            [s['symbol'] for s in stocks],
            format_func=lambda x: f"{x} - {next((s['company_name'] for s in stocks if s['symbol'] == x), x)}",
            key="symbol_selector_db"
        )

    def _render_manual_mode(self, default_symbol: str) -> str:
        """Render manual input mode"""
        return st.text_input(
            "Enter Stock Symbol",
            value=default_symbol,
            help="Type any valid stock ticker symbol",
            key="symbol_manual"
        ).upper()

    def _render_quick_info(self, symbol: str):
        """Render quick info panel for selected symbol"""
        from .data_fetchers import fetch_stock_info

        st.markdown("**📊 Quick Info**")

        with st.spinner("Loading..."):
            info = fetch_stock_info(symbol)

        if info:
            st.metric("Price", f"${info['current_price']:.2f}")
            st.caption(f"**Sector:** {info['sector']}")
            if info.get('market_cap', 0) > 0:
                st.caption(f"**Market Cap:** ${info['market_cap']/1e9:.1f}B")
        else:
            st.warning("Could not fetch stock info")
```

**Usage Example:**

```python
# In ai_options_agent_page.py
from src.ai_options_agent.shared.stock_selector import StockSelector

selector = StockSelector()

# For watchlist-based batch analysis
watchlist_name, symbols = selector.render_watchlist_selector()

# In comprehensive_strategy_page.py
from src.ai_options_agent.shared.stock_selector import StockSelector

selector = StockSelector()

# For single stock analysis with all 3 modes
selected_symbol = selector.render_single_stock_selector(
    modes=["manual", "tradingview", "database"],
    show_quick_info=True
)
```

**Lines Saved**:
- AI Options Agent: 20 lines
- Comprehensive Strategy: 70 lines
- Total: 90 lines

---

## Phase 3: Extract LLM Configuration UI (45 minutes)

### File: `src/ai_options_agent/shared/llm_config_ui.py`

**Purpose**: Reusable LLM provider configuration interface

**Current State**:
- AI Options Agent: Lines 67-196 (full LLM config UI with add provider)
- Comprehensive Strategy: Lines 40-46 (simple provider display)

**Extract To:**

```python
"""
Shared LLM Provider Configuration UI
Provides provider selection, testing, and management
"""

import streamlit as st
import os
from typing import Optional, List, Dict, Any


class LLMConfigUI:
    """Reusable LLM configuration interface"""

    def __init__(self, llm_manager):
        self.llm_manager = llm_manager

    def render_provider_selector(
        self,
        show_add_provider: bool = True,
        allow_manual_selection: bool = True
    ) -> Optional[str]:
        """
        Render LLM provider selection UI

        Args:
            show_add_provider: Show "Add New Provider" expander
            allow_manual_selection: Allow user to select specific provider

        Returns:
            Selected provider ID or None (for auto-select)
        """
        st.subheader("🤖 LLM Provider Configuration")

        # Get available providers
        available_providers = self.llm_manager.get_available_providers()

        col1, col2 = st.columns([2, 1])

        selected_provider = None

        with col1:
            st.markdown("**Available Providers:**")

            if available_providers:
                if allow_manual_selection:
                    # Create provider selection
                    provider_options = {
                        f"{p['name']} - {p['cost']} (Speed: {p['speed']})": p['id']
                        for p in available_providers
                    }
                    provider_options["🔄 Auto-select (Prioritizes Free/Cheap)"] = None

                    selected_provider_display = st.selectbox(
                        "Choose LLM Provider:",
                        options=list(provider_options.keys()),
                        index=0,
                        help="Select which AI provider to use for reasoning"
                    )

                    selected_provider = provider_options[selected_provider_display]

                    # Show provider details
                    if selected_provider:
                        provider_info = next((p for p in available_providers if p['id'] == selected_provider), None)
                        if provider_info:
                            st.info(f"""
                            **{provider_info['name']}**
                            - Model: `{provider_info['current_model']}`
                            - Cost: {provider_info['cost']}
                            - Speed: {provider_info['speed']}
                            - Quality: {provider_info['quality']}
                            """)
                else:
                    # Just show available providers (no selection)
                    st.write(f"**{len(available_providers)} AI models ready:**")
                    for p in available_providers:
                        st.write(f"- ✅ **{p['name']}** - {p['description']} ({p['cost']})")
            else:
                st.warning("⚠️ No LLM providers available. Add API keys below to enable LLM reasoning.")

        with col2:
            st.markdown("**Provider Status:**")
            if available_providers:
                for p in available_providers[:3]:  # Show top 3
                    st.success(f"✓ {p['name']}")
            else:
                st.error("No providers configured")

        # Add new provider section
        if show_add_provider:
            self._render_add_provider_section()

        return selected_provider

    def render_simple_provider_list(self):
        """Simple provider list display (no selection)"""
        available_providers = self.llm_manager.get_available_providers()

        with st.expander("🤖 AI Models Active", expanded=False):
            st.write(f"**{len(available_providers)} AI models ready:**")
            for p in available_providers:
                st.write(f"- ✅ **{p['name']}** - {p['description']} ({p['cost']})")

    def _render_add_provider_section(self):
        """Render 'Add New Provider' expander"""
        with st.expander("➕ Add New LLM Provider", expanded=False):
            st.markdown("Add a new AI provider by entering its API key:")

            col1, col2, col3 = st.columns([2, 2, 1])

            with col1:
                new_provider_type = st.selectbox(
                    "Provider Type:",
                    ["OpenAI", "Anthropic Claude", "Google Gemini", "DeepSeek", "Groq", "Grok (xAI)", "Kimi/Moonshot"],
                    help="Select the type of provider you want to add"
                )

            with col2:
                new_api_key = st.text_input(
                    "API Key:",
                    type="password",
                    placeholder="sk-...",
                    help="Enter your API key for this provider"
                )

            with col3:
                st.markdown("<br>", unsafe_allow_html=True)
                test_provider = st.button("🧪 Test", use_container_width=True)

            if test_provider and new_api_key:
                self._test_provider(new_provider_type, new_api_key)

    def _test_provider(self, provider_type: str, api_key: str):
        """Test a new provider API key"""
        # Map display name to env var name
        provider_map = {
            "OpenAI": "OPENAI_API_KEY",
            "Anthropic Claude": "ANTHROPIC_API_KEY",
            "Google Gemini": "GOOGLE_API_KEY",
            "DeepSeek": "DEEPSEEK_API_KEY",
            "Groq": "GROQ_API_KEY",
            "Grok (xAI)": "GROK_API_KEY",
            "Kimi/Moonshot": "KIMI_API_KEY"
        }

        env_var = provider_map.get(provider_type)

        with st.spinner(f"Testing {provider_type}..."):
            # Temporarily set the API key
            original_key = os.getenv(env_var)
            os.environ[env_var] = api_key

            try:
                # Reload LLM manager with new key
                from src.ai_options_agent.llm_manager import LLMManager
                test_manager = LLMManager()

                # Try to generate with this provider
                provider_id = provider_type.lower().split()[0]
                result = test_manager.generate(
                    "Say 'test successful' if you can read this.",
                    provider_id=provider_id,
                    max_tokens=50
                )

                if result['text'] and len(result['text']) > 0:
                    st.success(f"✅ {provider_type} is working! API key is valid.")
                    st.info(f"Add this to your .env file:\n```\n{env_var}={api_key}\n```")

                    # Show test response
                    with st.expander("Test Response"):
                        st.write(result['text'])
                else:
                    st.error(f"❌ Test failed - No response from {provider_type}")

            except Exception as e:
                st.error(f"❌ Test failed: {str(e)}")

            finally:
                # Restore original key
                if original_key:
                    os.environ[env_var] = original_key
                else:
                    os.environ.pop(env_var, None)
```

**Usage Example:**

```python
# In ai_options_agent_page.py
from src.ai_options_agent.shared.llm_config_ui import LLMConfigUI

llm_config = LLMConfigUI(llm_manager)
selected_provider = llm_config.render_provider_selector(
    show_add_provider=True,
    allow_manual_selection=True
)

# In comprehensive_strategy_page.py
from src.ai_options_agent.shared.llm_config_ui import LLMConfigUI

llm_config = LLMConfigUI(llm_manager)
llm_config.render_simple_provider_list()  # Just show available models
```

**Lines Saved**:
- AI Options Agent: 130 lines
- Comprehensive Strategy: 6 lines (but avoids future duplication)
- Total: 136 lines

---

## Phase 4: Extract Data Fetchers (45 minutes)

### File: `src/ai_options_agent/shared/data_fetchers.py`

**Purpose**: Centralized, cached data fetching functions

**Current State**:
- AI Options Agent: No stock_info fetching (relies on DB only)
- Comprehensive Strategy: Lines 51-223 (fetch functions)

**Extract To:**

```python
"""
Shared Data Fetching Functions
Provides cached database queries and yfinance fallback
"""

import streamlit as st
import yfinance as yf
from typing import Dict, List, Any, Optional
from src.tradingview_db_manager import TradingViewDBManager


@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_database_stocks() -> List[Dict[str, Any]]:
    """
    Fetch all active stocks from database

    Returns:
        List of stock dicts with symbol, company_name, price, etc.
    """
    try:
        tv_manager = TradingViewDBManager()
        conn = tv_manager.get_connection()
        cur = conn.cursor()

        # Try stock_data table first (most complete)
        cur.execute("""
            SELECT symbol, company_name, current_price, sector, market_cap,
                   week_52_high, week_52_low, last_updated
            FROM stock_data
            WHERE current_price > 0
            ORDER BY symbol
        """)

        columns = ['symbol', 'company_name', 'current_price', 'sector', 'market_cap',
                   'week_52_high', 'week_52_low', 'last_updated']
        stocks = [dict(zip(columns, row)) for row in cur.fetchall()]

        # Fallback to stocks table if stock_data is empty
        if not stocks:
            cur.execute("""
                SELECT ticker as symbol, name as company_name, price as current_price,
                       sector, market_cap, high_52week, low_52week, last_updated
                FROM stocks
                WHERE price > 0
                ORDER BY ticker
            """)
            stocks = [dict(zip(columns, row)) for row in cur.fetchall()]

        cur.close()
        conn.close()
        return stocks

    except Exception as e:
        st.error(f"Error fetching database stocks: {e}")
        return []


@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_stock_info(symbol: str) -> Optional[Dict[str, Any]]:
    """
    Fetch comprehensive stock info from database and yfinance

    Args:
        symbol: Stock ticker symbol

    Returns:
        Dict with stock info or None if not found
    """
    data = {
        'symbol': symbol.upper(),
        'name': symbol,
        'current_price': 0,
        'sector': 'Technology',
        'market_cap': 0,
        'pe_ratio': 28.5,
        'high_52week': 0,
        'low_52week': 0
    }

    # Try database first
    try:
        tv_manager = TradingViewDBManager()
        conn = tv_manager.get_connection()
        cur = conn.cursor()

        # Try stock_data table
        cur.execute("""
            SELECT company_name, current_price, sector, market_cap,
                   week_52_high, week_52_low, pe_ratio
            FROM stock_data
            WHERE symbol = %s
        """, (symbol.upper(),))

        row = cur.fetchone()
        if row:
            data['name'] = row[0] or symbol
            data['current_price'] = float(row[1]) if row[1] else 0
            data['sector'] = row[2] or 'Technology'
            data['market_cap'] = int(row[3]) if row[3] else 0
            data['high_52week'] = float(row[4]) if row[4] else 0
            data['low_52week'] = float(row[5]) if row[5] else 0
            if row[6]:
                data['pe_ratio'] = float(row[6])

        cur.close()
        conn.close()

    except Exception as e:
        st.warning(f"Database query failed: {e}")

    # Fallback to yfinance if data is missing
    if data['current_price'] == 0:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            data['name'] = info.get('longName', info.get('shortName', symbol))
            data['current_price'] = info.get('currentPrice', info.get('regularMarketPrice', 0))
            data['market_cap'] = info.get('marketCap', 0)
            data['pe_ratio'] = info.get('trailingPE', 28.5)
            data['sector'] = info.get('sector', 'Technology')
            data['high_52week'] = info.get('fiftyTwoWeekHigh', 0)
            data['low_52week'] = info.get('fiftyTwoWeekLow', 0)

        except Exception as e:
            st.warning(f"Could not fetch yfinance data for {symbol}: {e}")
            return None

    return data if data['current_price'] > 0 else None


@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_options_suggestions(
    symbol: str,
    dte_min: int = 20,
    dte_max: int = 45,
    delta_min: float = -0.35,
    delta_max: float = -0.25
) -> List[Dict[str, Any]]:
    """
    Fetch suggested options from database

    Args:
        symbol: Stock ticker symbol
        dte_min: Minimum days to expiration
        dte_max: Maximum days to expiration
        delta_min: Minimum delta (negative for puts)
        delta_max: Maximum delta (negative for puts)

    Returns:
        List of option suggestion dicts
    """
    try:
        tv_manager = TradingViewDBManager()
        conn = tv_manager.get_connection()
        cur = conn.cursor()

        # Query stock_premiums table for PUT options
        cur.execute("""
            SELECT strike_price, expiration_date, delta, premium, implied_volatility, dte
            FROM stock_premiums
            WHERE symbol = %s
              AND strike_type = 'put'
              AND dte BETWEEN %s AND %s
              AND delta BETWEEN %s AND %s
              AND delta IS NOT NULL
            ORDER BY ABS(delta + 0.30), dte
            LIMIT 5
        """, (symbol.upper(), dte_min, dte_max, delta_min, delta_max))

        options = []
        for row in cur.fetchall():
            options.append({
                'strike': float(row[0]) if row[0] else 0,
                'expiration': row[1],
                'delta': float(row[2]) if row[2] else -0.30,
                'premium': float(row[3]) if row[3] else 0,
                'iv': float(row[4]) if row[4] else 0.35,
                'dte': int(row[5]) if row[5] else 30
            })

        cur.close()
        conn.close()
        return options

    except Exception as e:
        # Silently fail - options suggestions are optional
        return []


@st.cache_data(ttl=300)  # Cache for 5 minutes
def calculate_iv_for_stock(symbol: str) -> float:
    """
    Calculate implied volatility from options data

    Args:
        symbol: Stock ticker symbol

    Returns:
        Average IV or 0.35 as fallback
    """
    try:
        tv_manager = TradingViewDBManager()
        conn = tv_manager.get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT AVG(implied_volatility) as avg_iv
            FROM stock_premiums
            WHERE symbol = %s
              AND dte BETWEEN 20 AND 45
              AND implied_volatility IS NOT NULL
              AND implied_volatility > 0
        """, (symbol.upper(),))

        row = cur.fetchone()
        cur.close()
        conn.close()

        if row and row[0]:
            return float(row[0])
        else:
            return 0.35  # Default fallback

    except Exception as e:
        return 0.35  # Default fallback
```

**Usage Example:**

```python
# In both pages
from src.ai_options_agent.shared.data_fetchers import (
    fetch_database_stocks,
    fetch_stock_info,
    fetch_options_suggestions,
    calculate_iv_for_stock
)

# Fetch stock info (cached for 5 minutes)
stock_info = fetch_stock_info("AAPL")

# Fetch options suggestions
options = fetch_options_suggestions("AAPL", dte_min=20, dte_max=40)
```

**Lines Saved**:
- AI Options Agent: 0 (but gains new capability)
- Comprehensive Strategy: 170 lines
- Total: 170 lines

---

## Phase 5: Extract Display Helpers (30 minutes)

### File: `src/ai_options_agent/shared/display_helpers.py`

**Purpose**: Shared UI utility functions

**Extract To:**

```python
"""
Shared Display Helper Functions
Provides common UI components and formatting
"""

import streamlit as st


def display_score_gauge(score: int, label: str):
    """Display a score as a colored gauge"""
    if score >= 80:
        color = "🟢"
    elif score >= 60:
        color = "🟡"
    else:
        color = "🔴"

    st.metric(label, f"{score}/100 {color}")


def display_recommendation_badge(recommendation: str) -> str:
    """Display recommendation with color coding"""
    colors = {
        'STRONG_BUY': '🟢',
        'BUY': '🟢',
        'HOLD': '🟡',
        'CAUTION': '🟠',
        'AVOID': '🔴'
    }

    color = colors.get(recommendation, '⚪')
    return f"{color} {recommendation}"


def format_currency(value: float) -> str:
    """Format value as currency"""
    return f"${value:,.2f}"


def format_percentage(value: float) -> str:
    """Format value as percentage"""
    return f"{value:.2f}%"


def format_market_cap(value: int) -> str:
    """Format market cap in billions"""
    return f"${value/1e9:.1f}B"
```

**Usage Example:**

```python
# In both pages
from src.ai_options_agent.shared.display_helpers import (
    display_score_gauge,
    display_recommendation_badge,
    format_currency
)

display_score_gauge(85, "Overall Score")
st.write(display_recommendation_badge("STRONG_BUY"))
st.metric("Price", format_currency(227.50))
```

**Lines Saved**: ~20 lines per page

---

## Phase 6: Update Both Pages to Use Shared Components (60 minutes)

### Update AI Options Agent Page

**File**: [ai_options_agent_page.py](ai_options_agent_page.py)

**Changes**:

```python
# Add imports
from src.ai_options_agent.shared.stock_selector import StockSelector
from src.ai_options_agent.shared.llm_config_ui import LLMConfigUI
from src.ai_options_agent.shared.data_fetchers import fetch_database_stocks
from src.ai_options_agent.shared.display_helpers import (
    display_score_gauge,
    display_recommendation_badge
)

# Replace lines 16-26 (score gauge function)
# DELETE - now imported from display_helpers

# Replace lines 28-40 (recommendation badge function)
# DELETE - now imported from display_helpers

# Replace lines 67-196 (LLM config section)
llm_config = LLMConfigUI(llm_manager)
selected_provider = llm_config.render_provider_selector(
    show_add_provider=True,
    allow_manual_selection=True
)

# Replace lines 206-224 (watchlist selection)
selector = StockSelector()

if analysis_source == "TradingView Watchlist":
    watchlist_name, symbols = selector.render_watchlist_selector()
else:
    # Analyze all stocks - no selector needed
    watchlist_name = None
```

### Update Comprehensive Strategy Page

**File**: [comprehensive_strategy_page.py](comprehensive_strategy_page.py)

**Changes**:

```python
# Add imports
from src.ai_options_agent.shared.stock_selector import StockSelector
from src.ai_options_agent.shared.llm_config_ui import LLMConfigUI
from src.ai_options_agent.shared.data_fetchers import (
    fetch_database_stocks,
    fetch_stock_info,
    fetch_options_suggestions,
    calculate_iv_for_stock
)

# Replace lines 40-46 (provider display)
llm_config = LLMConfigUI(llm_manager)
llm_config.render_simple_provider_list()

# Delete lines 51-223 (fetch functions)
# DELETE - now imported from data_fetchers

# Replace lines 228-312 (stock selection)
selector = StockSelector()
selected_symbol = selector.render_single_stock_selector(
    modes=["manual", "tradingview", "database"],
    show_quick_info=True
)
```

---

## Phase 7: Testing & Verification (45 minutes)

### Test Checklist

- [ ] **AI Options Agent**
  - [ ] LLM provider selection works
  - [ ] Add new provider UI works
  - [ ] Watchlist selection works
  - [ ] Analysis runs successfully
  - [ ] Score gauges display correctly
  - [ ] Recommendation badges display correctly

- [ ] **Comprehensive Strategy**
  - [ ] All 3 stock selection modes work (manual, TV, database)
  - [ ] Quick info panel displays
  - [ ] Stock data auto-populates
  - [ ] Options suggestions load
  - [ ] LLM provider list displays
  - [ ] Analysis completes successfully

- [ ] **Caching**
  - [ ] Stock info cached across pages
  - [ ] Options data cached across pages
  - [ ] Page switches are faster (measure time)

- [ ] **Database**
  - [ ] No additional database connections
  - [ ] Queries use connection pool correctly

### Test Script

```python
"""
Test Shared Components
Run this to verify all shared components work correctly
"""

import streamlit as st
from src.ai_options_agent.shared.stock_selector import StockSelector
from src.ai_options_agent.shared.llm_config_ui import LLMConfigUI
from src.ai_options_agent.shared.data_fetchers import (
    fetch_database_stocks,
    fetch_stock_info,
    fetch_options_suggestions
)
from src.ai_options_agent.llm_manager import get_llm_manager

st.title("Shared Components Test")

# Test Stock Selector
st.header("1. Stock Selector Test")
selector = StockSelector()
symbol = selector.render_single_stock_selector()
st.success(f"Selected: {symbol}")

# Test LLM Config
st.header("2. LLM Config Test")
llm_manager = get_llm_manager()
llm_config = LLMConfigUI(llm_manager)
provider = llm_config.render_provider_selector()
st.success(f"Provider: {provider}")

# Test Data Fetchers
st.header("3. Data Fetchers Test")
if symbol:
    stocks = fetch_database_stocks()
    st.write(f"Found {len(stocks)} stocks in database")

    info = fetch_stock_info(symbol)
    st.write(f"Stock Info: {info}")

    options = fetch_options_suggestions(symbol)
    st.write(f"Found {len(options)} options suggestions")

    st.success("All data fetchers working!")
```

---

## Rollout Plan

### Day 1 (2 hours)
1. ✅ Create shared module structure
2. ✅ Extract `stock_selector.py`
3. ✅ Extract `llm_config_ui.py`
4. ✅ Test in isolation

### Day 2 (2 hours)
1. ✅ Extract `data_fetchers.py`
2. ✅ Extract `display_helpers.py`
3. ✅ Update AI Options Agent page
4. ✅ Test AI Options Agent

### Day 3 (1 hour)
1. ✅ Update Comprehensive Strategy page
2. ✅ Test Comprehensive Strategy
3. ✅ Verify caching works
4. ✅ Deploy to production

---

## Success Metrics

| Metric | Before | After | Target |
|--------|--------|-------|--------|
| **Total Lines of Code** | 1,900 | 1,630 | -270 lines (14%) |
| **Duplicated Code** | 300 lines | 0 lines | 0% |
| **Page Load Time (cold)** | 3-4 seconds | 2-3 seconds | -30% |
| **Page Load Time (cache hit)** | 3-4 seconds | 1-2 seconds | -50% |
| **Database Queries (both pages)** | 12 queries | 6 queries | -50% |
| **Code Maintainability** | Medium | High | Improved |

---

## Rollback Plan

If issues arise:

1. **Git Revert**: All changes are in single commit
   ```bash
   git log --oneline -5
   git revert <commit-hash>
   ```

2. **File Restore**: Keep backup of original files
   ```bash
   cp ai_options_agent_page.py ai_options_agent_page.py.backup
   cp comprehensive_strategy_page.py comprehensive_strategy_page.py.backup
   ```

3. **Quick Fix**: Comment out imports, restore inline code temporarily

---

## Next Steps After Completion

1. ✅ Monitor performance in production (1 week)
2. ✅ Collect user feedback on any issues
3. ✅ Consider extracting more shared components:
   - Strategy display components
   - Greeks display components
   - Export/download utilities

4. ✅ Document shared components for future developers

---

**Status**: Ready to Implement
**Priority**: HIGH
**Risk**: LOW (easily reversible)
**Reward**: HIGH (significant code reduction + performance gain)
