# AI-Native Continuous Improvement System - Implementation Guide

**Version**: 1.0.0
**Date**: 2025-11-06
**Status**: Ready for Implementation

---

## Quick Start

### Prerequisites

1. PostgreSQL 14+ installed and running
2. Python 3.11+ with pip
3. API Keys:
   - OpenAI API key (or Ollama for local LLM)
   - Reddit API credentials
   - GitHub personal access token
4. Environment variables configured (see `.env.example`)

### 1. Database Setup (5 minutes)

```bash
# Navigate to project root
cd /c/Code/WheelStrategy

# Execute schema
psql -h localhost -U postgres -d magnus -f src/ai_continuous_improvement/schema.sql

# Verify installation
psql -h localhost -U postgres -d magnus -c "SELECT * FROM v_ci_top_priorities LIMIT 5;"
```

Expected output: Empty table (ready for data)

### 2. Install Python Dependencies (5 minutes)

```bash
# Add to requirements.txt
cat >> requirements.txt << EOF

# AI Continuous Improvement System
praw==7.7.1                    # Reddit API
PyGithub==2.1.1                # GitHub API
sentence-transformers==2.2.2   # Similarity detection
langchain==0.1.0               # LLM orchestration
apscheduler==3.10.4            # Job scheduling
EOF

# Install
pip install -r requirements.txt
```

### 3. Configure Environment Variables (5 minutes)

Create or update `.env`:

```bash
# AI Continuous Improvement Configuration

# OpenAI API (or use local Ollama)
OPENAI_API_KEY=sk-your-key-here
USE_LOCAL_LLM=false  # Set to true to use Ollama instead

# Reddit API
REDDIT_CLIENT_ID=your-client-id
REDDIT_CLIENT_SECRET=your-secret
REDDIT_USER_AGENT=Magnus Research Agent v1.0

# GitHub API
GITHUB_TOKEN=ghp_your-token-here

# Database (if different from main config)
# DB_HOST=localhost
# DB_NAME=magnus
# DB_USER=postgres
# DB_PASSWORD=
```

### 4. Migrate Existing Wishlist (15 minutes)

```bash
# Run migration script
python -m src.ai_continuous_improvement.migrate_wishlist

# Verify migration
psql -h localhost -U postgres -d magnus -c "SELECT COUNT(*) FROM ci_enhancements;"
```

Expected: 78+ enhancements from ENHANCEMENT_WISHLIST.md

### 5. Test Research Agent (10 minutes)

```bash
# Run test scan
python -m src.ai_continuous_improvement.research_agent

# Check results
psql -h localhost -U postgres -d magnus -c "SELECT * FROM v_ci_research_pipeline LIMIT 10;"
```

Expected: 10-50 research findings from Reddit/GitHub

### 6. Start Scheduled Jobs (5 minutes)

```bash
# Start the scheduler daemon
python -m src.ai_continuous_improvement.scheduler start

# Check status
python -m src.ai_continuous_improvement.scheduler status
```

Expected: Research agent scheduled for every 12 hours

---

## Implementation Phases

### Phase 1: Foundation (Weeks 1-2)

**Status**: Ready to Start

**Implementation Checklist**:

- [x] Database schema created (`schema.sql`)
- [x] Research agent core implementation (`research_agent.py`)
- [ ] Migration script for existing wishlist
- [ ] CLI interface for viewing findings
- [ ] Basic testing suite
- [ ] Documentation

**Files to Create**:

1. `src/ai_continuous_improvement/migrate_wishlist.py`
2. `src/ai_continuous_improvement/cli.py`
3. `tests/test_research_agent.py`

**Effort**: 40 hours (2 weeks, 1 developer)

### Phase 2: Enhancement Agent (Weeks 3-4)

**Files to Create**:

1. `src/ai_continuous_improvement/enhancement_agent.py`
   - Health check orchestrator
   - Code quality scanning
   - Security scanning
   - Test execution
   - Issue detection

2. `src/ai_continuous_improvement/health_checkers/`
   - `code_quality_checker.py`
   - `security_checker.py`
   - `performance_checker.py`
   - `test_runner.py`

3. `src/ai_continuous_improvement/prioritization_engine.py`
   - AI-driven priority scoring
   - Dependency resolution

**Effort**: 50 hours (2 weeks, 1 developer)

### Phase 3: Dashboard Integration (Weeks 5-6)

**Files to Create**:

1. `pages/continuous_improvement_page.py`
   - Enhancements Kanban board
   - Research discoveries feed
   - Health dashboard
   - Agent performance metrics

2. `src/ai_continuous_improvement/api.py`
   - RESTful API endpoints
   - FastAPI routes

**Effort**: 60 hours (2 weeks, 1 frontend + 1 backend developer)

### Phase 4: Learning Loops (Weeks 7-8)

**Files to Create**:

1. `src/ai_continuous_improvement/learning_engine.py`
   - Outcome tracking
   - Accuracy calculation
   - Training sample collection

2. `src/ai_continuous_improvement/model_optimizer.py`
   - A/B testing framework
   - Prompt optimization
   - Model fine-tuning

**Effort**: 50 hours (2 weeks, 1 ML engineer)

### Phase 5: Advanced Features (Weeks 9-12)

**Files to Create**:

1. `src/ai_continuous_improvement/auto_fix_executor.py`
   - Automated fix execution
   - Git integration
   - PR creation

2. `src/ai_continuous_improvement/sources/`
   - `arxiv_scraper.py`
   - `hacker_news_scraper.py`
   - `stackoverflow_scraper.py`

3. `src/ai_continuous_improvement/strategy_optimizer.py`
   - Trading strategy parameter tracking
   - Backtesting integration
   - Adaptive optimization

**Effort**: 80 hours (4 weeks, 1 developer + 1 ML engineer)

---

## API Documentation

See `docs/architecture/ai_continuous_improvement_system.md` Section 4 for complete API contracts.

### Key Endpoints

**Research Agent**:
- `POST /api/v1/research/scan` - Trigger research scan
- `GET /api/v1/research/findings` - List findings
- `POST /api/v1/research/findings/{id}/convert` - Convert to enhancement

**Enhancement Agent**:
- `POST /api/v1/health/check` - Trigger health check
- `GET /api/v1/health/check/{id}` - Get results
- `GET /api/v1/enhancements` - List enhancements
- `PUT /api/v1/enhancements/{id}` - Update enhancement
- `POST /api/v1/enhancements/{id}/feedback` - Submit feedback

**Learning Loop**:
- `GET /api/v1/learning/agent-performance` - Get metrics
- `POST /api/v1/learning/feedback` - Submit feedback

**Auto-Fix**:
- `POST /api/v1/auto-fix/execute` - Execute fix
- `GET /api/v1/auto-fix/execution/{id}` - Get status

---

## Configuration

### Research Sources Configuration

Edit research sources in database:

```sql
-- Add custom source
INSERT INTO ci_research_sources (
    source_type, source_name, source_url,
    search_queries, scan_frequency_hours
) VALUES (
    'reddit',
    'r/Python',
    'https://www.reddit.com/r/Python',
    ARRAY['trading bot', 'financial analysis', 'web scraping'],
    24
);

-- Update search queries
UPDATE ci_research_sources
SET search_queries = ARRAY['new query 1', 'new query 2']
WHERE source_name = 'r/options';

-- Disable a source
UPDATE ci_research_sources
SET enabled = FALSE
WHERE source_name = 'r/Python';
```

### Health Check Configuration

Configure health check frequency:

```python
# src/ai_continuous_improvement/config.py

HEALTH_CHECK_CONFIG = {
    'full_scan_frequency_hours': 24,  # Daily full scan
    'quick_scan_frequency_hours': 4,   # Every 4 hours
    'security_scan_frequency_hours': 168,  # Weekly

    'code_quality_thresholds': {
        'min_score': 70,
        'max_complexity': 10,
        'max_line_length': 120
    },

    'test_coverage_thresholds': {
        'min_total_coverage': 60,
        'min_new_code_coverage': 80
    },

    'performance_thresholds': {
        'max_page_load_ms': 2000,
        'max_query_time_ms': 100
    }
}
```

### LLM Configuration

```python
# src/ai_continuous_improvement/config.py

LLM_CONFIG = {
    'provider': 'openai',  # or 'ollama' for local
    'model': 'gpt-4',      # or 'llama2' for local
    'temperature': 0.3,
    'max_tokens': 1000,

    # Cost limits
    'daily_max_cost_usd': 10.0,
    'per_request_timeout_seconds': 30
}
```

---

## Testing

### Unit Tests

```bash
# Run all tests
pytest tests/test_ai_continuous_improvement/

# Run specific test
pytest tests/test_research_agent.py::test_reddit_scan

# Run with coverage
pytest --cov=src/ai_continuous_improvement tests/
```

### Integration Tests

```bash
# Test database connectivity
python -m src.ai_continuous_improvement.test_db_connection

# Test API endpoints
python -m src.ai_continuous_improvement.test_api

# Test end-to-end workflow
python -m src.ai_continuous_improvement.test_e2e
```

### Manual Testing

```bash
# Trigger manual research scan
curl -X POST http://localhost:8000/api/v1/research/scan \
  -H "Content-Type: application/json" \
  -d '{"source_types": ["reddit"], "priority": "high"}'

# Check health
curl http://localhost:8000/api/v1/health/check/latest
```

---

## Monitoring

### Application Metrics

Monitor via Prometheus + Grafana dashboard:

**Key Metrics**:
- `ci_research_findings_total` - Total findings discovered
- `ci_research_relevance_score_avg` - Average relevance score
- `ci_enhancement_completion_rate` - % of enhancements completed
- `ci_health_score` - Overall platform health (0-100)
- `ci_agent_accuracy` - AI prediction accuracy (0-100)

### Logging

Logs location: `logs/ai_continuous_improvement/`

**Log Levels**:
- `ERROR`: Failed API calls, database errors
- `WARNING`: Low relevance findings, API rate limits
- `INFO`: Scan completion, enhancement creation
- `DEBUG`: Detailed AI analysis, similarity scores

### Alerts

Configure alerts in `src/ai_continuous_improvement/alerts.py`:

```python
ALERT_CONFIG = {
    'health_score_drop': {
        'threshold': 5,  # Alert if drops >5 points
        'notify': ['email', 'telegram']
    },
    'critical_issues': {
        'threshold': 1,  # Alert on any critical issue
        'notify': ['telegram', 'sms']
    },
    'agent_accuracy_low': {
        'threshold': 70,  # Alert if accuracy <70%
        'notify': ['email']
    }
}
```

---

## Troubleshooting

### Common Issues

**1. "Reddit API authentication failed"**

Solution:
- Verify `REDDIT_CLIENT_ID` and `REDDIT_CLIENT_SECRET` in `.env`
- Create Reddit app at https://www.reddit.com/prefs/apps
- Ensure user agent is set correctly

**2. "OpenAI API rate limit exceeded"**

Solution:
- Check API usage at https://platform.openai.com/usage
- Enable `USE_LOCAL_LLM=true` to use Ollama instead
- Reduce scan frequency

**3. "Database connection pool exhausted"**

Solution:
- Increase `max_connections` in PostgreSQL config
- Implement connection pooling (pgbouncer)
- Check for connection leaks in code

**4. "Similarity model taking too long"**

Solution:
- Use GPU acceleration if available
- Reduce comparison window (currently 30 days)
- Use smaller model (e.g., 'all-MiniLM-L12-v2')

**5. "Auto-fix broke tests"**

Solution:
- Auto-fix only executes on `auto_fixable = TRUE` issues
- All auto-fixes run tests before committing
- Check auto-fix logs in `logs/auto_fix/`
- Manually rollback: `git revert <commit-hash>`

---

## Performance Optimization

### Database Optimization

```sql
-- Create missing indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ci_enhancements_priority_status
ON ci_enhancements(priority, status, ai_priority_score DESC);

-- Analyze tables
ANALYZE ci_enhancements;
ANALYZE ci_research_findings;
ANALYZE ci_health_checks;

-- Check slow queries
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
WHERE query LIKE '%ci_%'
ORDER BY mean_exec_time DESC
LIMIT 10;
```

### Caching Strategy

```python
# Use Redis for frequent queries
import redis

cache = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Cache top priorities for 5 minutes
cache.setex('ci:top_priorities', 300, json.dumps(priorities))

# Cache health score for 1 hour
cache.setex('ci:health_score', 3600, str(health_score))
```

### API Rate Limiting

```python
# Implement per-user rate limiting
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/v1/research/scan")
@limiter.limit("5/hour")  # Max 5 scans per hour per IP
async def trigger_scan():
    ...
```

---

## Security Best Practices

1. **API Keys**: Store in environment variables, never commit to git
2. **SQL Injection**: Always use parameterized queries
3. **Auto-Fix**: Sandbox code execution, require human approval for critical changes
4. **Authentication**: Implement OAuth2 for production API access
5. **Audit Logging**: Log all enhancement modifications with timestamps and user

---

## Deployment

### Development

```bash
# Local development server
python -m src.ai_continuous_improvement.server --env development

# Access at http://localhost:8000
```

### Staging

```bash
# Deploy to staging
git push staging main

# Run migrations
ssh staging "cd /app && python -m alembic upgrade head"

# Restart services
ssh staging "systemctl restart ci-research-agent ci-enhancement-agent"
```

### Production

```bash
# Create production release
git tag -a v1.0.0 -m "AI Continuous Improvement System v1.0.0"
git push origin v1.0.0

# Deploy via CI/CD (GitHub Actions)
# Manual approval required in GitHub UI

# Verify deployment
curl https://api.magnus.trading/health
```

---

## Maintenance

### Daily Tasks

- Monitor health score trends
- Review critical issues
- Approve high-priority enhancements

### Weekly Tasks

- Review research findings
- Analyze agent performance
- Update research source queries
- Check API cost usage

### Monthly Tasks

- Fine-tune AI models based on feedback
- Optimize database queries
- Review and archive completed enhancements
- Update documentation

---

## Support

For issues or questions:

1. Check troubleshooting section above
2. Review logs in `logs/ai_continuous_improvement/`
3. Search existing GitHub issues
4. Create new GitHub issue with logs and steps to reproduce

---

## Changelog

### v1.0.0 (2025-11-06)

- Initial release
- Research agent with Reddit and GitHub integration
- Database schema for enhancement tracking
- Architecture documentation
- Implementation guide

---

## License

Copyright 2025 Magnus Trading Platform. All rights reserved.

---

**Next Steps**: Begin Phase 1 implementation following the checklist above.
