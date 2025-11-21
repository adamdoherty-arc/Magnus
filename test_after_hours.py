"""Test After-Hours Price from Robinhood API"""
import robin_stocks.robinhood as rh
from dotenv import load_dotenv
import os
import json

load_dotenv()

# Login
username = os.getenv('ROBINHOOD_USERNAME')
password = os.getenv('ROBINHOOD_PASSWORD')

print("Logging into Robinhood...")
login = rh.login(username, password)

# Test symbols from user's positions
test_symbols = ['BMNR', 'UPST', 'CIFR', 'HIMS']

print("\n" + "="*80)
print("CHECKING AFTER-HOURS PRICES")
print("="*80)

for symbol in test_symbols:
    print(f"\n{symbol}:")
    
    # Get quotes (includes extended hours)
    quotes = rh.get_quotes(symbol)
    if quotes and len(quotes) > 0:
        quote = quotes[0]
        
        print(f"  Regular price fields:")
        print(f"    - last_trade_price: {quote.get('last_trade_price')}")
        print(f"    - adjusted_previous_close: {quote.get('adjusted_previous_close')}")
        print(f"    - bid_price: {quote.get('bid_price')}")
        print(f"    - ask_price: {quote.get('ask_price')}")
        
        print(f"  Extended hours fields:")
        print(f"    - last_extended_hours_trade_price: {quote.get('last_extended_hours_trade_price')}")
        print(f"    - has_traded_today: {quote.get('has_traded')}")
        
        print(f"  All available keys:")
        for key in sorted(quote.keys()):
            if 'extended' in key.lower() or 'after' in key.lower() or 'hour' in key.lower():
                print(f"    - {key}: {quote.get(key)}")

    # Also check stock quote
    print(f"\n  Checking rh.get_stock_quote_by_symbol:")
    stock_quote = rh.get_stock_quote_by_symbol(symbol)
    if stock_quote:
        print(f"    last_trade_price: {stock_quote.get('last_trade_price')}")
        print(f"    last_extended_hours_trade_price: {stock_quote.get('last_extended_hours_trade_price')}")

rh.logout()
print("\n" + "="*80)
print("Done")
