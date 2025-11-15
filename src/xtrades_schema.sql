-- ============================================================================
-- Xtrades Watchlists Feature - Database Schema
-- ============================================================================
-- Purpose: Track and analyze trades from Xtrades.net profiles
-- Database: magnus (PostgreSQL)
-- Created: 2025-11-02
-- ============================================================================

-- ============================================================================
-- Table 1: xtrades_profiles
-- ============================================================================
-- Stores Xtrades.net profiles to monitor for trading alerts
-- Each profile represents a trader whose alerts we want to track
-- ============================================================================

CREATE TABLE IF NOT EXISTS xtrades_profiles (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    display_name VARCHAR(255),
    active BOOLEAN DEFAULT TRUE,
    added_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_sync TIMESTAMP WITH TIME ZONE,
    last_sync_status VARCHAR(50), -- 'success', 'error', 'pending'
    total_trades_scraped INTEGER DEFAULT 0,
    notes TEXT,
    CONSTRAINT chk_sync_status CHECK (last_sync_status IN ('success', 'error', 'pending', NULL))
);

-- Add comments for documentation
COMMENT ON TABLE xtrades_profiles IS 'Stores Xtrades.net profiles to monitor for trading alerts';
COMMENT ON COLUMN xtrades_profiles.username IS 'Unique Xtrades.net username';
COMMENT ON COLUMN xtrades_profiles.active IS 'Whether this profile is actively being monitored';
COMMENT ON COLUMN xtrades_profiles.last_sync IS 'Timestamp of the last successful data sync';
COMMENT ON COLUMN xtrades_profiles.total_trades_scraped IS 'Running count of trades collected from this profile';

-- ============================================================================
-- Table 2: xtrades_trades
-- ============================================================================
-- Stores individual trades scraped from Xtrades profiles
-- Each row represents a single options trade or position
-- ============================================================================

CREATE TABLE IF NOT EXISTS xtrades_trades (
    id SERIAL PRIMARY KEY,
    profile_id INTEGER NOT NULL REFERENCES xtrades_profiles(id) ON DELETE CASCADE,
    ticker VARCHAR(20) NOT NULL,
    strategy VARCHAR(100), -- 'CSP', 'CC', 'Long Call', 'Put Credit Spread', etc.
    action VARCHAR(20), -- 'BTO', 'STC', 'BTC', 'STO'
    entry_price DECIMAL(10,2),
    entry_date TIMESTAMP WITH TIME ZONE,
    exit_price DECIMAL(10,2),
    exit_date TIMESTAMP WITH TIME ZONE,
    quantity INTEGER,
    pnl DECIMAL(10,2),
    pnl_percent DECIMAL(10,2),
    status VARCHAR(20) DEFAULT 'open', -- 'open', 'closed', 'expired'
    strike_price DECIMAL(10,2),
    expiration_date DATE,
    alert_text TEXT, -- Full alert text from Xtrades
    alert_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    xtrades_alert_id VARCHAR(255), -- Unique ID from Xtrades if available
    CONSTRAINT chk_trade_status CHECK (status IN ('open', 'closed', 'expired')),
    CONSTRAINT chk_trade_action CHECK (action IN ('BTO', 'STC', 'BTC', 'STO', 'OPEN', 'CLOSE', NULL))
);

-- Add comments for documentation
COMMENT ON TABLE xtrades_trades IS 'Individual trades and positions scraped from Xtrades profiles';
COMMENT ON COLUMN xtrades_trades.ticker IS 'Stock ticker symbol';
COMMENT ON COLUMN xtrades_trades.strategy IS 'Options strategy type (CSP, CC, spreads, etc.)';
COMMENT ON COLUMN xtrades_trades.action IS 'Trade action: BTO=Buy To Open, STC=Sell To Close, BTC=Buy To Close, STO=Sell To Open';
COMMENT ON COLUMN xtrades_trades.pnl IS 'Profit/Loss in dollars';
COMMENT ON COLUMN xtrades_trades.pnl_percent IS 'Profit/Loss as percentage';
COMMENT ON COLUMN xtrades_trades.alert_text IS 'Raw alert text from Xtrades.net';
COMMENT ON COLUMN xtrades_trades.xtrades_alert_id IS 'Unique identifier from Xtrades to prevent duplicates';

-- ============================================================================
-- Table 3: xtrades_sync_log
-- ============================================================================
-- Tracks synchronization history and errors
-- Used for monitoring and debugging the scraping process
-- ============================================================================

CREATE TABLE IF NOT EXISTS xtrades_sync_log (
    id SERIAL PRIMARY KEY,
    sync_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    profiles_synced INTEGER DEFAULT 0,
    trades_found INTEGER DEFAULT 0,
    new_trades INTEGER DEFAULT 0,
    updated_trades INTEGER DEFAULT 0,
    errors TEXT,
    duration_seconds DECIMAL(10,2),
    status VARCHAR(50) DEFAULT 'success', -- 'success', 'partial', 'failed'
    CONSTRAINT chk_sync_log_status CHECK (status IN ('success', 'partial', 'failed'))
);

-- Add comments for documentation
COMMENT ON TABLE xtrades_sync_log IS 'Audit log of all synchronization operations';
COMMENT ON COLUMN xtrades_sync_log.profiles_synced IS 'Number of profiles processed in this sync';
COMMENT ON COLUMN xtrades_sync_log.new_trades IS 'Number of new trades discovered';
COMMENT ON COLUMN xtrades_sync_log.updated_trades IS 'Number of existing trades updated';
COMMENT ON COLUMN xtrades_sync_log.duration_seconds IS 'How long the sync operation took';

-- ============================================================================
-- Table 4: xtrades_notifications
-- ============================================================================
-- Tracks notifications sent via Telegram or other channels
-- Prevents duplicate notifications and provides audit trail
-- ============================================================================

CREATE TABLE IF NOT EXISTS xtrades_notifications (
    id SERIAL PRIMARY KEY,
    trade_id INTEGER NOT NULL REFERENCES xtrades_trades(id) ON DELETE CASCADE,
    notification_type VARCHAR(50) NOT NULL, -- 'new_trade', 'trade_update', 'trade_closed'
    sent_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    telegram_message_id VARCHAR(255),
    status VARCHAR(20) DEFAULT 'sent', -- 'sent', 'failed'
    error_message TEXT,
    CONSTRAINT chk_notification_status CHECK (status IN ('sent', 'failed')),
    CONSTRAINT chk_notification_type CHECK (notification_type IN ('new_trade', 'trade_update', 'trade_closed'))
);

-- Add comments for documentation
COMMENT ON TABLE xtrades_notifications IS 'Tracks notifications sent for trades to prevent duplicates';
COMMENT ON COLUMN xtrades_notifications.notification_type IS 'Type of notification: new_trade, trade_update, or trade_closed';
COMMENT ON COLUMN xtrades_notifications.telegram_message_id IS 'Telegram message ID for tracking and potential editing';

-- ============================================================================
-- INDEXES for Performance Optimization
-- ============================================================================

-- Indexes on xtrades_profiles
CREATE INDEX IF NOT EXISTS idx_xtrades_profiles_username ON xtrades_profiles(username);
CREATE INDEX IF NOT EXISTS idx_xtrades_profiles_active ON xtrades_profiles(active);
CREATE INDEX IF NOT EXISTS idx_xtrades_profiles_last_sync ON xtrades_profiles(last_sync DESC);

-- Indexes on xtrades_trades
CREATE INDEX IF NOT EXISTS idx_xtrades_trades_profile_id ON xtrades_trades(profile_id);
CREATE INDEX IF NOT EXISTS idx_xtrades_trades_ticker ON xtrades_trades(ticker);
CREATE INDEX IF NOT EXISTS idx_xtrades_trades_status ON xtrades_trades(status);
CREATE INDEX IF NOT EXISTS idx_xtrades_trades_alert_timestamp ON xtrades_trades(alert_timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_xtrades_trades_entry_date ON xtrades_trades(entry_date DESC);
CREATE INDEX IF NOT EXISTS idx_xtrades_trades_strategy ON xtrades_trades(strategy);
CREATE INDEX IF NOT EXISTS idx_xtrades_trades_alert_id ON xtrades_trades(xtrades_alert_id);
-- Composite index for common queries
CREATE INDEX IF NOT EXISTS idx_xtrades_trades_profile_status ON xtrades_trades(profile_id, status);
CREATE INDEX IF NOT EXISTS idx_xtrades_trades_ticker_status ON xtrades_trades(ticker, status);

-- Indexes on xtrades_sync_log
CREATE INDEX IF NOT EXISTS idx_xtrades_sync_log_timestamp ON xtrades_sync_log(sync_timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_xtrades_sync_log_status ON xtrades_sync_log(status);

-- Indexes on xtrades_notifications
CREATE INDEX IF NOT EXISTS idx_xtrades_notifications_trade_id ON xtrades_notifications(trade_id);
CREATE INDEX IF NOT EXISTS idx_xtrades_notifications_sent_at ON xtrades_notifications(sent_at DESC);
CREATE INDEX IF NOT EXISTS idx_xtrades_notifications_type ON xtrades_notifications(notification_type);
-- Composite index for checking if notification already sent
CREATE INDEX IF NOT EXISTS idx_xtrades_notifications_trade_type ON xtrades_notifications(trade_id, notification_type);

-- ============================================================================
-- SAMPLE TEST DATA
-- ============================================================================

-- NO SAMPLE DATA - All data must come from real Xtrades.net profiles
-- Add profiles via the UI: Dashboard -> Xtrades Watchlists -> Manage Profiles
-- Database will be populated by the scraper when you sync real profiles

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Verify table creation
SELECT
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as column_count
FROM information_schema.tables t
WHERE table_schema = 'public'
    AND table_name LIKE 'xtrades_%'
ORDER BY table_name;

-- Verify indexes
SELECT
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
    AND tablename LIKE 'xtrades_%'
ORDER BY tablename, indexname;

-- Verify sample data
SELECT 'xtrades_profiles' as table_name, COUNT(*) as row_count FROM xtrades_profiles
UNION ALL
SELECT 'xtrades_trades', COUNT(*) FROM xtrades_trades
UNION ALL
SELECT 'xtrades_sync_log', COUNT(*) FROM xtrades_sync_log
UNION ALL
SELECT 'xtrades_notifications', COUNT(*) FROM xtrades_notifications;

-- ============================================================================
-- SUCCESS MESSAGE
-- ============================================================================
SELECT 'Xtrades Watchlists schema created successfully!' as status;
