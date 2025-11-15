"""
Game Watchlist Manager
Tracks user-selected games and sends regular Telegram updates
"""

import logging
import json
from datetime import datetime
from typing import List, Dict, Optional
import psycopg2
import psycopg2.extras
from src.kalshi_db_manager import KalshiDBManager

logger = logging.getLogger(__name__)


class GameWatchlistManager:
    """
    Manages user's watched games and sends updates via Telegram

    Features:
    - Track selected games per user
    - Store last known state (score, status, AI prediction)
    - Detect changes and send Telegram updates
    - Send updates on:
      * Score changes
      * Quarter/period changes
      * Win/loss status changes
      * AI prediction changes (>10% confidence swing)
      * Price/odds changes
    """

    def __init__(self, db_manager: KalshiDBManager = None):
        self.db = db_manager or KalshiDBManager()
        self._create_watchlist_tables()

    def _create_watchlist_tables(self):
        """Create tables to track watched games"""
        conn = None
        cur = None
        try:
            conn = self.db.get_connection()
            cur = conn.cursor()

            # User's watched games
            cur.execute("""
                CREATE TABLE IF NOT EXISTS game_watchlist (
                    id SERIAL PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    game_id TEXT NOT NULL CHECK (game_id != ''),
                    sport TEXT NOT NULL,
                    away_team TEXT,
                    home_team TEXT,
                    selected_team TEXT,
                    added_at TIMESTAMP DEFAULT NOW(),
                    is_active BOOLEAN DEFAULT TRUE
                )
            """)

            # Drop old unique constraint if it exists and add new composite one
            cur.execute("""
                DO $$
                BEGIN
                    -- Drop old constraint if exists
                    IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'game_watchlist_user_id_game_id_key') THEN
                        ALTER TABLE game_watchlist DROP CONSTRAINT game_watchlist_user_id_game_id_key;
                    END IF;

                    -- Add new composite unique constraint including sport
                    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'game_watchlist_user_game_sport_key') THEN
                        ALTER TABLE game_watchlist ADD CONSTRAINT game_watchlist_user_game_sport_key
                        UNIQUE (user_id, game_id, sport);
                    END IF;
                END $$;
            """)

            # Track last known state for change detection
            cur.execute("""
                CREATE TABLE IF NOT EXISTS game_state_history (
                    id SERIAL PRIMARY KEY,
                    game_id TEXT NOT NULL,
                    sport TEXT,
                    away_score INTEGER,
                    home_score INTEGER,
                    status TEXT,
                    period TEXT,
                    clock TEXT,
                    ai_confidence NUMERIC,
                    ai_predicted_winner TEXT,
                    ai_win_probability NUMERIC,
                    kalshi_away_odds NUMERIC,
                    kalshi_home_odds NUMERIC,
                    timestamp TIMESTAMP DEFAULT NOW()
                )
            """)

            # Index for fast lookups
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_watchlist_user_active
                ON game_watchlist(user_id, is_active)
            """)

            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_state_history_game_time
                ON game_state_history(game_id, timestamp DESC)
            """)

            # Add index for composite lookups
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_watchlist_composite
                ON game_watchlist(user_id, game_id, sport, is_active)
            """)

            conn.commit()
            logger.info("Game watchlist tables created successfully")

        except Exception as e:
            logger.error(f"Error creating watchlist tables: {e}")
            if conn:
                conn.rollback()
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    def add_game_to_watchlist(self, user_id: str, game: Dict, selected_team: str = None) -> bool:
        """
        Add a game to user's watchlist

        Args:
            user_id: Telegram user ID or identifier
            game: Game data dict
            selected_team: Which team user is rooting for ('away', 'home', or team name)

        Returns:
            True if added successfully
        """
        conn = None
        cur = None
        try:
            # Validate game_id exists
            game_id = game.get('game_id', '')
            if not game_id or str(game_id).strip() == '':
                logger.error(f"Cannot add game to watchlist: missing or empty game_id")
                return False

            conn = self.db.get_connection()
            cur = conn.cursor()

            cur.execute("""
                INSERT INTO game_watchlist
                    (user_id, game_id, sport, away_team, home_team, selected_team, is_active)
                VALUES (%s, %s, %s, %s, %s, %s, TRUE)
                ON CONFLICT (user_id, game_id, sport)
                DO UPDATE SET is_active = TRUE, selected_team = EXCLUDED.selected_team
            """, (
                user_id,
                str(game_id),
                game.get('sport', 'NFL'),
                game.get('away_team'),
                game.get('home_team'),
                selected_team
            ))

            conn.commit()
            logger.info(f"Added game {game_id} to watchlist for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error adding game to watchlist: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    def remove_game_from_watchlist(self, user_id: str, game_id: str) -> bool:
        """Remove a game from user's watchlist"""
        conn = None
        cur = None
        try:
            # Validate game_id
            if not game_id or str(game_id).strip() == '':
                logger.error(f"Cannot remove game: missing or empty game_id")
                return False

            conn = self.db.get_connection()
            cur = conn.cursor()

            cur.execute("""
                UPDATE game_watchlist
                SET is_active = FALSE
                WHERE user_id = %s AND game_id = %s
            """, (user_id, str(game_id)))

            conn.commit()
            logger.info(f"Removed game {game_id} from watchlist for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error removing game from watchlist: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    def get_user_watchlist(self, user_id: str) -> List[Dict]:
        """Get all active watched games for a user"""
        conn = None
        cur = None
        try:
            conn = self.db.get_connection()
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

            cur.execute("""
                SELECT * FROM game_watchlist
                WHERE user_id = %s AND is_active = TRUE
                ORDER BY added_at DESC
            """, (user_id,))

            watchlist = cur.fetchall()

            return [dict(row) for row in watchlist]

        except Exception as e:
            logger.error(f"Error getting watchlist: {e}")
            return []
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    def is_game_watched(self, user_id: str, game_id: str) -> bool:
        """Check if a game is in user's watchlist"""
        conn = None
        cur = None
        try:
            # Validate game_id
            if not game_id or str(game_id).strip() == '':
                return False

            conn = self.db.get_connection()
            cur = conn.cursor()

            cur.execute("""
                SELECT COUNT(*) FROM game_watchlist
                WHERE user_id = %s AND game_id = %s AND is_active = TRUE
            """, (user_id, str(game_id)))

            count = cur.fetchone()[0]
            return count > 0

        except Exception as e:
            logger.error(f"Error checking watchlist: {e}")
            return False
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    def record_game_state(self, game: Dict, ai_prediction: Dict = None):
        """Record current game state for change detection"""
        conn = None
        cur = None
        try:
            # Validate and get game_id
            game_id = game.get('game_id', '')
            if not game_id or str(game_id).strip() == '':
                logger.error(f"Cannot record game state: missing or empty game_id")
                return

            conn = self.db.get_connection()
            cur = conn.cursor()

            cur.execute("""
                INSERT INTO game_state_history (
                    game_id, sport, away_score, home_score, status, period, clock,
                    ai_confidence, ai_predicted_winner, ai_win_probability,
                    kalshi_away_odds, kalshi_home_odds
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                str(game_id),
                game.get('sport', 'NFL'),
                game.get('away_score', 0),
                game.get('home_score', 0),
                game.get('status', ''),
                game.get('period', ''),
                game.get('clock', ''),
                ai_prediction.get('confidence_score') if ai_prediction else None,
                ai_prediction.get('predicted_winner') if ai_prediction else None,
                ai_prediction.get('win_probability') if ai_prediction else None,
                game.get('kalshi_odds', {}).get('away_win_price'),
                game.get('kalshi_odds', {}).get('home_win_price')
            ))

            conn.commit()

        except Exception as e:
            logger.error(f"Error recording game state: {e}")
            if conn:
                conn.rollback()
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    def get_last_game_state(self, game_id: str) -> Optional[Dict]:
        """Get the last recorded state for a game"""
        conn = None
        cur = None
        try:
            # Validate game_id
            if not game_id or str(game_id).strip() == '':
                return None

            conn = self.db.get_connection()
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

            cur.execute("""
                SELECT * FROM game_state_history
                WHERE game_id = %s
                ORDER BY timestamp DESC
                LIMIT 1
            """, (str(game_id),))

            state = cur.fetchone()
            return dict(state) if state else None

        except Exception as e:
            logger.error(f"Error getting last game state: {e}")
            return None
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    def detect_changes(self, game: Dict, ai_prediction: Dict = None) -> Dict:
        """
        Detect what changed since last update

        Returns:
            Dict with change flags and details
        """
        last_state = self.get_last_game_state(game.get('game_id', ''))

        if not last_state:
            return {
                'is_new': True,
                'score_changed': False,
                'period_changed': False,
                'status_changed': False,
                'ai_changed': False,
                'odds_changed': False,
                'my_team_winning_changed': False
            }

        changes = {
            'is_new': False,
            'score_changed': False,
            'period_changed': False,
            'status_changed': False,
            'ai_changed': False,
            'odds_changed': False,
            'my_team_winning_changed': False,
            'details': {}
        }

        # Score changes
        current_away = game.get('away_score', 0)
        current_home = game.get('home_score', 0)
        if current_away != last_state.get('away_score') or current_home != last_state.get('home_score'):
            changes['score_changed'] = True
            changes['details']['old_score'] = f"{last_state.get('away_score')}-{last_state.get('home_score')}"
            changes['details']['new_score'] = f"{current_away}-{current_home}"

        # Period/quarter changes
        if game.get('period') != last_state.get('period'):
            changes['period_changed'] = True
            changes['details']['old_period'] = last_state.get('period')
            changes['details']['new_period'] = game.get('period')

        # Status changes
        if game.get('status') != last_state.get('status'):
            changes['status_changed'] = True
            changes['details']['old_status'] = last_state.get('status')
            changes['details']['new_status'] = game.get('status')

        # AI prediction changes (>10% confidence swing or winner change)
        if ai_prediction:
            old_confidence = float(last_state.get('ai_confidence', 0) or 0)
            new_confidence = float(ai_prediction.get('confidence_score', 0) or 0)

            if abs(new_confidence - old_confidence) > 10:
                changes['ai_changed'] = True
                changes['details']['confidence_change'] = new_confidence - old_confidence

            if ai_prediction.get('predicted_winner') != last_state.get('ai_predicted_winner'):
                changes['ai_changed'] = True
                changes['details']['winner_changed'] = True
                changes['details']['old_winner'] = last_state.get('ai_predicted_winner')
                changes['details']['new_winner'] = ai_prediction.get('predicted_winner')

        # Odds changes (>5% change)
        kalshi_odds = game.get('kalshi_odds', {})
        if kalshi_odds:
            old_away_odds = float(last_state.get('kalshi_away_odds', 0) or 0)
            new_away_odds = float(kalshi_odds.get('away_win_price', 0) or 0)

            if abs(new_away_odds - old_away_odds) > 0.05:
                changes['odds_changed'] = True
                changes['details']['odds_change'] = (new_away_odds - old_away_odds) * 100

        return changes

    def generate_game_update_message(
        self,
        game: Dict,
        ai_prediction: Dict,
        changes: Dict,
        selected_team: str = None
    ) -> str:
        """
        Generate Telegram message for game update

        Args:
            game: Current game data
            ai_prediction: Current AI prediction
            changes: Dict of detected changes
            selected_team: User's selected team ('away', 'home', or team name)

        Returns:
            Formatted message string
        """
        away_team = game.get('away_team', '')
        home_team = game.get('home_team', '')
        away_score = game.get('away_score', 0)
        home_score = game.get('home_score', 0)
        status = game.get('status', '')
        period = game.get('period', '')
        clock = game.get('clock', '')

        # Determine if user's team is winning
        my_team_winning = False
        my_team_emoji = ""

        if selected_team:
            if selected_team.lower() == 'away' or selected_team.lower() == away_team.lower():
                my_team_winning = away_score > home_score
                my_team_emoji = "✅" if my_team_winning else "❌"
            elif selected_team.lower() == 'home' or selected_team.lower() == home_team.lower():
                my_team_winning = home_score > away_score
                my_team_emoji = "✅" if my_team_winning else "❌"

        # Build message
        msg_lines = []

        # Header with change indicators
        change_indicators = []
        if changes.get('score_changed'):
            change_indicators.append("🔔 SCORE")
        if changes.get('period_changed'):
            change_indicators.append("⏱️ PERIOD")
        if changes.get('ai_changed'):
            change_indicators.append("🤖 AI UPDATE")
        if changes.get('odds_changed'):
            change_indicators.append("💰 ODDS")

        if change_indicators:
            msg_lines.append(" | ".join(change_indicators))
            msg_lines.append("")

        # Game info
        msg_lines.append(f"🏈 **{away_team} @ {home_team}**")
        msg_lines.append(f"**{away_score} - {home_score}** {my_team_emoji}")
        msg_lines.append(f"_{status}_ - {period} {clock}")
        msg_lines.append("")

        # My team status
        if selected_team:
            status_emoji = "🔥" if my_team_winning else "⚠️"
            status_text = "WINNING" if my_team_winning else "LOSING"
            point_diff = abs(away_score - home_score)
            msg_lines.append(f"{status_emoji} **Your Team ({selected_team}): {status_text}**")
            msg_lines.append(f"   By {point_diff} point{'s' if point_diff != 1 else ''}")
            msg_lines.append("")

        # AI Prediction
        predicted_winner = ai_prediction.get('predicted_winner', '').upper()
        win_prob = ai_prediction.get('win_probability', 0) * 100
        confidence = ai_prediction.get('confidence_score', 0)
        ev = ai_prediction.get('expected_value', 0)
        recommendation = ai_prediction.get('recommendation', 'PASS')

        # Highlight if AI agrees with my team
        ai_emoji = "🎯"
        if selected_team and predicted_winner.lower() == selected_team.lower():
            ai_emoji = "✅ 🎯"
        elif selected_team:
            ai_emoji = "⚠️ 🎯"

        msg_lines.append(f"{ai_emoji} **AI Predicts: {predicted_winner} wins**")
        msg_lines.append(f"   Win Probability: {win_prob:.0f}%")
        msg_lines.append(f"   Confidence: {confidence:.0f}%")
        msg_lines.append(f"   Expected Value: {ev:+.1f}%")
        msg_lines.append(f"   Recommendation: **{recommendation.replace('_', ' ')}**")
        msg_lines.append("")

        # Odds
        kalshi_odds = game.get('kalshi_odds', {})
        if kalshi_odds:
            away_odds = kalshi_odds.get('away_win_price', 0) * 100
            home_odds = kalshi_odds.get('home_win_price', 0) * 100
            msg_lines.append(f"💰 **Kalshi Odds:**")
            msg_lines.append(f"   {away_team}: {away_odds:.0f}¢")
            msg_lines.append(f"   {home_team}: {home_odds:.0f}¢")
            msg_lines.append("")

        # Change details
        if changes.get('score_changed'):
            msg_lines.append(f"📊 Score changed: {changes['details'].get('old_score')} → {changes['details'].get('new_score')}")

        if changes.get('ai_changed') and changes['details'].get('winner_changed'):
            msg_lines.append(f"🔄 AI prediction changed: {changes['details'].get('old_winner')} → {changes['details'].get('new_winner')}")

        if changes.get('odds_changed'):
            odds_change = changes['details'].get('odds_change', 0)
            msg_lines.append(f"💹 Odds moved: {odds_change:+.1f}¢")

        msg_lines.append("")
        msg_lines.append(f"_Updated: {datetime.now().strftime('%I:%M %p')}_")

        return "\n".join(msg_lines)

    def cleanup_old_games(self, days_to_keep: int = 7):
        """Remove old completed games from watchlist"""
        conn = None
        cur = None
        try:
            conn = self.db.get_connection()
            cur = conn.cursor()

            # Deactivate games older than X days
            cur.execute("""
                UPDATE game_watchlist
                SET is_active = FALSE
                WHERE added_at < NOW() - INTERVAL '%s days'
            """, (days_to_keep,))

            deactivated = cur.rowcount

            # Delete old state history
            cur.execute("""
                DELETE FROM game_state_history
                WHERE timestamp < NOW() - INTERVAL '%s days'
            """, (days_to_keep,))

            deleted = cur.rowcount

            conn.commit()
            logger.info(f"Cleaned up {deactivated} old watchlist entries and {deleted} state records")

        except Exception as e:
            logger.error(f"Error cleaning up old games: {e}")
            if conn:
                conn.rollback()
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()
