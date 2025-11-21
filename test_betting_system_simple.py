"""Simple test for AVA Betting Recommendations System (Windows-safe)"""

from ava_betting_recommendations_page import (
    analyze_all_games,
    analyze_betting_opportunity,
    rank_betting_opportunities,
    calculate_expected_value,
    calculate_kelly_criterion
)

print("=" * 80)
print("TESTING AVA BETTING RECOMMENDATIONS SYSTEM")
print("=" * 80)

# Test 1: Fetch games
print("\n1. Testing game fetching...")
games = analyze_all_games()
nfl_count = sum(1 for g in games if g.get('sport') == 'NFL')
ncaa_count = sum(1 for g in games if g.get('sport') == 'NCAA')
nba_count = sum(1 for g in games if g.get('sport') == 'NBA')

print(f"   [OK] Fetched {len(games)} total games")
print(f"   - NFL: {nfl_count}")
print(f"   - NCAA: {ncaa_count}")
print(f"   - NBA: {nba_count}")

# Count games with Kalshi odds
with_odds = sum(1 for g in games if g.get('kalshi_odds'))
print(f"   - Games with Kalshi odds: {with_odds}")

# Test 2: Analyze opportunities
print("\n2. Analyzing betting opportunities...")
opportunities = []
for game in games:
    if game.get('kalshi_odds'):  # Only analyze games with odds
        analysis = analyze_betting_opportunity(game)
        if analysis:
            opportunities.append(analysis)

print(f"   [OK] Found {len(opportunities)} betting opportunities")

# Test 3: Rank opportunities
if opportunities:
    print("\n3. Ranking opportunities...")
    ranked = rank_betting_opportunities(opportunities)

    print(f"   [OK] Ranked {len(ranked)} opportunities")

    # Display top 5
    print("\n   TOP 5 PICKS:")
    for idx, opp in enumerate(ranked[:5], 1):
        print(f"\n   #{idx} - {opp['sport']}: {opp['away_team']} @ {opp['home_team']}")
        print(f"       Pick: {opp['favorite']} ({opp['favorite_prob']:.0%})")
        print(f"       Odds: {opp['favorite_odds']:.0f} cents")
        print(f"       EV: ${opp['expected_value']:.2f}")
        print(f"       Kelly: {opp['kelly_pct']:.1%}")
        print(f"       Score: {opp['combined_score']:.1f}")
        print(f"       Confidence: {opp['confidence']}")

# Test 4: Test EV and Kelly calculations
print("\n4. Testing EV and Kelly calculations...")
test_cases = [
    (0.70, 70, "High confidence, fair odds"),
    (0.85, 85, "Very high confidence"),
    (0.60, 55, "Medium confidence, +EV"),
]

for win_prob, odds, description in test_cases:
    ev = calculate_expected_value(win_prob, odds)
    kelly = calculate_kelly_criterion(win_prob, odds)
    print(f"   {description}:")
    print(f"     Win Prob: {win_prob:.0%}, Odds: {odds} cents")
    print(f"     EV: ${ev:.2f}, Kelly: {kelly:.1%}")

print("\n" + "=" * 80)
print("ALL TESTS COMPLETED SUCCESSFULLY")
print("=" * 80)
print("\nNext Steps:")
print("   1. Open dashboard at http://localhost:8507")
print("   2. Click 'AVA Betting Picks' in sidebar")
print("   3. Review AI-ranked betting opportunities")
print("=" * 80)
