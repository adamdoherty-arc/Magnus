-- AVA Conversation Memory & Feedback System
-- ==========================================
-- Tracks all conversations, actions performed, and unanswered questions
-- Automatically creates Legion tasks for improvement opportunities

-- Conversation sessions
CREATE TABLE IF NOT EXISTS ava_conversations (
    conversation_id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,  -- Telegram user ID or session ID
    platform VARCHAR(50) NOT NULL,  -- 'telegram', 'web', 'api'
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    message_count INTEGER DEFAULT 0,
    total_duration_seconds INTEGER,
    user_satisfaction_rating INTEGER CHECK (user_satisfaction_rating BETWEEN 1 AND 5),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ava_conversations_user ON ava_conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_ava_conversations_started ON ava_conversations(started_at DESC);

-- Individual messages and responses
CREATE TABLE IF NOT EXISTS ava_messages (
    message_id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES ava_conversations(conversation_id) ON DELETE CASCADE,
    message_type VARCHAR(20) NOT NULL,  -- 'user_query', 'ava_response', 'system_event'
    user_message TEXT,
    ava_response TEXT,
    intent_detected VARCHAR(100),
    confidence_score DECIMAL(3,2),  -- 0.00 to 1.00

    -- Actions taken
    action_performed VARCHAR(255),  -- 'watchlist_analysis', 'portfolio_query', 'project_knowledge', etc.
    action_success BOOLEAN,
    action_duration_ms INTEGER,
    action_metadata JSONB,  -- Store details of what was done

    -- Model info
    model_used VARCHAR(100),
    provider VARCHAR(50),  -- 'groq', 'gemini', 'deepseek', 'ollama'
    tokens_used INTEGER,
    cost_usd DECIMAL(10,4),

    -- Status
    was_helpful BOOLEAN,  -- User feedback
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ava_messages_conversation ON ava_messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_ava_messages_created ON ava_messages(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_ava_messages_intent ON ava_messages(intent_detected);
CREATE INDEX IF NOT EXISTS idx_ava_messages_action ON ava_messages(action_performed);

-- Unanswered questions / Failed queries
CREATE TABLE IF NOT EXISTS ava_unanswered_questions (
    question_id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES ava_conversations(conversation_id),
    message_id INTEGER REFERENCES ava_messages(message_id),

    -- Question details
    user_question TEXT NOT NULL,
    intent_detected VARCHAR(100),
    confidence_score DECIMAL(3,2),

    -- Why it failed
    failure_reason VARCHAR(255),  -- 'low_confidence', 'no_data', 'error', 'unsupported_feature'
    error_message TEXT,
    stack_trace TEXT,

    -- Context
    user_id VARCHAR(255),
    platform VARCHAR(50),
    occurred_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Task creation
    legion_task_created BOOLEAN DEFAULT FALSE,
    legion_task_id INTEGER,
    task_created_at TIMESTAMP,

    -- Resolution tracking
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP,
    resolution_notes TEXT,

    -- Frequency tracking
    occurrence_count INTEGER DEFAULT 1,
    last_occurred_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ava_unanswered_unresolved ON ava_unanswered_questions(resolved) WHERE NOT resolved;
CREATE INDEX IF NOT EXISTS idx_ava_unanswered_task_created ON ava_unanswered_questions(legion_task_created);
CREATE INDEX IF NOT EXISTS idx_ava_unanswered_occurred ON ava_unanswered_questions(occurred_at DESC);
CREATE INDEX IF NOT EXISTS idx_ava_unanswered_frequency ON ava_unanswered_questions(occurrence_count DESC);

-- Action history (what AVA did)
CREATE TABLE IF NOT EXISTS ava_action_history (
    action_id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES ava_conversations(conversation_id),
    message_id INTEGER REFERENCES ava_messages(message_id),

    -- Action details
    action_type VARCHAR(100) NOT NULL,  -- 'analyzed_watchlist', 'ranked_strategies', 'queried_portfolio', etc.
    action_target VARCHAR(255),  -- 'NVDA', 'Tech Watchlist', 'All Positions', etc.

    -- Parameters used
    parameters JSONB,  -- Store all input parameters

    -- Results
    result_summary TEXT,
    result_data JSONB,  -- Store structured results
    result_count INTEGER,  -- Number of items returned

    -- Performance
    execution_time_ms INTEGER,
    success BOOLEAN,
    error_message TEXT,

    -- Context
    user_id VARCHAR(255),
    platform VARCHAR(50),
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ava_action_history_type ON ava_action_history(action_type);
CREATE INDEX IF NOT EXISTS idx_ava_action_history_executed ON ava_action_history(executed_at DESC);
CREATE INDEX IF NOT EXISTS idx_ava_action_history_user ON ava_action_history(user_id);

-- Conversation context (for memory/recall)
CREATE TABLE IF NOT EXISTS ava_conversation_context (
    context_id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES ava_conversations(conversation_id) ON DELETE CASCADE,

    -- Context tracking
    key VARCHAR(255) NOT NULL,  -- 'last_watchlist_analyzed', 'current_stock_focus', etc.
    value TEXT,
    value_json JSONB,  -- For structured data

    -- Metadata
    context_type VARCHAR(50),  -- 'user_preference', 'session_state', 'recent_action'
    expires_at TIMESTAMP,  -- Optional expiration

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(conversation_id, key)
);

CREATE INDEX IF NOT EXISTS idx_ava_context_conversation ON ava_conversation_context(conversation_id);
CREATE INDEX IF NOT EXISTS idx_ava_context_key ON ava_conversation_context(key);

-- User preferences (persistent across sessions)
CREATE TABLE IF NOT EXISTS ava_user_preferences (
    preference_id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL UNIQUE,

    -- Preferences
    preferred_model VARCHAR(100),  -- 'auto', 'ollama', 'gpt-4', etc.
    default_watchlist VARCHAR(255),
    notification_telegram BOOLEAN DEFAULT TRUE,
    notification_email BOOLEAN DEFAULT FALSE,

    -- Display preferences
    verbose_responses BOOLEAN DEFAULT FALSE,
    include_technical_details BOOLEAN DEFAULT TRUE,
    max_results_shown INTEGER DEFAULT 10,

    -- Trading preferences
    risk_tolerance VARCHAR(20) CHECK (risk_tolerance IN ('conservative', 'moderate', 'aggressive')),
    preferred_strategies TEXT[],  -- ['CSP', 'CC', 'Calendar']

    -- Metadata
    preferences_json JSONB,  -- Additional custom preferences

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ava_user_prefs_user ON ava_user_preferences(user_id);

-- Legion task creation log
CREATE TABLE IF NOT EXISTS ava_legion_task_log (
    log_id SERIAL PRIMARY KEY,
    question_id INTEGER REFERENCES ava_unanswered_questions(question_id),

    -- Task details
    legion_task_id INTEGER NOT NULL,
    task_title VARCHAR(500),
    task_description TEXT,
    task_priority VARCHAR(20),

    -- Creation info
    created_by VARCHAR(100) DEFAULT 'AVA_AUTO',
    creation_reason VARCHAR(255),
    occurrence_count INTEGER,  -- How many times this question was asked before creating task

    -- Status tracking
    task_status VARCHAR(50),
    completed_at TIMESTAMP,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ava_legion_log_task ON ava_legion_task_log(legion_task_id);
CREATE INDEX IF NOT EXISTS idx_ava_legion_log_question ON ava_legion_task_log(question_id);

-- Analytics views

-- View: Unanswered questions by frequency
CREATE OR REPLACE VIEW ava_unanswered_questions_summary AS
SELECT
    failure_reason,
    COUNT(*) as total_occurrences,
    SUM(occurrence_count) as total_asks,
    COUNT(*) FILTER (WHERE legion_task_created) as tasks_created,
    COUNT(*) FILTER (WHERE resolved) as resolved_count,
    MAX(occurred_at) as last_occurred
FROM ava_unanswered_questions
WHERE NOT resolved
GROUP BY failure_reason
ORDER BY total_occurrences DESC;

-- View: Top unanswered questions needing attention
CREATE OR REPLACE VIEW ava_questions_needing_tasks AS
SELECT
    question_id,
    user_question,
    failure_reason,
    occurrence_count,
    last_occurred_at,
    CASE
        WHEN occurrence_count >= 10 THEN 'high'
        WHEN occurrence_count >= 5 THEN 'medium'
        ELSE 'low'
    END as priority
FROM ava_unanswered_questions
WHERE NOT legion_task_created
  AND NOT resolved
  AND occurrence_count >= 3  -- Asked at least 3 times
ORDER BY occurrence_count DESC, last_occurred_at DESC;

-- View: AVA performance metrics
CREATE OR REPLACE VIEW ava_performance_metrics AS
SELECT
    DATE(created_at) as date,
    COUNT(*) as total_messages,
    COUNT(*) FILTER (WHERE action_success) as successful_actions,
    COUNT(*) FILTER (WHERE NOT action_success) as failed_actions,
    ROUND(AVG(confidence_score)::numeric, 2) as avg_confidence,
    ROUND(AVG(action_duration_ms)::numeric, 0) as avg_duration_ms,
    COUNT(DISTINCT conversation_id) as unique_conversations,
    ROUND(AVG(tokens_used)::numeric, 0) as avg_tokens_used
FROM ava_messages
WHERE message_type = 'ava_response'
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- View: Most common actions
CREATE OR REPLACE VIEW ava_action_frequency AS
SELECT
    action_type,
    COUNT(*) as execution_count,
    COUNT(*) FILTER (WHERE success) as success_count,
    ROUND(AVG(execution_time_ms)::numeric, 0) as avg_execution_time_ms,
    MAX(executed_at) as last_executed
FROM ava_action_history
GROUP BY action_type
ORDER BY execution_count DESC;

-- Function: Record unanswered question (deduplicate similar questions)
CREATE OR REPLACE FUNCTION record_unanswered_question(
    p_user_question TEXT,
    p_intent_detected VARCHAR(100),
    p_confidence_score DECIMAL(3,2),
    p_failure_reason VARCHAR(255),
    p_error_message TEXT,
    p_user_id VARCHAR(255),
    p_platform VARCHAR(50),
    p_conversation_id INTEGER DEFAULT NULL,
    p_message_id INTEGER DEFAULT NULL
) RETURNS INTEGER AS $$
DECLARE
    v_question_id INTEGER;
    v_existing_question_id INTEGER;
BEGIN
    -- Check if similar question already exists (case-insensitive, last 7 days)
    SELECT question_id INTO v_existing_question_id
    FROM ava_unanswered_questions
    WHERE LOWER(user_question) = LOWER(p_user_question)
      AND NOT resolved
      AND occurred_at > NOW() - INTERVAL '7 days'
    LIMIT 1;

    IF v_existing_question_id IS NOT NULL THEN
        -- Update existing record
        UPDATE ava_unanswered_questions
        SET occurrence_count = occurrence_count + 1,
            last_occurred_at = NOW(),
            updated_at = NOW()
        WHERE question_id = v_existing_question_id;

        RETURN v_existing_question_id;
    ELSE
        -- Insert new record
        INSERT INTO ava_unanswered_questions (
            conversation_id,
            message_id,
            user_question,
            intent_detected,
            confidence_score,
            failure_reason,
            error_message,
            user_id,
            platform
        ) VALUES (
            p_conversation_id,
            p_message_id,
            p_user_question,
            p_intent_detected,
            p_confidence_score,
            p_failure_reason,
            p_error_message,
            p_user_id,
            p_platform
        ) RETURNING question_id INTO v_question_id;

        RETURN v_question_id;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Function: Auto-create Legion task for high-frequency unanswered questions
CREATE OR REPLACE FUNCTION auto_create_legion_task_if_needed()
RETURNS TRIGGER AS $$
DECLARE
    v_task_id INTEGER;
BEGIN
    -- If question asked 5+ times and no task created yet
    IF NEW.occurrence_count >= 5 AND NOT NEW.legion_task_created THEN
        -- Create task in Legion (would call Legion API or direct insert)
        -- For now, just mark as needing task creation
        NEW.legion_task_created = FALSE;  -- Will be created by background job

        -- Log that this needs attention
        RAISE NOTICE 'Question asked % times, needs Legion task: %',
            NEW.occurrence_count, NEW.user_question;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_auto_create_legion_task
    BEFORE UPDATE ON ava_unanswered_questions
    FOR EACH ROW
    WHEN (NEW.occurrence_count > OLD.occurrence_count)
    EXECUTE FUNCTION auto_create_legion_task_if_needed();

-- Grants (adjust as needed)
-- GRANT ALL ON ALL TABLES IN SCHEMA public TO magnus_app;
-- GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO magnus_app;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO magnus_app;

COMMENT ON TABLE ava_conversations IS 'Tracks conversation sessions between users and AVA';
COMMENT ON TABLE ava_messages IS 'Individual messages and AVA responses with action tracking';
COMMENT ON TABLE ava_unanswered_questions IS 'Questions AVA couldn''t answer - auto-creates Legion tasks for high-frequency issues';
COMMENT ON TABLE ava_action_history IS 'Complete log of all actions AVA performed (watchlist analysis, portfolio queries, etc.)';
COMMENT ON TABLE ava_conversation_context IS 'Per-session memory for recall functionality';
COMMENT ON TABLE ava_user_preferences IS 'Persistent user preferences across sessions';
COMMENT ON TABLE ava_legion_task_log IS 'Tracks Legion tasks created from unanswered questions';
