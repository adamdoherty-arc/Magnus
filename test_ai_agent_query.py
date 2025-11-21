#!/usr/bin/env python3
"""
Test to verify the working centralized query vs the broken AI agent query
"""

from src.data.options_queries import get_premium_opportunities
from src.ai_options_agent.ai_options_db_manager import AIOptionsDBManager

print("=" * 80)
print("ROOT CAUSE ANALYSIS: AI Options Agent Query Bug")
print("=" * 80)

# Test 1: Working centralized query
print("\n1. Testing WORKING centralized query (src.data.options_queries):")
print("-" * 80)
opps = get_premium_opportunities({
    'min_premium_pct': 1.0,
    'min_annual_return': 15.0,
    'min_delta': -0.45,
    'max_delta': -0.15,
    'min_dte': 20,
    'max_dte': 40,
    'limit': 100
})
print(f"✓ Found {len(opps)} opportunities")
if opps:
    for opp in opps[:3]:
        print(f"  {opp['symbol']} ${opp['strike_price']}: {opp['annual_return']:.1f}% annual, {opp['premium_pct']:.1f}% premium")

# Test 2: Broken AI agent query
print("\n2. Testing BROKEN AI agent query (AIOptionsDBManager):")
print("-" * 80)
db_manager = AIOptionsDBManager()
ai_opps = db_manager.get_opportunities(
    symbols=None,
    dte_range=(20, 40),
    delta_range=(-0.45, -0.15),
    min_premium=100,
    limit=100
)
print(f"✗ Found {len(ai_opps)} opportunities")
if ai_opps:
    for opp in ai_opps[:3]:
        print(f"  {opp['symbol']} ${opp['strike_price']}: {opp['annual_return']:.1f}% annual")

print("\n" + "=" * 80)
print("DIAGNOSIS:")
print("=" * 80)
print("The AIOptionsDBManager.get_opportunities() query uses:")
print("  WHERE sp.strike_type IN ('30_delta', '30_dte')")
print("")
print("But the database schema actually has strike_type values:")
print("  - '30_delta' ✓")
print("  - '30_dte' ✓")
print("  - '5%_OTM' ✓")
print("")
print("The query EXCLUDES '5%_OTM' strikes, which contain most opportunities!")
print("=" * 80)
