"""
Sync earnings calendar from NASDAQ (free, comprehensive)
Run daily to keep calendar updated
"""
from finance_calendars import finance_calendars as fc
from datetime import datetime, timedelta
import psycopg2
import os
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

def sync_earnings_calendar(days_ahead=30):
    """
    Sync upcoming earnings from NASDAQ public API

    Args:
        days_ahead: Number of days to fetch ahead

    Returns:
        Number of earnings events synced
    """
    # Connect to database
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432'),
        database=os.getenv('DB_NAME', 'magnus'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'postgres123!')
    )
    cur = conn.cursor()

    synced_count = 0
    today = datetime.now()

    logger.info(f"Syncing earnings calendar for next {days_ahead} days...")

    for day_offset in range(days_ahead):
        target_date = today + timedelta(days=day_offset)

        try:
            # Fetch earnings for this date
            earnings = fc.get_earnings_by_date(target_date)

            if earnings is None or earnings.empty:
                continue

            # Insert each earnings event
            for _, row in earnings.iterrows():
                try:
                    cur.execute("""
                        INSERT INTO earnings_events (
                            symbol,
                            earnings_date,
                            is_confirmed,
                            has_occurred,
                            created_at,
                            updated_at
                        )
                        VALUES (%s, %s, TRUE, FALSE, NOW(), NOW())
                        ON CONFLICT (symbol, earnings_date)
                        DO UPDATE SET
                            is_confirmed = TRUE,
                            updated_at = NOW()
                    """, (
                        row['symbol'],
                        target_date.date()
                    ))

                    synced_count += 1

                except Exception as e:
                    logger.warning(f"Error syncing {row['symbol']}: {e}")
                    continue

            conn.commit()
            logger.info(f"Synced {len(earnings)} events for {target_date.strftime('%Y-%m-%d')}")

        except Exception as e:
            logger.error(f"Error fetching date {target_date}: {e}")
            continue

    cur.close()
    conn.close()

    logger.info(f"Total synced: {synced_count} earnings events")
    return synced_count

if __name__ == "__main__":
    sync_earnings_calendar(days_ahead=30)
