"""
Analyze historical earnings patterns for each stock
"""
import psycopg2
import os
from dotenv import load_dotenv
import logging
import statistics

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

def calculate_earnings_patterns(symbol):
    """
    Calculate beat rate, consistency, and quality metrics

    Returns:
        Dictionary with pattern analysis or None
    """
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432'),
        database=os.getenv('DB_NAME', 'magnus'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'postgres123!')
    )
    cur = conn.cursor()

    # Get last 12 quarters of earnings
    cur.execute("""
        SELECT
            eps_actual,
            eps_estimate,
            eps_surprise_percent,
            beat_miss,
            price_move_percent,
            expected_move_pct,
            CASE
                WHEN expected_move_pct IS NOT NULL AND price_move_percent IS NOT NULL THEN
                    ABS(price_move_percent) > expected_move_pct
                ELSE NULL
            END as exceeded_expected
        FROM earnings_history
        WHERE symbol = %s
          AND eps_actual IS NOT NULL
          AND eps_estimate IS NOT NULL
        ORDER BY report_date DESC
        LIMIT 12
    """, (symbol,))

    history = cur.fetchall()
    cur.close()
    conn.close()

    if not history:
        return None

    # Calculate metrics
    total = len(history)
    beats = sum(1 for h in history if h[3] == 'beat')
    misses = sum(1 for h in history if h[3] == 'miss')
    meets = sum(1 for h in history if h[3] == 'meet')

    beat_rate = (beats / total) * 100
    miss_rate = (misses / total) * 100
    meet_rate = (meets / total) * 100

    # Average surprise
    surprises = [float(h[2]) for h in history if h[2] is not None]
    avg_surprise = sum(surprises) / len(surprises) if surprises else 0

    # Consistency (standard deviation)
    surprise_std = statistics.stdev(surprises) if len(surprises) > 1 else 0

    # Exceed expected move rate
    exceeded_count = sum(1 for h in history if h[6] is True)
    valid_count = sum(1 for h in history if h[5] is not None)
    exceed_rate = (exceeded_count / valid_count * 100) if valid_count > 0 else 0

    # Calculate quality score (0-100)
    quality_score = calculate_quality_score(beat_rate, avg_surprise, surprise_std)

    result = {
        'symbol': symbol,
        'quarters_analyzed': total,
        'beat_rate': round(beat_rate, 2),
        'miss_rate': round(miss_rate, 2),
        'meet_rate': round(meet_rate, 2),
        'avg_surprise_pct': round(avg_surprise, 2),
        'surprise_std': round(surprise_std, 2),
        'exceed_expected_move_rate': round(exceed_rate, 2),
        'quality_score': round(quality_score, 2)
    }

    return result

def calculate_quality_score(beat_rate, avg_surprise, consistency):
    """
    Calculate 0-100 quality score

    High score = consistent beater, good trading opportunity
    Low score = unpredictable, avoid
    """
    score = 0

    # Beat rate component (0-40 points)
    score += (beat_rate / 100) * 40

    # Positive surprise component (0-30 points)
    score += min(abs(avg_surprise), 10) * 3

    # Consistency component (0-30 points)
    # Lower std dev = better
    consistency_score = max(0, 30 - consistency)
    score += consistency_score

    return min(100, score)

def update_all_patterns():
    """
    Calculate patterns for all stocks with earnings history
    """
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432'),
        database=os.getenv('DB_NAME', 'magnus'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'postgres123!')
    )
    cur = conn.cursor()

    # Get all symbols with earnings history
    cur.execute("""
        SELECT DISTINCT symbol
        FROM earnings_history
        WHERE eps_actual IS NOT NULL
    """)

    symbols = [row[0] for row in cur.fetchall()]

    logger.info(f"Calculating patterns for {len(symbols)} symbols...")

    success_count = 0
    fail_count = 0

    for symbol in symbols:
        patterns = calculate_earnings_patterns(symbol)

        if patterns:
            # Store in pattern analysis table
            cur.execute("""
                INSERT INTO earnings_pattern_analysis (
                    symbol, beat_rate_8q, miss_rate_8q, meet_rate_8q,
                    avg_surprise_pct_8q, surprise_std_8q,
                    exceed_expected_move_rate, quality_score,
                    quarters_analyzed, last_updated
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                ON CONFLICT (symbol)
                DO UPDATE SET
                    beat_rate_8q = EXCLUDED.beat_rate_8q,
                    miss_rate_8q = EXCLUDED.miss_rate_8q,
                    meet_rate_8q = EXCLUDED.meet_rate_8q,
                    avg_surprise_pct_8q = EXCLUDED.avg_surprise_pct_8q,
                    surprise_std_8q = EXCLUDED.surprise_std_8q,
                    exceed_expected_move_rate = EXCLUDED.exceed_expected_move_rate,
                    quality_score = EXCLUDED.quality_score,
                    quarters_analyzed = EXCLUDED.quarters_analyzed,
                    last_updated = NOW()
            """, (
                symbol,
                patterns['beat_rate'],
                patterns['miss_rate'],
                patterns['meet_rate'],
                patterns['avg_surprise_pct'],
                patterns['surprise_std'],
                patterns['exceed_expected_move_rate'],
                patterns['quality_score'],
                patterns['quarters_analyzed']
            ))

            conn.commit()
            success_count += 1

            logger.info(f"SUCCESS: {symbol}: Beat Rate {patterns['beat_rate']:.1f}%, "
                  f"Quality Score {patterns['quality_score']:.0f}/100")
        else:
            fail_count += 1
            logger.warning(f"FAIL: {symbol}: No pattern data")

    cur.close()
    conn.close()

    logger.info(f"Pattern analysis complete! Success: {success_count}, Failed: {fail_count}")
    return {'success': success_count, 'failed': fail_count}

if __name__ == "__main__":
    update_all_patterns()
