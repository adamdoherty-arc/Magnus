"""
ESPN Live Game Data Integration
Fetches real-time scores and game status
"""

import requests
import logging
from typing import Dict, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class ESPNLiveData:
    """Fetch live NFL game data from ESPN"""

    BASE_URL = "https://site.api.espn.com/apis/site/v2/sports/football/nfl"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def get_scoreboard(self, week: Optional[int] = None) -> List[Dict]:
        """
        Get current NFL scoreboard

        Args:
            week: Week number (optional, defaults to current week)

        Returns:
            List of game dictionaries with scores and status
        """
        try:
            url = f"{self.BASE_URL}/scoreboard"

            if week:
                url += f"?week={week}"

            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            data = response.json()

            games = []
            for event in data.get('events', []):
                game = self._parse_game(event)
                if game:
                    games.append(game)

            logger.info(f"Fetched {len(games)} games from ESPN scoreboard")
            return games

        except requests.RequestException as e:
            logger.error(f"Error fetching ESPN scoreboard: {e}")
            return []

    def _parse_game(self, event: Dict) -> Optional[Dict]:
        """Parse game data from ESPN event"""

        try:
            # Extract basic info
            game_id = event.get('id')
            name = event.get('name', '')
            short_name = event.get('shortName', '')

            # Status
            status = event.get('status', {})
            status_type = status.get('type', {}).get('name', 'Unknown')
            status_detail = status.get('type', {}).get('shortDetail', '')
            is_completed = status.get('type', {}).get('completed', False)
            clock = status.get('displayClock', '0:00')
            period = status.get('period', 0)

            # Teams (home and away)
            competitions = event.get('competitions', [])
            if not competitions:
                return None

            competition = competitions[0]
            competitors = competition.get('competitors', [])

            if len(competitors) < 2:
                return None

            home_team = next((c for c in competitors if c.get('homeAway') == 'home'), None)
            away_team = next((c for c in competitors if c.get('homeAway') == 'away'), None)

            if not home_team or not away_team:
                return None

            # Extract team data
            home_name = home_team.get('team', {}).get('displayName', '')
            home_abbr = home_team.get('team', {}).get('abbreviation', '')
            home_score = int(home_team.get('score', 0))
            home_logo = home_team.get('team', {}).get('logo', '')
            home_record = home_team.get('records', [{}])[0].get('summary', '') if home_team.get('records') else ''

            away_name = away_team.get('team', {}).get('displayName', '')
            away_abbr = away_team.get('team', {}).get('abbreviation', '')
            away_score = int(away_team.get('score', 0))
            away_logo = away_team.get('team', {}).get('logo', '')
            away_record = away_team.get('records', [{}])[0].get('summary', '') if away_team.get('records') else ''

            # Game time
            game_date = event.get('date')
            if game_date:
                game_datetime = datetime.fromisoformat(game_date.replace('Z', '+00:00'))
            else:
                game_datetime = None

            # Determine if live
            is_live = status_type in ['STATUS_IN_PROGRESS', 'STATUS_HALFTIME']

            return {
                'game_id': game_id,
                'name': name,
                'short_name': short_name,
                'home_team': home_name,
                'home_abbr': home_abbr,
                'home_score': home_score,
                'home_logo': home_logo,
                'home_record': home_record,
                'away_team': away_name,
                'away_abbr': away_abbr,
                'away_score': away_score,
                'away_logo': away_logo,
                'away_record': away_record,
                'status': status_type,
                'status_detail': status_detail,
                'is_live': is_live,
                'is_completed': is_completed,
                'clock': clock,
                'period': period,
                'game_time': game_datetime
            }

        except Exception as e:
            logger.error(f"Error parsing game: {e}")
            return None

    def get_game_status(self, team_name: str) -> Optional[Dict]:
        """
        Get live status for a specific team's game

        Args:
            team_name: Team name (e.g., "Indianapolis Colts", "Atlanta Falcons")

        Returns:
            Game dictionary if found, None otherwise
        """
        games = self.get_scoreboard()

        for game in games:
            if team_name in game['home_team'] or team_name in game['away_team']:
                return game

        return None

    def get_live_games(self) -> List[Dict]:
        """Get only games currently in progress"""
        all_games = self.get_scoreboard()
        return [g for g in all_games if g.get('is_live', False)]


# Singleton instance
_espn_client = None


def get_espn_client() -> ESPNLiveData:
    """Get or create ESPN client singleton"""
    global _espn_client
    if _espn_client is None:
        _espn_client = ESPNLiveData()
    return _espn_client


if __name__ == "__main__":
    # Test
    logging.basicConfig(level=logging.INFO)

    client = ESPNLiveData()

    print("Fetching scoreboard...")
    games = client.get_scoreboard()

    print(f"\nFound {len(games)} games:\n")

    for game in games:
        print(f"{game['away_abbr']} @ {game['home_abbr']}")
        print(f"  Score: {game['away_score']} - {game['home_score']}")
        print(f"  Status: {game['status_detail']}")
        if game['is_live']:
            print(f"  🔴 LIVE - {game['clock']} Q{game['period']}")
        print()
