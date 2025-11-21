"""
AI Options Agent Database Manager
Handles all database operations for AI-generated options analysis and recommendations
"""

import psycopg2
from psycopg2.extras import RealDictCursor, execute_batch
import os
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dotenv import load_dotenv
import logging

# Import centralized data layer
from src.data.options_queries import get_premium_opportunities

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()


class AIOptionsDBManager:
    """Manages AI options analysis data in Magnus PostgreSQL database"""

    def __init__(self):
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'postgres123!'),
            'database': os.getenv('DB_NAME', 'magnus')
        }

    def get_connection(self):
        """Get database connection"""
        return psycopg2.connect(**self.db_config)

    def get_opportunities(self,
                         symbols: Optional[List[str]] = None,
                         dte_range: Tuple[int, int] = (20, 40),
                         delta_range: Tuple[float, float] = (-0.45, -0.15),
                         min_premium: float = 0,
                         limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get options opportunities from stock_premiums table using centralized data layer

        Args:
            symbols: List of symbols to analyze (None = all)
            dte_range: (min_dte, max_dte) tuple
            delta_range: (min_delta, max_delta) tuple for puts (negative values)
            min_premium: Minimum premium in dollars
            limit: Maximum number of results

        Returns:
            List of option opportunities with all relevant data
        """
        try:
            # Convert premium from dollars to percentage for the centralized query
            # Note: min_premium is in cents in the database, premium_pct is percentage
            # We'll use a minimal premium_pct and filter by volume/OI instead

            filters = {
                'min_delta': delta_range[0],
                'max_delta': delta_range[1],
                'min_dte': dte_range[0],
                'max_dte': dte_range[1],
                'min_premium_pct': 0.5,  # Minimum 0.5% premium
                'min_annual_return': 0,  # Get all, we'll filter later
                'min_volume': 10,
                'min_open_interest': 50,
                'limit': limit * 2  # Get more results for filtering
            }

            # Use centralized data layer
            opportunities = get_premium_opportunities(filters)

            # Filter by symbols if provided
            if symbols:
                opportunities = [
                    opp for opp in opportunities
                    if opp.get('symbol') in symbols
                ]

            # Filter by minimum premium (premium is in cents in our data)
            if min_premium > 0:
                opportunities = [
                    opp for opp in opportunities
                    if opp.get('premium', 0) >= min_premium
                ]

            # Get only the top results by annual_return, one per symbol
            seen_symbols = set()
            filtered_opportunities = []
            for opp in opportunities:
                symbol = opp.get('symbol')
                if symbol not in seen_symbols:
                    seen_symbols.add(symbol)
                    # Rename fields to match expected format
                    opp['stock_price'] = opp.get('current_price', 0)
                    opp['iv'] = opp.get('implied_volatility', 0)
                    opp['oi'] = opp.get('open_interest', 0)
                    opp['breakeven'] = opp.get('strike_price', 0) - (opp.get('premium', 0) / 100)
                    filtered_opportunities.append(opp)

                    if len(filtered_opportunities) >= limit:
                        break

            logger.info(f"Found {len(filtered_opportunities)} opportunities using centralized data layer")
            return filtered_opportunities

        except Exception as e:
            logger.error(f"Error fetching opportunities: {e}")
            return []

    def save_analysis(self, analysis: Dict[str, Any]) -> Optional[int]:
        """
        Save AI analysis results to database

        Args:
            analysis: Dict containing all analysis fields

        Returns:
            Analysis ID if successful, None otherwise
        """
        conn = self.get_connection()
        cur = conn.cursor()

        try:
            query = """
                INSERT INTO ai_options_analyses (
                    symbol, strike_price, expiration_date, dte,
                    fundamental_score, technical_score, greeks_score,
                    risk_score, sentiment_score, final_score,
                    recommendation, strategy, confidence,
                    reasoning, key_risks, key_opportunities,
                    llm_model, llm_tokens_used, processing_time_ms
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                RETURNING id
            """

            params = (
                analysis.get('symbol'),
                analysis.get('strike_price'),
                analysis.get('expiration_date'),
                analysis.get('dte'),
                analysis.get('fundamental_score'),
                analysis.get('technical_score'),
                analysis.get('greeks_score'),
                analysis.get('risk_score'),
                analysis.get('sentiment_score'),
                analysis.get('final_score'),
                analysis.get('recommendation'),
                analysis.get('strategy'),
                analysis.get('confidence'),
                analysis.get('reasoning'),
                analysis.get('key_risks'),
                analysis.get('key_opportunities'),
                analysis.get('llm_model'),
                analysis.get('llm_tokens_used'),
                analysis.get('processing_time_ms')
            )

            cur.execute(query, params)
            analysis_id = cur.fetchone()[0]
            conn.commit()

            logger.info(f"Saved analysis {analysis_id} for {analysis.get('symbol')}")
            return analysis_id

        except Exception as e:
            conn.rollback()
            logger.error(f"Error saving analysis: {e}")
            return None
        finally:
            cur.close()
            conn.close()

    def get_recent_analyses(self, days: int = 7, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent AI analyses"""
        conn = self.get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        try:
            query = """
                SELECT *
                FROM ai_options_analyses
                WHERE analysis_date >= NOW() - INTERVAL '%s days'
                ORDER BY final_score DESC, analysis_date DESC
                LIMIT %s
            """
            cur.execute(query, (days, limit))
            results = cur.fetchall()
            return [dict(row) for row in results]

        except Exception as e:
            logger.error(f"Error fetching recent analyses: {e}")
            return []
        finally:
            cur.close()
            conn.close()

    def get_strong_buys(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get STRONG_BUY recommendations from recent analyses"""
        conn = self.get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        try:
            query = """
                SELECT *
                FROM recent_strong_buys
                WHERE analysis_date >= NOW() - INTERVAL '%s days'
                ORDER BY final_score DESC
            """
            cur.execute(query, (days,))
            results = cur.fetchall()
            return [dict(row) for row in results]

        except Exception as e:
            logger.error(f"Error fetching strong buys: {e}")
            return []
        finally:
            cur.close()
            conn.close()

    def update_outcome(self, analysis_id: int, outcome: str, pnl: float) -> bool:
        """
        Update analysis with actual trade outcome

        Args:
            analysis_id: ID of the analysis
            outcome: 'WIN', 'LOSS', 'EXPIRED', 'CLOSED_EARLY'
            pnl: Profit/loss amount

        Returns:
            True if successful
        """
        conn = self.get_connection()
        cur = conn.cursor()

        try:
            query = """
                UPDATE ai_options_analyses
                SET actual_outcome = %s,
                    actual_pnl = %s,
                    updated_at = NOW()
                WHERE id = %s
            """
            cur.execute(query, (outcome, pnl, analysis_id))
            conn.commit()
            logger.info(f"Updated outcome for analysis {analysis_id}: {outcome}")
            return True

        except Exception as e:
            conn.rollback()
            logger.error(f"Error updating outcome: {e}")
            return False
        finally:
            cur.close()
            conn.close()

    def get_agent_performance(self, agent_name: str, days: int = 30) -> Dict[str, Any]:
        """Get performance metrics for a specific agent"""
        conn = self.get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        try:
            query = """
                SELECT
                    agent_name,
                    SUM(predictions_made) as total_predictions,
                    SUM(correct_predictions) as total_correct,
                    AVG(accuracy_rate) as avg_accuracy,
                    AVG(avg_confidence) as avg_confidence
                FROM ai_agent_performance
                WHERE agent_name = %s
                    AND date >= NOW() - INTERVAL '%s days'
                GROUP BY agent_name
            """
            cur.execute(query, (agent_name, days))
            result = cur.fetchone()
            return dict(result) if result else {}

        except Exception as e:
            logger.error(f"Error fetching agent performance: {e}")
            return {}
        finally:
            cur.close()
            conn.close()

    def get_all_agents_performance(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get performance summary for all agents"""
        conn = self.get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        try:
            query = """
                SELECT *
                FROM agent_accuracy_summary
            """
            cur.execute(query)
            results = cur.fetchall()
            return [dict(row) for row in results]

        except Exception as e:
            logger.error(f"Error fetching all agents performance: {e}")
            return []
        finally:
            cur.close()
            conn.close()

    def get_watchlist_symbols(self, watchlist_name: str) -> List[str]:
        """Get symbols from a TradingView watchlist"""
        conn = self.get_connection()
        cur = conn.cursor()

        try:
            # Query from tv_watchlists_api and tv_symbols_api (live API data)
            query = """
                SELECT DISTINCT s.symbol
                FROM tv_symbols_api s
                JOIN tv_watchlists_api w ON s.watchlist_id = w.watchlist_id
                WHERE w.name = %s
                ORDER BY s.symbol
            """
            cur.execute(query, (watchlist_name,))
            results = cur.fetchall()
            return [row[0] for row in results]

        except Exception as e:
            logger.error(f"Error fetching watchlist symbols: {e}")
            return []
        finally:
            cur.close()
            conn.close()

    def get_all_watchlists(self) -> List[Dict[str, Any]]:
        """Get all available watchlists"""
        conn = self.get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        try:
            query = """
                SELECT id, name, symbol_count, last_refresh
                FROM tv_watchlists
                WHERE is_active = TRUE
                ORDER BY name
            """
            cur.execute(query)
            results = cur.fetchall()
            return [dict(row) for row in results]

        except Exception as e:
            logger.error(f"Error fetching watchlists: {e}")
            return []
        finally:
            cur.close()
            conn.close()
