"""
Run this 1-2 days before earnings
Collect expected move for earnings in next 2 days

Schedule this to run daily at market close
"""
from src.earnings_expected_move import calculate_expected_move_from_yf
import psycopg2
import os
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

def collect_pre_earnings_data():
    """
    Collect expected move for earnings in next 2 days

    Schedule this to run daily at market close
    """
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432'),
        database=os.getenv('DB_NAME', 'magnus'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'postgres123!')
    )
    cur = conn.cursor()

    # Get earnings in next 2 days without expected move data
    cur.execute("""
        SELECT symbol, earnings_date, id
        FROM earnings_events
        WHERE earnings_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '2 days'
          AND pre_earnings_iv IS NULL
          AND has_occurred = FALSE
        ORDER BY earnings_date
    """)

    earnings = cur.fetchall()

    logger.info(f"Collecting expected move for {len(earnings)} upcoming earnings...")

    success_count = 0
    fail_count = 0

    for symbol, earnings_date, event_id in earnings:
        logger.info(f"Processing {symbol}...")

        # Calculate expected move
        result = calculate_expected_move_from_yf(symbol, earnings_date)

        if result:
            # Update database
            cur.execute("""
                UPDATE earnings_events
                SET
                    pre_earnings_iv = %s,
                    expected_move_dollars = %s,
                    expected_move_pct = %s,
                    pre_earnings_price = %s,
                    updated_at = NOW()
                WHERE id = %s
            """, (
                result['pre_earnings_iv'],
                result['expected_move_dollars'],
                result['expected_move_pct'],
                result['stock_price'],
                event_id
            ))

            conn.commit()
            success_count += 1
            logger.info(f"SUCCESS: {symbol}: Expected move ±{result['expected_move_pct']:.2f}%")

        else:
            fail_count += 1
            logger.warning(f"FAIL: {symbol}: Could not calculate expected move")

    cur.close()
    conn.close()

    logger.info(f"Pre-earnings data collection complete! Success: {success_count}, Failed: {fail_count}")
    return {'success': success_count, 'failed': fail_count}

if __name__ == "__main__":
    collect_pre_earnings_data()
