"""
Kalshi Markets Sync Script
Fetches NFL and College Football markets from Kalshi API and stores in database
"""

import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv
from src.kalshi_client_v2 import KalshiClientV2
from src.kalshi_db_manager import KalshiDBManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('kalshi_sync.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

load_dotenv()


def sync_football_markets():
    """Sync all NFL and College football markets"""
    logger.info("="*70)
    logger.info("KALSHI FOOTBALL MARKETS SYNC")
    logger.info("="*70)

    start_time = datetime.now()

    # Initialize clients
    logger.info("\n[1] Initializing Kalshi API client...")
    client = KalshiClientV2()  # Uses credentials from .env
    # No need to call login() - API keys use signed headers on every request
    logger.info("    ✅ Kalshi client initialized with API keys")

    # Initialize database
    logger.info("\n[2] Initializing database...")
    db = KalshiDBManager()
    logger.info("    ✅ Database initialized")

    # Fetch football markets
    logger.info("\n[3] Fetching football markets from Kalshi...")
    football_markets = client.get_football_markets()

    nfl_markets = football_markets['nfl']
    college_markets = football_markets['college']

    logger.info(f"    Found {len(nfl_markets)} NFL markets")
    logger.info(f"    Found {len(college_markets)} College Football markets")

    # Store NFL markets
    logger.info("\n[4] Storing NFL markets in database...")
    nfl_stored = 0
    nfl_failed = 0

    try:
        nfl_stored = db.store_markets(nfl_markets, market_type='nfl')
        logger.info(f"    ✅ Stored {nfl_stored} NFL markets")
    except Exception as e:
        logger.error(f"    ❌ Error storing NFL markets: {e}")
        nfl_failed = len(nfl_markets)

    # Store College markets
    logger.info("\n[5] Storing College Football markets in database...")
    college_stored = 0
    college_failed = 0

    try:
        college_stored = db.store_markets(college_markets, market_type='college')
        logger.info(f"    ✅ Stored {college_stored} College Football markets")
    except Exception as e:
        logger.error(f"    ❌ Error storing College markets: {e}")
        college_failed = len(college_markets)

    # Log sync operation
    end_time = datetime.now()
    duration = int((end_time - start_time).total_seconds())

    # Log NFL sync
    if len(nfl_markets) > 0:
        db.log_sync(
            sync_type='markets',
            market_type='nfl',
            total=len(nfl_markets),
            successful=nfl_stored,
            failed=nfl_failed,
            duration=duration,
            status='completed' if nfl_failed == 0 else 'error'
        )

    # Log College sync
    if len(college_markets) > 0:
        db.log_sync(
            sync_type='markets',
            market_type='college',
            total=len(college_markets),
            successful=college_stored,
            failed=college_failed,
            duration=duration,
            status='completed' if college_failed == 0 else 'error'
        )

    # Summary
    logger.info("\n" + "="*70)
    logger.info("SYNC COMPLETE!")
    logger.info("="*70)
    logger.info(f"NFL Markets:")
    logger.info(f"  Total: {len(nfl_markets)}")
    logger.info(f"  Stored: {nfl_stored}")
    logger.info(f"  Failed: {nfl_failed}")
    logger.info(f"\nCollege Football Markets:")
    logger.info(f"  Total: {len(college_markets)}")
    logger.info(f"  Stored: {college_stored}")
    logger.info(f"  Failed: {college_failed}")
    logger.info(f"\nDuration: {duration} seconds")
    logger.info("="*70)

    # Display database stats
    logger.info("\n[6] Database Statistics:")
    stats = db.get_stats()
    logger.info(f"    Total Markets in DB: {stats['total_markets']}")
    logger.info(f"    Active Markets: {stats['active_markets']}")
    logger.info(f"    Markets by Type: {stats['markets_by_type']}")

    return True


if __name__ == "__main__":
    try:
        success = sync_football_markets()
        if success:
            logger.info("\n✅ Kalshi markets sync completed successfully!")
            sys.exit(0)
        else:
            logger.error("\n❌ Kalshi markets sync failed!")
            sys.exit(1)
    except Exception as e:
        logger.error(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
