-- ============================================================================
-- AVA Telegram Bot - State Management Enhancement
-- Migration: 001_telegram_enhancements.sql
-- Version: 2.0.0
-- Date: 2025-11-06
-- Description: Adds tables for conversation state, message logging, rate
--              limiting, and workflow management for the enhanced AVA bot
-- ============================================================================

BEGIN;

-- ============================================================================
-- Table: telegram_users
-- Purpose: Store Telegram user information and authorization
-- ============================================================================
CREATE TABLE IF NOT EXISTS telegram_users (
    id SERIAL PRIMARY KEY,

    -- Telegram identifiers
    chat_id BIGINT UNIQUE NOT NULL,
    user_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(100),
    first_name VARCHAR(100),
    last_name VARCHAR(100),

    -- User preferences
    notifications_enabled BOOLEAN DEFAULT TRUE,
    language_code VARCHAR(10) DEFAULT 'en',
    timezone VARCHAR(50) DEFAULT 'UTC',
    voice_messages_enabled BOOLEAN DEFAULT TRUE,

    -- Security and authorization
    is_authorized BOOLEAN DEFAULT FALSE,
    authorization_code VARCHAR(10),
    authorized_at TIMESTAMP WITH TIME ZONE,
    authorized_by VARCHAR(100), -- Admin who authorized

    -- Conversation state (primary state stored in Redis, this is backup)
    conversation_state JSONB DEFAULT '{"state": "IDLE"}'::jsonb,
    session_data JSONB DEFAULT '{}'::jsonb,
    last_workflow VARCHAR(100),

    -- Rate limiting counters (reset daily)
    message_count_today INTEGER DEFAULT 0,
    last_message_at TIMESTAMP WITH TIME ZONE,
    rate_limited_until TIMESTAMP WITH TIME ZONE,
    total_messages_sent INTEGER DEFAULT 0,

    -- Activity tracking
    first_seen_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_seen_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_command VARCHAR(50),

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT chk_chat_id_positive CHECK (chat_id > 0),
    CONSTRAINT chk_user_id_positive CHECK (user_id > 0)
);

-- Indexes for telegram_users
CREATE INDEX IF NOT EXISTS idx_telegram_users_chat_id ON telegram_users(chat_id);
CREATE INDEX IF NOT EXISTS idx_telegram_users_user_id ON telegram_users(user_id);
CREATE INDEX IF NOT EXISTS idx_telegram_users_authorized ON telegram_users(is_authorized) WHERE is_authorized = TRUE;
CREATE INDEX IF NOT EXISTS idx_telegram_users_last_seen ON telegram_users(last_seen_at DESC);

COMMENT ON TABLE telegram_users IS 'Telegram bot users with authorization and state tracking';
COMMENT ON COLUMN telegram_users.chat_id IS 'Telegram chat ID (unique per user-bot conversation)';
COMMENT ON COLUMN telegram_users.user_id IS 'Telegram user ID (unique per user globally)';
COMMENT ON COLUMN telegram_users.is_authorized IS 'Whether user has been authorized to use trading features';
COMMENT ON COLUMN telegram_users.conversation_state IS 'Backup of conversation state (primary storage is Redis)';

-- ============================================================================
-- Table: telegram_message_log
-- Purpose: Log all incoming and outgoing messages for debugging and analytics
-- ============================================================================
CREATE TABLE IF NOT EXISTS telegram_message_log (
    id SERIAL PRIMARY KEY,

    -- Message identifiers
    message_id BIGINT NOT NULL,
    update_id BIGINT UNIQUE NOT NULL,
    chat_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,

    -- Message details
    message_type VARCHAR(50) NOT NULL, -- 'text', 'voice', 'command', 'callback_query', 'photo', 'document'
    direction VARCHAR(10) NOT NULL, -- 'incoming', 'outgoing'
    content TEXT, -- Message text or file_id
    raw_update JSONB, -- Full Telegram update object

    -- Processing information
    handler VARCHAR(100), -- Handler that processed the message
    processing_time_ms INTEGER, -- Time taken to process
    status VARCHAR(50) DEFAULT 'queued', -- 'queued', 'processing', 'completed', 'failed', 'timeout'
    error_message TEXT,
    error_traceback TEXT,
    retry_count INTEGER DEFAULT 0,
    max_retries_exceeded BOOLEAN DEFAULT FALSE,

    -- Context
    conversation_state VARCHAR(50), -- State at time of message
    workflow_name VARCHAR(100), -- Active workflow if any
    session_id VARCHAR(100), -- Session identifier

    -- Queue information
    queue_name VARCHAR(50), -- 'high', 'normal', 'low'
    priority INTEGER DEFAULT 0, -- 0=normal, 1=high, -1=low

    -- Timestamps
    received_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    queued_at TIMESTAMP WITH TIME ZONE,
    processing_started_at TIMESTAMP WITH TIME ZONE,
    processed_at TIMESTAMP WITH TIME ZONE,

    -- Foreign key
    CONSTRAINT fk_telegram_message_user
        FOREIGN KEY (chat_id) REFERENCES telegram_users(chat_id)
        ON DELETE CASCADE,

    CONSTRAINT chk_message_direction CHECK (direction IN ('incoming', 'outgoing')),
    CONSTRAINT chk_message_status CHECK (status IN ('queued', 'processing', 'completed', 'failed', 'timeout', 'cancelled'))
);

-- Indexes for telegram_message_log
CREATE INDEX IF NOT EXISTS idx_telegram_message_log_chat ON telegram_message_log(chat_id, received_at DESC);
CREATE INDEX IF NOT EXISTS idx_telegram_message_log_user ON telegram_message_log(user_id, received_at DESC);
CREATE INDEX IF NOT EXISTS idx_telegram_message_log_update ON telegram_message_log(update_id);
CREATE INDEX IF NOT EXISTS idx_telegram_message_log_status ON telegram_message_log(status) WHERE status IN ('queued', 'processing', 'failed');
CREATE INDEX IF NOT EXISTS idx_telegram_message_log_type ON telegram_message_log(message_type);
CREATE INDEX IF NOT EXISTS idx_telegram_message_log_received ON telegram_message_log(received_at DESC);

-- Full-text search on message content
CREATE INDEX IF NOT EXISTS idx_telegram_message_log_content_search ON telegram_message_log USING GIN(to_tsvector('english', content));

COMMENT ON TABLE telegram_message_log IS 'Complete log of all Telegram messages for debugging and analytics';
COMMENT ON COLUMN telegram_message_log.raw_update IS 'Complete Telegram Update object for forensic analysis';
COMMENT ON COLUMN telegram_message_log.processing_time_ms IS 'Response time metric for performance monitoring';

-- ============================================================================
-- Table: telegram_rate_limits
-- Purpose: Track rate limiting per user and globally
-- ============================================================================
CREATE TABLE IF NOT EXISTS telegram_rate_limits (
    id SERIAL PRIMARY KEY,

    -- Scope
    chat_id BIGINT, -- NULL for global limits
    limit_type VARCHAR(50) NOT NULL, -- 'user_minute', 'user_hour', 'user_day', 'global_second', 'api_robinhood', 'api_tradingview'

    -- Time window
    window_start TIMESTAMP WITH TIME ZONE NOT NULL,
    window_end TIMESTAMP WITH TIME ZONE NOT NULL,
    window_duration_seconds INTEGER NOT NULL, -- 60, 3600, 86400

    -- Counter
    request_count INTEGER DEFAULT 0,
    max_requests_per_window INTEGER NOT NULL,
    limit_exceeded BOOLEAN DEFAULT FALSE,
    limit_exceeded_at TIMESTAMP WITH TIME ZONE,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    UNIQUE(chat_id, limit_type, window_start),

    CONSTRAINT chk_window_duration CHECK (window_duration_seconds > 0),
    CONSTRAINT chk_max_requests CHECK (max_requests_per_window > 0)
);

-- Indexes for telegram_rate_limits
CREATE INDEX IF NOT EXISTS idx_telegram_rate_limits_chat ON telegram_rate_limits(chat_id, limit_type);
CREATE INDEX IF NOT EXISTS idx_telegram_rate_limits_window ON telegram_rate_limits(window_start, window_end);
CREATE INDEX IF NOT EXISTS idx_telegram_rate_limits_exceeded ON telegram_rate_limits(limit_exceeded) WHERE limit_exceeded = TRUE;

COMMENT ON TABLE telegram_rate_limits IS 'Rate limiting tracking for users and global API limits';
COMMENT ON COLUMN telegram_rate_limits.limit_type IS 'Type of rate limit: user per minute/hour/day, global per second, or external API limits';

-- ============================================================================
-- Table: telegram_workflows
-- Purpose: Track multi-step conversation workflows
-- ============================================================================
CREATE TABLE IF NOT EXISTS telegram_workflows (
    id SERIAL PRIMARY KEY,

    -- Workflow identification
    workflow_name VARCHAR(100) NOT NULL, -- 'stock_analysis', 'trade_execution', 'portfolio_review'
    chat_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,

    -- Workflow state
    current_step INTEGER DEFAULT 1,
    total_steps INTEGER NOT NULL,
    status VARCHAR(50) DEFAULT 'active', -- 'active', 'completed', 'cancelled', 'timeout', 'error'

    -- Workflow data
    workflow_data JSONB DEFAULT '{}'::jsonb, -- Workflow-specific configuration
    collected_inputs JSONB DEFAULT '{}'::jsonb, -- User inputs collected so far
    step_history JSONB DEFAULT '[]'::jsonb, -- History of steps completed

    -- Result
    result JSONB, -- Final result when completed
    error_message TEXT,

    -- Timestamps
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '1 hour'),
    last_activity_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Foreign key
    CONSTRAINT fk_telegram_workflow_user
        FOREIGN KEY (chat_id) REFERENCES telegram_users(chat_id)
        ON DELETE CASCADE,

    CONSTRAINT chk_workflow_status CHECK (status IN ('active', 'completed', 'cancelled', 'timeout', 'error')),
    CONSTRAINT chk_steps CHECK (current_step <= total_steps AND current_step > 0)
);

-- Indexes for telegram_workflows
CREATE INDEX IF NOT EXISTS idx_telegram_workflows_chat ON telegram_workflows(chat_id, status);
CREATE INDEX IF NOT EXISTS idx_telegram_workflows_user ON telegram_workflows(user_id);
CREATE INDEX IF NOT EXISTS idx_telegram_workflows_status ON telegram_workflows(status) WHERE status = 'active';
CREATE INDEX IF NOT EXISTS idx_telegram_workflows_expires ON telegram_workflows(expires_at) WHERE status = 'active';
CREATE INDEX IF NOT EXISTS idx_telegram_workflows_name ON telegram_workflows(workflow_name, started_at DESC);

COMMENT ON TABLE telegram_workflows IS 'Multi-step conversation workflows with state persistence';
COMMENT ON COLUMN telegram_workflows.collected_inputs IS 'Dictionary of user inputs collected at each step';
COMMENT ON COLUMN telegram_workflows.expires_at IS 'Workflow expires after inactivity timeout';

-- ============================================================================
-- Table: telegram_command_stats
-- Purpose: Analytics on command usage
-- ============================================================================
CREATE TABLE IF NOT EXISTS telegram_command_stats (
    id SERIAL PRIMARY KEY,

    -- Command
    command VARCHAR(100) NOT NULL, -- '/start', '/portfolio', '/help', etc.

    -- Aggregation period
    date DATE NOT NULL,
    hour INTEGER CHECK (hour >= 0 AND hour <= 23),

    -- Counters
    execution_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    unique_users INTEGER DEFAULT 0,

    -- Performance
    avg_response_time_ms DECIMAL(10,2),
    p95_response_time_ms INTEGER,
    max_response_time_ms INTEGER,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    UNIQUE(command, date, hour)
);

-- Indexes for telegram_command_stats
CREATE INDEX IF NOT EXISTS idx_telegram_command_stats_date ON telegram_command_stats(date DESC, hour DESC);
CREATE INDEX IF NOT EXISTS idx_telegram_command_stats_command ON telegram_command_stats(command, date DESC);

COMMENT ON TABLE telegram_command_stats IS 'Aggregated statistics on command usage and performance';

-- ============================================================================
-- Functions and Triggers
-- ============================================================================

-- Function: Update updated_at timestamp
CREATE OR REPLACE FUNCTION update_telegram_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for updated_at
CREATE TRIGGER telegram_users_updated_at
    BEFORE UPDATE ON telegram_users
    FOR EACH ROW
    EXECUTE FUNCTION update_telegram_updated_at();

CREATE TRIGGER telegram_rate_limits_updated_at
    BEFORE UPDATE ON telegram_rate_limits
    FOR EACH ROW
    EXECUTE FUNCTION update_telegram_updated_at();

CREATE TRIGGER telegram_command_stats_updated_at
    BEFORE UPDATE ON telegram_command_stats
    FOR EACH ROW
    EXECUTE FUNCTION update_telegram_updated_at();

-- Function: Reset daily message counters
CREATE OR REPLACE FUNCTION reset_daily_message_counters()
RETURNS INTEGER AS $$
DECLARE
    rows_updated INTEGER;
BEGIN
    UPDATE telegram_users
    SET message_count_today = 0
    WHERE DATE(last_message_at) < CURRENT_DATE;

    GET DIAGNOSTICS rows_updated = ROW_COUNT;
    RETURN rows_updated;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION reset_daily_message_counters() IS 'Reset daily message counters (run as cron job at midnight)';

-- Function: Clean up old message logs (retain 30 days)
CREATE OR REPLACE FUNCTION cleanup_old_message_logs(retention_days INTEGER DEFAULT 30)
RETURNS INTEGER AS $$
DECLARE
    rows_deleted INTEGER;
BEGIN
    DELETE FROM telegram_message_log
    WHERE received_at < NOW() - INTERVAL '1 day' * retention_days;

    GET DIAGNOSTICS rows_deleted = ROW_COUNT;
    RETURN rows_deleted;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION cleanup_old_message_logs(INTEGER) IS 'Delete message logs older than specified days (default 30)';

-- ============================================================================
-- Views for Analytics
-- ============================================================================

-- View: Active users today
CREATE OR REPLACE VIEW v_telegram_active_users_today AS
SELECT
    COUNT(DISTINCT chat_id) as active_users,
    COUNT(*) as total_messages,
    AVG(processing_time_ms) as avg_response_time_ms
FROM telegram_message_log
WHERE received_at::date = CURRENT_DATE
    AND direction = 'incoming'
    AND status = 'completed';

COMMENT ON VIEW v_telegram_active_users_today IS 'Active users and message stats for today';

-- View: Command usage summary
CREATE OR REPLACE VIEW v_telegram_command_usage AS
SELECT
    command,
    SUM(execution_count) as total_executions,
    SUM(success_count) as total_successes,
    SUM(error_count) as total_errors,
    AVG(avg_response_time_ms) as avg_response_time_ms,
    MAX(date) as last_used_date
FROM telegram_command_stats
WHERE date >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY command
ORDER BY total_executions DESC;

COMMENT ON VIEW v_telegram_command_usage IS 'Command usage summary (last 7 days)';

-- View: Rate limit violations
CREATE OR REPLACE VIEW v_telegram_rate_limit_violations AS
SELECT
    trl.chat_id,
    tu.username,
    tu.first_name,
    trl.limit_type,
    trl.request_count,
    trl.max_requests_per_window,
    trl.limit_exceeded_at
FROM telegram_rate_limits trl
JOIN telegram_users tu ON trl.chat_id = tu.chat_id
WHERE trl.limit_exceeded = TRUE
    AND trl.limit_exceeded_at > NOW() - INTERVAL '24 hours'
ORDER BY trl.limit_exceeded_at DESC;

COMMENT ON VIEW v_telegram_rate_limit_violations IS 'Rate limit violations in the last 24 hours';

-- ============================================================================
-- Initial Data
-- ============================================================================

-- Insert default rate limit configuration (optional)
-- This can be managed dynamically, but here are sensible defaults

-- Note: These are examples, actual rate limiting is enforced in Redis

-- ============================================================================
-- Migration Completion
-- ============================================================================

-- Record migration in schema_migrations table (if it exists)
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_name = 'schema_migrations'
    ) THEN
        INSERT INTO schema_migrations (version, name, applied_at)
        VALUES (1, 'telegram_enhancements', NOW())
        ON CONFLICT (version) DO NOTHING;
    END IF;
END $$;

COMMIT;

-- ============================================================================
-- Verification Queries
-- ============================================================================

-- Verify tables were created
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE tablename LIKE 'telegram_%'
ORDER BY tablename;

-- ============================================================================
-- Success Message
-- ============================================================================

SELECT 'AVA Telegram Bot enhancement migration completed successfully!' as status,
       'Tables created: telegram_users, telegram_message_log, telegram_rate_limits, telegram_workflows, telegram_command_stats' as tables_created;
