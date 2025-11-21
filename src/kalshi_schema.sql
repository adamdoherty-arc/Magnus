-- ============================================================================
-- Kalshi Football Markets - Database Schema
-- ============================================================================
-- Purpose: Store and analyze NFL and College Football prediction markets
-- Database: magnus (PostgreSQL)
-- Created: 2025-11-04
-- ============================================================================

-- ============================================================================
-- Table 1: kalshi_markets
-- ============================================================================
-- Stores all football market data from Kalshi API
-- Each row represents a single prediction market (game or prop)
-- ============================================================================

CREATE TABLE IF NOT EXISTS kalshi_markets (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(100) UNIQUE NOT NULL,
    title TEXT NOT NULL,
    subtitle TEXT,
    market_type VARCHAR(50) NOT NULL, -- 'nfl', 'college'
    series_ticker VARCHAR(100),

    -- Teams and matchup info
    home_team VARCHAR(100),
    away_team VARCHAR(100),
    game_date TIMESTAMP WITH TIME ZONE,

    -- Market details
    yes_price DECIMAL(5,4), -- Current yes price (0.0000 to 1.0000)
    no_price DECIMAL(5,4), -- Current no price
    volume DECIMAL(15,2) DEFAULT 0, -- Total trading volume
    open_interest INTEGER DEFAULT 0,

    -- Market status
    status VARCHAR(20) DEFAULT 'open', -- 'open', 'closed', 'settled'
    close_time TIMESTAMP WITH TIME ZONE,
    expiration_time TIMESTAMP WITH TIME ZONE,
    result VARCHAR(10), -- 'yes', 'no', NULL if not settled

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    synced_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Raw API data (for debugging)
    raw_data JSONB,

    CONSTRAINT chk_market_type CHECK (market_type IN ('nfl', 'college')),
    CONSTRAINT chk_status CHECK (status IN ('open', 'closed', 'settled')),
    CONSTRAINT chk_result CHECK (result IN ('yes', 'no', NULL)),
    CONSTRAINT chk_prices CHECK (yes_price >= 0 AND yes_price <= 1 AND no_price >= 0 AND no_price <= 1)
);

-- Add comments for documentation
COMMENT ON TABLE kalshi_markets IS 'Stores all football market data from Kalshi prediction markets';
COMMENT ON COLUMN kalshi_markets.ticker IS 'Unique Kalshi market ticker symbol';
COMMENT ON COLUMN kalshi_markets.market_type IS 'Type of football: nfl or college';
COMMENT ON COLUMN kalshi_markets.yes_price IS 'Current market price for YES outcome (0-1)';
COMMENT ON COLUMN kalshi_markets.volume IS 'Total USD trading volume';
COMMENT ON COLUMN kalshi_markets.raw_data IS 'Complete API response for debugging';

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_kalshi_markets_type ON kalshi_markets(market_type);
CREATE INDEX IF NOT EXISTS idx_kalshi_markets_status ON kalshi_markets(status);
CREATE INDEX IF NOT EXISTS idx_kalshi_markets_game_date ON kalshi_markets(game_date);
CREATE INDEX IF NOT EXISTS idx_kalshi_markets_close_time ON kalshi_markets(close_time);
CREATE INDEX IF NOT EXISTS idx_kalshi_markets_home_team ON kalshi_markets(home_team);
CREATE INDEX IF NOT EXISTS idx_kalshi_markets_away_team ON kalshi_markets(away_team);

-- ============================================================================
-- Table 2: kalshi_predictions
-- ============================================================================
-- Stores AI-generated predictions and rankings for Kalshi markets
-- Each row represents an AI evaluation of a specific market
-- ============================================================================

CREATE TABLE IF NOT EXISTS kalshi_predictions (
    id SERIAL PRIMARY KEY,
    market_id INTEGER NOT NULL REFERENCES kalshi_markets(id) ON DELETE CASCADE,
    ticker VARCHAR(100) NOT NULL,

    -- AI Prediction
    predicted_outcome VARCHAR(10), -- 'yes', 'no'
    confidence_score DECIMAL(5,2), -- 0-100
    edge_percentage DECIMAL(5,2), -- Market inefficiency (positive = good bet)

    -- Ranking
    overall_rank INTEGER,
    type_rank INTEGER, -- Rank within NFL or College

    -- Analysis factors (weighted scoring)
    value_score DECIMAL(5,2), -- Price vs true probability
    liquidity_score DECIMAL(5,2), -- Volume and open interest
    timing_score DECIMAL(5,2), -- Time until close
    matchup_score DECIMAL(5,2), -- Team strength analysis
    sentiment_score DECIMAL(5,2), -- Market sentiment

    -- Betting recommendation
    recommended_action VARCHAR(20), -- 'strong_buy', 'buy', 'hold', 'pass'
    recommended_stake_pct DECIMAL(5,2), -- Percentage of bankroll (Kelly criterion)
    max_price DECIMAL(5,4), -- Don't buy above this price

    -- AI reasoning
    reasoning TEXT,
    key_factors JSONB, -- Array of key analysis points

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT chk_predicted_outcome CHECK (predicted_outcome IN ('yes', 'no')),
    CONSTRAINT chk_confidence CHECK (confidence_score >= 0 AND confidence_score <= 100),
    CONSTRAINT chk_action CHECK (recommended_action IN ('strong_buy', 'buy', 'hold', 'pass'))
);

-- Add comments
COMMENT ON TABLE kalshi_predictions IS 'AI-generated predictions and rankings for Kalshi football markets';
COMMENT ON COLUMN kalshi_predictions.edge_percentage IS 'Expected value edge over market price';
COMMENT ON COLUMN kalshi_predictions.confidence_score IS 'AI confidence in prediction (0-100)';
COMMENT ON COLUMN kalshi_predictions.recommended_stake_pct IS 'Recommended bet size as % of bankroll';

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_kalshi_predictions_market ON kalshi_predictions(market_id);
CREATE INDEX IF NOT EXISTS idx_kalshi_predictions_rank ON kalshi_predictions(overall_rank);
CREATE INDEX IF NOT EXISTS idx_kalshi_predictions_action ON kalshi_predictions(recommended_action);
CREATE INDEX IF NOT EXISTS idx_kalshi_predictions_edge ON kalshi_predictions(edge_percentage DESC);

-- Add unique constraint on market_id (one prediction per market)
-- This is done after indexes to ensure proper constraint handling
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'kalshi_predictions_market_id_key'
    ) THEN
        ALTER TABLE kalshi_predictions
        ADD CONSTRAINT kalshi_predictions_market_id_key UNIQUE (market_id);
    END IF;
END$$;

-- ============================================================================
-- Table 3: kalshi_price_history
-- ============================================================================
-- Stores historical price snapshots for markets
-- Used for charting and analysis
-- ============================================================================

CREATE TABLE IF NOT EXISTS kalshi_price_history (
    id SERIAL PRIMARY KEY,
    market_id INTEGER NOT NULL REFERENCES kalshi_markets(id) ON DELETE CASCADE,
    ticker VARCHAR(100) NOT NULL,

    -- Price snapshot
    yes_price DECIMAL(5,4),
    no_price DECIMAL(5,4),
    volume DECIMAL(15,2),
    open_interest INTEGER,

    -- Timestamp
    snapshot_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT chk_history_prices CHECK (yes_price >= 0 AND yes_price <= 1 AND no_price >= 0 AND no_price <= 1)
);

COMMENT ON TABLE kalshi_price_history IS 'Historical price snapshots for charting and analysis';

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_kalshi_price_history_market ON kalshi_price_history(market_id);
CREATE INDEX IF NOT EXISTS idx_kalshi_price_history_time ON kalshi_price_history(snapshot_time);
CREATE INDEX IF NOT EXISTS idx_kalshi_price_history_ticker ON kalshi_price_history(ticker);

-- ============================================================================
-- Table 4: kalshi_sync_log
-- ============================================================================
-- Tracks sync operations and their results
-- ============================================================================

CREATE TABLE IF NOT EXISTS kalshi_sync_log (
    id SERIAL PRIMARY KEY,
    sync_type VARCHAR(50) NOT NULL, -- 'markets', 'predictions', 'prices'
    market_type VARCHAR(20), -- 'nfl', 'college', 'all'

    -- Stats
    total_processed INTEGER DEFAULT 0,
    successful INTEGER DEFAULT 0,
    failed INTEGER DEFAULT 0,
    duration_seconds INTEGER,

    -- Status
    status VARCHAR(20) DEFAULT 'running', -- 'running', 'completed', 'error'
    error_message TEXT,

    -- Timestamps
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT chk_sync_type CHECK (sync_type IN ('markets', 'predictions', 'prices')),
    CONSTRAINT chk_sync_status CHECK (status IN ('running', 'completed', 'error'))
);

COMMENT ON TABLE kalshi_sync_log IS 'Tracks Kalshi data sync operations';

CREATE INDEX IF NOT EXISTS idx_kalshi_sync_log_type ON kalshi_sync_log(sync_type);
CREATE INDEX IF NOT EXISTS idx_kalshi_sync_log_started ON kalshi_sync_log(started_at DESC);

-- ============================================================================
-- Views for Easy Querying
-- ============================================================================

-- View: Active NFL markets with predictions
CREATE OR REPLACE VIEW v_kalshi_nfl_active AS
SELECT
    m.ticker,
    m.title,
    m.home_team,
    m.away_team,
    m.game_date,
    m.yes_price,
    m.no_price,
    m.volume,
    m.close_time,
    p.predicted_outcome,
    p.confidence_score,
    p.edge_percentage,
    p.overall_rank,
    p.recommended_action,
    p.recommended_stake_pct,
    p.reasoning
FROM kalshi_markets m
LEFT JOIN kalshi_predictions p ON m.id = p.market_id
WHERE m.market_type = 'nfl'
    AND m.status = 'open'
ORDER BY p.overall_rank ASC NULLS LAST;

COMMENT ON VIEW v_kalshi_nfl_active IS 'Active NFL markets with AI predictions, ranked by opportunity';

-- View: Active College markets with predictions
CREATE OR REPLACE VIEW v_kalshi_college_active AS
SELECT
    m.ticker,
    m.title,
    m.home_team,
    m.away_team,
    m.game_date,
    m.yes_price,
    m.no_price,
    m.volume,
    m.close_time,
    p.predicted_outcome,
    p.confidence_score,
    p.edge_percentage,
    p.overall_rank,
    p.recommended_action,
    p.recommended_stake_pct,
    p.reasoning
FROM kalshi_markets m
LEFT JOIN kalshi_predictions p ON m.id = p.market_id
WHERE m.market_type = 'college'
    AND m.status = 'open'
ORDER BY p.overall_rank ASC NULLS LAST;

COMMENT ON VIEW v_kalshi_college_active IS 'Active College Football markets with AI predictions, ranked by opportunity';

-- View: Top opportunities across all markets
CREATE OR REPLACE VIEW v_kalshi_top_opportunities AS
SELECT
    m.market_type,
    m.ticker,
    m.title,
    m.home_team,
    m.away_team,
    m.game_date,
    m.yes_price,
    m.no_price,
    m.volume,
    p.predicted_outcome,
    p.confidence_score,
    p.edge_percentage,
    p.overall_rank,
    p.recommended_action,
    p.recommended_stake_pct,
    p.reasoning,
    p.key_factors
FROM kalshi_markets m
INNER JOIN kalshi_predictions p ON m.id = p.market_id
WHERE m.status IN ('open', 'active')
    AND p.recommended_action IN ('strong_buy', 'buy')
    AND p.edge_percentage > 0
ORDER BY p.overall_rank ASC
LIMIT 50;

COMMENT ON VIEW v_kalshi_top_opportunities IS 'Top 50 betting opportunities ranked by AI analysis';

-- ============================================================================
-- Sample Queries
-- ============================================================================

-- Get all active NFL markets
-- SELECT * FROM v_kalshi_nfl_active;

-- Get top 10 opportunities
-- SELECT * FROM v_kalshi_top_opportunities LIMIT 10;

-- Get markets closing soon
-- SELECT ticker, title, close_time, yes_price, predicted_outcome
-- FROM kalshi_markets m
-- JOIN kalshi_predictions p ON m.id = p.market_id
-- WHERE status = 'open'
--   AND close_time < NOW() + INTERVAL '24 hours'
-- ORDER BY close_time ASC;

-- Get high-confidence predictions
-- SELECT ticker, title, predicted_outcome, confidence_score, edge_percentage
-- FROM kalshi_markets m
-- JOIN kalshi_predictions p ON m.id = p.market_id
-- WHERE confidence_score > 75 AND edge_percentage > 5
-- ORDER BY edge_percentage DESC;
