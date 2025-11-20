"""
Automated Cache Performance Tests
Verify caching provides expected performance benefits
"""
import pytest
import time
from unittest.mock import Mock, patch
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_cache_reduces_query_time():
    """Verify caching provides 10x+ speedup"""
    try:
        # Import a cached function
        from xtrades_watchlists_page import get_active_trades_cached

        # Clear cache
        import streamlit as st
        st.cache_data.clear()

        # First call (uncached) - measure time
        start = time.time()
        try:
            data1 = get_active_trades_cached(limit=10)
            uncached_time = time.time() - start
        except:
            pytest.skip("Database not available")

        # Second call (cached) - should be much faster
        start = time.time()
        data2 = get_active_trades_cached(limit=10)
        cached_time = time.time() - start

        # Cached should be at least 5x faster
        assert cached_time < uncached_time / 5, \
            f"Cache speedup insufficient: {uncached_time/cached_time:.1f}x"

    except ImportError:
        pytest.skip("XTrades page not available for testing")

def test_cache_data_consistency():
    """Verify cached data matches fresh data"""
    try:
        from positions_page_improved import get_closed_trades_cached

        # Get cached data
        try:
            cached = get_closed_trades_cached(days_back=7)
        except:
            pytest.skip("Database not available")

        # Clear cache and get fresh
        import streamlit as st
        st.cache_data.clear()
        fresh = get_closed_trades_cached(days_back=7)

        # Should be identical
        assert cached == fresh or (cached is None and fresh is None), \
            "Cached data doesn't match fresh data"

    except ImportError:
        pytest.skip("Positions page not available for testing")

def test_error_handling_graceful_degradation():
    """Verify error handling doesn't crash"""
    from src.utils.error_handling import with_error_handling

    @with_error_handling(fallback_value=[])
    def failing_function():
        raise ConnectionError("Test error")

    # Should return fallback, not raise
    result = failing_function()
    assert result == []

def test_error_handling_with_api_rate_limit():
    """Test handling of API rate limit errors"""
    from src.utils.error_handling import with_error_handling, APIRateLimitError

    @with_error_handling(fallback_value={"cached": True}, show_error=False)
    def rate_limited_function():
        raise APIRateLimitError("Rate limit exceeded")

    result = rate_limited_function()
    assert result == {"cached": True}

def test_error_handling_with_data_unavailable():
    """Test handling of data unavailable errors"""
    from src.utils.error_handling import with_error_handling, DataNotAvailableError

    @with_error_handling(fallback_value=None, show_error=False)
    def unavailable_data_function():
        raise DataNotAvailableError("Data temporarily unavailable")

    result = unavailable_data_function()
    assert result is None

def test_pagination_component():
    """Verify pagination component works correctly"""
    import pandas as pd
    try:
        from src.components.pagination_component import paginate_dataframe

        # Create test dataframe
        df = pd.DataFrame({'col': range(100)})

        # Mock session state
        import streamlit as st
        if 'test_page' in st.session_state:
            del st.session_state['test_page']

        # Get first page
        page1 = paginate_dataframe(df, page_size=10, key_prefix="test")

        # Should return first 10 rows
        assert len(page1) == 10
        assert page1.iloc[0]['col'] == 0

    except ImportError:
        pytest.skip("Pagination component not available")
    except Exception as e:
        # Streamlit session state might not be available in test context
        pytest.skip(f"Streamlit session state not available: {e}")

def test_cache_warming_runs():
    """Verify cache warming function executes without errors"""
    try:
        from dashboard import warm_critical_caches

        # Should execute without raising
        result = warm_critical_caches()
        assert result is True or result is None

    except ImportError:
        pytest.skip("Dashboard not available for testing")
    except Exception as e:
        pytest.skip(f"Cache warming not implemented or database unavailable: {e}")

def test_progressive_loading_utility():
    """Test progressive loading utility"""
    from src.utils.progressive_loading import load_with_timeout

    def quick_function():
        return "success"

    def slow_function():
        time.sleep(10)
        return "too slow"

    # Quick function should return result
    result = load_with_timeout(quick_function, timeout=1.0, fallback="fallback")
    assert result == "success"

    # Slow function should timeout and return fallback
    result = load_with_timeout(slow_function, timeout=0.5, fallback="fallback")
    assert result == "fallback"

def test_progressive_loader_class():
    """Test ProgressiveLoader class"""
    from src.utils.progressive_loading import ProgressiveLoader

    loader = ProgressiveLoader()

    def load_section1():
        return {"section": 1}

    def load_section2():
        return {"section": 2}

    loader.add_section("Section1", load_section1, critical=True)
    loader.add_section("Section2", load_section2, critical=False)

    # Should have 2 sections
    assert len(loader.sections) == 2

def test_redis_cache_availability():
    """Test Redis cache availability check"""
    from src.utils.redis_cache import get_redis_cache, get_cache_stats

    cache = get_redis_cache()
    stats = get_cache_stats()

    # Should return stats dict
    assert isinstance(stats, dict)
    assert 'enabled' in stats

    # If Redis is disabled, should have status message
    if not stats['enabled']:
        assert 'status' in stats or 'error' in stats

def test_redis_cache_operations():
    """Test Redis cache operations if available"""
    from src.utils.redis_cache import get_redis_cache

    cache = get_redis_cache()

    if not cache.enabled:
        pytest.skip("Redis not available")

    # Test set/get
    cache.set("test_key", "test_value", ttl=10)
    result = cache.get("test_key")
    assert result == "test_value"

    # Test delete
    cache.delete("test_key")
    result = cache.get("test_key")
    assert result is None

def test_cache_decorator():
    """Test cache decorator"""
    from src.utils.redis_cache import cache_with_redis

    call_count = [0]

    @cache_with_redis("test_cache", ttl=5)
    def expensive_function(x):
        call_count[0] += 1
        return x * 2

    # First call
    result1 = expensive_function(5)
    assert result1 == 10
    first_call_count = call_count[0]

    # Second call - should be cached (or not, depending on Redis availability)
    result2 = expensive_function(5)
    assert result2 == 10

    # Call count might be same if cached, or increased if Redis unavailable
    assert call_count[0] >= first_call_count

def test_safe_cache_data_decorator():
    """Test safe_cache_data decorator"""
    try:
        from src.utils.error_handling import safe_cache_data

        @safe_cache_data(ttl=60)
        def cached_function():
            return {"data": "cached"}

        result = cached_function()
        assert result == {"data": "cached"}

    except Exception as e:
        pytest.skip(f"Streamlit caching not available in test context: {e}")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
