"""
Test Database Sync - Test with 10 stocks only (30-day options)
"""
import psycopg2
import psycopg2.pool
import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv
from src.enhanced_options_fetcher import EnhancedOptionsFetcher
from concurrent.futures import ThreadPoolExecutor, as_completed

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

TARGET_DTES = [30]  # 30-day options only

def get_test_stocks():
    """Get 10 test stocks"""
    conn = psycopg2.connect(
        host='localhost',
        port='5432',
        database='magnus',
        user='postgres',
        password=os.getenv('DB_PASSWORD')
    )

    cur = conn.cursor()
    cur.execute("""
        SELECT ticker
        FROM stocks
        WHERE ticker IS NOT NULL
        LIMIT 10
    """)
    symbols = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()

    return symbols

def sync_stock(symbol, fetcher):
    """Sync one stock"""
    try:
        options_data = fetcher.get_all_expirations_data(symbol, target_dtes=TARGET_DTES)

        if not options_data:
            return f"{symbol}: No options"

        # Count options by DTE
        dte_counts = {}
        for opt in options_data:
            dte = opt.get('target_dte', 0)
            dte_counts[dte] = dte_counts.get(dte, 0) + 1

        total = len(options_data)
        breakdown = ", ".join([f"{dte}dte: {count}" for dte, count in sorted(dte_counts.items())])

        return f"{symbol}: ✅ {total} options ({breakdown})"

    except Exception as e:
        return f"{symbol}: ❌ Error: {str(e)[:50]}"

def main():
    logger.info("="*70)
    logger.info("DATABASE SYNC TEST - 10 Stocks")
    logger.info(f"DTE Coverage: {TARGET_DTES}")
    logger.info("="*70)

    test_stocks = get_test_stocks()
    logger.info(f"\nTesting with stocks: {', '.join(test_stocks)}")

    start = datetime.now()
    fetcher = EnhancedOptionsFetcher()

    logger.info("\n📊 Fetching options data...\n")

    for symbol in test_stocks:
        result = sync_stock(symbol, fetcher)
        logger.info(f"  {result}")

    duration = (datetime.now() - start).total_seconds()
    logger.info(f"\n⏱️  Duration: {duration:.1f} seconds ({len(test_stocks)/duration:.2f} stocks/sec)")
    logger.info("="*70)
    logger.info("✅ Test Complete!")

if __name__ == "__main__":
    main()
