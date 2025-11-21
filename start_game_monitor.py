"""
Start Game Watchlist Monitor Service
Run this as a background service to monitor watched games and send Telegram updates
"""

import asyncio
import logging
import sys
from src.game_watchlist_monitor import GameWatchlistMonitor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('game_monitor.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


async def main():
    """Main entry point"""
    logger.info("=" * 60)
    logger.info("Starting Game Watchlist Monitor Service")
    logger.info("=" * 60)
    
    monitor = GameWatchlistMonitor(check_interval=30)  # Check every 30 seconds
    
    try:
        await monitor.start()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
        monitor.stop()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        monitor.stop()
        raise


if __name__ == "__main__":
    asyncio.run(main())

