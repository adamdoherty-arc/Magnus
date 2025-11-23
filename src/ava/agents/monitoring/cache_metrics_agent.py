"""
Cache Metrics Agent - Monitor caching performance and hit rates
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import os
import streamlit as st

from ...core.agent_base import BaseAgent, AgentState
from langchain_core.tools import tool

logger = logging.getLogger(__name__)


@tool
def get_streamlit_cache_stats_tool() -> str:
    """
    Get Streamlit cache statistics (@st.cache_data and @st.cache_resource)

    Returns:
        JSON string with cache statistics
    """
    try:
        # Get cache stats from Streamlit
        cache_data_stats = {
            'enabled': True,
            'type': 'st.cache_data',
            'description': 'In-memory data caching with TTL'
        }

        cache_resource_stats = {
            'enabled': True,
            'type': 'st.cache_resource',
            'description': 'Singleton resource caching (DB connections, models)'
        }

        # Try to get actual cache metrics if available
        try:
            from streamlit.runtime.caching import cache_data_api, cache_resource_api

            # Get cache data stats
            if hasattr(cache_data_api, 'get_cache_stats'):
                cache_data_stats['stats'] = str(cache_data_api.get_cache_stats())

            # Get cache resource stats
            if hasattr(cache_resource_api, 'get_cache_stats'):
                cache_resource_stats['stats'] = str(cache_resource_api.get_cache_stats())

        except Exception as e:
            logger.debug(f"Could not get detailed cache stats: {e}")

        result = {
            'cache_data': cache_data_stats,
            'cache_resource': cache_resource_stats,
            'timestamp': datetime.now().isoformat()
        }

        return str(result)

    except Exception as e:
        logger.error(f"Error getting Streamlit cache stats: {e}")
        return f"Error: {str(e)}"


@tool
def get_redis_cache_stats_tool() -> str:
    """
    Get Redis cache statistics (if Redis is configured)

    Returns:
        JSON string with Redis cache stats
    """
    try:
        import redis

        redis_host = os.getenv('REDIS_HOST', 'localhost')
        redis_port = int(os.getenv('REDIS_PORT', 6379))
        redis_password = os.getenv('REDIS_PASSWORD')

        # Connect to Redis
        r = redis.Redis(
            host=redis_host,
            port=redis_port,
            password=redis_password,
            decode_responses=True
        )

        # Get Redis INFO
        info = r.info()

        # Extract relevant metrics
        stats = {
            'connected': True,
            'version': info.get('redis_version'),
            'uptime_days': info.get('uptime_in_days'),
            'total_keys': r.dbsize(),
            'used_memory_human': info.get('used_memory_human'),
            'used_memory_peak_human': info.get('used_memory_peak_human'),
            'total_connections_received': info.get('total_connections_received'),
            'total_commands_processed': info.get('total_commands_processed'),
            'keyspace_hits': info.get('keyspace_hits'),
            'keyspace_misses': info.get('keyspace_misses'),
            'evicted_keys': info.get('evicted_keys'),
            'expired_keys': info.get('expired_keys')
        }

        # Calculate hit rate
        hits = stats['keyspace_hits'] or 0
        misses = stats['keyspace_misses'] or 0
        total = hits + misses

        if total > 0:
            stats['hit_rate_percent'] = round((hits / total) * 100, 2)
        else:
            stats['hit_rate_percent'] = 0.0

        result = {
            'redis_stats': stats,
            'timestamp': datetime.now().isoformat()
        }

        return str(result)

    except ImportError:
        return "Redis library not installed. Install with: pip install redis"
    except redis.exceptions.ConnectionError:
        return f"Cannot connect to Redis at {redis_host}:{redis_port}. Redis may not be running."
    except Exception as e:
        logger.error(f"Error getting Redis cache stats: {e}")
        return f"Error: {str(e)}"


@tool
def get_llm_cache_stats_tool() -> str:
    """
    Get LLM response cache statistics

    Returns:
        JSON string with LLM cache stats
    """
    try:
        # Try to import the local LLM module which has caching
        from src.magnus_local_llm import MagnusLocalLLM

        # Get cache stats if available
        llm_stats = {
            'type': 'LLM Response Cache',
            'description': 'Caches LLM responses to avoid repeated API calls',
            'cache_location': 'In-memory (session-based)',
        }

        # If we can access cache stats
        try:
            llm = MagnusLocalLLM()
            if hasattr(llm, 'cache_hits'):
                llm_stats['cache_hits'] = llm.cache_hits
                llm_stats['total_calls'] = llm.total_calls
                if llm.total_calls > 0:
                    llm_stats['hit_rate_percent'] = round((llm.cache_hits / llm.total_calls) * 100, 2)
        except Exception as e:
            logger.debug(f"Could not get LLM cache details: {e}")

        result = {
            'llm_cache': llm_stats,
            'timestamp': datetime.now().isoformat()
        }

        return str(result)

    except Exception as e:
        logger.error(f"Error getting LLM cache stats: {e}")
        return f"Error: {str(e)}"


@tool
def get_yfinance_cache_stats_tool() -> str:
    """
    Get yFinance wrapper cache statistics

    Returns:
        JSON string with yFinance cache stats
    """
    try:
        from src.yfinance_wrapper import safe_yfinance_call

        # yFinance uses Streamlit caching
        stats = {
            'type': 'yFinance Data Cache',
            'description': 'Caches stock price and historical data',
            'cache_mechanism': '@st.cache_data with TTL',
            'ttl_seconds': 300,  # 5 minutes based on wrapper
            'files_using_wrapper': 54,  # From optimization docs
        }

        result = {
            'yfinance_cache': stats,
            'timestamp': datetime.now().isoformat()
        }

        return str(result)

    except Exception as e:
        logger.error(f"Error getting yFinance cache stats: {e}")
        return f"Error: {str(e)}"


@tool
def clear_cache_tool(cache_type: str = "all") -> str:
    """
    Clear specified cache type

    Args:
        cache_type: Type of cache to clear ('data', 'resource', 'all')

    Returns:
        Success message
    """
    try:
        cleared = []

        if cache_type in ['data', 'all']:
            st.cache_data.clear()
            cleared.append('cache_data')

        if cache_type in ['resource', 'all']:
            st.cache_resource.clear()
            cleared.append('cache_resource')

        result = {
            'cleared': cleared,
            'cache_type': cache_type,
            'timestamp': datetime.now().isoformat()
        }

        return f"Successfully cleared: {', '.join(cleared)}"

    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        return f"Error: {str(e)}"


class CacheMetricsAgent(BaseAgent):
    """
    Cache Metrics Agent - Monitor caching performance and hit rates

    Capabilities:
    - Monitor Streamlit cache statistics
    - Track Redis cache performance (if configured)
    - Monitor LLM response caching
    - Track yFinance data caching
    - Clear caches when needed
    - Analyze cache hit rates and efficiency
    """

    def __init__(self, use_huggingface: bool = False):
        """Initialize Cache Metrics Agent"""
        tools = [
            get_streamlit_cache_stats_tool,
            get_redis_cache_stats_tool,
            get_llm_cache_stats_tool,
            get_yfinance_cache_stats_tool,
            clear_cache_tool
        ]

        super().__init__(
            name="cache_metrics_agent",
            description="Monitors cache performance, hit rates, and provides cache management",
            tools=tools,
            use_huggingface=use_huggingface
        )

        self.metadata['capabilities'] = [
            'streamlit_cache_stats',
            'redis_cache_monitoring',
            'llm_cache_tracking',
            'yfinance_cache_stats',
            'cache_clearing',
            'hit_rate_analysis'
        ]

    async def execute(self, state: AgentState) -> AgentState:
        """Execute Cache Metrics agent"""
        try:
            input_text = state.get('input', '')
            context = state.get('context', {})

            result = {
                'agent': 'cache_metrics_agent',
                'timestamp': datetime.now().isoformat()
            }

            # Determine operation based on input
            if 'clear' in input_text.lower():
                # Clear cache
                cache_type = context.get('cache_type', 'all')
                data = clear_cache_tool.invoke({'cache_type': cache_type})
                result['operation'] = 'clear_cache'
                result['data'] = data

            elif 'redis' in input_text.lower():
                # Get Redis stats
                data = get_redis_cache_stats_tool.invoke({})
                result['operation'] = 'redis_stats'
                result['data'] = data

            elif 'llm' in input_text.lower():
                # Get LLM cache stats
                data = get_llm_cache_stats_tool.invoke({})
                result['operation'] = 'llm_cache_stats'
                result['data'] = data

            elif 'yfinance' in input_text.lower() or 'stock' in input_text.lower():
                # Get yFinance cache stats
                data = get_yfinance_cache_stats_tool.invoke({})
                result['operation'] = 'yfinance_cache_stats'
                result['data'] = data

            else:
                # Get all Streamlit cache stats (default)
                streamlit_stats = get_streamlit_cache_stats_tool.invoke({})
                redis_stats = get_redis_cache_stats_tool.invoke({})
                llm_stats = get_llm_cache_stats_tool.invoke({})

                result['operation'] = 'comprehensive_cache_stats'
                result['data'] = {
                    'streamlit': streamlit_stats,
                    'redis': redis_stats,
                    'llm': llm_stats
                }

            state['result'] = result
            return state

        except Exception as e:
            logger.error(f"CacheMetricsAgent error: {e}")
            state['error'] = str(e)
            return state
