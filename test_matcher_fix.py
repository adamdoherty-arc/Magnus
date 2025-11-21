"""
Test the fixed ESPN Kalshi matcher with Dallas vs Las Vegas game
"""
import sys
from src.espn_kalshi_matcher import ESPNKalshiMatcher

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Create test ESPN game
test_game = {
    'away_team': 'Dallas Cowboys',
    'home_team': 'Las Vegas Raiders',
    'game_time': '2025-11-17 16:25:00'
}

print("Testing ESPN Kalshi Matcher Fix")
print("=" * 60)
print(f"\nTest Game:")
print(f"  Away: {test_game['away_team']}")
print(f"  Home: {test_game['home_team']}")
print(f"  Time: {test_game['game_time']}")
print("\nExpected Results (from Kalshi):")
print("  Dallas Cowboys: 65¢")
print("  Las Vegas Raiders: 35¢")
print("-" * 60)

# Test matcher
matcher = ESPNKalshiMatcher()
result = matcher.match_game_to_kalshi(test_game)

if result:
    print("\nMatcher Results:")
    print(f"  Ticker: {result['ticker']}")
    print(f"  Market Title: {result['market_title']}")
    print(f"\n  Away (Dallas) Win Price: {result['away_win_price']:.2f}¢")
    print(f"  Home (Las Vegas) Win Price: {result['home_win_price']:.2f}¢")

    # Verify correctness
    print("\n" + "=" * 60)
    if abs(result['away_win_price'] - 0.65) < 0.03:  # Allow 3¢ variance
        print("✅ SUCCESS! Dallas odds are correct (~65¢)")
    else:
        print(f"❌ FAILED! Dallas odds are {result['away_win_price']:.2f}¢, expected ~0.65¢")

    if abs(result['home_win_price'] - 0.35) < 0.03:  # Allow 3¢ variance
        print("✅ SUCCESS! Las Vegas odds are correct (~35¢)")
    else:
        print(f"❌ FAILED! Las Vegas odds are {result['home_win_price']:.2f}¢, expected ~0.35¢")
else:
    print("\n❌ FAILED! No Kalshi market found for this game")
