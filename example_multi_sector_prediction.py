"""
Example: Multi-Sector Prediction Markets

Demonstrates how to use the Prediction Agent for sports, politics, economics, and crypto markets.

Author: Python Pro
Created: 2025-11-09
"""

import os
import sys
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from prediction_agent import MultiSectorPredictor, MarketSector
from kalshi_db_manager import KalshiDBManager
from kalshi_ai_evaluator import KalshiAIEvaluator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def example_1_predict_single_market():
    """Example 1: Predict a single market"""
    print("\n" + "="*80)
    print("EXAMPLE 1: Predict Single Market")
    print("="*80)

    # Initialize predictor
    predictor = MultiSectorPredictor()

    # Create test market (sports)
    market = {
        'ticker': 'NFL-CHIEFS-SB-2025',
        'title': 'Will the Kansas City Chiefs win Super Bowl LIX?',
        'yes_price': 0.35,
        'no_price': 0.65,
        'volume': 250000,
        'open_interest': 15000,
        'close_time': (datetime.now() + timedelta(days=90)).isoformat(),
        'home_team': 'Chiefs',
        'away_team': ''
    }

    # Get LLM prediction (from existing system)
    llm_prediction = {
        'ticker': 'NFL-CHIEFS-SB-2025',
        'predicted_outcome': 'yes',
        'confidence_score': 72.5,
        'edge_percentage': 8.3,
        'recommended_action': 'buy'
    }

    # Make prediction
    prediction = predictor.predict_market(market, llm_prediction)

    print(f"\nMarket: {market['title']}")
    print(f"Current Price: YES @ {market['yes_price']:.2%}")
    print(f"\nPrediction Results:")
    print(f"  Sector: {prediction['sector']}")
    print(f"  Predicted Outcome: {prediction['predicted_outcome']}")
    print(f"  Calibrated Probability: {prediction['calibrated_probability']:.2%}")
    print(f"  Confidence: {prediction['confidence_score']:.1f}%")
    print(f"  Edge: {prediction['edge_percentage']:.2f}%")
    print(f"  Recommendation: {prediction['recommended_action']}")
    print(f"  Suggested Stake: {prediction['recommended_stake_pct']:.2f}%")

    if 'llm_confidence' in prediction:
        print(f"\nEnsemble Details:")
        print(f"  LLM Confidence: {prediction['llm_confidence']:.1f}%")
        print(f"  ML Weight: {prediction.get('ensemble_weight_ml', 0):.0%}")
        print(f"  LLM Weight: {prediction.get('ensemble_weight_llm', 0):.0%}")


def example_2_predict_multiple_sectors():
    """Example 2: Predict markets from multiple sectors"""
    print("\n" + "="*80)
    print("EXAMPLE 2: Multi-Sector Predictions")
    print("="*80)

    predictor = MultiSectorPredictor()

    # Markets from different sectors
    markets = [
        # Sports
        {
            'ticker': 'NBA-LAKERS-CHAMP-2025',
            'title': 'Will the Lakers win the 2025 NBA Championship?',
            'yes_price': 0.12,
            'no_price': 0.88,
            'volume': 180000,
            'open_interest': 9000,
            'close_time': (datetime.now() + timedelta(days=180)).isoformat(),
        },
        # Politics
        {
            'ticker': 'PRES-2024-BIDEN',
            'title': 'Will Joe Biden win the 2024 Presidential Election?',
            'yes_price': 0.48,
            'no_price': 0.52,
            'volume': 1500000,
            'open_interest': 75000,
            'close_time': (datetime.now() + timedelta(days=30)).isoformat(),
        },
        # Economics
        {
            'ticker': 'FED-RATE-CUT-2024',
            'title': 'Will the Fed cut rates by year end 2024?',
            'yes_price': 0.68,
            'no_price': 0.32,
            'volume': 450000,
            'open_interest': 22000,
            'close_time': (datetime.now() + timedelta(days=60)).isoformat(),
        },
        # Crypto
        {
            'ticker': 'BTC-100K-2024',
            'title': 'Will Bitcoin reach $100,000 in 2024?',
            'yes_price': 0.32,
            'no_price': 0.68,
            'volume': 850000,
            'open_interest': 42000,
            'close_time': (datetime.now() + timedelta(days=50)).isoformat(),
        }
    ]

    # Make predictions
    predictions = predictor.predict_markets(markets)

    print(f"\nGenerated {len(predictions)} predictions:\n")

    for pred in predictions:
        print(f"Rank #{pred['overall_rank']}: {pred['ticker']}")
        print(f"  Sector: {pred['sector']}")
        print(f"  Prediction: {pred['predicted_outcome'].upper()} @ {pred['calibrated_probability']:.2%}")
        print(f"  Confidence: {pred['confidence_score']:.1f}%, Edge: {pred['edge_percentage']:.2f}%")
        print(f"  Action: {pred['recommended_action']}")
        print()


def example_3_train_sector_model():
    """Example 3: Train a model for a specific sector"""
    print("\n" + "="*80)
    print("EXAMPLE 3: Train Sector Model")
    print("="*80)

    import numpy as np

    predictor = MultiSectorPredictor()

    # Generate synthetic training data (in production, use real historical data)
    n_samples = 200
    training_markets = []
    outcomes = []

    for i in range(n_samples):
        yes_price = np.random.uniform(0.2, 0.8)
        outcome = 1 if np.random.random() < yes_price else 0

        market = {
            'ticker': f'TRAIN-SPORTS-{i:03d}',
            'title': f'Training market {i}',
            'yes_price': yes_price,
            'no_price': 1 - yes_price,
            'volume': np.random.uniform(10000, 500000),
            'open_interest': int(np.random.uniform(100, 50000)),
            'close_time': datetime.now().isoformat(),
        }

        training_markets.append(market)
        outcomes.append(outcome)

    print(f"\nTraining sports model with {n_samples} samples...")

    # Train model
    metrics = predictor.train_sector_model(
        sector=MarketSector.SPORTS,
        training_markets=training_markets,
        outcomes=outcomes
    )

    print(f"\nTraining Results:")
    print(f"  Accuracy: {metrics['accuracy']:.2%}")
    print(f"  Log Loss: {metrics['log_loss']:.4f}")
    print(f"  Brier Score: {metrics['brier_score']:.4f}")
    print(f"  AUC-ROC: {metrics['auc_roc']:.4f}")
    print(f"  Samples: {metrics['n_samples']}")
    print(f"  Features: {metrics['n_features']}")

    print(f"\n✓ Model saved to: {predictor.models_dir / 'sports_model.pkl'}")


def example_4_integrate_with_kalshi():
    """Example 4: Integrate with existing Kalshi database"""
    print("\n" + "="*80)
    print("EXAMPLE 4: Integrate with Kalshi Database")
    print("="*80)

    # Initialize components
    db = KalshiDBManager()
    llm_evaluator = KalshiAIEvaluator()
    predictor = MultiSectorPredictor()

    # Get active markets from database
    print("\nFetching active markets from database...")
    active_markets = db.get_active_markets()

    if not active_markets:
        print("No active markets found in database.")
        print("Run sync_kalshi_complete.py first to populate markets.")
        return

    print(f"Found {len(active_markets)} active markets")

    # Get LLM predictions for markets
    print("\nGenerating LLM predictions...")
    llm_predictions = llm_evaluator.evaluate_markets(active_markets)

    # Generate ensemble predictions
    print("\nGenerating ensemble predictions...")
    ensemble_predictions = predictor.predict_markets(
        active_markets[:10],  # Limit to first 10 for demo
        llm_predictions[:10]
    )

    # Display top opportunities
    print(f"\nTop 5 Opportunities:\n")
    for pred in ensemble_predictions[:5]:
        print(f"#{pred['overall_rank']}: {pred['ticker']}")
        print(f"  Sector: {pred['sector']}")
        print(f"  Confidence: {pred['confidence_score']:.1f}%")
        print(f"  Edge: {pred['edge_percentage']:.2f}%")
        print(f"  Action: {pred['recommended_action']}")
        print()

    # Store predictions in database (would need to extend db_manager)
    print("Note: To store predictions, extend KalshiDBManager.store_predictions()")
    print("      to handle new calibrated_probability and sector fields.")


def example_5_model_statistics():
    """Example 5: View model statistics"""
    print("\n" + "="*80)
    print("EXAMPLE 5: Model Statistics")
    print("="*80)

    predictor = MultiSectorPredictor()

    stats = predictor.get_sector_statistics()

    print("\nModel Statistics by Sector:\n")
    for sector, stat in stats.items():
        print(f"{sector.upper()}:")
        print(f"  Trained: {'Yes' if stat['is_trained'] else 'No'}")
        print(f"  Training Samples: {stat['n_samples_trained']}")
        print(f"  Features: {stat['n_features']}")

        if stat['metrics']:
            print(f"  Metrics:")
            for metric, value in stat['metrics'].items():
                if isinstance(value, float):
                    print(f"    {metric}: {value:.4f}")
                else:
                    print(f"    {metric}: {value}")
        print()


def main():
    """Run all examples"""
    print("\n" + "="*80)
    print("MULTI-SECTOR PREDICTION AGENT - EXAMPLES")
    print("="*80)

    try:
        # Run examples
        example_1_predict_single_market()
        example_2_predict_multiple_sectors()
        example_3_train_sector_model()
        example_5_model_statistics()

        # Example 4 requires database setup
        print("\n" + "="*80)
        print("EXAMPLE 4: Database Integration")
        print("="*80)
        print("\nTo run database integration example:")
        print("1. Ensure PostgreSQL is running")
        print("2. Run: python sync_kalshi_complete.py")
        print("3. Uncomment example_4_integrate_with_kalshi() below")

        # Uncomment to run if database is set up:
        # example_4_integrate_with_kalshi()

    except Exception as e:
        logger.error(f"Error running examples: {e}", exc_info=True)
        return 1

    print("\n" + "="*80)
    print("ALL EXAMPLES COMPLETE")
    print("="*80)
    print("\nNext Steps:")
    print("1. Train models with real historical data")
    print("2. Set up API keys (FRED_API_KEY, REDDIT_CLIENT_ID)")
    print("3. Apply database schema updates: psql -d magnus -f src/prediction_agent/schema_updates.sql")
    print("4. Integrate with production Kalshi sync")
    print("="*80 + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
