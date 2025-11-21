"""
Cache Management Utilities
===========================

Provides caching decorators and utilities for the centralized data layer.

Features:
- Multiple TTL tiers (SHORT, MEDIUM, LONG)
- Streamlit @st.cache_data wrapper
- Cache invalidation utilities
- Cache statistics (if available)

Usage:
    from src.data.cache_manager import cache_with_ttl, CacheTier

    @cache_with_ttl(CacheTier.SHORT)
    def get_stock_price(symbol: str) -> float:
        # Fetch from database
        return price
"""

import streamlit as st
import logging
from enum import Enum
from typing import Callable, Any
from functools import wraps

logger = logging.getLogger(__name__)


class CacheTier(Enum):
    """Cache TTL tiers for different types of data"""
    SHORT = 300      # 5 minutes - frequently changing data (prices, volumes)
    MEDIUM = 900     # 15 minutes - moderate frequency (options chains, premiums)
    LONG = 3600      # 1 hour - infrequent changes (company info, sectors)


def cache_with_ttl(ttl: CacheTier = CacheTier.MEDIUM):
    """
    Decorator to cache function results with specified TTL.

    Uses Streamlit's @st.cache_data decorator under the hood.

    Args:
        ttl: CacheTier enum value specifying cache duration

    Returns:
        Decorator function

    Example:
        @cache_with_ttl(CacheTier.SHORT)
        def get_current_price(symbol: str) -> float:
            # Database query
            return price
    """
    def decorator(func: Callable) -> Callable:
        # Apply Streamlit cache with TTL
        cached_func = st.cache_data(ttl=ttl.value, show_spinner=False)(func)

        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return cached_func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Cache error in {func.__name__}: {e}")
                # If cache fails, call function directly
                return func(*args, **kwargs)

        return wrapper
    return decorator


def invalidate_cache(function_name: str) -> bool:
    """
    Force invalidation of a cached function.

    Note: Streamlit's cache_data.clear() clears ALL cached data,
    not individual functions. This is a limitation of Streamlit's
    caching system as of version 1.28+.

    Args:
        function_name: Name of the cached function (for logging only)

    Returns:
        True if cache was cleared

    Example:
        invalidate_cache("get_stock_info")
    """
    try:
        logger.info(f"Clearing cache for: {function_name}")
        st.cache_data.clear()
        logger.info("Cache cleared successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to clear cache: {e}")
        return False


def get_cache_stats() -> dict:
    """
    Get cache statistics (if available).

    Note: Streamlit does not expose cache hit/miss statistics.
    This function returns basic information about cache tiers.

    Returns:
        Dictionary with cache configuration info

    Example:
        stats = get_cache_stats()
        print(f"SHORT tier TTL: {stats['tiers']['SHORT']} seconds")
    """
    return {
        "provider": "streamlit_cache_data",
        "tiers": {
            "SHORT": CacheTier.SHORT.value,
            "MEDIUM": CacheTier.MEDIUM.value,
            "LONG": CacheTier.LONG.value
        },
        "features": {
            "ttl_support": True,
            "individual_invalidation": False,
            "hit_miss_stats": False,
            "memory_management": "automatic"
        },
        "notes": [
            "Cache is per-session (per browser tab)",
            "Cache clears on app restart",
            "Use cache_data.clear() to clear all cached data"
        ]
    }


def clear_all_caches() -> bool:
    """
    Clear ALL cached data across the application.

    Use with caution - this will clear every cached function result.

    Returns:
        True if successful

    Example:
        if st.button("Clear All Caches"):
            clear_all_caches()
            st.success("All caches cleared!")
    """
    try:
        logger.warning("Clearing ALL application caches")
        st.cache_data.clear()
        logger.info("All caches cleared successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to clear all caches: {e}")
        return False


# Convenience functions for common TTL values
def cache_short(func: Callable) -> Callable:
    """Cache with SHORT tier (5 minutes) - for frequently changing data"""
    return cache_with_ttl(CacheTier.SHORT)(func)


def cache_medium(func: Callable) -> Callable:
    """Cache with MEDIUM tier (15 minutes) - for moderate frequency data"""
    return cache_with_ttl(CacheTier.MEDIUM)(func)


def cache_long(func: Callable) -> Callable:
    """Cache with LONG tier (1 hour) - for infrequently changing data"""
    return cache_with_ttl(CacheTier.LONG)(func)


# Example usage
if __name__ == "__main__":
    print("Cache Manager Configuration:")
    print("=" * 50)

    stats = get_cache_stats()
    print(f"\nProvider: {stats['provider']}")
    print("\nCache Tiers:")
    for tier_name, ttl_seconds in stats['tiers'].items():
        print(f"  {tier_name}: {ttl_seconds} seconds ({ttl_seconds // 60} minutes)")

    print("\nFeatures:")
    for feature, supported in stats['features'].items():
        status = "✓" if supported else "✗"
        print(f"  {status} {feature.replace('_', ' ').title()}")

    print("\nNotes:")
    for note in stats['notes']:
        print(f"  - {note}")

    print("\n" + "=" * 50)
    print("Ready to use in data layer!")
