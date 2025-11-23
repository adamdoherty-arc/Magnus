"""
AVA Betting Data Interface
Provides AVA chatbot access to betting opportunities and analysis
"""

import logging
from datetime import datetime
from typing import List, Dict, Optional
import psycopg2
import psycopg2.extras

logger = logging.getLogger(__name__)


class AVABettingDataInterface:
    """Interface for AVA to access betting data and opportunities"""

    def __init__(self, db_manager):
        self.db = db_manager

    def get_top_opportunities(self, limit: int = 10, min_score: float = 70) -> List[Dict]:
        """
        Get top betting opportunities for AVA to recommend

        Args:
            limit: Maximum number of opportunities to return
            min_score: Minimum opportunity score

        Returns:
            List of top betting opportunities
        """

        try:
            conn = self.db.get_connection()
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

            cur.execute("""
                SELECT *
                FROM betting_opportunities
                WHERE opportunity_score >= %s
                AND created_at > NOW() - INTERVAL '1 hour'
                ORDER BY opportunity_score DESC
                LIMIT %s
            """, (min_score, limit))

            opportunities = cur.fetchall()
            cur.close()
            conn.close()

            return [dict(opp) for opp in opportunities]

        except Exception as e:
            logger.error(f"Error fetching top opportunities: {e}")
            return []

    def get_live_games(self) -> List[Dict]:
        """Get currently live games with betting data"""

        try:
            conn = self.db.get_connection()
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

            cur.execute("""
                SELECT *
                FROM betting_opportunities
                WHERE is_live = TRUE
                AND created_at > NOW() - INTERVAL '30 minutes'
                ORDER BY opportunity_score DESC
            """)

            games = cur.fetchall()
            cur.close()
            conn.close()

            return [dict(game) for game in games]

        except Exception as e:
            logger.error(f"Error fetching live games: {e}")
            return []

    def get_alert_worthy_bets(self) -> List[Dict]:
        """Get bets that are alert-worthy (high value)"""

        try:
            conn = self.db.get_connection()
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

            cur.execute("""
                SELECT *
                FROM betting_opportunities
                WHERE alert_worthy = TRUE
                AND created_at > NOW() - INTERVAL '1 hour'
                ORDER BY opportunity_score DESC
            """)

            alerts = cur.fetchall()
            cur.close()
            conn.close()

            return [dict(alert) for alert in alerts]

        except Exception as e:
            logger.error(f"Error fetching alert-worthy bets: {e}")
            return []

    def get_game_by_teams(self, team1: str, team2: str) -> Optional[Dict]:
        """
        Get betting data for a specific game

        Args:
            team1: First team name
            team2: Second team name

        Returns:
            Game data if found, None otherwise
        """

        try:
            conn = self.db.get_connection()
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

            cur.execute("""
                SELECT *
                FROM betting_opportunities
                WHERE (away_team ILIKE %s OR home_team ILIKE %s)
                  AND (away_team ILIKE %s OR home_team ILIKE %s)
                AND created_at > NOW() - INTERVAL '1 hour'
                ORDER BY created_at DESC
                LIMIT 1
            """, (f'%{team1}%', f'%{team1}%', f'%{team2}%', f'%{team2}%'))

            game = cur.fetchone()
            cur.close()
            conn.close()

            return dict(game) if game else None

        except Exception as e:
            logger.error(f"Error fetching game by teams: {e}")
            return None

    def get_betting_summary(self) -> Dict:
        """Get summary of current betting landscape"""

        try:
            conn = self.db.get_connection()
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

            # Get counts
            cur.execute("""
                SELECT
                    COUNT(*) FILTER (WHERE is_live = TRUE) as live_games,
                    COUNT(*) FILTER (WHERE is_live = FALSE) as upcoming_games,
                    COUNT(*) FILTER (WHERE alert_worthy = TRUE) as alert_worthy,
                    COUNT(*) FILTER (WHERE recommendation = 'STRONG_BUY') as strong_buys,
                    COUNT(*) FILTER (WHERE recommendation = 'BUY') as buys,
                    AVG(opportunity_score) as avg_opportunity_score,
                    MAX(opportunity_score) as max_opportunity_score
                FROM betting_opportunities
                WHERE created_at > NOW() - INTERVAL '1 hour'
            """)

            summary = cur.fetchone()
            cur.close()
            conn.close()

            return dict(summary) if summary else {}

        except Exception as e:
            logger.error(f"Error fetching betting summary: {e}")
            return {}

    def format_opportunity_for_ava(self, opportunity: Dict) -> str:
        """
        Format opportunity data for AVA's natural language response

        Args:
            opportunity: Opportunity dict from database

        Returns:
            Formatted string for AVA to present to user
        """

        lines = []

        # Game info
        lines.append(f"**{opportunity['away_team']} @ {opportunity['home_team']}**")
        lines.append(f"Score: {opportunity['score']} ({opportunity['status']})")
        lines.append("")

        # Opportunity details
        lines.append(f"**Opportunity Score:** {opportunity['opportunity_score']:.1f}/100")
        lines.append(f"**Recommendation:** {opportunity['recommendation']}")
        lines.append(f"**Expected Value:** {opportunity['expected_value']:+.1f}%")
        lines.append("")

        # AI prediction if available
        if opportunity.get('ai_confidence'):
            lines.append(f"**AI Analysis:**")
            lines.append(f"  Prediction: {opportunity.get('ai_prediction', 'N/A')}")
            lines.append(f"  Confidence: {opportunity['ai_confidence']:.0f}%")
            lines.append(f"  Edge: {opportunity.get('ai_edge', 0):+.1f}%")
            lines.append("")

        # Reasoning
        if opportunity.get('reasoning'):
            lines.append("**Why this is a good bet:**")
            for reason in opportunity['reasoning'].split(', '):
                lines.append(f"  • {reason}")

        return "\n".join(lines)

    def get_ava_recommendations(self, user_question: str) -> str:
        """
        Get AVA's recommendations based on user question

        Args:
            user_question: User's natural language question

        Returns:
            AVA's formatted response
        """

        question_lower = user_question.lower()

        # Handle different types of questions
        if 'best' in question_lower or 'top' in question_lower:
            opportunities = self.get_top_opportunities(limit=5, min_score=70)
            if not opportunities:
                return "I don't see any strong betting opportunities right now. The market conditions aren't favorable."

            response = ["Here are the top betting opportunities I've identified:\n"]
            for i, opp in enumerate(opportunities, 1):
                response.append(f"\n**{i}. {opp['away_team']} @ {opp['home_team']}**")
                response.append(f"   Opportunity Score: {opp['opportunity_score']:.1f}/100")
                response.append(f"   Recommendation: {opp['recommendation']}")
                response.append(f"   Expected Value: {opp['expected_value']:+.1f}%")

            return "\n".join(response)

        elif 'live' in question_lower:
            live_games = self.get_live_games()
            if not live_games:
                return "No live games with betting opportunities right now."

            response = ["Here are the live games with betting opportunities:\n"]
            for game in live_games:
                response.append(f"\n**{game['away_team']} @ {game['home_team']}**")
                response.append(f"   Score: {game['score']} ({game['status']})")
                response.append(f"   Opportunity Score: {game['opportunity_score']:.1f}/100")

            return "\n".join(response)

        elif 'alert' in question_lower:
            alerts = self.get_alert_worthy_bets()
            if not alerts:
                return "No alert-worthy bets at this time. I'll notify you when I find high-value opportunities."

            response = ["🚨 Here are the alert-worthy bets:\n"]
            for alert in alerts:
                response.append(f"\n{self.format_opportunity_for_ava(alert)}")

            return "\n".join(response)

        elif 'summary' in question_lower or 'overview' in question_lower:
            summary = self.get_betting_summary()
            if not summary:
                return "Unable to get betting summary at this time."

            response = ["**Betting Landscape Summary:**\n"]
            response.append(f"Live Games: {summary.get('live_games', 0)}")
            response.append(f"Upcoming Games: {summary.get('upcoming_games', 0)}")
            response.append(f"Alert-Worthy Bets: {summary.get('alert_worthy', 0)}")
            response.append(f"Strong Buy Recommendations: {summary.get('strong_buys', 0)}")
            response.append(f"Buy Recommendations: {summary.get('buys', 0)}")
            response.append(f"\nAverage Opportunity Score: {summary.get('avg_opportunity_score', 0):.1f}/100")
            response.append(f"Highest Opportunity Score: {summary.get('max_opportunity_score', 0):.1f}/100")

            return "\n".join(response)

        else:
            # Default: show top opportunities
            return self.get_ava_recommendations("best bets")
