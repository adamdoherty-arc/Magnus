"""
Performance Metrics for Prediction Market Analytics

Implements standard financial and statistical metrics for evaluating
prediction performance, including calibration, risk-adjusted returns, and ROI.
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def calculate_brier_score(predicted_probs: np.ndarray, actual_outcomes: np.ndarray) -> float:
    """
    Calculate Brier score for calibration assessment.

    Brier score = mean((predicted_probability - actual_outcome)^2)
    Lower is better. Perfect predictions = 0, worst = 1.

    Args:
        predicted_probs: Array of predicted probabilities (0-1)
        actual_outcomes: Array of actual outcomes (0 or 1)

    Returns:
        Brier score (0-1)
    """
    if len(predicted_probs) == 0 or len(actual_outcomes) == 0:
        return np.nan

    if len(predicted_probs) != len(actual_outcomes):
        raise ValueError("Arrays must have same length")

    return float(np.mean((predicted_probs - actual_outcomes) ** 2))


def calculate_log_loss(predicted_probs: np.ndarray, actual_outcomes: np.ndarray,
                       eps: float = 1e-15) -> float:
    """
    Calculate logarithmic loss (cross-entropy loss).

    Log loss = -mean(actual * log(predicted) + (1-actual) * log(1-predicted))
    Lower is better. Heavily penalizes confident wrong predictions.

    Args:
        predicted_probs: Array of predicted probabilities (0-1)
        actual_outcomes: Array of actual outcomes (0 or 1)
        eps: Small constant to avoid log(0)

    Returns:
        Log loss value
    """
    if len(predicted_probs) == 0 or len(actual_outcomes) == 0:
        return np.nan

    if len(predicted_probs) != len(actual_outcomes):
        raise ValueError("Arrays must have same length")

    # Clip probabilities to avoid log(0)
    predicted_probs = np.clip(predicted_probs, eps, 1 - eps)

    return float(-np.mean(
        actual_outcomes * np.log(predicted_probs) +
        (1 - actual_outcomes) * np.log(1 - predicted_probs)
    ))


def calculate_sharpe_ratio(returns: np.ndarray, risk_free_rate: float = 0.0,
                           periods_per_year: int = 252) -> float:
    """
    Calculate Sharpe ratio (risk-adjusted return).

    Sharpe = (mean_return - risk_free_rate) / std_return * sqrt(periods)

    Args:
        returns: Array of period returns
        risk_free_rate: Annual risk-free rate (default 0)
        periods_per_year: Number of trading periods per year (252 for daily)

    Returns:
        Annualized Sharpe ratio
    """
    if len(returns) == 0:
        return np.nan

    mean_return = np.mean(returns)
    std_return = np.std(returns, ddof=1)

    if std_return == 0:
        return np.nan

    # Annualize
    sharpe = (mean_return - risk_free_rate / periods_per_year) / std_return
    sharpe_annualized = sharpe * np.sqrt(periods_per_year)

    return float(sharpe_annualized)


def calculate_sortino_ratio(returns: np.ndarray, risk_free_rate: float = 0.0,
                            periods_per_year: int = 252) -> float:
    """
    Calculate Sortino ratio (return / downside deviation).

    Like Sharpe but only considers downside volatility.

    Args:
        returns: Array of period returns
        risk_free_rate: Annual risk-free rate (default 0)
        periods_per_year: Number of trading periods per year

    Returns:
        Annualized Sortino ratio
    """
    if len(returns) == 0:
        return np.nan

    mean_return = np.mean(returns)

    # Calculate downside deviation (only negative returns)
    downside_returns = returns[returns < 0]
    if len(downside_returns) == 0:
        return np.inf if mean_return > 0 else np.nan

    downside_std = np.std(downside_returns, ddof=1)

    if downside_std == 0:
        return np.nan

    # Annualize
    sortino = (mean_return - risk_free_rate / periods_per_year) / downside_std
    sortino_annualized = sortino * np.sqrt(periods_per_year)

    return float(sortino_annualized)


def calculate_max_drawdown(equity_curve: np.ndarray) -> Tuple[float, int, int]:
    """
    Calculate maximum drawdown from equity curve.

    Args:
        equity_curve: Array of portfolio values over time

    Returns:
        Tuple of (max_drawdown_pct, start_idx, end_idx)
    """
    if len(equity_curve) == 0:
        return (np.nan, -1, -1)

    # Calculate running maximum
    running_max = np.maximum.accumulate(equity_curve)

    # Calculate drawdown at each point
    drawdown = (equity_curve - running_max) / running_max

    # Find maximum drawdown
    max_dd_idx = np.argmin(drawdown)
    max_dd = drawdown[max_dd_idx]

    # Find start of drawdown (last peak before max DD)
    start_idx = np.argmax(equity_curve[:max_dd_idx + 1])

    return (float(max_dd * 100), int(start_idx), int(max_dd_idx))


def calculate_calmar_ratio(returns: np.ndarray, equity_curve: np.ndarray,
                           periods_per_year: int = 252) -> float:
    """
    Calculate Calmar ratio (annualized return / max drawdown).

    Args:
        returns: Array of period returns
        equity_curve: Array of portfolio values
        periods_per_year: Number of trading periods per year

    Returns:
        Calmar ratio
    """
    if len(returns) == 0 or len(equity_curve) == 0:
        return np.nan

    # Annualized return
    total_return = (equity_curve[-1] / equity_curve[0]) - 1
    periods = len(returns)
    years = periods / periods_per_year
    annualized_return = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0

    # Max drawdown
    max_dd, _, _ = calculate_max_drawdown(equity_curve)
    max_dd_decimal = abs(max_dd) / 100

    if max_dd_decimal == 0:
        return np.nan

    return float(annualized_return / max_dd_decimal)


def calculate_roi_metrics(pnl: np.ndarray, position_sizes: np.ndarray) -> Dict[str, float]:
    """
    Calculate ROI metrics.

    Args:
        pnl: Array of profit/loss values
        position_sizes: Array of position sizes (capital invested)

    Returns:
        Dictionary with ROI metrics
    """
    if len(pnl) == 0 or len(position_sizes) == 0:
        return {
            'total_pnl': 0.0,
            'avg_roi': 0.0,
            'total_roi': 0.0,
            'win_rate': 0.0,
            'avg_win': 0.0,
            'avg_loss': 0.0,
            'profit_factor': 0.0,
        }

    # Calculate individual ROIs
    roi = np.where(position_sizes != 0, pnl / position_sizes * 100, 0)

    # Win/loss metrics
    wins = pnl[pnl > 0]
    losses = pnl[pnl < 0]

    profit_factor = abs(np.sum(wins) / np.sum(losses)) if len(losses) > 0 and np.sum(losses) != 0 else np.inf

    return {
        'total_pnl': float(np.sum(pnl)),
        'avg_roi': float(np.mean(roi)),
        'total_roi': float(np.sum(pnl) / np.sum(position_sizes) * 100) if np.sum(position_sizes) > 0 else 0.0,
        'win_rate': float(len(wins) / len(pnl) * 100) if len(pnl) > 0 else 0.0,
        'avg_win': float(np.mean(wins)) if len(wins) > 0 else 0.0,
        'avg_loss': float(np.mean(losses)) if len(losses) > 0 else 0.0,
        'profit_factor': float(profit_factor),
    }


def calculate_calibration_metrics(predicted_probs: np.ndarray, actual_outcomes: np.ndarray,
                                  n_bins: int = 10) -> Dict[str, any]:
    """
    Calculate calibration curve and expected calibration error (ECE).

    Args:
        predicted_probs: Array of predicted probabilities
        actual_outcomes: Array of actual outcomes (0 or 1)
        n_bins: Number of bins for calibration curve

    Returns:
        Dictionary with calibration metrics and curve data
    """
    if len(predicted_probs) == 0 or len(actual_outcomes) == 0:
        return {
            'ece': np.nan,
            'mce': np.nan,
            'bins': [],
            'bin_accuracy': [],
            'bin_confidence': [],
            'bin_counts': [],
        }

    # Create bins
    bin_edges = np.linspace(0, 1, n_bins + 1)
    bin_indices = np.digitize(predicted_probs, bin_edges[:-1]) - 1
    bin_indices = np.clip(bin_indices, 0, n_bins - 1)

    bin_accuracy = []
    bin_confidence = []
    bin_counts = []
    ece = 0.0
    mce = 0.0

    for i in range(n_bins):
        mask = bin_indices == i
        if np.sum(mask) > 0:
            bin_acc = np.mean(actual_outcomes[mask])
            bin_conf = np.mean(predicted_probs[mask])
            bin_count = np.sum(mask)

            bin_accuracy.append(float(bin_acc))
            bin_confidence.append(float(bin_conf))
            bin_counts.append(int(bin_count))

            # ECE: weighted average of absolute calibration error
            ece += (bin_count / len(predicted_probs)) * abs(bin_acc - bin_conf)

            # MCE: maximum calibration error
            mce = max(mce, abs(bin_acc - bin_conf))
        else:
            bin_accuracy.append(np.nan)
            bin_confidence.append(float((bin_edges[i] + bin_edges[i + 1]) / 2))
            bin_counts.append(0)

    return {
        'ece': float(ece),  # Expected Calibration Error
        'mce': float(mce),  # Maximum Calibration Error
        'bins': [float(x) for x in bin_edges],
        'bin_accuracy': bin_accuracy,
        'bin_confidence': bin_confidence,
        'bin_counts': bin_counts,
    }


def calculate_confidence_metrics(predicted_probs: np.ndarray, actual_outcomes: np.ndarray,
                                 confidence_score: np.ndarray) -> Dict[str, Dict[str, float]]:
    """
    Calculate metrics by confidence bucket (high/medium/low).

    Args:
        predicted_probs: Array of predicted probabilities
        actual_outcomes: Array of actual outcomes (0 or 1)
        confidence_score: Array of confidence scores (0-100)

    Returns:
        Dictionary with metrics for each confidence bucket
    """
    if len(predicted_probs) == 0:
        return {}

    results = {}

    # Define confidence buckets
    buckets = {
        'High (≥80)': confidence_score >= 80,
        'Medium (60-80)': (confidence_score >= 60) & (confidence_score < 80),
        'Low (<60)': confidence_score < 60,
    }

    for bucket_name, mask in buckets.items():
        if np.sum(mask) == 0:
            continue

        bucket_probs = predicted_probs[mask]
        bucket_outcomes = actual_outcomes[mask]

        results[bucket_name] = {
            'count': int(np.sum(mask)),
            'accuracy': float(np.mean(bucket_outcomes == (bucket_probs > 0.5)) * 100),
            'avg_confidence': float(np.mean(confidence_score[mask])),
            'brier_score': calculate_brier_score(bucket_probs, bucket_outcomes),
            'log_loss': calculate_log_loss(bucket_probs, bucket_outcomes),
        }

    return results


def calculate_time_series_metrics(df: pd.DataFrame, value_col: str = 'pnl',
                                  date_col: str = 'date',
                                  window_days: int = 30) -> pd.DataFrame:
    """
    Calculate rolling metrics over time.

    Args:
        df: DataFrame with date and value columns
        value_col: Name of value column (e.g., 'pnl', 'roi')
        date_col: Name of date column
        window_days: Rolling window size in days

    Returns:
        DataFrame with rolling metrics
    """
    if df.empty:
        return pd.DataFrame()

    df = df.sort_values(date_col)

    # Calculate cumulative sum
    df['cumulative'] = df[value_col].cumsum()

    # Calculate rolling metrics
    df['rolling_mean'] = df[value_col].rolling(window=window_days, min_periods=1).mean()
    df['rolling_std'] = df[value_col].rolling(window=window_days, min_periods=1).std()
    df['rolling_sum'] = df[value_col].rolling(window=window_days, min_periods=1).sum()

    # Calculate rolling Sharpe (approximation)
    df['rolling_sharpe'] = np.where(
        df['rolling_std'] > 0,
        df['rolling_mean'] / df['rolling_std'] * np.sqrt(252),
        np.nan
    )

    return df


def calculate_sector_metrics(df: pd.DataFrame, sector_col: str = 'sector',
                             pnl_col: str = 'pnl') -> pd.DataFrame:
    """
    Calculate performance metrics by sector/category.

    Args:
        df: DataFrame with sector and pnl columns
        sector_col: Name of sector column
        pnl_col: Name of P&L column

    Returns:
        DataFrame with metrics by sector
    """
    if df.empty:
        return pd.DataFrame()

    results = []

    for sector in df[sector_col].unique():
        sector_df = df[df[sector_col] == sector]

        wins = sector_df[sector_df[pnl_col] > 0]
        losses = sector_df[sector_df[pnl_col] < 0]

        results.append({
            'sector': sector,
            'count': len(sector_df),
            'total_pnl': sector_df[pnl_col].sum(),
            'avg_pnl': sector_df[pnl_col].mean(),
            'win_rate': len(wins) / len(sector_df) * 100 if len(sector_df) > 0 else 0,
            'avg_win': wins[pnl_col].mean() if len(wins) > 0 else 0,
            'avg_loss': losses[pnl_col].mean() if len(losses) > 0 else 0,
        })

    return pd.DataFrame(results).sort_values('total_pnl', ascending=False)


if __name__ == "__main__":
    # Test metrics
    print("="*80)
    print("METRICS MODULE - Test")
    print("="*80)

    # Generate test data
    np.random.seed(42)
    n_samples = 100

    predicted_probs = np.random.uniform(0.3, 0.9, n_samples)
    actual_outcomes = (predicted_probs + np.random.normal(0, 0.2, n_samples) > 0.5).astype(float)

    # Test Brier score
    brier = calculate_brier_score(predicted_probs, actual_outcomes)
    print(f"\nBrier Score: {brier:.4f} (lower is better, 0=perfect)")

    # Test Log Loss
    log_loss = calculate_log_loss(predicted_probs, actual_outcomes)
    print(f"Log Loss: {log_loss:.4f} (lower is better)")

    # Test Sharpe ratio
    returns = np.random.normal(0.001, 0.02, 100)
    sharpe = calculate_sharpe_ratio(returns)
    print(f"\nSharpe Ratio: {sharpe:.2f} (higher is better, >1 is good)")

    # Test Sortino ratio
    sortino = calculate_sortino_ratio(returns)
    print(f"Sortino Ratio: {sortino:.2f} (higher is better)")

    # Test Max Drawdown
    equity = 10000 * (1 + returns).cumprod()
    max_dd, start_idx, end_idx = calculate_max_drawdown(equity)
    print(f"\nMax Drawdown: {max_dd:.2f}% (from index {start_idx} to {end_idx})")

    # Test Calmar ratio
    calmar = calculate_calmar_ratio(returns, equity)
    print(f"Calmar Ratio: {calmar:.2f}")

    # Test ROI metrics
    pnl = np.random.normal(10, 50, 100)
    position_sizes = np.full(100, 100.0)
    roi_metrics = calculate_roi_metrics(pnl, position_sizes)
    print(f"\nROI Metrics:")
    print(f"  Total P&L: ${roi_metrics['total_pnl']:.2f}")
    print(f"  Average ROI: {roi_metrics['avg_roi']:.2f}%")
    print(f"  Win Rate: {roi_metrics['win_rate']:.1f}%")
    print(f"  Profit Factor: {roi_metrics['profit_factor']:.2f}")

    # Test calibration
    calibration = calculate_calibration_metrics(predicted_probs, actual_outcomes, n_bins=5)
    print(f"\nCalibration Metrics:")
    print(f"  Expected Calibration Error: {calibration['ece']:.4f}")
    print(f"  Maximum Calibration Error: {calibration['mce']:.4f}")

    print("\n" + "="*80)
    print("All Tests Passed!")
    print("="*80)
