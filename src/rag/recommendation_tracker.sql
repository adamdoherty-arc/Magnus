-- ============================================================================
-- RAG Recommendation Tracking Schema
-- ============================================================================
-- Purpose: Track RAG recommendations and learn from outcomes
-- Database: magnus (PostgreSQL)
-- Created: 2025-11-06
-- ============================================================================

-- ============================================================================
-- Table: xtrades_recommendations
-- ============================================================================
-- Stores RAG-generated recommendations for Xtrades alerts
-- Links recommendations to actual trade outcomes for learning
-- ============================================================================

CREATE TABLE IF NOT EXISTS xtrades_recommendations (
    id SERIAL PRIMARY KEY,
    trade_id INTEGER REFERENCES xtrades_trades(id) ON DELETE CASCADE,

    -- Recommendation details
    recommendation VARCHAR(20) NOT NULL,  -- 'TAKE', 'PASS', 'MONITOR'
    confidence INTEGER NOT NULL CHECK (confidence >= 0 AND confidence <= 100),
    reasoning TEXT NOT NULL,
    historical_evidence JSONB,  -- Array of similar trade outcomes
    risk_factors JSONB,  -- Array of identified risks
    suggested_adjustments TEXT,

    -- RAG metadata
    similar_trades_found INTEGER DEFAULT 0,
    top_trades_used INTEGER DEFAULT 0,
    statistics JSONB,  -- Aggregate stats from similar trades
    query_latency_ms INTEGER,  -- How long RAG query took

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Outcome tracking (filled after trade closes)
    actual_outcome VARCHAR(20),  -- 'WIN', 'LOSS', 'BREAK_EVEN', 'NOT_TAKEN'
    actual_pnl DECIMAL(10,2),
    actual_pnl_percent DECIMAL(10,2),
    actual_hold_days INTEGER,
    recommendation_correct BOOLEAN,
    outcome_recorded_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT chk_recommendation CHECK (recommendation IN ('TAKE', 'PASS', 'MONITOR')),
    CONSTRAINT chk_actual_outcome CHECK (actual_outcome IN ('WIN', 'LOSS', 'BREAK_EVEN', 'NOT_TAKEN', NULL))
);

-- Add comments
COMMENT ON TABLE xtrades_recommendations IS 'RAG-generated recommendations for options trades';
COMMENT ON COLUMN xtrades_recommendations.recommendation IS 'AI recommendation: TAKE, PASS, or MONITOR';
COMMENT ON COLUMN xtrades_recommendations.confidence IS 'Confidence level 0-100%';
COMMENT ON COLUMN xtrades_recommendations.reasoning IS 'AI reasoning for recommendation';
COMMENT ON COLUMN xtrades_recommendations.historical_evidence IS 'JSON array of similar trade outcomes';
COMMENT ON COLUMN xtrades_recommendations.statistics IS 'Aggregate statistics from similar trades';
COMMENT ON COLUMN xtrades_recommendations.recommendation_correct IS 'Whether recommendation matched actual outcome';

-- ============================================================================
-- Table: xtrades_rag_performance
-- ============================================================================
-- Aggregated performance metrics for RAG system
-- Updated periodically to track system accuracy
-- ============================================================================

CREATE TABLE IF NOT EXISTS xtrades_rag_performance (
    id SERIAL PRIMARY KEY,
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Overall metrics
    total_recommendations INTEGER DEFAULT 0,
    recommendations_with_outcomes INTEGER DEFAULT 0,
    overall_accuracy DECIMAL(5,2),  -- Percentage

    -- By recommendation type
    take_count INTEGER DEFAULT 0,
    take_correct INTEGER DEFAULT 0,
    take_accuracy DECIMAL(5,2),

    pass_count INTEGER DEFAULT 0,
    pass_correct INTEGER DEFAULT 0,
    pass_accuracy DECIMAL(5,2),

    monitor_count INTEGER DEFAULT 0,

    -- By confidence band
    high_confidence_count INTEGER DEFAULT 0,  -- 80-100%
    high_confidence_accuracy DECIMAL(5,2),

    medium_confidence_count INTEGER DEFAULT 0,  -- 50-79%
    medium_confidence_accuracy DECIMAL(5,2),

    low_confidence_count INTEGER DEFAULT 0,  -- 0-49%
    low_confidence_accuracy DECIMAL(5,2),

    -- P&L impact
    avg_pnl_per_take DECIMAL(10,2),
    avg_pnl_per_pass DECIMAL(10,2),
    total_pnl_impact DECIMAL(10,2),

    -- False positives/negatives
    false_positives INTEGER DEFAULT 0,  -- Recommended TAKE but lost
    false_negatives INTEGER DEFAULT 0,  -- Recommended PASS but would have won

    -- Time period
    period_start TIMESTAMP WITH TIME ZONE,
    period_end TIMESTAMP WITH TIME ZONE
);

COMMENT ON TABLE xtrades_rag_performance IS 'Aggregated RAG system performance metrics';

-- ============================================================================
-- Table: xtrades_rag_learning_weights
-- ============================================================================
-- Stores learning weights for individual trades
-- Used to boost/reduce influence of trades in future recommendations
-- ============================================================================

CREATE TABLE IF NOT EXISTS xtrades_rag_learning_weights (
    trade_id INTEGER PRIMARY KEY REFERENCES xtrades_trades(id) ON DELETE CASCADE,

    -- Learning metrics
    success_weight DECIMAL(5,2) DEFAULT 1.0,  -- Boost factor for this trade
    times_referenced INTEGER DEFAULT 0,  -- How many times used in recommendations
    recommendations_correct INTEGER DEFAULT 0,  -- How many were accurate
    recommendations_incorrect INTEGER DEFAULT 0,  -- How many were wrong
    accuracy_rate DECIMAL(5,2),  -- recommendations_correct / times_referenced

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT chk_success_weight CHECK (success_weight >= 0 AND success_weight <= 5.0)
);

COMMENT ON TABLE xtrades_rag_learning_weights IS 'Learning weights for individual trades in RAG system';
COMMENT ON COLUMN xtrades_rag_learning_weights.success_weight IS 'Multiplier for re-ranking (1.0 = neutral, >1.0 = boost, <1.0 = reduce)';

-- ============================================================================
-- INDEXES for Performance
-- ============================================================================

-- Recommendations indexes
CREATE INDEX IF NOT EXISTS idx_xtrades_recommendations_trade_id ON xtrades_recommendations(trade_id);
CREATE INDEX IF NOT EXISTS idx_xtrades_recommendations_recommendation ON xtrades_recommendations(recommendation);
CREATE INDEX IF NOT EXISTS idx_xtrades_recommendations_confidence ON xtrades_recommendations(confidence);
CREATE INDEX IF NOT EXISTS idx_xtrades_recommendations_outcome ON xtrades_recommendations(actual_outcome);
CREATE INDEX IF NOT EXISTS idx_xtrades_recommendations_correct ON xtrades_recommendations(recommendation_correct);
CREATE INDEX IF NOT EXISTS idx_xtrades_recommendations_created ON xtrades_recommendations(created_at DESC);

-- Composite index for accuracy analysis
CREATE INDEX IF NOT EXISTS idx_xtrades_recommendations_rec_outcome
    ON xtrades_recommendations(recommendation, actual_outcome, recommendation_correct);

-- Learning weights index
CREATE INDEX IF NOT EXISTS idx_xtrades_rag_learning_weights_accuracy
    ON xtrades_rag_learning_weights(accuracy_rate DESC);

-- ============================================================================
-- VIEWS for Analysis
-- ============================================================================

-- Recommendation accuracy by type
CREATE OR REPLACE VIEW v_rag_accuracy_by_recommendation AS
SELECT
    recommendation,
    COUNT(*) as total,
    COUNT(CASE WHEN recommendation_correct THEN 1 END) as correct,
    ROUND(COUNT(CASE WHEN recommendation_correct THEN 1 END)::NUMERIC / COUNT(*)::NUMERIC * 100, 2) as accuracy_pct,
    AVG(confidence) as avg_confidence,
    AVG(actual_pnl) as avg_pnl
FROM xtrades_recommendations
WHERE actual_outcome IS NOT NULL
GROUP BY recommendation;

COMMENT ON VIEW v_rag_accuracy_by_recommendation IS 'Accuracy metrics by recommendation type';

-- Confidence calibration analysis
CREATE OR REPLACE VIEW v_rag_confidence_calibration AS
SELECT
    CASE
        WHEN confidence >= 80 THEN 'High (80-100%)'
        WHEN confidence >= 50 THEN 'Medium (50-79%)'
        ELSE 'Low (0-49%)'
    END as confidence_band,
    COUNT(*) as total,
    COUNT(CASE WHEN recommendation_correct THEN 1 END) as correct,
    ROUND(COUNT(CASE WHEN recommendation_correct THEN 1 END)::NUMERIC / COUNT(*)::NUMERIC * 100, 2) as actual_accuracy,
    AVG(confidence) as avg_confidence
FROM xtrades_recommendations
WHERE actual_outcome IS NOT NULL
GROUP BY confidence_band
ORDER BY avg_confidence DESC;

COMMENT ON VIEW v_rag_confidence_calibration IS 'Confidence calibration - are high confidence recs actually more accurate?';

-- Most influential trades (best learning weights)
CREATE OR REPLACE VIEW v_rag_top_learning_trades AS
SELECT
    lw.trade_id,
    t.ticker,
    t.strategy,
    t.pnl,
    t.pnl_percent,
    lw.success_weight,
    lw.times_referenced,
    lw.accuracy_rate
FROM xtrades_rag_learning_weights lw
JOIN xtrades_trades t ON lw.trade_id = t.id
WHERE lw.times_referenced >= 3  -- Only trades used at least 3 times
ORDER BY lw.accuracy_rate DESC, lw.success_weight DESC
LIMIT 50;

COMMENT ON VIEW v_rag_top_learning_trades IS 'Top 50 most accurate trades for RAG learning';

-- ============================================================================
-- FUNCTIONS for Learning
-- ============================================================================

-- Function: Update learning weights after recommendation outcome
CREATE OR REPLACE FUNCTION update_rag_learning_weights(
    p_recommendation_id INTEGER
) RETURNS VOID AS $$
DECLARE
    v_rec RECORD;
    v_similar_trade_id INTEGER;
    v_was_correct BOOLEAN;
BEGIN
    -- Get recommendation details
    SELECT * INTO v_rec
    FROM xtrades_recommendations
    WHERE id = p_recommendation_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Recommendation % not found', p_recommendation_id;
    END IF;

    -- Determine if recommendation was correct
    v_was_correct := v_rec.recommendation_correct;

    -- Update weights for all similar trades used in this recommendation
    FOR v_similar_trade_id IN
        SELECT (jsonb_array_elements(v_rec.historical_evidence)->>'trade_id')::INTEGER
    LOOP
        -- Insert or update learning weight
        INSERT INTO xtrades_rag_learning_weights (
            trade_id,
            times_referenced,
            recommendations_correct,
            recommendations_incorrect
        )
        VALUES (
            v_similar_trade_id,
            1,
            CASE WHEN v_was_correct THEN 1 ELSE 0 END,
            CASE WHEN v_was_correct THEN 0 ELSE 1 END
        )
        ON CONFLICT (trade_id) DO UPDATE SET
            times_referenced = xtrades_rag_learning_weights.times_referenced + 1,
            recommendations_correct = xtrades_rag_learning_weights.recommendations_correct +
                CASE WHEN v_was_correct THEN 1 ELSE 0 END,
            recommendations_incorrect = xtrades_rag_learning_weights.recommendations_incorrect +
                CASE WHEN v_was_correct THEN 0 ELSE 1 END,
            accuracy_rate = (
                (xtrades_rag_learning_weights.recommendations_correct +
                 CASE WHEN v_was_correct THEN 1 ELSE 0 END)::NUMERIC /
                (xtrades_rag_learning_weights.times_referenced + 1)::NUMERIC * 100
            ),
            success_weight = CASE
                WHEN v_was_correct THEN LEAST(xtrades_rag_learning_weights.success_weight + 0.1, 5.0)
                ELSE GREATEST(xtrades_rag_learning_weights.success_weight - 0.1, 0.1)
            END,
            updated_at = NOW();
    END LOOP;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION update_rag_learning_weights IS 'Update learning weights for trades after recommendation outcome';

-- Function: Calculate RAG performance metrics
CREATE OR REPLACE FUNCTION calculate_rag_performance(
    p_days_back INTEGER DEFAULT 30
) RETURNS INTEGER AS $$
DECLARE
    v_performance_id INTEGER;
    v_period_start TIMESTAMP WITH TIME ZONE;
    v_period_end TIMESTAMP WITH TIME ZONE;
BEGIN
    v_period_end := NOW();
    v_period_start := NOW() - (p_days_back || ' days')::INTERVAL;

    -- Insert performance record
    INSERT INTO xtrades_rag_performance (
        calculated_at,
        period_start,
        period_end,
        total_recommendations,
        recommendations_with_outcomes,
        overall_accuracy,
        take_count,
        take_correct,
        take_accuracy,
        pass_count,
        pass_correct,
        pass_accuracy,
        monitor_count,
        high_confidence_count,
        high_confidence_accuracy,
        medium_confidence_count,
        medium_confidence_accuracy,
        low_confidence_count,
        low_confidence_accuracy,
        avg_pnl_per_take,
        avg_pnl_per_pass,
        total_pnl_impact,
        false_positives,
        false_negatives
    )
    SELECT
        NOW(),
        v_period_start,
        v_period_end,
        COUNT(*),
        COUNT(CASE WHEN actual_outcome IS NOT NULL THEN 1 END),
        ROUND(
            COUNT(CASE WHEN recommendation_correct THEN 1 END)::NUMERIC /
            NULLIF(COUNT(CASE WHEN actual_outcome IS NOT NULL THEN 1 END), 0)::NUMERIC * 100,
            2
        ),
        COUNT(CASE WHEN recommendation = 'TAKE' THEN 1 END),
        COUNT(CASE WHEN recommendation = 'TAKE' AND recommendation_correct THEN 1 END),
        ROUND(
            COUNT(CASE WHEN recommendation = 'TAKE' AND recommendation_correct THEN 1 END)::NUMERIC /
            NULLIF(COUNT(CASE WHEN recommendation = 'TAKE' AND actual_outcome IS NOT NULL THEN 1 END), 0)::NUMERIC * 100,
            2
        ),
        COUNT(CASE WHEN recommendation = 'PASS' THEN 1 END),
        COUNT(CASE WHEN recommendation = 'PASS' AND recommendation_correct THEN 1 END),
        ROUND(
            COUNT(CASE WHEN recommendation = 'PASS' AND recommendation_correct THEN 1 END)::NUMERIC /
            NULLIF(COUNT(CASE WHEN recommendation = 'PASS' AND actual_outcome IS NOT NULL THEN 1 END), 0)::NUMERIC * 100,
            2
        ),
        COUNT(CASE WHEN recommendation = 'MONITOR' THEN 1 END),
        COUNT(CASE WHEN confidence >= 80 THEN 1 END),
        ROUND(
            COUNT(CASE WHEN confidence >= 80 AND recommendation_correct THEN 1 END)::NUMERIC /
            NULLIF(COUNT(CASE WHEN confidence >= 80 AND actual_outcome IS NOT NULL THEN 1 END), 0)::NUMERIC * 100,
            2
        ),
        COUNT(CASE WHEN confidence >= 50 AND confidence < 80 THEN 1 END),
        ROUND(
            COUNT(CASE WHEN confidence >= 50 AND confidence < 80 AND recommendation_correct THEN 1 END)::NUMERIC /
            NULLIF(COUNT(CASE WHEN confidence >= 50 AND confidence < 80 AND actual_outcome IS NOT NULL THEN 1 END), 0)::NUMERIC * 100,
            2
        ),
        COUNT(CASE WHEN confidence < 50 THEN 1 END),
        ROUND(
            COUNT(CASE WHEN confidence < 50 AND recommendation_correct THEN 1 END)::NUMERIC /
            NULLIF(COUNT(CASE WHEN confidence < 50 AND actual_outcome IS NOT NULL THEN 1 END), 0)::NUMERIC * 100,
            2
        ),
        AVG(CASE WHEN recommendation = 'TAKE' THEN actual_pnl END),
        AVG(CASE WHEN recommendation = 'PASS' THEN actual_pnl END),
        SUM(actual_pnl),
        COUNT(CASE WHEN recommendation = 'TAKE' AND actual_pnl < 0 THEN 1 END),
        COUNT(CASE WHEN recommendation = 'PASS' AND actual_pnl > 0 THEN 1 END)
    FROM xtrades_recommendations
    WHERE created_at >= v_period_start
        AND created_at <= v_period_end
    RETURNING id INTO v_performance_id;

    RETURN v_performance_id;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION calculate_rag_performance IS 'Calculate and store RAG performance metrics for time period';

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Check table creation
SELECT
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as column_count
FROM information_schema.tables t
WHERE table_schema = 'public'
    AND table_name LIKE 'xtrades_r%'
ORDER BY table_name;

-- Check views
SELECT
    table_name as view_name
FROM information_schema.views
WHERE table_schema = 'public'
    AND table_name LIKE 'v_rag_%'
ORDER BY table_name;

-- Check functions
SELECT
    routine_name as function_name,
    routine_type
FROM information_schema.routines
WHERE routine_schema = 'public'
    AND routine_name LIKE '%rag%'
ORDER BY routine_name;

-- ============================================================================
-- SUCCESS MESSAGE
-- ============================================================================
SELECT 'RAG Recommendation Tracking schema created successfully!' as status;
