"""
Best Bets Ranker Service

Fetches betting opportunities from ALL sources (NFL, NCAA, NBA, politics, etc.)
and ranks them using the OpportunityScorer to identify the most profitable bets
across all sports and markets.
"""

import logging
import psycopg2
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from .opportunity_scorer import OpportunityScorer

logger = logging.getLogger(__name__)


class BestBetsRanker:
    """
    Service to fetch and rank the best betting opportunities across all sports
    """

    def __init__(self, db_connection_string: str):
        """
        Initialize with database connection string

        Args:
            db_connection_string: PostgreSQL connection string
        """
        self.db_connection_string = db_connection_string
        self.scorer = OpportunityScorer()

    def get_best_bets(
        self,
        top_n: int = 20,
        min_ev: float = 0.05,
        min_confidence: float = 60.0,
        sports_filter: Optional[List[str]] = None,
        max_age_hours: int = 24
    ) -> List[Dict]:
        """
        Get the top N best betting opportunities across all sports

        Args:
            top_n: Number of top opportunities to return
            min_ev: Minimum EV percentage (e.g., 0.05 = 5%)
            min_confidence: Minimum confidence score (0-100)
            sports_filter: Optional list of sports to include (e.g., ['NFL', 'NCAA'])
            max_age_hours: Maximum age of odds in hours (default 24)

        Returns:
            List of top opportunities sorted by score, each containing:
            {
                'sport': Sport name,
                'game_info': Game description,
                'market_type': Type of market (e.g., 'Winner', 'Over/Under'),
                'team': Team or outcome being bet on,
                'ai_win_prob': AI predicted probability,
                'market_price': Market price,
                'ev_percentage': Expected value percentage,
                'confidence': Confidence score,
                'total_score': Opportunity score (0-100),
                'score_details': Detailed scoring breakdown,
                'game_time': When the game starts,
                'last_updated': When odds were last updated
            }
        """
        opportunities = []

        try:
            # Fetch from all sources
            opportunities.extend(self._fetch_nfl_opportunities(max_age_hours))
            opportunities.extend(self._fetch_ncaa_opportunities(max_age_hours))
            opportunities.extend(self._fetch_nba_opportunities(max_age_hours))
            # opportunities.extend(self._fetch_politics_opportunities(max_age_hours))
            # Add more sources as needed

            logger.info(f"Fetched {len(opportunities)} total opportunities from all sources")

            # Filter by sports if specified
            if sports_filter:
                opportunities = [opp for opp in opportunities if opp.get('sport') in sports_filter]
                logger.info(f"Filtered to {len(opportunities)} opportunities for sports: {sports_filter}")

            # Filter by minimum EV and confidence
            opportunities = [
                opp for opp in opportunities
                if opp.get('ai_win_prob', 0) > 0  # Has AI prediction
                and opp.get('market_price', 0) > 0  # Has market price
            ]

            # Score and rank all opportunities
            ranked_opportunities = self.scorer.rank_opportunities(opportunities)

            # Filter by minimum requirements AFTER scoring
            filtered_opportunities = [
                opp for opp in ranked_opportunities
                if opp['score_details']['ev_percentage'] >= (min_ev * 100)
                and opp['score_details']['confidence_score'] >= min_confidence
            ]

            logger.info(f"After filtering (EV>={min_ev*100}%, confidence>={min_confidence}): {len(filtered_opportunities)} opportunities")

            # Return top N
            return filtered_opportunities[:top_n]

        except Exception as e:
            logger.error(f"Error fetching best bets: {e}", exc_info=True)
            return []

    def _fetch_nfl_opportunities(self, max_age_hours: int) -> List[Dict]:
        """Fetch NFL betting opportunities from database"""
        opportunities = []

        try:
            conn = psycopg2.connect(self.db_connection_string)
            cursor = conn.cursor()

            # Query NFL games with Kalshi odds and AI predictions
            query = """
                SELECT
                    g.home_team,
                    g.away_team,
                    g.game_time,
                    g.kalshi_market_ticker,
                    k.away_win_price,
                    k.home_win_price,
                    k.last_updated,
                    k.volume,
                    a.away_win_probability,
                    a.home_win_probability,
                    a.away_confidence,
                    a.home_confidence
                FROM espn_games g
                LEFT JOIN kalshi_markets k ON g.kalshi_market_ticker = k.market_ticker
                LEFT JOIN ai_predictions a ON g.game_id = a.game_id
                WHERE g.sport = 'NFL'
                  AND g.game_time > NOW()
                  AND k.last_updated > NOW() - INTERVAL '%s hours'
                  AND k.away_win_price > 0.15 AND k.away_win_price < 0.85
                  AND k.home_win_price > 0.15 AND k.home_win_price < 0.85
                  AND a.away_win_probability IS NOT NULL
                ORDER BY g.game_time ASC
            """

            cursor.execute(query, (max_age_hours,))
            rows = cursor.fetchall()

            for row in rows:
                (home_team, away_team, game_time, ticker, away_price, home_price,
                 last_updated, volume, away_ai_prob, home_ai_prob, away_conf, home_conf) = row

                # Create opportunity for away team
                if away_ai_prob and away_price:
                    opportunities.append({
                        'sport': 'NFL',
                        'game_info': f"{away_team} @ {home_team}",
                        'market_type': 'Winner',
                        'team': away_team,
                        'ai_win_prob': float(away_ai_prob),
                        'market_price': float(away_price),
                        'confidence': float(away_conf) if away_conf else None,
                        'market_volume': float(volume) if volume else None,
                        'last_updated': last_updated,
                        'game_time': game_time,
                        'market_ticker': ticker
                    })

                # Create opportunity for home team
                if home_ai_prob and home_price:
                    opportunities.append({
                        'sport': 'NFL',
                        'game_info': f"{away_team} @ {home_team}",
                        'market_type': 'Winner',
                        'team': home_team,
                        'ai_win_prob': float(home_ai_prob),
                        'market_price': float(home_price),
                        'confidence': float(home_conf) if home_conf else None,
                        'market_volume': float(volume) if volume else None,
                        'last_updated': last_updated,
                        'game_time': game_time,
                        'market_ticker': ticker
                    })

            cursor.close()
            conn.close()

            logger.info(f"Fetched {len(opportunities)} NFL opportunities")

        except Exception as e:
            logger.error(f"Error fetching NFL opportunities: {e}", exc_info=True)

        return opportunities

    def _fetch_ncaa_opportunities(self, max_age_hours: int) -> List[Dict]:
        """Fetch NCAA betting opportunities from database"""
        opportunities = []

        try:
            conn = psycopg2.connect(self.db_connection_string)
            cursor = conn.cursor()

            # Similar query to NFL but for NCAA
            query = """
                SELECT
                    g.home_team,
                    g.away_team,
                    g.game_time,
                    g.kalshi_market_ticker,
                    k.away_win_price,
                    k.home_win_price,
                    k.last_updated,
                    k.volume,
                    a.away_win_probability,
                    a.home_win_probability,
                    a.away_confidence,
                    a.home_confidence
                FROM espn_games g
                LEFT JOIN kalshi_markets k ON g.kalshi_market_ticker = k.market_ticker
                LEFT JOIN ai_predictions a ON g.game_id = a.game_id
                WHERE g.sport = 'NCAA'
                  AND g.game_time > NOW()
                  AND k.last_updated > NOW() - INTERVAL '%s hours'
                  AND k.away_win_price > 0.15 AND k.away_win_price < 0.85
                  AND k.home_win_price > 0.15 AND k.home_win_price < 0.85
                  AND a.away_win_probability IS NOT NULL
                ORDER BY g.game_time ASC
            """

            cursor.execute(query, (max_age_hours,))
            rows = cursor.fetchall()

            for row in rows:
                (home_team, away_team, game_time, ticker, away_price, home_price,
                 last_updated, volume, away_ai_prob, home_ai_prob, away_conf, home_conf) = row

                # Away team opportunity
                if away_ai_prob and away_price:
                    opportunities.append({
                        'sport': 'NCAA',
                        'game_info': f"{away_team} @ {home_team}",
                        'market_type': 'Winner',
                        'team': away_team,
                        'ai_win_prob': float(away_ai_prob),
                        'market_price': float(away_price),
                        'confidence': float(away_conf) if away_conf else None,
                        'market_volume': float(volume) if volume else None,
                        'last_updated': last_updated,
                        'game_time': game_time,
                        'market_ticker': ticker
                    })

                # Home team opportunity
                if home_ai_prob and home_price:
                    opportunities.append({
                        'sport': 'NCAA',
                        'game_info': f"{away_team} @ {home_team}",
                        'market_type': 'Winner',
                        'team': home_team,
                        'ai_win_prob': float(home_ai_prob),
                        'market_price': float(home_price),
                        'confidence': float(home_conf) if home_conf else None,
                        'market_volume': float(volume) if volume else None,
                        'last_updated': last_updated,
                        'game_time': game_time,
                        'market_ticker': ticker
                    })

            cursor.close()
            conn.close()

            logger.info(f"Fetched {len(opportunities)} NCAA opportunities")

        except Exception as e:
            logger.error(f"Error fetching NCAA opportunities: {e}", exc_info=True)

        return opportunities

    def _fetch_nba_opportunities(self, max_age_hours: int) -> List[Dict]:
        """Fetch NBA betting opportunities from database"""
        opportunities = []

        try:
            conn = psycopg2.connect(self.db_connection_string)
            cursor = conn.cursor()

            # Similar query for NBA
            query = """
                SELECT
                    g.home_team,
                    g.away_team,
                    g.game_time,
                    g.kalshi_market_ticker,
                    k.away_win_price,
                    k.home_win_price,
                    k.last_updated,
                    k.volume,
                    a.away_win_probability,
                    a.home_win_probability,
                    a.away_confidence,
                    a.home_confidence
                FROM espn_games g
                LEFT JOIN kalshi_markets k ON g.kalshi_market_ticker = k.market_ticker
                LEFT JOIN ai_predictions a ON g.game_id = a.game_id
                WHERE g.sport = 'NBA'
                  AND g.game_time > NOW()
                  AND k.last_updated > NOW() - INTERVAL '%s hours'
                  AND k.away_win_price > 0.15 AND k.away_win_price < 0.85
                  AND k.home_win_price > 0.15 AND k.home_win_price < 0.85
                  AND a.away_win_probability IS NOT NULL
                ORDER BY g.game_time ASC
            """

            cursor.execute(query, (max_age_hours,))
            rows = cursor.fetchall()

            for row in rows:
                (home_team, away_team, game_time, ticker, away_price, home_price,
                 last_updated, volume, away_ai_prob, home_ai_prob, away_conf, home_conf) = row

                # Away team opportunity
                if away_ai_prob and away_price:
                    opportunities.append({
                        'sport': 'NBA',
                        'game_info': f"{away_team} @ {home_team}",
                        'market_type': 'Winner',
                        'team': away_team,
                        'ai_win_prob': float(away_ai_prob),
                        'market_price': float(away_price),
                        'confidence': float(away_conf) if away_conf else None,
                        'market_volume': float(volume) if volume else None,
                        'last_updated': last_updated,
                        'game_time': game_time,
                        'market_ticker': ticker
                    })

                # Home team opportunity
                if home_ai_prob and home_price:
                    opportunities.append({
                        'sport': 'NBA',
                        'game_info': f"{away_team} @ {home_team}",
                        'market_type': 'Winner',
                        'team': home_team,
                        'ai_win_prob': float(home_ai_prob),
                        'market_price': float(home_price),
                        'confidence': float(home_conf) if home_conf else None,
                        'market_volume': float(volume) if volume else None,
                        'last_updated': last_updated,
                        'game_time': game_time,
                        'market_ticker': ticker
                    })

            cursor.close()
            conn.close()

            logger.info(f"Fetched {len(opportunities)} NBA opportunities")

        except Exception as e:
            logger.error(f"Error fetching NBA opportunities: {e}", exc_info=True)

        return opportunities

    def get_sport_summary(self) -> Dict[str, int]:
        """
        Get summary of available opportunities by sport

        Returns:
            Dictionary with sport names as keys and opportunity counts as values
        """
        summary = {}

        try:
            conn = psycopg2.connect(self.db_connection_string)
            cursor = conn.cursor()

            query = """
                SELECT
                    g.sport,
                    COUNT(DISTINCT g.game_id) as game_count
                FROM espn_games g
                LEFT JOIN kalshi_markets k ON g.kalshi_market_ticker = k.market_ticker
                LEFT JOIN ai_predictions a ON g.game_id = a.game_id
                WHERE g.game_time > NOW()
                  AND k.last_updated > NOW() - INTERVAL '24 hours'
                  AND a.away_win_probability IS NOT NULL
                GROUP BY g.sport
                ORDER BY game_count DESC
            """

            cursor.execute(query)
            rows = cursor.fetchall()

            for sport, count in rows:
                summary[sport] = count * 2  # x2 because each game has 2 opportunities (home + away)

            cursor.close()
            conn.close()

        except Exception as e:
            logger.error(f"Error getting sport summary: {e}", exc_info=True)

        return summary
