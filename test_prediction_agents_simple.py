"""
Simple test script for NFL and NCAA prediction agents (Windows compatible).
"""

from datetime import datetime
from src.prediction_agents import NFLPredictor, NCAAPredictor


def test_nfl():
    """Test NFL predictor."""
    print("\n" + "=" * 60)
    print("NFL PREDICTION TEST")
    print("=" * 60)

    predictor = NFLPredictor()
    print("[OK] NFL Predictor initialized")

    # Save Elo ratings
    predictor._save_elo_ratings()
    print("[OK] Elo ratings saved")

    # Test prediction
    pred = predictor.predict_winner(
        home_team="Kansas City Chiefs",
        away_team="Buffalo Bills"
    )

    print(f"\nPredicted Winner: {pred['winner']}")
    print(f"Win Probability: {pred['probability']:.1%}")
    print(f"Confidence: {pred['confidence']}")
    print(f"Spread: {pred['spread']:.1f} pts")
    print(f"\nExplanation: {pred.get('explanation', 'N/A')}")

    return True


def test_ncaa():
    """Test NCAA predictor."""
    print("\n" + "=" * 60)
    print("NCAA PREDICTION TEST")
    print("=" * 60)

    predictor = NCAAPredictor()
    print("[OK] NCAA Predictor initialized")

    # Save Elo ratings
    predictor._save_elo_ratings()
    print("[OK] Elo ratings saved")

    # Test prediction
    pred = predictor.predict_winner(
        home_team="Alabama",
        away_team="Georgia",
        crowd_size=100000
    )

    print(f"\nPredicted Winner: {pred['winner']}")
    print(f"Win Probability: {pred['probability']:.1%}")
    print(f"Confidence: {pred['confidence']}")
    print(f"Spread: {pred['spread']:.1f} pts")
    print(f"\nExplanation: {pred.get('explanation', 'N/A')}")

    return True


def test_batch():
    """Test batch predictions."""
    print("\n" + "=" * 60)
    print("BATCH NFL PREDICTIONS")
    print("=" * 60)

    predictor = NFLPredictor()

    games = [
        ("Kansas City Chiefs", "Buffalo Bills"),
        ("Philadelphia Eagles", "Dallas Cowboys"),
        ("San Francisco 49ers", "Seattle Seahawks"),
    ]

    for home, away in games:
        pred = predictor.predict_winner(home, away)
        print(f"\n{home} vs {away}")
        print(f"  Winner: {pred['winner']} ({pred['probability']:.0%})")
        print(f"  Confidence: {pred['confidence']}")

    return True


if __name__ == "__main__":
    print("\nSTARTING PREDICTION AGENT TESTS\n")

    try:
        test_nfl()
        test_ncaa()
        test_batch()

        print("\n" + "=" * 60)
        print("ALL TESTS PASSED!")
        print("=" * 60)
        print("\nPrediction agents are ready for use.")
        print("Check src/data/ for saved Elo ratings.\n")

    except Exception as e:
        print(f"\nTEST FAILED: {e}")
        import traceback
        traceback.print_exc()
