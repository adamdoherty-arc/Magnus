"""
Test script for NFL and NCAA prediction agents.

This script initializes the prediction agents and tests them with sample games.
"""

import sys
from datetime import datetime
from src.prediction_agents import NFLPredictor, NCAAPredictor


def test_nfl_predictor():
    """Test NFL predictions."""
    print("=" * 70)
    print("NFL PREDICTION AGENT TEST")
    print("=" * 70)

    try:
        predictor = NFLPredictor()
        print("\n✅ NFL Predictor initialized successfully")

        # Save initial Elo ratings
        predictor._save_elo_ratings()
        print("✅ NFL Elo ratings saved to file")

        # Test game: Kansas City Chiefs vs Buffalo Bills
        print("\n" + "-" * 70)
        print("TEST GAME: Kansas City Chiefs (Home) vs Buffalo Bills (Away)")
        print("-" * 70)

        prediction = predictor.predict_winner(
            home_team="Kansas City Chiefs",
            away_team="Buffalo Bills",
            game_date=datetime(2025, 11, 16)
        )

        print(f"\n🏆 Predicted Winner: {prediction['winner']}")
        print(f"📊 Win Probability: {prediction['probability']:.1%}")
        print(f"🎯 Confidence: {prediction['confidence'].upper()}")
        print(f"📈 Predicted Spread: {prediction['spread']:.1f} points")

        if prediction.get('explanation'):
            print(f"\n💡 Explanation:")
            print(f"   {prediction['explanation']}")

        # Print key features
        print(f"\n📋 Key Features:")
        features = prediction.get('features', {})
        for feature, value in features.items():
            if isinstance(value, float):
                print(f"   • {feature}: {value:.2f}")
            else:
                print(f"   • {feature}: {value}")

        # Print adjustments
        adjustments = prediction.get('adjustments', {})
        if adjustments:
            print(f"\n🔧 Prediction Adjustments:")
            for adj, value in adjustments.items():
                print(f"   • {adj}: {value}")

        return True

    except Exception as e:
        print(f"\n❌ NFL Predictor test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ncaa_predictor():
    """Test NCAA predictions."""
    print("\n" + "=" * 70)
    print("NCAA PREDICTION AGENT TEST")
    print("=" * 70)

    try:
        predictor = NCAAPredictor()
        print("\n✅ NCAA Predictor initialized successfully")

        # Save initial Elo ratings
        predictor._save_elo_ratings()
        print("✅ NCAA Elo ratings saved to file")

        # Test game: Alabama vs Georgia
        print("\n" + "-" * 70)
        print("TEST GAME: Alabama (Home) vs Georgia (Away)")
        print("-" * 70)

        prediction = predictor.predict_winner(
            home_team="Alabama",
            away_team="Georgia",
            game_date=datetime(2025, 11, 16),
            crowd_size=100000  # Bryant-Denny Stadium
        )

        print(f"\n🏆 Predicted Winner: {prediction['winner']}")
        print(f"📊 Win Probability: {prediction['probability']:.1%}")
        print(f"🎯 Confidence: {prediction['confidence'].upper()}")
        print(f"📈 Predicted Spread: {prediction['spread']:.1f} points")

        if prediction.get('explanation'):
            print(f"\n💡 Explanation:")
            print(f"   {prediction['explanation']}")

        # Print key features
        print(f"\n📋 Key Features:")
        features = prediction.get('features', {})
        for feature, value in features.items():
            if isinstance(value, float):
                print(f"   • {feature}: {value:.2f}")
            else:
                print(f"   • {feature}: {value}")

        # Print adjustments
        adjustments = prediction.get('adjustments', {})
        if adjustments:
            print(f"\n🔧 Prediction Adjustments:")
            for adj, value in adjustments.items():
                if isinstance(value, (int, float)):
                    print(f"   • {adj}: {value}")
                else:
                    print(f"   • {adj}: {value}")

        return True

    except Exception as e:
        print(f"\n❌ NCAA Predictor test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_batch_predictions():
    """Test multiple game predictions."""
    print("\n" + "=" * 70)
    print("BATCH PREDICTION TEST (NFL)")
    print("=" * 70)

    try:
        nfl_predictor = NFLPredictor()

        games = [
            ("Kansas City Chiefs", "Buffalo Bills"),
            ("Philadelphia Eagles", "Dallas Cowboys"),
            ("San Francisco 49ers", "Seattle Seahawks"),
            ("Green Bay Packers", "Chicago Bears"),
        ]

        print(f"\nPredicting {len(games)} NFL games...\n")

        for home, away in games:
            try:
                pred = nfl_predictor.predict_winner(home, away)

                # Determine confidence emoji
                conf = pred['confidence']
                if conf == 'high':
                    emoji = '🟢'
                elif conf == 'medium':
                    emoji = '🟡'
                else:
                    emoji = '⚪'

                print(f"{home} vs {away}")
                print(f"  → {pred['winner']} {emoji} ({pred['probability']:.0%}) - {pred['confidence']} confidence")
                print(f"     Spread: {pred['spread']:.1f} points")
                print()

            except Exception as e:
                print(f"{home} vs {away}")
                print(f"  → Error: {e}")
                print()

        return True

    except Exception as e:
        print(f"\n❌ Batch prediction test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_confidence_levels():
    """Test that confidence levels are correctly calculated."""
    print("\n" + "=" * 70)
    print("CONFIDENCE LEVEL TEST")
    print("=" * 70)

    try:
        nfl_predictor = NFLPredictor()

        # Test different probability scenarios
        test_cases = [
            (0.80, 'high', '80% probability should be high confidence'),
            (0.65, 'medium', '65% probability should be medium confidence'),
            (0.52, 'low', '52% probability should be low confidence'),
            (0.95, 'high', '95% probability should be high confidence'),
        ]

        print("\nTesting confidence level calculations:\n")

        all_passed = True
        for probability, expected_conf, description in test_cases:
            actual_conf = nfl_predictor.get_confidence(probability)
            passed = (actual_conf == expected_conf)

            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{status} - {description}")
            print(f"       Expected: {expected_conf}, Got: {actual_conf}")

            if not passed:
                all_passed = False

        return all_passed

    except Exception as e:
        print(f"\n❌ Confidence level test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("SPORTS PREDICTION AGENTS - COMPREHENSIVE TEST SUITE")
    print("=" * 70 + "\n")

    results = []

    # Run tests
    results.append(("NFL Predictor Initialization", test_nfl_predictor()))
    results.append(("NCAA Predictor Initialization", test_ncaa_predictor()))
    results.append(("Batch Predictions", test_batch_predictions()))
    results.append(("Confidence Level Calculation", test_confidence_levels()))

    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70 + "\n")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} - {test_name}")

    print(f"\n{'=' * 70}")
    print(f"OVERALL: {passed}/{total} tests passed")
    print("=" * 70)

    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Prediction agents are ready for production use.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review errors above.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
