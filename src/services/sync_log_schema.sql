-- Sync Log Table - Track all sync operations and failures
-- Purpose: Monitor sync health, track failures, enable retry logic

CREATE TABLE IF NOT EXISTS sync_log (
    id SERIAL PRIMARY KEY,
    sync_type VARCHAR(50) NOT NULL,  -- 'stock_data', 'stock_premiums', 'xtrades', 'tradingview', etc.
    status VARCHAR(20) NOT NULL,      -- 'success', 'failed', 'in_progress'
    items_processed INTEGER DEFAULT 0,
    items_successful INTEGER DEFAULT 0,
    items_failed INTEGER DEFAULT 0,
    error_message TEXT,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_seconds INTEGER,
    metadata JSONB,
    
    CONSTRAINT chk_sync_status CHECK (status IN ('success', 'failed', 'in_progress'))
);

-- Indexes for fast queries
CREATE INDEX IF NOT EXISTS idx_sync_log_type ON sync_log(sync_type);
CREATE INDEX IF NOT EXISTS idx_sync_log_status ON sync_log(status);
CREATE INDEX IF NOT EXISTS idx_sync_log_started ON sync_log(started_at DESC);
CREATE INDEX IF NOT EXISTS idx_sync_log_type_status ON sync_log(sync_type, status);

-- View for recent sync failures
CREATE OR REPLACE VIEW sync_failures_recent AS
SELECT 
    sync_type,
    status,
    error_message,
    started_at,
    completed_at,
    duration_seconds
FROM sync_log
WHERE status = 'failed'
  AND started_at > NOW() - INTERVAL '7 days'
ORDER BY started_at DESC;

