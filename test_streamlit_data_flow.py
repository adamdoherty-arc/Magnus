"""Test what Streamlit page sees"""
from src.espn_live_data import get_espn_client
from src.espn_kalshi_matcher import enrich_games_with_kalshi_odds

print("=" * 80)
print("SIMULATING STREAMLIT PAGE DATA FLOW")
print("=" * 80)

# Step 1: Fetch ESPN data (what line 456 does)
print("\n[1] Fetching ESPN games...")
espn = get_espn_client()
espn_games = espn.get_scoreboard()
print(f"    Fetched {len(espn_games)} games")

# Step 2: Enrich with Kalshi (what line 470 does)
print("\n[2] Enriching with Kalshi odds...")
espn_games = enrich_games_with_kalshi_odds(espn_games)
kalshi_matched = sum(1 for g in espn_games if g.get('kalshi_odds'))
print(f"    Matched {kalshi_matched}/{len(espn_games)} games")

# Step 3: Check what display function sees
print("\n[3] What display_espn_live_games() sees:")
for i, game in enumerate(espn_games[:3], 1):
    print(f"\n    Game {i}: {game['away_team']} @ {game['home_team']}")
    print(f"        away_score: {game.get('away_score')}")
    print(f"        home_score: {game.get('home_score')}")
    print(f"        status: {game.get('status_detail')}")
    print(f"        has kalshi_odds: {'kalshi_odds' in game}")

    if 'kalshi_odds' in game:
        odds = game['kalshi_odds']
        print(f"        kalshi_odds.away_win_price: {odds.get('away_win_price')}")
        print(f"        kalshi_odds.home_win_price: {odds.get('home_win_price')}")

        # Simulate what card displays (lines 916-917)
        away_price = odds.get('away_win_price', 0) * 100
        home_price = odds.get('home_win_price', 0) * 100
        print(f"        DISPLAY: {game['away_team']}: {away_price:.0f}¢")
        print(f"        DISPLAY: {game['home_team']}: {home_price:.0f}¢")

print("\n" + "=" * 80)
print("CONCLUSION")
print("=" * 80)
print(f"""
Backend Status:
- ESPN games fetched: {len(espn_games)} ✓
- Kalshi matches: {kalshi_matched}/{len(espn_games)} ({kalshi_matched/len(espn_games)*100:.0f}%) ✓
- Scores are 0: Expected (games not started) ✓
- Kalshi odds present: {'YES ✓' if kalshi_matched > 0 else 'NO ✗'}

If Streamlit page shows:
- No odds → Cache issue (press 'C' to clear)
- "PASS" recommendations → AI not analyzing odds
- Scores = 0 → Normal (games haven't started)
""")
