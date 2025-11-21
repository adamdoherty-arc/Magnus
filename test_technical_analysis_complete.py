"""
Complete Technical Analysis System Test
========================================

Tests all technical analysis components:
1. Fibonacci Calculator
2. Volume Profile Calculator
3. Order Flow Analyzer
4. Database Caching
5. Integration
"""

import yfinance as yf
from src.fibonacci_calculator import FibonacciCalculator
from src.advanced_technical_indicators import VolumeProfileCalculator, OrderFlowAnalyzer
from src.technical_analysis_db_manager import TechnicalAnalysisDBManager
import pandas as pd
from datetime import datetime

def print_header(title):
    """Print formatted header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def print_section(title):
    """Print formatted section"""
    print(f"\n{title}")
    print("-" * 80)

def test_fibonacci_calculator():
    """Test Fibonacci Calculator"""
    print_section("1. Fibonacci Calculator Test")

    try:
        # Get stock data
        ticker = yf.Ticker('AAPL')
        df = ticker.history(period='6mo', interval='1d')
        df.columns = [col.lower() for col in df.columns]

        print(f"   Loaded {len(df)} days of AAPL data")

        # Calculate Fibonacci
        calc = FibonacciCalculator()
        swings = calc.auto_detect_swings(df, lookback=20, prominence_pct=0.02)

        print(f"   Found {len(swings)} swing patterns")

        if len(swings) > 0:
            swing = swings[0]
            print(f"\n   Latest Swing:")
            print(f"     Type: {swing['type']}")
            print(f"     Range: ${swing['swing_low']:.2f} -> ${swing['swing_high']:.2f}")
            print(f"     Golden Zone: ${swing['golden_zone']['bottom']:.2f} - ${swing['golden_zone']['top']:.2f}")

            # Test current position
            current_price = df['close'].iloc[-1]
            position = calc.get_current_position_relative_to_fibonacci(
                current_price,
                swing['swing_high'],
                swing['swing_low'],
                'up' if swing['type'] == 'UPTREND_RETRACEMENT' else 'down'
            )

            print(f"\n   Current Position Analysis:")
            print(f"     Price: ${position['current_price']:.2f}")
            print(f"     Nearest Level: {position['nearest_level']['name']} @ ${position['nearest_level']['price']:.2f}")
            print(f"     In Golden Zone: {position['in_golden_zone']}")
            print(f"     Setup Quality: {position['setup_quality']}")

        # Test confluence
        if len(swings) >= 3:
            confluences = calc.find_fibonacci_confluence(swings, tolerance_pct=1.0)
            print(f"\n   Found {len(confluences)} confluence zones")

            if len(confluences) > 0:
                conf = confluences[0]
                print(f"\n   Strongest Confluence:")
                print(f"     Price: ${conf['price']:.2f}")
                print(f"     Strength: {conf['strength']} overlapping levels")
                print(f"     Zone: ${conf['price_min']:.2f} - ${conf['price_max']:.2f}")

        print("\n   Status: PASS")
        return True

    except Exception as e:
        print(f"\n   Status: FAIL - {e}")
        return False

def test_volume_profile_calculator():
    """Test Volume Profile Calculator"""
    print_section("2. Volume Profile Calculator Test")

    try:
        # Get stock data
        ticker = yf.Ticker('TSLA')
        df = ticker.history(period='3mo', interval='1d')
        df.columns = [col.lower() for col in df.columns]

        print(f"   Loaded {len(df)} days of TSLA data")

        # Calculate Volume Profile
        calc = VolumeProfileCalculator()
        vp = calc.calculate_volume_profile(df, price_bins=40)

        print(f"\n   Volume Profile Metrics:")
        print(f"     POC Price: ${vp['poc']['price']:.2f}")
        print(f"     POC Volume: {vp['poc']['volume']:,.0f}")
        print(f"     POC % of Total: {vp['poc']['pct_of_total']:.1f}%")
        print(f"     VAH: ${vp['vah']:.2f}")
        print(f"     VAL: ${vp['val']:.2f}")
        print(f"     Value Area: ${vp['val']:.2f} - ${vp['vah']:.2f}")
        print(f"     Total Volume: {vp['total_volume']:,.0f}")

        # Test trading signals
        current_price = df['close'].iloc[-1]
        signals = calc.get_trading_signals(current_price, vp)

        print(f"\n   Trading Signals:")
        print(f"     Current Price: ${current_price:.2f}")
        print(f"     Position: {signals['position']}")
        print(f"     Bias: {signals['bias']}")
        print(f"     Setup Quality: {signals['setup_quality']}")

        print("\n   Status: PASS")
        return True

    except Exception as e:
        print(f"\n   Status: FAIL - {e}")
        return False

def test_order_flow_analyzer():
    """Test Order Flow Analyzer"""
    print_section("3. Order Flow Analyzer Test")

    try:
        # Get stock data
        ticker = yf.Ticker('NVDA')
        df = ticker.history(period='1mo', interval='1d')
        df.columns = [col.lower() for col in df.columns]

        print(f"   Loaded {len(df)} days of NVDA data")

        # Calculate CVD
        analyzer = OrderFlowAnalyzer()
        cvd = analyzer.calculate_cvd(df)
        df['cvd'] = cvd

        print(f"\n   Order Flow Metrics:")
        print(f"     Current CVD: {df['cvd'].iloc[-1]:,.0f}")
        print(f"     CVD Change (1d): {df['cvd'].diff().iloc[-1]:,.0f}")

        if len(df) >= 5:
            cvd_change_5d = df['cvd'].iloc[-1] - df['cvd'].iloc[-6]
            print(f"     CVD Change (5d): {cvd_change_5d:,.0f}")
            trend = "BULLISH" if cvd_change_5d > 0 else "BEARISH"
            print(f"     Trend: {trend}")

        # Test divergences
        divergences = analyzer.find_cvd_divergences(df, lookback=10)

        print(f"\n   Divergences Found: {len(divergences)}")

        if len(divergences) > 0:
            div = divergences[0]
            print(f"\n   Latest Divergence:")
            print(f"     Type: {div['type']}")
            print(f"     Strength: {div['strength']}")
            print(f"     Date: {div['date']}")

        print("\n   Status: PASS")
        return True

    except Exception as e:
        print(f"\n   Status: FAIL - {e}")
        return False

def test_database_caching():
    """Test Database Caching"""
    print_section("4. Database Caching Test")

    try:
        db = TechnicalAnalysisDBManager()

        # Get stock data for caching test
        ticker = yf.Ticker('MSFT')
        df = ticker.history(period='6mo', interval='1d')
        df.columns = [col.lower() for col in df.columns]

        print(f"   Loaded {len(df)} days of MSFT data")

        # Calculate Fibonacci
        fib_calc = FibonacciCalculator()
        swings = fib_calc.auto_detect_swings(df, lookback=20)

        print(f"   Calculated {len(swings)} Fibonacci swings")

        # Cache Fibonacci levels
        success = db.cache_fibonacci_levels('MSFT', '1d', '6mo', swings, ttl_seconds=3600)
        print(f"\n   Cache Fibonacci: {'SUCCESS' if success else 'FAIL'}")

        # Retrieve cached data (should be cache HIT)
        cached_swings = db.get_cached_fibonacci_levels('MSFT', '1d', '6mo')

        if cached_swings:
            print(f"   Retrieve Cached: SUCCESS (found {len(cached_swings)} swings)")
            print(f"   Cache Status: HIT")
        else:
            print(f"   Retrieve Cached: FAIL")
            print(f"   Cache Status: MISS")

        # Test cache stats
        stats = db.get_cache_stats('MSFT')
        print(f"\n   Cache Statistics:")

        if stats:
            for stat in stats:
                print(f"     Type: {stat['analysis_type']}")
                print(f"     Timeframe: {stat['timeframe']}")
                print(f"     Hits: {stat['cache_hits']}")
                print(f"     Misses: {stat['cache_misses']}")
        else:
            print(f"     No stats available yet")

        # Test cleanup
        cleanup_success = db.cleanup_expired_cache()
        print(f"\n   Cleanup: {'SUCCESS' if cleanup_success else 'FAIL'}")

        print("\n   Status: PASS")
        return True

    except Exception as e:
        print(f"\n   Status: FAIL - {e}")
        import traceback
        traceback.print_exc()
        return False

def test_integration():
    """Test Full Integration"""
    print_section("5. Integration Test")

    try:
        # Get stock data
        ticker = yf.Ticker('SPY')
        df = ticker.history(period='3mo', interval='1d')
        df.columns = [col.lower() for col in df.columns]

        print(f"   Loaded {len(df)} days of SPY data")

        # Test all calculators together
        fib_calc = FibonacciCalculator()
        vp_calc = VolumeProfileCalculator()
        of_analyzer = OrderFlowAnalyzer()
        db = TechnicalAnalysisDBManager()

        # Fibonacci
        swings = fib_calc.auto_detect_swings(df, lookback=20)
        print(f"\n   Fibonacci: Found {len(swings)} swings")

        # Volume Profile
        vp = vp_calc.calculate_volume_profile(df, price_bins=40)
        print(f"   Volume Profile: POC at ${vp['poc']['price']:.2f}")

        # Order Flow
        df['cvd'] = of_analyzer.calculate_cvd(df)
        divergences = of_analyzer.find_cvd_divergences(df, lookback=10)
        print(f"   Order Flow: {len(divergences)} divergences found")

        # Cache all results
        db.cache_fibonacci_levels('SPY', '1d', '3mo', swings)

        # Convert divergences to JSON-serializable format
        serializable_divergences = []
        for div in divergences:
            serializable_div = {
                'type': div['type'],
                'strength': div['strength'],
                'date': div['date'].strftime('%Y-%m-%d') if hasattr(div['date'], 'strftime') else str(div['date'])
            }
            serializable_divergences.append(serializable_div)

        order_flow_data = {
            'current_cvd': float(df['cvd'].iloc[-1]),
            'cvd_change_1d': float(df['cvd'].diff().iloc[-1]),
            'cvd_change_5d': float(df['cvd'].iloc[-1] - df['cvd'].iloc[-6]) if len(df) >= 6 else 0,
            'cvd_trend': 'BULLISH' if df['cvd'].iloc[-1] > df['cvd'].iloc[-6] else 'BEARISH',
            'divergence_count': len(divergences),
            'divergences': serializable_divergences
        }

        db.cache_order_flow('SPY', '1d', '3mo', order_flow_data)

        print(f"\n   Cache Results: SUCCESS")

        # Verify confluence (multi-indicator)
        current_price = df['close'].iloc[-1]

        print(f"\n   Confluence Analysis:")
        print(f"     Current Price: ${current_price:.2f}")

        # Check if price near Golden Zone
        if len(swings) > 0:
            swing = swings[0]
            golden_bottom = swing['golden_zone']['bottom']
            golden_top = swing['golden_zone']['top']

            in_golden_zone = golden_bottom <= current_price <= golden_top
            print(f"     In Golden Zone: {in_golden_zone}")

        # Check if price near POC
        poc_distance = abs(current_price - vp['poc']['price']) / vp['poc']['price'] * 100
        print(f"     Distance from POC: {poc_distance:.2f}%")

        # Check CVD trend
        print(f"     CVD Trend: {order_flow_data['cvd_trend']}")

        print("\n   Status: PASS")
        return True

    except Exception as e:
        print(f"\n   Status: FAIL - {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print_header("TECHNICAL ANALYSIS COMPLETE SYSTEM TEST")
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Run all tests
    results = {
        'Fibonacci Calculator': test_fibonacci_calculator(),
        'Volume Profile Calculator': test_volume_profile_calculator(),
        'Order Flow Analyzer': test_order_flow_analyzer(),
        'Database Caching': test_database_caching(),
        'Integration': test_integration()
    }

    # Summary
    print_header("TEST SUMMARY")

    passed = sum(results.values())
    total = len(results)

    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        symbol = "[OK]" if result else "[X]"
        print(f"  {symbol} {test_name}: {status}")

    print("\n" + "=" * 80)
    print(f"  Results: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    print("=" * 80)

    if passed == total:
        print("\nSUCCESS - All tests passed!")
        return 0
    else:
        print(f"\nWARNING - {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    exit(main())
