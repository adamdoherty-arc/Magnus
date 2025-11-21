"""
Test Adaptive Polling Logic
Tests the smart interval logic without requiring full database setup
"""
import sys

# Fix Windows console encoding
sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

print("="*70)
print("ADAPTIVE POLLING LOGIC TEST")
print("="*70)
print()

def get_smart_interval(game: dict) -> int:
    """
    Determine optimal polling interval based on game state
    (Copy of the logic from NFLRealtimeSync)
    """
    game_status = game.get('game_status', 'unknown')

    # Completed games - check infrequently
    if game_status in ['final', 'completed']:
        return 300

    # Scheduled games - moderate frequency
    if game_status == 'scheduled':
        return 60

    # Live games - adaptive based on game situation
    if game.get('is_live', False):
        quarter = game.get('quarter', 1)
        home_score = game.get('home_score', 0)
        away_score = game.get('away_score', 0)
        score_diff = abs(home_score - away_score)

        # Halftime - less frequent
        if quarter == 2 and game.get('time_remaining', '').startswith('Halftime'):
            return 15

        # 4th quarter close game - most frequent
        if quarter == 4 and score_diff <= 7:
            return 5

        # Regular live game - moderate frequency
        return 10

    # Default fallback
    return 15


# Test scenarios
test_scenarios = [
    {
        "name": "Scheduled Game",
        "game": {
            "game_id": "test_1",
            "game_status": "scheduled",
            "away_team": "BUF",
            "home_team": "KC",
            "quarter": 1,
            "home_score": 0,
            "away_score": 0
        },
        "expected_interval": 60,
        "description": "Not started yet"
    },
    {
        "name": "Live Q1",
        "game": {
            "game_id": "test_2",
            "game_status": "in_progress",
            "is_live": True,
            "away_team": "DAL",
            "home_team": "PHI",
            "quarter": 1,
            "home_score": 7,
            "away_score": 3
        },
        "expected_interval": 10,
        "description": "Regular live game"
    },
    {
        "name": "Halftime",
        "game": {
            "game_id": "test_3",
            "game_status": "in_progress",
            "is_live": True,
            "away_team": "DAL",
            "home_team": "PHI",
            "quarter": 2,
            "time_remaining": "Halftime",
            "home_score": 14,
            "away_score": 10
        },
        "expected_interval": 15,
        "description": "Halftime break"
    },
    {
        "name": "Q4 Close Game",
        "game": {
            "game_id": "test_4",
            "game_status": "in_progress",
            "is_live": True,
            "away_team": "PIT",
            "home_team": "CLE",
            "quarter": 4,
            "home_score": 24,
            "away_score": 21
        },
        "expected_interval": 5,
        "description": "4th quarter, 3-point game (CRITICAL)"
    },
    {
        "name": "Q4 Blowout",
        "game": {
            "game_id": "test_5",
            "game_status": "in_progress",
            "is_live": True,
            "away_team": "SF",
            "home_team": "NYJ",
            "quarter": 4,
            "home_score": 10,
            "away_score": 35
        },
        "expected_interval": 10,
        "description": "4th quarter, 25-point lead"
    },
    {
        "name": "Completed Game",
        "game": {
            "game_id": "test_6",
            "game_status": "final",
            "away_team": "SF",
            "home_team": "SEA",
            "quarter": 4,
            "home_score": 30,
            "away_score": 27
        },
        "expected_interval": 300,
        "description": "Game over"
    }
]

print("Testing interval logic for different game scenarios:")
print()

all_passed = True
for scenario in test_scenarios:
    game = scenario["game"]
    expected = scenario["expected_interval"]
    actual = get_smart_interval(game)

    status = "✅ PASS" if actual == expected else "❌ FAIL"
    if actual != expected:
        all_passed = False

    print(f"{status} | {scenario['name']:20} | {actual:3}s | {scenario['description']}")
    if actual != expected:
        print(f"       Expected: {expected}s, Got: {actual}s")

print()
print("="*70)
print("RESULTS")
print("="*70)
print()

if all_passed:
    print("✅ All adaptive polling tests PASSED!")
    print()
    print("Interval Summary:")
    print("  •   5s - Q4 close games (≤7 point differential)")
    print("  •  10s - Regular live games")
    print("  •  15s - Halftime")
    print("  •  60s - Scheduled (not started)")
    print("  • 300s - Completed games")
    print()
    print("Expected API Call Reduction: 60-70%")
    print()
else:
    print("❌ Some tests failed!")
    sys.exit(1)

print("="*70)
