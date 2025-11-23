"""
Discord Integration Agent - Monitor and analyze Discord messages
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import psycopg2
import os

from ...core.agent_base import BaseAgent, AgentState
from langchain_core.tools import tool

logger = logging.getLogger(__name__)


@tool
def get_discord_messages_tool(hours_back: int = 24, channel: Optional[str] = None, limit: int = 50) -> str:
    """
    Get recent Discord messages (XTrades trader signals)

    Args:
        hours_back: How many hours back to fetch (default 24)
        channel: Specific channel name to filter (optional)
        limit: Maximum number of messages to return (default 50)

    Returns:
        JSON string with Discord messages
    """
    try:
        # Database connection
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432'),
            database=os.getenv('DB_NAME', 'trading'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', '')
        )

        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Build query
        since_time = datetime.now() - timedelta(hours=hours_back)

        if channel:
            query = """
                SELECT message_id, channel_name, author_name, content, timestamp,
                       attachments, embeds, message_type
                FROM discord_messages
                WHERE timestamp >= %s AND channel_name = %s
                ORDER BY timestamp DESC
                LIMIT %s
            """
            cursor.execute(query, (since_time, channel, limit))
        else:
            query = """
                SELECT message_id, channel_name, author_name, content, timestamp,
                       attachments, embeds, message_type
                FROM discord_messages
                WHERE timestamp >= %s
                ORDER BY timestamp DESC
                LIMIT %s
            """
            cursor.execute(query, (since_time, limit))

        messages = cursor.fetchall()
        cursor.close()
        conn.close()

        if not messages:
            return f"No Discord messages found in the last {hours_back} hours"

        # Format response
        result = {
            'count': len(messages),
            'time_range': f'Last {hours_back} hours',
            'messages': messages
        }

        return str(result)

    except Exception as e:
        logger.error(f"Error fetching Discord messages: {e}")
        return f"Error: {str(e)}"


@tool
def search_discord_alerts_tool(keywords: str, days_back: int = 7) -> str:
    """
    Search Discord messages for specific keywords (e.g., ticker symbols, alerts)

    Args:
        keywords: Keywords to search for (space-separated)
        days_back: How many days back to search (default 7)

    Returns:
        JSON string with matching messages
    """
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432'),
            database=os.getenv('DB_NAME', 'trading'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', '')
        )

        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        since_time = datetime.now() - timedelta(days=days_back)

        # Use full-text search or LIKE for keyword matching
        keyword_list = keywords.strip().split()
        search_pattern = '%' + '%'.join(keyword_list) + '%'

        query = """
            SELECT message_id, channel_name, author_name, content, timestamp,
                   message_type
            FROM discord_messages
            WHERE timestamp >= %s AND content ILIKE %s
            ORDER BY timestamp DESC
            LIMIT 100
        """

        cursor.execute(query, (since_time, search_pattern))
        messages = cursor.fetchall()

        cursor.close()
        conn.close()

        if not messages:
            return f"No messages found matching '{keywords}' in the last {days_back} days"

        result = {
            'keywords': keywords,
            'count': len(messages),
            'time_range': f'Last {days_back} days',
            'matches': messages
        }

        return str(result)

    except Exception as e:
        logger.error(f"Error searching Discord messages: {e}")
        return f"Error: {str(e)}"


@tool
def filter_trader_messages_tool(trader_name: str, hours_back: int = 48) -> str:
    """
    Filter Discord messages by specific trader/author

    Args:
        trader_name: Trader/author username to filter
        hours_back: How many hours back to search (default 48)

    Returns:
        JSON string with trader's messages
    """
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432'),
            database=os.getenv('DB_NAME', 'trading'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', '')
        )

        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        since_time = datetime.now() - timedelta(hours=hours_back)

        query = """
            SELECT message_id, channel_name, author_name, content, timestamp,
                   message_type, attachments
            FROM discord_messages
            WHERE timestamp >= %s AND author_name ILIKE %s
            ORDER BY timestamp DESC
            LIMIT 50
        """

        cursor.execute(query, (since_time, f'%{trader_name}%'))
        messages = cursor.fetchall()

        cursor.close()
        conn.close()

        if not messages:
            return f"No messages found from trader '{trader_name}' in the last {hours_back} hours"

        result = {
            'trader': trader_name,
            'count': len(messages),
            'time_range': f'Last {hours_back} hours',
            'messages': messages
        }

        return str(result)

    except Exception as e:
        logger.error(f"Error filtering trader messages: {e}")
        return f"Error: {str(e)}"


class DiscordAgent(BaseAgent):
    """
    Discord Integration Agent - Monitor and analyze Discord messages

    Capabilities:
    - Get recent Discord messages (XTrades trader signals)
    - Search messages by keywords (tickers, alerts)
    - Filter by specific traders/authors
    - Analyze trader activity patterns
    - Track signal frequency and timing
    """

    def __init__(self, use_huggingface: bool = False):
        """Initialize Discord Integration Agent"""
        tools = [
            get_discord_messages_tool,
            search_discord_alerts_tool,
            filter_trader_messages_tool
        ]

        super().__init__(
            name="discord_agent",
            description="Monitors and analyzes Discord messages from XTrades trader channels",
            tools=tools,
            use_huggingface=use_huggingface
        )

        self.metadata['capabilities'] = [
            'get_discord_messages',
            'search_trader_alerts',
            'filter_by_trader',
            'analyze_trader_activity',
            'track_signal_patterns',
            'discord_message_analysis'
        ]

    async def execute(self, state: AgentState) -> AgentState:
        """Execute Discord agent"""
        try:
            input_text = state.get('input', '')
            context = state.get('context', {})

            # Extract parameters from input
            hours_back = context.get('hours_back', 24)
            keywords = context.get('keywords')
            trader_name = context.get('trader_name')

            result = {
                'agent': 'discord_agent',
                'timestamp': datetime.now().isoformat()
            }

            # Determine which operation to perform
            if trader_name:
                # Filter by trader
                messages = filter_trader_messages_tool.invoke({
                    'trader_name': trader_name,
                    'hours_back': hours_back
                })
                result['operation'] = 'filter_by_trader'
                result['data'] = messages

            elif keywords:
                # Search by keywords
                messages = search_discord_alerts_tool.invoke({
                    'keywords': keywords,
                    'days_back': hours_back // 24 or 1
                })
                result['operation'] = 'search_keywords'
                result['data'] = messages

            else:
                # Get recent messages
                messages = get_discord_messages_tool.invoke({
                    'hours_back': hours_back,
                    'limit': 50
                })
                result['operation'] = 'get_recent_messages'
                result['data'] = messages

            state['result'] = result
            return state

        except Exception as e:
            logger.error(f"DiscordAgent error: {e}")
            state['error'] = str(e)
            return state
