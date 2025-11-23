"""
Daily automation for earnings calendar system
Run this via cron or Windows Task Scheduler

Schedule: Daily at 4:00 PM ET (after market close)
"""
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.earnings_calendar_sync import sync_earnings_calendar
from src.earnings_pre_earnings_collector import collect_pre_earnings_data
from src.earnings_post_earnings_collector import collect_post_earnings_data
from src.earnings_pattern_analyzer import update_all_patterns

def main():
    """
    Run all daily earnings tasks
    """
    print("=" * 80)
    print("DAILY EARNINGS AUTOMATION")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()

    # 1. Sync calendar (get upcoming earnings)
    print("STEP 1: Syncing earnings calendar...")
    print("-" * 80)
    try:
        sync_earnings_calendar(days_ahead=30)
        print("SUCCESS: Calendar sync complete")
    except Exception as e:
        print(f"ERROR: Calendar sync failed: {e}")
    print()

    # 2. Collect pre-earnings data (expected move)
    print("STEP 2: Collecting pre-earnings data...")
    print("-" * 80)
    try:
        collect_pre_earnings_data()
        print("SUCCESS: Pre-earnings data collection complete")
    except Exception as e:
        print(f"ERROR: Pre-earnings collection failed: {e}")
    print()

    # 3. Collect post-earnings data (actual results)
    print("STEP 3: Collecting post-earnings results...")
    print("-" * 80)
    try:
        collect_post_earnings_data()
        print("SUCCESS: Post-earnings data collection complete")
    except Exception as e:
        print(f"ERROR: Post-earnings collection failed: {e}")
    print()

    # 4. Update pattern analysis (weekly - check day of week)
    if datetime.now().weekday() == 5:  # Saturday
        print("STEP 4: Updating pattern analysis (weekly)...")
        print("-" * 80)
        try:
            update_all_patterns()
            print("SUCCESS: Pattern analysis complete")
        except Exception as e:
            print(f"ERROR: Pattern analysis failed: {e}")
        print()

    print("=" * 80)
    print("ALL TASKS COMPLETE")
    print(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

if __name__ == "__main__":
    main()
