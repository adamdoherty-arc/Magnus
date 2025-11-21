"""
Debug NCAA AI predictions to find why all games show same 57% probability
"""
import sys
import logging
from src.prediction_agents.ncaa_predictor import NCAAPredictor
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

# Test with actual NCAA games from the user's screenshot
test_games = [
    ("Akron", "Bowling Green"),
    ("Massachusetts", "Ohio"),
    ("Ohio", "Western Michigan"),
    ("Buffalo", "Kent State"),
    ("Miami (OH)", "Ball State")
]

print("\n" + "="*80)
print("NCAA PREDICTION DEBUG TEST")
print("="*80)

predictor = NCAAPredictor()

print(f"\nTesting {len(test_games)} NCAA games...")
print("-" * 80)

predictions = []
for i, (away, home) in enumerate(test_games, 1):
    print(f"\n{i}. {away} @ {home}")

    # Get prediction
    prediction = predictor.predict_winner(
        home_team=home,
        away_team=away,
        game_date=datetime.now()
    )

    if prediction:
        winner = prediction.get('winner', 'unknown')
        prob = prediction.get('probability', 0)
        confidence = prediction.get('confidence', 'unknown')
        spread = prediction.get('spread_prediction', 0)

        print(f"   Winner: {winner}")
        print(f"   Probability: {prob:.1%}")
        print(f"   Confidence: {confidence}")
        print(f"   Spread: {spread:+.1f}")

        predictions.append({
            'game': f"{away} @ {home}",
            'winner': winner,
            'probability': prob
        })
    else:
        print(f"   ERROR: No prediction returned!")
        predictions.append({
            'game': f"{away} @ {home}",
            'winner': 'ERROR',
            'probability': 0
        })

print("\n" + "="*80)
print("SUMMARY")
print("="*80)

# Check if all predictions are identical
unique_probs = set(p['probability'] for p in predictions)

if len(unique_probs) == 1:
    prob = list(unique_probs)[0]
    print(f"\n🔴 BUG CONFIRMED: All {len(predictions)} games have IDENTICAL probability: {prob:.1%}")
    print("   This is the duplicate prediction bug!")
else:
    print(f"\n✅ Predictions are UNIQUE ({len(unique_probs)} different probabilities)")
    for prob in sorted(unique_probs):
        count = sum(1 for p in predictions if p['probability'] == prob)
        print(f"   {prob:.1%}: {count} games")

print("\nAll predictions:")
for p in predictions:
    print(f"  {p['game']:30} → {p['winner']:20} {p['probability']:.1%}")

print("\n" + "="*80)
