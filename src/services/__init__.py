"""
Services Package
Centralized external services layer for the trading dashboard

This package provides thread-safe singleton services for:
- Robinhood API integration
- LLM (Language Model) providers
- Rate limiting
- Service configuration

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

from src.services.robinhood_client import (
    RobinhoodClient,
    get_robinhood_client,
)

from src.services.llm_service import (
    LLMService,
    ResponseCache,
    UsageTracker,
    get_llm_service,
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
]


__version__ = "1.0.0"
__author__ = "WheelStrategy Team"
__description__ = "Centralized external services layer with rate limiting and retry logic"
