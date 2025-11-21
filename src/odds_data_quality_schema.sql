-- ============================================================================
-- Odds Data Quality Tracking Schema
-- ============================================================================
-- Purpose: Track validation results and data quality issues for betting odds
-- Database: magnus (PostgreSQL)
-- Created: 2025-11-18
-- ============================================================================

-- ============================================================================
-- Table 1: odds_data_quality_log
-- ============================================================================
-- Stores individual validation check results
-- ============================================================================

CREATE TABLE IF NOT EXISTS odds_data_quality_log (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(100) NOT NULL,

    -- Validation details
    rule_type VARCHAR(50) NOT NULL,  -- Type of validation rule applied
    severity VARCHAR(20) NOT NULL,   -- 'critical', 'warning', 'info'
    passed BOOLEAN NOT NULL,         -- Whether validation passed
    message TEXT NOT NULL,           -- Human-readable message
    details JSONB,                   -- Detailed validation data

    -- Timestamps
    checked_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Constraints
    CONSTRAINT chk_severity CHECK (severity IN ('critical', 'warning', 'info')),
    CONSTRAINT chk_rule_type CHECK (rule_type IN (
        'probability_sum',
        'team_record_correlation',
        'home_advantage',
        'historical_performance',
        'market_efficiency',
        'odds_range',
        'upset_detection',
        'data_freshness'
    ))
);

-- Add comments
COMMENT ON TABLE odds_data_quality_log IS 'Logs all validation checks performed on betting odds';
COMMENT ON COLUMN odds_data_quality_log.ticker IS 'Market ticker symbol being validated';
COMMENT ON COLUMN odds_data_quality_log.rule_type IS 'Type of validation rule (e.g., probability_sum, record_correlation)';
COMMENT ON COLUMN odds_data_quality_log.severity IS 'Severity level: critical (blocking), warning (suspicious), info (informational)';
COMMENT ON COLUMN odds_data_quality_log.passed IS 'Whether the validation check passed';
COMMENT ON COLUMN odds_data_quality_log.details IS 'JSON details about the validation (prices, deviations, etc.)';

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_odds_quality_ticker ON odds_data_quality_log(ticker);
CREATE INDEX IF NOT EXISTS idx_odds_quality_checked_at ON odds_data_quality_log(checked_at DESC);
CREATE INDEX IF NOT EXISTS idx_odds_quality_severity ON odds_data_quality_log(severity);
CREATE INDEX IF NOT EXISTS idx_odds_quality_passed ON odds_data_quality_log(passed);
CREATE INDEX IF NOT EXISTS idx_odds_quality_rule_type ON odds_data_quality_log(rule_type);

-- Composite index for common queries
CREATE INDEX IF NOT EXISTS idx_odds_quality_severity_failed
    ON odds_data_quality_log(severity, checked_at DESC)
    WHERE passed = FALSE;


-- ============================================================================
-- Table 2: odds_anomaly_alerts
-- ============================================================================
-- Stores anomaly alerts that require human review
-- ============================================================================

CREATE TABLE IF NOT EXISTS odds_anomaly_alerts (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(100) NOT NULL,

    -- Alert details
    alert_type VARCHAR(50) NOT NULL,  -- Type of anomaly detected
    severity VARCHAR(20) NOT NULL,    -- 'critical', 'warning', 'info'
    title TEXT NOT NULL,              -- Alert title
    description TEXT NOT NULL,        -- Detailed description

    -- Affected data
    away_team VARCHAR(100),
    home_team VARCHAR(100),
    away_win_price DECIMAL(5,4),
    home_win_price DECIMAL(5,4),

    -- Additional context
    metadata JSONB,                   -- Additional context (records, historical data, etc.)

    -- Alert status
    status VARCHAR(20) DEFAULT 'open',  -- 'open', 'acknowledged', 'resolved', 'false_positive'
    acknowledged_by VARCHAR(100),
    acknowledged_at TIMESTAMP WITH TIME ZONE,
    resolution_notes TEXT,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Constraints
    CONSTRAINT chk_alert_severity CHECK (severity IN ('critical', 'warning', 'info')),
    CONSTRAINT chk_alert_status CHECK (status IN ('open', 'acknowledged', 'resolved', 'false_positive'))
);

-- Add comments
COMMENT ON TABLE odds_anomaly_alerts IS 'Alerts for odds anomalies requiring human review';
COMMENT ON COLUMN odds_anomaly_alerts.alert_type IS 'Type of anomaly (e.g., reversed_odds, invalid_sum, missing_home_advantage)';
COMMENT ON COLUMN odds_anomaly_alerts.status IS 'Alert status: open (new), acknowledged (seen), resolved (fixed), false_positive (not an issue)';

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_odds_alerts_ticker ON odds_anomaly_alerts(ticker);
CREATE INDEX IF NOT EXISTS idx_odds_alerts_status ON odds_anomaly_alerts(status);
CREATE INDEX IF NOT EXISTS idx_odds_alerts_severity ON odds_anomaly_alerts(severity);
CREATE INDEX IF NOT EXISTS idx_odds_alerts_created_at ON odds_anomaly_alerts(created_at DESC);

-- Composite index for active alerts
CREATE INDEX IF NOT EXISTS idx_odds_alerts_active
    ON odds_anomaly_alerts(severity, created_at DESC)
    WHERE status = 'open';


-- ============================================================================
-- Table 3: odds_quality_metrics
-- ============================================================================
-- Stores aggregated data quality metrics over time
-- ============================================================================

CREATE TABLE IF NOT EXISTS odds_quality_metrics (
    id SERIAL PRIMARY KEY,

    -- Time period
    metric_date DATE NOT NULL,
    hour INTEGER,  -- Optional: hour of day (0-23) for hourly metrics

    -- Validation metrics
    total_validations INTEGER DEFAULT 0,
    passed_validations INTEGER DEFAULT 0,
    failed_validations INTEGER DEFAULT 0,

    -- Failures by severity
    critical_failures INTEGER DEFAULT 0,
    warning_failures INTEGER DEFAULT 0,

    -- Failures by rule type
    probability_sum_failures INTEGER DEFAULT 0,
    record_correlation_failures INTEGER DEFAULT 0,
    home_advantage_failures INTEGER DEFAULT 0,
    historical_performance_failures INTEGER DEFAULT 0,
    odds_range_failures INTEGER DEFAULT 0,
    data_freshness_failures INTEGER DEFAULT 0,

    -- Quality score (0-100)
    quality_score DECIMAL(5,2),  -- Percentage of validations passed

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Unique constraint on date/hour
    CONSTRAINT uq_odds_metrics_date_hour UNIQUE (metric_date, hour)
);

-- Add comments
COMMENT ON TABLE odds_quality_metrics IS 'Aggregated data quality metrics over time';
COMMENT ON COLUMN odds_quality_metrics.quality_score IS 'Overall quality score (0-100) based on validation pass rate';

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_odds_metrics_date ON odds_quality_metrics(metric_date DESC);
CREATE INDEX IF NOT EXISTS idx_odds_metrics_score ON odds_quality_metrics(quality_score);


-- ============================================================================
-- Table 4: odds_validation_rules_config
-- ============================================================================
-- Configuration for validation rules (allows dynamic tuning)
-- ============================================================================

CREATE TABLE IF NOT EXISTS odds_validation_rules_config (
    id SERIAL PRIMARY KEY,
    rule_type VARCHAR(50) UNIQUE NOT NULL,

    -- Rule configuration
    enabled BOOLEAN DEFAULT TRUE,
    severity VARCHAR(20) DEFAULT 'warning',

    -- Rule parameters (stored as JSON for flexibility)
    parameters JSONB,

    -- Description
    description TEXT,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add comments
COMMENT ON TABLE odds_validation_rules_config IS 'Configuration for validation rules (enables dynamic tuning)';
COMMENT ON COLUMN odds_validation_rules_config.parameters IS 'Rule-specific parameters (thresholds, limits, etc.)';

-- Insert default rule configurations
INSERT INTO odds_validation_rules_config (rule_type, enabled, severity, parameters, description) VALUES
('probability_sum', TRUE, 'critical',
    '{"min": 0.95, "max": 1.05}'::jsonb,
    'Validates that away_price + home_price is approximately 1.0'),

('team_record_correlation', TRUE, 'critical',
    '{"win_pct_threshold": 0.10}'::jsonb,
    'Validates that team with better record has higher win probability'),

('home_advantage', TRUE, 'warning',
    '{"min_advantage": 0.02, "max_advantage": 0.15}'::jsonb,
    'Validates that home team has appropriate advantage for evenly matched teams'),

('historical_performance', TRUE, 'warning',
    '{"max_deviation": 0.20, "min_games": 3}'::jsonb,
    'Validates odds align with historical head-to-head performance'),

('odds_range', TRUE, 'critical',
    '{"min": 0.01, "max": 0.99}'::jsonb,
    'Validates odds are within valid range'),

('data_freshness', TRUE, 'warning',
    '{"max_age_hours": 24}'::jsonb,
    'Validates that odds data is not stale'),

('upset_detection', TRUE, 'info',
    '{"win_pct_threshold": 0.10}'::jsonb,
    'Detects potential upsets (underdog has better record)')
ON CONFLICT (rule_type) DO NOTHING;


-- ============================================================================
-- Views for Easy Querying
-- ============================================================================

-- View: Recent critical failures
CREATE OR REPLACE VIEW v_odds_critical_failures AS
SELECT
    ticker,
    rule_type,
    message,
    details,
    checked_at
FROM odds_data_quality_log
WHERE severity = 'critical'
    AND passed = FALSE
    AND checked_at > NOW() - INTERVAL '7 days'
ORDER BY checked_at DESC;

COMMENT ON VIEW v_odds_critical_failures IS 'Recent critical validation failures (last 7 days)';


-- View: Active anomaly alerts
CREATE OR REPLACE VIEW v_odds_active_alerts AS
SELECT
    id,
    ticker,
    alert_type,
    severity,
    title,
    description,
    away_team,
    home_team,
    away_win_price,
    home_win_price,
    metadata,
    created_at
FROM odds_anomaly_alerts
WHERE status = 'open'
ORDER BY severity DESC, created_at DESC;

COMMENT ON VIEW v_odds_active_alerts IS 'Currently open anomaly alerts requiring review';


-- View: Daily quality trends
CREATE OR REPLACE VIEW v_odds_quality_trends AS
SELECT
    metric_date,
    total_validations,
    quality_score,
    critical_failures,
    warning_failures,
    ROUND(
        (critical_failures::numeric / NULLIF(total_validations, 0) * 100),
        2
    ) as critical_failure_rate,
    ROUND(
        (warning_failures::numeric / NULLIF(total_validations, 0) * 100),
        2
    ) as warning_failure_rate
FROM odds_quality_metrics
WHERE hour IS NULL  -- Daily metrics only
ORDER BY metric_date DESC;

COMMENT ON VIEW v_odds_quality_trends IS 'Daily data quality trends and failure rates';


-- View: Validation summary by rule type
CREATE OR REPLACE VIEW v_odds_validation_by_rule AS
SELECT
    rule_type,
    COUNT(*) as total_checks,
    SUM(CASE WHEN passed THEN 1 ELSE 0 END) as passed,
    SUM(CASE WHEN NOT passed THEN 1 ELSE 0 END) as failed,
    ROUND(
        (SUM(CASE WHEN passed THEN 1 ELSE 0 END)::numeric / COUNT(*) * 100),
        2
    ) as pass_rate,
    MAX(checked_at) as last_check
FROM odds_data_quality_log
WHERE checked_at > NOW() - INTERVAL '7 days'
GROUP BY rule_type
ORDER BY failed DESC;

COMMENT ON VIEW v_odds_validation_by_rule IS 'Validation statistics by rule type (last 7 days)';


-- ============================================================================
-- Functions for Metrics Aggregation
-- ============================================================================

-- Function to aggregate daily metrics
CREATE OR REPLACE FUNCTION aggregate_daily_odds_metrics(target_date DATE)
RETURNS VOID AS $$
BEGIN
    INSERT INTO odds_quality_metrics (
        metric_date,
        hour,
        total_validations,
        passed_validations,
        failed_validations,
        critical_failures,
        warning_failures,
        probability_sum_failures,
        record_correlation_failures,
        home_advantage_failures,
        historical_performance_failures,
        odds_range_failures,
        data_freshness_failures,
        quality_score
    )
    SELECT
        target_date,
        NULL,  -- Daily aggregate (no hour)
        COUNT(*) as total_validations,
        SUM(CASE WHEN passed THEN 1 ELSE 0 END) as passed_validations,
        SUM(CASE WHEN NOT passed THEN 1 ELSE 0 END) as failed_validations,
        SUM(CASE WHEN severity = 'critical' AND NOT passed THEN 1 ELSE 0 END) as critical_failures,
        SUM(CASE WHEN severity = 'warning' AND NOT passed THEN 1 ELSE 0 END) as warning_failures,
        SUM(CASE WHEN rule_type = 'probability_sum' AND NOT passed THEN 1 ELSE 0 END) as probability_sum_failures,
        SUM(CASE WHEN rule_type = 'team_record_correlation' AND NOT passed THEN 1 ELSE 0 END) as record_correlation_failures,
        SUM(CASE WHEN rule_type = 'home_advantage' AND NOT passed THEN 1 ELSE 0 END) as home_advantage_failures,
        SUM(CASE WHEN rule_type = 'historical_performance' AND NOT passed THEN 1 ELSE 0 END) as historical_performance_failures,
        SUM(CASE WHEN rule_type = 'odds_range' AND NOT passed THEN 1 ELSE 0 END) as odds_range_failures,
        SUM(CASE WHEN rule_type = 'data_freshness' AND NOT passed THEN 1 ELSE 0 END) as data_freshness_failures,
        ROUND(
            (SUM(CASE WHEN passed THEN 1 ELSE 0 END)::numeric / COUNT(*) * 100),
            2
        ) as quality_score
    FROM odds_data_quality_log
    WHERE DATE(checked_at) = target_date
    ON CONFLICT (metric_date, hour) DO UPDATE SET
        total_validations = EXCLUDED.total_validations,
        passed_validations = EXCLUDED.passed_validations,
        failed_validations = EXCLUDED.failed_validations,
        critical_failures = EXCLUDED.critical_failures,
        warning_failures = EXCLUDED.warning_failures,
        probability_sum_failures = EXCLUDED.probability_sum_failures,
        record_correlation_failures = EXCLUDED.record_correlation_failures,
        home_advantage_failures = EXCLUDED.home_advantage_failures,
        historical_performance_failures = EXCLUDED.historical_performance_failures,
        odds_range_failures = EXCLUDED.odds_range_failures,
        data_freshness_failures = EXCLUDED.data_freshness_failures,
        quality_score = EXCLUDED.quality_score,
        updated_at = NOW();
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION aggregate_daily_odds_metrics IS 'Aggregates validation metrics for a specific date';


-- Function to create anomaly alert
CREATE OR REPLACE FUNCTION create_odds_anomaly_alert(
    p_ticker VARCHAR(100),
    p_alert_type VARCHAR(50),
    p_severity VARCHAR(20),
    p_title TEXT,
    p_description TEXT,
    p_away_team VARCHAR(100) DEFAULT NULL,
    p_home_team VARCHAR(100) DEFAULT NULL,
    p_away_win_price DECIMAL(5,4) DEFAULT NULL,
    p_home_win_price DECIMAL(5,4) DEFAULT NULL,
    p_metadata JSONB DEFAULT NULL
)
RETURNS INTEGER AS $$
DECLARE
    alert_id INTEGER;
BEGIN
    -- Check if similar alert already exists and is open
    SELECT id INTO alert_id
    FROM odds_anomaly_alerts
    WHERE ticker = p_ticker
        AND alert_type = p_alert_type
        AND status = 'open'
        AND created_at > NOW() - INTERVAL '24 hours'
    LIMIT 1;

    IF alert_id IS NOT NULL THEN
        -- Update existing alert
        UPDATE odds_anomaly_alerts
        SET updated_at = NOW(),
            description = p_description,
            metadata = p_metadata
        WHERE id = alert_id;

        RETURN alert_id;
    ELSE
        -- Create new alert
        INSERT INTO odds_anomaly_alerts (
            ticker,
            alert_type,
            severity,
            title,
            description,
            away_team,
            home_team,
            away_win_price,
            home_win_price,
            metadata
        ) VALUES (
            p_ticker,
            p_alert_type,
            p_severity,
            p_title,
            p_description,
            p_away_team,
            p_home_team,
            p_away_win_price,
            p_home_win_price,
            p_metadata
        )
        RETURNING id INTO alert_id;

        RETURN alert_id;
    END IF;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION create_odds_anomaly_alert IS 'Creates or updates an anomaly alert (prevents duplicates)';


-- ============================================================================
-- Sample Queries
-- ============================================================================

-- Get recent critical failures
-- SELECT * FROM v_odds_critical_failures LIMIT 10;

-- Get all active alerts
-- SELECT * FROM v_odds_active_alerts;

-- Get quality trends for last 30 days
-- SELECT * FROM v_odds_quality_trends LIMIT 30;

-- Get validation stats by rule
-- SELECT * FROM v_odds_validation_by_rule;

-- Aggregate metrics for today
-- SELECT aggregate_daily_odds_metrics(CURRENT_DATE);

-- Create anomaly alert
-- SELECT create_odds_anomaly_alert(
--     'KXNFL-DAL-PHI',
--     'reversed_odds',
--     'critical',
--     'Reversed Odds Detected',
--     'Better team showing lower win probability',
--     'Dallas Cowboys',
--     'Philadelphia Eagles',
--     0.35,
--     0.65,
--     '{"away_record": "9-1", "home_record": "3-7"}'::jsonb
-- );
