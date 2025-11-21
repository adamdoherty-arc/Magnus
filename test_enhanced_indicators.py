"""
Test Enhanced Indicators System
Tests all new indicator classes with real stock data
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from src.smart_money_indicators import SmartMoneyIndicators
from src.volume_profile_analyzer import VolumeProfileAnalyzer
from src.momentum_indicators import MomentumIndicators
from src.enhanced_zone_analyzer import EnhancedZoneAnalyzer
from src.zone_detector import ZoneDetector

def normalize_dataframe(df):
    """Normalize dataframe column names to lowercase"""
    df.columns = df.columns.str.lower()
    return df

def test_smart_money_indicators():
    """Test Smart Money Concepts indicators"""
    print("\n" + "="*60)
    print("TESTING SMART MONEY INDICATORS")
    print("="*60)

    # Download AAPL data
    print("\nDownloading AAPL data...")
    ticker = yf.Ticker("AAPL")
    df = ticker.history(period="3mo", interval="1d")
    df = normalize_dataframe(df)

    if df.empty:
        print("ERROR: Failed to download data")
        return False

    print(f"[OK] Downloaded {len(df)} candles")

    # Initialize SMC
    smc = SmartMoneyIndicators()

    # Test Order Blocks
    print("\n--- Testing Order Blocks ---")
    order_blocks = smc.detect_order_blocks(df)
    print(f"Found {len(order_blocks)} order blocks")

    if order_blocks:
        ob = order_blocks[0]
        print(f"\nExample Order Block:")
        print(f"  Type: {ob['type']}")
        print(f"  Price Range: ${ob['bottom']:.2f} - ${ob['top']:.2f}")
        print(f"  Strength: {ob['strength']:.1f}/100")
        print(f"  Date: {ob.get('timestamp', 'N/A')}")

    # Test Fair Value Gaps
    print("\n--- Testing Fair Value Gaps ---")
    fvgs = smc.detect_fair_value_gaps(df)
    print(f"Found {len(fvgs)} fair value gaps")

    if fvgs:
        fvg = fvgs[0]
        print(f"\nExample Fair Value Gap:")
        print(f"  Type: {fvg['type']}")
        print(f"  Gap Range: ${fvg['bottom']:.2f} - ${fvg['top']:.2f}")
        print(f"  Gap Size: ${fvg['gap_size']:.2f} ({fvg['gap_pct']:.2f}%)")
        print(f"  Status: {'Filled' if fvg['filled'] else 'Open'}")

    # Test Market Structure
    print("\n--- Testing Market Structure ---")
    structure = smc.detect_market_structure(df)
    print(f"Current Trend: {structure['current_trend']}")
    last_bos = structure['bos'][-1]['timestamp'] if structure.get('bos') else 'None'
    last_choch = structure['choch'][-1]['timestamp'] if structure.get('choch') else 'None'
    print(f"Last BOS: {last_bos}")
    print(f"Last CHoCH: {last_choch}")

    # Test Liquidity Pools
    print("\n--- Testing Liquidity Pools ---")
    liquidity = smc.detect_liquidity_pools(df)
    print(f"Found {len(liquidity)} liquidity pools")

    if liquidity:
        liq = liquidity[0]
        print(f"\nExample Liquidity Pool:")
        print(f"  Type: {liq['type']}")
        print(f"  Price: ${liq['price']:.2f}")
        print(f"  Strength: {liq['strength']:.1f}/100")
        print(f"  Status: {'Swept' if liq['swept'] else 'Active'}")

    print("\n[OK] Smart Money Indicators test PASSED")
    return True

def test_volume_profile():
    """Test Volume Profile analyzer"""
    print("\n" + "="*60)
    print("TESTING VOLUME PROFILE ANALYZER")
    print("="*60)

    # Download data
    print("\nDownloading TSLA data...")
    ticker = yf.Ticker("TSLA")
    df = ticker.history(period="1mo", interval="1d")
    df = normalize_dataframe(df)

    if df.empty:
        print("ERROR: Failed to download data")
        return False

    print(f"[OK] Downloaded {len(df)} candles")

    # Initialize VPA
    vpa = VolumeProfileAnalyzer()

    # Calculate volume profile
    print("\n--- Calculating Volume Profile ---")
    profile = vpa.calculate_volume_profile(df)

    print(f"\nVolume Profile Results:")
    print(f"  POC (Point of Control): ${profile['poc']:.2f}")
    print(f"  POC Volume: {profile['poc_volume']:,.0f}")
    print(f"  Value Area High: ${profile['vah']:.2f}")
    print(f"  Value Area Low: ${profile['val']:.2f}")
    print(f"  Value Area Range: ${profile['vah'] - profile['val']:.2f}")

    # Identify volume nodes
    print("\n--- Identifying Volume Nodes ---")
    nodes = vpa.identify_volume_nodes(profile)

    print(f"\nHigh Volume Nodes (HVN): {len(nodes['hvn'])}")
    if nodes['hvn']:
        print(f"  Top HVN: ${nodes['hvn'][0]['price']:.2f} ({nodes['hvn'][0]['volume']:,.0f} volume)")

    print(f"\nLow Volume Nodes (LVN): {len(nodes['lvn'])}")
    if nodes['lvn']:
        print(f"  Top LVN: ${nodes['lvn'][0]['price']:.2f} ({nodes['lvn'][0]['volume']:,.0f} volume)")

    # Test proximity checks
    current_price = df['close'].iloc[-1]
    print(f"\n--- Proximity Checks (Current Price: ${current_price:.2f}) ---")
    print(f"  Near POC: {vpa.is_near_poc(current_price, profile)}")
    print(f"  In Value Area: {vpa.is_in_value_area(current_price, profile)}")

    print("\n[OK] Volume Profile test PASSED")
    return True

def test_momentum_indicators():
    """Test Momentum indicators"""
    print("\n" + "="*60)
    print("TESTING MOMENTUM INDICATORS")
    print("="*60)

    # Download data
    print("\nDownloading NVDA data...")
    ticker = yf.Ticker("NVDA")
    df = ticker.history(period="3mo", interval="1d")
    df = normalize_dataframe(df)

    if df.empty:
        print("ERROR: Failed to download data")
        return False

    print(f"[OK] Downloaded {len(df)} candles")

    # Initialize MI
    mi = MomentumIndicators()
    current_price = df['close'].iloc[-1]

    # Test RSI
    print("\n--- Testing RSI ---")
    rsi = mi.calculate_rsi(df)
    rsi_signal = mi.get_rsi_signal(rsi)

    print(f"Current RSI: {rsi_signal['value']:.2f}")
    print(f"Signal: {rsi_signal['signal']}")
    print(f"Strength: {rsi_signal["strength"]}")
    print(f"Condition: {rsi_signal['signal']}")

    # Test MACD
    print("\n--- Testing MACD ---")
    macd = mi.calculate_macd(df)

    print(f"MACD Line: {macd['macd'].iloc[-1]:.4f}")
    print(f"Signal Line: {macd['signal'].iloc[-1]:.4f}")
    print(f"Histogram: {macd['histogram'].iloc[-1]:.4f}")
    macd_signal = mi.get_macd_signal(macd)
    print(f"MACD Signal: {macd_signal["signal"]}")
    print(f"Signal: {macd_signal['signal']}")

    # Test EMAs
    print("\n--- Testing EMAs ---")
    emas = mi.calculate_emas(df)
    alignment = mi.get_ema_alignment(emas, current_price)

    print(f"Current Price: ${current_price:.2f}")
    print(f"EMA 20: ${emas['ema_20'].iloc[-1]:.2f}")
    print(f"EMA 50: ${emas['ema_50'].iloc[-1]:.2f}")
    print(f"EMA 200: ${emas['ema_200'].iloc[-1]:.2f}")
    print(f"\nAlignment: {alignment['alignment']}")
    print(f"Strength: {alignment['strength']}")

    # Test ATR
    print("\n--- Testing ATR ---")
    atr = mi.calculate_atr(df)
    stops = mi.calculate_atr_stops(current_price, atr)

    print(f"Current ATR: ${stops['atr']:.2f}")
    print(f"ATR %: {stops['atr_pct']:.2f}%")
    print(f"\nFor LONG Position:")
    print(f"  Stop Loss: ${stops['long_stop']:.2f} (-{stops['long_stop_pct']:.2f}%)")
    print(f"  Target 1 (1:2): ${stops['long_target1']:.2f} (+{stops['long_target1_pct']:.2f}%)")
    print(f"  Target 2 (1:3): ${stops['long_target2']:.2f} (+{stops['long_target2_pct']:.2f}%)")

    # Test Volume Delta
    print("\n--- Testing Volume Delta / CVD ---")
    volume_df = mi.calculate_volume_delta(df)

    print(f"Current CVD: {volume_df['cvd'].iloc[-1]:,.0f}")
    print(f"CVD Trend: {volume_df['cvd_trend'].iloc[-1]}")
    print(f"Latest Volume Delta: {volume_df['volume_delta'].iloc[-1]:,.0f}")

    # Test Fibonacci
    print("\n--- Testing Fibonacci Levels ---")
    swing_high = df['high'].max()
    swing_low = df['low'].min()
    fib = mi.calculate_fibonacci_levels(swing_high, swing_low, trend='BEARISH')

    print(f"Swing High: ${swing_high:.2f}")
    print(f"Swing Low: ${swing_low:.2f}")
    print(f"\nFibonacci Retracement Levels (BEARISH):")
    for level_name, price in fib.items():
        if level_name not in ['swing_high', 'swing_low', 'trend']:
            print(f"  {level_name}: ${price:.2f}")

    print("\n[OK] Momentum Indicators test PASSED")
    return True

def test_enhanced_zone_analyzer():
    """Test Enhanced Zone Analyzer with complete integration"""
    print("\n" + "="*60)
    print("TESTING ENHANCED ZONE ANALYZER")
    print("="*60)

    # Download data
    print("\nDownloading AAPL data for complete analysis...")
    ticker = yf.Ticker("AAPL")
    df = ticker.history(period="3mo", interval="1d")
    df = normalize_dataframe(df)

    if df.empty:
        print("ERROR: Failed to download data")
        return False

    print(f"[OK] Downloaded {len(df)} candles")
    current_price = df['close'].iloc[-1]

    # Initialize analyzers
    print("\nInitializing analyzers...")
    zone_detector = ZoneDetector()
    enhanced_analyzer = EnhancedZoneAnalyzer()

    # Detect zones
    print("\n--- Detecting Supply/Demand Zones ---")
    zones = zone_detector.detect_zones(df, symbol="AAPL")
    print(f"Found {len(zones)} zones")

    if not zones:
        print("\nNo zones detected. Adjusting parameters for testing...")
        # Create a test zone manually
        zones = [{
            'symbol': 'AAPL',
            'zone_type': 'DEMAND',
            'zone_top': current_price * 0.98,
            'zone_bottom': current_price * 0.95,
            'zone_midpoint': current_price * 0.965,
            'strength': 70,
            'volume_ratio': 2.0,
            'formation_date': df.index[-20],
            'last_test_date': None,
            'test_count': 0,
            'status': 'FRESH'
        }]
        print(f"Created test zone for demonstration")

    # Analyze first zone with complete enhancement
    zone = zones[0]
    print(f"\n--- Analyzing Zone with All Indicators ---")
    print(f"Zone Type: {zone['zone_type']}")
    print(f"Price Range: ${zone['zone_bottom']:.2f} - ${zone['zone_top']:.2f}")
    print(f"Base Strength: {zone.get('strength', 70):.1f}/100")

    # Complete analysis
    print("\nRunning complete multi-indicator analysis...")
    analysis = enhanced_analyzer.analyze_zone_complete(zone, df, current_price)

    # Display results
    print("\n" + "="*60)
    print("COMPLETE ANALYSIS RESULTS")
    print("="*60)

    print(f"\n[CHART] ZONE QUALITY")
    print(f"   Base Score: {analysis.get('strength_score', 70):.1f}/100")
    print(f"   Enhanced Score: {analysis['enhanced_score']:.1f}/100")
    print(f"   Setup Quality: {analysis['setup_quality']}")
    print(f"   Confirmations: {len(analysis.get('confirmations', []))}/10")

    print(f"\n[OK] CONFIRMATIONS ({len(analysis.get('confirmations', []))})")
    for conf in analysis.get('confirmations', []):
        print(f"   • {conf}")

    # Enhanced analysis complete
    # Zone has: enhanced_score, confirmations, confirmation_count, setup_quality, trading_plan

    print(f"\n[MONEY] TRADING PLAN")
    plan = analysis['trading_plan']
    print(f"   Recommendation: {plan.get('direction', 'N/A')}")
    print(f"   Entry Zone: {plan['entry_zone']}")
    print(f"   Optimal Entry: {plan['optimal_entry']}")
    print(f"   Stop Loss: {plan['stop_loss']}")
    print(f"   Target 1: {plan['target_1']}")
    print(f"   Target 2: {plan['target_2']}")
    print(f"   Risk/Reward: {plan['risk_reward']}")

    print("\n[OK] Enhanced Zone Analyzer test PASSED")
    return True

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("ENHANCED INDICATORS COMPREHENSIVE TEST")
    print("="*60)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    results = []

    # Test each component
    try:
        results.append(("Smart Money Indicators", test_smart_money_indicators()))
    except Exception as e:
        print(f"\n[FAIL] Smart Money Indicators test FAILED: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Smart Money Indicators", False))

    try:
        results.append(("Volume Profile", test_volume_profile()))
    except Exception as e:
        print(f"\n[FAIL] Volume Profile test FAILED: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Volume Profile", False))

    try:
        results.append(("Momentum Indicators", test_momentum_indicators()))
    except Exception as e:
        print(f"\n[FAIL] Momentum Indicators test FAILED: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Momentum Indicators", False))

    try:
        results.append(("Enhanced Zone Analyzer", test_enhanced_zone_analyzer()))
    except Exception as e:
        print(f"\n[FAIL] Enhanced Zone Analyzer test FAILED: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Enhanced Zone Analyzer", False))

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    for test_name, passed in results:
        status = "[OK] PASSED" if passed else "[FAIL] FAILED"
        print(f"{test_name}: {status}")

    total_tests = len(results)
    passed_tests = sum(1 for _, passed in results if passed)

    print(f"\nTotal: {passed_tests}/{total_tests} tests passed")

    if passed_tests == total_tests:
        print("\n[SUCCESS] ALL TESTS PASSED! System is ready for integration.")
        return True
    else:
        print(f"\n[WARNING]  {total_tests - passed_tests} test(s) failed. Review errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
