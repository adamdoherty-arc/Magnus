"""
Test Script for Centralized Data Layer
========================================

Quick validation that all imports and functions work correctly.
"""

import sys
from pathlib import Path

# Ensure src is in path
sys.path.insert(0, str(Path(__file__).parent))

print("Testing Centralized Data Layer")
print("=" * 60)

# Test 1: Import cache manager
print("\n1. Testing cache manager imports...")
try:
    from src.data import (
        cache_with_ttl,
        CacheTier,
        cache_short,
        cache_medium,
        cache_long,
        get_cache_stats,
        clear_all_caches
    )
    print("   SUCCESS: All cache manager functions imported")
    print(f"   Cache tiers: {[t.name for t in CacheTier]}")
except Exception as e:
    print(f"   FAILED: {e}")

# Test 2: Import stock queries
print("\n2. Testing stock query imports...")
try:
    from src.data import (
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
    print("   SUCCESS: All stock query functions imported")
    print("   Functions: get_stock_info, get_all_stocks, search_stocks, etc.")
except Exception as e:
    print(f"   FAILED: {e}")

# Test 3: Import options queries
print("\n3. Testing options query imports...")
try:
    from src.data import (
        get_options_chain,
        get_premium_opportunities,
        get_options_by_strike,
        get_historical_premiums,
        get_high_iv_stocks,
        calculate_expected_return,
        get_options_summary_by_symbol,
        get_best_strikes_for_csp
    )
    print("   SUCCESS: All options query functions imported")
    print("   Functions: get_options_chain, get_premium_opportunities, etc.")
except Exception as e:
    print(f"   FAILED: {e}")

# Test 4: Check cache stats
print("\n4. Testing cache configuration...")
try:
    from src.data import get_cache_stats
    stats = get_cache_stats()
    print(f"   Provider: {stats['provider']}")
    print("   Cache Tiers:")
    for tier, ttl in stats['tiers'].items():
        print(f"     {tier}: {ttl} seconds ({ttl // 60} minutes)")
except Exception as e:
    print(f"   FAILED: {e}")

# Test 5: Test calculate_expected_return (no DB required)
print("\n5. Testing calculation function...")
try:
    from src.data import calculate_expected_return
    returns = calculate_expected_return(premium=2.50, strike=150.0, dte=30)
    print(f"   Premium: ${returns['premium']}")
    print(f"   Annual Return: {returns['annual_return']:.1f}%")
    print(f"   Break-even: ${returns['break_even']}")
    print("   SUCCESS: Calculation function works")
except Exception as e:
    print(f"   FAILED: {e}")

# Test 6: Verify database queries work (requires DB connection)
print("\n6. Testing database connection...")
try:
    from src.data import get_stock_count
    count = get_stock_count()
    print(f"   Database contains {count} active stocks")
    if count > 0:
        print("   SUCCESS: Database connection works")
    else:
        print("   WARNING: Database is empty (run stock sync first)")
except Exception as e:
    print(f"   FAILED: {e}")
    print("   NOTE: This is expected if database is not running")

print("\n" + "=" * 60)
print("Data layer validation complete!")
print("\nUsage:")
print("  from src.data import get_stock_info, get_options_chain")
print("  stock = get_stock_info('AAPL')")
print("  chain = get_options_chain('AAPL', dte_range=(20, 45))")
