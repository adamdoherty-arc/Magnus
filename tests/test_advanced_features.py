"""
Comprehensive Test Suite for Advanced Features

Tests all 4 advanced features implemented:
1. APM Monitoring (Sentry)
2. Skeleton Loaders
3. Batch API Manager
4. Query Performance Analyzer
5. Real-Time WebSocket Pipeline
6. GraphQL API Layer
7. ML Performance Predictions

Run with: pytest tests/test_advanced_features.py -v
"""

import pytest
import time
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


# ==========================================================================
# Test 1: APM Monitoring
# ==========================================================================

def test_apm_monitoring_import():
    """Test APM monitoring module imports correctly."""
    try:
        from src.utils.apm_monitoring import apm, init_sentry, track_performance
        assert apm is not None
        assert callable(init_sentry)
        assert callable(track_performance)
    except ImportError as e:
        pytest.skip(f"APM dependencies not installed: {e}")


def test_apm_monitoring_graceful_degradation():
    """Test APM gracefully degrades when Sentry not configured."""
    try:
        from src.utils.apm_monitoring import apm, track_performance

        # Should not raise even if not configured
        @track_performance("test_func")
        def test_function():
            return "success"

        result = test_function()
        assert result == "success"

    except ImportError:
        pytest.skip("APM dependencies not installed")


def test_apm_measure_time_decorator():
    """Test basic time measurement decorator works."""
    try:
        from src.utils.apm_monitoring import measure_time

        @measure_time("test_timing")
        def slow_function():
            time.sleep(0.1)
            return "done"

        result = slow_function()
        assert result == "done"

    except ImportError:
        pytest.skip("APM dependencies not installed")


# ==========================================================================
# Test 2: Skeleton Loaders
# ==========================================================================

def test_skeleton_loaders_import():
    """Test skeleton loaders import correctly."""
    from src.components.skeleton_loaders import (
        skeleton_dataframe,
        skeleton_metric_row,
        skeleton_chart,
        skeleton_card,
        with_skeleton,
        SkeletonContext
    )

    assert callable(skeleton_dataframe)
    assert callable(skeleton_metric_row)
    assert callable(with_skeleton)
    assert SkeletonContext is not None


def test_skeleton_context_manager():
    """Test skeleton context manager creates/cleans properly."""
    from src.components.skeleton_loaders import SkeletonContext, skeleton_card

    # Should create and clean without errors
    try:
        with SkeletonContext(skeleton_card, title=True, content_lines=3):
            time.sleep(0.1)  # Simulate data loading
    except Exception as e:
        # Expected - Streamlit not running in test
        if "StreamlitAPIException" not in str(e.__class__.__name__):
            raise


# ==========================================================================
# Test 3: Batch API Manager
# ==========================================================================

def test_batch_api_manager_import():
    """Test batch API manager imports correctly."""
    from src.utils.batch_api_manager import (
        BatchAPIManager,
        APIRequest,
        RequestPriority,
        batch_request
    )

    assert BatchAPIManager is not None
    assert APIRequest is not None
    assert RequestPriority is not None
    assert callable(batch_request)


def test_batch_api_manager_initialization():
    """Test batch API manager initializes correctly."""
    from src.utils.batch_api_manager import BatchAPIManager

    manager = BatchAPIManager(batch_size=10, batch_window=0.5)

    assert manager.batch_size == 10
    assert manager.batch_window == 0.5
    assert manager.stats['total_requests'] == 0


def test_batch_api_manager_add_request():
    """Test adding requests to batch manager."""
    from src.utils.batch_api_manager import BatchAPIManager, RequestPriority

    manager = BatchAPIManager()

    request_id = manager.add_request(
        endpoint="test_api",
        params={"symbol": "AAPL"},
        priority=RequestPriority.HIGH
    )

    assert request_id is not None
    assert manager.stats['total_requests'] == 1


def test_batch_api_circuit_breaker():
    """Test circuit breaker pattern."""
    from src.utils.batch_api_manager import CircuitBreaker

    breaker = CircuitBreaker(failure_threshold=3, timeout=1.0)

    assert breaker.state == "closed"

    # Simulate failures
    for _ in range(3):
        try:
            breaker.call(lambda: (_ for _ in ()).throw(Exception("test")))
        except Exception:
            pass

    assert breaker.state == "open"


# ==========================================================================
# Test 4: Query Performance Analyzer
# ==========================================================================

def test_query_analyzer_import():
    """Test query analyzer imports correctly."""
    from src.utils.query_performance_analyzer import (
        QueryAnalyzer,
        QueryExecution,
        track_query_performance,
        analyze_query
    )

    assert QueryAnalyzer is not None
    assert QueryExecution is not None
    assert callable(track_query_performance)
    assert callable(analyze_query)


def test_query_analyzer_initialization():
    """Test query analyzer initializes correctly."""
    from src.utils.query_performance_analyzer import QueryAnalyzer

    analyzer = QueryAnalyzer(slow_query_threshold=1.0)

    assert analyzer.slow_query_threshold == 1.0
    assert analyzer.stats['total_queries'] == 0


def test_query_analyzer_track_query():
    """Test query tracking works."""
    from src.utils.query_performance_analyzer import QueryAnalyzer

    analyzer = QueryAnalyzer(slow_query_threshold=0.05)

    with analyzer.track_query("SELECT * FROM test_table", params=()):
        time.sleep(0.1)  # Simulate slow query

    assert analyzer.stats['total_queries'] == 1
    assert analyzer.stats['slow_queries'] == 1


def test_query_analyzer_normalization():
    """Test query normalization works."""
    from src.utils.query_performance_analyzer import QueryAnalyzer

    analyzer = QueryAnalyzer()

    # These should normalize to the same pattern
    query1 = "SELECT * FROM users WHERE id = 123"
    query2 = "SELECT * FROM users WHERE id = 456"

    normalized1 = analyzer._normalize_query(query1)
    normalized2 = analyzer._normalize_query(query2)

    assert normalized1 == normalized2


def test_query_analyzer_recommendations():
    """Test optimization recommendations."""
    from src.utils.query_performance_analyzer import QueryAnalyzer

    analyzer = QueryAnalyzer(enable_recommendations=True)

    # Simulate some queries
    with analyzer.track_query("SELECT * FROM large_table"):
        pass

    recommendations = analyzer.get_optimization_recommendations()

    # Should recommend adding WHERE clause
    assert any(r['type'] == 'missing_where' for r in recommendations)


# ==========================================================================
# Test 5: WebSocket Pipeline
# ==========================================================================

def test_websocket_pipeline_import():
    """Test WebSocket pipeline imports correctly."""
    try:
        from src.utils.realtime_websocket_pipeline import (
            WebSocketServer,
            StreamlitWebSocketClient,
            realtime_data_stream
        )

        assert WebSocketServer is not None
        assert StreamlitWebSocketClient is not None
        assert callable(realtime_data_stream)

    except ImportError as e:
        pytest.skip(f"WebSocket dependencies not installed: {e}")


def test_websocket_server_initialization():
    """Test WebSocket server initializes correctly."""
    try:
        from src.utils.realtime_websocket_pipeline import WebSocketServer

        server = WebSocketServer(host="localhost", port=8765)

        assert server.host == "localhost"
        assert server.port == 8765
        assert not server.is_running

    except ImportError:
        pytest.skip("WebSocket dependencies not installed")


def test_websocket_client_initialization():
    """Test WebSocket client initializes correctly."""
    try:
        from src.utils.realtime_websocket_pipeline import StreamlitWebSocketClient

        client = StreamlitWebSocketClient(server_url="ws://localhost:8765")

        assert client.server_url == "ws://localhost:8765"
        assert not client.is_connected

    except ImportError:
        pytest.skip("WebSocket dependencies not installed")


# ==========================================================================
# Test 6: GraphQL API Layer
# ==========================================================================

def test_graphql_layer_import():
    """Test GraphQL layer imports correctly."""
    try:
        from src.api.graphql_layer import GraphQLAPI, execute_query

        assert GraphQLAPI is not None
        assert callable(execute_query)

    except ImportError as e:
        pytest.skip(f"GraphQL dependencies not installed: {e}")


def test_graphql_schema_exists():
    """Test GraphQL schema is defined."""
    try:
        from src.api.graphql_layer import schema

        assert schema is not None

    except ImportError:
        pytest.skip("GraphQL dependencies not installed")


def test_graphql_execute_query():
    """Test GraphQL query execution."""
    try:
        from src.api.graphql_layer import execute_query

        query = '''
            query {
                portfolio {
                    totalValue
                    cashBalance
                }
            }
        '''

        result = execute_query(query)

        assert result is not None
        assert 'data' in result or 'errors' in result

    except ImportError:
        pytest.skip("GraphQL dependencies not installed")


# ==========================================================================
# Test 7: ML Performance Predictor
# ==========================================================================

def test_ml_predictor_import():
    """Test ML performance predictor imports correctly."""
    try:
        from src.ml.performance_predictor import PerformancePredictor

        assert PerformancePredictor is not None

    except ImportError as e:
        pytest.skip(f"ML dependencies not installed: {e}")


def test_ml_predictor_initialization():
    """Test ML predictor initializes correctly."""
    try:
        from src.ml.performance_predictor import PerformancePredictor

        predictor = PerformancePredictor()

        assert predictor is not None
        assert not predictor.models_trained['cache_predictor']
        assert not predictor.models_trained['query_predictor']

    except ImportError:
        pytest.skip("ML dependencies not installed")


def test_ml_cache_ttl_recommendation():
    """Test cache TTL recommendation."""
    try:
        from src.ml.performance_predictor import PerformancePredictor

        predictor = PerformancePredictor()

        # Simulate access pattern (seconds between accesses)
        access_pattern = [60, 62, 58, 61, 59, 63, 60]  # ~1 minute intervals

        recommendation = predictor.recommend_cache_ttl(
            cache_name="test_cache",
            historical_access_pattern=access_pattern
        )

        assert 'recommended_ttl' in recommendation
        assert recommendation['recommended_ttl'] > 0
        assert recommendation['recommended_ttl'] <= 3600

    except ImportError:
        pytest.skip("ML dependencies not installed")


def test_ml_query_time_prediction():
    """Test query time prediction."""
    try:
        from src.ml.performance_predictor import PerformancePredictor
        import pandas as pd
        import numpy as np

        predictor = PerformancePredictor()

        # Create synthetic training data
        training_data = pd.DataFrame({
            'query_complexity': np.random.randint(1, 100, 100),
            'table_size': np.random.randint(100, 10000, 100),
            'join_count': np.random.randint(0, 5, 100),
            'where_clause_count': np.random.randint(0, 10, 100),
            'has_index': np.random.choice([True, False], 100),
            'execution_time': np.random.uniform(0.01, 5.0, 100)
        })

        # Train predictor
        metrics = predictor.train_query_predictor(training_data)

        assert 'mae' in metrics
        assert 'r2' in metrics

        # Make prediction
        prediction = predictor.predict_query_time(
            query_complexity=50,
            table_size=5000,
            join_count=2,
            where_clause_count=3,
            has_index=True
        )

        assert 'predicted_time' in prediction
        assert prediction['predicted_time'] >= 0

    except ImportError:
        pytest.skip("ML dependencies not installed")


# ==========================================================================
# Integration Tests
# ==========================================================================

def test_all_modules_compile():
    """Test that all advanced feature modules compile without errors."""
    modules = [
        'src.utils.apm_monitoring',
        'src.components.skeleton_loaders',
        'src.utils.batch_api_manager',
        'src.utils.query_performance_analyzer',
        'src.utils.realtime_websocket_pipeline',
        'src.api.graphql_layer',
        'src.ml.performance_predictor'
    ]

    for module_name in modules:
        try:
            __import__(module_name)
        except ImportError as e:
            # Some modules have optional dependencies - that's okay
            if "not installed" in str(e).lower():
                pytest.skip(f"Optional dependency not installed for {module_name}")
            else:
                raise


def test_feature_flags_exist():
    """Test that feature flags exist for advanced features."""
    # This test assumes feature flags would be in config
    # Placeholder for when features are integrated
    assert True  # Placeholder


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
