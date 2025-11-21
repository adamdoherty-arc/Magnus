"""
Test what the dashboard would actually display for positions
"""
import robin_stocks.robinhood as rh
import os
from dotenv import load_dotenv
import sys

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

load_dotenv()

username = os.getenv('ROBINHOOD_USERNAME')
password = os.getenv('ROBINHOOD_PASSWORD')

print("="*80)
print("DASHBOARD DISPLAY TEST - EXACTLY WHAT YOU'D SEE")
print("="*80)

try:
    # Login
    print("\nLogging in to Robinhood...")
    rh.login(username=username, password=password)
    print("OK - Logged in\n")

    # Get positions
    positions = rh.get_open_option_positions()
    print(f"Found {len(positions)} option positions\n")

    print("="*80)
    print("POSITIONS AS THEY WOULD APPEAR IN DASHBOARD:")
    print("="*80)
    print(f"{'Symbol':^8} | {'Strike':^10} | {'Exp':^10} | {'Contracts':^10} | {'Bought At':^12} | {'Current':^12} | {'P/L':^12}")
    print("-"*80)

    total_pl = 0
    total_premium = 0

    for pos in positions:
        opt_id = pos.get('option_id')
        if not opt_id:
            continue

        # Get option details
        opt_data = rh.get_option_instrument_data_by_id(opt_id)
        symbol = opt_data.get('chain_symbol', 'Unknown')
        strike = float(opt_data.get('strike_price', 0))
        exp_date = opt_data.get('expiration_date', 'Unknown')
        opt_type = opt_data.get('type', 'unknown')

        # Position details
        position_type = pos.get('type', 'unknown')
        quantity = float(pos.get('quantity', 0))
        avg_price = abs(float(pos.get('average_price', 0)))

        # Premium collected/paid
        total_premium_pos = avg_price * quantity * 100  # Convert to dollars

        # Get current market price
        market_data = rh.get_option_market_data_by_id(opt_id)
        if market_data and len(market_data) > 0:
            adjusted_mark = market_data[0].get('adjusted_mark_price')
            mark_price = market_data[0].get('mark_price')
            bid_price = market_data[0].get('bid_price')
            ask_price = market_data[0].get('ask_price')

            # Use adjusted_mark_price (same as dashboard code)
            if adjusted_mark:
                current_price = float(adjusted_mark) * 100  # This is total value per contract
            elif mark_price:
                current_price = float(mark_price) * 100
            elif bid_price and ask_price:
                current_price = (float(bid_price) + float(ask_price)) / 2 * 100
            else:
                current_price = 0
        else:
            current_price = 0

        # Total current value
        current_value = current_price * quantity

        # Calculate P/L
        if position_type == 'short':
            pl = total_premium_pos - current_value
        else:
            pl = current_value - total_premium_pos

        # Per-contract display values
        per_contract_cost = avg_price * 100  # Convert to dollars per contract
        per_contract_current = current_price  # Already per contract

        # Accumulate totals
        total_premium += total_premium_pos
        total_pl += pl

        # Display row
        exp_short = exp_date[5:] if len(exp_date) > 5 else exp_date  # Show MM-DD
        print(f"{symbol:^8} | ${strike:>8.2f} | {exp_short:^10} | {int(quantity):^10} | ${per_contract_cost:>10.2f} | ${per_contract_current:>10.2f} | ${pl:>10.2f}")

    print("-"*80)
    print(f"{'TOTALS':^8} | {' ':^10} | {' ':^10} | {len(positions):^10} | ${total_premium:>10.2f} | {' ':^12} | ${total_pl:>10.2f}")
    print("="*80)

    # Summary
    print(f"\nSummary:")
    print(f"  Total Premium Collected/Paid: ${total_premium:,.2f}")
    print(f"  Total P/L: ${total_pl:,.2f}")
    print(f"  P/L %: {(total_pl/total_premium*100):.1f}%" if total_premium > 0 else "  P/L %: N/A")

    # Check for missing values
    print(f"\nData Quality Check:")
    positions_with_values = 0
    positions_without_values = 0

    for pos in positions:
        opt_id = pos.get('option_id')
        if not opt_id:
            continue

        market_data = rh.get_option_market_data_by_id(opt_id)
        if market_data and len(market_data) > 0:
            adjusted_mark = market_data[0].get('adjusted_mark_price')
            mark_price = market_data[0].get('mark_price')
            bid_price = market_data[0].get('bid_price')
            ask_price = market_data[0].get('ask_price')

            if adjusted_mark or mark_price or (bid_price and ask_price):
                positions_with_values += 1
            else:
                positions_without_values += 1
                opt_data = rh.get_option_instrument_data_by_id(opt_id)
                symbol = opt_data.get('chain_symbol', 'Unknown')
                print(f"  WARNING: {symbol} has NO current price data!")
        else:
            positions_without_values += 1
            opt_data = rh.get_option_instrument_data_by_id(opt_id)
            symbol = opt_data.get('chain_symbol', 'Unknown')
            print(f"  WARNING: {symbol} has NO market data!")

    print(f"\n  Positions with current values: {positions_with_values}/{len(positions)}")
    print(f"  Positions WITHOUT current values: {positions_without_values}/{len(positions)}")

    if positions_without_values == 0:
        print("\n  OK - All positions have current values!")
        print("  If you're not seeing values in the dashboard, the issue is:")
        print("    1. Dashboard display formatting")
        print("    2. Session/login timing")
        print("    3. Browser cache")
        print("\n  Try: Hard refresh the dashboard (Ctrl+Shift+R)")
    else:
        print("\n  WARNING: Some positions are missing current values!")
        print("  This could be due to:")
        print("    1. Options expired/inactive")
        print("    2. Market closed + no after-hours data")
        print("    3. Delisted/halted symbols")

except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()

finally:
    try:
        rh.logout()
    except:
        pass

print("\n" + "="*80)
print("TEST COMPLETE")
print("="*80)
