"""
ESPN to Kalshi Odds Matcher
Matches ESPN live games to Kalshi prediction markets
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import psycopg2.extras
from src.kalshi_db_manager import KalshiDBManager

logger = logging.getLogger(__name__)


class ESPNKalshiMatcher:
    """
    Match ESPN live games to Kalshi prediction markets
    """

    def __init__(self):
        self.db = KalshiDBManager()

    def match_game_to_kalshi(self, espn_game: Dict) -> Optional[Dict]:
        """
        Find Kalshi market odds for an ESPN game

        Args:
            espn_game: ESPN game dict with away_team, home_team, game_time

        Returns:
            Dict with away_win_price, home_win_price, volume, ticker
        """
        away_team = espn_game.get('away_team', '')
        home_team = espn_game.get('home_team', '')
        game_time = espn_game.get('game_time', '')

        if not away_team or not home_team:
            return None

        # Extract date from game_time (format: "YYYY-MM-DD HH:MM")
        try:
            if game_time:
                game_date = datetime.strptime(game_time[:10], '%Y-%m-%d').date()
            else:
                # If no game time, use today
                game_date = datetime.now().date()
        except:
            game_date = datetime.now().date()

        # Query Kalshi database for matching market
        conn = None
        cur = None
        try:
            conn = self.db.get_connection()
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

            # Search for market with both team names
            # Kalshi markets often format as: "Team1-to-win-vs-Team2" or similar
            query = """
            SELECT
                ticker,
                title,
                yes_price,
                no_price,
                volume,
                close_time,
                market_type
            FROM kalshi_markets
            WHERE
                (
                    title ILIKE %s AND title ILIKE %s
                )
                AND market_type IN ('nfl', 'cfb', 'winner')
                AND close_time >= %s
                AND close_time <= %s
                AND status != 'closed'
                AND yes_price IS NOT NULL
            ORDER BY volume DESC, close_time ASC
            LIMIT 1
            """

            # Search within +/- 3 days of game time
            date_start = game_date - timedelta(days=3)
            date_end = game_date + timedelta(days=3)

            cur.execute(query, (
                f'%{away_team}%',
                f'%{home_team}%',
                date_start,
                date_end
            ))

            result = cur.fetchone()

            if result:
                # Determine which team is "yes" and which is "no"
                ticker = result['ticker'].lower()
                title = result['title'].lower()

                # Check if away team is in the "yes" position
                away_is_yes = away_team.lower() in ticker or \
                             (ticker.startswith('nfl') and away_team.split()[-1].lower() in ticker)

                if away_is_yes:
                    away_price = result['yes_price']
                    home_price = result['no_price']
                else:
                    away_price = result['no_price']
                    home_price = result['yes_price']

                return {
                    'away_win_price': away_price,
                    'home_win_price': home_price,
                    'volume': result['volume'],
                    'ticker': result['ticker'],
                    'market_title': result['title'],
                    'close_time': result['close_time']
                }

            return None

        except Exception as e:
            logger.error(f"Error matching game to Kalshi: {e}")
            return None
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    def enrich_espn_games_with_kalshi(self, espn_games: List[Dict]) -> List[Dict]:
        """
        Add Kalshi odds to all ESPN games

        Args:
            espn_games: List of ESPN game dicts

        Returns:
            Same list with kalshi_odds added to each game
        """
        enriched_games = []

        for game in espn_games:
            kalshi_odds = self.match_game_to_kalshi(game)

            if kalshi_odds:
                game['kalshi_odds'] = kalshi_odds
                logger.info(f"Matched Kalshi odds for {game['away_team']} @ {game['home_team']}: "
                          f"{kalshi_odds['away_win_price']:.2%} / {kalshi_odds['home_win_price']:.2%}")
            else:
                game['kalshi_odds'] = None
                logger.debug(f"No Kalshi market found for {game['away_team']} @ {game['home_team']}")

            enriched_games.append(game)

        matched_count = sum(1 for g in enriched_games if g.get('kalshi_odds'))
        logger.info(f"Enriched {len(espn_games)} ESPN games with Kalshi odds. "
                   f"Matched: {matched_count}, Unmatched: {len(espn_games) - matched_count}")

        return enriched_games

    def get_team_name_variations(self, team_name: str) -> List[str]:
        """
        Generate common variations of team names for fuzzy matching

        Examples:
            "Buffalo Bills" -> ["Buffalo Bills", "Bills", "Buffalo"]
            "Ohio State Buckeyes" -> ["Ohio State Buckeyes", "Buckeyes", "Ohio State", "OSU"]
        """
        variations = [team_name]

        # Split team name
        parts = team_name.split()

        if len(parts) >= 2:
            # Add just the mascot (last word)
            variations.append(parts[-1])

            # Add everything except mascot
            variations.append(' '.join(parts[:-1]))

            # Common abbreviations for college teams
            if len(parts) >= 2:
                # Ohio State -> OSU
                if len(parts) == 2:
                    abbrev = ''.join([p[0] for p in parts]).upper()
                    variations.append(abbrev)

        return variations

    def search_kalshi_markets(self, search_term: str, limit: int = 10) -> List[Dict]:
        """
        Search Kalshi markets by keyword

        Args:
            search_term: Team name or search query
            limit: Max number of results

        Returns:
            List of matching markets
        """
        conn = None
        cur = None
        try:
            conn = self.db.get_connection()
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

            query = """
            SELECT
                ticker,
                title,
                yes_price,
                no_price,
                volume,
                close_time,
                market_type,
                status
            FROM kalshi_markets
            WHERE title ILIKE %s
              AND status != 'closed'
            ORDER BY volume DESC, close_time ASC
            LIMIT %s
            """

            cur.execute(query, (f'%{search_term}%', limit))
            results = cur.fetchall()

            return [dict(row) for row in results]

        except Exception as e:
            logger.error(f"Error searching Kalshi markets: {e}")
            return []
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()


# Convenience function for easy importing
def enrich_games_with_kalshi_odds(espn_games: List[Dict]) -> List[Dict]:
    """
    Quick function to enrich ESPN games with Kalshi odds

    Usage:
        from src.espn_kalshi_matcher import enrich_games_with_kalshi_odds

        espn_games = get_espn_games()
        games_with_odds = enrich_games_with_kalshi_odds(espn_games)
    """
    matcher = ESPNKalshiMatcher()
    return matcher.enrich_espn_games_with_kalshi(espn_games)


if __name__ == "__main__":
    # Test matching
    import sys
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')

    from src.espn_live_data import get_espn_client
    from src.espn_ncaa_live_data import get_espn_ncaa_client

    print("Testing ESPN to Kalshi Matcher")
    print("=" * 60)

    # Get ESPN games
    espn = get_espn_client()
    nfl_games = espn.get_live_scores()

    print(f"\nFound {len(nfl_games)} NFL games")

    # Enrich with Kalshi
    matcher = ESPNKalshiMatcher()
    enriched = matcher.enrich_espn_games_with_kalshi(nfl_games[:5])  # Test first 5

    print("\nResults:")
    for game in enriched:
        odds = game.get('kalshi_odds')
        if odds:
            print(f"✅ {game['away_team']} @ {game['home_team']}")
            print(f"   Away: {odds['away_win_price']:.1%}, Home: {odds['home_win_price']:.1%}")
            print(f"   Market: {odds['ticker']}")
        else:
            print(f"❌ {game['away_team']} @ {game['home_team']} - No Kalshi market found")
        print()
