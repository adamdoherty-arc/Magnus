"""
Real-Time Kalshi Price Monitor
Updates prices every 30 seconds for active markets
Tracks price changes and alerts on significant moves
"""

import time
import sys
from datetime import datetime, timezone
from src.kalshi_public_client import KalshiPublicClient
from src.kalshi_db_manager import KalshiDBManager
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def monitor_prices(interval_seconds=30, min_price_change=0.05):
    """
    Monitor Kalshi prices in real-time

    Args:
        interval_seconds: How often to check prices
        min_price_change: Minimum price change to log (5% = 0.05)
    """

    client = KalshiPublicClient()  # No auth needed!
    db = KalshiDBManager()

    logger.info(f"Starting real-time price monitor (checking every {interval_seconds}s)")
    logger.info(f"Alerting on price changes >= {min_price_change * 100}%")

    # Store previous prices
    previous_prices = {}

    try:
        while True:
            logger.info("=== Fetching latest prices ===")

            # Get active markets from database
            active_markets = db.get_active_markets()

            if not active_markets:
                logger.warning("No active markets found in database")
                time.sleep(interval_seconds)
                continue

            logger.info(f"Monitoring {len(active_markets)} markets")

            # Track changes
            price_changes = []
            updated_count = 0

            for market in active_markets:
                ticker = market.get('ticker')
                old_yes = market.get('yes_price')
                old_no = market.get('no_price')

                try:
                    # Fetch latest price from Kalshi API
                    fresh_market = client.get_market(ticker)

                    if not fresh_market:
                        continue

                    new_yes = fresh_market.get('yes_price')
                    new_no = fresh_market.get('no_price')

                    # Update database
                    if new_yes is not None and new_no is not None:
                        db.update_market_prices(ticker, new_yes, new_no)
                        updated_count += 1

                        # Check for significant changes
                        if old_yes and old_yes > 0:
                            yes_change = abs(new_yes - old_yes) / old_yes

                            if yes_change >= min_price_change:
                                change_pct = (new_yes - old_yes) / old_yes * 100
                                price_changes.append({
                                    'ticker': ticker,
                                    'title': market.get('title', '')[:60],
                                    'old_yes': old_yes,
                                    'new_yes': new_yes,
                                    'change_pct': change_pct
                                })

                except Exception as e:
                    logger.error(f"Error fetching {ticker}: {e}")
                    continue

            logger.info(f"✓ Updated {updated_count}/{len(active_markets)} markets")

            # Display significant price changes
            if price_changes:
                logger.info(f"\n🚨 PRICE ALERTS ({len(price_changes)} markets):")

                for change in sorted(price_changes, key=lambda x: abs(x['change_pct']), reverse=True):
                    direction = "📈" if change['change_pct'] > 0 else "📉"
                    logger.info(
                        f"{direction} {change['ticker']}: "
                        f"{change['old_yes']:.2%} → {change['new_yes']:.2%} "
                        f"({change['change_pct']:+.1f}%) | {change['title']}"
                    )

            # Wait before next check
            logger.info(f"Waiting {interval_seconds}s...\n")
            time.sleep(interval_seconds)

    except KeyboardInterrupt:
        logger.info("\n✓ Price monitor stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


def update_all_prices_once():
    """Update all prices once and exit"""

    client = KalshiPublicClient()  # No auth needed!
    db = KalshiDBManager()

    logger.info("Fetching all market prices...")

    active_markets = db.get_active_markets()

    if not active_markets:
        logger.warning("No active markets found")
        return

    logger.info(f"Updating {len(active_markets)} markets...")

    updated = 0
    failed = 0

    for i, market in enumerate(active_markets, 1):
        ticker = market.get('ticker')

        if i % 50 == 0:
            logger.info(f"Progress: {i}/{len(active_markets)} ({i/len(active_markets)*100:.1f}%)")

        try:
            fresh_market = client.get_market(ticker)

            if fresh_market:
                yes_price = fresh_market.get('yes_price')
                no_price = fresh_market.get('no_price')

                if yes_price is not None and no_price is not None:
                    db.update_market_prices(ticker, yes_price, no_price)
                    updated += 1
        except Exception as e:
            logger.debug(f"Failed to update {ticker}: {e}")
            failed += 1

    logger.info(f"✓ Updated {updated} markets, {failed} failed")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Kalshi Real-Time Price Monitor")
    parser.add_argument('--once', action='store_true', help='Update all prices once and exit')
    parser.add_argument('--interval', type=int, default=30, help='Check interval in seconds (default: 30)')
    parser.add_argument('--threshold', type=float, default=0.05, help='Alert threshold (default: 0.05 = 5%%)')

    args = parser.parse_args()

    if args.once:
        update_all_prices_once()
    else:
        monitor_prices(args.interval, args.threshold)
