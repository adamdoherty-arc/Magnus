-- ============================================================================
-- AI-Native Continuous Improvement System - Database Schema
-- ============================================================================
-- Purpose: World-class AI-driven platform self-improvement and learning
-- Database: magnus (PostgreSQL)
-- Created: 2025-11-06
-- Version: 1.0.0
-- ============================================================================

-- ============================================================================
-- PART 1: ENHANCEMENT TRACKING SYSTEM
-- ============================================================================

-- ============================================================================
-- Table: ci_enhancements
-- ============================================================================
-- Master table for all enhancement requests (replaces markdown wishlists)
-- Supports AI-driven prioritization and tracking
-- ============================================================================

CREATE TABLE IF NOT EXISTS ci_enhancements (
    id SERIAL PRIMARY KEY,

    -- Core identification
    title VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,
    feature_area VARCHAR(100), -- 'dashboard', 'positions', 'options_flow', 'general'

    -- Categorization
    category VARCHAR(50) NOT NULL, -- 'bug_fix', 'enhancement', 'new_feature', 'performance', 'security', 'refactoring'
    priority VARCHAR(20) NOT NULL DEFAULT 'medium', -- 'critical', 'high', 'medium', 'low'
    complexity VARCHAR(20), -- 'trivial', 'simple', 'moderate', 'complex', 'epic'

    -- Effort estimation
    estimated_hours DECIMAL(6,2),
    actual_hours DECIMAL(6,2),
    effort_confidence DECIMAL(5,2) CHECK (effort_confidence >= 0 AND effort_confidence <= 100), -- AI confidence in estimate

    -- AI-driven scoring (0-100)
    business_value_score INTEGER CHECK (business_value_score >= 0 AND business_value_score <= 100),
    technical_debt_score INTEGER CHECK (technical_debt_score >= 0 AND technical_debt_score <= 100),
    user_impact_score INTEGER CHECK (user_impact_score >= 0 AND user_impact_score <= 100),
    risk_score INTEGER CHECK (risk_score >= 0 AND risk_score <= 100), -- Risk of NOT implementing
    implementation_risk_score INTEGER CHECK (implementation_risk_score >= 0 AND implementation_risk_score <= 100), -- Risk of implementing
    strategic_alignment_score INTEGER CHECK (strategic_alignment_score >= 0 AND strategic_alignment_score <= 100),

    -- Calculated priority score (weighted combination)
    ai_priority_score DECIMAL(7,2) CHECK (ai_priority_score >= 0 AND ai_priority_score <= 100),
    ai_priority_reasoning TEXT, -- LLM explanation of priority

    -- Status tracking
    status VARCHAR(30) DEFAULT 'proposed', -- 'proposed', 'approved', 'in_progress', 'blocked', 'completed', 'rejected', 'deferred'
    completion_percentage INTEGER DEFAULT 0 CHECK (completion_percentage >= 0 AND completion_percentage <= 100),

    -- Dependencies
    depends_on_enhancement_ids INTEGER[], -- Array of enhancement IDs this depends on
    blocks_enhancement_ids INTEGER[], -- Array of enhancement IDs blocked by this
    related_enhancement_ids INTEGER[], -- Related but not dependent

    -- Source tracking
    source VARCHAR(50), -- 'ai_research', 'user_feedback', 'health_check', 'manual', 'github', 'reddit', 'academic_paper'
    source_url TEXT,
    source_metadata JSONB, -- Full context from source

    -- Implementation tracking
    branch_name VARCHAR(200),
    pull_request_url TEXT,
    commit_hashes TEXT[], -- Array of git commit SHAs

    -- Outcome tracking
    deployed_at TIMESTAMP WITH TIME ZONE,
    rollback_at TIMESTAMP WITH TIME ZONE,
    success_metrics JSONB, -- Actual impact measured

    -- AI learning
    predicted_impact JSONB, -- What AI predicted would happen
    actual_impact JSONB, -- What actually happened
    prediction_accuracy_score DECIMAL(5,2), -- How accurate was AI prediction

    -- User feedback
    user_satisfaction_score DECIMAL(3,1), -- 1.0 to 5.0 stars
    user_feedback_count INTEGER DEFAULT 0,
    user_comments TEXT[],

    -- Tags for flexible categorization
    tags TEXT[],

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    approved_at TIMESTAMP WITH TIME ZONE,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,

    -- Audit
    created_by VARCHAR(100), -- 'ai_agent', 'user', 'admin'
    assigned_to VARCHAR(100),

    CONSTRAINT chk_category CHECK (category IN ('bug_fix', 'enhancement', 'new_feature', 'performance', 'security', 'refactoring', 'documentation', 'testing')),
    CONSTRAINT chk_priority CHECK (priority IN ('critical', 'high', 'medium', 'low')),
    CONSTRAINT chk_complexity CHECK (complexity IN ('trivial', 'simple', 'moderate', 'complex', 'epic', NULL)),
    CONSTRAINT chk_status CHECK (status IN ('proposed', 'approved', 'in_progress', 'blocked', 'completed', 'rejected', 'deferred', 'archived'))
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_ci_enhancements_status ON ci_enhancements(status);
CREATE INDEX IF NOT EXISTS idx_ci_enhancements_priority ON ci_enhancements(priority, ai_priority_score DESC);
CREATE INDEX IF NOT EXISTS idx_ci_enhancements_category ON ci_enhancements(category);
CREATE INDEX IF NOT EXISTS idx_ci_enhancements_feature_area ON ci_enhancements(feature_area);
CREATE INDEX IF NOT EXISTS idx_ci_enhancements_source ON ci_enhancements(source);
CREATE INDEX IF NOT EXISTS idx_ci_enhancements_created_at ON ci_enhancements(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_ci_enhancements_ai_score ON ci_enhancements(ai_priority_score DESC);
CREATE INDEX IF NOT EXISTS idx_ci_enhancements_tags ON ci_enhancements USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_ci_enhancements_source_metadata ON ci_enhancements USING GIN(source_metadata);

-- Full-text search
CREATE INDEX IF NOT EXISTS idx_ci_enhancements_search ON ci_enhancements USING GIN(
    to_tsvector('english', title || ' ' || description)
);

-- Comments
COMMENT ON TABLE ci_enhancements IS 'Master enhancement tracking table with AI-driven prioritization';
COMMENT ON COLUMN ci_enhancements.ai_priority_score IS 'Weighted score combining all dimensions for optimal prioritization';
COMMENT ON COLUMN ci_enhancements.source_metadata IS 'Complete context from research source (Reddit post, GitHub issue, paper abstract)';
COMMENT ON COLUMN ci_enhancements.predicted_impact IS 'AI prediction of metrics before implementation';
COMMENT ON COLUMN ci_enhancements.actual_impact IS 'Measured metrics after implementation for learning';

-- ============================================================================
-- Table: ci_research_findings
-- ============================================================================
-- Stores raw research findings from various sources before conversion to enhancements
-- ============================================================================

CREATE TABLE IF NOT EXISTS ci_research_findings (
    id SERIAL PRIMARY KEY,

    -- Source information
    source_type VARCHAR(50) NOT NULL, -- 'github', 'reddit', 'arxiv', 'hacker_news', 'medium', 'stackoverflow'
    source_url TEXT NOT NULL,
    source_title TEXT,
    source_author VARCHAR(200),
    source_date TIMESTAMP WITH TIME ZONE,

    -- Content
    content TEXT NOT NULL,
    content_summary TEXT, -- AI-generated summary
    keywords TEXT[], -- Extracted keywords

    -- Relevance scoring (0-100)
    relevance_score INTEGER CHECK (relevance_score >= 0 AND relevance_score <= 100),
    novelty_score INTEGER CHECK (novelty_score >= 0 AND novelty_score <= 100), -- How new/unique is this
    applicability_score INTEGER CHECK (applicability_score >= 0 AND applicability_score <= 100), -- How applicable to Magnus
    implementation_difficulty INTEGER CHECK (implementation_difficulty >= 0 AND implementation_difficulty <= 100),

    -- AI analysis
    ai_analysis TEXT, -- LLM interpretation and recommendations
    extracted_technologies JSONB, -- Technologies/libraries mentioned
    extracted_patterns JSONB, -- Design patterns identified

    -- Processing status
    status VARCHAR(30) DEFAULT 'new', -- 'new', 'analyzed', 'converted_to_enhancement', 'rejected', 'duplicate'
    rejection_reason TEXT,

    -- Deduplication
    content_hash VARCHAR(64) UNIQUE, -- SHA256 of normalized content
    similar_finding_ids INTEGER[], -- IDs of similar findings
    similarity_scores DECIMAL(5,2)[], -- Similarity scores for each

    -- Conversion tracking
    enhancement_id INTEGER REFERENCES ci_enhancements(id),

    -- Metadata
    sentiment_score DECIMAL(4,2), -- -1.0 (negative) to 1.0 (positive)
    upvotes INTEGER DEFAULT 0,
    downvotes INTEGER DEFAULT 0,
    comment_count INTEGER DEFAULT 0,
    view_count INTEGER DEFAULT 0,

    -- Search optimization
    search_vector TSVECTOR,

    -- Timestamps
    discovered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    analyzed_at TIMESTAMP WITH TIME ZONE,
    processed_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT chk_research_source_type CHECK (source_type IN (
        'github', 'reddit', 'arxiv', 'hacker_news', 'medium',
        'stackoverflow', 'twitter', 'discord', 'slack', 'blog', 'youtube'
    )),
    CONSTRAINT chk_research_status CHECK (status IN ('new', 'analyzed', 'converted_to_enhancement', 'rejected', 'duplicate', 'archived'))
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_research_findings_source ON ci_research_findings(source_type, source_date DESC);
CREATE INDEX IF NOT EXISTS idx_research_findings_relevance ON ci_research_findings(relevance_score DESC);
CREATE INDEX IF NOT EXISTS idx_research_findings_status ON ci_research_findings(status);
CREATE INDEX IF NOT EXISTS idx_research_findings_discovered ON ci_research_findings(discovered_at DESC);
CREATE INDEX IF NOT EXISTS idx_research_findings_search ON ci_research_findings USING GIN(search_vector);
CREATE INDEX IF NOT EXISTS idx_research_findings_keywords ON ci_research_findings USING GIN(keywords);

-- Comments
COMMENT ON TABLE ci_research_findings IS 'Raw research findings from automated discovery before enhancement creation';
COMMENT ON COLUMN ci_research_findings.content_hash IS 'Prevents duplicate discoveries from same content';

-- ============================================================================
-- Table: ci_research_sources
-- ============================================================================
-- Configuration and tracking for research sources
-- ============================================================================

CREATE TABLE IF NOT EXISTS ci_research_sources (
    id SERIAL PRIMARY KEY,

    -- Source configuration
    source_type VARCHAR(50) NOT NULL,
    source_name VARCHAR(200) NOT NULL,
    source_url TEXT NOT NULL,

    -- Search configuration
    search_queries TEXT[], -- List of queries to run
    search_filters JSONB, -- Source-specific filters (e.g., subreddit, date range)

    -- Scheduling
    enabled BOOLEAN DEFAULT TRUE,
    scan_frequency_hours INTEGER DEFAULT 24,
    last_scanned_at TIMESTAMP WITH TIME ZONE,
    next_scan_at TIMESTAMP WITH TIME ZONE,

    -- Performance metrics
    total_scans INTEGER DEFAULT 0,
    findings_discovered INTEGER DEFAULT 0,
    findings_converted INTEGER DEFAULT 0,
    avg_relevance_score DECIMAL(5,2),

    -- Rate limiting
    requests_per_minute INTEGER DEFAULT 10,
    requests_per_day INTEGER DEFAULT 1000,

    -- Authentication
    requires_auth BOOLEAN DEFAULT FALSE,
    auth_config_encrypted BYTEA, -- Encrypted credentials

    -- Quality metrics
    precision_score DECIMAL(5,2), -- How often findings are relevant
    recall_estimate DECIMAL(5,2), -- Estimated coverage

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    UNIQUE(source_type, source_name)
);

CREATE INDEX IF NOT EXISTS idx_research_sources_enabled ON ci_research_sources(enabled, next_scan_at);
CREATE INDEX IF NOT EXISTS idx_research_sources_performance ON ci_research_sources(findings_converted DESC);

COMMENT ON TABLE ci_research_sources IS 'Configuration for automated research discovery sources';

-- ============================================================================
-- PART 2: PLATFORM HEALTH MONITORING
-- ============================================================================

-- ============================================================================
-- Table: ci_health_checks
-- ============================================================================
-- Comprehensive platform health monitoring
-- ============================================================================

CREATE TABLE IF NOT EXISTS ci_health_checks (
    id SERIAL PRIMARY KEY,

    -- Check identification
    check_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    check_type VARCHAR(50) NOT NULL, -- 'full_scan', 'feature_specific', 'dependency_check', 'security_scan'

    -- Overall health scores (0-100)
    overall_health_score DECIMAL(5,2) CHECK (overall_health_score >= 0 AND overall_health_score <= 100),
    code_quality_score DECIMAL(5,2) CHECK (code_quality_score >= 0 AND code_quality_score <= 100),
    test_coverage_score DECIMAL(5,2) CHECK (test_coverage_score >= 0 AND test_coverage_score <= 100),
    security_score DECIMAL(5,2) CHECK (security_score >= 0 AND security_score <= 100),
    performance_score DECIMAL(5,2) CHECK (performance_score >= 0 AND performance_score <= 100),
    documentation_score DECIMAL(5,2) CHECK (documentation_score >= 0 AND documentation_score <= 100),
    dependency_health_score DECIMAL(5,2) CHECK (dependency_health_score >= 0 AND dependency_health_score <= 100),

    -- Detailed metrics
    total_files INTEGER,
    total_lines_of_code INTEGER,
    total_functions INTEGER,
    total_classes INTEGER,
    total_tests INTEGER,

    -- Test metrics
    tests_passed INTEGER,
    tests_failed INTEGER,
    test_coverage_percentage DECIMAL(5,2),

    -- Code quality metrics
    complexity_issues INTEGER,
    style_violations INTEGER,
    code_smells INTEGER,
    duplicate_code_percentage DECIMAL(5,2),

    -- Security metrics
    critical_vulnerabilities INTEGER DEFAULT 0,
    high_vulnerabilities INTEGER DEFAULT 0,
    medium_vulnerabilities INTEGER DEFAULT 0,
    low_vulnerabilities INTEGER DEFAULT 0,

    -- Performance metrics
    avg_page_load_time_ms INTEGER,
    slow_queries_count INTEGER,
    memory_usage_mb DECIMAL(10,2),
    cpu_usage_percentage DECIMAL(5,2),

    -- Dependencies
    outdated_dependencies INTEGER,
    vulnerable_dependencies INTEGER,
    total_dependencies INTEGER,

    -- Feature health
    total_features INTEGER,
    healthy_features INTEGER,
    degraded_features INTEGER,
    broken_features INTEGER,

    -- Issues detected
    critical_issues INTEGER DEFAULT 0,
    high_priority_issues INTEGER DEFAULT 0,
    medium_priority_issues INTEGER DEFAULT 0,
    low_priority_issues INTEGER DEFAULT 0,

    -- AI recommendations
    recommendations_generated INTEGER DEFAULT 0,
    auto_fixable_issues INTEGER DEFAULT 0,

    -- Comparison to previous check
    health_score_change DECIMAL(6,2), -- Change from last check
    new_issues INTEGER DEFAULT 0,
    resolved_issues INTEGER DEFAULT 0,

    -- Raw results
    detailed_results JSONB, -- Complete scan results

    -- Execution info
    scan_duration_seconds INTEGER,
    scanner_version VARCHAR(20),

    CONSTRAINT chk_health_check_type CHECK (check_type IN ('full_scan', 'feature_specific', 'dependency_check', 'security_scan', 'performance_test'))
);

CREATE INDEX IF NOT EXISTS idx_health_checks_timestamp ON ci_health_checks(check_timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_health_checks_score ON ci_health_checks(overall_health_score DESC);
CREATE INDEX IF NOT EXISTS idx_health_checks_type ON ci_health_checks(check_type);

COMMENT ON TABLE ci_health_checks IS 'Comprehensive platform health monitoring and trend tracking';

-- ============================================================================
-- Table: ci_health_issues
-- ============================================================================
-- Specific issues identified during health checks
-- ============================================================================

CREATE TABLE IF NOT EXISTS ci_health_issues (
    id SERIAL PRIMARY KEY,
    health_check_id INTEGER REFERENCES ci_health_checks(id) ON DELETE CASCADE,

    -- Issue details
    issue_type VARCHAR(50) NOT NULL, -- 'security', 'performance', 'code_quality', 'dependency', 'test_failure'
    severity VARCHAR(20) NOT NULL, -- 'critical', 'high', 'medium', 'low', 'info'

    title VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,

    -- Location
    file_path TEXT,
    line_number INTEGER,
    function_name VARCHAR(200),

    -- Fix information
    auto_fixable BOOLEAN DEFAULT FALSE,
    fix_script TEXT, -- Automated fix if available
    fix_effort_estimate VARCHAR(20), -- 'minutes', 'hours', 'days'

    -- Related enhancement
    enhancement_id INTEGER REFERENCES ci_enhancements(id),
    auto_created_enhancement BOOLEAN DEFAULT FALSE,

    -- Status
    status VARCHAR(30) DEFAULT 'open', -- 'open', 'acknowledged', 'fixing', 'fixed', 'wont_fix', 'false_positive'

    -- Tracking
    first_detected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_seen_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    fixed_at TIMESTAMP WITH TIME ZONE,
    occurrence_count INTEGER DEFAULT 1,

    -- Additional context
    stack_trace TEXT,
    related_issue_ids INTEGER[],
    tags TEXT[],

    CONSTRAINT chk_issue_type CHECK (issue_type IN ('security', 'performance', 'code_quality', 'dependency', 'test_failure', 'configuration', 'database')),
    CONSTRAINT chk_issue_severity CHECK (severity IN ('critical', 'high', 'medium', 'low', 'info')),
    CONSTRAINT chk_issue_status CHECK (status IN ('open', 'acknowledged', 'fixing', 'fixed', 'wont_fix', 'false_positive', 'duplicate'))
);

CREATE INDEX IF NOT EXISTS idx_health_issues_check ON ci_health_issues(health_check_id);
CREATE INDEX IF NOT EXISTS idx_health_issues_severity ON ci_health_issues(severity, status);
CREATE INDEX IF NOT EXISTS idx_health_issues_type ON ci_health_issues(issue_type);
CREATE INDEX IF NOT EXISTS idx_health_issues_status ON ci_health_issues(status);
CREATE INDEX IF NOT EXISTS idx_health_issues_auto_fix ON ci_health_issues(auto_fixable, status);

COMMENT ON TABLE ci_health_issues IS 'Specific issues identified during health monitoring';

-- ============================================================================
-- PART 3: CONTINUOUS LEARNING & PERFORMANCE TRACKING
-- ============================================================================

-- ============================================================================
-- Table: ci_agent_performance
-- ============================================================================
-- Tracks AI agent performance for continuous improvement
-- ============================================================================

CREATE TABLE IF NOT EXISTS ci_agent_performance (
    id SERIAL PRIMARY KEY,

    -- Agent identification
    agent_name VARCHAR(100) NOT NULL, -- 'research_agent', 'enhancement_agent', 'prioritization_agent'
    agent_version VARCHAR(20),

    -- Time period
    date DATE NOT NULL,
    hour INTEGER CHECK (hour >= 0 AND hour <= 23),

    -- Activity metrics
    tasks_executed INTEGER DEFAULT 0,
    tasks_successful INTEGER DEFAULT 0,
    tasks_failed INTEGER DEFAULT 0,

    -- Quality metrics
    avg_confidence_score DECIMAL(5,2),
    avg_accuracy_score DECIMAL(5,2), -- Measured against outcomes

    -- Performance metrics
    avg_execution_time_ms INTEGER,
    total_api_calls INTEGER DEFAULT 0,
    total_api_cost_usd DECIMAL(10,4),

    -- Learning metrics
    predictions_made INTEGER DEFAULT 0,
    predictions_correct INTEGER DEFAULT 0,
    predictions_incorrect INTEGER DEFAULT 0,
    prediction_accuracy DECIMAL(5,2),

    -- Model information
    model_name VARCHAR(100),
    model_temperature DECIMAL(3,2),
    model_parameters JSONB,

    -- Feedback
    positive_feedback INTEGER DEFAULT 0,
    negative_feedback INTEGER DEFAULT 0,

    -- Resource usage
    memory_used_mb DECIMAL(10,2),
    cpu_time_seconds DECIMAL(10,2),

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    UNIQUE(agent_name, date, hour)
);

CREATE INDEX IF NOT EXISTS idx_agent_performance_agent ON ci_agent_performance(agent_name, date DESC);
CREATE INDEX IF NOT EXISTS idx_agent_performance_accuracy ON ci_agent_performance(prediction_accuracy DESC);

COMMENT ON TABLE ci_agent_performance IS 'AI agent performance tracking for continuous learning';

-- ============================================================================
-- Table: ci_learning_samples
-- ============================================================================
-- Training data for agent improvement
-- ============================================================================

CREATE TABLE IF NOT EXISTS ci_learning_samples (
    id SERIAL PRIMARY KEY,

    -- Sample identification
    agent_name VARCHAR(100) NOT NULL,
    sample_type VARCHAR(50), -- 'prioritization', 'research_relevance', 'fix_suggestion'

    -- Input/Output
    input_data JSONB NOT NULL,
    expected_output JSONB,
    actual_output JSONB,

    -- Quality
    correctness_score DECIMAL(5,2), -- 0-100
    user_feedback VARCHAR(20), -- 'excellent', 'good', 'acceptable', 'poor', 'wrong'

    -- Context
    context_data JSONB, -- Additional context for learning

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    reviewed_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT chk_feedback CHECK (user_feedback IN ('excellent', 'good', 'acceptable', 'poor', 'wrong', NULL))
);

CREATE INDEX IF NOT EXISTS idx_learning_samples_agent ON ci_learning_samples(agent_name, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_learning_samples_feedback ON ci_learning_samples(user_feedback);

COMMENT ON TABLE ci_learning_samples IS 'Training samples for agent improvement and fine-tuning';

-- ============================================================================
-- Table: ci_performance_metrics
-- ============================================================================
-- Platform-wide performance metrics over time
-- ============================================================================

CREATE TABLE IF NOT EXISTS ci_performance_metrics (
    id SERIAL PRIMARY KEY,

    -- Time bucket
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    aggregation_level VARCHAR(20), -- 'minute', 'hour', 'day', 'week'

    -- User engagement
    active_users INTEGER DEFAULT 0,
    page_views INTEGER DEFAULT 0,
    feature_usage JSONB, -- Usage count per feature

    -- System performance
    avg_response_time_ms DECIMAL(10,2),
    p95_response_time_ms INTEGER,
    p99_response_time_ms INTEGER,
    error_rate DECIMAL(5,4),

    -- Trading metrics
    total_trades_analyzed INTEGER DEFAULT 0,
    ai_recommendations_generated INTEGER DEFAULT 0,
    recommendations_followed INTEGER DEFAULT 0,
    recommendation_success_rate DECIMAL(5,2),

    -- Financial performance (if applicable)
    total_pnl DECIMAL(15,2),
    winning_trades INTEGER DEFAULT 0,
    losing_trades INTEGER DEFAULT 0,

    -- Feature health
    features_online INTEGER,
    features_degraded INTEGER,
    features_offline INTEGER,

    -- Resource utilization
    database_size_mb BIGINT,
    cache_hit_rate DECIMAL(5,2),
    api_quota_used_percentage DECIMAL(5,2),

    CONSTRAINT chk_aggregation_level CHECK (aggregation_level IN ('minute', 'hour', 'day', 'week', 'month'))
);

CREATE INDEX IF NOT EXISTS idx_performance_metrics_time ON ci_performance_metrics(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_level ON ci_performance_metrics(aggregation_level, timestamp DESC);

COMMENT ON TABLE ci_performance_metrics IS 'Platform-wide performance metrics for trend analysis';

-- ============================================================================
-- Table: ci_strategy_performance
-- ============================================================================
-- Tracks performance of AI trading strategies over time
-- ============================================================================

CREATE TABLE IF NOT EXISTS ci_strategy_performance (
    id SERIAL PRIMARY KEY,

    -- Strategy identification
    strategy_name VARCHAR(100) NOT NULL,
    strategy_version VARCHAR(20),
    strategy_parameters JSONB,

    -- Time period
    period_start TIMESTAMP WITH TIME ZONE NOT NULL,
    period_end TIMESTAMP WITH TIME ZONE NOT NULL,

    -- Performance metrics
    total_signals INTEGER DEFAULT 0,
    signals_taken INTEGER DEFAULT 0,
    winning_signals INTEGER DEFAULT 0,
    losing_signals INTEGER DEFAULT 0,

    win_rate DECIMAL(5,2),
    avg_return DECIMAL(8,4),
    total_return DECIMAL(10,2),
    max_drawdown DECIMAL(8,4),
    sharpe_ratio DECIMAL(6,3),
    sortino_ratio DECIMAL(6,3),

    -- Risk metrics
    avg_risk_per_trade DECIMAL(8,4),
    max_risk_taken DECIMAL(8,4),
    risk_adjusted_return DECIMAL(8,4),

    -- Adaptive learning
    parameter_adjustments JSONB, -- History of parameter changes
    performance_trend VARCHAR(20), -- 'improving', 'stable', 'degrading'

    -- Confidence
    strategy_confidence DECIMAL(5,2), -- AI confidence in strategy

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT chk_performance_trend CHECK (performance_trend IN ('improving', 'stable', 'degrading', 'unknown'))
);

CREATE INDEX IF NOT EXISTS idx_strategy_performance_name ON ci_strategy_performance(strategy_name, period_end DESC);
CREATE INDEX IF NOT EXISTS idx_strategy_performance_winrate ON ci_strategy_performance(win_rate DESC);

COMMENT ON TABLE ci_strategy_performance IS 'Trading strategy performance for adaptive parameter optimization';

-- ============================================================================
-- PART 4: AUTOMATION & WORKFLOW
-- ============================================================================

-- ============================================================================
-- Table: ci_automation_runs
-- ============================================================================
-- Tracks automated improvement runs
-- ============================================================================

CREATE TABLE IF NOT EXISTS ci_automation_runs (
    id SERIAL PRIMARY KEY,

    -- Run identification
    run_type VARCHAR(50) NOT NULL, -- 'health_check', 'research', 'auto_fix', 'optimization'
    run_trigger VARCHAR(50), -- 'scheduled', 'manual', 'event_driven', 'api_call'

    -- Execution
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_seconds INTEGER,

    status VARCHAR(30), -- 'running', 'completed', 'failed', 'cancelled'

    -- Results
    items_processed INTEGER DEFAULT 0,
    items_successful INTEGER DEFAULT 0,
    items_failed INTEGER DEFAULT 0,

    enhancements_created INTEGER DEFAULT 0,
    issues_detected INTEGER DEFAULT 0,
    fixes_applied INTEGER DEFAULT 0,

    -- Output
    results_summary TEXT,
    detailed_results JSONB,

    -- Errors
    error_count INTEGER DEFAULT 0,
    error_messages TEXT[],

    -- Resource usage
    peak_memory_mb DECIMAL(10,2),
    cpu_seconds DECIMAL(10,2),
    api_calls_made INTEGER DEFAULT 0,
    api_cost_usd DECIMAL(10,4),

    CONSTRAINT chk_automation_run_type CHECK (run_type IN ('health_check', 'research', 'auto_fix', 'optimization', 'backup', 'cleanup')),
    CONSTRAINT chk_automation_trigger CHECK (run_trigger IN ('scheduled', 'manual', 'event_driven', 'api_call', 'webhook')),
    CONSTRAINT chk_automation_status CHECK (status IN ('running', 'completed', 'failed', 'cancelled', 'timeout'))
);

CREATE INDEX IF NOT EXISTS idx_automation_runs_type ON ci_automation_runs(run_type, started_at DESC);
CREATE INDEX IF NOT EXISTS idx_automation_runs_status ON ci_automation_runs(status);

COMMENT ON TABLE ci_automation_runs IS 'Tracks automated improvement and maintenance runs';

-- ============================================================================
-- Table: ci_feedback
-- ============================================================================
-- User feedback on enhancements and AI recommendations
-- ============================================================================

CREATE TABLE IF NOT EXISTS ci_feedback (
    id SERIAL PRIMARY KEY,

    -- Feedback target
    feedback_type VARCHAR(50), -- 'enhancement', 'research_finding', 'health_issue', 'ai_recommendation'
    target_id INTEGER NOT NULL, -- ID of the target item

    -- Feedback content
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    feedback_text TEXT,

    -- Categorization
    feedback_category VARCHAR(50), -- 'accuracy', 'usefulness', 'completeness', 'performance'
    sentiment VARCHAR(20), -- 'positive', 'neutral', 'negative'

    -- User information
    user_id VARCHAR(100),
    user_role VARCHAR(50), -- 'developer', 'trader', 'admin'

    -- Context
    context_data JSONB,

    -- Processing
    processed BOOLEAN DEFAULT FALSE,
    incorporated_into_learning BOOLEAN DEFAULT FALSE,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT chk_feedback_type CHECK (feedback_type IN ('enhancement', 'research_finding', 'health_issue', 'ai_recommendation', 'general')),
    CONSTRAINT chk_feedback_sentiment CHECK (sentiment IN ('positive', 'neutral', 'negative', NULL))
);

CREATE INDEX IF NOT EXISTS idx_feedback_type_target ON ci_feedback(feedback_type, target_id);
CREATE INDEX IF NOT EXISTS idx_feedback_rating ON ci_feedback(rating, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_feedback_processed ON ci_feedback(processed, incorporated_into_learning);

COMMENT ON TABLE ci_feedback IS 'User feedback for continuous improvement of AI agents';

-- ============================================================================
-- PART 5: VIEWS FOR EASY QUERYING
-- ============================================================================

-- View: Top Priority Enhancements
CREATE OR REPLACE VIEW v_ci_top_priorities AS
SELECT
    id,
    title,
    category,
    priority,
    status,
    ai_priority_score,
    business_value_score,
    user_impact_score,
    estimated_hours,
    feature_area,
    created_at,
    ai_priority_reasoning
FROM ci_enhancements
WHERE status IN ('proposed', 'approved')
    AND ai_priority_score IS NOT NULL
ORDER BY ai_priority_score DESC, priority, created_at
LIMIT 50;

COMMENT ON VIEW v_ci_top_priorities IS 'Top 50 prioritized enhancements ready for implementation';

-- View: Research Pipeline
CREATE OR REPLACE VIEW v_ci_research_pipeline AS
SELECT
    rf.id,
    rf.source_type,
    rf.source_title,
    rf.relevance_score,
    rf.applicability_score,
    rf.status,
    rf.discovered_at,
    rf.enhancement_id,
    e.title as enhancement_title,
    e.status as enhancement_status
FROM ci_research_findings rf
LEFT JOIN ci_enhancements e ON rf.enhancement_id = e.id
WHERE rf.status IN ('new', 'analyzed')
ORDER BY rf.relevance_score DESC, rf.discovered_at DESC;

COMMENT ON VIEW v_ci_research_pipeline IS 'Research findings in the processing pipeline';

-- View: Health Trends
CREATE OR REPLACE VIEW v_ci_health_trends AS
SELECT
    DATE(check_timestamp) as check_date,
    AVG(overall_health_score) as avg_health_score,
    AVG(code_quality_score) as avg_code_quality,
    AVG(security_score) as avg_security,
    AVG(performance_score) as avg_performance,
    SUM(critical_issues) as total_critical_issues,
    SUM(high_priority_issues) as total_high_issues
FROM ci_health_checks
WHERE check_timestamp >= NOW() - INTERVAL '30 days'
GROUP BY DATE(check_timestamp)
ORDER BY check_date DESC;

COMMENT ON VIEW v_ci_health_trends IS '30-day health score trends';

-- View: Agent Performance Summary
CREATE OR REPLACE VIEW v_ci_agent_summary AS
SELECT
    agent_name,
    DATE(date) as period,
    SUM(tasks_executed) as total_tasks,
    AVG(prediction_accuracy) as avg_accuracy,
    SUM(total_api_cost_usd) as total_cost,
    AVG(avg_execution_time_ms) as avg_time_ms
FROM ci_agent_performance
WHERE date >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY agent_name, DATE(date)
ORDER BY agent_name, period DESC;

COMMENT ON VIEW v_ci_agent_summary IS '7-day agent performance summary';

-- View: Critical Issues
CREATE OR REPLACE VIEW v_ci_critical_issues AS
SELECT
    hi.id,
    hi.issue_type,
    hi.title,
    hi.severity,
    hi.file_path,
    hi.auto_fixable,
    hi.status,
    hi.first_detected_at,
    hi.occurrence_count,
    hc.check_timestamp,
    e.id as enhancement_id,
    e.title as enhancement_title
FROM ci_health_issues hi
JOIN ci_health_checks hc ON hi.health_check_id = hc.id
LEFT JOIN ci_enhancements e ON hi.enhancement_id = e.id
WHERE hi.severity IN ('critical', 'high')
    AND hi.status IN ('open', 'acknowledged')
ORDER BY hi.severity, hi.occurrence_count DESC, hi.first_detected_at;

COMMENT ON VIEW v_ci_critical_issues IS 'All critical and high severity open issues';

-- ============================================================================
-- PART 6: TRIGGERS AND FUNCTIONS
-- ============================================================================

-- Update updated_at timestamp trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
CREATE TRIGGER update_ci_enhancements_updated_at
    BEFORE UPDATE ON ci_enhancements
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ci_research_sources_updated_at
    BEFORE UPDATE ON ci_research_sources
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Function to calculate AI priority score
CREATE OR REPLACE FUNCTION calculate_ai_priority_score(
    p_business_value INTEGER,
    p_technical_debt INTEGER,
    p_user_impact INTEGER,
    p_risk INTEGER,
    p_implementation_risk INTEGER,
    p_strategic_alignment INTEGER
) RETURNS DECIMAL(7,2) AS $$
BEGIN
    -- Weighted formula (customize weights based on organizational priorities)
    RETURN (
        COALESCE(p_business_value, 0) * 0.25 +
        COALESCE(p_user_impact, 0) * 0.25 +
        COALESCE(p_strategic_alignment, 0) * 0.20 +
        COALESCE(p_technical_debt, 0) * 0.15 +
        COALESCE(p_risk, 0) * 0.10 -
        COALESCE(p_implementation_risk, 0) * 0.05
    );
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Function to update search vectors
CREATE OR REPLACE FUNCTION update_research_search_vector()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector := to_tsvector('english',
        COALESCE(NEW.source_title, '') || ' ' ||
        COALESCE(NEW.content, '') || ' ' ||
        COALESCE(NEW.content_summary, '')
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_research_search_vector_trigger
    BEFORE INSERT OR UPDATE ON ci_research_findings
    FOR EACH ROW
    EXECUTE FUNCTION update_research_search_vector();

-- ============================================================================
-- PART 7: INITIAL CONFIGURATION DATA
-- ============================================================================

-- Insert default research sources
INSERT INTO ci_research_sources (source_type, source_name, source_url, search_queries, scan_frequency_hours) VALUES
('reddit', 'r/options', 'https://www.reddit.com/r/options', ARRAY['trading platform', 'options scanner', 'portfolio tracker', 'automated trading'], 12),
('reddit', 'r/algotrading', 'https://www.reddit.com/r/algotrading', ARRAY['algorithmic trading', 'backtesting', 'trading bot', 'market data'], 12),
('reddit', 'r/Python', 'https://www.reddit.com/r/Python', ARRAY['python trading', 'data analysis', 'web scraping', 'API integration'], 24),
('github', 'Trading Platforms', 'https://github.com/topics/trading-platform', ARRAY['options trading', 'stock analysis', 'portfolio management'], 24),
('github', 'Python Finance', 'https://github.com/topics/finance', ARRAY['financial analysis', 'market data', 'technical indicators'], 24),
('arxiv', 'Quantitative Finance', 'https://arxiv.org/list/q-fin/recent', ARRAY['options pricing', 'risk management', 'portfolio optimization'], 168),
('hacker_news', 'HN', 'https://news.ycombinator.com', ARRAY['trading platform', 'fintech', 'market analysis'], 12)
ON CONFLICT (source_type, source_name) DO NOTHING;

-- ============================================================================
-- SUCCESS MESSAGE
-- ============================================================================

SELECT 'AI-Native Continuous Improvement System schema created successfully!' as status,
       'Database ready for world-class autonomous platform evolution' as message;
