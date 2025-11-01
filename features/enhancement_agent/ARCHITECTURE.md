# Enhancement Agent - Architecture

## System Architecture

### Overview

The Enhancement Agent is a meta-monitoring system that operates as a continuous improvement engine for the Magnus platform. It employs a sophisticated multi-agent architecture using LangChain and CrewAI to analyze, evaluate, and recommend improvements across all 13+ features of the platform.

```
┌─────────────────────────────────────────────────────────────┐
│                     Enhancement Agent                        │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Scanner    │  │   Analyzer   │  │  Recommender │     │
│  │    Agent     │→ │    Agent     │→ │    Agent     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│         ↓                  ↓                  ↓             │
│  ┌──────────────────────────────────────────────────┐     │
│  │           Feature Health Database                 │     │
│  └──────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            ↓
     ┌──────────────────────────────────────────┐
     │         All Magnus Features               │
     │  (Dashboard, Positions, AI Research...)   │
     └──────────────────────────────────────────┘
```

### Core Components

1. **Scanner Agent** (`src/agents/enhancement_agent/scanner.py`)
   - Responsibility: Daily filesystem scanning and data collection
   - Key functions:
     - `scan_all_features()`: Traverses features/ directory
     - `parse_documentation()`: Extracts metadata from .md files
     - `analyze_code_quality()`: Runs static analysis
     - `check_dependencies()`: Verifies package versions

2. **Analyzer Agent** (`src/agents/enhancement_agent/analyzer.py`)
   - Responsibility: Deep analysis of collected data
   - Key functions:
     - `calculate_health_score()`: Generates 0-100% scores
     - `detect_patterns()`: Identifies anti-patterns and tech debt
     - `measure_complexity()`: Cyclomatic complexity analysis
     - `track_usage()`: Analyzes Streamlit session data

3. **Recommender Agent** (`src/agents/enhancement_agent/recommender.py`)
   - Responsibility: AI-powered improvement suggestions
   - Key functions:
     - `generate_recommendations()`: Creates prioritized suggestions
     - `estimate_effort()`: Time/resource estimation
     - `suggest_frameworks()`: Modern framework alternatives
     - `create_implementation_plan()`: Step-by-step guides

4. **Coordinator** (`src/agents/enhancement_agent/coordinator.py`)
   - Responsibility: Orchestrates all agents and manages workflow
   - Key functions:
     - `run_daily_scan()`: Main entry point
     - `aggregate_results()`: Combines agent outputs
     - `generate_report()`: Creates dashboard data
     - `notify_stakeholders()`: Sends alerts/digests

5. **Dashboard Interface** (`enhancement_agent_page.py`)
   - Responsibility: Streamlit UI for viewing results
   - Key functions:
     - `display_health_dashboard()`: Visual health metrics
     - `show_recommendations()`: Interactive recommendation cards
     - `render_todo_aggregator()`: Consolidated TODO view
     - `handle_actions()`: Process user decisions

## Data Flow

```
1. Cron Trigger (2:00 AM daily)
         ↓
2. Coordinator.run_daily_scan()
         ↓
3. Scanner Agent
   - Read all features/ folders
   - Parse .md files (TODO, AGENT, CHANGELOG)
   - Analyze Python files
   - Check package.json, requirements.txt
         ↓
4. Data Collection → feature_health table
         ↓
5. Analyzer Agent
   - Calculate metrics
   - Identify patterns
   - Score features
         ↓
6. Analysis Results → feature_analysis table
         ↓
7. Recommender Agent
   - Generate suggestions
   - Prioritize by impact
   - Create action plans
         ↓
8. Recommendations → feature_recommendations table
         ↓
9. Dashboard Update
   - Aggregate data
   - Calculate trends
   - Prepare visualizations
         ↓
10. User Review → Action/Defer/Dismiss
```

## Key Algorithms

### Feature Health Score Algorithm
```python
def calculate_health_score(feature_data):
    """
    Calculates 0-100% health score for a feature.

    Weights:
    - Code Quality: 25%
    - Test Coverage: 20%
    - Documentation: 15%
    - Performance: 15%
    - Dependencies: 10%
    - TODO Count: 10%
    - Last Update: 5%
    """
    scores = {
        'code_quality': analyze_code_quality(feature_data) * 0.25,
        'test_coverage': get_test_coverage(feature_data) * 0.20,
        'documentation': check_documentation(feature_data) * 0.15,
        'performance': measure_performance(feature_data) * 0.15,
        'dependencies': check_dependencies(feature_data) * 0.10,
        'todo_debt': calculate_todo_score(feature_data) * 0.10,
        'freshness': calculate_freshness(feature_data) * 0.05
    }

    return sum(scores.values())
```

### Recommendation Priority Algorithm
```python
def prioritize_recommendations(recommendations):
    """
    Scores recommendations based on impact and effort.

    Priority = (Impact * 0.7) - (Effort * 0.3)

    Where:
    - Impact: 0-10 (user value, performance gain, debt reduction)
    - Effort: 0-10 (time, complexity, risk)
    """
    for rec in recommendations:
        impact = calculate_impact(rec)
        effort = estimate_effort(rec)
        rec['priority_score'] = (impact * 0.7) - (effort * 0.3)

    return sorted(recommendations, key=lambda x: x['priority_score'], reverse=True)
```

### Pattern Detection Algorithm
```python
def detect_anti_patterns(code_ast):
    """
    Uses AST analysis to find common anti-patterns.

    Patterns detected:
    - God classes (>500 lines)
    - Long methods (>50 lines)
    - Duplicate code blocks
    - Missing error handling
    - Hardcoded values
    - Circular dependencies
    """
    patterns = []

    # Check class sizes
    for class_node in ast.walk(code_ast):
        if isinstance(class_node, ast.ClassDef):
            if count_lines(class_node) > 500:
                patterns.append({
                    'type': 'god_class',
                    'location': class_node.name,
                    'severity': 'high'
                })

    return patterns
```

## Dependencies

### External APIs
- **GitHub API**: For checking latest framework versions
  - Rate limit: 60 requests/hour (unauthenticated)
  - Authentication: Optional GitHub token for 5000 req/hour

- **PyPI API**: For Python package version checking
  - Rate limit: None
  - Endpoint: https://pypi.org/pypi/{package}/json

- **npm Registry API**: For JavaScript package versions
  - Rate limit: None
  - Endpoint: https://registry.npmjs.org/{package}

### Database Tables

1. **feature_health**
```sql
CREATE TABLE feature_health (
    id SERIAL PRIMARY KEY,
    feature_name VARCHAR(100) NOT NULL,
    scan_timestamp TIMESTAMP NOT NULL,
    health_score INTEGER CHECK (health_score >= 0 AND health_score <= 100),
    code_quality_score INTEGER,
    test_coverage_percentage INTEGER,
    documentation_score INTEGER,
    performance_score INTEGER,
    dependency_score INTEGER,
    todo_count INTEGER,
    bug_count INTEGER,
    last_commit_date DATE,
    file_count INTEGER,
    total_lines_of_code INTEGER,
    UNIQUE(feature_name, scan_timestamp)
);

CREATE INDEX idx_feature_health_timestamp ON feature_health(scan_timestamp);
CREATE INDEX idx_feature_health_name ON feature_health(feature_name);
```

2. **feature_analysis**
```sql
CREATE TABLE feature_analysis (
    id SERIAL PRIMARY KEY,
    feature_name VARCHAR(100) NOT NULL,
    analysis_date DATE NOT NULL,
    anti_patterns JSONB,
    complexity_metrics JSONB,
    dependency_graph JSONB,
    usage_statistics JSONB,
    performance_metrics JSONB,
    security_issues JSONB,
    FOREIGN KEY (feature_name) REFERENCES feature_health(feature_name)
);
```

3. **feature_recommendations**
```sql
CREATE TABLE feature_recommendations (
    id SERIAL PRIMARY KEY,
    feature_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    title VARCHAR(500) NOT NULL,
    description TEXT,
    category VARCHAR(50), -- 'framework', 'performance', 'refactor', 'feature', 'bugfix'
    priority VARCHAR(20), -- 'critical', 'high', 'medium', 'low'
    impact_score INTEGER CHECK (impact_score >= 1 AND impact_score <= 10),
    effort_hours INTEGER,
    implementation_guide TEXT,
    frameworks_suggested JSONB,
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'accepted', 'deferred', 'dismissed', 'completed'
    status_changed_at TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE INDEX idx_recommendations_status ON feature_recommendations(status);
CREATE INDEX idx_recommendations_priority ON feature_recommendations(priority);
```

4. **feature_todos**
```sql
CREATE TABLE feature_todos (
    id SERIAL PRIMARY KEY,
    feature_name VARCHAR(100) NOT NULL,
    todo_text TEXT NOT NULL,
    priority VARCHAR(20),
    category VARCHAR(50),
    file_path VARCHAR(500),
    line_number INTEGER,
    created_date DATE,
    completed BOOLEAN DEFAULT FALSE,
    completed_date DATE,
    extracted_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_todos_feature ON feature_todos(feature_name);
CREATE INDEX idx_todos_completed ON feature_todos(completed);
```

### Other Features
- **Dashboard Feature**: Provides navigation integration
- **Database Scan Feature**: Shares database connection pool
- **AI Research Feature**: Uses same LangChain/CrewAI setup

## Performance Considerations

### Caching Strategy
- **Scan Results Cache**: 24-hour TTL for feature health data
  - Key: `enhancement:health:{feature_name}:{date}`
  - Invalidation: On manual rescan or feature update

- **Recommendation Cache**: 7-day TTL for generated recommendations
  - Key: `enhancement:recommendations:{feature_name}:{week_number}`
  - Invalidation: When recommendation status changes

- **Dependency Check Cache**: 12-hour TTL for package versions
  - Key: `enhancement:deps:{package_name}`
  - Invalidation: Manual refresh or scheduled update

### Query Optimization
- **Batch Processing**: Scan all features in parallel using asyncio
- **Incremental Updates**: Only scan changed files (git diff based)
- **Indexed Queries**: All frequent queries use indexed columns
- **Connection Pooling**: Reuse database connections (pool size: 20)

### Rate Limiting
- **GitHub API**: Max 50 requests per scan cycle
- **AI Model Calls**: Batch recommendations, max 10 per minute
- **Dashboard Refresh**: Update every 5 minutes minimum
- **Manual Scans**: Limited to 1 per hour per user

## Error Handling

### File System Errors
```python
try:
    scan_results = scanner.scan_feature(feature_path)
except FileNotFoundError:
    log.warning(f"Feature directory not found: {feature_path}")
    mark_feature_inactive(feature_name)
except PermissionError:
    log.error(f"Permission denied accessing: {feature_path}")
    use_cached_results(feature_name)
```

### API Failures
```python
try:
    latest_version = check_pypi_version(package_name)
except requests.RequestException as e:
    log.warning(f"PyPI API failed: {e}")
    # Use cached version or skip version check
    latest_version = get_cached_version(package_name)
```

### AI Model Errors
```python
try:
    recommendations = ai_model.generate_recommendations(analysis)
except OpenAIError as e:
    log.error(f"AI model error: {e}")
    # Fall back to rule-based recommendations
    recommendations = generate_rule_based_recommendations(analysis)
```

## Security Considerations

### Authentication
- **Dashboard Access**: Requires Streamlit authentication
- **API Keys**: Stored in environment variables
  - `OPENAI_API_KEY`: For LangChain AI models
  - `GITHUB_TOKEN`: Optional, for higher rate limits

### Data Validation
- **Path Traversal Protection**: Validate all file paths
- **Input Sanitization**: Clean all user inputs before database storage
- **SQL Injection Prevention**: Use parameterized queries only

### API Key Management
- **Rotation**: Monthly key rotation recommended
- **Scoping**: Minimal permissions (read-only where possible)
- **Encryption**: Keys encrypted at rest in .env file

## Integration Architecture

### With Main Agent
```python
# Main Agent queries Enhancement Agent
request = {
    "action": "get_feature_health",
    "feature": "positions"
}

response = enhancement_agent.handle_request(request)
# Returns: {"health_score": 85, "top_issues": [...], "recommendations": [...]}
```

### With Feature Agents
```python
# Feature agents can request their own analysis
request = {
    "action": "analyze_my_feature",
    "feature_name": "calendar_spreads",
    "include_recommendations": True
}

analysis = enhancement_agent.analyze_feature(request)
```

### Webhook Integration
```python
# GitHub webhook for immediate analysis on push
@app.route('/webhook/github/push', methods=['POST'])
def handle_github_push():
    payload = request.json
    changed_files = extract_changed_files(payload)
    affected_features = determine_affected_features(changed_files)

    for feature in affected_features:
        enhancement_agent.scan_feature(feature, incremental=True)
```

## Monitoring & Observability

### Metrics Tracked
- **Scan Duration**: Time to complete full scan
- **Recommendation Acceptance Rate**: % of recommendations implemented
- **Feature Health Trends**: Daily health score changes
- **Error Rates**: Failures per component
- **Cache Hit Rates**: Efficiency of caching layer

### Logging
```python
# Structured logging with context
logger.info("Scan completed", extra={
    "feature": feature_name,
    "duration_seconds": scan_duration,
    "issues_found": len(issues),
    "recommendations_generated": len(recommendations),
    "health_score": health_score
})
```

### Alerting
- **Critical Health Drop**: Alert if score drops >20 points
- **Scan Failure**: Alert if daily scan fails
- **Security Issues**: Immediate alert for vulnerabilities
- **Performance Degradation**: Alert if scan time >30 minutes

## Future Architecture Improvements

1. **Distributed Scanning**: Use Celery for parallel feature scanning
2. **Machine Learning Models**: Train on historical data for better predictions
3. **Real-time Monitoring**: WebSocket connections for live updates
4. **Plugin Architecture**: Allow custom analyzers and recommenders
5. **GraphQL API**: More flexible querying of enhancement data
6. **Kubernetes Jobs**: Containerized scanning for scalability
7. **Event Streaming**: Kafka integration for event-driven updates
8. **Federated Analysis**: Analyze across multiple Magnus instances
9. **Custom Metrics**: User-defined health metrics and weights
10. **A/B Testing**: Test recommendations before full rollout

---

**Last Updated**: 2025-11-01
**Architecture Version**: 1.0.0
**Maintained By**: Enhancement Agent Team