"""
API Timeout Configuration
Provides timeout constants for different external API calls
DEPRECATED: Do not use global socket timeouts as they affect all operations
Use library-specific timeout parameters instead
"""

import logging

logger = logging.getLogger(__name__)

# Recommended timeout values for different API types
DEFAULT_TIMEOUT = 10  # seconds - for quick API calls
LONG_TIMEOUT = 30  # seconds - for heavy queries
CRITICAL_TIMEOUT = 60  # seconds - for critical operations

# Library-specific timeout configurations
REQUESTS_TIMEOUT = (5, 10)  # (connect_timeout, read_timeout)
AIOHTTP_TIMEOUT = 10  # Total timeout in seconds
DATABASE_TIMEOUT = 30  # For long queries

def get_requests_timeout(operation_type: str = "default") -> tuple:
    """
    Get timeout tuple for requests library

    Args:
        operation_type: Type of operation ('quick', 'default', 'long', 'critical')

    Returns:
        Tuple of (connect_timeout, read_timeout)
    """
    timeouts = {
        'quick': (3, 5),
        'default': (5, 10),
        'long': (10, 30),
        'critical': (15, 60)
    }
    return timeouts.get(operation_type, timeouts['default'])


def get_aiohttp_timeout(operation_type: str = "default") -> int:
    """
    Get timeout for aiohttp library

    Args:
        operation_type: Type of operation ('quick', 'default', 'long', 'critical')

    Returns:
        Total timeout in seconds
    """
    timeouts = {
        'quick': 5,
        'default': 10,
        'long': 30,
        'critical': 60
    }
    return timeouts.get(operation_type, timeouts['default'])


# WARNING: Do NOT call socket.setdefaulttimeout() globally!
# It affects ALL socket operations including database connections,
# long-running tasks, and can cause unexpected timeouts.
# Always use library-specific timeout parameters instead.
