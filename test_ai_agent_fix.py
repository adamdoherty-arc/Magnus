"""Test script to verify AI Options Agent fix"""

from src.ai_options_agent.ai_options_db_manager import AIOptionsDBManager

print("Testing AI Options Agent get_opportunities() method...")
print("=" * 60)

db = AIOptionsDBManager()

# Test 1: Get all opportunities
print("\nTest 1: Get all opportunities (limit 5)")
opps = db.get_opportunities(limit=5)
print(f"Found {len(opps)} opportunities")

if opps:
    for i, opp in enumerate(opps[:3], 1):
        symbol = opp.get('symbol', 'N/A')
        strike = opp.get('strike_price', 0)
        premium = opp.get('premium', 0) / 100
        dte = opp.get('dte', 0)
        annual_return = opp.get('annual_return', 0)
        print(f"  {i}. {symbol} - Strike: ${strike:.2f}, Premium: ${premium:.2f}, DTE: {dte}, Annual: {annual_return:.1f}%")
else:
    print("  No opportunities found")

# Test 2: Get opportunities with specific symbols
print("\nTest 2: Get opportunities for specific symbols")
test_symbols = ['AAPL', 'MSFT', 'NVDA']
opps_filtered = db.get_opportunities(symbols=test_symbols, limit=3)
print(f"Found {len(opps_filtered)} opportunities for {test_symbols}")

if opps_filtered:
    for i, opp in enumerate(opps_filtered, 1):
        symbol = opp.get('symbol', 'N/A')
        strike = opp.get('strike_price', 0)
        premium = opp.get('premium', 0) / 100
        print(f"  {i}. {symbol} - Strike: ${strike:.2f}, Premium: ${premium:.2f}")

print("\n" + "=" * 60)
print("Test complete!")
