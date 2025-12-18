"""
Services Package
Centralized external services layer for the trading dashboard

This package provides thread-safe singleton services for:
- Robinhood API integration
- LLM (Language Model) providers
- Rate limiting
- Service configuration
- Database service registry (singleton database managers)

All services follow these principles:
- Thread-safe singleton pattern
- Automatic rate limiting
- Exponential backoff retry logic
- Comprehensive error handling and logging
- Session/connection pooling
"""

from src.services.config import (
    ServiceConfig,
    ServiceRateLimit,
    RetryPolicy,
    get_service_config,
    SERVICE_CONFIGS,
    LLM_COSTS,
    get_llm_cost,
    calculate_cost,
)

from src.services.rate_limiter import (
    TokenBucket,
    RateLimiter,
    get_rate_limiter,
    rate_limit,
    rate_limit_async,
)

# Optional import - robinhood_client may not have all dependencies
try:
    from src.services.robinhood_client import (
        RobinhoodClient,
        get_robinhood_client,
    )
    ROBINHOOD_AVAILABLE = True
except ImportError:
    ROBINHOOD_AVAILABLE = False
    RobinhoodClient = None
    get_robinhood_client = None

# Optional import - llm_service may not have all dependencies
try:
    from src.services.llm_service import (
        LLMService,
        ResponseCache,
        UsageTracker,
        get_llm_service,
    )
    LLM_SERVICE_AVAILABLE = True
except ImportError:
    LLM_SERVICE_AVAILABLE = False
    LLMService = None
    ResponseCache = None
    UsageTracker = None
    get_llm_service = None

from src.services.data_service_registry import (
    DataServiceRegistry,
    get_tradingview_manager,
    get_kalshi_manager,
    get_xtrades_manager,
    get_zone_manager,
    get_nfl_manager,
    get_technical_analysis_manager,
    get_database_scanner,
    get_registry_stats,
    get_cached_registry,
)


__all__ = [
    # Config
    "ServiceConfig",
    "ServiceRateLimit",
    "RetryPolicy",
    "get_service_config",
    "SERVICE_CONFIGS",
    "LLM_COSTS",
    "get_llm_cost",
    "calculate_cost",

    # Rate Limiting
    "TokenBucket",
    "RateLimiter",
    "get_rate_limiter",
    "rate_limit",
    "rate_limit_async",

    # Robinhood Client
    "RobinhoodClient",
    "get_robinhood_client",

    # LLM Service
    "LLMService",
    "ResponseCache",
    "UsageTracker",
    "get_llm_service",

    # Database Service Registry
    "DataServiceRegistry",
    "get_tradingview_manager",
    "get_kalshi_manager",
    "get_xtrades_manager",
    "get_zone_manager",
    "get_nfl_manager",
    "get_technical_analysis_manager",
    "get_database_scanner",
    "get_registry_stats",
    "get_cached_registry",
]


__version__ = "1.0.0"
__author__ = "WheelStrategy Team"
__description__ = "Centralized external services layer with rate limiting and retry logic"
