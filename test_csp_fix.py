"""Test CSP opportunities finder with fixes"""
import sys
sys.path.insert(0, 'c:\\Code\\WheelStrategy')

from src.csp_opportunities_finder import CSPOpportunitiesFinder

finder = CSPOpportunitiesFinder()

# Test with actual position symbols
symbols = ['BMNR', 'UPST', 'CIFR', 'HIMS']

print("=" * 80)
print("TESTING FIXED CSP OPPORTUNITIES FINDER")
print("=" * 80)
print(f"\nSearching for opportunities for: {', '.join(symbols)}")
print(f"DTE range: {finder.dte_range}")
print(f"Delta range: {finder.delta_range}")

opportunities = finder.find_opportunities_for_symbols(symbols)

if not opportunities.empty:
    print(f"\nSUCCESS! Found {len(opportunities)} opportunities")
    print("\n" + "=" * 80)
    print("OPPORTUNITIES FOUND:")
    print("=" * 80)
    print(opportunities[['Symbol', 'Stock Price', 'Strike', 'DTE', 'Premium', 'Delta', 'Monthly %']].to_string(index=False))

    print("\n" + "=" * 80)
    print("SUMMARY METRICS:")
    print("=" * 80)
    metrics = finder.get_summary_metrics(opportunities)
    for key, value in metrics.items():
        print(f"{key}: {value:.2f}" if isinstance(value, float) else f"{key}: {value}")
else:
    print("\nFAILED! No opportunities found")
    print("This means the fix didn't work or data is missing")
