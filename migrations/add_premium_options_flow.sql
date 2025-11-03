-- ============================================================================
-- PREMIUM OPTIONS FLOW TABLES - Magnus Trading Platform
-- Created: 2025-11-02
-- Purpose: Track institutional options flow, premium inflows/outflows, and identify trading opportunities
-- ============================================================================

-- Table 1: Options Flow Data (Daily snapshots)
CREATE TABLE IF NOT EXISTS options_flow (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    flow_date DATE NOT NULL,
    call_volume BIGINT DEFAULT 0,
    put_volume BIGINT DEFAULT 0,
    call_premium DECIMAL(15,2) DEFAULT 0,
    put_premium DECIMAL(15,2) DEFAULT 0,
    net_premium_flow DECIMAL(15,2) DEFAULT 0,
    put_call_ratio DECIMAL(10,4) DEFAULT 0,
    unusual_activity BOOLEAN DEFAULT false,
    flow_sentiment VARCHAR(20) DEFAULT 'Neutral',
    avg_call_premium DECIMAL(10,2) DEFAULT 0,
    avg_put_premium DECIMAL(10,2) DEFAULT 0,
    total_volume BIGINT DEFAULT 0,
    total_open_interest BIGINT DEFAULT 0,
    iv_rank DECIMAL(5,2),
    last_updated TIMESTAMP DEFAULT NOW(),
    UNIQUE(symbol, flow_date)
);

-- Table 2: Options Flow Analysis (Aggregated insights)
CREATE TABLE IF NOT EXISTS options_flow_analysis (
    symbol VARCHAR(10) PRIMARY KEY,
    flow_trend_7d VARCHAR(20) DEFAULT 'Stable',
    net_flow_7d DECIMAL(15,2) DEFAULT 0,
    net_flow_30d DECIMAL(15,2) DEFAULT 0,
    dominant_strategy VARCHAR(30) DEFAULT 'Balanced',
    ai_recommendation TEXT,
    opportunity_score DECIMAL(5,2) DEFAULT 0,
    best_action VARCHAR(20) DEFAULT 'WAIT',
    risk_level VARCHAR(20) DEFAULT 'Medium',
    confidence DECIMAL(5,4) DEFAULT 0,
    key_insights TEXT[],
    avg_put_call_ratio_7d DECIMAL(10,4),
    unusual_activity_count_7d INTEGER DEFAULT 0,
    current_price DECIMAL(10,2),
    target_delta DECIMAL(5,4),
    recommended_strike DECIMAL(10,2),
    recommended_expiration DATE,
    expected_premium DECIMAL(10,2),
    win_probability DECIMAL(5,4),
    sector VARCHAR(100),
    market_cap BIGINT,
    last_updated TIMESTAMP DEFAULT NOW()
);

-- Table 3: Premium Flow Opportunities (Top ranked opportunities)
CREATE TABLE IF NOT EXISTS premium_flow_opportunities (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    opportunity_type VARCHAR(30) NOT NULL,
    opportunity_score DECIMAL(5,2) NOT NULL,
    net_flow_7d DECIMAL(15,2),
    put_call_ratio DECIMAL(10,4),
    flow_sentiment VARCHAR(20),
    trend_direction VARCHAR(20),
    entry_price DECIMAL(10,2),
    target_strike DECIMAL(10,2),
    target_premium DECIMAL(10,2),
    expected_return DECIMAL(10,4),
    risk_score DECIMAL(5,2),
    confidence DECIMAL(5,4),
    ai_rationale TEXT,
    recommended_position_size DECIMAL(10,2),
    max_loss DECIMAL(10,2),
    breakeven_price DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

-- Table 4: Flow Alerts (Unusual activity tracking)
CREATE TABLE IF NOT EXISTS options_flow_alerts (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    alert_type VARCHAR(50) NOT NULL,
    alert_severity VARCHAR(20) DEFAULT 'Medium',
    description TEXT NOT NULL,
    trigger_value DECIMAL(15,2),
    threshold_value DECIMAL(15,2),
    flow_data JSONB,
    triggered_at TIMESTAMP DEFAULT NOW(),
    is_read BOOLEAN DEFAULT false,
    is_dismissed BOOLEAN DEFAULT false
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_options_flow_symbol ON options_flow(symbol);
CREATE INDEX IF NOT EXISTS idx_options_flow_date ON options_flow(flow_date);
CREATE INDEX IF NOT EXISTS idx_options_flow_symbol_date ON options_flow(symbol, flow_date);
CREATE INDEX IF NOT EXISTS idx_flow_analysis_score ON options_flow_analysis(opportunity_score DESC);
CREATE INDEX IF NOT EXISTS idx_flow_opportunities_score ON premium_flow_opportunities(opportunity_score DESC);
CREATE INDEX IF NOT EXISTS idx_flow_opportunities_active ON premium_flow_opportunities(is_active, opportunity_score DESC);
CREATE INDEX IF NOT EXISTS idx_flow_alerts_symbol ON options_flow_alerts(symbol);
CREATE INDEX IF NOT EXISTS idx_flow_alerts_unread ON options_flow_alerts(is_read, triggered_at DESC);

-- Function to calculate net premium flow
CREATE OR REPLACE FUNCTION calculate_net_flow()
RETURNS TRIGGER AS $$
BEGIN
    NEW.net_premium_flow := NEW.call_premium - NEW.put_premium;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-calculate net flow
DROP TRIGGER IF EXISTS trigger_calculate_net_flow ON options_flow;
CREATE TRIGGER trigger_calculate_net_flow
    BEFORE INSERT OR UPDATE ON options_flow
    FOR EACH ROW
    EXECUTE FUNCTION calculate_net_flow();

-- Function to update analysis timestamp
CREATE OR REPLACE FUNCTION update_flow_analysis_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_updated := NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to update analysis timestamp
DROP TRIGGER IF EXISTS trigger_update_flow_analysis_timestamp ON options_flow_analysis;
CREATE TRIGGER trigger_update_flow_analysis_timestamp
    BEFORE UPDATE ON options_flow_analysis
    FOR EACH ROW
    EXECUTE FUNCTION update_flow_analysis_timestamp();

-- Sample data comments
COMMENT ON TABLE options_flow IS 'Daily options volume and premium flow data for tracking institutional money movement';
COMMENT ON TABLE options_flow_analysis IS 'Aggregated flow analysis with AI recommendations and opportunity scoring';
COMMENT ON TABLE premium_flow_opportunities IS 'Top-ranked trading opportunities based on options flow analysis';
COMMENT ON TABLE options_flow_alerts IS 'Real-time alerts for unusual options activity and flow spikes';
