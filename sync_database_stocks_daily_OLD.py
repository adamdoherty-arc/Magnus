"""
Daily Database Options Sync - Runs AFTER Market Opens
Syncs options data for ALL stocks in the stocks table
Completely separate from TradingView watchlist syncs
"""
import psycopg2
import os
import sys
import time
import logging
import json
from datetime import datetime
from dotenv import load_dotenv
from src.enhanced_options_fetcher import EnhancedOptionsFetcher
from src.tradingview_db_manager import TradingViewDBManager

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

def get_all_database_stocks():
    """Get all stock symbols from stocks table"""
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
        ORDER BY ticker
    """)
    symbols = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()

    return symbols

def update_progress(current, total, symbol, start_time):
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
        'last_updated': datetime.now().isoformat()
    }

    try:
        with open('database_sync_progress.json', 'w') as f:
            json.dump(progress, f)
    except:
        pass

def sync_stock_options(symbol, fetcher, tv_manager):
    """Sync options data for a single stock"""
    try:
        # Fetch options data for 30-day expiration only (simplified)
        options_data = fetcher.get_all_expirations_data(symbol, target_dtes=[30])

        if not options_data:
            logger.debug(f"  {symbol}: No options data available")
            return False

        # Get current stock price from first option (all have same current_price)
        stock_price = options_data[0].get('current_price', 0)

        if not stock_price:
            logger.debug(f"  {symbol}: Could not get current price")
            return False

        # Store in database
        conn = tv_manager.get_connection()
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

        # Insert new options data
        inserted = 0
        for opt in options_data:
            try:
                # Map field names from get_all_expirations_data() to database
                # actual_dte -> dte
                # iv (percentage) -> implied_volatility (decimal)
                # target_dte -> strike_type (e.g., "7_dte", "30_dte")

                cur.execute("""
                    INSERT INTO stock_premiums (
                        symbol, strike_price, expiration_date, dte,
                        premium, delta, implied_volatility,
                        bid, ask, volume, open_interest,
                        strike_type, monthly_return, annual_return
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """, (
                    symbol,
                    opt.get('strike_price'),
                    opt.get('expiration_date'),
                    opt.get('actual_dte'),  # Use actual_dte, not dte
                    opt.get('premium'),
                    opt.get('delta'),
                    opt.get('iv', 0) / 100,  # Convert IV from percentage to decimal
                    opt.get('bid'),
                    opt.get('ask'),
                    opt.get('volume'),
                    opt.get('open_interest'),
                    f"{opt.get('target_dte', 30)}_dte",  # Create strike_type from target_dte
                    opt.get('monthly_return'),
                    opt.get('annual_return')
                ))
                inserted += 1
            except Exception as e:
                logger.debug(f"    Error inserting option: {e}")
                continue

        conn.commit()
        cur.close()
        conn.close()

        if inserted > 0:
            logger.info(f"  {symbol}: ✅ Synced {inserted} options")
            return True
        else:
            logger.debug(f"  {symbol}: No options inserted")
            return False

    except Exception as e:
        logger.error(f"  {symbol}: ❌ Error: {e}")
        return False

def main():
    logger.info("="*70)
    logger.info("DATABASE STOCKS DAILY OPTIONS SYNC - AFTER MARKET OPEN")
    logger.info("="*70)

    start_time = datetime.now()

    # Get all stocks from database
    logger.info("\n[1] Fetching all stocks from database...")
    all_stocks = get_all_database_stocks()
    logger.info(f"    Found {len(all_stocks)} stocks in database")

    # Initialize fetchers
    logger.info("\n[2] Initializing options data fetchers...")
    fetcher = EnhancedOptionsFetcher()
    tv_manager = TradingViewDBManager()

    # Sync each stock
    logger.info(f"\n[3] Syncing 30-day options premiums for {len(all_stocks)} stocks...")
    logger.info("    This may take 3-5 minutes (30-day options only)...")

    successful = 0
    failed = 0
    no_options = 0

    for idx, symbol in enumerate(all_stocks, 1):
        # Update progress file
        update_progress(idx, len(all_stocks), symbol, start_time)

        if idx % 10 == 0:
            logger.info(f"\n    Progress: {idx}/{len(all_stocks)} ({idx/len(all_stocks)*100:.1f}%)")

        result = sync_stock_options(symbol, fetcher, tv_manager)

        if result:
            successful += 1
        else:
            failed += 1

        # Rate limiting - small delay between requests
        time.sleep(0.3)

        # Larger delay every 50 stocks to avoid rate limits
        if idx % 50 == 0:
            logger.info("    Taking 5 second break to avoid rate limits...")
            time.sleep(5)

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
        'successful': successful,
        'failed': failed
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
    logger.info(f"Successfully synced: {successful}")
    logger.info(f"Failed/No options: {failed}")
    logger.info(f"Duration: {duration/60:.1f} minutes")
    logger.info("="*70)

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
                duration_seconds INTEGER
            )
        """)

        cur.execute("""
            INSERT INTO database_sync_log (
                sync_date, sync_time, total_stocks,
                successful_syncs, failed_syncs, duration_seconds
            ) VALUES (
                %s, %s, %s, %s, %s, %s
            )
        """, (
            datetime.now().date(),
            datetime.now(),
            len(all_stocks),
            successful,
            failed,
            int(duration)
        ))

        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        logger.error(f"Could not update sync log: {e}")

    logger.info(f"\n✅ Database options sync complete! Check database_sync.log for details.")

if __name__ == "__main__":
    main()
