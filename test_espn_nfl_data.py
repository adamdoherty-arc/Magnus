"""Quick test to verify ESPN NFL data fetching"""
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_espn_nfl_data():
    """Test ESPN NFL data fetching"""
    try:
        from src.espn_live_data import get_espn_client

        logger.info("Initializing ESPN client...")
        espn = get_espn_client()

        logger.info("Fetching NFL scoreboard...")
        games = espn.get_scoreboard()

        logger.info(f"✅ Successfully fetched {len(games)} NFL games")

        if games:
            logger.info("\nFirst game details:")
            game = games[0]
            logger.info(f"  Away: {game.get('away_team')} - {game.get('away_score')}")
            logger.info(f"  Home: {game.get('home_team')} - {game.get('home_score')}")
            logger.info(f"  Status: {game.get('status_detail')}")
            logger.info(f"  Live: {game.get('is_live')}")
            logger.info(f"  Time: {game.get('game_time')}")
        else:
            logger.warning("⚠️ No games returned from ESPN")

        return True

    except Exception as e:
        logger.error(f"❌ Error fetching ESPN data: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_espn_nfl_data()
    sys.exit(0 if success else 1)
