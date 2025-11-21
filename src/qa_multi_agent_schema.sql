-- ============================================================================
-- Multi-Agent QA System - Database Schema
-- ============================================================================
-- Purpose: Comprehensive QA system with agent sign-offs and issue tracking
-- Database: magnus (PostgreSQL)
-- Created: 2025-11-10
-- ============================================================================
--
-- Features:
-- - Multi-agent review and sign-off requirements
-- - QA issue tracking (separate from main tasks)
-- - Agent expertise tracking via RAG
-- - Historical audit trail (NEVER delete)
-- - Integration with Legion agent system
-- - Agent-specific vector embeddings for expertise
-- ============================================================================

-- ============================================================================
-- Table 1: qa_agent_registry
-- ============================================================================
-- Registry of all QA agents and their expertise areas
-- ============================================================================

CREATE TABLE IF NOT EXISTS qa_agent_registry (
    id SERIAL PRIMARY KEY,
    agent_name VARCHAR(100) UNIQUE NOT NULL,
    agent_type VARCHAR(100) NOT NULL, -- 'code-reviewer', 'security-auditor', 'performance-engineer', etc.
    expertise_areas TEXT[], -- Array of expertise domains
    description TEXT,
    is_active BOOLEAN DEFAULT true,

    -- RAG/Vector DB info
    rag_collection_name VARCHAR(200), -- Collection name in vector DB
    expertise_doc_count INTEGER DEFAULT 0, -- Number of documents in expertise base

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_active_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Statistics
    total_reviews INTEGER DEFAULT 0,
    total_issues_found INTEGER DEFAULT 0,
    total_approvals INTEGER DEFAULT 0,
    average_review_time_minutes INTEGER,

    CONSTRAINT chk_agent_type CHECK (agent_type IN (
        'code-reviewer', 'security-auditor', 'performance-engineer',
        'database-optimizer', 'ui-ux-designer', 'accessibility-auditor',
        'api-architect', 'test-automator', 'documentation-reviewer',
        'business-analyst', 'deployment-engineer', 'backend-architect',
        'frontend-developer', 'ai-engineer', 'data-engineer'
    ))
);

COMMENT ON TABLE qa_agent_registry IS 'Registry of all QA agents with their expertise and performance metrics';
COMMENT ON COLUMN qa_agent_registry.expertise_areas IS 'Array of domains this agent is expert in (e.g., {security, authentication, encryption})';
COMMENT ON COLUMN qa_agent_registry.rag_collection_name IS 'Vector database collection containing agent''s expertise documents';

-- ============================================================================
-- Table 2: qa_sign_off_requirements
-- ============================================================================
-- Defines which agents must sign off for different task types
-- ============================================================================

CREATE TABLE IF NOT EXISTS qa_sign_off_requirements (
    id SERIAL PRIMARY KEY,
    task_type VARCHAR(100) NOT NULL, -- 'feature', 'bug_fix', 'enhancement', etc.
    feature_area VARCHAR(200), -- NULL = applies to all features
    priority VARCHAR(20), -- NULL = applies to all priorities

    -- Required agents for sign-off
    required_agents TEXT[] NOT NULL, -- Array of agent names that MUST review
    optional_agents TEXT[], -- Array of agent names that CAN review (recommended)

    -- Review settings
    minimum_required_sign_offs INTEGER DEFAULT 2, -- Minimum approvals needed
    requires_unanimous BOOLEAN DEFAULT false, -- All required agents must approve

    -- Auto-approval settings
    allow_auto_approval BOOLEAN DEFAULT false,
    auto_approval_conditions JSONB, -- Conditions for auto-approval

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by VARCHAR(100),
    is_active BOOLEAN DEFAULT true,

    CONSTRAINT chk_task_type_req CHECK (task_type IN ('feature', 'bug_fix', 'enhancement', 'qa', 'refactor', 'documentation', 'investigation'))
);

COMMENT ON TABLE qa_sign_off_requirements IS 'Defines QA sign-off requirements for different task types and priorities';
COMMENT ON COLUMN qa_sign_off_requirements.required_agents IS 'Agents that MUST review (e.g., {code-reviewer, security-auditor})';
COMMENT ON COLUMN qa_sign_off_requirements.requires_unanimous IS 'If true, ALL required agents must approve (no rejections allowed)';

-- ============================================================================
-- Table 3: qa_agent_sign_offs
-- ============================================================================
-- Tracks individual agent sign-offs for each task
-- NEVER DELETE - Historical record of all reviews
-- ============================================================================

CREATE TABLE IF NOT EXISTS qa_agent_sign_offs (
    id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL REFERENCES development_tasks(id) ON DELETE CASCADE,
    agent_name VARCHAR(100) NOT NULL REFERENCES qa_agent_registry(agent_name),

    -- Review details
    sign_off_status VARCHAR(50) NOT NULL DEFAULT 'pending', -- 'pending', 'approved', 'rejected', 'needs_changes', 'delegated'
    review_started_at TIMESTAMP WITH TIME ZONE,
    review_completed_at TIMESTAMP WITH TIME ZONE,
    review_duration_minutes INTEGER,

    -- Review findings
    review_notes TEXT,
    issues_found INTEGER DEFAULT 0,
    severity_level VARCHAR(50), -- 'critical', 'high', 'medium', 'low', 'info'

    -- Recommendations
    recommendation TEXT, -- Agent's recommendation
    confidence_score NUMERIC(3, 2), -- 0.00 to 1.00 (agent's confidence in their review)

    -- RAG-assisted review
    rag_context_used BOOLEAN DEFAULT false, -- Did agent use RAG expertise?
    rag_sources TEXT[], -- Documents/sources consulted from RAG

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Historical tracking (NEVER modified after completion)
    is_final BOOLEAN DEFAULT false, -- Once true, record is immutable
    superseded_by INTEGER REFERENCES qa_agent_sign_offs(id), -- If agent changes mind

    CONSTRAINT chk_sign_off_status CHECK (sign_off_status IN ('pending', 'approved', 'rejected', 'needs_changes', 'delegated', 'skipped')),
    CONSTRAINT chk_severity CHECK (severity_level IN ('critical', 'high', 'medium', 'low', 'info', NULL)),
    CONSTRAINT chk_confidence CHECK (confidence_score IS NULL OR (confidence_score >= 0 AND confidence_score <= 1)),
    UNIQUE(task_id, agent_name, created_at) -- Allow multiple reviews by same agent (history)
);

COMMENT ON TABLE qa_agent_sign_offs IS 'Individual agent sign-offs for tasks - NEVER DELETE, historical record';
COMMENT ON COLUMN qa_agent_sign_offs.sign_off_status IS 'pending → approved/rejected/needs_changes (immutable after final)';
COMMENT ON COLUMN qa_agent_sign_offs.is_final IS 'Once true, this record cannot be modified (historical integrity)';
COMMENT ON COLUMN qa_agent_sign_offs.superseded_by IS 'If agent re-reviews, points to newer sign-off record';

-- ============================================================================
-- Table 4: qa_tasks
-- ============================================================================
-- QA issues/tasks created during review process
-- Separate from main development_tasks to track QA-specific work
-- NEVER DELETE - Historical record of all QA issues
-- ============================================================================

CREATE TABLE IF NOT EXISTS qa_tasks (
    id SERIAL PRIMARY KEY,

    -- Relationship to original task
    parent_task_id INTEGER NOT NULL REFERENCES development_tasks(id) ON DELETE CASCADE,
    sign_off_id INTEGER REFERENCES qa_agent_sign_offs(id), -- Which sign-off created this issue

    -- QA Issue details
    title VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,
    issue_type VARCHAR(100) NOT NULL, -- 'bug', 'security', 'performance', 'code_quality', 'documentation', etc.
    severity VARCHAR(50) NOT NULL, -- 'critical', 'high', 'medium', 'low'

    -- Agent who found the issue
    reported_by_agent VARCHAR(100) NOT NULL REFERENCES qa_agent_registry(agent_name),
    reported_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Assignment
    assigned_to_agent VARCHAR(100), -- Agent assigned to fix
    assigned_at TIMESTAMP WITH TIME ZONE,

    -- Status tracking
    status VARCHAR(50) DEFAULT 'open', -- 'open', 'in_progress', 'fixed', 'verified', 'closed', 'wont_fix', 'duplicate'
    started_at TIMESTAMP WITH TIME ZONE,
    fixed_at TIMESTAMP WITH TIME ZONE,
    verified_at TIMESTAMP WITH TIME ZONE,
    closed_at TIMESTAMP WITH TIME ZONE,

    -- Resolution
    resolution_notes TEXT,
    fix_verification_method TEXT, -- How the fix was verified
    verified_by_agent VARCHAR(100) REFERENCES qa_agent_registry(agent_name),

    -- Impact assessment
    impact_areas TEXT[], -- Areas affected (e.g., {authentication, database, api})
    breaking_change BOOLEAN DEFAULT false,
    requires_migration BOOLEAN DEFAULT false,

    -- Metadata
    tags TEXT[],
    priority INTEGER DEFAULT 3, -- 1 (highest) to 5 (lowest)
    estimated_fix_time_minutes INTEGER,
    actual_fix_time_minutes INTEGER,

    -- Historical tracking (NEVER delete)
    is_deleted BOOLEAN DEFAULT false, -- Soft delete
    deleted_at TIMESTAMP WITH TIME ZONE,
    deleted_by VARCHAR(100),
    delete_reason TEXT,

    -- Audit trail
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT chk_qa_issue_type CHECK (issue_type IN (
        'bug', 'security', 'performance', 'code_quality', 'documentation',
        'accessibility', 'usability', 'compatibility', 'data_integrity',
        'api_contract', 'best_practice', 'technical_debt'
    )),
    CONSTRAINT chk_qa_severity CHECK (severity IN ('critical', 'high', 'medium', 'low')),
    CONSTRAINT chk_qa_status CHECK (status IN ('open', 'in_progress', 'fixed', 'verified', 'closed', 'wont_fix', 'duplicate'))
);

COMMENT ON TABLE qa_tasks IS 'QA issues found during review - NEVER physically deleted, only marked deleted';
COMMENT ON COLUMN qa_tasks.is_deleted IS 'Soft delete flag - TRUE means logically deleted but data preserved';
COMMENT ON COLUMN qa_tasks.issue_type IS 'Category of QA issue for classification and routing';

-- ============================================================================
-- Table 5: qa_agent_expertise
-- ============================================================================
-- Agent expertise knowledge base with vector embeddings
-- Stores documents/knowledge that agents use for reviews
-- ============================================================================

CREATE TABLE IF NOT EXISTS qa_agent_expertise (
    id SERIAL PRIMARY KEY,
    agent_name VARCHAR(100) NOT NULL REFERENCES qa_agent_registry(agent_name),

    -- Expertise document
    document_title VARCHAR(500) NOT NULL,
    document_content TEXT NOT NULL,
    document_type VARCHAR(100), -- 'best_practice', 'pattern', 'anti_pattern', 'guideline', 'checklist'

    -- Categorization
    expertise_domain VARCHAR(200) NOT NULL, -- e.g., 'security', 'performance', 'api_design'
    relevance_tags TEXT[],

    -- Vector embedding (for RAG)
    embedding JSONB, -- 768-dim embedding from sentence-transformers stored as JSON array
    embedding_model VARCHAR(100) DEFAULT 'all-mpnet-base-v2',

    -- Usage tracking
    times_referenced INTEGER DEFAULT 0,
    last_referenced_at TIMESTAMP WITH TIME ZONE,
    relevance_score NUMERIC(3, 2) DEFAULT 1.00, -- Quality score (0.00 to 1.00)

    -- Source information
    source_url TEXT,
    source_file TEXT,
    source_reference TEXT,

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true,

    CONSTRAINT chk_relevance_score CHECK (relevance_score >= 0 AND relevance_score <= 1)
);

COMMENT ON TABLE qa_agent_expertise IS 'Knowledge base for agent expertise with vector embeddings for RAG';
COMMENT ON COLUMN qa_agent_expertise.embedding IS '768-dimensional vector embedding for semantic search';
COMMENT ON COLUMN qa_agent_expertise.relevance_score IS 'Quality/relevance score updated based on usage and feedback';

-- ============================================================================
-- Table 6: qa_review_checklist
-- ============================================================================
-- Dynamic checklists for agent reviews based on task type
-- ============================================================================

CREATE TABLE IF NOT EXISTS qa_review_checklist (
    id SERIAL PRIMARY KEY,
    agent_name VARCHAR(100) NOT NULL REFERENCES qa_agent_registry(agent_name),
    task_type VARCHAR(100) NOT NULL,
    feature_area VARCHAR(200),

    -- Checklist items
    checklist_items JSONB NOT NULL, -- Array of checklist items with descriptions

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true,
    version INTEGER DEFAULT 1,

    UNIQUE(agent_name, task_type, feature_area, version)
);

COMMENT ON TABLE qa_review_checklist IS 'Dynamic checklist templates for agent reviews';
COMMENT ON COLUMN qa_review_checklist.checklist_items IS 'JSON array of checklist items: [{item: "...", category: "...", critical: true/false}]';

-- ============================================================================
-- Table 7: qa_review_history
-- ============================================================================
-- Complete history of all QA reviews
-- Immutable historical record - NEVER delete or modify
-- ============================================================================

CREATE TABLE IF NOT EXISTS qa_review_history (
    id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL REFERENCES development_tasks(id),
    sign_off_id INTEGER NOT NULL REFERENCES qa_agent_sign_offs(id),

    -- Snapshot of review state
    review_snapshot JSONB NOT NULL, -- Complete snapshot of review at time of completion
    checklist_results JSONB, -- Results of checklist items

    -- Timing
    review_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Immutability
    is_immutable BOOLEAN DEFAULT true,
    snapshot_hash VARCHAR(64), -- SHA-256 hash of snapshot for integrity verification

    CONSTRAINT chk_immutable CHECK (is_immutable = true) -- Enforces immutability
);

COMMENT ON TABLE qa_review_history IS 'Immutable historical record of all QA reviews for audit trail';
COMMENT ON COLUMN qa_review_history.review_snapshot IS 'Complete snapshot including agent, status, findings, recommendations';
COMMENT ON COLUMN qa_review_history.snapshot_hash IS 'Hash for detecting tampering - ensures historical integrity';

-- ============================================================================
-- INDEXES - Optimized for QA workflow queries
-- ============================================================================

-- Agent registry
CREATE INDEX IF NOT EXISTS idx_qa_agents_active ON qa_agent_registry(agent_name) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_qa_agents_type ON qa_agent_registry(agent_type);

-- Sign-off requirements
CREATE INDEX IF NOT EXISTS idx_qa_requirements_task_type ON qa_sign_off_requirements(task_type) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_qa_requirements_feature ON qa_sign_off_requirements(feature_area) WHERE is_active = true;

-- Agent sign-offs
CREATE INDEX IF NOT EXISTS idx_qa_signoffs_task ON qa_agent_sign_offs(task_id, sign_off_status);
CREATE INDEX IF NOT EXISTS idx_qa_signoffs_agent ON qa_agent_sign_offs(agent_name, sign_off_status);
CREATE INDEX IF NOT EXISTS idx_qa_signoffs_pending ON qa_agent_sign_offs(task_id) WHERE sign_off_status = 'pending';
CREATE INDEX IF NOT EXISTS idx_qa_signoffs_final ON qa_agent_sign_offs(task_id) WHERE is_final = true;

-- QA tasks
CREATE INDEX IF NOT EXISTS idx_qa_tasks_parent ON qa_tasks(parent_task_id);
CREATE INDEX IF NOT EXISTS idx_qa_tasks_status ON qa_tasks(status) WHERE is_deleted = false;
CREATE INDEX IF NOT EXISTS idx_qa_tasks_agent ON qa_tasks(reported_by_agent, status);
CREATE INDEX IF NOT EXISTS idx_qa_tasks_severity ON qa_tasks(severity, status) WHERE is_deleted = false;
CREATE INDEX IF NOT EXISTS idx_qa_tasks_open ON qa_tasks(parent_task_id, status) WHERE status IN ('open', 'in_progress') AND is_deleted = false;

-- Agent expertise (with vector similarity search support)
CREATE INDEX IF NOT EXISTS idx_qa_expertise_agent ON qa_agent_expertise(agent_name) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_qa_expertise_domain ON qa_agent_expertise(expertise_domain) WHERE is_active = true;
-- Vector index for similarity search (requires pgvector extension)
-- Commented out: Using ChromaDB for vector search instead
-- CREATE INDEX IF NOT EXISTS idx_qa_expertise_embedding ON qa_agent_expertise USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Review history
CREATE INDEX IF NOT EXISTS idx_qa_history_task ON qa_review_history(task_id, review_timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_qa_history_signoff ON qa_review_history(sign_off_id);

-- ============================================================================
-- FUNCTIONS - QA Workflow Automation
-- ============================================================================

-- Function: Check if task has all required sign-offs
CREATE OR REPLACE FUNCTION check_qa_sign_offs_complete(task_id_param INTEGER)
RETURNS BOOLEAN AS $$
DECLARE
    required_agents TEXT[];
    minimum_signoffs INTEGER;
    requires_unanimous BOOLEAN;
    approved_count INTEGER;
    rejected_count INTEGER;
    total_required INTEGER;
BEGIN
    -- Get requirements for this task
    SELECT
        req.required_agents,
        req.minimum_required_sign_offs,
        req.requires_unanimous
    INTO
        required_agents,
        minimum_signoffs,
        requires_unanimous
    FROM qa_sign_off_requirements req
    JOIN development_tasks t ON (
        req.task_type = t.task_type
        AND (req.feature_area IS NULL OR req.feature_area = t.feature_area)
        AND (req.priority IS NULL OR req.priority = t.priority)
    )
    WHERE t.id = task_id_param
    AND req.is_active = true
    LIMIT 1;

    -- If no requirements found, return true (no sign-offs needed)
    IF required_agents IS NULL THEN
        RETURN true;
    END IF;

    -- Count approvals and rejections from required agents
    SELECT
        COUNT(*) FILTER (WHERE sign_off_status = 'approved'),
        COUNT(*) FILTER (WHERE sign_off_status = 'rejected')
    INTO approved_count, rejected_count
    FROM qa_agent_sign_offs
    WHERE task_id = task_id_param
    AND agent_name = ANY(required_agents)
    AND is_final = true;

    total_required := array_length(required_agents, 1);

    -- Check if unanimous approval required
    IF requires_unanimous THEN
        RETURN (approved_count = total_required AND rejected_count = 0);
    END IF;

    -- Check if minimum sign-offs met and no rejections
    RETURN (approved_count >= minimum_signoffs AND rejected_count = 0);
END;
$$ LANGUAGE plpgsql;

-- Function: Get next pending sign-off for an agent
CREATE OR REPLACE FUNCTION get_next_pending_sign_off(agent_name_param VARCHAR)
RETURNS TABLE (
    task_id INTEGER,
    task_title VARCHAR,
    task_priority VARCHAR,
    sign_off_id INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        t.id,
        t.title,
        t.priority,
        s.id
    FROM development_tasks t
    JOIN qa_agent_sign_offs s ON t.id = s.task_id
    WHERE s.agent_name = agent_name_param
    AND s.sign_off_status = 'pending'
    AND t.status = 'completed' -- Only review completed tasks
    ORDER BY
        CASE t.priority
            WHEN 'critical' THEN 1
            WHEN 'high' THEN 2
            WHEN 'medium' THEN 3
            WHEN 'low' THEN 4
        END,
        t.completed_at DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- Function: Calculate agent review performance
CREATE OR REPLACE FUNCTION calculate_agent_review_metrics(agent_name_param VARCHAR)
RETURNS TABLE (
    total_reviews BIGINT,
    total_approved BIGINT,
    total_rejected BIGINT,
    total_issues_found BIGINT,
    avg_review_time_minutes NUMERIC,
    avg_confidence_score NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(*) as total_reviews,
        COUNT(*) FILTER (WHERE sign_off_status = 'approved') as total_approved,
        COUNT(*) FILTER (WHERE sign_off_status = 'rejected') as total_rejected,
        SUM(issues_found) as total_issues_found,
        AVG(review_duration_minutes) as avg_review_time_minutes,
        AVG(confidence_score) as avg_confidence_score
    FROM qa_agent_sign_offs
    WHERE agent_name = agent_name_param
    AND is_final = true;
END;
$$ LANGUAGE plpgsql;

-- Function: Create QA task from sign-off issue
CREATE OR REPLACE FUNCTION create_qa_task_from_signoff(
    parent_task_id_param INTEGER,
    sign_off_id_param INTEGER,
    title_param VARCHAR,
    description_param TEXT,
    issue_type_param VARCHAR,
    severity_param VARCHAR,
    reported_by_param VARCHAR
) RETURNS INTEGER AS $$
DECLARE
    new_qa_task_id INTEGER;
BEGIN
    INSERT INTO qa_tasks (
        parent_task_id,
        sign_off_id,
        title,
        description,
        issue_type,
        severity,
        reported_by_agent
    ) VALUES (
        parent_task_id_param,
        sign_off_id_param,
        title_param,
        description_param,
        issue_type_param,
        severity_param,
        reported_by_param
    )
    RETURNING id INTO new_qa_task_id;

    -- Update sign-off issues count
    UPDATE qa_agent_sign_offs
    SET issues_found = issues_found + 1
    WHERE id = sign_off_id_param;

    RETURN new_qa_task_id;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- TRIGGERS - Automated QA Workflow
-- ============================================================================

-- Trigger: Update agent registry statistics
CREATE OR REPLACE FUNCTION update_agent_stats()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.is_final = true AND OLD.is_final = false THEN
        UPDATE qa_agent_registry
        SET
            total_reviews = total_reviews + 1,
            total_approvals = total_approvals + CASE WHEN NEW.sign_off_status = 'approved' THEN 1 ELSE 0 END,
            total_issues_found = total_issues_found + NEW.issues_found,
            last_active_at = NOW()
        WHERE agent_name = NEW.agent_name;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_agent_stats
    AFTER UPDATE ON qa_agent_sign_offs
    FOR EACH ROW
    EXECUTE FUNCTION update_agent_stats();

-- Trigger: Create immutable history record on sign-off completion
CREATE OR REPLACE FUNCTION create_review_history()
RETURNS TRIGGER AS $$
DECLARE
    snapshot JSONB;
    hash VARCHAR(64);
BEGIN
    IF NEW.is_final = true AND (OLD.is_final IS NULL OR OLD.is_final = false) THEN
        -- Create snapshot
        snapshot := jsonb_build_object(
            'agent_name', NEW.agent_name,
            'task_id', NEW.task_id,
            'sign_off_status', NEW.sign_off_status,
            'review_notes', NEW.review_notes,
            'issues_found', NEW.issues_found,
            'severity_level', NEW.severity_level,
            'recommendation', NEW.recommendation,
            'confidence_score', NEW.confidence_score,
            'review_started_at', NEW.review_started_at,
            'review_completed_at', NEW.review_completed_at,
            'review_duration_minutes', NEW.review_duration_minutes
        );

        -- Calculate hash
        hash := encode(digest(snapshot::text, 'sha256'), 'hex');

        -- Insert into history
        INSERT INTO qa_review_history (
            task_id,
            sign_off_id,
            review_snapshot,
            snapshot_hash
        ) VALUES (
            NEW.task_id,
            NEW.id,
            snapshot,
            hash
        );
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_create_review_history
    AFTER UPDATE ON qa_agent_sign_offs
    FOR EACH ROW
    EXECUTE FUNCTION create_review_history();

-- Trigger: Prevent modification of final sign-offs (immutability)
CREATE OR REPLACE FUNCTION enforce_signoff_immutability()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.is_final = true THEN
        -- Allow only superseding (creating new record)
        IF NEW.superseded_by IS DISTINCT FROM OLD.superseded_by THEN
            RETURN NEW;
        END IF;

        RAISE EXCEPTION 'Cannot modify final sign-off record. Create new sign-off instead.';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_enforce_signoff_immutability
    BEFORE UPDATE ON qa_agent_sign_offs
    FOR EACH ROW
    EXECUTE FUNCTION enforce_signoff_immutability();

-- Trigger: Soft delete for QA tasks (never hard delete)
CREATE OR REPLACE FUNCTION prevent_qa_task_delete()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'QA tasks cannot be deleted. Use is_deleted flag for soft delete.';
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_prevent_qa_task_delete
    BEFORE DELETE ON qa_tasks
    FOR EACH ROW
    EXECUTE FUNCTION prevent_qa_task_delete();

-- ============================================================================
-- VIEWS - QA Dashboard and Reporting
-- ============================================================================

-- View: Pending QA reviews
CREATE OR REPLACE VIEW v_pending_qa_reviews AS
SELECT
    t.id as task_id,
    t.title,
    t.task_type,
    t.priority,
    t.feature_area,
    t.completed_at,
    s.id as sign_off_id,
    s.agent_name,
    s.created_at as review_requested_at,
    EXTRACT(EPOCH FROM (NOW() - s.created_at)) / 3600 as hours_waiting
FROM development_tasks t
JOIN qa_agent_sign_offs s ON t.id = s.task_id
WHERE s.sign_off_status = 'pending'
AND t.status = 'completed'
ORDER BY t.priority, t.completed_at DESC;

-- View: Open QA tasks requiring fixes
CREATE OR REPLACE VIEW v_open_qa_tasks AS
SELECT
    q.id,
    q.parent_task_id,
    t.title as parent_task_title,
    q.title as qa_issue_title,
    q.issue_type,
    q.severity,
    q.status,
    q.reported_by_agent,
    q.assigned_to_agent,
    q.reported_at,
    EXTRACT(EPOCH FROM (NOW() - q.reported_at)) / 86400 as days_open
FROM qa_tasks q
JOIN development_tasks t ON q.parent_task_id = t.id
WHERE q.status IN ('open', 'in_progress')
AND q.is_deleted = false
ORDER BY
    CASE q.severity
        WHEN 'critical' THEN 1
        WHEN 'high' THEN 2
        WHEN 'medium' THEN 3
        WHEN 'low' THEN 4
    END,
    q.reported_at ASC;

-- View: QA agent performance metrics
CREATE OR REPLACE VIEW v_qa_agent_performance AS
SELECT
    a.agent_name,
    a.agent_type,
    a.total_reviews,
    a.total_approvals,
    a.total_issues_found,
    a.average_review_time_minutes,
    ROUND((a.total_approvals::NUMERIC / NULLIF(a.total_reviews, 0)) * 100, 2) as approval_rate_pct,
    ROUND((a.total_issues_found::NUMERIC / NULLIF(a.total_reviews, 0)), 2) as avg_issues_per_review,
    a.last_active_at,
    COUNT(DISTINCT s.id) FILTER (WHERE s.sign_off_status = 'pending') as pending_reviews
FROM qa_agent_registry a
LEFT JOIN qa_agent_sign_offs s ON a.agent_name = s.agent_name
WHERE a.is_active = true
GROUP BY a.agent_name, a.agent_type, a.total_reviews, a.total_approvals,
         a.total_issues_found, a.average_review_time_minutes, a.last_active_at
ORDER BY a.total_reviews DESC;

-- View: Task QA status
CREATE OR REPLACE VIEW v_task_qa_status AS
SELECT
    t.id as task_id,
    t.title,
    t.status as task_status,
    COUNT(DISTINCT s.id) as total_reviews,
    COUNT(DISTINCT s.id) FILTER (WHERE s.sign_off_status = 'approved') as approvals,
    COUNT(DISTINCT s.id) FILTER (WHERE s.sign_off_status = 'rejected') as rejections,
    COUNT(DISTINCT s.id) FILTER (WHERE s.sign_off_status = 'pending') as pending,
    check_qa_sign_offs_complete(t.id) as all_sign_offs_complete,
    COUNT(DISTINCT q.id) FILTER (WHERE q.status IN ('open', 'in_progress') AND q.is_deleted = false) as open_qa_issues
FROM development_tasks t
LEFT JOIN qa_agent_sign_offs s ON t.id = s.task_id AND s.is_final = true
LEFT JOIN qa_tasks q ON t.id = q.parent_task_id
WHERE t.status = 'completed'
GROUP BY t.id, t.title, t.status
ORDER BY t.completed_at DESC;

-- ============================================================================
-- INITIAL DATA - Default QA Agents and Requirements
-- ============================================================================

-- Register default QA agents
INSERT INTO qa_agent_registry (agent_name, agent_type, expertise_areas, description, rag_collection_name) VALUES
('code-reviewer', 'code-reviewer', ARRAY['code_quality', 'best_practices', 'maintainability'], 'Reviews code quality, patterns, and maintainability', 'code_review_expertise'),
('security-auditor', 'security-auditor', ARRAY['security', 'authentication', 'encryption', 'owasp'], 'Audits security vulnerabilities and compliance', 'security_expertise'),
('performance-engineer', 'performance-engineer', ARRAY['performance', 'optimization', 'scalability'], 'Reviews performance and scalability', 'performance_expertise'),
('database-optimizer', 'database-optimizer', ARRAY['database', 'sql', 'indexing', 'queries'], 'Optimizes database operations', 'database_expertise'),
('test-automator', 'test-automator', ARRAY['testing', 'qa', 'automation', 'coverage'], 'Ensures comprehensive testing', 'testing_expertise'),
('api-architect', 'api-architect', ARRAY['api_design', 'rest', 'graphql', 'contracts'], 'Reviews API design and contracts', 'api_expertise'),
('frontend-developer', 'frontend-developer', ARRAY['ui', 'ux', 'react', 'accessibility'], 'Reviews UI/UX and frontend code', 'frontend_expertise'),
('backend-architect', 'backend-architect', ARRAY['architecture', 'design_patterns', 'scalability'], 'Reviews system architecture', 'backend_expertise')
ON CONFLICT (agent_name) DO NOTHING;

-- Define default sign-off requirements
INSERT INTO qa_sign_off_requirements (task_type, required_agents, minimum_required_sign_offs, requires_unanimous) VALUES
('feature', ARRAY['code-reviewer', 'security-auditor', 'test-automator'], 2, false),
('bug_fix', ARRAY['code-reviewer'], 1, false),
('enhancement', ARRAY['code-reviewer', 'performance-engineer'], 1, false),
('refactor', ARRAY['code-reviewer', 'backend-architect'], 2, false),
('documentation', ARRAY['code-reviewer'], 1, false)
ON CONFLICT DO NOTHING;

-- ============================================================================
-- PERMISSIONS
-- ============================================================================

-- Grant permissions (adjust based on your setup)
-- GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO wheel_strategy_app;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO wheel_strategy_app;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO wheel_strategy_app;

-- ============================================================================
-- VERIFICATION QUERY
-- ============================================================================

-- Verify all QA tables were created
SELECT
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) AS column_count
FROM information_schema.tables t
WHERE table_schema = 'public'
AND table_name LIKE 'qa_%'
ORDER BY table_name;

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
