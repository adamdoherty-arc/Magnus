"""
Debug script to test ESPN data flow in game_cards_visual_page.py
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import logging
logging.basicConfig(level=logging.INFO)

# Test 1: Import the ESPN clients
print("=" * 80)
print("TEST 1: Import ESPN clients")
print("=" * 80)
try:
    from src.espn_live_data import get_espn_client
    from src.espn_ncaa_live_data import get_espn_ncaa_client
    print("✅ ESPN clients imported successfully")
except Exception as e:
    print(f"❌ Failed to import ESPN clients: {e}")
    exit(1)

# Test 2: Fetch NFL data
print("\n" + "=" * 80)
print("TEST 2: Fetch NFL data")
print("=" * 80)
try:
    espn_nfl = get_espn_client()
    nfl_games = espn_nfl.get_scoreboard()
    print(f"✅ NFL games fetched: {len(nfl_games)}")
    if nfl_games:
        game = nfl_games[0]
        print(f"   Sample game: {game['away_team']} ({game['away_score']}) @ {game['home_team']} ({game['home_score']})")
        print(f"   Status: {game['status_detail']}")
        print(f"   Is Live: {game['is_live']}")
    else:
        print("   ⚠️ No NFL games returned")
except Exception as e:
    print(f"❌ Failed to fetch NFL data: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Fetch NCAA data
print("\n" + "=" * 80)
print("TEST 3: Fetch NCAA data")
print("=" * 80)
try:
    espn_ncaa = get_espn_ncaa_client()
    ncaa_games = espn_ncaa.get_scoreboard(group='80')  # FBS
    print(f"✅ NCAA games fetched: {len(ncaa_games)}")
    if ncaa_games:
        game = ncaa_games[0]
        print(f"   Sample game: {game['away_team']} ({game['away_score']}) @ {game['home_team']} ({game['home_score']})")
        print(f"   Status: {game['status_detail']}")
        print(f"   Is Live: {game['is_live']}")
    else:
        print("   ⚠️ No NCAA games returned")
except Exception as e:
    print(f"❌ Failed to fetch NCAA data: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Check if Kalshi enrichment breaks things
print("\n" + "=" * 80)
print("TEST 4: Test Kalshi enrichment")
print("=" * 80)
try:
    from src.espn_kalshi_matcher import enrich_games_with_kalshi_odds
    print("✅ Kalshi enrichment module imported")

    # Try enriching NFL games
    enriched_games = enrich_games_with_kalshi_odds(nfl_games[:3])  # Test with first 3 games
    print(f"✅ Enrichment completed: {len(enriched_games)} games")

    matched = sum(1 for g in enriched_games if g.get('kalshi_odds'))
    print(f"   Kalshi matches: {matched}/{len(enriched_games)}")

except Exception as e:
    print(f"⚠️ Kalshi enrichment failed (this is OK if Kalshi isn't set up): {e}")

# Test 5: Simulate the actual code flow
print("\n" + "=" * 80)
print("TEST 5: Simulate game_cards_visual_page.py flow")
print("=" * 80)

sport_filter = 'NFL'
print(f"Sport filter: {sport_filter}")

# Replicate the exact try-except logic
espn_status = "❌ Failed"
espn_games = []
try:
    if sport_filter == 'CFB':
        espn = get_espn_ncaa_client()
        espn_games = espn.get_scoreboard(group='80')
    else:
        espn = get_espn_client()
        espn_games = espn.get_scoreboard()
    espn_status = f"✅ {len(espn_games)} games fetched"
    print(f"ESPN Status: {espn_status}")
except Exception as e:
    print(f"❌ ESPN fetch failed: {e}")
    espn_games = []
    # THIS IS THE PROBLEM - the code returns here
    print("🚨 CRITICAL: Code would return here (line 437)")
    print("   This prevents any games from being displayed!")

# Check if we got games
if espn_games:
    print(f"\n✅ SUCCESS: {len(espn_games)} games ready to display")
    print(f"   First game has scores: away={espn_games[0].get('away_score')}, home={espn_games[0].get('home_score')}")
else:
    print(f"\n❌ FAILURE: No games to display")

# Test 6: Check display logic
print("\n" + "=" * 80)
print("TEST 6: Check display conditions")
print("=" * 80)

if not espn_games:
    print("❌ Display would show: 'No live games available from ESPN at this time'")
else:
    print(f"✅ Display would proceed with {len(espn_games)} games")

    # Check filtering
    live_games = [g for g in espn_games if g.get('is_live', False)]
    upcoming_games = [g for g in espn_games if not g.get('is_live', False) and not g.get('is_completed', False)]
    final_games = [g for g in espn_games if g.get('is_completed', False)]

    print(f"\nGame breakdown:")
    print(f"  Live games: {len(live_games)}")
    print(f"  Upcoming games: {len(upcoming_games)}")
    print(f"  Final games: {len(final_games)}")

print("\n" + "=" * 80)
print("DIAGNOSIS COMPLETE")
print("=" * 80)
