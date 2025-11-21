"""Test HIMS After-Hours Price"""

import robin_stocks.robinhood as rh
import os
from dotenv import load_dotenv
import json

load_dotenv()

print("=" * 80)
print("HIMS AFTER-HOURS PRICE TEST")
print("=" * 80)

# Login
username = os.getenv('ROBINHOOD_USERNAME')
password = os.getenv('ROBINHOOD_PASSWORD')

print("\n1. Logging in...")
rh.login(username=username, password=password)
print("   [OK] Logged in")

symbol = 'HIMS'

print(f"\n2. Testing {symbol}:")
print("=" * 80)

# Get regular price
print("\n   A. Regular price (get_latest_price):")
stock_quote = rh.get_latest_price(symbol)
regular_price = float(stock_quote[0]) if stock_quote else None
print(f"      Result: ${regular_price:.2f}" if regular_price else "      Result: N/A")

# Get full quote data
print("\n   B. Full quote data (get_quotes):")
quote_data = rh.get_quotes(symbol)

if quote_data and len(quote_data) > 0:
    quote = quote_data[0]

    print("\n      ALL FIELDS IN QUOTE:")
    print("      " + "-" * 70)
    for key, value in sorted(quote.items()):
        print(f"      {key:40s}: {value}")

    print("\n      PRICE-RELATED FIELDS:")
    print("      " + "-" * 70)

    # Extract all price fields
    price_fields = {
        'ask_price': quote.get('ask_price'),
        'bid_price': quote.get('bid_price'),
        'last_trade_price': quote.get('last_trade_price'),
        'last_extended_hours_trade_price': quote.get('last_extended_hours_trade_price'),
        'last_non_reg_trade_price': quote.get('last_non_reg_trade_price'),
        'adjusted_previous_close': quote.get('adjusted_previous_close'),
        'previous_close': quote.get('previous_close'),
    }

    for field, value in price_fields.items():
        if value:
            try:
                float_val = float(value)
                print(f"      {field:40s}: ${float_val:.2f}")
            except:
                print(f"      {field:40s}: {value}")
        else:
            print(f"      {field:40s}: None")

    # Check trading status
    print("\n      TRADING STATUS:")
    print("      " + "-" * 70)
    print(f"      trading_halted: {quote.get('trading_halted')}")
    print(f"      has_traded: {quote.get('has_traded')}")

    # Determine the best after-hours price
    print("\n3. AFTER-HOURS PRICE LOGIC:")
    print("=" * 80)

    extended_price = quote.get('last_extended_hours_trade_price')
    non_reg_price = quote.get('last_non_reg_trade_price')

    print(f"\n   Option 1: last_extended_hours_trade_price = {extended_price}")
    print(f"   Option 2: last_non_reg_trade_price = {non_reg_price}")
    print(f"   Regular price: ${regular_price:.2f}" if regular_price else "   Regular price: N/A")

    # Show what we should display
    after_hours = None
    if extended_price:
        after_hours = float(extended_price)
    elif non_reg_price:
        after_hours = float(non_reg_price)

    if after_hours:
        print(f"\n   RECOMMENDATION: Always show after-hours price")
        print(f"   After-Hours Display: ${after_hours:.2f}")
        if regular_price:
            diff = after_hours - regular_price
            pct = (diff / regular_price * 100) if regular_price > 0 else 0
            print(f"   Difference: ${diff:+.2f} ({pct:+.2f}%)")
    else:
        print(f"\n   No after-hours price available")

else:
    print("   [ERROR] No quote data returned")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
