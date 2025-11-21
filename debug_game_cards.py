"""
Debug script to test game cards logic without Streamlit
"""

from game_cards_visual_page import fetch_games_grouped, calculate_expected_value
from src.kalshi_db_manager import KalshiDBManager
from src.espn_live_data import get_espn_client

def test_game_cards():
    print("="*80)
    print("DEBUGGING GAME CARDS PAGE")
    print("="*80)

    db = KalshiDBManager()

    # Test 1: Fetch games
    print("\n[TEST 1] Fetching NFL games with min_confidence=70...")
    games = fetch_games_grouped(db, min_confidence=70, sport='NFL')
    print(f"[OK] Returned {len(games)} games")

    if not games:
        print("[ERROR] No games returned!")

        # Try with lower confidence
        print("\n[TEST 1b] Trying with min_confidence=0...")
        games = fetch_games_grouped(db, min_confidence=0, sport='NFL')
        print(f"[OK] Returned {len(games)} games")

    # Test 2: Show first few games
    if games:
        print(f"\n[TEST 2] First 5 games:")
        for i, game in enumerate(games[:5], 1):
            print(f"\n  Game {i}:")
            print(f"    Teams: {game['team1']} vs {game['team2']}")
            print(f"    Time: {game['game_time_str']}")
            print(f"    Markets: {len(game['markets'])}")
            print(f"    Best Confidence: {game['best_confidence']:.1f}%")
            print(f"    Best Edge: {game['best_edge']:.1f}%")

    # Test 3: Calculate EV for games
    if games:
        print(f"\n[TEST 3] Calculating Expected Value...")
        for game in games[:3]:
            ev = calculate_expected_value(game)
            game['expected_value'] = ev
            print(f"  {game['team1']} vs {game['team2']}: EV = {ev:+.1f}%")

    # Test 4: ESPN integration
    print(f"\n[TEST 4] Testing ESPN integration...")
    try:
        espn = get_espn_client()
        live_scores = espn.get_scoreboard()
        print(f"[OK] ESPN API returned {len(live_scores)} games")

        if live_scores:
            print(f"\n  First 3 ESPN games:")
            for game in live_scores[:3]:
                print(f"    {game['away_abbr']} @ {game['home_abbr']}: {game['away_score']}-{game['home_score']}")
    except Exception as e:
        print(f"[ERROR] ESPN API error: {e}")

    # Test 5: Check data completeness
    if games:
        print(f"\n[TEST 5] Data completeness check:")
        game = games[0]
        required_fields = ['team1', 'team2', 'game_time', 'game_time_str', 'markets', 'best_confidence', 'best_edge']
        for field in required_fields:
            has_field = field in game
            value = game.get(field, 'MISSING')
            status = '[OK]' if has_field else '[MISSING]'
            print(f"    {field}: {status} = {value}")

    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Total games: {len(games)}")
    print(f"Games with markets: {sum(1 for g in games if g['markets'])}")
    print(f"Games with high confidence (>80%): {sum(1 for g in games if g['best_confidence'] > 80)}")
    status = '[OK] ALL TESTS PASSED' if games else '[FAILED] No games found'
    print(f"\nStatus: {status}")
    print("="*80)

if __name__ == "__main__":
    test_game_cards()
