"""Test After-Hours Price Retrieval"""

import robin_stocks.robinhood as rh
import os
from dotenv import load_dotenv
import json

load_dotenv()

print("=" * 80)
print("AFTER-HOURS PRICE TEST")
print("=" * 80)

# Login
username = os.getenv('ROBINHOOD_USERNAME')
password = os.getenv('ROBINHOOD_PASSWORD')

print("\n1. Logging in...")
try:
    rh.login(username=username, password=password)
    print("   [OK] Logged in successfully")
except Exception as e:
    print(f"   [ERROR] Login failed: {e}")
    exit(1)

# Get a test symbol from positions
print("\n2. Getting test symbols from positions...")
try:
    positions = rh.get_open_option_positions()
    if positions:
        # Get unique symbols
        symbols = set()
        for pos in positions[:3]:  # Test first 3
            opt_id = pos.get('option_id')
            if opt_id:
                opt_data = rh.get_option_instrument_data_by_id(opt_id)
                symbol = opt_data.get('chain_symbol')
                if symbol:
                    symbols.add(symbol)

        symbols = list(symbols)[:3]  # Limit to 3 symbols
        print(f"   Test symbols: {symbols}")
    else:
        # Fallback to common symbols
        symbols = ['AAPL', 'TSLA', 'SPY']
        print(f"   Using fallback symbols: {symbols}")
except Exception as e:
    print(f"   Error getting positions: {e}")
    symbols = ['AAPL', 'TSLA', 'SPY']
    print(f"   Using fallback symbols: {symbols}")

# Test each symbol
print("\n3. Testing after-hours price retrieval...")
for symbol in symbols:
    print(f"\n   Testing {symbol}:")
    print("   " + "-" * 70)

    # Get regular price
    try:
        stock_quote = rh.get_latest_price(symbol)
        regular_price = float(stock_quote[0]) if stock_quote else None
        print(f"   Regular price: ${regular_price:.2f}" if regular_price else "   Regular price: N/A")
    except Exception as e:
        print(f"   Error getting regular price: {e}")
        regular_price = None

    # Get quotes data
    try:
        quote_data = rh.get_quotes(symbol)
        if quote_data and len(quote_data) > 0:
            quote = quote_data[0]

            print(f"\n   Available quote fields:")
            for key, value in quote.items():
                if 'price' in key.lower() or 'extended' in key.lower():
                    print(f"      {key}: {value}")

            # Test different fields
            extended_price = quote.get('last_extended_hours_trade_price')
            after_hours_price = quote.get('after_hours_price')
            last_trade_price = quote.get('last_trade_price')

            print(f"\n   Extracted values:")
            print(f"      last_extended_hours_trade_price: {extended_price}")
            print(f"      after_hours_price: {after_hours_price}")
            print(f"      last_trade_price: {last_trade_price}")

            # Determine what to use
            if extended_price:
                try:
                    ext_float = float(extended_price)
                    if regular_price and abs(ext_float - regular_price) > 0.01:
                        print(f"\n   [OK] After-hours price: ${ext_float:.2f} (diff: ${ext_float - regular_price:+.2f})")
                    else:
                        print(f"\n   [-] No significant after-hours movement")
                except:
                    print(f"\n   [ERROR] Could not convert extended price: {extended_price}")
            else:
                print(f"\n   [-] No extended hours data available")
        else:
            print(f"   [ERROR] No quote data returned")
    except Exception as e:
        print(f"   [ERROR] Error getting quotes: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
