"""
Daily Trade Sync Service
Automatically syncs closed trades from Robinhood to database at end of trading day
Runs daily at 4:30 PM ET (after market close at 4:00 PM ET)
"""

import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv
import robin_stocks.robinhood as rh
from src.trade_history_sync import TradeHistorySyncService

# Setup logging
log_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(log_dir, exist_ok=True)

log_file = os.path.join(log_dir, f'trade_sync_{datetime.now().strftime("%Y%m%d")}.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def run_daily_sync():
    """
    Run daily trade sync
    Called automatically by Task Scheduler at 4:30 PM ET daily
    """
    logger.info("=" * 60)
    logger.info("Starting daily trade sync")
    logger.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')}")
    logger.info("=" * 60)

    load_dotenv()

    # Get Robinhood credentials
    rh_user = os.getenv('RH_USERNAME')
    rh_pass = os.getenv('RH_PASSWORD')

    if not rh_user or not rh_pass:
        logger.error("❌ Robinhood credentials not found in .env file")
        logger.error("Please set RH_USERNAME and RH_PASSWORD in .env")
        return False

    try:
        # Login to Robinhood
        logger.info("🔐 Logging into Robinhood...")
        rh.login(rh_user, rh_pass)
        logger.info("✅ Login successful")

        # Initialize sync service
        sync_service = TradeHistorySyncService()

        # Check last sync time
        last_sync = sync_service.get_last_sync_time()
        if last_sync:
            logger.info(f"📅 Last sync: {last_sync.strftime('%Y-%m-%d %I:%M:%S %p')}")
        else:
            logger.info("📅 No previous sync found - this is the first sync")

        # Sync trades
        logger.info("🔄 Syncing trades from Robinhood to database...")
        count = sync_service.sync_trades_from_robinhood(rh)

        if count > 0:
            logger.info(f"✅ Successfully synced {count} new closed trades")
        else:
            logger.info("✅ Sync complete - no new closed trades found")

        # Get summary stats
        trades = sync_service.get_closed_trades_from_db(days_back=30)
        logger.info(f"📊 Total closed trades in last 30 days: {len(trades)}")

        if trades:
            total_pl = sum(t['profit_loss'] for t in trades)
            logger.info(f"💰 30-day P/L: ${total_pl:,.2f}")

        # Logout
        rh.logout()
        logger.info("🔒 Logged out of Robinhood")

        logger.info("=" * 60)
        logger.info("✅ Daily sync completed successfully")
        logger.info("=" * 60)
        return True

    except Exception as e:
        logger.error("=" * 60)
        logger.error(f"❌ ERROR during daily sync: {e}")
        logger.error("=" * 60)
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = run_daily_sync()
    sys.exit(0 if success else 1)
