-- ============================================================================
-- Analytics and Backtesting Schema
-- ============================================================================
-- Purpose: Track prediction performance, backtesting results, and feature store
-- Database: magnus (PostgreSQL)
-- Created: 2025-11-09
-- ============================================================================

-- ============================================================================
-- Table 1: prediction_performance
-- ============================================================================
-- Tracks actual outcomes and performance metrics for predictions
-- ============================================================================

CREATE TABLE IF NOT EXISTS prediction_performance (
    id SERIAL PRIMARY KEY,
    prediction_id INTEGER NOT NULL,
    market_id INTEGER NOT NULL,
    ticker VARCHAR(100) NOT NULL,

    -- Prediction details
    predicted_outcome VARCHAR(10) NOT NULL,
    confidence_score DECIMAL(5,2),
    predicted_probability DECIMAL(5,4), -- Our estimated probability
    market_price DECIMAL(5,4), -- Price when prediction was made

    -- Actual outcome
    actual_outcome VARCHAR(10), -- 'yes', 'no', NULL if not settled
    is_correct BOOLEAN, -- True if prediction matched outcome
    settled_at TIMESTAMP WITH TIME ZONE,

    -- Financial metrics
    bet_size DECIMAL(10,2), -- Amount bet (if any)
    pnl DECIMAL(10,2), -- Profit/Loss
    roi_percent DECIMAL(8,2), -- Return on investment %

    -- Performance metrics
    brier_score DECIMAL(8,6), -- Calibration metric (0=perfect, 1=worst)
    log_loss DECIMAL(10,6), -- Logarithmic loss

    -- Context
    market_type VARCHAR(50), -- 'nfl', 'college'
    sector VARCHAR(100), -- Team, division, conference
    time_to_close_hours INTEGER, -- Hours until close when predicted

    -- Timestamps
    predicted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT chk_perf_predicted_outcome CHECK (predicted_outcome IN ('yes', 'no')),
    CONSTRAINT chk_perf_actual_outcome CHECK (actual_outcome IN ('yes', 'no', NULL)),
    CONSTRAINT chk_perf_probability CHECK (predicted_probability >= 0 AND predicted_probability <= 1)
);

COMMENT ON TABLE prediction_performance IS 'Tracks actual outcomes and performance metrics for AI predictions';
COMMENT ON COLUMN prediction_performance.brier_score IS 'Calibration metric: (predicted_prob - actual)^2';
COMMENT ON COLUMN prediction_performance.log_loss IS 'Logarithmic loss: -log(prob of correct outcome)';

CREATE INDEX IF NOT EXISTS idx_perf_market ON prediction_performance(market_id);
CREATE INDEX IF NOT EXISTS idx_perf_prediction ON prediction_performance(prediction_id);
CREATE INDEX IF NOT EXISTS idx_perf_ticker ON prediction_performance(ticker);
CREATE INDEX IF NOT EXISTS idx_perf_outcome ON prediction_performance(actual_outcome);
CREATE INDEX IF NOT EXISTS idx_perf_settled ON prediction_performance(settled_at);
CREATE INDEX IF NOT EXISTS idx_perf_market_type ON prediction_performance(market_type);
CREATE INDEX IF NOT EXISTS idx_perf_sector ON prediction_performance(sector);

-- ============================================================================
-- Table 2: feature_store
-- ============================================================================
-- Stores computed features with versioning for ML training and predictions
-- ============================================================================

CREATE TABLE IF NOT EXISTS feature_store (
    id SERIAL PRIMARY KEY,
    market_id INTEGER NOT NULL,
    ticker VARCHAR(100) NOT NULL,

    -- Feature version control
    feature_version VARCHAR(50) NOT NULL, -- e.g., 'v1.0', 'v2.0'
    feature_set VARCHAR(100) NOT NULL, -- e.g., 'base', 'advanced', 'ensemble'

    -- Features (JSONB for flexibility)
    features JSONB NOT NULL, -- All computed features as JSON

    -- Feature metadata
    feature_names TEXT[], -- Array of feature names
    feature_count INTEGER, -- Number of features

    -- Market context (for fast filtering)
    market_type VARCHAR(50),
    close_time TIMESTAMP WITH TIME ZONE,

    -- Timestamps
    computed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Unique constraint: one feature set per market per version
    CONSTRAINT uq_feature_store UNIQUE (market_id, feature_version, feature_set)
);

COMMENT ON TABLE feature_store IS 'Versioned feature storage for ML training and predictions';
COMMENT ON COLUMN feature_store.features IS 'All computed features stored as JSONB for flexibility';
COMMENT ON COLUMN feature_store.feature_version IS 'Version of feature computation logic';

CREATE INDEX IF NOT EXISTS idx_feature_market ON feature_store(market_id);
CREATE INDEX IF NOT EXISTS idx_feature_ticker ON feature_store(ticker);
CREATE INDEX IF NOT EXISTS idx_feature_version ON feature_store(feature_version);
CREATE INDEX IF NOT EXISTS idx_feature_set ON feature_store(feature_set);
CREATE INDEX IF NOT EXISTS idx_feature_computed ON feature_store(computed_at);
CREATE INDEX IF NOT EXISTS idx_feature_type ON feature_store(market_type);

-- GIN index for JSONB queries
CREATE INDEX IF NOT EXISTS idx_feature_features_gin ON feature_store USING GIN(features);

-- ============================================================================
-- Table 3: backtest_results
-- ============================================================================
-- Stores backtesting simulation results for different strategies
-- ============================================================================

CREATE TABLE IF NOT EXISTS backtest_results (
    id SERIAL PRIMARY KEY,

    -- Backtest configuration
    backtest_name VARCHAR(200) NOT NULL,
    strategy_name VARCHAR(100) NOT NULL,
    version VARCHAR(50) NOT NULL,

    -- Time period
    start_date TIMESTAMP WITH TIME ZONE NOT NULL,
    end_date TIMESTAMP WITH TIME ZONE NOT NULL,

    -- Configuration
    initial_capital DECIMAL(12,2) NOT NULL,
    position_sizing VARCHAR(50), -- 'kelly', 'fixed', 'proportional'
    kelly_fraction DECIMAL(5,3), -- e.g., 0.25 for quarter Kelly
    max_position_size DECIMAL(5,2), -- Max % of capital per bet
    max_drawdown_limit DECIMAL(5,2), -- Stop trading if DD exceeds this

    -- Filters applied
    min_confidence DECIMAL(5,2),
    min_edge DECIMAL(5,2),
    market_types TEXT[], -- ['nfl', 'college']

    -- Overall performance metrics
    total_trades INTEGER DEFAULT 0,
    winning_trades INTEGER DEFAULT 0,
    losing_trades INTEGER DEFAULT 0,
    win_rate DECIMAL(5,2), -- Percentage

    -- Financial metrics
    final_capital DECIMAL(12,2),
    total_pnl DECIMAL(12,2),
    total_return_pct DECIMAL(8,2),

    -- Risk-adjusted metrics
    sharpe_ratio DECIMAL(8,4),
    sortino_ratio DECIMAL(8,4),
    calmar_ratio DECIMAL(8,4),
    max_drawdown_pct DECIMAL(8,2),
    max_drawdown_amount DECIMAL(12,2),

    -- Additional metrics
    avg_trade_pnl DECIMAL(10,2),
    avg_win_amount DECIMAL(10,2),
    avg_loss_amount DECIMAL(10,2),
    profit_factor DECIMAL(8,4), -- Gross profit / Gross loss

    -- Calibration metrics
    avg_brier_score DECIMAL(8,6),
    avg_log_loss DECIMAL(10,6),

    -- Timestamps
    executed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT chk_backtest_dates CHECK (end_date > start_date),
    CONSTRAINT chk_backtest_capital CHECK (initial_capital > 0)
);

COMMENT ON TABLE backtest_results IS 'Stores backtesting simulation results for strategy evaluation';
COMMENT ON COLUMN backtest_results.sharpe_ratio IS 'Risk-adjusted return: (mean return - risk-free rate) / std dev';
COMMENT ON COLUMN backtest_results.sortino_ratio IS 'Return / downside deviation (only negative returns)';
COMMENT ON COLUMN backtest_results.calmar_ratio IS 'Annualized return / max drawdown';

CREATE INDEX IF NOT EXISTS idx_backtest_name ON backtest_results(backtest_name);
CREATE INDEX IF NOT EXISTS idx_backtest_strategy ON backtest_results(strategy_name);
CREATE INDEX IF NOT EXISTS idx_backtest_dates ON backtest_results(start_date, end_date);
CREATE INDEX IF NOT EXISTS idx_backtest_executed ON backtest_results(executed_at DESC);

-- ============================================================================
-- Table 4: backtest_trades
-- ============================================================================
-- Individual trades from backtesting simulations
-- ============================================================================

CREATE TABLE IF NOT EXISTS backtest_trades (
    id SERIAL PRIMARY KEY,
    backtest_id INTEGER NOT NULL,

    -- Market info
    market_id INTEGER,
    ticker VARCHAR(100) NOT NULL,
    market_type VARCHAR(50),

    -- Trade details
    prediction_outcome VARCHAR(10) NOT NULL,
    confidence_score DECIMAL(5,2),
    edge_percentage DECIMAL(5,2),
    entry_price DECIMAL(5,4),

    -- Position sizing
    position_size DECIMAL(10,2),
    position_pct DECIMAL(5,2), -- % of capital

    -- Outcome
    actual_outcome VARCHAR(10),
    is_win BOOLEAN,
    pnl DECIMAL(10,2),
    roi_pct DECIMAL(8,2),

    -- Timing
    trade_date TIMESTAMP WITH TIME ZONE,
    settlement_date TIMESTAMP WITH TIME ZONE,

    -- Portfolio state
    capital_before DECIMAL(12,2),
    capital_after DECIMAL(12,2),

    CONSTRAINT chk_bt_trade_prediction CHECK (prediction_outcome IN ('yes', 'no')),
    CONSTRAINT chk_bt_trade_actual CHECK (actual_outcome IN ('yes', 'no', NULL))
);

COMMENT ON TABLE backtest_trades IS 'Individual trades from backtesting simulations';

CREATE INDEX IF NOT EXISTS idx_bt_trade_backtest ON backtest_trades(backtest_id);
CREATE INDEX IF NOT EXISTS idx_bt_trade_market ON backtest_trades(market_id);
CREATE INDEX IF NOT EXISTS idx_bt_trade_date ON backtest_trades(trade_date);
CREATE INDEX IF NOT EXISTS idx_bt_trade_outcome ON backtest_trades(is_win);

-- ============================================================================
-- Table 5: performance_snapshots
-- ============================================================================
-- Rolling performance metrics over time
-- ============================================================================

CREATE TABLE IF NOT EXISTS performance_snapshots (
    id SERIAL PRIMARY KEY,

    -- Time window
    snapshot_date DATE NOT NULL,
    window_days INTEGER NOT NULL, -- 7, 30, 90, etc.

    -- Market filters
    market_type VARCHAR(50), -- 'nfl', 'college', 'all'

    -- Prediction metrics
    total_predictions INTEGER DEFAULT 0,
    settled_predictions INTEGER DEFAULT 0,
    correct_predictions INTEGER DEFAULT 0,
    accuracy DECIMAL(5,2),

    -- Financial metrics
    total_pnl DECIMAL(12,2),
    avg_roi DECIMAL(8,2),

    -- Risk metrics
    sharpe_ratio DECIMAL(8,4),
    max_drawdown_pct DECIMAL(8,2),

    -- Calibration
    avg_brier_score DECIMAL(8,6),
    avg_log_loss DECIMAL(10,6),

    -- Confidence buckets
    high_conf_accuracy DECIMAL(5,2), -- Accuracy for confidence > 80
    med_conf_accuracy DECIMAL(5,2), -- Accuracy for confidence 60-80
    low_conf_accuracy DECIMAL(5,2), -- Accuracy for confidence < 60

    -- Timestamps
    computed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT uq_snapshot UNIQUE (snapshot_date, window_days, market_type)
);

COMMENT ON TABLE performance_snapshots IS 'Rolling performance metrics computed daily';

CREATE INDEX IF NOT EXISTS idx_snapshot_date ON performance_snapshots(snapshot_date DESC);
CREATE INDEX IF NOT EXISTS idx_snapshot_window ON performance_snapshots(window_days);
CREATE INDEX IF NOT EXISTS idx_snapshot_type ON performance_snapshots(market_type);

-- ============================================================================
-- Views for Analytics
-- ============================================================================

-- View: Overall performance summary
CREATE OR REPLACE VIEW v_performance_summary AS
SELECT
    COUNT(*) as total_predictions,
    COUNT(actual_outcome) as settled_predictions,
    COUNT(CASE WHEN is_correct = TRUE THEN 1 END) as correct_predictions,
    ROUND(100.0 * COUNT(CASE WHEN is_correct = TRUE THEN 1 END) /
          NULLIF(COUNT(actual_outcome), 0), 2) as accuracy_pct,
    SUM(pnl) as total_pnl,
    AVG(roi_percent) as avg_roi,
    AVG(brier_score) as avg_brier_score,
    AVG(log_loss) as avg_log_loss,
    MIN(predicted_at) as first_prediction,
    MAX(predicted_at) as last_prediction
FROM prediction_performance
WHERE actual_outcome IS NOT NULL;

COMMENT ON VIEW v_performance_summary IS 'Overall prediction performance metrics';

-- View: Performance by market type
CREATE OR REPLACE VIEW v_performance_by_type AS
SELECT
    market_type,
    COUNT(*) as total_predictions,
    COUNT(actual_outcome) as settled_predictions,
    COUNT(CASE WHEN is_correct = TRUE THEN 1 END) as correct_predictions,
    ROUND(100.0 * COUNT(CASE WHEN is_correct = TRUE THEN 1 END) /
          NULLIF(COUNT(actual_outcome), 0), 2) as accuracy_pct,
    SUM(pnl) as total_pnl,
    AVG(roi_percent) as avg_roi,
    AVG(brier_score) as avg_brier_score
FROM prediction_performance
WHERE actual_outcome IS NOT NULL
GROUP BY market_type
ORDER BY accuracy_pct DESC;

COMMENT ON VIEW v_performance_by_type IS 'Performance metrics grouped by market type';

-- View: Performance by confidence level
CREATE OR REPLACE VIEW v_performance_by_confidence AS
SELECT
    CASE
        WHEN confidence_score >= 80 THEN 'High (80+)'
        WHEN confidence_score >= 60 THEN 'Medium (60-80)'
        ELSE 'Low (<60)'
    END as confidence_bucket,
    COUNT(*) as total_predictions,
    COUNT(actual_outcome) as settled_predictions,
    COUNT(CASE WHEN is_correct = TRUE THEN 1 END) as correct_predictions,
    ROUND(100.0 * COUNT(CASE WHEN is_correct = TRUE THEN 1 END) /
          NULLIF(COUNT(actual_outcome), 0), 2) as accuracy_pct,
    AVG(confidence_score) as avg_confidence,
    AVG(brier_score) as avg_brier_score
FROM prediction_performance
WHERE actual_outcome IS NOT NULL
GROUP BY confidence_bucket
ORDER BY avg_confidence DESC;

COMMENT ON VIEW v_performance_by_confidence IS 'Performance metrics grouped by confidence level';

-- View: Recent performance (last 30 days)
CREATE OR REPLACE VIEW v_recent_performance AS
SELECT
    DATE(predicted_at) as prediction_date,
    COUNT(*) as predictions,
    COUNT(actual_outcome) as settled,
    COUNT(CASE WHEN is_correct = TRUE THEN 1 END) as correct,
    ROUND(100.0 * COUNT(CASE WHEN is_correct = TRUE THEN 1 END) /
          NULLIF(COUNT(actual_outcome), 0), 2) as accuracy_pct,
    SUM(pnl) as daily_pnl
FROM prediction_performance
WHERE predicted_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE(predicted_at)
ORDER BY prediction_date DESC;

COMMENT ON VIEW v_recent_performance IS 'Daily performance metrics for last 30 days';

-- ============================================================================
-- Sample Queries
-- ============================================================================

-- Get overall performance summary
-- SELECT * FROM v_performance_summary;

-- Get performance by market type
-- SELECT * FROM v_performance_by_type;

-- Get best performing sectors
-- SELECT sector, COUNT(*) as trades, AVG(roi_percent) as avg_roi
-- FROM prediction_performance
-- WHERE actual_outcome IS NOT NULL
-- GROUP BY sector
-- ORDER BY avg_roi DESC;

-- Get calibration analysis (predicted vs actual)
-- SELECT
--     ROUND(predicted_probability * 10) / 10 as prob_bucket,
--     COUNT(*) as predictions,
--     AVG(CASE WHEN actual_outcome = predicted_outcome THEN 1 ELSE 0 END) as actual_rate
-- FROM prediction_performance
-- WHERE actual_outcome IS NOT NULL
-- GROUP BY prob_bucket
-- ORDER BY prob_bucket;
