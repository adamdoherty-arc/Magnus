"""
Complete Kalshi Sync Script
1. Fetches NFL and College Football markets from Kalshi API
2. Stores markets in database
3. Generates AI predictions and rankings
4. Stores predictions in database
"""

import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv
from src.kalshi_client import KalshiClient
from src.kalshi_db_manager import KalshiDBManager
from src.kalshi_ai_evaluator import KalshiAIEvaluator

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


def sync_complete():
    """Complete Kalshi sync: markets + AI predictions"""
    logger.info("="*70)
    logger.info("KALSHI COMPLETE SYNC - Markets + AI Predictions")
    logger.info("="*70)

    start_time = datetime.now()

    # ========================================================================
    # STEP 1: Initialize clients
    # ========================================================================
    logger.info("\n[1] Initializing clients...")

    client = KalshiClient()
    if not client.login():
        logger.error("Failed to login to Kalshi. Check credentials in .env file.")
        return False
    logger.info("    ✅ Kalshi API client ready")

    db = KalshiDBManager()
    logger.info("    ✅ Database manager ready")

    evaluator = KalshiAIEvaluator()
    logger.info("    ✅ AI evaluator ready")

    # ========================================================================
    # STEP 2: Fetch football markets from Kalshi
    # ========================================================================
    logger.info("\n[2] Fetching football markets from Kalshi API...")

    football_markets = client.get_football_markets()
    nfl_markets = football_markets['nfl']
    college_markets = football_markets['college']

    logger.info(f"    Found {len(nfl_markets)} NFL markets")
    logger.info(f"    Found {len(college_markets)} College Football markets")

    total_markets = len(nfl_markets) + len(college_markets)

    if total_markets == 0:
        logger.warning("    ⚠️  No football markets found!")
        return False

    # ========================================================================
    # STEP 3: Store markets in database
    # ========================================================================
    logger.info("\n[3] Storing markets in database...")

    nfl_stored = 0
    college_stored = 0

    try:
        if nfl_markets:
            nfl_stored = db.store_markets(nfl_markets, market_type='nfl')
            logger.info(f"    ✅ Stored {nfl_stored} NFL markets")
    except Exception as e:
        logger.error(f"    ❌ Error storing NFL markets: {e}")

    try:
        if college_markets:
            college_stored = db.store_markets(college_markets, market_type='college')
            logger.info(f"    ✅ Stored {college_stored} College Football markets")
    except Exception as e:
        logger.error(f"    ❌ Error storing College markets: {e}")

    # ========================================================================
    # STEP 4: Generate AI predictions for all markets
    # ========================================================================
    logger.info("\n[4] Generating AI predictions...")

    # Get all active markets from database
    all_active_markets = db.get_active_markets()
    logger.info(f"    Found {len(all_active_markets)} total active markets")

    if not all_active_markets:
        logger.warning("    ⚠️  No active markets to evaluate!")
    else:
        # Generate predictions
        predictions = evaluator.evaluate_markets(all_active_markets)
        logger.info(f"    ✅ Generated {len(predictions)} predictions")

        # Display top 10 opportunities
        logger.info("\n    📊 Top 10 Opportunities:")
        for i, pred in enumerate(predictions[:10], 1):
            action_emoji = "🟢" if pred['recommended_action'] == 'strong_buy' else "🟡" if pred['recommended_action'] == 'buy' else "⚪"
            logger.info(f"    {i}. {action_emoji} {pred['ticker'][:30]} - "
                       f"{pred['predicted_outcome'].upper()} "
                       f"(Edge: {pred['edge_percentage']:.1f}%, "
                       f"Confidence: {pred['confidence_score']:.0f}%)")

        # ====================================================================
        # STEP 5: Store predictions in database
        # ====================================================================
        logger.info("\n[5] Storing predictions in database...")

        try:
            predictions_stored = db.store_predictions(predictions)
            logger.info(f"    ✅ Stored {predictions_stored} predictions")
        except Exception as e:
            logger.error(f"    ❌ Error storing predictions: {e}")
            import traceback
            traceback.print_exc()

    # ========================================================================
    # STEP 6: Log sync operation
    # ========================================================================
    end_time = datetime.now()
    duration = int((end_time - start_time).total_seconds())

    db.log_sync(
        sync_type='markets',
        market_type='all',
        total=total_markets,
        successful=nfl_stored + college_stored,
        failed=total_markets - (nfl_stored + college_stored),
        duration=duration,
        status='completed'
    )

    # ========================================================================
    # SUMMARY
    # ========================================================================
    logger.info("\n" + "="*70)
    logger.info("SYNC COMPLETE!")
    logger.info("="*70)
    logger.info(f"\nMarkets:")
    logger.info(f"  NFL: {len(nfl_markets)} found, {nfl_stored} stored")
    logger.info(f"  College: {len(college_markets)} found, {college_stored} stored")
    logger.info(f"  Total: {total_markets} markets")

    logger.info(f"\nPredictions:")
    logger.info(f"  Generated: {len(predictions) if all_active_markets else 0}")
    logger.info(f"  Strong Buy: {sum(1 for p in predictions if p['recommended_action'] == 'strong_buy')}")
    logger.info(f"  Buy: {sum(1 for p in predictions if p['recommended_action'] == 'buy')}")
    logger.info(f"  Hold: {sum(1 for p in predictions if p['recommended_action'] == 'hold')}")
    logger.info(f"  Pass: {sum(1 for p in predictions if p['recommended_action'] == 'pass')}")

    logger.info(f"\nDuration: {duration} seconds ({duration/60:.1f} minutes)")
    logger.info("="*70)

    # Database stats
    logger.info("\n[6] Database Statistics:")
    stats = db.get_stats()
    logger.info(f"    Total Markets in DB: {stats['total_markets']}")
    logger.info(f"    Active Markets: {stats['active_markets']}")
    logger.info(f"    Markets by Type: {stats['markets_by_type']}")
    logger.info(f"    Total Predictions: {stats['total_predictions']}")

    return True


if __name__ == "__main__":
    try:
        success = sync_complete()
        if success:
            logger.info("\n✅ Kalshi complete sync finished successfully!")
            sys.exit(0)
        else:
            logger.error("\n❌ Kalshi sync encountered errors!")
            sys.exit(1)
    except Exception as e:
        logger.error(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
