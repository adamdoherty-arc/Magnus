"""
Test script to verify enhanced prediction agents are working correctly.
"""
from src.prediction_agents import NFLPredictor, NCAAPredictor
from datetime import datetime

def test_nfl_predictions():
    """Test NFL predictor with various scenarios."""
    print("=" * 80)
    print("NFL PREDICTION AGENT TESTS")
    print("=" * 80)

    predictor = NFLPredictor()

    # Test 1: Strong favorite (Chiefs vs Panthers)
    print("\nTest 1: Strong Favorite - Kansas City Chiefs (home) vs Carolina Panthers (away)")
    print("-" * 80)
    prediction = predictor.predict_winner(
        home_team="Kansas City Chiefs",
        away_team="Carolina Panthers",
        game_date=datetime.now()
    )
    print(f"Winner: {prediction['winner']}")
    print(f"Probability: {prediction['probability']:.1%}")
    print(f"Confidence: {prediction['confidence']}")
    print(f"Spread: {prediction['spread']:.1f}")
    print(f"Home Elo: {prediction['home_elo']}")
    print(f"Away Elo: {prediction['away_elo']}")
    print(f"\nAdjustments:")
    for key, value in prediction['adjustments'].items():
        print(f"  {key}: {value}")
    print(f"\nExplanation:\n{prediction['explanation']}")

    # Test 2: Close matchup (Ravens at Bills)
    print("\n" + "=" * 80)
    print("Test 2: Close Matchup - Baltimore Ravens (away) at Buffalo Bills (home)")
    print("-" * 80)
    prediction = predictor.predict_winner(
        home_team="Buffalo Bills",
        away_team="Baltimore Ravens",
        game_date=datetime.now()
    )
    print(f"Winner: {prediction['winner']}")
    print(f"Probability: {prediction['probability']:.1%}")
    print(f"Confidence: {prediction['confidence']}")
    print(f"Spread: {prediction['spread']:.1f}")
    print(f"Home Elo: {prediction['home_elo']}")
    print(f"Away Elo: {prediction['away_elo']}")
    print(f"\nExplanation:\n{prediction['explanation']}")

    # Test 3: Division rivals (Steelers at Ravens)
    print("\n" + "=" * 80)
    print("Test 3: Division Rivals - Pittsburgh Steelers (away) at Baltimore Ravens (home)")
    print("-" * 80)
    prediction = predictor.predict_winner(
        home_team="Baltimore Ravens",
        away_team="Pittsburgh Steelers",
        game_date=datetime.now()
    )
    print(f"Winner: {prediction['winner']}")
    print(f"Probability: {prediction['probability']:.1%}")
    print(f"Confidence: {prediction['confidence']}")
    print(f"Spread: {prediction['spread']:.1f}")
    print(f"Divisional: {prediction['adjustments']['divisional']}")
    print(f"\nExplanation:\n{prediction['explanation']}")

def test_ncaa_predictions():
    """Test NCAA predictor with various scenarios."""
    print("\n\n" + "=" * 80)
    print("NCAA PREDICTION AGENT TESTS")
    print("=" * 80)

    predictor = NCAAPredictor()

    # Test 1: Strong favorite (Georgia vs Vanderbilt)
    print("\nTest 1: Strong Favorite - Georgia (home) vs Vanderbilt (away)")
    print("-" * 80)
    prediction = predictor.predict_winner(
        home_team="Georgia",
        away_team="Vanderbilt",
        game_date=datetime.now()
    )
    print(f"Winner: {prediction['winner']}")
    print(f"Probability: {prediction['probability']:.1%}")
    print(f"Confidence: {prediction['confidence']}")
    print(f"Spread: {prediction['spread']:.1f}")
    print(f"Home Elo: {prediction['home_elo']}")
    print(f"Away Elo: {prediction['away_elo']}")
    print(f"\nExplanation:\n{prediction['explanation']}")

    # Test 2: Top matchup (Michigan at Ohio State)
    print("\n" + "=" * 80)
    print("Test 2: Top Matchup - Michigan (away) at Ohio State (home)")
    print("-" * 80)
    prediction = predictor.predict_winner(
        home_team="Ohio State",
        away_team="Michigan",
        game_date=datetime.now()
    )
    print(f"Winner: {prediction['winner']}")
    print(f"Probability: {prediction['probability']:.1%}")
    print(f"Confidence: {prediction['confidence']}")
    print(f"Spread: {prediction['spread']:.1f}")
    print(f"Home Elo: {prediction['home_elo']}")
    print(f"Away Elo: {prediction['away_elo']}")
    print(f"\nExplanation:\n{prediction['explanation']}")

def print_summary():
    """Print summary of enhancements."""
    print("\n\n" + "=" * 80)
    print("ENHANCEMENT SUMMARY")
    print("=" * 80)
    print("\nEnhancements Applied:")
    print("1. Realistic Elo ratings based on 2024-2025 season performance")
    print("2. Team strength modifiers (offensive/defensive rankings)")
    print("3. Recent form tracking (wins in last 5 games)")
    print("4. Momentum adjustments")
    print("5. Matchup-specific analysis (offense vs defense)")
    print("6. Detailed expert-style explanations")
    print("7. Proper prediction variance (65-75% vs 52-58% for rivalries)")
    print("\nExpected Results:")
    print("- Strong favorites: 65-75% win probability, high confidence")
    print("- Close matchups: 50-55% win probability, low confidence")
    print("- Division rivals: Adjusted toward 50%, medium confidence")
    print("- Explanations: Detailed with team strengths, momentum, matchups")

if __name__ == '__main__':
    test_nfl_predictions()
    test_ncaa_predictions()
    print_summary()
    print("\n" + "=" * 80)
    print("ALL TESTS COMPLETED")
    print("=" * 80)
