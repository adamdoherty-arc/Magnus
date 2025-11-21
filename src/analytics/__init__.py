"""
Analytics Package for Kalshi Prediction Markets

Provides comprehensive performance tracking, backtesting, and feature management.

Modules:
    - metrics: Performance metrics (Brier, Sharpe, ROI, etc.)
    - performance_tracker: Track prediction performance and outcomes
    - backtest: Backtesting framework with Kelly criterion
    - feature_store: Versioned feature storage for ML
"""

from .metrics import (
    calculate_brier_score,
    calculate_log_loss,
    calculate_sharpe_ratio,
    calculate_sortino_ratio,
    calculate_max_drawdown,
    calculate_calmar_ratio,
    calculate_roi_metrics,
    calculate_calibration_metrics
)

from .performance_tracker import PerformanceTracker
from .backtest import BacktestEngine, BacktestConfig
from .feature_store import FeatureStore

__version__ = "1.0.0"

__all__ = [
    # Metrics
    'calculate_brier_score',
    'calculate_log_loss',
    'calculate_sharpe_ratio',
    'calculate_sortino_ratio',
    'calculate_max_drawdown',
    'calculate_calmar_ratio',
    'calculate_roi_metrics',
    'calculate_calibration_metrics',

    # Classes
    'PerformanceTracker',
    'BacktestEngine',
    'BacktestConfig',
    'FeatureStore',
]
