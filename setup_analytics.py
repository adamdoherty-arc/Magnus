"""
Analytics System Setup and Verification

Initializes the analytics pipeline and verifies all components are working.

Usage:
    python setup_analytics.py
"""

import sys
import os
import traceback

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


def test_imports():
    """Test that all analytics modules can be imported"""
    print("Testing module imports...")
    print("-" * 80)

    try:
        print("  [1/4] Importing metrics module...")
        from analytics.metrics import (
            calculate_brier_score,
            calculate_log_loss,
            calculate_sharpe_ratio,
            calculate_sortino_ratio,
            calculate_max_drawdown,
        )
        print("        [OK] Metrics module OK")

        print("  [2/4] Importing performance_tracker module...")
        from analytics.performance_tracker import PerformanceTracker
        print("        [OK] Performance tracker module OK")

        print("  [3/4] Importing backtest module...")
        from analytics.backtest import BacktestEngine, BacktestConfig
        print("        [OK] Backtest module OK")

        print("  [4/4] Importing feature_store module...")
        from analytics.feature_store import FeatureStore
        print("        [OK] Feature store module OK")

        print("\n[OK] All modules imported successfully!")
        return True

    except Exception as e:
        print(f"\n[FAIL] Import failed: {e}")
        traceback.print_exc()
        return False


def test_database_connection():
    """Test database connection"""
    print("\n\nTesting database connection...")
    print("-" * 80)

    try:
        import psycopg2
        db_config = {
            'host': 'localhost',
            'port': '5432',
            'database': 'magnus',
            'user': 'postgres',
            'password': os.getenv('DB_PASSWORD')
        }

        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        cur.close()
        conn.close()

        print(f"  [OK] Connected to PostgreSQL")
        print(f"    Version: {version[:50]}...")
        return True

    except Exception as e:
        print(f"  [FAIL] Connection failed: {e}")
        print("\n  Make sure:")
        print("    1. PostgreSQL is running")
        print("    2. Database 'magnus' exists")
        print("    3. DB_PASSWORD environment variable is set")
        return False


def initialize_schema():
    """Initialize analytics schema"""
    print("\n\nInitializing analytics schema...")
    print("-" * 80)

    try:
        from analytics.performance_tracker import PerformanceTracker

        tracker = PerformanceTracker()
        print("  [OK] Analytics schema initialized")
        print("    Tables created:")
        print("      - prediction_performance")
        print("      - feature_store")
        print("      - backtest_results")
        print("      - backtest_trades")
        print("      - performance_snapshots")
        return True

    except Exception as e:
        print(f"  [FAIL] Schema initialization failed: {e}")
        traceback.print_exc()
        return False


def test_metrics():
    """Test metrics calculations"""
    print("\n\nTesting metrics calculations...")
    print("-" * 80)

    try:
        import numpy as np
        from analytics.metrics import (
            calculate_brier_score,
            calculate_log_loss,
            calculate_sharpe_ratio,
            calculate_max_drawdown,
        )

        # Test data
        predicted_probs = np.array([0.7, 0.6, 0.8, 0.55, 0.9])
        actual_outcomes = np.array([1.0, 0.0, 1.0, 1.0, 1.0])

        # Test Brier score
        brier = calculate_brier_score(predicted_probs, actual_outcomes)
        print(f"  [OK] Brier Score: {brier:.4f}")

        # Test Log Loss
        log_loss = calculate_log_loss(predicted_probs, actual_outcomes)
        print(f"  [OK] Log Loss: {log_loss:.4f}")

        # Test Sharpe ratio
        returns = np.random.normal(0.001, 0.02, 100)
        sharpe = calculate_sharpe_ratio(returns)
        print(f"  [OK] Sharpe Ratio: {sharpe:.2f}")

        # Test Max Drawdown
        equity = 10000 * (1 + returns).cumprod()
        max_dd, _, _ = calculate_max_drawdown(equity)
        print(f"  [OK] Max Drawdown: {abs(max_dd):.2f}%")

        print("\n  [OK] All metrics working correctly!")
        return True

    except Exception as e:
        print(f"  [FAIL] Metrics test failed: {e}")
        traceback.print_exc()
        return False


def test_performance_tracker():
    """Test performance tracker"""
    print("\n\nTesting performance tracker...")
    print("-" * 80)

    try:
        from analytics.performance_tracker import PerformanceTracker

        tracker = PerformanceTracker()

        # Get summary
        summary = tracker.get_performance_summary()
        print(f"  [OK] Performance summary loaded")
        print(f"    Total Predictions: {summary['total_predictions']}")
        print(f"    Settled: {summary['settled_predictions']}")
        print(f"    Accuracy: {summary['accuracy']:.2f}%")

        # Get by confidence
        df_conf = tracker.get_performance_by_confidence()
        print(f"  [OK] Confidence analysis loaded: {len(df_conf)} buckets")

        return True

    except Exception as e:
        print(f"  [FAIL] Performance tracker test failed: {e}")
        traceback.print_exc()
        return False


def test_feature_store():
    """Test feature store"""
    print("\n\nTesting feature store...")
    print("-" * 80)

    try:
        from analytics.feature_store import FeatureStore

        store = FeatureStore()

        # Test storing features
        test_features = {
            'yes_price': 0.65,
            'volume': 1000.0,
            'implied_prob': 0.65,
        }

        success = store.store_features(
            market_id=999999,
            ticker="TEST-SETUP",
            features=test_features,
            feature_version="v1.0",
            feature_set="test"
        )

        if success:
            print("  [OK] Feature storage working")

            # Test retrieval
            retrieved = store.get_features("TEST-SETUP", "v1.0", "test")
            if retrieved:
                print("  [OK] Feature retrieval working")

            # Clean up
            store.delete_features("TEST-SETUP")
            print("  [OK] Feature deletion working")

            return True
        else:
            print("  [FAIL] Feature storage failed")
            return False

    except Exception as e:
        print(f"  [FAIL] Feature store test failed: {e}")
        traceback.print_exc()
        return False


def check_existing_data():
    """Check for existing prediction data"""
    print("\n\nChecking existing data...")
    print("-" * 80)

    try:
        import psycopg2
        db_config = {
            'host': 'localhost',
            'port': '5432',
            'database': 'magnus',
            'user': 'postgres',
            'password': os.getenv('DB_PASSWORD')
        }

        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()

        # Check markets
        cur.execute("SELECT COUNT(*) FROM kalshi_markets")
        market_count = cur.fetchone()[0]
        print(f"  [OK] Markets: {market_count:,}")

        # Check predictions
        cur.execute("SELECT COUNT(*) FROM kalshi_predictions")
        pred_count = cur.fetchone()[0]
        print(f"  [OK] Predictions: {pred_count:,}")

        # Check settled markets
        cur.execute("SELECT COUNT(*) FROM kalshi_markets WHERE status = 'settled'")
        settled_count = cur.fetchone()[0]
        print(f"  [OK] Settled Markets: {settled_count:,}")

        # Check performance records
        cur.execute("SELECT COUNT(*) FROM prediction_performance")
        perf_count = cur.fetchone()[0]
        print(f"  [OK] Performance Records: {perf_count:,}")

        cur.close()
        conn.close()

        if pred_count > 0:
            print("\n  [OK] System has prediction data!")
            if settled_count > 0:
                print("  [OK] System has settled markets - ready for performance tracking!")
            else:
                print("  [INFO] No settled markets yet - waiting for outcomes")
        else:
            print("\n  [INFO] No predictions yet - run AI evaluator first")

        return True

    except Exception as e:
        print(f"  [FAIL] Data check failed: {e}")
        return False


def print_next_steps():
    """Print next steps for user"""
    print("\n\n" + "="*80)
    print("ANALYTICS SYSTEM READY!")
    print("="*80)

    print("\n[CHART] Next Steps:\n")

    print("1. Track Performance (when markets settle):")
    print("   python -c \"from src.analytics.performance_tracker import PerformanceTracker; \\")
    print("              tracker = PerformanceTracker(); \\")
    print("              tracker.update_market_outcome('TICKER', 'yes')\"")

    print("\n2. Run Sample Backtests:")
    print("   python run_sample_backtest.py")

    print("\n3. Launch Dashboard:")
    print("   streamlit run analytics_performance_page.py")
    print("   Then visit: http://localhost:8501")

    print("\n4. View Documentation:")
    print("   Read ANALYTICS_README.md for detailed usage")

    print("\n[DOCS] Key Files:")
    print("   src/analytics/metrics.py           - Performance metrics")
    print("   src/analytics/performance_tracker.py - Track predictions")
    print("   src/analytics/backtest.py          - Backtesting engine")
    print("   src/analytics/feature_store.py     - Feature storage")
    print("   analytics_performance_page.py      - Streamlit dashboard")
    print("   run_sample_backtest.py             - Sample backtests")

    print("\n" + "="*80)


def main():
    """Main setup and verification"""
    print("="*80)
    print("ANALYTICS SYSTEM SETUP")
    print("="*80)

    results = []

    # Run tests
    results.append(("Import Modules", test_imports()))
    results.append(("Database Connection", test_database_connection()))
    results.append(("Initialize Schema", initialize_schema()))
    results.append(("Test Metrics", test_metrics()))
    results.append(("Test Performance Tracker", test_performance_tracker()))
    results.append(("Test Feature Store", test_feature_store()))
    results.append(("Check Existing Data", check_existing_data()))

    # Summary
    print("\n\n" + "="*80)
    print("SETUP SUMMARY")
    print("="*80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "[OK] PASS" if result else "[FAIL] FAIL"
        print(f"  {status:<10} {test_name}")

    print("\n" + "-"*80)
    print(f"  Results: {passed}/{total} tests passed")

    if passed == total:
        print("\n  [OK] All tests passed! System is ready to use.")
        print_next_steps()
        return True
    else:
        print("\n  [FAIL] Some tests failed. Please fix issues above.")
        return False


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        traceback.print_exc()
        sys.exit(1)
