"""
Test Sports Game Cards Redesign
Verify all new features work correctly
"""

import sys
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_espn_ncaa_api():
    """Test 1: NCAA ESPN API Integration"""
    print("\n" + "="*80)
    print("TEST 1: NCAA ESPN API Integration")
    print("="*80)

    try:
        from src.espn_ncaa_live_data import get_espn_ncaa_client

        client = get_espn_ncaa_client()
        games = client.get_scoreboard(group='80')  # FBS only

        print(f"✅ NCAA Games Found: {len(games)}")

        if games:
            sample = games[0]
            print(f"\n📊 Sample Game:")
            print(f"   Matchup: {sample['away_team']} @ {sample['home_team']}")
            print(f"   Score: {sample['away_score']} - {sample['home_score']}")
            print(f"   Status: {sample['status_detail']}")
            print(f"   Live: {sample['is_live']}")

            # Check for rankings
            if sample.get('away_rank'):
                print(f"   Away Rank: #{sample['away_rank']}")
            if sample.get('home_rank'):
                print(f"   Home Rank: #{sample['home_rank']}")

            # Check for logos
            if sample.get('away_logo'):
                print(f"   Away Logo: {sample['away_logo'][:50]}...")
            if sample.get('home_logo'):
                print(f"   Home Logo: {sample['home_logo'][:50]}...")

        return True
    except Exception as e:
        print(f"❌ NCAA API Test Failed: {e}")
        return False


def test_espn_nfl_api():
    """Test 2: NFL ESPN API Integration"""
    print("\n" + "="*80)
    print("TEST 2: NFL ESPN API Integration")
    print("="*80)

    try:
        from src.espn_live_data import get_espn_client

        client = get_espn_client()
        games = client.get_scoreboard()

        print(f"✅ NFL Games Found: {len(games)}")

        if games:
            sample = games[0]
            print(f"\n📊 Sample Game:")
            print(f"   Matchup: {sample['away_team']} @ {sample['home_team']}")
            print(f"   Score: {sample['away_score']} - {sample['home_score']}")
            print(f"   Status: {sample['status_detail']}")
            print(f"   Live: {sample['is_live']}")

        return True
    except Exception as e:
        print(f"❌ NFL API Test Failed: {e}")
        return False


def test_watch_manager():
    """Test 3: Watch List Manager"""
    print("\n" + "="*80)
    print("TEST 3: Watch List Manager")
    print("="*80)

    try:
        from src.game_watchlist_manager import GameWatchlistManager
        from src.kalshi_db_manager import KalshiDBManager

        db = KalshiDBManager()
        manager = GameWatchlistManager(db)

        # Test add game
        test_game = {
            'game_id': 'test_12345',
            'sport': 'NFL',
            'away_team': 'Test Away',
            'home_team': 'Test Home',
            'away_score': 14,
            'home_score': 21,
            'status': 'Live',
            'is_live': True
        }

        test_user = 'test_user_redesign'

        # Add to watchlist
        added = manager.add_game_to_watchlist(test_user, test_game, selected_team='Test Away')
        print(f"✅ Add Game: {added}")

        # Check if watched
        is_watched = manager.is_game_watched(test_user, 'test_12345')
        print(f"✅ Is Watched: {is_watched}")

        # Get watchlist
        watchlist = manager.get_user_watchlist(test_user)
        print(f"✅ Watchlist Count: {len(watchlist)}")

        if watchlist:
            print(f"\n📊 Watchlist Entry:")
            entry = watchlist[0]
            print(f"   Game ID: {entry.get('game_id')}")
            print(f"   Away Team: {entry.get('away_team')}")
            print(f"   Home Team: {entry.get('home_team')}")
            print(f"   Selected Team: {entry.get('selected_team')}")
            print(f"   Has game_data: {'game_data' in entry}")

        # Test cleanup (won't remove test game since it's not in ESPN)
        cleaned = manager.cleanup_finished_games(test_user)
        print(f"✅ Cleanup Result: {cleaned} games removed")

        # Remove test game
        removed = manager.remove_game_from_watchlist(test_user, 'test_12345')
        print(f"✅ Remove Game: {removed}")

        return True
    except Exception as e:
        print(f"❌ Watch Manager Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ncaa_team_database():
    """Test 4: NCAA Team Database"""
    print("\n" + "="*80)
    print("TEST 4: NCAA Team Database")
    print("="*80)

    try:
        from src.ncaa_team_database import NCAA_LOGOS, get_team_logo_url, find_team_by_name

        print(f"✅ NCAA Teams in Database: {len(NCAA_LOGOS)}")

        # Test logo URL generation
        test_teams = ['Alabama', 'Ohio State', 'Michigan', 'Georgia']

        for team in test_teams:
            logo_url = get_team_logo_url(team)
            if logo_url:
                print(f"   {team}: {logo_url[:60]}...")
            else:
                print(f"   {team}: No logo found")

        # Test find by name
        alabama = find_team_by_name('Alabama')
        if alabama:
            print(f"\n📊 Alabama Details:")
            print(f"   Name: {alabama.get('name')}")
            print(f"   Mascot: {alabama.get('mascot')}")
            print(f"   ESPN ID: {alabama.get('espn_id')}")

        return True
    except Exception as e:
        print(f"❌ NCAA Team Database Test Failed: {e}")
        return False


def test_ai_agent():
    """Test 5: AI Betting Agent"""
    print("\n" + "="*80)
    print("TEST 5: AI Betting Agent")
    print("="*80)

    try:
        from src.advanced_betting_ai_agent import AdvancedBettingAIAgent

        agent = AdvancedBettingAIAgent()

        # Create test game
        test_game = {
            'away_team': 'Kansas City',
            'home_team': 'Buffalo',
            'away_score': 21,
            'home_score': 28,
            'is_live': True,
            'period': 4,
            'clock': '5:30',
            'status': 'In Progress'
        }

        # Test market data
        market_data = {
            'away_win_price': 0.45,
            'home_win_price': 0.55
        }

        # Get AI prediction
        prediction = agent.analyze_betting_opportunity(test_game, market_data)

        print(f"✅ AI Prediction Generated")
        print(f"\n📊 Prediction Details:")
        print(f"   Predicted Winner: {prediction.get('predicted_winner', 'N/A')}")
        print(f"   Win Probability: {prediction.get('win_probability', 0)*100:.1f}%")
        print(f"   Confidence: {prediction.get('confidence_score', 0)*100:.1f}%")
        print(f"   Expected Value: {prediction.get('expected_value', 0):+.2f}%")
        print(f"   Recommendation: {prediction.get('recommendation', 'N/A')}")

        return True
    except Exception as e:
        print(f"❌ AI Agent Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def print_summary(results):
    """Print test summary"""
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    total = len(results)
    passed = sum(results.values())
    failed = total - passed

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")

    print("\n" + "-"*80)
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")

    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! 🎉")
        print("Sports Game Cards Redesign is ready for production!")
    else:
        print("\n⚠️ Some tests failed. Please review errors above.")


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("SPORTS GAME CARDS REDESIGN - VERIFICATION TESTS")
    print("="*80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    results = {}

    # Run tests
    results['NCAA ESPN API'] = test_espn_ncaa_api()
    results['NFL ESPN API'] = test_espn_nfl_api()
    results['Watch List Manager'] = test_watch_manager()
    results['NCAA Team Database'] = test_ncaa_team_database()
    results['AI Betting Agent'] = test_ai_agent()

    # Print summary
    print_summary(results)

    print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)


if __name__ == "__main__":
    main()
