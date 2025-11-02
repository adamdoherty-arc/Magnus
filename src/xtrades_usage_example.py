"""
Xtrades.net Scraper - Usage Examples
=====================================
Demonstrates how to use the Xtrades scraper for various use cases.

Examples:
1. Basic scraping
2. Database integration
3. Batch processing multiple profiles
4. Error handling and retries
5. Integration with notification system
"""

import sys
from pathlib import Path
from typing import List, Dict
from datetime import datetime
import psycopg2
from psycopg2.extras import execute_values

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from xtrades_scraper import (
    XtradesScraper,
    LoginFailedException,
    ProfileNotFoundException,
    scrape_profile
)


# ============================================================================
# Example 1: Basic Usage
# ============================================================================

def example_basic_scraping():
    """Simple example of scraping a single profile"""
    print("\n" + "="*80)
    print("Example 1: Basic Scraping")
    print("="*80)

    scraper = XtradesScraper()

    try:
        # Login
        print("\n1. Logging in...")
        scraper.login()

        # Scrape profile
        print("\n2. Scraping profile 'behappy'...")
        alerts = scraper.get_profile_alerts("behappy", max_alerts=10)

        # Display results
        print(f"\n3. Found {len(alerts)} alerts:\n")
        for i, alert in enumerate(alerts, 1):
            print(f"Alert {i}:")
            print(f"  Ticker: {alert['ticker']}")
            print(f"  Strategy: {alert['strategy']}")
            print(f"  Action: {alert['action']}")
            if alert['entry_price']:
                print(f"  Entry: ${alert['entry_price']:.2f}")
            if alert['pnl']:
                print(f"  P&L: ${alert['pnl']:.2f}")
            print()

    except LoginFailedException as e:
        print(f"Login failed: {e}")
    except ProfileNotFoundException as e:
        print(f"Profile not found: {e}")
    finally:
        scraper.close()


# ============================================================================
# Example 2: Database Integration
# ============================================================================

def example_database_integration():
    """Example of storing scraped data in PostgreSQL database"""
    print("\n" + "="*80)
    print("Example 2: Database Integration")
    print("="*80)

    import os
    from dotenv import load_dotenv

    load_dotenv()

    # Database connection
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432'),
        database=os.getenv('DB_NAME', 'magnus'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD')
    )

    cursor = conn.cursor()

    try:
        # Scrape profile
        print("\n1. Scraping profile...")
        alerts = scrape_profile("behappy", max_alerts=20)

        # Ensure profile exists in database
        print("\n2. Checking profile in database...")
        cursor.execute("""
            INSERT INTO xtrades_profiles (username, display_name, active)
            VALUES (%s, %s, %s)
            ON CONFLICT (username) DO UPDATE
                SET last_sync = NOW(),
                    last_sync_status = 'success'
            RETURNING id
        """, ("behappy", "behappy", True))

        profile_id = cursor.fetchone()[0]
        print(f"   Profile ID: {profile_id}")

        # Insert trades
        print(f"\n3. Inserting {len(alerts)} trades...")
        insert_query = """
            INSERT INTO xtrades_trades (
                profile_id, ticker, strategy, action, entry_price,
                strike_price, expiration_date, quantity, pnl, pnl_percent,
                status, alert_text, alert_timestamp
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (xtrades_alert_id) DO UPDATE
                SET exit_price = EXCLUDED.exit_price,
                    pnl = EXCLUDED.pnl,
                    pnl_percent = EXCLUDED.pnl_percent,
                    status = EXCLUDED.status,
                    updated_at = NOW()
            RETURNING id
        """

        new_trades = 0
        for alert in alerts:
            cursor.execute(insert_query, (
                profile_id,
                alert['ticker'],
                alert['strategy'],
                alert['action'],
                alert['entry_price'],
                alert['strike_price'],
                alert['expiration_date'],
                alert['quantity'],
                alert['pnl'],
                alert['pnl_percent'],
                alert['status'],
                alert['alert_text'],
                alert['alert_timestamp']
            ))
            new_trades += 1

        # Update profile stats
        cursor.execute("""
            UPDATE xtrades_profiles
            SET total_trades_scraped = total_trades_scraped + %s,
                last_sync = NOW()
            WHERE id = %s
        """, (new_trades, profile_id))

        # Log sync operation
        cursor.execute("""
            INSERT INTO xtrades_sync_log (
                profiles_synced, trades_found, new_trades, status
            )
            VALUES (%s, %s, %s, %s)
        """, (1, len(alerts), new_trades, 'success'))

        conn.commit()
        print(f"   Successfully inserted {new_trades} trades")

        # Display summary
        print("\n4. Database Summary:")
        cursor.execute("""
            SELECT
                COUNT(*) as total_trades,
                COUNT(CASE WHEN status = 'open' THEN 1 END) as open_trades,
                COUNT(CASE WHEN status = 'closed' THEN 1 END) as closed_trades,
                SUM(pnl) as total_pnl
            FROM xtrades_trades
            WHERE profile_id = %s
        """, (profile_id,))

        stats = cursor.fetchone()
        print(f"   Total trades: {stats[0]}")
        print(f"   Open trades: {stats[1]}")
        print(f"   Closed trades: {stats[2]}")
        print(f"   Total P&L: ${stats[3]:.2f}" if stats[3] else "   Total P&L: N/A")

    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()


# ============================================================================
# Example 3: Batch Processing Multiple Profiles
# ============================================================================

def example_batch_processing():
    """Example of scraping multiple profiles efficiently"""
    print("\n" + "="*80)
    print("Example 3: Batch Processing Multiple Profiles")
    print("="*80)

    profiles = ["behappy", "trader1", "trader2"]  # Add real usernames

    scraper = XtradesScraper()
    results = {}

    try:
        # Login once
        print("\n1. Logging in...")
        scraper.login()

        # Scrape each profile
        for username in profiles:
            print(f"\n2. Scraping profile: {username}")
            try:
                alerts = scraper.get_profile_alerts(username, max_alerts=50)
                results[username] = {
                    'success': True,
                    'alerts': alerts,
                    'count': len(alerts)
                }
                print(f"   Found {len(alerts)} alerts")
            except ProfileNotFoundException:
                print(f"   Profile not found: {username}")
                results[username] = {
                    'success': False,
                    'error': 'Profile not found'
                }
            except Exception as e:
                print(f"   Error: {e}")
                results[username] = {
                    'success': False,
                    'error': str(e)
                }

        # Summary
        print("\n3. Batch Processing Summary:")
        successful = sum(1 for r in results.values() if r['success'])
        total_alerts = sum(r.get('count', 0) for r in results.values() if r['success'])
        print(f"   Profiles processed: {len(profiles)}")
        print(f"   Successful: {successful}")
        print(f"   Total alerts: {total_alerts}")

    finally:
        scraper.close()

    return results


# ============================================================================
# Example 4: Error Handling and Retries
# ============================================================================

def example_error_handling():
    """Example of robust error handling"""
    print("\n" + "="*80)
    print("Example 4: Error Handling and Retries")
    print("="*80)

    import time

    max_retries = 3
    retry_delay = 5

    for attempt in range(max_retries):
        scraper = XtradesScraper()

        try:
            print(f"\nAttempt {attempt + 1}/{max_retries}")

            # Login with retries
            scraper.login(retry_count=2)

            # Scrape profile
            alerts = scraper.get_profile_alerts("behappy")

            print(f"Success! Found {len(alerts)} alerts")
            return alerts

        except LoginFailedException as e:
            print(f"Login failed: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                print("Max retries reached. Giving up.")
                raise

        except ProfileNotFoundException as e:
            print(f"Profile error: {e}")
            # Don't retry for profile not found
            raise

        except Exception as e:
            print(f"Unexpected error: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                raise

        finally:
            scraper.close()

    return []


# ============================================================================
# Example 5: Integration with Telegram Notifications
# ============================================================================

def example_telegram_integration():
    """Example of sending alerts to Telegram"""
    print("\n" + "="*80)
    print("Example 5: Telegram Integration")
    print("="*80)

    import os
    import requests

    telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
    telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')

    if not telegram_token or not telegram_chat_id:
        print("Telegram not configured. Skipping.")
        return

    def send_telegram_message(message: str) -> bool:
        """Send message to Telegram"""
        try:
            url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
            data = {
                'chat_id': telegram_chat_id,
                'text': message,
                'parse_mode': 'Markdown'
            }
            response = requests.post(url, data=data)
            return response.status_code == 200
        except Exception as e:
            print(f"Failed to send Telegram message: {e}")
            return False

    try:
        # Scrape profile
        print("\n1. Scraping profile...")
        alerts = scrape_profile("behappy", max_alerts=5)

        # Send new alerts to Telegram
        print(f"\n2. Sending {len(alerts)} alerts to Telegram...")
        for alert in alerts:
            if alert['ticker']:
                message = f"""
🚨 *New Trade Alert*

*Ticker:* {alert['ticker']}
*Strategy:* {alert['strategy'] or 'N/A'}
*Action:* {alert['action'] or 'N/A'}
*Entry Price:* ${alert['entry_price']:.2f} if alert['entry_price'] else 'N/A'
*Strike:* ${alert['strike_price']:.2f} if alert['strike_price'] else 'N/A'
*Status:* {alert['status']}

_{alert['alert_text'][:100]}_
"""
                if send_telegram_message(message):
                    print(f"   Sent: {alert['ticker']}")
                else:
                    print(f"   Failed: {alert['ticker']}")

        print("\n3. Notifications sent!")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


# ============================================================================
# Example 6: Scheduled Scraping with APScheduler
# ============================================================================

def example_scheduled_scraping():
    """Example of scheduled scraping"""
    print("\n" + "="*80)
    print("Example 6: Scheduled Scraping (Press Ctrl+C to stop)")
    print("="*80)

    from apscheduler.schedulers.blocking import BlockingScheduler

    def scrape_job():
        """Job to scrape profiles"""
        print(f"\n[{datetime.now()}] Starting scheduled scrape...")

        try:
            alerts = scrape_profile("behappy", max_alerts=20)
            print(f"Found {len(alerts)} alerts")

            # Here you would:
            # 1. Store in database
            # 2. Check for new alerts
            # 3. Send notifications
            # 4. Update statistics

        except Exception as e:
            print(f"Error in scheduled job: {e}")

    # Create scheduler
    scheduler = BlockingScheduler()

    # Schedule job to run every hour
    scheduler.add_job(scrape_job, 'interval', hours=1)

    # Schedule job to run daily at specific time
    scheduler.add_job(scrape_job, 'cron', hour=9, minute=0)

    print("\nScheduled jobs:")
    print("  - Every hour")
    print("  - Daily at 9:00 AM")
    print("\nPress Ctrl+C to exit")

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("\nScheduler stopped")


# ============================================================================
# Main Menu
# ============================================================================

def main():
    """Interactive menu for examples"""
    examples = {
        '1': ('Basic Scraping', example_basic_scraping),
        '2': ('Database Integration', example_database_integration),
        '3': ('Batch Processing', example_batch_processing),
        '4': ('Error Handling', example_error_handling),
        '5': ('Telegram Integration', example_telegram_integration),
        '6': ('Scheduled Scraping', example_scheduled_scraping),
    }

    print("\n" + "="*80)
    print("Xtrades.net Scraper - Usage Examples")
    print("="*80)
    print("\nSelect an example to run:\n")

    for key, (name, _) in examples.items():
        print(f"  {key}. {name}")

    print("\n  0. Run all examples (except scheduled)")
    print("  q. Quit")

    choice = input("\nEnter choice: ").strip()

    if choice == 'q':
        print("Goodbye!")
        return

    if choice == '0':
        # Run all except scheduled
        for key in ['1', '2', '3', '4', '5']:
            try:
                _, func = examples[key]
                func()
                print("\n" + "-"*80)
            except Exception as e:
                print(f"Error running example: {e}")
                import traceback
                traceback.print_exc()
        return

    if choice in examples:
        _, func = examples[choice]
        try:
            func()
        except Exception as e:
            print(f"\nError: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("Invalid choice!")


if __name__ == "__main__":
    main()
