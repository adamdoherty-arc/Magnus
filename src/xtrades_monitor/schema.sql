-- ============================================
-- Xtrades Real-Time Monitoring System - Database Schema
-- ============================================
-- Created: November 6, 2025
-- Purpose: Support real-time Xtrades alert monitoring, AI evaluation, and Telegram notifications
-- Tables: 4 new tables for comprehensive monitoring system

-- ============================================
-- Table 1: xtrades_alerts
-- Purpose: Store AI evaluation results for each Xtrades trade alert
-- ============================================
CREATE TABLE IF NOT EXISTS xtrades_alerts (
    id SERIAL PRIMARY KEY,
    trade_id INTEGER REFERENCES xtrades_trades(id) ON DELETE CASCADE,

    -- Strategy Evaluation
    strategy_rank INTEGER NOT NULL,  -- 1-10 ranking
    strategy_name VARCHAR(100) NOT NULL,
    strategy_score INTEGER NOT NULL CHECK (strategy_score BETWEEN 0 AND 100),
    environment_fit VARCHAR(50),  -- 'excellent', 'good', 'poor'

    -- Multi-Model AI Scores
    claude_score INTEGER CHECK (claude_score BETWEEN 0 AND 100),
    deepseek_score INTEGER CHECK (deepseek_score BETWEEN 0 AND 100),
    gemini_score INTEGER CHECK (gemini_score BETWEEN 0 AND 100),
    consensus_score INTEGER NOT NULL CHECK (consensus_score BETWEEN 0 AND 100),

    -- AI Analysis
    ai_reasoning TEXT,  -- Combined reasoning from all models
    key_risk TEXT,  -- Primary risk identified
    recommendation VARCHAR(50),  -- 'STRONG_BUY', 'BUY', 'HOLD', 'AVOID'

    -- RAG Similarity Search Results
    similar_trades_count INTEGER DEFAULT 0,
    similar_trades_avg_pnl DECIMAL(10,2),
    similar_trades_success_rate DECIMAL(5,2),  -- 0-100%
    similar_trade_ids INTEGER[],  -- Array of similar trade IDs

    -- Vector Database Integration
    qdrant_vector_id VARCHAR(255),  -- UUID from Qdrant
    embedding_model VARCHAR(100) DEFAULT 'sentence-transformers/all-MiniLM-L6-v2',

    -- Metadata
    evaluated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    evaluation_duration_ms INTEGER,  -- Time taken for evaluation

    -- Indexes for fast querying
    CONSTRAINT unique_trade_alert UNIQUE (trade_id)
);

CREATE INDEX idx_xtrades_alerts_score ON xtrades_alerts(consensus_score DESC);
CREATE INDEX idx_xtrades_alerts_evaluated ON xtrades_alerts(evaluated_at DESC);
CREATE INDEX idx_xtrades_alerts_recommendation ON xtrades_alerts(recommendation);

-- ============================================
-- Table 2: xtrades_notification_queue
-- Purpose: Rate-limited notification queue for Telegram alerts
-- ============================================
CREATE TABLE IF NOT EXISTS xtrades_notification_queue (
    id SERIAL PRIMARY KEY,
    alert_id INTEGER REFERENCES xtrades_alerts(id) ON DELETE CASCADE,
    trade_id INTEGER REFERENCES xtrades_trades(id) ON DELETE CASCADE,

    -- Notification Details
    notification_type VARCHAR(50) DEFAULT 'telegram',  -- 'telegram', 'email', 'webhook'
    priority INTEGER DEFAULT 5 CHECK (priority BETWEEN 1 AND 10),  -- 1=highest, 10=lowest

    -- Status Tracking
    status VARCHAR(50) DEFAULT 'pending',  -- 'pending', 'sent', 'failed', 'rate_limited', 'cancelled'

    -- Message Content
    message_title VARCHAR(255),
    message_body TEXT,
    message_format VARCHAR(20) DEFAULT 'markdown',  -- 'markdown', 'html', 'plain'

    -- Retry Logic
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    next_retry_at TIMESTAMP WITH TIME ZONE,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    sent_at TIMESTAMP WITH TIME ZONE,
    failed_at TIMESTAMP WITH TIME ZONE,

    -- Error Handling
    error_message TEXT,
    error_code VARCHAR(50),

    -- Telegram Specific
    telegram_message_id BIGINT,  -- Message ID from Telegram API
    telegram_chat_id BIGINT,

    CONSTRAINT unique_alert_notification UNIQUE (alert_id, notification_type)
);

CREATE INDEX idx_notifications_status ON xtrades_notification_queue(status, created_at);
CREATE INDEX idx_notifications_priority ON xtrades_notification_queue(priority, status);
CREATE INDEX idx_notifications_retry ON xtrades_notification_queue(next_retry_at) WHERE status = 'rate_limited';

-- ============================================
-- Table 3: xtrades_scraper_state
-- Purpose: Track scraper health and session management
-- ============================================
CREATE TABLE IF NOT EXISTS xtrades_scraper_state (
    id SERIAL PRIMARY KEY,
    profile_username VARCHAR(100) UNIQUE NOT NULL,

    -- Session Management
    last_scraped_at TIMESTAMP WITH TIME ZONE,
    session_valid_until TIMESTAMP WITH TIME ZONE,
    session_token TEXT,  -- Discord OAuth token (encrypted)
    cookies_json TEXT,  -- Browser cookies for session

    -- Health Monitoring
    is_healthy BOOLEAN DEFAULT TRUE,
    consecutive_failures INTEGER DEFAULT 0,
    last_error TEXT,
    last_success_at TIMESTAMP WITH TIME ZONE,

    -- Performance Metrics
    total_scrapes INTEGER DEFAULT 0,
    successful_scrapes INTEGER DEFAULT 0,
    failed_scrapes INTEGER DEFAULT 0,
    avg_scrape_duration_seconds DECIMAL(6,2),

    -- Rate Limiting
    requests_this_hour INTEGER DEFAULT 0,
    rate_limit_reset_at TIMESTAMP WITH TIME ZONE,

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_scraper_health ON xtrades_scraper_state(is_healthy, last_scraped_at);
CREATE INDEX idx_scraper_session ON xtrades_scraper_state(session_valid_until);

-- ============================================
-- Table 4: xtrades_rate_limiter
-- Purpose: Track notification rate limits (5 alerts per hour)
-- ============================================
CREATE TABLE IF NOT EXISTS xtrades_rate_limiter (
    id SERIAL PRIMARY KEY,

    -- Time Window
    window_start TIMESTAMP WITH TIME ZONE NOT NULL,
    window_end TIMESTAMP WITH TIME ZONE NOT NULL,
    window_duration_minutes INTEGER DEFAULT 60,  -- 1 hour default

    -- Limits
    max_notifications INTEGER DEFAULT 5,  -- Max 5 per hour
    notifications_sent INTEGER DEFAULT 0,

    -- Tracking
    notification_ids INTEGER[],  -- Array of sent notification IDs
    last_notification_at TIMESTAMP WITH TIME ZONE,

    -- Status
    is_active BOOLEAN DEFAULT TRUE,

    CONSTRAINT unique_active_window UNIQUE (window_start, is_active)
);

CREATE INDEX idx_rate_limiter_active ON xtrades_rate_limiter(is_active, window_end);
CREATE INDEX idx_rate_limiter_window ON xtrades_rate_limiter(window_start, window_end);

-- ============================================
-- Helper Function: Check if notification is allowed
-- ============================================
CREATE OR REPLACE FUNCTION can_send_notification()
RETURNS BOOLEAN AS $$
DECLARE
    current_window RECORD;
    now_ts TIMESTAMP WITH TIME ZONE := NOW();
BEGIN
    -- Get or create current rate limit window
    SELECT * INTO current_window
    FROM xtrades_rate_limiter
    WHERE is_active = TRUE
      AND window_start <= now_ts
      AND window_end > now_ts
    ORDER BY window_start DESC
    LIMIT 1;

    -- If no active window or notifications below limit
    IF current_window IS NULL THEN
        -- Create new window
        INSERT INTO xtrades_rate_limiter (window_start, window_end, is_active)
        VALUES (now_ts, now_ts + INTERVAL '1 hour', TRUE);
        RETURN TRUE;
    ELSIF current_window.notifications_sent < current_window.max_notifications THEN
        RETURN TRUE;
    ELSE
        RETURN FALSE;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- Helper Function: Record notification sent
-- ============================================
CREATE OR REPLACE FUNCTION record_notification_sent(notification_id INTEGER)
RETURNS VOID AS $$
DECLARE
    current_window RECORD;
    now_ts TIMESTAMP WITH TIME ZONE := NOW();
BEGIN
    -- Get current active window
    SELECT * INTO current_window
    FROM xtrades_rate_limiter
    WHERE is_active = TRUE
      AND window_start <= now_ts
      AND window_end > now_ts
    ORDER BY window_start DESC
    LIMIT 1;

    IF current_window IS NOT NULL THEN
        -- Update existing window
        UPDATE xtrades_rate_limiter
        SET notifications_sent = notifications_sent + 1,
            notification_ids = array_append(notification_ids, notification_id),
            last_notification_at = now_ts
        WHERE id = current_window.id;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- Helper Function: Clean up old rate limit windows
-- ============================================
CREATE OR REPLACE FUNCTION cleanup_old_rate_limit_windows()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    -- Mark old windows as inactive
    UPDATE xtrades_rate_limiter
    SET is_active = FALSE
    WHERE window_end < NOW() - INTERVAL '24 hours'
      AND is_active = TRUE;

    GET DIAGNOSTICS deleted_count = ROW_COUNT;

    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- Triggers for automatic timestamp updates
-- ============================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_scraper_state_updated_at
    BEFORE UPDATE ON xtrades_scraper_state
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- Initial Data: Create rate limit window
-- ============================================
INSERT INTO xtrades_rate_limiter (window_start, window_end, is_active)
VALUES (NOW(), NOW() + INTERVAL '1 hour', TRUE)
ON CONFLICT DO NOTHING;

-- ============================================
-- Views for easy querying
-- ============================================

-- View: High-quality alerts (score >= 80) not yet notified
CREATE OR REPLACE VIEW xtrades_alerts_pending_notification AS
SELECT
    a.id,
    a.trade_id,
    a.consensus_score,
    a.strategy_name,
    a.recommendation,
    t.symbol,
    t.trader_username,
    t.action,
    t.strike_price,
    t.premium,
    t.expiry_date,
    a.ai_reasoning,
    a.key_risk
FROM xtrades_alerts a
JOIN xtrades_trades t ON a.trade_id = t.id
LEFT JOIN xtrades_notification_queue nq ON a.id = nq.alert_id
WHERE a.consensus_score >= 80
  AND nq.id IS NULL
  AND t.status = 'active'
ORDER BY a.consensus_score DESC;

-- View: Scraper health dashboard
CREATE OR REPLACE VIEW xtrades_scraper_health_dashboard AS
SELECT
    profile_username,
    is_healthy,
    last_scraped_at,
    session_valid_until,
    consecutive_failures,
    total_scrapes,
    successful_scrapes,
    failed_scrapes,
    ROUND((successful_scrapes::DECIMAL / NULLIF(total_scrapes, 0)) * 100, 2) as success_rate,
    avg_scrape_duration_seconds,
    last_error
FROM xtrades_scraper_state
ORDER BY is_healthy DESC, last_scraped_at DESC;

-- View: Current rate limit status
CREATE OR REPLACE VIEW xtrades_rate_limit_status AS
SELECT
    window_start,
    window_end,
    max_notifications,
    notifications_sent,
    max_notifications - notifications_sent as remaining_slots,
    ROUND((notifications_sent::DECIMAL / max_notifications) * 100, 2) as usage_percent,
    last_notification_at,
    EXTRACT(EPOCH FROM (window_end - NOW())) / 60 as minutes_until_reset
FROM xtrades_rate_limiter
WHERE is_active = TRUE
  AND window_end > NOW()
ORDER BY window_start DESC
LIMIT 1;

-- ============================================
-- Comments for documentation
-- ============================================
COMMENT ON TABLE xtrades_alerts IS 'Stores AI evaluation results for each Xtrades trade alert';
COMMENT ON TABLE xtrades_notification_queue IS 'Rate-limited notification queue for Telegram alerts';
COMMENT ON TABLE xtrades_scraper_state IS 'Track scraper health and session management';
COMMENT ON TABLE xtrades_rate_limiter IS 'Track notification rate limits (5 alerts per hour)';

COMMENT ON COLUMN xtrades_alerts.consensus_score IS 'Weighted average of Claude (50%), DeepSeek (30%), Gemini (20%)';
COMMENT ON COLUMN xtrades_alerts.similar_trades_count IS 'Number of similar historical trades found via RAG';
COMMENT ON COLUMN xtrades_notification_queue.priority IS '1=highest priority, 10=lowest priority';
COMMENT ON COLUMN xtrades_scraper_state.session_valid_until IS 'When Discord OAuth session expires';

-- ============================================
-- Success Message
-- ============================================
DO $$
BEGIN
    RAISE NOTICE '✅ Xtrades monitoring schema created successfully!';
    RAISE NOTICE 'Tables created: 4';
    RAISE NOTICE 'Views created: 3';
    RAISE NOTICE 'Functions created: 4';
    RAISE NOTICE 'System ready for real-time monitoring!';
END $$;
