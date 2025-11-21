-- RAG Autonomous Learning System - Database Schema
--
-- This schema extends the existing xtrades schema to support autonomous learning
--
-- Author: Magnus Wheel Strategy Dashboard
-- Created: 2025-11-10

-- ============================================================================
-- LEARNING INSIGHTS TABLE
-- ============================================================================
-- Stores extracted patterns and insights from trade outcomes

CREATE TABLE IF NOT EXISTS xtrades_learning_insights (
    id SERIAL PRIMARY KEY,
    insight_type VARCHAR(50) NOT NULL,  -- success_pattern, failure_pattern, regime_change, pattern_break
    ticker VARCHAR(10),
    strategy VARCHAR(50),
    insight_text TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',  -- Additional context (pnl, vix_change, etc.)
    embedding VECTOR(768),  -- Will be populated by embedding pipeline
    created_at TIMESTAMP DEFAULT NOW(),

    -- Indexes
    INDEX idx_learning_insights_type (insight_type),
    INDEX idx_learning_insights_ticker (ticker),
    INDEX idx_learning_insights_created (created_at DESC)
);

COMMENT ON TABLE xtrades_learning_insights IS 'Stores autonomous learning insights extracted from trade outcomes';
COMMENT ON COLUMN xtrades_learning_insights.insight_type IS 'Type of insight: success_pattern, failure_pattern, regime_change, pattern_break';
COMMENT ON COLUMN xtrades_learning_insights.embedding IS 'Vector embedding of insight text (768-dim for all-mpnet-base-v2)';

-- ============================================================================
-- LEARNING CONFIGURATION TABLE
-- ============================================================================
-- Stores adaptive parameters for the learning system

CREATE TABLE IF NOT EXISTS xtrades_learning_config (
    id SERIAL PRIMARY KEY,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value JSONB NOT NULL,
    description TEXT,
    updated_at TIMESTAMP DEFAULT NOW(),
    updated_by VARCHAR(50) DEFAULT 'system'
);

COMMENT ON TABLE xtrades_learning_config IS 'Adaptive configuration parameters for the learning system';

-- Insert default learning parameters
INSERT INTO xtrades_learning_config (config_key, config_value, description)
VALUES
    ('success_weight_params',
     '{"min_weight": 0.1, "max_weight": 2.0, "boost_factor": 1.1, "penalty_factor": 0.9}'::jsonb,
     'Parameters for success weight updates'),

    ('retrieval_weights',
     '{"semantic_similarity": 0.4, "recency": 0.2, "success_weight": 0.2, "market_regime_match": 0.1, "user_preference": 0.1}'::jsonb,
     'Weights for hybrid retrieval re-ranking'),

    ('confidence_bands',
     '[{"low": 0, "high": 50}, {"low": 50, "high": 70}, {"low": 70, "high": 85}, {"low": 85, "high": 100}]'::jsonb,
     'Confidence calibration bands'),

    ('learning_cycle_config',
     '{"frequency_minutes": 30, "batch_size": 100, "max_insights_per_trade": 5}'::jsonb,
     'Configuration for learning cycle execution')
ON CONFLICT (config_key) DO NOTHING;

-- ============================================================================
-- MARKET REGIME HISTORY TABLE
-- ============================================================================
-- Tracks market regime classifications over time

CREATE TABLE IF NOT EXISTS xtrades_market_regimes (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    vix NUMERIC(6, 2) NOT NULL,
    spy_trend VARCHAR(20) NOT NULL,  -- bullish, bearish, neutral
    volatility_regime VARCHAR(20) NOT NULL,  -- low, normal, high, extreme
    trend_regime VARCHAR(20) NOT NULL,  -- bull, bear, neutral
    risk_appetite NUMERIC(3, 2) NOT NULL,  -- 0.0 to 1.0
    metadata JSONB DEFAULT '{}',

    -- Indexes
    INDEX idx_market_regimes_timestamp (timestamp DESC),
    INDEX idx_market_regimes_vol_regime (volatility_regime),
    INDEX idx_market_regimes_trend_regime (trend_regime)
);

COMMENT ON TABLE xtrades_market_regimes IS 'Historical market regime classifications for context-aware learning';

-- ============================================================================
-- EXTEND RECOMMENDATIONS TABLE
-- ============================================================================
-- Add columns to track learning process

ALTER TABLE xtrades_recommendations
ADD COLUMN IF NOT EXISTS learning_processed_at TIMESTAMP;

ALTER TABLE xtrades_recommendations
ADD COLUMN IF NOT EXISTS insights_extracted INTEGER DEFAULT 0;

ALTER TABLE xtrades_recommendations
ADD COLUMN IF NOT EXISTS weights_updated INTEGER DEFAULT 0;

COMMENT ON COLUMN xtrades_recommendations.learning_processed_at IS 'When this recommendation was processed by the learning system';
COMMENT ON COLUMN xtrades_recommendations.insights_extracted IS 'Number of insights extracted from this recommendation';
COMMENT ON COLUMN xtrades_recommendations.weights_updated IS 'Number of similar trade weights updated';

-- Create index for learning pipeline queries
CREATE INDEX IF NOT EXISTS idx_recommendations_learning_pending
ON xtrades_recommendations (learning_processed_at)
WHERE learning_processed_at IS NULL AND outcome_recorded_at IS NOT NULL;

-- ============================================================================
-- LEARNING METRICS TABLE
-- ============================================================================
-- Tracks performance of the learning system over time

CREATE TABLE IF NOT EXISTS xtrades_learning_metrics (
    id SERIAL PRIMARY KEY,
    cycle_timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    trades_processed INTEGER NOT NULL DEFAULT 0,
    weights_updated INTEGER NOT NULL DEFAULT 0,
    insights_extracted INTEGER NOT NULL DEFAULT 0,
    accuracy_before NUMERIC(5, 2),
    accuracy_after NUMERIC(5, 2),
    accuracy_improvement NUMERIC(5, 2),
    cycle_duration_seconds NUMERIC(8, 2),
    metadata JSONB DEFAULT '{}',

    -- Indexes
    INDEX idx_learning_metrics_timestamp (cycle_timestamp DESC)
);

COMMENT ON TABLE xtrades_learning_metrics IS 'Performance metrics for each learning cycle';

-- ============================================================================
-- CONFIDENCE CALIBRATION TABLE
-- ============================================================================
-- Tracks confidence calibration analysis over time

CREATE TABLE IF NOT EXISTS xtrades_confidence_calibration (
    id SERIAL PRIMARY KEY,
    analysis_timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    confidence_band VARCHAR(20) NOT NULL,  -- e.g., "70-85%"
    expected_accuracy NUMERIC(5, 2) NOT NULL,
    actual_accuracy NUMERIC(5, 2) NOT NULL,
    calibration_error NUMERIC(5, 2) NOT NULL,
    adjustment_factor NUMERIC(4, 3) NOT NULL,
    sample_count INTEGER NOT NULL,

    -- Indexes
    INDEX idx_confidence_calibration_timestamp (analysis_timestamp DESC),
    INDEX idx_confidence_calibration_band (confidence_band)
);

COMMENT ON TABLE xtrades_confidence_calibration IS 'Confidence calibration analysis results';

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Function: Get current market regime
CREATE OR REPLACE FUNCTION get_current_market_regime()
RETURNS TABLE (
    vix NUMERIC,
    spy_trend VARCHAR,
    volatility_regime VARCHAR,
    trend_regime VARCHAR,
    risk_appetite NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        mr.vix,
        mr.spy_trend,
        mr.volatility_regime,
        mr.trend_regime,
        mr.risk_appetite
    FROM xtrades_market_regimes mr
    ORDER BY mr.timestamp DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_current_market_regime() IS 'Get the most recent market regime classification';

-- Function: Record learning cycle metrics
CREATE OR REPLACE FUNCTION record_learning_cycle(
    p_trades_processed INTEGER,
    p_weights_updated INTEGER,
    p_insights_extracted INTEGER,
    p_accuracy_before NUMERIC DEFAULT NULL,
    p_accuracy_after NUMERIC DEFAULT NULL,
    p_duration_seconds NUMERIC DEFAULT NULL
) RETURNS INTEGER AS $$
DECLARE
    v_metric_id INTEGER;
    v_accuracy_improvement NUMERIC;
BEGIN
    -- Calculate improvement
    IF p_accuracy_before IS NOT NULL AND p_accuracy_after IS NOT NULL THEN
        v_accuracy_improvement := p_accuracy_after - p_accuracy_before;
    ELSE
        v_accuracy_improvement := NULL;
    END IF;

    -- Insert metrics
    INSERT INTO xtrades_learning_metrics (
        cycle_timestamp,
        trades_processed,
        weights_updated,
        insights_extracted,
        accuracy_before,
        accuracy_after,
        accuracy_improvement,
        cycle_duration_seconds
    )
    VALUES (
        NOW(),
        p_trades_processed,
        p_weights_updated,
        p_insights_extracted,
        p_accuracy_before,
        p_accuracy_after,
        v_accuracy_improvement,
        p_duration_seconds
    )
    RETURNING id INTO v_metric_id;

    RETURN v_metric_id;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION record_learning_cycle IS 'Record metrics from a learning cycle execution';

-- Function: Get learning system statistics
CREATE OR REPLACE FUNCTION get_learning_statistics(p_days INTEGER DEFAULT 7)
RETURNS TABLE (
    total_insights INTEGER,
    total_cycles INTEGER,
    total_trades_processed INTEGER,
    avg_insights_per_cycle NUMERIC,
    avg_accuracy_improvement NUMERIC,
    recent_accuracy NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(*)::INTEGER as total_insights,
        (SELECT COUNT(*)::INTEGER
         FROM xtrades_learning_metrics
         WHERE cycle_timestamp > NOW() - INTERVAL '1 day' * p_days) as total_cycles,
        (SELECT SUM(trades_processed)::INTEGER
         FROM xtrades_learning_metrics
         WHERE cycle_timestamp > NOW() - INTERVAL '1 day' * p_days) as total_trades_processed,
        (SELECT AVG(insights_extracted)
         FROM xtrades_learning_metrics
         WHERE cycle_timestamp > NOW() - INTERVAL '1 day' * p_days) as avg_insights_per_cycle,
        (SELECT AVG(accuracy_improvement)
         FROM xtrades_learning_metrics
         WHERE cycle_timestamp > NOW() - INTERVAL '1 day' * p_days
         AND accuracy_improvement IS NOT NULL) as avg_accuracy_improvement,
        (SELECT accuracy_after
         FROM xtrades_learning_metrics
         WHERE accuracy_after IS NOT NULL
         ORDER BY cycle_timestamp DESC
         LIMIT 1) as recent_accuracy
    FROM xtrades_learning_insights
    WHERE created_at > NOW() - INTERVAL '1 day' * p_days;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_learning_statistics IS 'Get aggregate statistics about the learning system';

-- ============================================================================
-- VIEWS
-- ============================================================================

-- View: Learning System Dashboard
CREATE OR REPLACE VIEW v_learning_dashboard AS
SELECT
    (SELECT COUNT(*) FROM xtrades_recommendations WHERE learning_processed_at IS NULL AND outcome_recorded_at IS NOT NULL) as pending_trades,
    (SELECT COUNT(*) FROM xtrades_learning_insights WHERE created_at > NOW() - INTERVAL '24 hours') as insights_today,
    (SELECT SUM(trades_processed) FROM xtrades_learning_metrics WHERE cycle_timestamp > NOW() - INTERVAL '24 hours') as trades_processed_today,
    (SELECT AVG(accuracy_improvement) FROM xtrades_learning_metrics WHERE cycle_timestamp > NOW() - INTERVAL '7 days' AND accuracy_improvement IS NOT NULL) as avg_improvement_7d,
    (SELECT cycle_timestamp FROM xtrades_learning_metrics ORDER BY cycle_timestamp DESC LIMIT 1) as last_cycle_at;

COMMENT ON VIEW v_learning_dashboard IS 'Quick dashboard view of learning system status';

-- View: Recent Insights
CREATE OR REPLACE VIEW v_recent_insights AS
SELECT
    id,
    insight_type,
    ticker,
    strategy,
    LEFT(insight_text, 100) || '...' as insight_summary,
    created_at
FROM xtrades_learning_insights
ORDER BY created_at DESC
LIMIT 50;

COMMENT ON VIEW v_recent_insights IS 'Recent learning insights extracted by the system';

-- View: Learning Performance Trend
CREATE OR REPLACE VIEW v_learning_performance_trend AS
SELECT
    DATE(cycle_timestamp) as date,
    COUNT(*) as cycles,
    SUM(trades_processed) as trades_processed,
    SUM(insights_extracted) as insights_extracted,
    AVG(accuracy_improvement) as avg_improvement,
    AVG(cycle_duration_seconds) as avg_duration_seconds
FROM xtrades_learning_metrics
WHERE cycle_timestamp > NOW() - INTERVAL '30 days'
GROUP BY DATE(cycle_timestamp)
ORDER BY date DESC;

COMMENT ON VIEW v_learning_performance_trend IS 'Daily learning system performance trends';

-- ============================================================================
-- GRANTS (adjust as needed for your setup)
-- ============================================================================

-- Grant permissions to application user (adjust username as needed)
-- GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO your_app_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO your_app_user;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO your_app_user;

-- ============================================================================
-- MAINTENANCE
-- ============================================================================

-- Function: Cleanup old insights (keep last 90 days)
CREATE OR REPLACE FUNCTION cleanup_old_learning_data()
RETURNS INTEGER AS $$
DECLARE
    v_deleted INTEGER;
BEGIN
    -- Delete insights older than 90 days
    DELETE FROM xtrades_learning_insights
    WHERE created_at < NOW() - INTERVAL '90 days';

    GET DIAGNOSTICS v_deleted = ROW_COUNT;

    -- Delete old learning metrics (keep 180 days)
    DELETE FROM xtrades_learning_metrics
    WHERE cycle_timestamp < NOW() - INTERVAL '180 days';

    -- Delete old market regimes (keep 180 days)
    DELETE FROM xtrades_market_regimes
    WHERE timestamp < NOW() - INTERVAL '180 days';

    RETURN v_deleted;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION cleanup_old_learning_data() IS 'Cleanup old learning data (call monthly via cron)';

-- ============================================================================
-- SAMPLE DATA (for testing)
-- ============================================================================

-- Insert sample market regime
INSERT INTO xtrades_market_regimes (vix, spy_trend, volatility_regime, trend_regime, risk_appetite)
VALUES (15.5, 'bullish', 'normal', 'bull', 0.75)
ON CONFLICT DO NOTHING;

-- ============================================================================
-- COMPLETION MESSAGE
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'RAG Autonomous Learning Schema Installed';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Tables created:';
    RAISE NOTICE '  - xtrades_learning_insights';
    RAISE NOTICE '  - xtrades_learning_config';
    RAISE NOTICE '  - xtrades_market_regimes';
    RAISE NOTICE '  - xtrades_learning_metrics';
    RAISE NOTICE '  - xtrades_confidence_calibration';
    RAISE NOTICE '';
    RAISE NOTICE 'Views created:';
    RAISE NOTICE '  - v_learning_dashboard';
    RAISE NOTICE '  - v_recent_insights';
    RAISE NOTICE '  - v_learning_performance_trend';
    RAISE NOTICE '';
    RAISE NOTICE 'Functions created:';
    RAISE NOTICE '  - get_current_market_regime()';
    RAISE NOTICE '  - record_learning_cycle()';
    RAISE NOTICE '  - get_learning_statistics()';
    RAISE NOTICE '  - cleanup_old_learning_data()';
    RAISE NOTICE '';
    RAISE NOTICE 'Next steps:';
    RAISE NOTICE '  1. Install pgvector extension (if not already installed)';
    RAISE NOTICE '  2. Run: CREATE EXTENSION IF NOT EXISTS vector;';
    RAISE NOTICE '  3. Test learning pipeline: python src/rag/autonomous_learning.py';
    RAISE NOTICE '========================================';
END $$;
