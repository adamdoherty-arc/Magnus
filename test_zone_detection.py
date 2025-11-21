"""
Quick test to verify supply/demand zones are now detecting
"""
import yfinance as yf
import sys
sys.path.insert(0, 'src')

from src.zone_detector import ZoneDetector

print("\n" + "="*80)
print("SUPPLY/DEMAND ZONE DETECTION TEST")
print("="*80)

# Test on a few popular stocks
test_symbols = ['AAPL', 'MSFT', 'TSLA', 'SPY', 'NVDA']

# Use shorter lookback since yfinance may have gaps
detector = ZoneDetector(lookback_periods=50)

print(f"\nTesting zone detection on {len(test_symbols)} symbols...")
print("-" * 80)

total_zones = 0

for symbol in test_symbols:
    print(f"\n{symbol}:")

    # Fetch data
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period='3mo', interval='1d')

        if len(df) == 0:
            print(f"  No data available")
            continue

        # Normalize column names to lowercase
        df.columns = [col.lower() for col in df.columns]

        # Detect zones
        zones = detector.detect_zones(df, symbol)

        if len(zones) == 0:
            print(f"  No zones detected")
        else:
            total_zones += len(zones)
            demand_zones = [z for z in zones if z['type'] == 'DEMAND']
            supply_zones = [z for z in zones if z['type'] == 'SUPPLY']

            print(f"  ✅ Detected {len(zones)} zones:")
            print(f"     - {len(demand_zones)} DEMAND zones")
            print(f"     - {len(supply_zones)} SUPPLY zones")

            # Show details of first zone
            if zones:
                z = zones[0]
                print(f"     Example: {z['type']} zone at ${z['zone_bottom']:.2f}-${z['zone_top']:.2f}")
                print(f"              Strength: {z['strength']}/100, Status: {z['status']}")

    except Exception as e:
        print(f"  Error: {e}")

print("\n" + "="*80)
print(f"TOTAL: {total_zones} zones detected across {len(test_symbols)} symbols")
print("="*80)

if total_zones == 0:
    print("\n⚠️  WARNING: No zones detected!")
    print("   The filters may still be too strict or data unavailable")
else:
    print(f"\n✅ SUCCESS: Zone detection is working!")
    print(f"   Average: {total_zones/len(test_symbols):.1f} zones per symbol")

print()
