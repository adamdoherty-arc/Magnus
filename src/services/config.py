"""
Service Configuration
Central configuration for all external services with rate limits, timeouts, and retry policies
"""

from typing import Dict, Any, Tuple
from dataclasses import dataclass


@dataclass
class ServiceRateLimit:
    """Rate limit configuration for a service"""
    max_calls: int
    time_window: int  # seconds

    @property
    def calls_per_second(self) -> float:
        """Calculate calls per second"""
        return self.max_calls / self.time_window


@dataclass
class RetryPolicy:
    """Retry policy configuration"""
    max_retries: int = 3
    base_delay: float = 1.0  # seconds
    max_delay: float = 60.0  # seconds
    exponential_base: float = 2.0

    def get_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt using exponential backoff"""
        delay = min(self.base_delay * (self.exponential_base ** attempt), self.max_delay)
        return delay


@dataclass
class ServiceConfig:
    """Configuration for an external service"""
    name: str
    rate_limit: ServiceRateLimit
    timeout: int  # seconds
    retry_policy: RetryPolicy
    base_url: str = ""


# =============================================================================
# Robinhood Configuration
# =============================================================================

ROBINHOOD_CONFIG = ServiceConfig(
    name="robinhood",
    rate_limit=ServiceRateLimit(
        max_calls=60,  # 60 requests per minute to be safe
        time_window=60
    ),
    timeout=30,
    retry_policy=RetryPolicy(
        max_retries=3,
        base_delay=1.0,
        max_delay=30.0,
        exponential_base=2.0
    ),
    base_url="https://api.robinhood.com"
)


# =============================================================================
# LLM Provider Configurations
# =============================================================================

# Ollama (Local) - No rate limits
OLLAMA_CONFIG = ServiceConfig(
    name="ollama",
    rate_limit=ServiceRateLimit(
        max_calls=1000,  # Effectively unlimited for local
        time_window=60
    ),
    timeout=60,
    retry_policy=RetryPolicy(
        max_retries=1,  # Local, so minimal retries
        base_delay=0.5,
        max_delay=2.0
    ),
    base_url="http://localhost:11434"
)

# Groq - Free tier with generous limits
GROQ_CONFIG = ServiceConfig(
    name="groq",
    rate_limit=ServiceRateLimit(
        max_calls=30,  # 30 requests per minute on free tier
        time_window=60
    ),
    timeout=30,
    retry_policy=RetryPolicy(
        max_retries=3,
        base_delay=2.0,
        max_delay=60.0
    ),
    base_url="https://api.groq.com/openai/v1"
)

# DeepSeek - Very cheap, reasonable limits
DEEPSEEK_CONFIG = ServiceConfig(
    name="deepseek",
    rate_limit=ServiceRateLimit(
        max_calls=60,  # Conservative estimate
        time_window=60
    ),
    timeout=30,
    retry_policy=RetryPolicy(
        max_retries=3,
        base_delay=1.0,
        max_delay=30.0
    ),
    base_url="https://api.deepseek.com/v1"
)

# Gemini - Good free tier
GEMINI_CONFIG = ServiceConfig(
    name="gemini",
    rate_limit=ServiceRateLimit(
        max_calls=60,  # 60 requests per minute on free tier
        time_window=60
    ),
    timeout=30,
    retry_policy=RetryPolicy(
        max_retries=3,
        base_delay=1.0,
        max_delay=30.0
    ),
    base_url="https://generativelanguage.googleapis.com"
)

# OpenAI - Standard tier
OPENAI_CONFIG = ServiceConfig(
    name="openai",
    rate_limit=ServiceRateLimit(
        max_calls=60,  # Conservative for tier 1
        time_window=60
    ),
    timeout=60,
    retry_policy=RetryPolicy(
        max_retries=3,
        base_delay=1.0,
        max_delay=60.0
    ),
    base_url="https://api.openai.com/v1"
)

# Anthropic Claude - Standard tier
ANTHROPIC_CONFIG = ServiceConfig(
    name="anthropic",
    rate_limit=ServiceRateLimit(
        max_calls=50,  # Conservative estimate
        time_window=60
    ),
    timeout=60,
    retry_policy=RetryPolicy(
        max_retries=3,
        base_delay=2.0,
        max_delay=60.0
    ),
    base_url="https://api.anthropic.com"
)

# Grok (xAI)
GROK_CONFIG = ServiceConfig(
    name="grok",
    rate_limit=ServiceRateLimit(
        max_calls=60,  # Conservative estimate
        time_window=60
    ),
    timeout=30,
    retry_policy=RetryPolicy(
        max_retries=3,
        base_delay=1.0,
        max_delay=30.0
    ),
    base_url="https://api.x.ai/v1"
)

# Kimi/Moonshot
KIMI_CONFIG = ServiceConfig(
    name="kimi",
    rate_limit=ServiceRateLimit(
        max_calls=60,  # Conservative estimate
        time_window=60
    ),
    timeout=30,
    retry_policy=RetryPolicy(
        max_retries=3,
        base_delay=1.0,
        max_delay=30.0
    ),
    base_url="https://api.moonshot.cn/v1"
)


# =============================================================================
# Service Registry
# =============================================================================

SERVICE_CONFIGS: Dict[str, ServiceConfig] = {
    "robinhood": ROBINHOOD_CONFIG,
    "ollama": OLLAMA_CONFIG,
    "groq": GROQ_CONFIG,
    "deepseek": DEEPSEEK_CONFIG,
    "gemini": GEMINI_CONFIG,
    "openai": OPENAI_CONFIG,
    "anthropic": ANTHROPIC_CONFIG,
    "grok": GROK_CONFIG,
    "kimi": KIMI_CONFIG,
}


def get_service_config(service_name: str) -> ServiceConfig:
    """Get configuration for a service"""
    config = SERVICE_CONFIGS.get(service_name)
    if not config:
        raise ValueError(f"Unknown service: {service_name}")
    return config


# =============================================================================
# Cost Tracking (for LLM services)
# =============================================================================

# Cost per 1M tokens (input, output) in USD
LLM_COSTS: Dict[str, Tuple[float, float]] = {
    "ollama": (0.0, 0.0),  # Free (local)
    "groq": (0.0, 0.0),  # Free tier
    "deepseek": (0.14, 0.28),  # Very cheap
    "gemini-2.5-flash": (0.075, 0.30),  # Flash model
    "gemini-2.5-pro": (1.25, 5.00),  # Pro model
    "gpt-4o-mini": (0.15, 0.60),  # Mini model
    "gpt-4o": (2.50, 10.00),  # Full model
    "claude-sonnet-4-5": (3.00, 15.00),  # Latest Sonnet
    "claude-3-5-sonnet": (3.00, 15.00),  # Previous Sonnet
    "claude-3-opus": (15.00, 75.00),  # Most powerful
    "claude-3-haiku": (0.25, 1.25),  # Fastest
    "grok-beta": (5.00, 15.00),  # Estimate
    "moonshot-v1-8k": (0.50, 1.00),  # Estimate
}


def get_llm_cost(model: str) -> Tuple[float, float]:
    """
    Get cost per 1M tokens for a model

    Args:
        model: Model name

    Returns:
        Tuple of (input_cost, output_cost) per 1M tokens
    """
    # Try exact match first
    if model in LLM_COSTS:
        return LLM_COSTS[model]

    # Try to find provider match
    for key in LLM_COSTS:
        if key in model or model in key:
            return LLM_COSTS[key]

    # Default to free if unknown
    return (0.0, 0.0)


def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """
    Calculate cost for a specific API call

    Args:
        model: Model name
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens

    Returns:
        Cost in USD
    """
    input_cost, output_cost = get_llm_cost(model)

    # Convert from "per 1M tokens" to actual cost
    total_cost = (
        (input_tokens / 1_000_000) * input_cost +
        (output_tokens / 1_000_000) * output_cost
    )

    return total_cost
