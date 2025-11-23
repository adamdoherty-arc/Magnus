-- ============================================================================
-- Kalshi AI Enhancement - Database Schema Extensions
-- ============================================================================
-- Purpose: Extend existing Kalshi schema with AI/ML capabilities
-- Database: magnus (PostgreSQL)
-- Created: 2025-11-09
-- ============================================================================

-- ============================================================================
-- Table: kalshi_ai_usage
-- ============================================================================
-- Tracks AI model API usage and costs
-- ============================================================================

CREATE TABLE IF NOT EXISTS kalshi_ai_usage (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(50) NOT NULL,
    request_type VARCHAR(50),
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    cost DECIMAL(10,4) DEFAULT 0,
    market_ticker VARCHAR(100),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE kalshi_ai_usage IS 'Logs AI model API usage for cost tracking';
COMMENT ON COLUMN kalshi_ai_usage.model_name IS 'AI model used (gpt4, claude, gemini, llama3)';
COMMENT ON COLUMN kalshi_ai_usage.request_type IS 'Type of analysis request';
COMMENT ON COLUMN kalshi_ai_usage.cost IS 'USD cost of API call';

CREATE INDEX IF NOT EXISTS idx_ai_usage_timestamp ON kalshi_ai_usage(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_ai_usage_model ON kalshi_ai_usage(model_name);
CREATE INDEX IF NOT EXISTS idx_ai_usage_market ON kalshi_ai_usage(market_ticker);

-- ============================================================================
-- Table: kalshi_ai_budgets
-- ============================================================================
-- Stores budget limits and alert thresholds
-- ============================================================================

CREATE TABLE IF NOT EXISTS kalshi_ai_budgets (
    id SERIAL PRIMARY KEY,
    period VARCHAR(20) NOT NULL,          -- 'daily', 'weekly', 'monthly'
    budget_limit DECIMAL(10,2) NOT NULL,
    alert_threshold DECIMAL(5,2) DEFAULT 80.0, -- Alert at 80% of budget
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(period)
);

COMMENT ON TABLE kalshi_ai_budgets IS 'AI API budget limits and thresholds';

-- Insert default budgets
INSERT INTO kalshi_ai_budgets (period, budget_limit, alert_threshold)
VALUES
    ('daily', 150.00, 80.0),
    ('weekly', 700.00, 80.0),
    ('monthly', 2500.00, 80.0)
ON CONFLICT (period) DO NOTHING;

-- ============================================================================
-- Table: kalshi_ml_features
-- ============================================================================
-- Stores engineered features for ML models
-- ============================================================================

CREATE TABLE IF NOT EXISTS kalshi_ml_features (
    id SERIAL PRIMARY KEY,
    market_id INTEGER NOT NULL REFERENCES kalshi_markets(id) ON DELETE CASCADE,
    ticker VARCHAR(100) NOT NULL,

    -- Market features
    price_efficiency DECIMAL(6,4),
    volume_log DECIMAL(10,4),
    oi_log DECIMAL(10,4),
    liquidity_ratio DECIMAL(10,4),
    hours_until_close DECIMAL(8,2),

    -- Team features (if applicable)
    home_win_pct DECIMAL(5,3),
    away_win_pct DECIMAL(5,3),
    home_ppg DECIMAL(5,2),
    away_ppg DECIMAL(5,2),
    home_papg DECIMAL(5,2),
    away_papg DECIMAL(5,2),
    elo_diff DECIMAL(6,2),
    home_last5_wins INTEGER,
    away_last5_wins INTEGER,

    -- Situational features
    temperature DECIMAL(5,2),
    wind_speed DECIMAL(5,2),
    weather_impact_score DECIMAL(5,2),
    home_injury_impact DECIMAL(5,2),
    away_injury_impact DECIMAL(5,2),
    days_rest_home INTEGER,
    days_rest_away INTEGER,

    -- Historical features
    h2h_home_wins INTEGER,
    h2h_total_games INTEGER,
    h2h_avg_point_diff DECIMAL(6,2),

    -- Sentiment features
    twitter_sentiment DECIMAL(5,3),  -- -1 to 1
    reddit_sentiment DECIMAL(5,3),
    betting_pct_on_yes DECIMAL(5,2),
    price_velocity DECIMAL(8,6),
    steam_move_count INTEGER,

    -- Full feature vector (JSON for flexibility)
    feature_vector JSONB,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE kalshi_ml_features IS 'Engineered features for machine learning models';

CREATE INDEX IF NOT EXISTS idx_kalshi_ml_features_market ON kalshi_ml_features(market_id);
CREATE INDEX IF NOT EXISTS idx_kalshi_ml_features_ticker ON kalshi_ml_features(ticker);

-- ============================================================================
-- Table: kalshi_social_sentiment
-- ============================================================================
-- Tracks social media sentiment for markets
-- ============================================================================

CREATE TABLE IF NOT EXISTS kalshi_social_sentiment (
    id SERIAL PRIMARY KEY,
    market_id INTEGER NOT NULL REFERENCES kalshi_markets(id) ON DELETE CASCADE,
    ticker VARCHAR(100) NOT NULL,

    source VARCHAR(20) NOT NULL, -- 'twitter', 'reddit', 'stocktwits'

    -- Sentiment scores
    sentiment_score DECIMAL(5,3), -- -1 to 1 (bearish to bullish)
    volume_mentions INTEGER DEFAULT 0,
    positive_mentions INTEGER DEFAULT 0,
    negative_mentions INTEGER DEFAULT 0,
    neutral_mentions INTEGER DEFAULT 0,

    -- Top keywords/phrases
    trending_keywords JSONB,

    -- Timestamp
    snapshot_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT chk_source CHECK (source IN ('twitter', 'reddit', 'stocktwits'))
);

COMMENT ON TABLE kalshi_social_sentiment IS 'Social media sentiment analysis for markets';

CREATE INDEX IF NOT EXISTS idx_kalshi_sentiment_market ON kalshi_social_sentiment(market_id);
CREATE INDEX IF NOT EXISTS idx_kalshi_sentiment_time ON kalshi_social_sentiment(snapshot_time DESC);
CREATE INDEX IF NOT EXISTS idx_kalshi_sentiment_source ON kalshi_social_sentiment(source);

-- ============================================================================
-- Table: kalshi_live_events
-- ============================================================================
-- Stores live game events and updates
-- ============================================================================

CREATE TABLE IF NOT EXISTS kalshi_live_events (
    id SERIAL PRIMARY KEY,
    game_id VARCHAR(50) NOT NULL,

    -- Game state
    quarter INTEGER,
    time_remaining VARCHAR(10),
    home_score INTEGER,
    away_score INTEGER,
    possession VARCHAR(10), -- 'home', 'away', 'none'

    -- Recent play
    play_description TEXT,
    play_type VARCHAR(50),
    yards_gained INTEGER,

    -- Affected markets (tickers)
    affected_markets JSONB,

    -- Timestamp
    event_time TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE kalshi_live_events IS 'Live game events affecting markets';

CREATE INDEX IF NOT EXISTS idx_kalshi_live_game ON kalshi_live_events(game_id);
CREATE INDEX IF NOT EXISTS idx_kalshi_live_time ON kalshi_live_events(event_time DESC);

-- ============================================================================
-- Table: kalshi_model_performance
-- ============================================================================
-- Tracks accuracy and performance of each AI model
-- ============================================================================

CREATE TABLE IF NOT EXISTS kalshi_model_performance (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(50) NOT NULL,

    -- Performance metrics
    total_predictions INTEGER DEFAULT 0,
    correct_predictions INTEGER DEFAULT 0,
    accuracy DECIMAL(5,2),

    avg_edge DECIMAL(5,2),
    avg_confidence DECIMAL(5,2),

    -- By market type
    nfl_accuracy DECIMAL(5,2),
    college_accuracy DECIMAL(5,2),

    -- Calibration
    edge_calibration_error DECIMAL(5,2), -- Avg deviation of predicted edge from actual

    -- Time period
    period_start TIMESTAMP WITH TIME ZONE,
    period_end TIMESTAMP WITH TIME ZONE,

    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE kalshi_model_performance IS 'AI model performance tracking and evaluation';

CREATE INDEX IF NOT EXISTS idx_kalshi_model_perf ON kalshi_model_performance(model_name);

-- ============================================================================
-- Table: kalshi_ensemble_predictions
-- ============================================================================
-- Stores detailed ensemble prediction logs
-- ============================================================================

CREATE TABLE IF NOT EXISTS kalshi_ensemble_predictions (
    id SERIAL PRIMARY KEY,
    market_id INTEGER NOT NULL REFERENCES kalshi_markets(id) ON DELETE CASCADE,
    ticker VARCHAR(100) NOT NULL,

    -- Ensemble details
    ensemble_mode VARCHAR(20), -- 'premium', 'balanced', 'fast', 'cost'
    models_used JSONB,         -- Array of model names

    -- Individual model predictions
    gpt4_prediction JSONB,
    claude_prediction JSONB,
    gemini_prediction JSONB,
    llama3_prediction JSONB,

    -- Consensus result
    consensus_outcome VARCHAR(10),
    consensus_confidence DECIMAL(5,2),
    consensus_edge DECIMAL(5,2),
    model_agreement DECIMAL(5,2),

    -- Performance
    total_latency_ms INTEGER,
    total_cost DECIMAL(10,4),

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE kalshi_ensemble_predictions IS 'Detailed logs of ensemble predictions';

CREATE INDEX IF NOT EXISTS idx_ensemble_preds_market ON kalshi_ensemble_predictions(market_id);
CREATE INDEX IF NOT EXISTS idx_ensemble_preds_mode ON kalshi_ensemble_predictions(ensemble_mode);

-- ============================================================================
-- Views for Analysis
-- ============================================================================

-- View: Daily cost summary
CREATE OR REPLACE VIEW v_kalshi_ai_daily_costs AS
SELECT
    DATE(timestamp) as date,
    model_name,
    COUNT(*) as requests,
    SUM(input_tokens) as total_input_tokens,
    SUM(output_tokens) as total_output_tokens,
    SUM(cost) as total_cost
FROM kalshi_ai_usage
WHERE timestamp >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(timestamp), model_name
ORDER BY date DESC, total_cost DESC;

COMMENT ON VIEW v_kalshi_ai_daily_costs IS 'Daily AI cost breakdown by model';

-- View: Model performance comparison
CREATE OR REPLACE VIEW v_kalshi_model_comparison AS
SELECT
    model_name,
    accuracy,
    avg_confidence,
    avg_edge,
    edge_calibration_error,
    total_predictions,
    correct_predictions,
    nfl_accuracy,
    college_accuracy,
    updated_at
FROM kalshi_model_performance
ORDER BY accuracy DESC;

COMMENT ON VIEW v_kalshi_model_comparison IS 'Compare AI model performance metrics';

-- View: High-confidence opportunities
CREATE OR REPLACE VIEW v_kalshi_ai_opportunities AS
SELECT
    m.ticker,
    m.title,
    m.market_type,
    m.yes_price,
    m.no_price,
    m.volume,
    m.close_time,
    p.predicted_outcome,
    p.confidence_score,
    p.edge_percentage,
    p.recommended_action,
    p.recommended_stake_pct,
    p.reasoning,
    p.overall_rank
FROM kalshi_markets m
INNER JOIN kalshi_predictions p ON m.id = p.market_id
WHERE m.status = 'open'
    AND p.confidence_score >= 70
    AND p.edge_percentage >= 5
    AND p.recommended_action IN ('strong_buy', 'buy')
ORDER BY p.overall_rank ASC;

COMMENT ON VIEW v_kalshi_ai_opportunities IS 'High-confidence betting opportunities';

-- ============================================================================
-- Functions
-- ============================================================================

-- Function: Calculate budget status
CREATE OR REPLACE FUNCTION get_budget_status(p_period VARCHAR)
RETURNS TABLE (
    period VARCHAR,
    budget_limit DECIMAL,
    current_spend DECIMAL,
    remaining DECIMAL,
    percentage_used DECIMAL,
    status VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    WITH budget AS (
        SELECT budget_limit as limit
        FROM kalshi_ai_budgets
        WHERE period = p_period
    ),
    spending AS (
        SELECT COALESCE(SUM(cost), 0) as spend
        FROM kalshi_ai_usage
        WHERE
            CASE
                WHEN p_period = 'daily' THEN timestamp >= CURRENT_DATE
                WHEN p_period = 'weekly' THEN timestamp >= CURRENT_DATE - INTERVAL '7 days'
                WHEN p_period = 'monthly' THEN timestamp >= CURRENT_DATE - INTERVAL '30 days'
            END
    )
    SELECT
        p_period,
        budget.limit,
        spending.spend,
        budget.limit - spending.spend as remaining,
        ROUND((spending.spend / budget.limit * 100)::numeric, 2) as pct_used,
        CASE
            WHEN spending.spend >= budget.limit THEN 'EXCEEDED'
            WHEN spending.spend >= budget.limit * 0.95 THEN 'CRITICAL'
            WHEN spending.spend >= budget.limit * 0.80 THEN 'WARNING'
            ELSE 'OK'
        END as status
    FROM budget, spending;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_budget_status IS 'Check current budget status for a period';

-- ============================================================================
-- Sample Queries
-- ============================================================================

/*

-- Get budget status
SELECT * FROM get_budget_status('daily');
SELECT * FROM get_budget_status('weekly');
SELECT * FROM get_budget_status('monthly');

-- Daily cost summary
SELECT * FROM v_kalshi_ai_daily_costs LIMIT 7;

-- Model performance comparison
SELECT * FROM v_kalshi_model_comparison;

-- Top opportunities
SELECT * FROM v_kalshi_ai_opportunities LIMIT 10;

-- Cost by model (last 7 days)
SELECT
    model_name,
    COUNT(*) as requests,
    SUM(cost) as total_cost,
    AVG(cost) as avg_cost
FROM kalshi_ai_usage
WHERE timestamp >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY model_name
ORDER BY total_cost DESC;

-- Sentiment trends
SELECT
    DATE(snapshot_time) as date,
    source,
    AVG(sentiment_score) as avg_sentiment,
    SUM(volume_mentions) as total_mentions
FROM kalshi_social_sentiment
WHERE snapshot_time >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY DATE(snapshot_time), source
ORDER BY date DESC;

*/

-- ============================================================================
-- End of Schema
-- ============================================================================
