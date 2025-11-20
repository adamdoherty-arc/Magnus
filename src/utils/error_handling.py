"""
Enhanced Error Handling Utilities
Provides graceful error handling with user-friendly messages
"""
import streamlit as st
import logging
from typing import Callable, Any, Optional
from functools import wraps

logger = logging.getLogger(__name__)

class APIRateLimitError(Exception):
    """Raised when API rate limit is exceeded"""
    pass

class DataNotAvailableError(Exception):
    """Raised when data is temporarily unavailable"""
    pass

def with_error_handling(
    fallback_value: Any = None,
    show_error: bool = True,
    error_message: Optional[str] = None
):
    """
    Decorator for graceful error handling with user feedback.

    Args:
        fallback_value: Value to return on error
        show_error: Whether to display error to user
        error_message: Custom error message (None = use exception message)

    Example:
        @with_error_handling(fallback_value=[])
        def get_data():
            return api.fetch()
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)

            except APIRateLimitError as e:
                if show_error:
                    st.warning(
                        f"⚠️ API rate limit reached. "
                        f"Showing cached data. Resets in 60 seconds."
                    )
                logger.warning(f"Rate limit in {func.__name__}: {e}")
                return fallback_value

            except DataNotAvailableError as e:
                if show_error:
                    st.info(
                        f"ℹ️ Data temporarily unavailable. "
                        f"Please try again in a moment."
                    )
                logger.info(f"Data unavailable in {func.__name__}: {e}")
                return fallback_value

            except ConnectionError as e:
                if show_error:
                    st.error(
                        f"❌ Connection error. "
                        f"Please check your internet connection and try again."
                    )
                logger.error(f"Connection error in {func.__name__}: {e}")
                return fallback_value

            except Exception as e:
                msg = error_message or f"An error occurred: {str(e)}"
                if show_error:
                    st.error(f"❌ {msg}")
                logger.exception(f"Error in {func.__name__}")
                return fallback_value

        return wrapper
    return decorator

def safe_cache_data(ttl: int = 300, **cache_kwargs):
    """
    Wrapper combining @st.cache_data with error handling.

    Args:
        ttl: Time to live in seconds
        **cache_kwargs: Additional arguments for @st.cache_data
    """
    def decorator(func: Callable) -> Callable:
        # Apply error handling first
        func_with_errors = with_error_handling(fallback_value=None)(func)
        # Then apply caching
        return st.cache_data(ttl=ttl, **cache_kwargs)(func_with_errors)
    return decorator
