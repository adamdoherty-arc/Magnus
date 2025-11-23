-- ============================================================================
-- Supply/Demand Zone Detection System - Database Schema
-- ============================================================================
-- Purpose: Track supply/demand zones, test history, and alerts
-- Database: magnus (PostgreSQL)
-- Created: 2025-11-09
-- ============================================================================

-- ============================================================================
-- Table 1: sd_zones
-- ============================================================================
-- Stores identified supply and demand zones from price action analysis
-- ============================================================================

CREATE TABLE IF NOT EXISTS sd_zones (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(20) NOT NULL,
    zone_type VARCHAR(10) NOT NULL, -- 'SUPPLY' or 'DEMAND'
    timeframe VARCHAR(10) NOT NULL, -- '1d', '4h', '1h', '15m'

    -- Zone boundaries
    zone_top DECIMAL(10,2) NOT NULL,
    zone_bottom DECIMAL(10,2) NOT NULL,
    zone_midpoint DECIMAL(10,2) NOT NULL,

    -- Formation details
    formed_date TIMESTAMP WITH TIME ZONE NOT NULL,
    formation_candle_index INTEGER,
    approach_volume BIGINT,
    departure_volume BIGINT,

    -- Strength indicators
    strength_score DECIMAL(5,2) DEFAULT 0.0, -- 0-100
    volume_ratio DECIMAL(10,2), -- departure_vol / approach_vol
    time_at_zone INTEGER, -- candles spent in zone
    rejection_candles INTEGER, -- candles showing rejection

    -- Zone status
    status VARCHAR(20) DEFAULT 'FRESH', -- FRESH, TESTED, WEAK, BROKEN
    test_count INTEGER DEFAULT 0,
    last_test_date TIMESTAMP WITH TIME ZONE,
    broken_date TIMESTAMP WITH TIME ZONE,

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    notes TEXT,

    CONSTRAINT chk_zone_type CHECK (zone_type IN ('SUPPLY', 'DEMAND')),
    CONSTRAINT chk_zone_status CHECK (status IN ('FRESH', 'TESTED', 'WEAK', 'BROKEN')),
    CONSTRAINT chk_timeframe CHECK (timeframe IN ('1d', '4h', '1h', '15m'))
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_sd_zones_ticker ON sd_zones(ticker);
CREATE INDEX IF NOT EXISTS idx_sd_zones_status ON sd_zones(status);
CREATE INDEX IF NOT EXISTS idx_sd_zones_active ON sd_zones(is_active);
CREATE INDEX IF NOT EXISTS idx_sd_zones_type ON sd_zones(zone_type);
CREATE INDEX IF NOT EXISTS idx_sd_zones_ticker_active ON sd_zones(ticker, is_active);
CREATE INDEX IF NOT EXISTS idx_sd_zones_strength ON sd_zones(strength_score DESC);
CREATE INDEX IF NOT EXISTS idx_sd_zones_formed_date ON sd_zones(formed_date DESC);

-- Comments for documentation
COMMENT ON TABLE sd_zones IS 'Supply and demand zones detected from price action';
COMMENT ON COLUMN sd_zones.zone_type IS 'SUPPLY=resistance/selling pressure, DEMAND=support/buying pressure';
COMMENT ON COLUMN sd_zones.strength_score IS 'Zone strength 0-100 based on volume, rejection, and tests';
COMMENT ON COLUMN sd_zones.status IS 'FRESH=untested, TESTED=held, WEAK=multiple tests, BROKEN=penetrated';
COMMENT ON COLUMN sd_zones.volume_ratio IS 'Departure volume / approach volume (higher = stronger)';
COMMENT ON COLUMN sd_zones.zone_midpoint IS 'Middle of zone - ideal entry point';

-- ============================================================================
-- Table 2: sd_zone_tests
-- ============================================================================
-- Tracks each time price tests a zone (touches, penetrations, rejections)
-- ============================================================================

CREATE TABLE IF NOT EXISTS sd_zone_tests (
    id SERIAL PRIMARY KEY,
    zone_id INTEGER NOT NULL REFERENCES sd_zones(id) ON DELETE CASCADE,

    -- Test details
    test_date TIMESTAMP WITH TIME ZONE NOT NULL,
    test_price DECIMAL(10,2) NOT NULL,
    test_type VARCHAR(20) NOT NULL, -- 'TOUCH', 'PENETRATION', 'REJECTION', 'BREAK'

    -- Price action during test
    penetration_percent DECIMAL(5,2), -- How far into zone (%)
    reaction_candles INTEGER, -- Candles to react
    bounce_percent DECIMAL(5,2), -- % bounce from zone
    test_volume BIGINT,

    -- Test outcome
    held BOOLEAN, -- Did zone hold?
    broke_through BOOLEAN, -- Did price break through?

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT chk_test_type CHECK (test_type IN ('TOUCH', 'PENETRATION', 'REJECTION', 'BREAK'))
);

CREATE INDEX IF NOT EXISTS idx_sd_zone_tests_zone_id ON sd_zone_tests(zone_id);
CREATE INDEX IF NOT EXISTS idx_sd_zone_tests_date ON sd_zone_tests(test_date DESC);
CREATE INDEX IF NOT EXISTS idx_sd_zone_tests_type ON sd_zone_tests(test_type);

COMMENT ON TABLE sd_zone_tests IS 'Historical record of zone test events';
COMMENT ON COLUMN sd_zone_tests.test_type IS 'TOUCH=price near zone, PENETRATION=price in zone, REJECTION=wick reversal, BREAK=zone broken';
COMMENT ON COLUMN sd_zone_tests.penetration_percent IS 'Percentage of zone height price penetrated (0-100)';
COMMENT ON COLUMN sd_zone_tests.held IS 'True if zone held and price reversed';

-- ============================================================================
-- Table 3: sd_alerts
-- ============================================================================
-- Tracks alerts sent via Telegram for zone events
-- ============================================================================

CREATE TABLE IF NOT EXISTS sd_alerts (
    id SERIAL PRIMARY KEY,
    zone_id INTEGER NOT NULL REFERENCES sd_zones(id) ON DELETE CASCADE,
    ticker VARCHAR(20) NOT NULL,

    -- Alert details
    alert_type VARCHAR(30) NOT NULL, -- Alert category
    alert_price DECIMAL(10,2) NOT NULL,
    zone_type VARCHAR(10) NOT NULL,

    -- Trading context
    distance_to_zone DECIMAL(5,2), -- % distance
    zone_strength DECIMAL(5,2),
    setup_quality VARCHAR(20), -- 'HIGH', 'MEDIUM', 'LOW'

    -- Alert delivery
    sent_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    telegram_message_id VARCHAR(255),
    status VARCHAR(20) DEFAULT 'sent', -- 'sent', 'failed'
    error_message TEXT,

    CONSTRAINT chk_alert_type CHECK (alert_type IN (
        'PRICE_ENTERING_DEMAND', 'PRICE_AT_DEMAND', 'PRICE_ENTERING_SUPPLY',
        'PRICE_AT_SUPPLY', 'ZONE_BOUNCE', 'ZONE_BREAK'
    )),
    CONSTRAINT chk_setup_quality CHECK (setup_quality IN ('HIGH', 'MEDIUM', 'LOW')),
    CONSTRAINT chk_alert_status CHECK (status IN ('sent', 'failed'))
);

CREATE INDEX IF NOT EXISTS idx_sd_alerts_zone_id ON sd_alerts(zone_id);
CREATE INDEX IF NOT EXISTS idx_sd_alerts_ticker ON sd_alerts(ticker);
CREATE INDEX IF NOT EXISTS idx_sd_alerts_sent_at ON sd_alerts(sent_at DESC);
CREATE INDEX IF NOT EXISTS idx_sd_alerts_type ON sd_alerts(alert_type);
CREATE INDEX IF NOT EXISTS idx_sd_alerts_quality ON sd_alerts(setup_quality);

COMMENT ON TABLE sd_alerts IS 'Alert history for supply/demand zone events';
COMMENT ON COLUMN sd_alerts.alert_type IS 'Type of zone event that triggered alert';
COMMENT ON COLUMN sd_alerts.setup_quality IS 'Trade setup quality based on zone strength and test history';
COMMENT ON COLUMN sd_alerts.telegram_message_id IS 'Telegram message ID for tracking';

-- ============================================================================
-- Table 4: sd_scan_log
-- ============================================================================
-- Audit log for scanner operations (zone detection and price monitoring)
-- ============================================================================

CREATE TABLE IF NOT EXISTS sd_scan_log (
    id SERIAL PRIMARY KEY,
    scan_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    scan_type VARCHAR(50), -- 'ZONE_DETECTION', 'PRICE_MONITORING', 'ZONE_CLEANUP'

    -- Scan results
    tickers_scanned INTEGER DEFAULT 0,
    zones_found INTEGER DEFAULT 0,
    zones_updated INTEGER DEFAULT 0,
    alerts_sent INTEGER DEFAULT 0,

    -- Performance
    duration_seconds DECIMAL(10,2),
    status VARCHAR(50) DEFAULT 'success', -- 'success', 'partial', 'failed'
    errors TEXT,

    CONSTRAINT chk_scan_status CHECK (status IN ('success', 'partial', 'failed')),
    CONSTRAINT chk_scan_type CHECK (scan_type IN ('ZONE_DETECTION', 'PRICE_MONITORING', 'ZONE_CLEANUP'))
);

CREATE INDEX IF NOT EXISTS idx_sd_scan_log_timestamp ON sd_scan_log(scan_timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_sd_scan_log_status ON sd_scan_log(status);
CREATE INDEX IF NOT EXISTS idx_sd_scan_log_type ON sd_scan_log(scan_type);

COMMENT ON TABLE sd_scan_log IS 'Audit log for zone scanner operations';
COMMENT ON COLUMN sd_scan_log.scan_type IS 'Type of scan: ZONE_DETECTION (find new zones), PRICE_MONITORING (check for touches), ZONE_CLEANUP (remove old zones)';

-- ============================================================================
-- USEFUL QUERIES
-- ============================================================================

-- Get all active high-strength zones
-- SELECT * FROM sd_zones
-- WHERE is_active = TRUE AND status != 'BROKEN' AND strength_score >= 70
-- ORDER BY strength_score DESC;

-- Get zones currently being tested
-- SELECT z.*, t.test_type, t.penetration_percent
-- FROM sd_zones z
-- JOIN sd_zone_tests t ON z.id = t.zone_id
-- WHERE t.test_date >= NOW() - INTERVAL '1 hour'
-- ORDER BY t.test_date DESC;

-- Get alert statistics by ticker
-- SELECT ticker, COUNT(*) as alert_count,
--        AVG(zone_strength) as avg_strength,
--        COUNT(CASE WHEN setup_quality = 'HIGH' THEN 1 END) as high_quality_count
-- FROM sd_alerts
-- WHERE sent_at >= NOW() - INTERVAL '7 days'
-- GROUP BY ticker
-- ORDER BY alert_count DESC;

-- Get zone test success rate
-- SELECT z.ticker, z.zone_type,
--        COUNT(t.id) as total_tests,
--        SUM(CASE WHEN t.held THEN 1 ELSE 0 END) as successful_holds,
--        ROUND(100.0 * SUM(CASE WHEN t.held THEN 1 ELSE 0 END) / COUNT(t.id), 2) as success_rate
-- FROM sd_zones z
-- LEFT JOIN sd_zone_tests t ON z.id = t.zone_id
-- WHERE z.test_count > 0
-- GROUP BY z.ticker, z.zone_type
-- HAVING COUNT(t.id) >= 3
-- ORDER BY success_rate DESC;

-- Get scanner performance metrics
-- SELECT scan_type,
--        COUNT(*) as total_scans,
--        AVG(duration_seconds) as avg_duration,
--        SUM(zones_found) as total_zones_found,
--        SUM(alerts_sent) as total_alerts_sent,
--        COUNT(CASE WHEN status = 'success' THEN 1 END) as successful_scans
-- FROM sd_scan_log
-- WHERE scan_timestamp >= NOW() - INTERVAL '30 days'
-- GROUP BY scan_type;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Verify table creation
SELECT
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as column_count
FROM information_schema.tables t
WHERE table_schema = 'public'
    AND table_name LIKE 'sd_%'
ORDER BY table_name;

-- Verify indexes
SELECT
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
    AND tablename LIKE 'sd_%'
ORDER BY tablename, indexname;

-- Check row counts
SELECT 'sd_zones' as table_name, COUNT(*) as row_count FROM sd_zones
UNION ALL
SELECT 'sd_zone_tests', COUNT(*) FROM sd_zone_tests
UNION ALL
SELECT 'sd_alerts', COUNT(*) FROM sd_alerts
UNION ALL
SELECT 'sd_scan_log', COUNT(*) FROM sd_scan_log;

-- ============================================================================
-- SUCCESS MESSAGE
-- ============================================================================
SELECT 'Supply/Demand Zone Detection schema created successfully!' as status;
