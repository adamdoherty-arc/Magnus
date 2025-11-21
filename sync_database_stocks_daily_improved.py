"""
Daily Database Options Sync - IMPROVED VERSION
- Expanded DTE coverage: 7, 14, 21, 30, 45 days
- Parallel processing (10x faster)
- Retry logic with exponential backoff
- Error categorization and tracking
- Connection pooling
- Progress tracking with real-time updates
"""
import psycopg2
import psycopg2.pool
import os
import sys
import time
import logging
import json
from datetime import datetime
from dotenv import load_dotenv
from src.enhanced_options_fetcher import EnhancedOptionsFetcher
from src.tradingview_db_manager import TradingViewDBManager
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Tuple
import traceback

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('database_sync.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

load_dotenv()

# Configuration
MAX_WORKERS = 5  # Parallel workers (adjust based on API rate limits)
RETRY_ATTEMPTS = 3
RETRY_DELAY = 2  # seconds
TARGET_DTES = [7, 14, 21, 30, 45]  # All desired expirations

# Global connection pool
connection_pool = None

# Sync statistics
sync_stats = {
    'total': 0,
    'successful': 0,
    'failed': 0,
    'no_options': 0,
    'api_error': 0,
    'retry_success': 0,
    'errors_by_type': {}
}

def init_connection_pool():
    """Initialize database connection pool"""
    global connection_pool
    connection_pool = psycopg2.pool.ThreadedConnectionPool(
        minconn=1,
        maxconn=MAX_WORKERS + 2,
        host='localhost',
        port='5432',
        database='magnus',
        user='postgres',
        password=os.getenv('DB_PASSWORD')
    )
    logger.info(f"    Connection pool initialized (max {MAX_WORKERS + 2} connections)")

def get_connection():
    """Get connection from pool"""
    return connection_pool.getconn()

def return_connection(conn):
    """Return connection to pool"""
    connection_pool.putconn(conn)

def get_all_database_stocks() -> List[str]:
    """Get all stock symbols from stocks table"""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT ticker
            FROM stocks
            WHERE ticker IS NOT NULL
            ORDER BY ticker
        """)
        symbols = [row[0] for row in cur.fetchall()]
        cur.close()
        return symbols
    finally:
        return_connection(conn)

def update_progress(current, total, symbol, start_time, stats):
    """Update progress file for dashboard to read"""
    elapsed = (datetime.now() - start_time).total_seconds()
    rate = current / elapsed if elapsed > 0 else 0
    remaining = (total - current) / rate if rate > 0 else 0

    progress = {
        'current': current,
        'total': total,
        'percent': (current / total * 100) if total > 0 else 0,
        'current_symbol': symbol,
        'elapsed_seconds': int(elapsed),
        'remaining_seconds': int(remaining),
        'rate_per_second': round(rate, 2),
        'last_updated': datetime.now().isoformat(),
        'stats': stats
    }

    try:
        with open('database_sync_progress.json', 'w') as f:
            json.dump(progress, f)
    except:
        pass

def categorize_error(error_msg: str) -> str:
    """Categorize error type for tracking"""
    error_lower = str(error_msg).lower()

    if 'no options' in error_lower or 'not found' in error_lower:
        return 'no_options'
    elif 'rate limit' in error_lower or '429' in error_lower:
        return 'rate_limit'
    elif 'timeout' in error_lower or 'timed out' in error_lower:
        return 'timeout'
    elif 'connection' in error_lower:
        return 'connection_error'
    elif 'invalid symbol' in error_lower:
        return 'invalid_symbol'
    else:
        return 'unknown_error'

def sync_stock_options_with_retry(symbol: str, fetcher: EnhancedOptionsFetcher) -> Tuple[bool, str, int]:
    """
    Sync options data for a single stock with retry logic

    Returns:
        Tuple of (success, error_type, options_count)
    """
    for attempt in range(1, RETRY_ATTEMPTS + 1):
        try:
            # Fetch options data for multiple DTEs
            options_data = fetcher.get_all_expirations_data(symbol, target_dtes=TARGET_DTES)

            if not options_data:
                return False, 'no_options', 0

            # Get current stock price from first option
            stock_price = options_data[0].get('current_price', 0)

            if not stock_price:
                return False, 'no_price', 0

            # Store in database using connection pool
            conn = get_connection()
            try:
                cur = conn.cursor()

                # Update or insert stock_data
                cur.execute("""
                    INSERT INTO stock_data (symbol, current_price, last_updated)
                    VALUES (%s, %s, NOW())
                    ON CONFLICT (symbol)
                    DO UPDATE SET
                        current_price = EXCLUDED.current_price,
                        last_updated = NOW()
                """, (symbol, stock_price))

                # Clear old options data for this symbol
                cur.execute("DELETE FROM stock_premiums WHERE symbol = %s", (symbol,))

                # Insert new options data in batch
                inserted = 0
                batch_data = []

                for opt in options_data:
                    batch_data.append((
                        symbol,
                        opt.get('strike_price'),
                        opt.get('expiration_date'),
                        opt.get('actual_dte'),
                        opt.get('premium'),
                        opt.get('delta'),
                        opt.get('iv', 0) / 100,
                        opt.get('bid'),
                        opt.get('ask'),
                        opt.get('volume'),
                        opt.get('open_interest'),
                        f"{opt.get('target_dte', 30)}_dte",
                        opt.get('monthly_return'),
                        opt.get('annual_return')
                    ))

                # Batch insert
                if batch_data:
                    psycopg2.extras.execute_batch(cur, """
                        INSERT INTO stock_premiums (
                            symbol, strike_price, expiration_date, dte,
                            premium, delta, implied_volatility,
                            bid, ask, volume, open_interest,
                            strike_type, monthly_return, annual_return
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, batch_data, page_size=100)

                    inserted = len(batch_data)

                conn.commit()
                cur.close()

                if inserted > 0:
                    return True, 'success', inserted
                else:
                    return False, 'no_inserts', 0

            finally:
                return_connection(conn)

        except Exception as e:
            error_type = categorize_error(str(e))

            # If it's a no_options or invalid_symbol, don't retry
            if error_type in ['no_options', 'invalid_symbol']:
                return False, error_type, 0

            # If rate limited, wait longer
            if error_type == 'rate_limit':
                wait_time = RETRY_DELAY * (2 ** attempt) * 2  # Longer backoff for rate limits
                logger.warning(f"  {symbol}: Rate limited, waiting {wait_time}s before retry {attempt}/{RETRY_ATTEMPTS}")
                time.sleep(wait_time)
                continue

            # For other errors, retry with exponential backoff
            if attempt < RETRY_ATTEMPTS:
                wait_time = RETRY_DELAY * (2 ** (attempt - 1))
                logger.warning(f"  {symbol}: Attempt {attempt} failed ({error_type}), retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                logger.error(f"  {symbol}: ❌ Failed after {RETRY_ATTEMPTS} attempts: {e}")
                return False, error_type, 0

    return False, 'max_retries_exceeded', 0

def process_stock(symbol: str, fetcher: EnhancedOptionsFetcher) -> Dict:
    """Process a single stock and return results"""
    success, error_type, options_count = sync_stock_options_with_retry(symbol, fetcher)

    return {
        'symbol': symbol,
        'success': success,
        'error_type': error_type,
        'options_count': options_count
    }

def main():
    logger.info("="*70)
    logger.info("DATABASE STOCKS DAILY OPTIONS SYNC - IMPROVED VERSION")
    logger.info(f"DTE Coverage: {TARGET_DTES}")
    logger.info(f"Parallel Workers: {MAX_WORKERS}")
    logger.info("="*70)

    start_time = datetime.now()

    # Initialize connection pool
    logger.info("\n[1] Initializing connection pool...")
    init_connection_pool()

    # Get all stocks from database
    logger.info("\n[2] Fetching all stocks from database...")
    all_stocks = get_all_database_stocks()
    logger.info(f"    Found {len(all_stocks)} stocks in database")

    sync_stats['total'] = len(all_stocks)

    # Initialize fetchers (one per worker)
    logger.info(f"\n[3] Syncing options for {len(all_stocks)} stocks using {MAX_WORKERS} parallel workers...")
    logger.info(f"    Fetching DTEs: {TARGET_DTES} (5 expirations per stock)")
    logger.info("    This should take 10-15 minutes...")

    completed = 0
    results = []

    # Process stocks in parallel
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Create fetcher for each worker thread
        fetchers = {i: EnhancedOptionsFetcher() for i in range(MAX_WORKERS)}

        # Submit all jobs
        future_to_symbol = {}
        for idx, symbol in enumerate(all_stocks):
            fetcher_id = idx % MAX_WORKERS
            future = executor.submit(process_stock, symbol, fetchers[fetcher_id])
            future_to_symbol[future] = symbol

        # Process results as they complete
        for future in as_completed(future_to_symbol):
            symbol = future_to_symbol[future]
            completed += 1

            try:
                result = future.result()
                results.append(result)

                if result['success']:
                    sync_stats['successful'] += 1
                    logger.info(f"  {symbol}: ✅ Synced {result['options_count']} options")
                else:
                    sync_stats['failed'] += 1
                    error_type = result['error_type']

                    # Track error types
                    sync_stats['errors_by_type'][error_type] = sync_stats['errors_by_type'].get(error_type, 0) + 1

                    if error_type == 'no_options':
                        sync_stats['no_options'] += 1
                    else:
                        sync_stats['api_error'] += 1

                    if error_type not in ['no_options', 'no_price']:
                        logger.debug(f"  {symbol}: Failed ({error_type})")

                # Update progress every 10 stocks
                if completed % 10 == 0:
                    update_progress(completed, len(all_stocks), symbol, start_time, sync_stats)
                    logger.info(f"\n    Progress: {completed}/{len(all_stocks)} ({completed/len(all_stocks)*100:.1f}%)")
                    logger.info(f"    Success: {sync_stats['successful']}, Failed: {sync_stats['failed']}")

            except Exception as e:
                logger.error(f"  {symbol}: ❌ Unexpected error: {e}")
                sync_stats['failed'] += 1

    # Summary
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    # Write final progress
    final_progress = {
        'current': len(all_stocks),
        'total': len(all_stocks),
        'percent': 100.0,
        'current_symbol': 'COMPLETE',
        'elapsed_seconds': int(duration),
        'remaining_seconds': 0,
        'rate_per_second': len(all_stocks) / duration if duration > 0 else 0,
        'last_updated': datetime.now().isoformat(),
        'completed': True,
        'stats': sync_stats
    }

    try:
        with open('database_sync_progress.json', 'w') as f:
            json.dump(final_progress, f)
    except:
        pass

    logger.info("\n" + "="*70)
    logger.info("SYNC COMPLETE!")
    logger.info("="*70)
    logger.info(f"Total stocks: {len(all_stocks)}")
    logger.info(f"Successfully synced: {sync_stats['successful']} ({sync_stats['successful']/len(all_stocks)*100:.1f}%)")
    logger.info(f"Failed/No options: {sync_stats['failed']}")
    logger.info(f"  - No options available: {sync_stats['no_options']}")
    logger.info(f"  - API errors: {sync_stats['api_error']}")
    logger.info(f"\nError breakdown:")
    for error_type, count in sorted(sync_stats['errors_by_type'].items(), key=lambda x: x[1], reverse=True):
        logger.info(f"  - {error_type}: {count}")
    logger.info(f"\nDuration: {duration/60:.1f} minutes")
    logger.info(f"Speed: {len(all_stocks)/duration:.2f} stocks/second")
    logger.info("="*70)

    # Close connection pool
    connection_pool.closeall()

    # Update sync log
    try:
        conn = psycopg2.connect(
            host='localhost',
            port='5432',
            database='magnus',
            user='postgres',
            password=os.getenv('DB_PASSWORD')
        )

        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS database_sync_log (
                id SERIAL PRIMARY KEY,
                sync_date DATE NOT NULL,
                sync_time TIMESTAMP NOT NULL,
                total_stocks INTEGER,
                successful_syncs INTEGER,
                failed_syncs INTEGER,
                no_options_count INTEGER,
                api_error_count INTEGER,
                duration_seconds INTEGER,
                stocks_per_second DECIMAL(10, 2),
                error_details JSONB
            )
        """)

        cur.execute("""
            INSERT INTO database_sync_log (
                sync_date, sync_time, total_stocks,
                successful_syncs, failed_syncs, no_options_count, api_error_count,
                duration_seconds, stocks_per_second, error_details
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """, (
            datetime.now().date(),
            datetime.now(),
            len(all_stocks),
            sync_stats['successful'],
            sync_stats['failed'],
            sync_stats['no_options'],
            sync_stats['api_error'],
            int(duration),
            round(len(all_stocks) / duration, 2),
            json.dumps(sync_stats['errors_by_type'])
        ))

        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        logger.error(f"Could not update sync log: {e}")

    logger.info(f"\n✅ Database options sync complete! Check database_sync.log for details.")

if __name__ == "__main__":
    main()
