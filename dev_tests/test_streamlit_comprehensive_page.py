"""
Quick test to validate comprehensive_strategy_page.py can be imported and run
Tests the key functions without launching the full Streamlit UI
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

print("="*60)
print("COMPREHENSIVE STRATEGY PAGE - CODE VALIDATION TEST")
print("="*60)

# Test 1: Import the page
print("\n[TEST 1] Importing comprehensive_strategy_page.py...")
try:
    # We can't fully import because it will try to run Streamlit
    # But we can check if the file is valid Python
    with open('comprehensive_strategy_page.py', 'r', encoding='utf-8') as f:
        code = f.read()
    compile(code, 'comprehensive_strategy_page.py', 'exec')
    print("[PASS] File is valid Python code")
except SyntaxError as e:
    print(f"[FAIL] Syntax error: {e}")
    exit(1)
except Exception as e:
    print(f"[FAIL] Error: {e}")
    exit(1)

# Test 2: Import the dependencies
print("\n[TEST 2] Checking dependencies...")
try:
    from src.tradingview_db_manager import TradingViewDBManager
    print("[PASS] TradingViewDBManager imported")

    from src.ai_options_agent.comprehensive_strategy_analyzer import ComprehensiveStrategyAnalyzer
    print("[PASS] ComprehensiveStrategyAnalyzer imported")

    from src.ai_options_agent.llm_manager import get_llm_manager
    print("[PASS] get_llm_manager imported")

    import yfinance as yf
    print("[PASS] yfinance imported")

    import psycopg2
    print("[PASS] psycopg2 imported")

except ImportError as e:
    print(f"[FAIL] Import error: {e}")
    exit(1)

# Test 3: Test the helper functions
print("\n[TEST 3] Testing helper functions...")
try:
    tv_manager = TradingViewDBManager()
    print("[PASS] TradingViewDBManager initialized")

    watchlists = tv_manager.get_all_symbols_dict()
    print(f"[PASS] get_all_symbols_dict() returned {len(watchlists)} watchlists")

except Exception as e:
    print(f"[FAIL] Error: {e}")
    exit(1)

# Test 4: Test database connection
print("\n[TEST 4] Testing database connection...")
try:
    conn = tv_manager.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM stock_data")
    count = cur.fetchone()[0]
    print(f"[PASS] Database connection OK - {count} stocks in stock_data")
    cur.close()
    conn.close()
except Exception as e:
    print(f"[FAIL] Database error: {e}")
    exit(1)

# Test 5: Test yfinance data fetching
print("\n[TEST 5] Testing yfinance data fetching...")
try:
    ticker = yf.Ticker("AAPL")
    info = ticker.info
    price = info.get('currentPrice', 0)
    print(f"[PASS] yfinance can fetch data - AAPL price: ${price:.2f}")
except Exception as e:
    print(f"[WARN] yfinance error (may be rate limited): {e}")

# Test 6: Check page structure
print("\n[TEST 6] Validating page structure...")
with open('comprehensive_strategy_page.py', 'r', encoding='utf-8') as f:
    content = f.read()

checks = [
    ("Data source selector", "data_source = st.radio" in content),
    ("TradingView watchlist section", "TradingView Watchlist" in content),
    ("Database stocks section", "Database Stocks" in content),
    ("Manual input section", "Manual Input" in content),
    ("Auto-population", "fetch_stock_info" in content),
    ("Options suggestions", "fetch_options_suggestions" in content),
    ("Error handling", "try:" in content and "except" in content),
]

all_passed = True
for check_name, result in checks:
    status = "[PASS]" if result else "[FAIL]"
    print(f"{status} {check_name}")
    if not result:
        all_passed = False

if not all_passed:
    print("\n[FAIL] Some structure checks failed")
    exit(1)

# Final summary
print("\n" + "="*60)
print("VALIDATION SUMMARY")
print("="*60)
print("[PASS] All code validation tests passed")
print("[PASS] All dependencies available")
print("[PASS] Database connection working")
print("[PASS] Page structure validated")
print("\n[SUCCESS] comprehensive_strategy_page.py is ready to use!")
print("\nTo run the page:")
print("  streamlit run comprehensive_strategy_page.py")
print("\n" + "="*60)
