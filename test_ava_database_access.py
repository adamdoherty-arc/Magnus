"""
Test AVA Database Access
========================

Verify that AVA can access database and retrieve data properly
"""

import sys
import asyncio
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from src.ava.magnus_integration import MagnusIntegration
from src.ava.db_manager import get_db_manager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_database_access():
    """Test database access for AVA"""
    print("=" * 60)
    print("Testing AVA Database Access")
    print("=" * 60)
    print()

    # Test 1: Database Connection
    print("Test 1: Database Connection")
    try:
        db = get_db_manager()
        with db.get_cursor() as cursor:
            cursor.execute("SELECT 1 as test")
            result = cursor.fetchone()
            print(f"[OK] Database connection working: {result}")
    except Exception as e:
        print(f"[FAIL] Database connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    print()

    # Test 2: Check Tables Exist
    print("Test 2: Check Tables Exist")
    try:
        tables = [
            'portfolio_balances',
            'options_positions',
            'csp_opportunities',
            'tradingview_watchlists',
            'xtrades_following',
            'ci_enhancements'
        ]

        with db.get_cursor() as cursor:
            for table in tables:
                cursor.execute(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_name = '{table}'
                    )
                """)
                exists = cursor.fetchone()[0]
                status = "[OK]" if exists else "[FAIL]"
                print(f"  {status} Table '{table}': {'exists' if exists else 'NOT FOUND'}")
    except Exception as e:
        print(f"[FAIL] Error checking tables: {e}")
        import traceback
        traceback.print_exc()
    print()

    # Test 3: Check Data in Tables
    print("Test 3: Check Data in Tables")
    try:
        with db.get_cursor() as cursor:
            # Portfolio balances
            cursor.execute("SELECT COUNT(*) FROM portfolio_balances")
            count = cursor.fetchone()[0]
            print(f"  Portfolio balances: {count} records")

            if count > 0:
                cursor.execute("SELECT balance, timestamp FROM portfolio_balances ORDER BY timestamp DESC LIMIT 1")
                latest = cursor.fetchone()
                print(f"    Latest balance: ${latest[0]:,.2f} at {latest[1]}")

            # Options positions
            cursor.execute("SELECT COUNT(*) FROM options_positions")
            count = cursor.fetchone()[0]
            print(f"  Options positions: {count} records")

            # CSP opportunities
            cursor.execute("SELECT COUNT(*) FROM csp_opportunities")
            count = cursor.fetchone()[0]
            print(f"  CSP opportunities: {count} records")

    except Exception as e:
        print(f"[FAIL] Error checking data: {e}")
        import traceback
        traceback.print_exc()
    print()

    # Test 4: Magnus Integration - Portfolio
    print("Test 4: Magnus Integration - Portfolio")
    try:
        magnus = MagnusIntegration()
        portfolio = await magnus.get_portfolio_summary()
        print(f"  Portfolio data: {portfolio}")

        if portfolio.get('balance'):
            print(f"  [OK] Balance: ${portfolio['balance']:,.2f}")
            print(f"     Daily change: ${portfolio.get('daily_change', 0):,.2f} ({portfolio.get('daily_change_pct', 0):.2f}%)")
        else:
            print(f"  [FAIL] {portfolio.get('message', 'No data')}")
    except Exception as e:
        print(f"[FAIL] Error getting portfolio: {e}")
        import traceback
        traceback.print_exc()
    print()

    # Test 5: Magnus Integration - Positions
    print("Test 5: Magnus Integration - Positions")
    try:
        positions = await magnus.get_options_positions(active_only=True)
        print(f"  Found {len(positions)} active positions")

        if positions:
            for i, pos in enumerate(positions[:3], 1):  # Show first 3
                print(f"  Position {i}: {pos.get('ticker')} ${pos.get('strike')} {pos.get('option_type')} exp {pos.get('expiration_date')}")
        else:
            print("  [WARN] No active positions found")
    except Exception as e:
        print(f"[FAIL] Error getting positions: {e}")
        import traceback
        traceback.print_exc()
    print()

    # Test 6: Magnus Integration - Opportunities
    print("Test 6: Magnus Integration - Opportunities")
    try:
        opportunities = await magnus.get_csp_opportunities(limit=5)
        print(f"  Found {len(opportunities)} CSP opportunities")

        if opportunities:
            for i, opp in enumerate(opportunities[:3], 1):
                print(f"  Opportunity {i}: {opp.get('ticker')} ${opp.get('strike_price')} exp {opp.get('expiration_date')}, premium ${opp.get('premium'):.2f}")
        else:
            print("  [WARN] No opportunities found")
    except Exception as e:
        print(f"[FAIL] Error getting opportunities: {e}")
        import traceback
        traceback.print_exc()
    print()

    # Test 7: Magnus Integration - Tasks
    print("Test 7: Magnus Integration - Tasks")
    try:
        tasks = await magnus.get_active_tasks()
        print(f"  Found {len(tasks)} active tasks")

        if tasks:
            for i, task in enumerate(tasks[:3], 1):
                print(f"  Task {i}: {task.get('title')} - {task.get('status')}")
    except Exception as e:
        print(f"[FAIL] Error getting tasks: {e}")
        import traceback
        traceback.print_exc()
    print()

    print("=" * 60)
    print("[OK] Database access tests completed!")
    print("=" * 60)

    return True

if __name__ == "__main__":
    try:
        asyncio.run(test_database_access())
    except KeyboardInterrupt:
        print("\n[WARN] Tests interrupted by user")
    except Exception as e:
        print(f"\n[FAIL] Error running tests: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
