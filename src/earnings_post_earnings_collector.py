"""
Collect actual price movement after earnings
Run this daily to capture post-earnings metrics
"""
import yfinance as yf
from datetime import datetime, timedelta
import psycopg2
import os
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

def collect_post_earnings_data():
    """
    Collect actual price movement 1 day after earnings

    Run this daily to capture post-earnings metrics
    """
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432'),
        database=os.getenv('DB_NAME', 'magnus'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'postgres123!')
    )
    cur = conn.cursor()

    # Get earnings from yesterday that need post-data
    cur.execute("""
        SELECT symbol, earnings_date, pre_earnings_price, expected_move_pct, id
        FROM earnings_events
        WHERE earnings_date = CURRENT_DATE - INTERVAL '1 day'
          AND post_earnings_price IS NULL
          AND pre_earnings_price IS NOT NULL
    """)

    earnings = cur.fetchall()

    logger.info(f"Collecting post-earnings data for {len(earnings)} events...")

    success_count = 0
    fail_count = 0

    for symbol, earnings_date, pre_price, expected_move, event_id in earnings:
        try:
            # Get stock data
            ticker = yf.Ticker(symbol)

            # Get price 1 day after earnings
            post_date = earnings_date + timedelta(days=1)

            # Fetch historical data (get a couple days window in case of market holiday)
            hist = ticker.history(start=post_date, end=post_date + timedelta(days=3))

            if hist.empty:
                logger.warning(f"{symbol}: No price data available yet")
                fail_count += 1
                continue

            post_price = hist.iloc[0]['Close']

            # Calculate actual move
            price_move_dollars = post_price - pre_price
            price_move_pct = (price_move_dollars / pre_price) * 100

            # Did it exceed expected move?
            exceeded_expected = abs(price_move_pct) > expected_move if expected_move else False

            # Get volume data
            post_volume = hist.iloc[0]['Volume']

            # Get average volume (20 days before earnings)
            hist_volume = ticker.history(
                start=earnings_date - timedelta(days=30),
                end=earnings_date
            )
            avg_volume = hist_volume['Volume'].mean() if not hist_volume.empty else None
            volume_ratio = post_volume / avg_volume if avg_volume and avg_volume > 0 else None

            # Get post-earnings IV if possible (from options expiring soon)
            post_iv = None
            try:
                expirations = ticker.options
                if expirations:
                    # Get nearest expiration
                    exp = expirations[0]
                    opt_chain = ticker.option_chain(exp)
                    if not opt_chain.calls.empty:
                        # Get ATM IV
                        atm_strike = round(post_price / 5) * 5
                        atm_calls = opt_chain.calls[opt_chain.calls['strike'] == atm_strike]
                        if not atm_calls.empty:
                            post_iv = atm_calls.iloc[0]['impliedVolatility']
            except:
                pass

            # Update database
            cur.execute("""
                UPDATE earnings_events
                SET
                    post_earnings_price = %s,
                    price_move_dollars = %s,
                    price_move_percent = %s,
                    exceeded_expected_move = %s,
                    volume_ratio = %s,
                    post_earnings_iv = %s,
                    has_occurred = TRUE,
                    updated_at = NOW()
                WHERE id = %s
            """, (
                post_price,
                price_move_dollars,
                price_move_pct,
                exceeded_expected,
                volume_ratio,
                post_iv,
                event_id
            ))

            conn.commit()
            success_count += 1

            exceed_text = "EXCEEDED" if exceeded_expected else "within"
            logger.info(f"SUCCESS: {symbol}: {price_move_pct:+.2f}% "
                  f"(expected ±{expected_move:.2f}%, {exceed_text})")

        except Exception as e:
            logger.error(f"ERROR processing {symbol}: {e}")
            fail_count += 1
            continue

    cur.close()
    conn.close()

    logger.info(f"Post-earnings data collection complete! Success: {success_count}, Failed: {fail_count}")
    return {'success': success_count, 'failed': fail_count}

if __name__ == "__main__":
    collect_post_earnings_data()
