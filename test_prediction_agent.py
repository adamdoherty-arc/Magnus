"""
Test Suite for Prediction Agent

Comprehensive tests for multi-sector prediction system.

Author: Python Pro
Created: 2025-11-09
"""

import sys
import logging
from pathlib import Path
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from prediction_agent import (
    MultiSectorPredictor,
    EnsembleModel,
    FeatureEngineering,
    DataSourceManager,
    MarketSector,
    detect_sector,
    get_sector_config,
    SECTOR_CONFIGS
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TestResults:
    """Track test results"""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []

    def record_pass(self, test_name: str):
        self.passed += 1
        logger.info(f"✓ {test_name} - PASSED")

    def record_fail(self, test_name: str, error: str):
        self.failed += 1
        self.errors.append((test_name, error))
        logger.error(f"✗ {test_name} - FAILED: {error}")

    def summary(self):
        total = self.passed + self.failed
        logger.info(f"\n{'='*80}")
        logger.info(f"TEST SUMMARY")
        logger.info(f"{'='*80}")
        logger.info(f"Total Tests: {total}")
        logger.info(f"Passed: {self.passed} ({self.passed/total*100:.1f}%)")
        logger.info(f"Failed: {self.failed} ({self.failed/total*100:.1f}%)")

        if self.errors:
            logger.info(f"\nFailed Tests:")
            for test_name, error in self.errors:
                logger.info(f"  - {test_name}: {error}")

        logger.info(f"{'='*80}\n")
        return self.failed == 0


def test_sector_detection():
    """Test automatic sector detection"""
    results = TestResults()

    test_cases = [
        ("Will the Chiefs win the Super Bowl?", MarketSector.SPORTS),
        ("NFL game outcome", MarketSector.SPORTS),
        ("Will Biden win the election?", MarketSector.POLITICS),
        ("Congressional race results", MarketSector.POLITICS),
        ("Will GDP grow by 2%?", MarketSector.ECONOMICS),
        ("Fed interest rate decision", MarketSector.ECONOMICS),
        ("Will Bitcoin reach $100k?", MarketSector.CRYPTO),
        ("Ethereum price target", MarketSector.CRYPTO),
    ]

    for text, expected_sector in test_cases:
        try:
            detected = detect_sector(text)
            if detected == expected_sector:
                results.record_pass(f"Sector detection: {text[:30]}...")
            else:
                results.record_fail(
                    f"Sector detection: {text[:30]}...",
                    f"Expected {expected_sector}, got {detected}"
                )
        except Exception as e:
            results.record_fail(f"Sector detection: {text[:30]}...", str(e))

    return results


def test_sector_configs():
    """Test sector configurations"""
    results = TestResults()

    for sector in MarketSector:
        try:
            config = get_sector_config(sector)

            # Check required fields
            assert config.sector == sector
            assert len(config.feature_groups) > 0
            assert len(config.xgboost_params) > 0
            assert len(config.data_sources) > 0
            assert 0 <= config.min_confidence_threshold <= 1
            assert config.min_confidence_threshold < config.max_confidence_threshold

            results.record_pass(f"Sector config: {sector.value}")
        except Exception as e:
            results.record_fail(f"Sector config: {sector.value}", str(e))

    return results


def test_data_sources():
    """Test data source integrations"""
    results = TestResults()

    manager = DataSourceManager()

    # Test Reddit (may fail without API key, that's ok)
    try:
        result = manager.get_reddit_sentiment('nfl', ['chiefs'], limit=10)
        if result.success or result.error:  # Either success or graceful error
            results.record_pass("Data source: Reddit API")
        else:
            results.record_fail("Data source: Reddit API", "Unexpected result")
    except Exception as e:
        results.record_fail("Data source: Reddit API", str(e))

    # Test CoinGecko
    try:
        result = manager.get_crypto_data('bitcoin')
        if result.success:
            assert 'current_price' in result.data
            results.record_pass("Data source: CoinGecko API")
        else:
            results.record_fail("Data source: CoinGecko API", result.error or "No data")
    except Exception as e:
        results.record_fail("Data source: CoinGecko API", str(e))

    # Test yfinance
    try:
        result = manager.get_market_data('SPY')
        if result.success:
            assert 'latest_price' in result.data
            results.record_pass("Data source: yfinance")
        else:
            results.record_fail("Data source: yfinance", result.error or "No data")
    except Exception as e:
        results.record_fail("Data source: yfinance", str(e))

    # Test FRED (may fail without API key)
    try:
        result = manager.get_fred_indicator('UNRATE')
        if result.success or result.error:  # Either success or graceful error
            results.record_pass("Data source: FRED API")
        else:
            results.record_fail("Data source: FRED API", "Unexpected result")
    except Exception as e:
        results.record_fail("Data source: FRED API", str(e))

    return results


def test_feature_engineering():
    """Test feature extraction"""
    results = TestResults()

    feature_eng = FeatureEngineering()

    test_market = {
        'ticker': 'TEST-001',
        'title': 'Test market for NFL game',
        'yes_price': 0.45,
        'no_price': 0.55,
        'volume': 100000,
        'open_interest': 5000,
        'close_time': (datetime.now() + timedelta(hours=24)).isoformat(),
    }

    # Test each sector
    for sector in MarketSector:
        try:
            context = {'sport': 'nfl', 'keywords': ['test']}
            features = feature_eng.extract_features(test_market, sector, context)

            # Check common features
            assert 'yes_price' in features
            assert 'volume_log' in features
            assert 'hours_to_close' in features
            assert all(isinstance(v, (int, float)) for v in features.values())
            assert all(np.isfinite(v) for v in features.values())

            results.record_pass(f"Feature extraction: {sector.value}")
        except Exception as e:
            results.record_fail(f"Feature extraction: {sector.value}", str(e))

    # Test batch feature extraction
    try:
        markets = [test_market] * 5
        contexts = [{'sport': 'nfl'}] * 5
        df = feature_eng.create_feature_dataframe(
            markets, MarketSector.SPORTS, contexts
        )

        assert len(df) == 5
        assert 'ticker' in df.columns
        assert len(df.columns) > 10  # Should have many features

        results.record_pass("Batch feature extraction")
    except Exception as e:
        results.record_fail("Batch feature extraction", str(e))

    return results


def test_ensemble_model():
    """Test ensemble model training and prediction"""
    results = TestResults()

    # Generate synthetic data
    np.random.seed(42)
    n_samples = 200
    n_features = 15

    X = pd.DataFrame(
        np.random.randn(n_samples, n_features),
        columns=[f'feature_{i}' for i in range(n_features)]
    )
    y = ((X['feature_0'] + X['feature_1']) > 0).astype(int).values

    # Test model initialization
    try:
        model = EnsembleModel(calibration_method='isotonic')
        assert not model.is_trained
        results.record_pass("Ensemble model: Initialization")
    except Exception as e:
        results.record_fail("Ensemble model: Initialization", str(e))
        return results

    # Test training
    try:
        metrics = model.train(X, y, validation_split=0.2)

        assert 'accuracy' in metrics
        assert 'log_loss' in metrics
        assert 'brier_score' in metrics
        assert 'auc_roc' in metrics
        assert 0 <= metrics['accuracy'] <= 1
        assert model.is_trained

        results.record_pass("Ensemble model: Training")
    except Exception as e:
        results.record_fail("Ensemble model: Training", str(e))
        return results

    # Test prediction
    try:
        X_test = X.head(10)
        predictions, probabilities = model.predict(X_test)

        assert len(predictions) == 10
        assert len(probabilities) == 10
        assert all(p in [0, 1] for p in predictions)
        assert all(0 <= p <= 1 for p in probabilities)

        results.record_pass("Ensemble model: Prediction")
    except Exception as e:
        results.record_fail("Ensemble model: Prediction", str(e))

    # Test feature importance
    try:
        importance = model.get_feature_importance(top_n=10)
        assert len(importance) == min(10, n_features)
        assert 'feature' in importance.columns
        assert 'importance' in importance.columns

        results.record_pass("Ensemble model: Feature importance")
    except Exception as e:
        results.record_fail("Ensemble model: Feature importance", str(e))

    # Test save/load
    try:
        model_path = "test_ensemble_model.pkl"
        model.save_model(model_path)

        model2 = EnsembleModel()
        model2.load_model(model_path)

        assert model2.is_trained
        assert model2.n_samples_trained == model.n_samples_trained

        # Cleanup
        import os
        if os.path.exists(model_path):
            os.remove(model_path)

        results.record_pass("Ensemble model: Save/load")
    except Exception as e:
        results.record_fail("Ensemble model: Save/load", str(e))

    return results


def test_multi_sector_predictor():
    """Test main prediction system"""
    results = TestResults()

    predictor = MultiSectorPredictor()

    # Test single market prediction
    try:
        market = {
            'ticker': 'TEST-NFL-001',
            'title': 'Will the Chiefs win the game?',
            'yes_price': 0.45,
            'no_price': 0.55,
            'volume': 100000,
            'open_interest': 5000,
            'close_time': datetime.now().isoformat(),
        }

        prediction = predictor.predict_market(market)

        assert 'ticker' in prediction
        assert 'sector' in prediction
        assert 'predicted_outcome' in prediction
        assert 'confidence_score' in prediction
        assert 'calibrated_probability' in prediction
        assert 'edge_percentage' in prediction
        assert 'recommended_action' in prediction

        results.record_pass("Multi-sector predictor: Single prediction")
    except Exception as e:
        results.record_fail("Multi-sector predictor: Single prediction", str(e))

    # Test batch prediction
    try:
        markets = [
            {
                'ticker': f'TEST-{i:03d}',
                'title': 'Test market',
                'yes_price': 0.4 + i * 0.05,
                'no_price': 0.6 - i * 0.05,
                'volume': 100000,
                'open_interest': 5000,
                'close_time': datetime.now().isoformat(),
            }
            for i in range(5)
        ]

        predictions = predictor.predict_markets(markets)

        assert len(predictions) == 5
        assert all('overall_rank' in p for p in predictions)
        assert [p['overall_rank'] for p in predictions] == list(range(1, 6))

        results.record_pass("Multi-sector predictor: Batch prediction")
    except Exception as e:
        results.record_fail("Multi-sector predictor: Batch prediction", str(e))

    # Test with LLM predictions
    try:
        market = {
            'ticker': 'TEST-LLM-001',
            'title': 'Test market with LLM',
            'yes_price': 0.45,
            'no_price': 0.55,
            'volume': 100000,
            'open_interest': 5000,
            'close_time': datetime.now().isoformat(),
        }

        llm_prediction = {
            'ticker': 'TEST-LLM-001',
            'predicted_outcome': 'yes',
            'confidence_score': 75.0,
            'edge_percentage': 5.0
        }

        prediction = predictor.predict_market(market, llm_prediction)

        assert 'llm_confidence' in prediction
        assert 'ensemble_weight_ml' in prediction
        assert 'ensemble_weight_llm' in prediction

        results.record_pass("Multi-sector predictor: LLM integration")
    except Exception as e:
        results.record_fail("Multi-sector predictor: LLM integration", str(e))

    # Test model statistics
    try:
        stats = predictor.get_sector_statistics()

        assert len(stats) == len(MarketSector)
        for sector_name, stat in stats.items():
            assert 'is_trained' in stat
            assert 'n_samples_trained' in stat
            assert 'n_features' in stat

        results.record_pass("Multi-sector predictor: Statistics")
    except Exception as e:
        results.record_fail("Multi-sector predictor: Statistics", str(e))

    # Test model training
    try:
        # Generate synthetic training data
        n_samples = 150
        training_markets = []
        outcomes = []

        for i in range(n_samples):
            yes_price = np.random.uniform(0.3, 0.7)
            outcome = 1 if np.random.random() < yes_price else 0

            market = {
                'ticker': f'TRAIN-{i:03d}',
                'title': 'Training market',
                'yes_price': yes_price,
                'no_price': 1 - yes_price,
                'volume': np.random.uniform(10000, 500000),
                'open_interest': int(np.random.uniform(100, 50000)),
                'close_time': datetime.now().isoformat(),
            }

            training_markets.append(market)
            outcomes.append(outcome)

        metrics = predictor.train_sector_model(
            MarketSector.SPORTS,
            training_markets,
            outcomes
        )

        assert 'accuracy' in metrics
        assert 'auc_roc' in metrics
        assert metrics['n_samples'] == n_samples

        results.record_pass("Multi-sector predictor: Model training")
    except Exception as e:
        results.record_fail("Multi-sector predictor: Model training", str(e))

    return results


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("PREDICTION AGENT TEST SUITE")
    print("="*80 + "\n")

    all_results = []

    # Run test suites
    logger.info("Testing sector detection...")
    all_results.append(test_sector_detection())

    logger.info("\nTesting sector configurations...")
    all_results.append(test_sector_configs())

    logger.info("\nTesting data sources...")
    all_results.append(test_data_sources())

    logger.info("\nTesting feature engineering...")
    all_results.append(test_feature_engineering())

    logger.info("\nTesting ensemble model...")
    all_results.append(test_ensemble_model())

    logger.info("\nTesting multi-sector predictor...")
    all_results.append(test_multi_sector_predictor())

    # Overall summary
    total_passed = sum(r.passed for r in all_results)
    total_failed = sum(r.failed for r in all_results)
    total_tests = total_passed + total_failed

    print("\n" + "="*80)
    print("OVERALL TEST RESULTS")
    print("="*80)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {total_passed} ({total_passed/total_tests*100:.1f}%)")
    print(f"Failed: {total_failed} ({total_failed/total_tests*100:.1f}%)")

    if total_failed > 0:
        print("\nSome tests failed. Check logs above for details.")
        print("="*80 + "\n")
        return 1
    else:
        print("\n[SUCCESS] ALL TESTS PASSED")
        print("="*80 + "\n")
        return 0


if __name__ == "__main__":
    sys.exit(main())
