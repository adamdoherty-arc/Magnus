-- ============================================================================
-- Task Management System - Database Schema
-- ============================================================================
-- Purpose: Track and manage development tasks for WheelStrategy project
-- Database: magnus (PostgreSQL)
-- Created: 2025-11-07
-- ============================================================================
--
-- Features:
-- - Development task tracking with status workflow
-- - Agent assignment and execution logging
-- - Task verification and user feedback loop
-- - File change tracking per task
-- - Dependency management between tasks
-- ============================================================================

-- ============================================================================
-- Table 1: development_tasks
-- ============================================================================
-- Core task tracking table with workflow states and metadata
-- ============================================================================

CREATE TABLE IF NOT EXISTS development_tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    task_type VARCHAR(100), -- 'bug_fix', 'feature', 'enhancement', 'qa', 'refactor', 'documentation'
    priority VARCHAR(20) DEFAULT 'medium', -- 'low', 'medium', 'high', 'critical'
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'in_progress', 'completed', 'failed', 'blocked', 'cancelled'
    assigned_agent VARCHAR(100), -- 'database-optimizer', 'backend-architect', 'qa-agent', etc.
    feature_area VARCHAR(200), -- 'comprehensive_strategy', 'dashboard', 'xtrades', 'kalshi', 'ava', 'options_flow', etc.

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,

    -- Duration tracking
    estimated_duration_minutes INTEGER,
    actual_duration_minutes INTEGER,

    -- Relationships
    dependencies TEXT[], -- Array of task IDs this task depends on (e.g., '{1,3,5}')
    parent_task_id INTEGER REFERENCES development_tasks(id) ON DELETE SET NULL, -- For subtasks
    tags TEXT[], -- Array of tags for categorization (e.g., '{frontend, api, urgent}')

    -- Metadata
    created_by VARCHAR(100) DEFAULT 'user',
    blocked_reason TEXT, -- Explanation if status is 'blocked'

    -- Constraints
    CONSTRAINT chk_status CHECK (status IN ('pending', 'in_progress', 'completed', 'failed', 'blocked', 'cancelled')),
    CONSTRAINT chk_priority CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    CONSTRAINT chk_task_type CHECK (task_type IN ('bug_fix', 'feature', 'enhancement', 'qa', 'refactor', 'documentation', 'investigation'))
);

-- Table comments
COMMENT ON TABLE development_tasks IS 'Core task tracking table for development workflow management';
COMMENT ON COLUMN development_tasks.task_type IS 'Type of task: bug_fix, feature, enhancement, qa, refactor, documentation, investigation';
COMMENT ON COLUMN development_tasks.status IS 'Current task status in workflow: pending → in_progress → completed/failed/cancelled';
COMMENT ON COLUMN development_tasks.assigned_agent IS 'Agent responsible for executing this task (e.g., database-optimizer, backend-architect)';
COMMENT ON COLUMN development_tasks.feature_area IS 'System area affected: comprehensive_strategy, dashboard, xtrades, kalshi, ava, options_flow';
COMMENT ON COLUMN development_tasks.dependencies IS 'Array of task IDs that must be completed before this task can start';
COMMENT ON COLUMN development_tasks.parent_task_id IS 'Parent task ID if this is a subtask, NULL for top-level tasks';

-- ============================================================================
-- Table 2: task_execution_log
-- ============================================================================
-- Detailed audit log of all task execution activities
-- ============================================================================

CREATE TABLE IF NOT EXISTS task_execution_log (
    id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL REFERENCES development_tasks(id) ON DELETE CASCADE,
    execution_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    agent_name VARCHAR(100), -- Agent that performed the action
    action_type VARCHAR(50), -- 'started', 'progress_update', 'completed', 'failed', 'verification', 'blocked', 'resumed'
    message TEXT, -- Description of the action or progress
    files_modified TEXT[], -- Array of file paths modified in this action
    error_details TEXT, -- Stack trace or error message if action failed
    duration_seconds INTEGER, -- Duration of this action in seconds

    CONSTRAINT chk_action_type CHECK (action_type IN ('started', 'progress_update', 'completed', 'failed', 'verification', 'blocked', 'resumed', 'cancelled'))
);

-- Table comments
COMMENT ON TABLE task_execution_log IS 'Detailed audit log tracking all actions taken during task execution';
COMMENT ON COLUMN task_execution_log.action_type IS 'Type of action: started, progress_update, completed, failed, verification, blocked, resumed, cancelled';
COMMENT ON COLUMN task_execution_log.files_modified IS 'Array of absolute file paths that were created, modified, or deleted';
COMMENT ON COLUMN task_execution_log.error_details IS 'Full error message or stack trace if action failed';

-- ============================================================================
-- Table 3: task_verification
-- ============================================================================
-- Task verification results and user feedback
-- ============================================================================

CREATE TABLE IF NOT EXISTS task_verification (
    id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL REFERENCES development_tasks(id) ON DELETE CASCADE,
    verified_by VARCHAR(100), -- 'qa_agent', 'user', 'automated_test'
    verification_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    passed BOOLEAN NOT NULL, -- TRUE if verification passed, FALSE if failed
    verification_notes TEXT, -- Detailed findings from verification
    test_results JSONB, -- Structured test results (test cases, pass/fail counts, etc.)
    user_feedback VARCHAR(50), -- 'approved', 'rejected', 'work_again', 'needs_changes'
    user_comments TEXT, -- User's comments or requested changes

    CONSTRAINT chk_user_feedback CHECK (user_feedback IN ('approved', 'rejected', 'work_again', 'needs_changes', NULL))
);

-- Table comments
COMMENT ON TABLE task_verification IS 'Stores verification results from QA agents, automated tests, and user feedback';
COMMENT ON COLUMN task_verification.verified_by IS 'Entity that performed verification: qa_agent, user, automated_test';
COMMENT ON COLUMN task_verification.passed IS 'TRUE if verification passed all checks, FALSE if failed';
COMMENT ON COLUMN task_verification.test_results IS 'JSON object containing structured test results';
COMMENT ON COLUMN task_verification.user_feedback IS 'User decision: approved, rejected, work_again, needs_changes';

-- ============================================================================
-- Table 4: task_files
-- ============================================================================
-- Track all file changes associated with each task
-- ============================================================================

CREATE TABLE IF NOT EXISTS task_files (
    id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL REFERENCES development_tasks(id) ON DELETE CASCADE,
    file_path TEXT NOT NULL, -- Absolute file path
    change_type VARCHAR(50), -- 'created', 'modified', 'deleted', 'renamed'
    lines_added INTEGER DEFAULT 0,
    lines_removed INTEGER DEFAULT 0,
    file_size_bytes INTEGER, -- File size after modification
    git_commit_hash VARCHAR(40), -- Git commit SHA if applicable
    modified_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT chk_change_type CHECK (change_type IN ('created', 'modified', 'deleted', 'renamed')),
    UNIQUE(task_id, file_path, change_type, modified_at) -- Allow tracking multiple changes to same file
);

-- Table comments
COMMENT ON TABLE task_files IS 'Tracks all file changes made during task execution';
COMMENT ON COLUMN task_files.change_type IS 'Type of change: created, modified, deleted, renamed';
COMMENT ON COLUMN task_files.git_commit_hash IS 'Git commit SHA that includes this change';

-- ============================================================================
-- INDEXES - Optimized for common query patterns
-- ============================================================================

-- Primary workflow queries
CREATE INDEX IF NOT EXISTS idx_tasks_status ON development_tasks(status) WHERE status IN ('pending', 'in_progress', 'blocked');
CREATE INDEX IF NOT EXISTS idx_tasks_priority_status ON development_tasks(priority, status) WHERE status != 'completed' AND status != 'cancelled';
CREATE INDEX IF NOT EXISTS idx_tasks_feature_area ON development_tasks(feature_area);
CREATE INDEX IF NOT EXISTS idx_tasks_assigned_agent ON development_tasks(assigned_agent);
CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON development_tasks(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_tasks_completed_at ON development_tasks(completed_at DESC) WHERE completed_at IS NOT NULL;

-- Parent-child task relationships
CREATE INDEX IF NOT EXISTS idx_tasks_parent_task_id ON development_tasks(parent_task_id) WHERE parent_task_id IS NOT NULL;

-- Execution log queries
CREATE INDEX IF NOT EXISTS idx_task_execution_log_task_id ON task_execution_log(task_id);
CREATE INDEX IF NOT EXISTS idx_task_execution_log_timestamp ON task_execution_log(execution_timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_task_execution_log_agent ON task_execution_log(agent_name);

-- Verification queries
CREATE INDEX IF NOT EXISTS idx_task_verification_task_id ON task_verification(task_id);
CREATE INDEX IF NOT EXISTS idx_task_verification_passed ON task_verification(passed, verification_timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_task_verification_user_feedback ON task_verification(user_feedback) WHERE user_feedback IS NOT NULL;

-- File tracking queries
CREATE INDEX IF NOT EXISTS idx_task_files_task_id ON task_files(task_id);
CREATE INDEX IF NOT EXISTS idx_task_files_path ON task_files(file_path);
CREATE INDEX IF NOT EXISTS idx_task_files_change_type ON task_files(change_type);

-- Full-text search on task titles and descriptions (GIN index for better performance)
CREATE INDEX IF NOT EXISTS idx_tasks_fulltext ON development_tasks USING gin(to_tsvector('english', title || ' ' || COALESCE(description, '')));

-- ============================================================================
-- FUNCTIONS - Helper functions for common operations
-- ============================================================================

-- Function: Get task duration in minutes
CREATE OR REPLACE FUNCTION calculate_task_duration(task_id_param INTEGER)
RETURNS INTEGER AS $$
DECLARE
    start_time TIMESTAMP WITH TIME ZONE;
    end_time TIMESTAMP WITH TIME ZONE;
    duration_minutes INTEGER;
BEGIN
    SELECT started_at, completed_at
    INTO start_time, end_time
    FROM development_tasks
    WHERE id = task_id_param;

    IF start_time IS NULL OR end_time IS NULL THEN
        RETURN NULL;
    END IF;

    duration_minutes := EXTRACT(EPOCH FROM (end_time - start_time)) / 60;
    RETURN duration_minutes;
END;
$$ LANGUAGE plpgsql;

-- Function: Check if task dependencies are met
CREATE OR REPLACE FUNCTION check_task_dependencies(task_id_param INTEGER)
RETURNS BOOLEAN AS $$
DECLARE
    task_dependencies TEXT[];
    dep_id INTEGER;
    dep_status VARCHAR(50);
    all_completed BOOLEAN := TRUE;
BEGIN
    -- Get dependencies array
    SELECT dependencies INTO task_dependencies
    FROM development_tasks
    WHERE id = task_id_param;

    -- If no dependencies, return TRUE
    IF task_dependencies IS NULL OR array_length(task_dependencies, 1) IS NULL THEN
        RETURN TRUE;
    END IF;

    -- Check each dependency
    FOREACH dep_id IN ARRAY task_dependencies::INTEGER[] LOOP
        SELECT status INTO dep_status
        FROM development_tasks
        WHERE id = dep_id;

        IF dep_status IS NULL OR dep_status != 'completed' THEN
            all_completed := FALSE;
            EXIT;
        END IF;
    END LOOP;

    RETURN all_completed;
END;
$$ LANGUAGE plpgsql;

-- Function: Get task completion percentage for a feature area
CREATE OR REPLACE FUNCTION get_feature_completion_percentage(feature_area_param VARCHAR)
RETURNS NUMERIC AS $$
DECLARE
    total_tasks INTEGER;
    completed_tasks INTEGER;
    percentage NUMERIC;
BEGIN
    SELECT COUNT(*) INTO total_tasks
    FROM development_tasks
    WHERE feature_area = feature_area_param
    AND status NOT IN ('cancelled');

    IF total_tasks = 0 THEN
        RETURN 0;
    END IF;

    SELECT COUNT(*) INTO completed_tasks
    FROM development_tasks
    WHERE feature_area = feature_area_param
    AND status = 'completed';

    percentage := (completed_tasks::NUMERIC / total_tasks::NUMERIC) * 100;
    RETURN ROUND(percentage, 2);
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- TRIGGERS - Automatic timestamp and status management
-- ============================================================================

-- Trigger: Update updated_at timestamp on task changes
CREATE OR REPLACE FUNCTION update_task_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();

    -- Set started_at when status changes to 'in_progress'
    IF OLD.status != 'in_progress' AND NEW.status = 'in_progress' AND NEW.started_at IS NULL THEN
        NEW.started_at = NOW();
    END IF;

    -- Set completed_at when status changes to 'completed'
    IF OLD.status != 'completed' AND NEW.status = 'completed' AND NEW.completed_at IS NULL THEN
        NEW.completed_at = NOW();
        NEW.actual_duration_minutes = calculate_task_duration(NEW.id);
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_task_timestamp
    BEFORE UPDATE ON development_tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_task_timestamp();

-- Trigger: Log task status changes
CREATE OR REPLACE FUNCTION log_task_status_change()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.status IS DISTINCT FROM NEW.status THEN
        INSERT INTO task_execution_log (task_id, agent_name, action_type, message)
        VALUES (
            NEW.id,
            NEW.assigned_agent,
            CASE
                WHEN NEW.status = 'in_progress' THEN 'started'
                WHEN NEW.status = 'completed' THEN 'completed'
                WHEN NEW.status = 'failed' THEN 'failed'
                WHEN NEW.status = 'blocked' THEN 'blocked'
                WHEN NEW.status = 'cancelled' THEN 'cancelled'
                ELSE 'progress_update'
            END,
            'Status changed from ' || COALESCE(OLD.status, 'NULL') || ' to ' || NEW.status
        );
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_log_task_status_change
    AFTER UPDATE ON development_tasks
    FOR EACH ROW
    EXECUTE FUNCTION log_task_status_change();

-- ============================================================================
-- VIEWS - Common query patterns for dashboard and reporting
-- ============================================================================

-- View: Active tasks requiring attention
CREATE OR REPLACE VIEW v_active_tasks AS
SELECT
    t.id,
    t.title,
    t.task_type,
    t.priority,
    t.status,
    t.assigned_agent,
    t.feature_area,
    t.created_at,
    t.started_at,
    t.estimated_duration_minutes,
    check_task_dependencies(t.id) AS dependencies_met,
    COUNT(DISTINCT l.id) AS execution_log_count,
    MAX(l.execution_timestamp) AS last_activity
FROM development_tasks t
LEFT JOIN task_execution_log l ON t.id = l.task_id
WHERE t.status IN ('pending', 'in_progress', 'blocked')
GROUP BY t.id
ORDER BY
    CASE t.priority
        WHEN 'critical' THEN 1
        WHEN 'high' THEN 2
        WHEN 'medium' THEN 3
        WHEN 'low' THEN 4
    END,
    t.created_at ASC;

-- View: Task performance metrics
CREATE OR REPLACE VIEW v_task_metrics AS
SELECT
    t.id,
    t.title,
    t.task_type,
    t.feature_area,
    t.assigned_agent,
    t.status,
    t.estimated_duration_minutes,
    t.actual_duration_minutes,
    CASE
        WHEN t.estimated_duration_minutes > 0 AND t.actual_duration_minutes IS NOT NULL
        THEN ROUND((t.actual_duration_minutes::NUMERIC / t.estimated_duration_minutes::NUMERIC) * 100, 2)
        ELSE NULL
    END AS duration_accuracy_pct,
    COUNT(DISTINCT f.id) AS files_changed,
    SUM(f.lines_added) AS total_lines_added,
    SUM(f.lines_removed) AS total_lines_removed,
    COUNT(DISTINCT v.id) AS verification_count,
    BOOL_AND(v.passed) AS all_verifications_passed
FROM development_tasks t
LEFT JOIN task_files f ON t.id = f.task_id
LEFT JOIN task_verification v ON t.id = v.task_id
WHERE t.status = 'completed'
GROUP BY t.id
ORDER BY t.completed_at DESC;

-- View: Feature area progress dashboard
CREATE OR REPLACE VIEW v_feature_progress AS
SELECT
    feature_area,
    COUNT(*) AS total_tasks,
    COUNT(*) FILTER (WHERE status = 'completed') AS completed_tasks,
    COUNT(*) FILTER (WHERE status = 'in_progress') AS in_progress_tasks,
    COUNT(*) FILTER (WHERE status = 'pending') AS pending_tasks,
    COUNT(*) FILTER (WHERE status = 'blocked') AS blocked_tasks,
    COUNT(*) FILTER (WHERE status = 'failed') AS failed_tasks,
    get_feature_completion_percentage(feature_area) AS completion_percentage,
    MIN(created_at) AS first_task_created,
    MAX(updated_at) AS last_activity
FROM development_tasks
WHERE status NOT IN ('cancelled')
GROUP BY feature_area
ORDER BY completion_percentage ASC, total_tasks DESC;

-- View: Agent workload distribution
CREATE OR REPLACE VIEW v_agent_workload AS
SELECT
    assigned_agent,
    COUNT(*) AS total_assigned_tasks,
    COUNT(*) FILTER (WHERE status = 'in_progress') AS active_tasks,
    COUNT(*) FILTER (WHERE status = 'pending') AS pending_tasks,
    COUNT(*) FILTER (WHERE status = 'completed') AS completed_tasks,
    COUNT(*) FILTER (WHERE status = 'failed') AS failed_tasks,
    AVG(actual_duration_minutes) FILTER (WHERE actual_duration_minutes IS NOT NULL) AS avg_completion_time_minutes,
    COUNT(*) FILTER (WHERE status = 'completed' AND actual_duration_minutes <= estimated_duration_minutes) AS on_time_completions,
    COUNT(*) FILTER (WHERE status = 'completed' AND actual_duration_minutes > estimated_duration_minutes) AS overdue_completions
FROM development_tasks
WHERE assigned_agent IS NOT NULL
GROUP BY assigned_agent
ORDER BY active_tasks DESC, total_assigned_tasks DESC;

-- ============================================================================
-- INITIAL DATA - Sample configuration
-- ============================================================================

-- Add system configuration task (tracks schema deployment)
INSERT INTO development_tasks (
    title,
    description,
    task_type,
    priority,
    status,
    assigned_agent,
    feature_area,
    created_by
) VALUES (
    'Initialize Task Management System',
    'Deploy task management database schema and verify table creation',
    'feature',
    'high',
    'completed',
    'database-optimizer',
    'task_management',
    'system'
) ON CONFLICT DO NOTHING;

-- ============================================================================
-- PERMISSIONS - Grant appropriate access (adjust based on your users)
-- ============================================================================

-- Example: Grant permissions to application user
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO wheel_strategy_app;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO wheel_strategy_app;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO wheel_strategy_app;

-- ============================================================================
-- MAINTENANCE QUERIES - Useful for database administrators
-- ============================================================================

-- Vacuum and analyze for optimal performance
-- VACUUM ANALYZE development_tasks;
-- VACUUM ANALYZE task_execution_log;
-- VACUUM ANALYZE task_verification;
-- VACUUM ANALYZE task_files;

-- Check table sizes
-- SELECT
--     schemaname,
--     tablename,
--     pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
-- FROM pg_tables
-- WHERE tablename LIKE 'development_tasks%' OR tablename LIKE 'task_%'
-- ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- ============================================================================
-- SCHEMA VERIFICATION QUERY
-- ============================================================================

-- Run this query to verify all tables were created successfully:
SELECT
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) AS column_count
FROM information_schema.tables t
WHERE table_schema = 'public'
AND table_name IN ('development_tasks', 'task_execution_log', 'task_verification', 'task_files')
ORDER BY table_name;

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
