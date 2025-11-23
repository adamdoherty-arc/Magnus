-- ============================================================================
-- Prediction Agent - Database Schema Updates
-- ============================================================================
-- Purpose: Extend Kalshi schema to support multi-sector predictions
-- Database: magnus (PostgreSQL)
-- Created: 2025-11-09
-- ============================================================================

-- ============================================================================
-- ALTER TABLE: kalshi_markets
-- Add sector support
-- ============================================================================

-- Add sector column to support multiple market types
ALTER TABLE kalshi_markets
ADD COLUMN IF NOT EXISTS sector VARCHAR(50);

-- Add index on sector
CREATE INDEX IF NOT EXISTS idx_kalshi_markets_sector ON kalshi_markets(sector);

-- Add comment
COMMENT ON COLUMN kalshi_markets.sector IS 'Market sector: sports, politics, economics, crypto';

-- Update market_type constraint to allow more types
ALTER TABLE kalshi_markets
DROP CONSTRAINT IF EXISTS chk_market_type;

ALTER TABLE kalshi_markets
ADD CONSTRAINT chk_market_type
CHECK (market_type IN ('nfl', 'college', 'politics', 'economics', 'crypto', 'other'));

-- Update existing records to set sector based on market_type
UPDATE kalshi_markets
SET sector = CASE
    WHEN market_type IN ('nfl', 'college') THEN 'sports'
    WHEN market_type = 'politics' THEN 'politics'
    WHEN market_type = 'economics' THEN 'economics'
    WHEN market_type = 'crypto' THEN 'crypto'
    ELSE 'sports'
END
WHERE sector IS NULL;

-- ============================================================================
-- ALTER TABLE: kalshi_predictions
-- Add calibrated probability and version tracking
-- ============================================================================

-- Add calibrated probability column
ALTER TABLE kalshi_predictions
ADD COLUMN IF NOT EXISTS calibrated_probability DECIMAL(6,4);

-- Add prediction agent version tracking
ALTER TABLE kalshi_predictions
ADD COLUMN IF NOT EXISTS prediction_agent_version VARCHAR(20);

-- Add model metadata
ALTER TABLE kalshi_predictions
ADD COLUMN IF NOT EXISTS model_trained_samples INTEGER DEFAULT 0;

-- Add ensemble information
ALTER TABLE kalshi_predictions
ADD COLUMN IF NOT EXISTS ensemble_weight_ml DECIMAL(4,2);

ALTER TABLE kalshi_predictions
ADD COLUMN IF NOT EXISTS ensemble_weight_llm DECIMAL(4,2);

-- Add LLM comparison fields
ALTER TABLE kalshi_predictions
ADD COLUMN IF NOT EXISTS llm_confidence DECIMAL(5,2);

ALTER TABLE kalshi_predictions
ADD COLUMN IF NOT EXISTS llm_predicted_outcome VARCHAR(10);

-- Add sector column for easier querying
ALTER TABLE kalshi_predictions
ADD COLUMN IF NOT EXISTS sector VARCHAR(50);

-- Add comments
COMMENT ON COLUMN kalshi_predictions.calibrated_probability IS 'Calibrated probability from ensemble model (0-1)';
COMMENT ON COLUMN kalshi_predictions.prediction_agent_version IS 'Version of prediction agent used';
COMMENT ON COLUMN kalshi_predictions.model_trained_samples IS 'Number of samples model was trained on';
COMMENT ON COLUMN kalshi_predictions.ensemble_weight_ml IS 'Weight given to ML model in ensemble';
COMMENT ON COLUMN kalshi_predictions.ensemble_weight_llm IS 'Weight given to LLM in ensemble';

-- Add index on calibrated probability for fast filtering
CREATE INDEX IF NOT EXISTS idx_kalshi_predictions_calibrated_prob
ON kalshi_predictions(calibrated_probability DESC);

-- Add index on sector
CREATE INDEX IF NOT EXISTS idx_kalshi_predictions_sector ON kalshi_predictions(sector);

-- Add constraint on calibrated probability
ALTER TABLE kalshi_predictions
ADD CONSTRAINT chk_calibrated_probability
CHECK (calibrated_probability IS NULL OR (calibrated_probability >= 0 AND calibrated_probability <= 1));

-- ============================================================================
-- CREATE VIEW: Multi-sector opportunities
-- ============================================================================

-- Drop existing view if exists
DROP VIEW IF EXISTS v_kalshi_top_opportunities;

-- Create improved view with sector support
CREATE OR REPLACE VIEW v_kalshi_top_opportunities AS
SELECT
    m.sector,
    m.market_type,
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
    p.calibrated_probability,
    p.edge_percentage,
    p.overall_rank,
    p.recommended_action,
    p.recommended_stake_pct,
    p.prediction_agent_version,
    p.model_trained_samples,
    p.ensemble_weight_ml,
    p.ensemble_weight_llm,
    p.reasoning,
    p.key_factors
FROM kalshi_markets m
INNER JOIN kalshi_predictions p ON m.id = p.market_id
WHERE m.status IN ('open', 'active')
    AND p.recommended_action IN ('strong_buy', 'buy')
    AND p.edge_percentage > 0
ORDER BY p.overall_rank ASC
LIMIT 50;

COMMENT ON VIEW v_kalshi_top_opportunities IS 'Top 50 betting opportunities across all sectors';

-- ============================================================================
-- CREATE VIEW: Sector-specific opportunities
-- ============================================================================

-- Sports opportunities
CREATE OR REPLACE VIEW v_kalshi_sports_opportunities AS
SELECT *
FROM v_kalshi_top_opportunities
WHERE sector = 'sports'
ORDER BY overall_rank ASC;

COMMENT ON VIEW v_kalshi_sports_opportunities IS 'Top sports betting opportunities';

-- Politics opportunities
CREATE OR REPLACE VIEW v_kalshi_politics_opportunities AS
SELECT *
FROM v_kalshi_top_opportunities
WHERE sector = 'politics'
ORDER BY overall_rank ASC;

COMMENT ON VIEW v_kalshi_politics_opportunities IS 'Top political prediction opportunities';

-- Economics opportunities
CREATE OR REPLACE VIEW v_kalshi_economics_opportunities AS
SELECT *
FROM v_kalshi_top_opportunities
WHERE sector = 'economics'
ORDER BY overall_rank ASC;

COMMENT ON VIEW v_kalshi_economics_opportunities IS 'Top economic prediction opportunities';

-- Crypto opportunities
CREATE OR REPLACE VIEW v_kalshi_crypto_opportunities AS
SELECT *
FROM v_kalshi_top_opportunities
WHERE sector = 'crypto'
ORDER BY overall_rank ASC;

COMMENT ON VIEW v_kalshi_crypto_opportunities IS 'Top crypto prediction opportunities';

-- ============================================================================
-- CREATE VIEW: Model performance tracking
-- ============================================================================

CREATE OR REPLACE VIEW v_prediction_model_performance AS
SELECT
    p.sector,
    p.prediction_agent_version,
    COUNT(*) as total_predictions,
    AVG(p.confidence_score) as avg_confidence,
    AVG(p.calibrated_probability) as avg_calibrated_prob,
    AVG(p.edge_percentage) as avg_edge,
    AVG(p.model_trained_samples) as avg_training_samples,
    COUNT(CASE WHEN p.recommended_action IN ('strong_buy', 'buy') THEN 1 END) as buy_recommendations,
    COUNT(CASE WHEN m.result = p.predicted_outcome THEN 1 END) as correct_predictions,
    COUNT(CASE WHEN m.result IS NOT NULL THEN 1 END) as settled_predictions,
    CASE
        WHEN COUNT(CASE WHEN m.result IS NOT NULL THEN 1 END) > 0
        THEN CAST(COUNT(CASE WHEN m.result = p.predicted_outcome THEN 1 END) AS DECIMAL) /
             COUNT(CASE WHEN m.result IS NOT NULL THEN 1 END)
        ELSE NULL
    END as accuracy
FROM kalshi_predictions p
INNER JOIN kalshi_markets m ON p.market_id = m.id
WHERE p.prediction_agent_version IS NOT NULL
GROUP BY p.sector, p.prediction_agent_version
ORDER BY p.sector, p.prediction_agent_version DESC;

COMMENT ON VIEW v_prediction_model_performance IS 'Track prediction model performance by sector and version';

-- ============================================================================
-- CREATE TABLE: Model training history
-- ============================================================================

CREATE TABLE IF NOT EXISTS prediction_model_training_history (
    id SERIAL PRIMARY KEY,
    sector VARCHAR(50) NOT NULL,
    model_version VARCHAR(20) NOT NULL,

    -- Training data
    n_samples INTEGER NOT NULL,
    n_features INTEGER NOT NULL,
    training_start TIMESTAMP WITH TIME ZONE NOT NULL,
    training_end TIMESTAMP WITH TIME ZONE NOT NULL,
    training_duration_seconds INTEGER,

    -- Model metrics
    accuracy DECIMAL(6,4),
    log_loss DECIMAL(8,6),
    brier_score DECIMAL(6,4),
    auc_roc DECIMAL(6,4),

    -- Model parameters
    xgboost_params JSONB,
    calibration_method VARCHAR(20),

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    notes TEXT,

    CONSTRAINT chk_sector_training CHECK (sector IN ('sports', 'politics', 'economics', 'crypto'))
);

CREATE INDEX IF NOT EXISTS idx_training_history_sector ON prediction_model_training_history(sector);
CREATE INDEX IF NOT EXISTS idx_training_history_version ON prediction_model_training_history(model_version);
CREATE INDEX IF NOT EXISTS idx_training_history_created ON prediction_model_training_history(created_at DESC);

COMMENT ON TABLE prediction_model_training_history IS 'History of model training runs';

-- ============================================================================
-- SAMPLE QUERIES
-- ============================================================================

-- Get top opportunities across all sectors
-- SELECT * FROM v_kalshi_top_opportunities LIMIT 20;

-- Get sports-specific opportunities
-- SELECT * FROM v_kalshi_sports_opportunities;

-- Get model performance by sector
-- SELECT * FROM v_prediction_model_performance ORDER BY accuracy DESC;

-- Get high-confidence, high-edge predictions
-- SELECT ticker, title, sector, confidence_score, calibrated_probability, edge_percentage
-- FROM v_kalshi_top_opportunities
-- WHERE confidence_score > 80 AND edge_percentage > 10;

-- Compare ML vs LLM predictions
-- SELECT
--     ticker,
--     predicted_outcome,
--     llm_predicted_outcome,
--     confidence_score,
--     llm_confidence,
--     ensemble_weight_ml,
--     ensemble_weight_llm
-- FROM kalshi_predictions
-- WHERE llm_predicted_outcome IS NOT NULL
-- ORDER BY confidence_score DESC;
