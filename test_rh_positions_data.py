"""
Test Robinhood positions data to diagnose missing current values
"""
import robin_stocks.robinhood as rh
import os
from dotenv import load_dotenv
import json
import sys

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

load_dotenv()

username = os.getenv('ROBINHOOD_USERNAME')
password = os.getenv('ROBINHOOD_PASSWORD')

if not username or not password:
    print("ERROR: Robinhood credentials not found")
    exit(1)

print("="*70)
print("TESTING ROBINHOOD POSITIONS DATA")
print("="*70)

try:
    # Login
    print("\n[1] Logging in...")
    rh.login(username=username, password=password)
    print("✅ Login successful")

    # Get open option positions
    print("\n[2] Fetching open option positions...")
    positions = rh.get_open_option_positions()
    print(f"✅ Found {len(positions)} positions")

    if not positions:
        print("No positions to analyze")
        exit(0)

    # Analyze first position in detail
    print("\n[3] Analyzing first position...")
    print("="*70)

    pos = positions[0]
    print(f"\nRaw position data (first 500 chars):")
    print(json.dumps(pos, indent=2)[:500])

    # Get option details
    opt_id = pos.get('option_id')
    print(f"\n[4] Option ID: {opt_id}")

    if opt_id:
        # Get option instrument data
        print("\n[5] Fetching option instrument data...")
        opt_data = rh.get_option_instrument_data_by_id(opt_id)

        symbol = opt_data.get('chain_symbol', 'Unknown')
        strike = float(opt_data.get('strike_price', 0))
        exp_date = opt_data.get('expiration_date', 'Unknown')
        opt_type = opt_data.get('type', 'unknown')

        print(f"Symbol: {symbol}")
        print(f"Strike: ${strike}")
        print(f"Expiration: {exp_date}")
        print(f"Type: {opt_type}")

        # Get market data - THIS IS THE KEY
        print("\n[6] Fetching market data...")
        market_data = rh.get_option_market_data_by_id(opt_id)

        print(f"\nMarket data returned: {type(market_data)}")
        print(f"Market data length: {len(market_data) if market_data else 0}")

        if market_data and len(market_data) > 0:
            print("\n✅ Market data available:")
            print(json.dumps(market_data[0], indent=2))

            # Extract key pricing fields
            adjusted_mark = market_data[0].get('adjusted_mark_price')
            mark_price = market_data[0].get('mark_price')
            bid_price = market_data[0].get('bid_price')
            ask_price = market_data[0].get('ask_price')
            last_trade_price = market_data[0].get('last_trade_price')

            print(f"\n📊 Pricing Fields:")
            print(f"  adjusted_mark_price: {adjusted_mark}")
            print(f"  mark_price: {mark_price}")
            print(f"  bid_price: {bid_price}")
            print(f"  ask_price: {ask_price}")
            print(f"  last_trade_price: {last_trade_price}")

            # Calculate current value (as dashboard does)
            quantity = float(pos.get('quantity', 0))
            if adjusted_mark:
                current_price = float(adjusted_mark) * 100
                current_value = current_price * quantity
                print(f"\n💰 Calculated Values:")
                print(f"  Quantity: {quantity}")
                print(f"  Current Price (per contract): ${current_price:.2f}")
                print(f"  Current Value (total): ${current_value:.2f}")
            else:
                print(f"\n❌ adjusted_mark_price is None/0 - this is the problem!")

                # Try alternative pricing
                if mark_price:
                    print(f"\n💡 Can use mark_price instead: {mark_price}")
                    alt_price = float(mark_price) * 100
                    alt_value = alt_price * quantity
                    print(f"  Alternative Current Price: ${alt_price:.2f}")
                    print(f"  Alternative Current Value: ${alt_value:.2f}")

                if bid_price and ask_price:
                    print(f"\n💡 Can use mid-point of bid/ask:")
                    mid_price = (float(bid_price) + float(ask_price)) / 2 * 100
                    mid_value = mid_price * quantity
                    print(f"  Mid-point Price: ${mid_price:.2f}")
                    print(f"  Mid-point Value: ${mid_value:.2f}")
        else:
            print("\n❌ NO MARKET DATA RETURNED!")
            print("This is why current values are showing as $0.00")

    # Test all positions summary
    print("\n"+"="*70)
    print("[7] Testing all positions...")
    print("="*70)

    positions_with_data = 0
    positions_without_data = 0

    for i, pos in enumerate(positions, 1):
        opt_id = pos.get('option_id')
        if not opt_id:
            continue

        opt_data = rh.get_option_instrument_data_by_id(opt_id)
        symbol = opt_data.get('chain_symbol', '?')

        market_data = rh.get_option_market_data_by_id(opt_id)

        has_price = False
        if market_data and len(market_data) > 0:
            adjusted_mark = market_data[0].get('adjusted_mark_price')
            mark_price = market_data[0].get('mark_price')
            bid_price = market_data[0].get('bid_price')
            ask_price = market_data[0].get('ask_price')

            if adjusted_mark or mark_price or (bid_price and ask_price):
                has_price = True
                positions_with_data += 1
                print(f"  [{i}] {symbol:6} ✅ Has pricing data")
            else:
                positions_without_data += 1
                print(f"  [{i}] {symbol:6} ❌ NO pricing data")
        else:
            positions_without_data += 1
            print(f"  [{i}] {symbol:6} ❌ NO market data returned")

    print("\n"+"="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Total positions: {len(positions)}")
    print(f"With pricing data: {positions_with_data}")
    print(f"Without pricing data: {positions_without_data}")

    if positions_without_data > 0:
        print(f"\n⚠️  {positions_without_data} positions have missing current values!")
        print("This is causing the issue you reported.")

        print("\n💡 Possible Solutions:")
        print("1. Use mark_price as fallback if adjusted_mark_price is None")
        print("2. Use bid/ask mid-point as fallback")
        print("3. Check if market is closed (after-hours may have limited data)")
        print("4. Verify these options have active market makers")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

finally:
    try:
        rh.logout()
    except:
        pass

print("\n"+"="*70)
print("TEST COMPLETE")
print("="*70)
