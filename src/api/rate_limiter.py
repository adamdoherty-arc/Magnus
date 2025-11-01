"""
Rate Limiter
Token bucket rate limiting using Redis
"""

import time
import logging
from typing import Optional
from src.api.redis_cache import RedisCache

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Token bucket rate limiter using Redis

    Implements sliding window rate limiting with Redis
    """

    def __init__(
        self,
        redis_cache: RedisCache,
        max_requests: int = 10,
        window_seconds: int = 60
    ):
        """
        Initialize rate limiter

        Args:
            redis_cache: Redis cache instance
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds
        """
        self.redis_cache = redis_cache
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    def _get_rate_limit_key(self, user_id: str) -> str:
        """Get Redis key for user rate limit"""
        return f"ratelimit:{user_id}"

    def _get_window_key(self, user_id: str) -> str:
        """Get Redis key for user rate limit window start"""
        return f"ratelimit_window:{user_id}"

    async def allow_request(self, user_id: str) -> bool:
        """
        Check if request is allowed under rate limit

        Args:
            user_id: User identifier (IP address, user ID, etc.)

        Returns:
            True if request is allowed, False if rate limit exceeded
        """
        try:
            rate_key = self._get_rate_limit_key(user_id)
            window_key = self._get_window_key(user_id)
            current_time = int(time.time())

            # Get current request count and window start
            client = await self.redis_cache._get_client()

            # Use pipeline for atomic operations
            async with client.pipeline(transaction=True) as pipe:
                # Get current count and window start
                pipe.get(rate_key)
                pipe.get(window_key)
                results = await pipe.execute()

            current_count = int(results[0]) if results[0] else 0
            window_start = int(results[1]) if results[1] else None

            # Check if we need to reset the window
            if window_start is None or (current_time - window_start) >= self.window_seconds:
                # Start new window
                async with client.pipeline(transaction=True) as pipe:
                    pipe.set(rate_key, 1)
                    pipe.set(window_key, current_time)
                    pipe.expire(rate_key, self.window_seconds)
                    pipe.expire(window_key, self.window_seconds)
                    await pipe.execute()

                logger.debug(f"Started new rate limit window for {user_id}")
                return True

            # Within existing window
            if current_count < self.max_requests:
                # Increment counter
                await client.incr(rate_key)
                logger.debug(f"Request {current_count + 1}/{self.max_requests} for {user_id}")
                return True
            else:
                # Rate limit exceeded
                logger.warning(f"Rate limit exceeded for {user_id}: {current_count}/{self.max_requests}")
                return False

        except Exception as e:
            logger.error(f"Error checking rate limit for {user_id}: {str(e)}")
            # Fail open - allow request if rate limiter fails
            return True

    async def get_current_usage(self, user_id: str) -> tuple[int, int]:
        """
        Get current usage for user

        Args:
            user_id: User identifier

        Returns:
            Tuple of (current_requests, max_requests)
        """
        try:
            rate_key = self._get_rate_limit_key(user_id)
            client = await self.redis_cache._get_client()

            current_count = await client.get(rate_key)
            current_count = int(current_count) if current_count else 0

            return (current_count, self.max_requests)

        except Exception as e:
            logger.error(f"Error getting usage for {user_id}: {str(e)}")
            return (0, self.max_requests)

    async def get_retry_after(self, user_id: str) -> int:
        """
        Get seconds until rate limit resets

        Args:
            user_id: User identifier

        Returns:
            Seconds until rate limit window resets
        """
        try:
            window_key = self._get_window_key(user_id)
            client = await self.redis_cache._get_client()

            window_start = await client.get(window_key)
            if window_start:
                window_start = int(window_start)
                current_time = int(time.time())
                elapsed = current_time - window_start
                remaining = max(0, self.window_seconds - elapsed)
                return remaining

            return 0

        except Exception as e:
            logger.error(f"Error getting retry_after for {user_id}: {str(e)}")
            return self.window_seconds

    async def reset_user_limit(self, user_id: str) -> bool:
        """
        Reset rate limit for a specific user

        Args:
            user_id: User identifier

        Returns:
            True if reset successful
        """
        try:
            rate_key = self._get_rate_limit_key(user_id)
            window_key = self._get_window_key(user_id)

            await self.redis_cache.delete(rate_key)
            await self.redis_cache.delete(window_key)

            logger.info(f"Reset rate limit for {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error resetting rate limit for {user_id}: {str(e)}")
            return False

    async def get_remaining_requests(self, user_id: str) -> int:
        """
        Get remaining requests in current window

        Args:
            user_id: User identifier

        Returns:
            Number of requests remaining
        """
        try:
            current_count, max_requests = await self.get_current_usage(user_id)
            return max(0, max_requests - current_count)

        except Exception as e:
            logger.error(f"Error getting remaining requests for {user_id}: {str(e)}")
            return 0


class AdaptiveRateLimiter(RateLimiter):
    """
    Adaptive rate limiter with different limits for different user tiers

    Extends base RateLimiter to support multiple rate limit tiers
    """

    def __init__(
        self,
        redis_cache: RedisCache,
        tier_limits: dict[str, tuple[int, int]] = None
    ):
        """
        Initialize adaptive rate limiter

        Args:
            redis_cache: Redis cache instance
            tier_limits: Dict mapping tier names to (max_requests, window_seconds)
                Example: {
                    'free': (10, 60),      # 10 req/min
                    'premium': (100, 60),  # 100 req/min
                    'enterprise': (1000, 60)  # 1000 req/min
                }
        """
        self.redis_cache = redis_cache

        self.tier_limits = tier_limits or {
            'free': (10, 60),
            'premium': (100, 60),
            'enterprise': (1000, 60)
        }

        # Default to free tier
        default_limit = self.tier_limits.get('free', (10, 60))
        super().__init__(
            redis_cache=redis_cache,
            max_requests=default_limit[0],
            window_seconds=default_limit[1]
        )

    def _get_user_tier_key(self, user_id: str) -> str:
        """Get Redis key for user tier"""
        return f"user_tier:{user_id}"

    async def set_user_tier(self, user_id: str, tier: str) -> bool:
        """
        Set rate limit tier for user

        Args:
            user_id: User identifier
            tier: Tier name (must exist in tier_limits)

        Returns:
            True if successful
        """
        if tier not in self.tier_limits:
            logger.error(f"Invalid tier: {tier}")
            return False

        try:
            tier_key = self._get_user_tier_key(user_id)
            await self.redis_cache.set(
                tier_key,
                {'tier': tier},
                ttl=86400 * 30  # 30 days
            )
            logger.info(f"Set user {user_id} to tier {tier}")
            return True

        except Exception as e:
            logger.error(f"Error setting user tier: {str(e)}")
            return False

    async def get_user_tier(self, user_id: str) -> str:
        """
        Get rate limit tier for user

        Args:
            user_id: User identifier

        Returns:
            Tier name (defaults to 'free')
        """
        try:
            tier_key = self._get_user_tier_key(user_id)
            tier_data = await self.redis_cache.get(tier_key)

            if tier_data:
                return tier_data.get('tier', 'free')

            return 'free'

        except Exception as e:
            logger.error(f"Error getting user tier: {str(e)}")
            return 'free'

    async def allow_request(self, user_id: str) -> bool:
        """
        Check if request is allowed based on user's tier

        Args:
            user_id: User identifier

        Returns:
            True if request is allowed
        """
        # Get user tier and apply corresponding limits
        tier = await self.get_user_tier(user_id)
        limits = self.tier_limits.get(tier, self.tier_limits['free'])

        # Temporarily override instance limits
        original_max_requests = self.max_requests
        original_window_seconds = self.window_seconds

        self.max_requests = limits[0]
        self.window_seconds = limits[1]

        # Check rate limit with tier-specific limits
        result = await super().allow_request(user_id)

        # Restore original limits
        self.max_requests = original_max_requests
        self.window_seconds = original_window_seconds

        return result
