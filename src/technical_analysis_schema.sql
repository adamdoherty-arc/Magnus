-- Technical Analysis Caching Schema
-- Stores Fibonacci levels, Volume Profile, and Order Flow data to avoid repeated calculations

-- Table: fibonacci_levels
-- Stores calculated Fibonacci retracement and extension levels
CREATE TABLE IF NOT EXISTS fibonacci_levels (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL,
    timeframe VARCHAR(10) NOT NULL,  -- e.g., '1d', '1wk', '1h'
    period VARCHAR(10) NOT NULL,     -- e.g., '1mo', '3mo', '6mo', '1y'
    swing_type VARCHAR(20) NOT NULL, -- 'UPTREND_RETRACEMENT' or 'DOWNTREND_RETRACEMENT'
    swing_high NUMERIC(12, 4) NOT NULL,
    swing_low NUMERIC(12, 4) NOT NULL,
    high_date TIMESTAMP NOT NULL,
    low_date TIMESTAMP NOT NULL,

    -- Retracement levels (JSONB for flexibility)
    retracement_levels JSONB NOT NULL,
    -- Example: {"0%": 100.0, "23.6%": 95.0, "38.2%": 92.0, ...}

    -- Extension levels (JSONB)
    extension_levels JSONB,

    -- Golden Zone
    golden_zone_top NUMERIC(12, 4),
    golden_zone_bottom NUMERIC(12, 4),

    -- Metadata
    price_range NUMERIC(12, 4),
    range_pct NUMERIC(6, 2),

    -- Caching info
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,

    CONSTRAINT unique_fibonacci_swing UNIQUE (ticker, timeframe, period, swing_high, swing_low, high_date)
);

-- Index for fast lookups
CREATE INDEX IF NOT EXISTS idx_fibonacci_ticker ON fibonacci_levels(ticker);
CREATE INDEX IF NOT EXISTS idx_fibonacci_active ON fibonacci_levels(ticker, is_active) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_fibonacci_expires ON fibonacci_levels(expires_at);

-- Table: fibonacci_confluence_zones
-- Stores confluence zones where multiple Fibonacci levels overlap
CREATE TABLE IF NOT EXISTS fibonacci_confluence_zones (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL,
    timeframe VARCHAR(10) NOT NULL,
    period VARCHAR(10) NOT NULL,

    -- Confluence details
    price NUMERIC(12, 4) NOT NULL,
    price_min NUMERIC(12, 4) NOT NULL,
    price_max NUMERIC(12, 4) NOT NULL,
    level_count INTEGER NOT NULL,      -- Number of overlapping levels
    strength INTEGER NOT NULL,          -- Strength score (same as level_count)
    zone_width_pct NUMERIC(6, 4),

    -- Contributing levels (JSONB array)
    levels JSONB NOT NULL,
    -- Example: [{"price": 150.5, "level": "61.8%", "swing_type": "UPTREND"}, ...]

    -- Caching info
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,

    CONSTRAINT unique_confluence UNIQUE (ticker, timeframe, period, price)
);

CREATE INDEX IF NOT EXISTS idx_confluence_ticker ON fibonacci_confluence_zones(ticker);
CREATE INDEX IF NOT EXISTS idx_confluence_strength ON fibonacci_confluence_zones(ticker, strength) WHERE is_active = TRUE;

-- Table: volume_profile_data
-- Stores Volume Profile analysis results (POC, VAH, VAL, etc.)
CREATE TABLE IF NOT EXISTS volume_profile_data (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL,
    timeframe VARCHAR(10) NOT NULL,
    period VARCHAR(10) NOT NULL,

    -- Volume Profile metrics
    poc_price NUMERIC(12, 4) NOT NULL,      -- Point of Control
    poc_volume BIGINT NOT NULL,
    poc_pct_of_total NUMERIC(6, 2),

    vah_price NUMERIC(12, 4) NOT NULL,      -- Value Area High
    val_price NUMERIC(12, 4) NOT NULL,      -- Value Area Low
    value_area_volume BIGINT,
    value_area_pct NUMERIC(6, 2),

    total_volume BIGINT NOT NULL,

    -- Volume distribution (JSONB)
    price_levels JSONB NOT NULL,            -- Array of price levels
    volume_at_price JSONB NOT NULL,         -- Volume at each price level
    volume_pct_at_price JSONB NOT NULL,     -- Percentage at each price

    -- High/Low Volume Nodes
    high_volume_nodes JSONB,                -- Array of HVN prices
    low_volume_nodes JSONB,                 -- Array of LVN prices

    -- Caching info
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,

    CONSTRAINT unique_volume_profile UNIQUE (ticker, timeframe, period, calculated_at)
);

CREATE INDEX IF NOT EXISTS idx_volume_profile_ticker ON volume_profile_data(ticker);
CREATE INDEX IF NOT EXISTS idx_volume_profile_active ON volume_profile_data(ticker, is_active) WHERE is_active = TRUE;

-- Table: order_flow_data
-- Stores Order Flow (CVD - Cumulative Volume Delta) analysis
CREATE TABLE IF NOT EXISTS order_flow_data (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL,
    timeframe VARCHAR(10) NOT NULL,
    period VARCHAR(10) NOT NULL,

    -- Current CVD metrics
    current_cvd NUMERIC(20, 2) NOT NULL,
    cvd_change_1d NUMERIC(20, 2),
    cvd_change_5d NUMERIC(20, 2),
    cvd_trend VARCHAR(10),                  -- 'BULLISH' or 'BEARISH'

    -- CVD time series (JSONB)
    cvd_series JSONB NOT NULL,
    -- Example: [{"date": "2025-01-15", "cvd": 1500000}, ...]

    -- Divergences
    divergence_count INTEGER DEFAULT 0,
    divergences JSONB,
    -- Example: [{"type": "BULLISH", "date": "2025-01-15", "strength": "STRONG"}, ...]

    -- Pressure metrics
    buy_pressure_pct NUMERIC(6, 2),
    sell_pressure_pct NUMERIC(6, 2),
    net_pressure VARCHAR(10),               -- 'BUYERS' or 'SELLERS'

    -- Caching info
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,

    CONSTRAINT unique_order_flow UNIQUE (ticker, timeframe, period, calculated_at)
);

CREATE INDEX IF NOT EXISTS idx_order_flow_ticker ON order_flow_data(ticker);
CREATE INDEX IF NOT EXISTS idx_order_flow_active ON order_flow_data(ticker, is_active) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_order_flow_divergences ON order_flow_data(ticker, divergence_count) WHERE divergence_count > 0;

-- Table: technical_analysis_cache_metadata
-- Tracks cache status and TTL for each analysis type
CREATE TABLE IF NOT EXISTS technical_analysis_cache_metadata (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL,
    analysis_type VARCHAR(30) NOT NULL,     -- 'fibonacci', 'volume_profile', 'order_flow'
    timeframe VARCHAR(10) NOT NULL,
    period VARCHAR(10) NOT NULL,

    -- Cache metadata
    last_calculated TIMESTAMP NOT NULL,
    cache_hits INTEGER DEFAULT 0,
    cache_misses INTEGER DEFAULT 0,
    avg_calculation_time_ms INTEGER,

    -- TTL settings (in seconds)
    ttl_seconds INTEGER DEFAULT 3600,       -- 1 hour default
    next_refresh TIMESTAMP,

    is_stale BOOLEAN DEFAULT FALSE,

    CONSTRAINT unique_cache_metadata UNIQUE (ticker, analysis_type, timeframe, period)
);

CREATE INDEX IF NOT EXISTS idx_cache_metadata_ticker ON technical_analysis_cache_metadata(ticker, analysis_type);
CREATE INDEX IF NOT EXISTS idx_cache_metadata_stale ON technical_analysis_cache_metadata(is_stale, next_refresh);

-- Cleanup function to remove expired cache entries
CREATE OR REPLACE FUNCTION cleanup_technical_analysis_cache()
RETURNS void AS $$
BEGIN
    -- Mark expired Fibonacci levels as inactive
    UPDATE fibonacci_levels
    SET is_active = FALSE
    WHERE expires_at < CURRENT_TIMESTAMP AND is_active = TRUE;

    -- Mark expired confluence zones as inactive
    UPDATE fibonacci_confluence_zones
    SET is_active = FALSE
    WHERE expires_at < CURRENT_TIMESTAMP AND is_active = TRUE;

    -- Mark expired volume profiles as inactive
    UPDATE volume_profile_data
    SET is_active = FALSE
    WHERE expires_at < CURRENT_TIMESTAMP AND is_active = TRUE;

    -- Mark expired order flow data as inactive
    UPDATE order_flow_data
    SET is_active = FALSE
    WHERE expires_at < CURRENT_TIMESTAMP AND is_active = TRUE;

    -- Update metadata stale flag
    UPDATE technical_analysis_cache_metadata
    SET is_stale = TRUE
    WHERE next_refresh < CURRENT_TIMESTAMP AND is_stale = FALSE;
END;
$$ LANGUAGE plpgsql;

-- Comments for documentation
COMMENT ON TABLE fibonacci_levels IS 'Cached Fibonacci retracement and extension levels for stocks';
COMMENT ON TABLE fibonacci_confluence_zones IS 'Fibonacci confluence zones where multiple levels overlap';
COMMENT ON TABLE volume_profile_data IS 'Volume Profile analysis including POC, VAH, VAL';
COMMENT ON TABLE order_flow_data IS 'Order Flow (CVD) analysis and divergences';
COMMENT ON TABLE technical_analysis_cache_metadata IS 'Cache metadata and TTL tracking';

COMMENT ON FUNCTION cleanup_technical_analysis_cache IS 'Cleanup function to mark expired cache entries as inactive';
