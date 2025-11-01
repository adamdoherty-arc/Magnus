"""
FastAPI Research Endpoints
Provides cached and rate-limited access to AI research reports
"""

from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import logging
import json
import traceback

from src.agents.ai_research.models import ResearchReport, ResearchRequest, ErrorResponse
from src.agents.ai_research.orchestrator import ResearchOrchestrator
from src.api.redis_cache import RedisCache
from src.api.rate_limiter import RateLimiter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Research API",
    description="AI-powered stock research with multi-agent analysis",
    version="1.0.0"
)

# Initialize services
redis_cache = RedisCache(
    host="localhost",
    port=6379,
    db=0,
    default_ttl=1800  # 30 minutes
)

rate_limiter = RateLimiter(
    redis_cache=redis_cache,
    max_requests=10,
    window_seconds=60
)

orchestrator = ResearchOrchestrator()


# Dependency for rate limiting
async def check_rate_limit(request: Request):
    """Check if user has exceeded rate limit"""
    # Use IP address as user identifier (in production, use actual user ID)
    user_id = request.client.host

    if not await rate_limiter.allow_request(user_id):
        retry_after = await rate_limiter.get_retry_after(user_id)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error_code": "RATE_LIMIT_EXCEEDED",
                "error_message": f"Rate limit exceeded. Maximum {rate_limiter.max_requests} requests per {rate_limiter.window_seconds} seconds.",
                "retry_after_seconds": retry_after
            },
            headers={"Retry-After": str(retry_after)}
        )

    return True


@app.get("/api/research/{symbol}", response_model=Dict[str, Any])
async def get_research(
    symbol: str,
    force_refresh: bool = False,
    include_fundamental: bool = True,
    include_technical: bool = True,
    include_sentiment: bool = True,
    include_options: bool = True,
    _: bool = Depends(check_rate_limit)
):
    """
    Get AI research report for a symbol (cached or fresh)

    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL')
        force_refresh: If True, bypass cache and generate fresh analysis
        include_fundamental: Include fundamental analysis
        include_technical: Include technical analysis
        include_sentiment: Include sentiment analysis
        include_options: Include options analysis

    Returns:
        ResearchReport as JSON

    Rate Limits:
        10 requests per minute per user

    Cache:
        Results cached for 30 minutes unless force_refresh=True
    """
    try:
        symbol = symbol.upper().strip()

        # Validate symbol
        if not symbol or len(symbol) > 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error_code": "INVALID_SYMBOL",
                    "error_message": "Symbol must be 1-10 characters"
                }
            )

        # Check cache first (unless force_refresh)
        cache_key = f"research:{symbol}"
        if not force_refresh:
            cached_data = await redis_cache.get(cache_key)
            if cached_data:
                logger.info(f"Cache hit for {symbol}")
                return JSONResponse(
                    content=cached_data,
                    headers={"X-Cache": "HIT"}
                )

        # Build research request
        include_sections = []
        if include_fundamental:
            include_sections.append('fundamental')
        if include_technical:
            include_sections.append('technical')
        if include_sentiment:
            include_sections.append('sentiment')
        if include_options:
            include_sections.append('options')

        request = ResearchRequest(
            symbol=symbol,
            force_refresh=force_refresh,
            include_sections=include_sections
        )

        # Generate fresh research
        logger.info(f"Generating fresh research for {symbol}")
        report = await orchestrator.analyze(request)

        # Convert to dict and cache
        report_dict = report.to_dict()
        await redis_cache.set(cache_key, report_dict, ttl=1800)  # 30 min TTL

        return JSONResponse(
            content=report_dict,
            headers={"X-Cache": "MISS"}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating research for {symbol}: {str(e)}")
        logger.error(traceback.format_exc())

        # Try to return cached data as fallback
        try:
            cached_data = await redis_cache.get(cache_key)
            if cached_data:
                logger.info(f"Returning stale cache for {symbol} due to error")
                return JSONResponse(
                    content=cached_data,
                    headers={
                        "X-Cache": "STALE",
                        "X-Error": str(e)
                    }
                )
        except:
            pass

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_code": "ANALYSIS_FAILED",
                "error_message": str(e),
                "cached_data_available": False
            }
        )


@app.get("/api/research/{symbol}/refresh", response_model=Dict[str, Any])
async def refresh_research(
    symbol: str,
    _: bool = Depends(check_rate_limit)
):
    """
    Force refresh analysis for a symbol (bypasses cache)

    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL')

    Returns:
        Fresh ResearchReport as JSON

    Rate Limits:
        10 requests per minute per user

    Note:
        This endpoint always generates fresh analysis and updates the cache
    """
    return await get_research(
        symbol=symbol,
        force_refresh=True,
        include_fundamental=True,
        include_technical=True,
        include_sentiment=True,
        include_options=True
    )


@app.get("/api/research/{symbol}/status")
async def get_cache_status(symbol: str):
    """
    Check cache status for a symbol

    Args:
        symbol: Stock ticker symbol

    Returns:
        Cache metadata (exists, age, expires_in)
    """
    try:
        symbol = symbol.upper().strip()
        cache_key = f"research:{symbol}"

        cached_data = await redis_cache.get(cache_key)
        ttl = await redis_cache.get_ttl(cache_key)

        if cached_data:
            timestamp = datetime.fromisoformat(cached_data.get('timestamp', datetime.now().isoformat()))
            age_seconds = (datetime.now() - timestamp).total_seconds()

            return {
                "symbol": symbol,
                "cached": True,
                "timestamp": cached_data.get('timestamp'),
                "age_seconds": int(age_seconds),
                "expires_in_seconds": ttl,
                "overall_rating": cached_data.get('overall_rating')
            }
        else:
            return {
                "symbol": symbol,
                "cached": False,
                "message": "No cached data available"
            }

    except Exception as e:
        logger.error(f"Error checking cache status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.delete("/api/research/{symbol}/cache")
async def clear_cache(
    symbol: str,
    _: bool = Depends(check_rate_limit)
):
    """
    Clear cached research for a symbol

    Args:
        symbol: Stock ticker symbol

    Returns:
        Confirmation message
    """
    try:
        symbol = symbol.upper().strip()
        cache_key = f"research:{symbol}"

        deleted = await redis_cache.delete(cache_key)

        return {
            "symbol": symbol,
            "deleted": deleted,
            "message": "Cache cleared" if deleted else "No cache found"
        }

    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/health")
async def health_check():
    """
    Health check endpoint

    Returns:
        Service status and component health
    """
    try:
        # Check Redis connection
        redis_healthy = await redis_cache.ping()

        # Check orchestrator (basic validation)
        orchestrator_healthy = orchestrator is not None

        return {
            "status": "healthy" if (redis_healthy and orchestrator_healthy) else "degraded",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "redis": "healthy" if redis_healthy else "unhealthy",
                "orchestrator": "healthy" if orchestrator_healthy else "unhealthy"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail if isinstance(exc.detail, dict) else {"error_message": exc.detail},
        headers=exc.headers
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
