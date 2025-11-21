"""
End-to-End Test for Game Cards Page
Tests ESPN data fetching, filtering, and display logic
"""

import sys
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_espn_data_fetching():
    """Test ESPN API data fetching"""
    print("\n" + "="*80)
    print("TEST 1: ESPN Data Fetching")
    print("="*80)
    
    try:
        from src.espn_live_data import get_espn_client
        from src.espn_ncaa_live_data import get_espn_ncaa_client
        
        # Test NFL
        nfl_client = get_espn_client()
        nfl_games = nfl_client.get_scoreboard()
        print(f"[OK] NFL games fetched: {len(nfl_games)}")
        
        if nfl_games:
            sample_nfl = nfl_games[0]
            print(f"[OK] Sample NFL game: {sample_nfl.get('away_team')} @ {sample_nfl.get('home_team')}")
            print(f"[OK] NFL game keys: {list(sample_nfl.keys())[:10]}...")
            print(f"[OK] NFL status field: {sample_nfl.get('status')}")
            print(f"[OK] NFL is_live: {sample_nfl.get('is_live')}")
            print(f"[OK] NFL game_time type: {type(sample_nfl.get('game_time'))}")
        
        # Test NCAA
        ncaa_client = get_espn_ncaa_client()
        ncaa_games = ncaa_client.get_scoreboard(group='80')
        print(f"\n[OK] NCAA games fetched: {len(ncaa_games)}")
        
        if ncaa_games:
            sample_ncaa = ncaa_games[0]
            print(f"[OK] Sample NCAA game: {sample_ncaa.get('away_team')} @ {sample_ncaa.get('home_team')}")
            print(f"[OK] NCAA game keys: {list(sample_ncaa.keys())[:10]}...")
            print(f"[OK] NCAA status field: {sample_ncaa.get('status')}")
            print(f"[OK] NCAA is_live: {sample_ncaa.get('is_live')}")
            print(f"[OK] NCAA game_time type: {type(sample_ncaa.get('game_time'))}")
        
        return True, nfl_games, ncaa_games
        
    except Exception as e:
        print(f"[ERROR] ESPN data fetching failed: {e}")
        import traceback
        traceback.print_exc()
        return False, [], []


def test_filtering_logic(games):
    """Test the filtering logic used in display_espn_live_games"""
    print("\n" + "="*80)
    print("TEST 2: Filtering Logic")
    print("="*80)
    
    if not games:
        print("[SKIP] No games to filter")
        return True
    
    sample_game = games[0]
    
    # Test status filtering
    print("\n[TEST] Status filtering:")
    print(f"  - is_live: {sample_game.get('is_live')}")
    print(f"  - status: {sample_game.get('status')}")
    print(f"  - status_detail: {sample_game.get('status_detail')}")
    
    # Test what the current code would filter
    live_games = [g for g in games if g.get('is_live', False)]
    print(f"  - Live games (is_live=True): {len(live_games)}")
    
    # Check status_type field (this might be the issue)
    status_type_games = [g for g in games if g.get('status_type')]
    print(f"  - Games with 'status_type' field: {len(status_type_games)}")
    
    # Test date filtering
    print("\n[TEST] Date filtering:")
    game_time = sample_game.get('game_time')
    print(f"  - game_time value: {game_time}")
    print(f"  - game_time type: {type(game_time)}")
    
    if game_time:
        if isinstance(game_time, datetime):
            print(f"  - game_time is datetime: {game_time.date()}")
        else:
            print(f"  - game_time is string: {game_time}")
            try:
                parsed = datetime.strptime(str(game_time)[:10], '%Y-%m-%d').date()
                print(f"  - Parsed date: {parsed}")
            except Exception as e:
                print(f"  - [ERROR] Cannot parse date: {e}")
    
    return True


def test_display_function_signature():
    """Test that display_espn_live_games function exists and has correct signature"""
    print("\n" + "="*80)
    print("TEST 3: Display Function")
    print("="*80)
    
    try:
        import game_cards_visual_page
        func = getattr(game_cards_visual_page, 'display_espn_live_games', None)
        
        if func:
            print("[OK] display_espn_live_games function exists")
            import inspect
            sig = inspect.signature(func)
            print(f"[OK] Function signature: {sig}")
            return True
        else:
            print("[ERROR] display_espn_live_games function not found")
            return False
            
    except Exception as e:
        print(f"[ERROR] Cannot import display function: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_data_source_logic():
    """Test the data source selection logic"""
    print("\n" + "="*80)
    print("TEST 4: Data Source Selection Logic")
    print("="*80)
    
    try:
        # Simulate the logic from show_sport_games
        from src.espn_ncaa_live_data import get_espn_ncaa_client
        
        espn = get_espn_ncaa_client()
        espn_games = espn.get_scoreboard(group='80')
        
        print(f"[OK] ESPN games fetched: {len(espn_games)}")
        
        # Simulate kalshi_game_markets check (would be empty)
        kalshi_game_markets = []
        player_props_count = 0  # Simulate
        
        if kalshi_game_markets:
            data_source = "kalshi_games"
            print("[OK] Data source: kalshi_games")
        elif player_props_count > 0:
            data_source = "espn_live"
            print("[OK] Data source: espn_live (with player props)")
        else:
            data_source = "espn_live"
            print("[OK] Data source: espn_live (ESPN only)")
        
        print(f"[OK] Would call display_espn_live_games with {len(espn_games)} games")
        
        if len(espn_games) == 0:
            print("[WARNING] espn_games is empty - this would trigger 'No live games' message")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Data source logic test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all end-to-end tests"""
    print("\n" + "="*80)
    print("GAME CARDS END-TO-END TEST")
    print("="*80)
    
    results = []
    
    # Test 1: ESPN Data Fetching
    success, nfl_games, ncaa_games = test_espn_data_fetching()
    results.append(("ESPN Data Fetching", success))
    
    # Test 2: Filtering Logic
    if ncaa_games:
        success = test_filtering_logic(ncaa_games)
        results.append(("Filtering Logic", success))
    
    # Test 3: Display Function
    success = test_display_function_signature()
    results.append(("Display Function", success))
    
    # Test 4: Data Source Logic
    success = test_data_source_logic()
    results.append(("Data Source Logic", success))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    for test_name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {test_name}")
    
    all_passed = all(result[1] for result in results)
    print("\n" + "="*80)
    if all_passed:
        print("[OK] All tests passed!")
    else:
        print("[ERROR] Some tests failed - see details above")
    print("="*80)
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

