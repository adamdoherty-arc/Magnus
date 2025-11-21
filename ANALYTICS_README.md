# Analytics Pipeline & Backtesting Framework

Comprehensive analytics system for tracking prediction performance and backtesting trading strategies on Kalshi football markets.

## 📊 Overview

This analytics pipeline provides:
- **Performance Tracking**: Monitor prediction accuracy, calibration, and ROI
- **Backtesting**: Simulate trading strategies with Kelly Criterion position sizing
- **Risk Management**: Calculate Sharpe ratio, Sortino ratio, max drawdown
- **Feature Store**: Versioned storage of computed features for ML
- **Streamlit Dashboard**: Interactive visualization and monitoring

## 🏗️ Architecture

```
src/analytics/
├── __init__.py              # Package initialization
├── metrics.py               # Performance metrics (Brier, Sharpe, ROI, etc.)
├── performance_tracker.py   # Track actual outcomes and performance
├── backtest.py             # Backtesting engine with Kelly Criterion
└── feature_store.py        # Versioned feature storage

analytics_performance_page.py  # Streamlit dashboard
run_sample_backtest.py        # Sample backtest script
```

## 📈 Key Metrics

### Calibration Metrics
- **Brier Score**: Measures prediction calibration (0 = perfect, 1 = worst)
- **Log Loss**: Logarithmic loss, heavily penalizes confident wrong predictions
- **ECE**: Expected Calibration Error across probability bins

### Financial Metrics
- **ROI**: Return on Investment percentage
- **P&L**: Profit and Loss in dollars
- **Win Rate**: Percentage of winning trades
- **Profit Factor**: Gross profit / Gross loss

### Risk-Adjusted Metrics
- **Sharpe Ratio**: (Return - Risk-free rate) / Volatility
- **Sortino Ratio**: Return / Downside deviation (only negative returns)
- **Calmar Ratio**: Annualized return / Max drawdown
- **Max Drawdown**: Largest peak-to-trough decline

## 🚀 Quick Start

### 1. Initialize Database Schema

```python
from src.analytics.performance_tracker import PerformanceTracker

# Initialize schema (creates tables)
tracker = PerformanceTracker()
```

Or run SQL directly:
```bash
psql -U postgres -d magnus -f src/analytics_schema.sql
```

### 2. Track Prediction Performance

```python
from src.analytics.performance_tracker import PerformanceTracker

tracker = PerformanceTracker()

# Update actual outcome for a market
tracker.update_market_outcome(ticker="NFL-2024-KC-BUF", actual_outcome="yes")

# Get performance summary
summary = tracker.get_performance_summary()
print(f"Accuracy: {summary['accuracy']:.1f}%")
print(f"Total P&L: ${summary['total_pnl']:.2f}")
print(f"Brier Score: {summary['avg_brier_score']:.4f}")
```

### 3. Run Backtests

```python
from src.analytics.backtest import BacktestEngine, BacktestConfig

# Create backtest configuration
config = BacktestConfig(
    name="Conservative Kelly Strategy",
    initial_capital=10000.0,
    position_sizing="kelly",
    kelly_fraction=0.25,  # Quarter Kelly
    max_position_size=10.0,  # Max 10% of capital per bet
    min_confidence=60.0,
    min_edge=5.0,
)

# Run backtest
engine = BacktestEngine()
results = engine.run_backtest(config)

print(f"Total Return: {results['total_return_pct']:.2f}%")
print(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")
print(f"Max Drawdown: {results['max_drawdown_pct']:.2f}%")
```

### 4. Launch Streamlit Dashboard

```bash
streamlit run analytics_performance_page.py
```

Visit: http://localhost:8501

### 5. Run Sample Backtests

```bash
python run_sample_backtest.py
```

This will run multiple strategies and compare results.

## 📊 Database Schema

### prediction_performance
Stores actual outcomes and performance metrics:
```sql
- prediction_id: Link to kalshi_predictions
- actual_outcome: 'yes' or 'no'
- is_correct: Boolean
- pnl: Profit/Loss
- roi_percent: ROI percentage
- brier_score: Calibration metric
- log_loss: Prediction quality metric
```

### backtest_results
Stores backtesting simulation results:
```sql
- backtest_name: Strategy name
- total_trades: Number of trades
- win_rate: Win percentage
- total_return_pct: Total return
- sharpe_ratio: Risk-adjusted return
- max_drawdown_pct: Maximum drawdown
```

### feature_store
Versioned feature storage:
```sql
- market_id: Market reference
- feature_version: Version (e.g., 'v1.0')
- feature_set: Set name (e.g., 'base', 'advanced')
- features: JSONB with all features
```

## 🎯 Backtesting Strategies

### Position Sizing Methods

1. **Kelly Criterion** (Recommended)
   - Optimal bet size based on edge and odds
   - Kelly % = (edge / odds)
   - Use fractional Kelly (0.25 = quarter Kelly) for safety

2. **Fixed Size**
   - Fixed dollar amount per bet
   - Simple and predictable
   - Good for conservative strategies

3. **Proportional**
   - Fixed percentage of current capital
   - Scales with portfolio size
   - Good for consistent exposure

### Risk Management

- **Max Position Size**: Cap individual bet as % of capital
- **Max Drawdown Limit**: Stop trading if drawdown exceeds threshold
- **Filters**: Min confidence, min edge, price limits

### Sample Strategies

```python
# Conservative Strategy
config = BacktestConfig(
    position_sizing="kelly",
    kelly_fraction=0.25,
    max_position_size=10.0,
    min_confidence=70.0,
    min_edge=8.0
)

# Aggressive Strategy
config = BacktestConfig(
    position_sizing="kelly",
    kelly_fraction=0.5,
    max_position_size=20.0,
    min_confidence=55.0,
    min_edge=3.0
)

# High Confidence Only
config = BacktestConfig(
    position_sizing="fixed",
    fixed_bet_size=200.0,
    min_confidence=80.0,
    min_edge=10.0
)
```

## 📈 Streamlit Dashboard Features

### Tabs

1. **Calibration**
   - Calibration curve (predicted vs actual)
   - Performance by confidence bucket
   - ECE metric

2. **Performance Analysis**
   - Top sectors by P&L
   - Accuracy by sector
   - ROI analysis

3. **Time Series**
   - Cumulative P&L over time
   - Daily accuracy trends
   - Rolling metrics

4. **Best/Worst**
   - Highest P&L predictions
   - Lowest P&L predictions
   - Learning opportunities

5. **Backtesting**
   - Interactive backtest runner
   - Strategy comparison
   - Equity curves

## 🔧 Advanced Usage

### Custom Metrics

```python
from src.analytics.metrics import (
    calculate_brier_score,
    calculate_sharpe_ratio,
    calculate_calibration_metrics
)

# Calculate Brier score
brier = calculate_brier_score(predicted_probs, actual_outcomes)

# Calculate Sharpe ratio
sharpe = calculate_sharpe_ratio(returns, periods_per_year=365)

# Get calibration curve
calibration = calculate_calibration_metrics(
    predicted_probs,
    actual_outcomes,
    n_bins=10
)
print(f"ECE: {calibration['ece']:.4f}")
```

### Feature Store

```python
from src.analytics.feature_store import FeatureStore

store = FeatureStore()

# Store features
features = {
    'yes_price': 0.65,
    'volume': 1000.0,
    'implied_prob': 0.65,
    'log_odds': 0.619,
}

store.store_features(
    market_id=1,
    ticker="NFL-2024-KC-BUF",
    features=features,
    feature_version="v1.0",
    feature_set="base"
)

# Retrieve features
features = store.get_features("NFL-2024-KC-BUF", "v1.0", "base")

# Get as DataFrame for ML training
df = store.get_features_dataframe(
    feature_version="v1.0",
    feature_set="base",
    market_type="nfl"
)
```

### Bulk Performance Tracking

```python
from src.kalshi_db_manager import KalshiDBManager
from src.analytics.performance_tracker import PerformanceTracker

db = KalshiDBManager()
tracker = PerformanceTracker()

# Get settled markets
markets = db.get_connection().execute("""
    SELECT ticker, result
    FROM kalshi_markets
    WHERE status = 'settled' AND result IS NOT NULL
""").fetchall()

# Update outcomes
for ticker, result in markets:
    tracker.update_market_outcome(ticker, result)

print("Performance tracking updated!")
```

## 📊 Performance Benchmarks

Based on 211 historical predictions:

### Expected Metrics (Good Performance)
- **Accuracy**: 55-65% (vs 50% random)
- **Brier Score**: < 0.15 (well-calibrated)
- **Sharpe Ratio**: > 1.0 (good risk-adjusted return)
- **Max Drawdown**: < 20% (acceptable risk)
- **Win Rate**: 50-60%
- **Profit Factor**: > 1.5

### Excellent Performance
- **Accuracy**: > 65%
- **Brier Score**: < 0.10
- **Sharpe Ratio**: > 2.0
- **Max Drawdown**: < 15%
- **Profit Factor**: > 2.0

## 🎓 Interpreting Results

### Calibration
- Well-calibrated predictions have ECE < 0.05
- Calibration curve should be close to diagonal line
- If predictions are overconfident, calibration curve will be below line

### Risk-Adjusted Returns
- Sharpe > 1: Good performance
- Sharpe > 2: Excellent performance
- Sortino is more relevant if you only care about downside risk

### Drawdown
- Max drawdown shows worst-case scenario
- Important for position sizing and risk management
- Lower is better (< 20% is good)

## 🔍 Common Issues

### Issue: No predictions found
**Solution**: Ensure predictions table is populated
```python
from src.kalshi_ai_evaluator import KalshiAIEvaluator
evaluator = KalshiAIEvaluator()
# Generate predictions...
```

### Issue: Database connection error
**Solution**: Check DB_PASSWORD environment variable
```bash
export DB_PASSWORD=your_password
```

### Issue: Empty backtest results
**Solution**: Check filters (min_confidence, min_edge)
```python
# Relax filters
config.min_confidence = 0.0
config.min_edge = 0.0
```

## 📚 References

- **Kelly Criterion**: https://en.wikipedia.org/wiki/Kelly_criterion
- **Brier Score**: https://en.wikipedia.org/wiki/Brier_score
- **Sharpe Ratio**: https://en.wikipedia.org/wiki/Sharpe_ratio
- **Calibration**: https://machinelearningmastery.com/calibrated-classification-model-in-scikit-learn/

## 🤝 Integration

### With Existing Dashboard
```python
# Add to dashboard.py
from analytics_performance_page import main as analytics_main

# Create new tab
with tab_analytics:
    analytics_main()
```

### With Telegram Bot
```python
from src.analytics.performance_tracker import PerformanceTracker

tracker = PerformanceTracker()
summary = tracker.get_performance_summary()

# Send to Telegram
bot.send_message(f"""
📊 Performance Update
Accuracy: {summary['accuracy']:.1f}%
P&L: ${summary['total_pnl']:.2f}
Sharpe: {summary['sharpe_ratio']:.2f}
""")
```

## 📊 Production Deployment

1. **Initialize schema** in production database
2. **Schedule backtest runs** (weekly/monthly)
3. **Monitor key metrics** via Streamlit dashboard
4. **Set up alerts** for performance degradation
5. **Regular calibration checks** to ensure prediction quality

## 🚀 Next Steps

1. Run sample backtests to understand strategies
2. Track actual outcomes as markets settle
3. Monitor calibration and adjust models
4. Experiment with position sizing
5. Integrate with live trading system (with caution!)

---

**Created by**: Python Pro Agent
**Date**: 2025-11-09
**Version**: 1.0.0

For questions or issues, check the code comments or database schema documentation.
