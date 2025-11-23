"""
Analytics Performance Agent - Monitor system performance and prediction accuracy
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import psycopg2
import psycopg2.extras
import os

from ...core.agent_base import BaseAgent, AgentState
from langchain_core.tools import tool

logger = logging.getLogger(__name__)


@tool
def get_prediction_performance_tool(days_back: int = 30, market_type: Optional[str] = None) -> str:
    """
    Get prediction performance metrics (accuracy, ROI, calibration)

    Args:
        days_back: How many days back to analyze (default 30)
        market_type: Filter by market type ('nfl', 'college', etc.)

    Returns:
        JSON string with performance metrics
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

        since_date = datetime.now() - timedelta(days=days_back)

        # Base query
        base_where = "WHERE settled_at >= %s AND actual_outcome IS NOT NULL"
        params = [since_date]

        if market_type:
            base_where += " AND market_type = %s"
            params.append(market_type)

        # Get overall metrics
        query = f"""
            SELECT
                COUNT(*) as total_predictions,
                SUM(CASE WHEN is_correct THEN 1 ELSE 0 END) as correct_predictions,
                ROUND(AVG(CASE WHEN is_correct THEN 1 ELSE 0 END) * 100, 2) as accuracy_percent,
                ROUND(AVG(confidence_score), 2) as avg_confidence,
                ROUND(SUM(pnl), 2) as total_pnl,
                ROUND(AVG(roi_percent), 2) as avg_roi_percent,
                ROUND(AVG(brier_score), 4) as avg_brier_score,
                ROUND(AVG(log_loss), 4) as avg_log_loss,
                COUNT(DISTINCT market_type) as market_types_count,
                COUNT(DISTINCT sector) as sectors_count
            FROM prediction_performance
            {base_where}
        """

        cursor.execute(query, params)
        overall = cursor.fetchone()

        # Get performance by market type
        query2 = f"""
            SELECT
                market_type,
                COUNT(*) as predictions,
                ROUND(AVG(CASE WHEN is_correct THEN 1 ELSE 0 END) * 100, 2) as accuracy,
                ROUND(SUM(pnl), 2) as pnl,
                ROUND(AVG(roi_percent), 2) as avg_roi
            FROM prediction_performance
            {base_where}
            GROUP BY market_type
            ORDER BY predictions DESC
        """

        cursor.execute(query2, params)
        by_market = cursor.fetchall()

        # Get recent best/worst predictions
        query3 = f"""
            SELECT ticker, predicted_outcome, actual_outcome, confidence_score,
                   pnl, roi_percent, settled_at
            FROM prediction_performance
            {base_where}
            ORDER BY roi_percent DESC
            LIMIT 5
        """

        cursor.execute(query3, params)
        best_predictions = cursor.fetchall()

        cursor.close()
        conn.close()

        result = {
            'time_range': f'Last {days_back} days',
            'overall_metrics': overall,
            'by_market_type': by_market,
            'best_predictions': best_predictions,
            'timestamp': datetime.now().isoformat()
        }

        return str(result)

    except Exception as e:
        logger.error(f"Error getting prediction performance: {e}")
        return f"Error: {str(e)}"


@tool
def get_backtest_results_tool(strategy_name: Optional[str] = None, limit: int = 10) -> str:
    """
    Get backtest results and performance analysis

    Args:
        strategy_name: Filter by strategy name (optional)
        limit: Maximum number of results to return (default 10)

    Returns:
        JSON string with backtest results
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

        if strategy_name:
            query = """
                SELECT id, strategy_name, start_date, end_date,
                       total_trades, winning_trades, losing_trades,
                       total_pnl, sharpe_ratio, max_drawdown_percent,
                       avg_trade_pnl, win_rate_percent,
                       created_at
                FROM backtest_results
                WHERE strategy_name ILIKE %s
                ORDER BY created_at DESC
                LIMIT %s
            """
            cursor.execute(query, (f'%{strategy_name}%', limit))
        else:
            query = """
                SELECT id, strategy_name, start_date, end_date,
                       total_trades, winning_trades, losing_trades,
                       total_pnl, sharpe_ratio, max_drawdown_percent,
                       avg_trade_pnl, win_rate_percent,
                       created_at
                FROM backtest_results
                ORDER BY created_at DESC
                LIMIT %s
            """
            cursor.execute(query, (limit,))

        results = cursor.fetchall()

        cursor.close()
        conn.close()

        if not results:
            return f"No backtest results found" + (f" for strategy '{strategy_name}'" if strategy_name else "")

        result = {
            'count': len(results),
            'backtest_results': results
        }

        return str(result)

    except Exception as e:
        logger.error(f"Error getting backtest results: {e}")
        return f"Error: {str(e)}"


@tool
def get_system_performance_metrics_tool() -> str:
    """
    Get overall system performance metrics (API response times, cache hit rates, etc.)

    Returns:
        JSON string with system performance metrics
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

        # Get database table sizes and counts
        query = """
            SELECT
                schemaname,
                tablename,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
                (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = schemaname AND table_name = tablename) as exists
            FROM pg_tables
            WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
            ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
            LIMIT 10
        """

        cursor.execute(query)
        table_sizes = cursor.fetchall()

        # Get recent prediction performance summary
        query2 = """
            SELECT
                COUNT(*) as total_predictions_24h,
                ROUND(AVG(CASE WHEN is_correct THEN 1 ELSE 0 END) * 100, 2) as accuracy_24h
            FROM prediction_performance
            WHERE settled_at >= NOW() - INTERVAL '24 hours'
            AND actual_outcome IS NOT NULL
        """

        cursor.execute(query2)
        recent_perf = cursor.fetchone()

        # Get active markets count
        query3 = """
            SELECT COUNT(*) as active_markets
            FROM kalshi_markets
            WHERE status = 'active'
        """

        try:
            cursor.execute(query3)
            market_count = cursor.fetchone()
        except:
            market_count = {'active_markets': 0}

        cursor.close()
        conn.close()

        result = {
            'top_tables_by_size': table_sizes,
            'recent_performance': recent_perf,
            'active_markets': market_count,
            'timestamp': datetime.now().isoformat()
        }

        return str(result)

    except Exception as e:
        logger.error(f"Error getting system performance metrics: {e}")
        return f"Error: {str(e)}"


class AnalyticsAgent(BaseAgent):
    """
    Analytics Performance Agent - Monitor system performance and prediction accuracy

    Capabilities:
    - Track prediction performance (accuracy, ROI, calibration)
    - Analyze backtest results
    - Monitor system performance metrics
    - Provide performance insights and recommendations
    - Track model calibration and Brier scores
    """

    def __init__(self, use_huggingface: bool = False):
        """Initialize Analytics Performance Agent"""
        tools = [
            get_prediction_performance_tool,
            get_backtest_results_tool,
            get_system_performance_metrics_tool
        ]

        super().__init__(
            name="analytics_agent",
            description="Monitors prediction performance, backtest results, and system analytics",
            tools=tools,
            use_huggingface=use_huggingface
        )

        self.metadata['capabilities'] = [
            'prediction_performance',
            'backtest_analysis',
            'system_metrics',
            'calibration_tracking',
            'roi_analysis',
            'performance_insights'
        ]

    async def execute(self, state: AgentState) -> AgentState:
        """Execute Analytics agent"""
        try:
            input_text = state.get('input', '')
            context = state.get('context', {})

            # Extract parameters
            days_back = context.get('days_back', 30)
            market_type = context.get('market_type')
            strategy_name = context.get('strategy_name')

            result = {
                'agent': 'analytics_agent',
                'timestamp': datetime.now().isoformat()
            }

            # Determine operation based on input
            if 'backtest' in input_text.lower() or strategy_name:
                # Get backtest results
                data = get_backtest_results_tool.invoke({
                    'strategy_name': strategy_name,
                    'limit': 10
                })
                result['operation'] = 'backtest_analysis'
                result['data'] = data

            elif 'system' in input_text.lower() or 'performance' in input_text.lower():
                # Get system metrics
                data = get_system_performance_metrics_tool.invoke({})
                result['operation'] = 'system_metrics'
                result['data'] = data

            else:
                # Get prediction performance (default)
                data = get_prediction_performance_tool.invoke({
                    'days_back': days_back,
                    'market_type': market_type
                })
                result['operation'] = 'prediction_performance'
                result['data'] = data

            state['result'] = result
            return state

        except Exception as e:
            logger.error(f"AnalyticsAgent error: {e}")
            state['error'] = str(e)
            return state
