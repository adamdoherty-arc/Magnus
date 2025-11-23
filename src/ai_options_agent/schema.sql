-- AI Options Agent Database Schema
-- Creates tables for storing AI analysis results and performance tracking

-- Table: ai_options_analyses
-- Stores detailed analysis results from the AI Options Agent
CREATE TABLE IF NOT EXISTS ai_options_analyses (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    analysis_date TIMESTAMP NOT NULL DEFAULT NOW(),
    strike_price DECIMAL(10,2),
    expiration_date DATE,
    dte INTEGER,

    -- Agent Scores (0-100)
    fundamental_score INTEGER CHECK (fundamental_score BETWEEN 0 AND 100),
    technical_score INTEGER CHECK (technical_score BETWEEN 0 AND 100),
    greeks_score INTEGER CHECK (greeks_score BETWEEN 0 AND 100),
    risk_score INTEGER CHECK (risk_score BETWEEN 0 AND 100),
    sentiment_score INTEGER CHECK (sentiment_score BETWEEN 0 AND 100),
    final_score INTEGER CHECK (final_score BETWEEN 0 AND 100),

    -- Recommendation
    recommendation VARCHAR(20) CHECK (recommendation IN ('STRONG_BUY', 'BUY', 'HOLD', 'CAUTION', 'AVOID')),
    strategy VARCHAR(50), -- CSP, Credit Spread, Iron Condor, etc.
    confidence INTEGER CHECK (confidence BETWEEN 0 AND 100),

    -- Reasoning (LLM-generated)
    reasoning TEXT,
    key_risks TEXT,
    key_opportunities TEXT,

    -- LLM metadata
    llm_model VARCHAR(50),
    llm_tokens_used INTEGER,
    processing_time_ms INTEGER,

    -- Outcome tracking (filled after trade execution)
    actual_outcome VARCHAR(20) CHECK (actual_outcome IN ('WIN', 'LOSS', 'EXPIRED', 'CLOSED_EARLY', NULL)),
    actual_pnl DECIMAL(10,2),
    accuracy_score INTEGER CHECK (accuracy_score BETWEEN 0 AND 100),

    -- Audit fields
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_ai_analyses_symbol ON ai_options_analyses(symbol);
CREATE INDEX IF NOT EXISTS idx_ai_analyses_date ON ai_options_analyses(analysis_date DESC);
CREATE INDEX IF NOT EXISTS idx_ai_analyses_score ON ai_options_analyses(final_score DESC);
CREATE INDEX IF NOT EXISTS idx_ai_analyses_recommendation ON ai_options_analyses(recommendation);

-- Table: ai_agent_performance
-- Tracks each agent's prediction accuracy over time for continuous improvement
CREATE TABLE IF NOT EXISTS ai_agent_performance (
    id SERIAL PRIMARY KEY,
    agent_name VARCHAR(50) NOT NULL,
    date DATE NOT NULL,
    predictions_made INTEGER DEFAULT 0,
    correct_predictions INTEGER DEFAULT 0,
    accuracy_rate DECIMAL(5,2),
    avg_confidence DECIMAL(5,2),
    avg_score DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(agent_name, date)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_ai_performance_agent ON ai_agent_performance(agent_name);
CREATE INDEX IF NOT EXISTS idx_ai_performance_date ON ai_agent_performance(date DESC);

-- Table: ai_options_watchlist
-- Stores user-selected symbols for AI monitoring (optional, can use existing watchlists)
CREATE TABLE IF NOT EXISTS ai_options_watchlist (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL UNIQUE,
    added_date TIMESTAMP DEFAULT NOW(),
    last_analyzed TIMESTAMP,
    alert_on_strong_buy BOOLEAN DEFAULT TRUE,
    notes TEXT
);

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_ai_analyses_updated_at
    BEFORE UPDATE ON ai_options_analyses
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Views for quick analysis

-- View: recent_strong_buys
CREATE OR REPLACE VIEW recent_strong_buys AS
SELECT
    symbol,
    strike_price,
    expiration_date,
    dte,
    final_score,
    confidence,
    reasoning,
    analysis_date
FROM ai_options_analyses
WHERE recommendation = 'STRONG_BUY'
    AND analysis_date >= NOW() - INTERVAL '7 days'
ORDER BY final_score DESC, analysis_date DESC;

-- View: agent_accuracy_summary
CREATE OR REPLACE VIEW agent_accuracy_summary AS
SELECT
    agent_name,
    SUM(predictions_made) as total_predictions,
    SUM(correct_predictions) as total_correct,
    AVG(accuracy_rate) as avg_accuracy_rate,
    MAX(date) as last_updated
FROM ai_agent_performance
WHERE date >= NOW() - INTERVAL '30 days'
GROUP BY agent_name
ORDER BY avg_accuracy_rate DESC;

-- Comments
COMMENT ON TABLE ai_options_analyses IS 'Stores AI-generated analysis and recommendations for options opportunities';
COMMENT ON TABLE ai_agent_performance IS 'Tracks prediction accuracy of each specialized agent over time';
COMMENT ON TABLE ai_options_watchlist IS 'User-selected symbols for continuous AI monitoring';
COMMENT ON VIEW recent_strong_buys IS 'STRONG_BUY recommendations from the last 7 days';
COMMENT ON VIEW agent_accuracy_summary IS '30-day accuracy summary for all agents';
