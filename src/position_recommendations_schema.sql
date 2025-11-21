-- Position Recommendations Schema
-- Stores AI-generated recommendations for option positions
-- Author: Claude Code
-- Date: 2025-11-10

-- Create position_recommendations table
CREATE TABLE IF NOT EXISTS position_recommendations (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    recommendation JSONB NOT NULL,  -- Full recommendation data
    user_action VARCHAR(50),  -- What the user actually did (accepted/ignored/overrode)
    user_action_timestamp TIMESTAMP,
    final_pnl DECIMAL(10, 2),  -- Actual P/L from following/ignoring advice
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    -- Ensure one active recommendation per symbol
    CONSTRAINT unique_symbol UNIQUE (symbol)
);

-- Create indexes for fast queries
CREATE INDEX IF NOT EXISTS idx_recommendations_symbol ON position_recommendations(symbol);
CREATE INDEX IF NOT EXISTS idx_recommendations_created_at ON position_recommendations(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_recommendations_updated_at ON position_recommendations(updated_at DESC);

-- Create index on recommendation JSONB for fast filtering
CREATE INDEX IF NOT EXISTS idx_recommendations_action
    ON position_recommendations USING gin ((recommendation->'action'));
CREATE INDEX IF NOT EXISTS idx_recommendations_confidence
    ON position_recommendations USING btree (CAST(recommendation->>'confidence' AS INTEGER));
CREATE INDEX IF NOT EXISTS idx_recommendations_urgency
    ON position_recommendations USING gin ((recommendation->'urgency'));

-- Create table for tracking recommendation accuracy
CREATE TABLE IF NOT EXISTS recommendation_outcomes (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    recommendation_action VARCHAR(50) NOT NULL,
    recommended_confidence INTEGER NOT NULL,
    user_followed BOOLEAN NOT NULL DEFAULT FALSE,
    position_closed_at TIMESTAMP,
    actual_pnl DECIMAL(10, 2),
    recommendation_timestamp TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for analytics
CREATE INDEX IF NOT EXISTS idx_outcomes_symbol ON recommendation_outcomes(symbol);
CREATE INDEX IF NOT EXISTS idx_outcomes_action ON recommendation_outcomes(recommendation_action);
CREATE INDEX IF NOT EXISTS idx_outcomes_followed ON recommendation_outcomes(user_followed);
CREATE INDEX IF NOT EXISTS idx_outcomes_timestamp ON recommendation_outcomes(recommendation_timestamp DESC);

-- Create view for recommendation accuracy metrics
CREATE OR REPLACE VIEW recommendation_accuracy AS
SELECT
    recommendation_action,
    COUNT(*) as total_recommendations,
    COUNT(*) FILTER (WHERE user_followed = TRUE) as followed_count,
    ROUND(100.0 * COUNT(*) FILTER (WHERE user_followed = TRUE) / COUNT(*), 1) as follow_rate,
    AVG(recommended_confidence) as avg_confidence,
    AVG(actual_pnl) FILTER (WHERE user_followed = TRUE) as avg_pnl_when_followed,
    AVG(actual_pnl) FILTER (WHERE user_followed = FALSE) as avg_pnl_when_ignored,
    COUNT(*) FILTER (WHERE actual_pnl > 0 AND user_followed = TRUE) as profitable_when_followed,
    COUNT(*) FILTER (WHERE actual_pnl > 0 AND user_followed = FALSE) as profitable_when_ignored
FROM recommendation_outcomes
WHERE position_closed_at IS NOT NULL
GROUP BY recommendation_action;

COMMENT ON TABLE position_recommendations IS 'Stores AI-generated recommendations for active positions';
COMMENT ON TABLE recommendation_outcomes IS 'Tracks recommendation accuracy and user actions for analytics';
COMMENT ON VIEW recommendation_accuracy IS 'Calculates accuracy metrics for recommendations by action type';
