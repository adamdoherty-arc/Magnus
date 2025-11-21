"""
Centralized Data Layer
======================

Provides cached, reusable query functions for the trading dashboard.

Features:
- Connection pooling for efficient database access
- Multi-tier caching (SHORT, MEDIUM, LONG TTL)
- Graceful error handling
- SQL injection prevention via parameterized queries
- Type hints and comprehensive docstrings

Modules:
- cache_manager: Caching utilities and decorators
- stock_queries: Stock data query functions
- options_queries: Options and premium data query functions

Quick Start:
    from src.data import (
        get_stock_info,
        get_all_stocks,
        get_options_chain,
        get_premium_opportunities
    )

    # Get stock info
    stock = get_stock_info("AAPL")
    print(f"{stock['company_name']}: ${stock['current_price']}")

    # Find CSP opportunities
    opportunities = get_premium_opportunities({
        'min_premium_pct': 1.5,
        'min_annual_return': 20.0
    })

Cache Management:
    from src.data import clear_all_caches, get_cache_stats

    # View cache configuration
    stats = get_cache_stats()

    # Clear all caches if needed
    clear_all_caches()
"""

# Cache Management
from src.data.cache_manager import (
    cache_with_ttl,
    CacheTier,
    cache_short,
    cache_medium,
    cache_long,
    invalidate_cache,
    get_cache_stats,
    clear_all_caches
)

# Stock Queries
from src.data.stock_queries import (
    get_stock_info,
    get_all_stocks,
    get_stocks_by_sector,
    search_stocks,
    get_stock_price_history,
    get_watchlist_stocks,
    get_all_sectors,
    get_stocks_by_market_cap,
    get_stock_count
)

# Options Queries
from src.data.options_queries import (
    get_options_chain,
    get_premium_opportunities,
    get_options_by_strike,
    get_historical_premiums,
    get_high_iv_stocks,
    calculate_expected_return,
    get_options_summary_by_symbol,
    get_best_strikes_for_csp
)

# Public API
__all__ = [
    # Cache Management
    'cache_with_ttl',
    'CacheTier',
    'cache_short',
    'cache_medium',
    'cache_long',
    'invalidate_cache',
    'get_cache_stats',
    'clear_all_caches',

    # Stock Queries
    'get_stock_info',
    'get_all_stocks',
    'get_stocks_by_sector',
    'search_stocks',
    'get_stock_price_history',
    'get_watchlist_stocks',
    'get_all_sectors',
    'get_stocks_by_market_cap',
    'get_stock_count',

    # Options Queries
    'get_options_chain',
    'get_premium_opportunities',
    'get_options_by_strike',
    'get_historical_premiums',
    'get_high_iv_stocks',
    'calculate_expected_return',
    'get_options_summary_by_symbol',
    'get_best_strikes_for_csp',
]

__version__ = '1.0.0'
__author__ = 'WheelStrategy Team'
