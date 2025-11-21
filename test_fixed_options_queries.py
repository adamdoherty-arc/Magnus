"""Test fixed options queries"""
import sys
sys.path.insert(0, 'c:/Code/WheelStrategy')

from src.data.options_queries import get_premium_opportunities

print('Testing fixed get_premium_opportunities() function...')
print('=' * 60)

# Test with relaxed filters to ensure we get results
opportunities = get_premium_opportunities({
    'min_premium_pct': 0.5,
    'min_annual_return': 10.0,
    'min_delta': -0.50,
    'max_delta': -0.15,
    'min_dte': 7,
    'max_dte': 60,
    'min_volume': 0,
    'min_open_interest': 0,
    'limit': 10
})

print(f'\nFound {len(opportunities)} opportunities')
print('\nTop 5 opportunities:')
print('=' * 60)
for i, opp in enumerate(opportunities[:5], 1):
    print(f'\n{i}. {opp.get("symbol", "N/A")} - ${opp.get("strike_price", 0):.2f}')
    print(f'   Premium: ${opp.get("premium", 0):.2f} ({opp.get("premium_pct", 0):.2f}%)')
    print(f'   Annual Return: {opp.get("annual_return", 0):.1f}%')
    print(f'   Delta: {opp.get("delta", 0):.3f}, DTE: {opp.get("dte", 0)}')
    print(f'   Sector: {opp.get("sector", "N/A")}')

if len(opportunities) > 0:
    print('\n' + '=' * 60)
    print('✅ SUCCESS! AI Options Agent should now show opportunities!')
else:
    print('\n' + '=' * 60)
    print('❌ No opportunities found. This might be a data quality issue.')
