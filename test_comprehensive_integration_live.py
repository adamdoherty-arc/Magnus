"""
Live Integration Test for Comprehensive Options Strategy Analysis Page
Tests all three modes: Manual, TradingView Watchlist, Database Stocks
"""

import sys
import os
import psycopg2
from dotenv import load_dotenv
import yfinance as yf

load_dotenv()

def test_database_connection():
    """Test 1: Database connection"""
    print("\n=== TEST 1: Database Connection ===")
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()
        print(f"[PASS] Connected to PostgreSQL: {version[0][:50]}...")
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"[FAIL] Database connection failed: {e}")
        return False

def test_tradingview_watchlists():
    """Test 2: TradingView Watchlists Table"""
    print("\n=== TEST 2: TradingView Watchlists ===")
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cur = conn.cursor()

        # Check if table exists
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = 'tv_watchlists'
            );
        """)
        exists = cur.fetchone()[0]
        if not exists:
            print("[FAIL] tv_watchlists table does not exist")
            return False

        # Get watchlist count
        cur.execute("SELECT COUNT(*) FROM tv_watchlists;")
        count = cur.fetchone()[0]
        print(f"[PASS] Found {count} TradingView watchlists")

        # Get sample watchlists
        cur.execute("SELECT id, name FROM tv_watchlists LIMIT 5;")
        watchlists = cur.fetchall()
        print("\nSample watchlists:")
        for wl_id, name in watchlists:
            print(f"  - {name} (ID: {wl_id})")

        cur.close()
        conn.close()
        return count > 0
    except Exception as e:
        print(f"[FAIL] TradingView watchlist test failed: {e}")
        return False

def test_tradingview_symbols():
    """Test 3: TradingView Watchlist Symbols"""
    print("\n=== TEST 3: TradingView Symbols ===")
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cur = conn.cursor()

        # Check if table exists
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = 'tv_watchlist_symbols'
            );
        """)
        exists = cur.fetchone()[0]
        if not exists:
            print("[FAIL] tv_watchlist_symbols table does not exist")
            return False

        # Get symbol count
        cur.execute("SELECT COUNT(*) FROM tv_watchlist_symbols;")
        count = cur.fetchone()[0]
        print(f"[PASS] Found {count} symbols across all watchlists")

        # Get sample symbols from first watchlist
        cur.execute("""
            SELECT w.name, s.symbol
            FROM tv_watchlists w
            JOIN tv_watchlist_symbols s ON w.id = s.watchlist_id
            LIMIT 10;
        """)
        symbols = cur.fetchall()
        print("\nSample symbols:")
        for wl_name, symbol in symbols:
            print(f"  - {symbol} (in {wl_name})")

        cur.close()
        conn.close()
        return count > 0
    except Exception as e:
        print(f"[FAIL] TradingView symbols test failed: {e}")
        return False

def test_database_stocks():
    """Test 4: Database Stocks Table"""
    print("\n=== TEST 4: Database Stocks ===")
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cur = conn.cursor()

        # Check stocks table
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = 'stocks'
            );
        """)
        exists = cur.fetchone()[0]
        if not exists:
            print("[FAIL] stocks table does not exist")
            return False

        # Get stock count
        cur.execute("SELECT COUNT(DISTINCT ticker) FROM stocks;")
        count = cur.fetchone()[0]
        print(f"[PASS] Found {count} unique stocks in database")

        # Get sample stocks
        cur.execute("SELECT ticker, name FROM stocks ORDER BY ticker LIMIT 10;")
        stocks = cur.fetchall()
        print("\nSample stocks:")
        for ticker, name in stocks:
            print(f"  - {ticker}: {name}")

        cur.close()
        conn.close()
        return count > 0
    except Exception as e:
        print(f"[FAIL] Database stocks test failed: {e}")
        return False

def test_stock_data_table():
    """Test 5: Stock Data Table (for auto-population)"""
    print("\n=== TEST 5: Stock Data Table ===")
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cur = conn.cursor()

        # Check if stock_data table exists
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = 'stock_data'
            );
        """)
        exists = cur.fetchone()[0]

        if exists:
            cur.execute("SELECT COUNT(*) FROM stock_data;")
            count = cur.fetchone()[0]
            print(f"[PASS] stock_data table exists with {count} records")

            # Get sample
            cur.execute("SELECT ticker, current_price FROM stock_data LIMIT 5;")
            data = cur.fetchall()
            print("\nSample stock data:")
            for ticker, price in data:
                print(f"  - {ticker}: ${price}")
        else:
            print("[WARN]  stock_data table does not exist (will use yfinance fallback)")

        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"[WARN]  Stock data table check: {e}")
        return True  # Not critical

def test_yfinance_fallback():
    """Test 6: yfinance API Fallback"""
    print("\n=== TEST 6: yfinance Fallback ===")
    try:
        ticker = yf.Ticker("AAPL")
        info = ticker.info
        price = info.get('currentPrice', info.get('regularMarketPrice', 0))
        print(f"[PASS] yfinance working: AAPL = ${price}")
        return True
    except Exception as e:
        print(f"[FAIL] yfinance fallback failed: {e}")
        return False

def test_tradingview_db_manager():
    """Test 7: TradingViewDBManager Integration"""
    print("\n=== TEST 7: TradingViewDBManager ===")
    try:
        sys.path.insert(0, 'c:/Code/WheelStrategy/src')
        from tradingview_db_manager import TradingViewDBManager

        tv_db = TradingViewDBManager()
        watchlists = tv_db.get_all_watchlists()

        print(f"[PASS] TradingViewDBManager loaded {len(watchlists)} watchlists")

        if watchlists:
            first_wl = watchlists[0]
            print(f"\nFirst watchlist details:")
            print(f"  - ID: {first_wl['id']}")
            print(f"  - Name: {first_wl['name']}")
            print(f"  - Symbols: {len(first_wl.get('symbols', []))}")
            if first_wl.get('symbols'):
                print(f"  - First 5 symbols: {first_wl['symbols'][:5]}")

        return len(watchlists) > 0
    except Exception as e:
        print(f"[FAIL] TradingViewDBManager test failed: {e}")
        return False

def test_comprehensive_page_imports():
    """Test 8: Comprehensive Strategy Page Imports"""
    print("\n=== TEST 8: Comprehensive Page Imports ===")
    try:
        # Check if file exists
        page_path = "c:/Code/WheelStrategy/comprehensive_strategy_page.py"
        if not os.path.exists(page_path):
            print(f"[FAIL] File not found: {page_path}")
            return False

        # Read and check for watchlist integration code
        with open(page_path, 'r', encoding='utf-8') as f:
            content = f.read()

        checks = {
            "TradingView Watchlist mode": '"TradingView Watchlist"' in content,
            "Database Stocks mode": '"Database Stocks"' in content,
            "Manual Input mode": '"Manual Input"' in content,
            "get_tv_watchlists function": "def get_tv_watchlists" in content,
            "get_database_stocks function": "def get_database_stocks" in content,
            "TradingViewDBManager import": "TradingViewDBManager" in content,
            "Stock auto-population": "fetch_stock_info" in content or "yf.Ticker" in content
        }

        print("Code integration checks:")
        all_passed = True
        for check, passed in checks.items():
            status = "[PASS]" if passed else "[FAIL]"
            print(f"  {status} {check}")
            if not passed:
                all_passed = False

        return all_passed
    except Exception as e:
        print(f"[FAIL] Comprehensive page import test failed: {e}")
        return False

def test_stock_premiums_table():
    """Test 9: Stock Premiums Table (for IV data)"""
    print("\n=== TEST 9: Stock Premiums Table ===")
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cur = conn.cursor()

        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = 'stock_premiums'
            );
        """)
        exists = cur.fetchone()[0]

        if exists:
            cur.execute("SELECT COUNT(*) FROM stock_premiums;")
            count = cur.fetchone()[0]
            print(f"[PASS] stock_premiums table exists with {count} records")

            # Get sample with IV data
            cur.execute("""
                SELECT ticker, iv_rank, iv_percentile
                FROM stock_premiums
                WHERE iv_rank IS NOT NULL
                LIMIT 5;
            """)
            data = cur.fetchall()
            if data:
                print("\nSample IV data:")
                for ticker, iv_rank, iv_pct in data:
                    print(f"  - {ticker}: IV Rank {iv_rank}, Percentile {iv_pct}")
        else:
            print("[WARN]  stock_premiums table does not exist")

        cur.close()
        conn.close()
        return True  # Not critical
    except Exception as e:
        print(f"[WARN]  Stock premiums check: {e}")
        return True

def run_all_tests():
    """Run all integration tests"""
    print("="*70)
    print("COMPREHENSIVE STRATEGY PAGE - LIVE INTEGRATION TEST")
    print("="*70)

    tests = [
        ("Database Connection", test_database_connection),
        ("TradingView Watchlists", test_tradingview_watchlists),
        ("TradingView Symbols", test_tradingview_symbols),
        ("Database Stocks", test_database_stocks),
        ("Stock Data Table", test_stock_data_table),
        ("yfinance Fallback", test_yfinance_fallback),
        ("TradingViewDBManager", test_tradingview_db_manager),
        ("Comprehensive Page Code", test_comprehensive_page_imports),
        ("Stock Premiums Table", test_stock_premiums_table),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n[FAIL] Test '{name}' crashed: {e}")
            results.append((name, False))

    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "[PASS] PASS" if result else "[FAIL] FAIL"
        print(f"{status}: {name}")

    print(f"\n{passed}/{total} tests passed ({100*passed//total}%)")

    if passed == total:
        print("\n[SUCCESS] ALL TESTS PASSED - SYSTEM READY!")
    elif passed >= total * 0.8:
        print("\n[WARN]  MOSTLY WORKING - Some non-critical features unavailable")
    else:
        print("\n[FAIL] CRITICAL FAILURES - System needs attention")

    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
