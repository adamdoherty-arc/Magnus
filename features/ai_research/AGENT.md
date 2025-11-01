# AI Research Assistant - Agent Configuration

## Agent Identity

**Agent Name**: AI Research Agent
**Agent ID**: `ai_research_agent`
**Version**: 1.0.0
**Status**: 🟡 In Development
**Template**: FEATURE_TEMPLATE.md

---

## Role & Responsibilities

### Primary Role
Provide comprehensive AI-powered stock analysis for trading decisions

### Core Responsibilities
1. **Data Aggregation** - Collect fundamental, technical, sentiment, and options data
2. **Multi-Agent Orchestration** - Coordinate 4 specialist agents
3. **Insight Synthesis** - Combine agent outputs into actionable recommendations
4. **Cache Management** - Optimize for performance and API rate limits
5. **User Communication** - Deliver clear, concise analysis through UI

---

## Agent Architecture

### Orchestrator Agent
**Class**: `ResearchOrchestrator`
**Location**: `src/agents/ai_research/orchestrator.py`

**Responsibilities**:
- Initialize specialist agents
- Define task execution flow
- Handle agent failures gracefully
- Synthesize final report
- Manage caching strategy

**Dependencies**:
- LangChain (agent framework)
- CrewAI (multi-agent coordination)
- Redis (caching layer)

---

### Specialist Agents

#### 1. Fundamental Analyst Agent
**Name**: `fundamental_analyst`
**Role**: Financial analyst
**Goal**: Assess company financial health and valuation
**Tools**: Alpha Vantage, yfinance
**Output**: FundamentalAnalysis (score 0-100)

#### 2. Technical Analyst Agent
**Name**: `technical_analyst`
**Role**: Chart analyst
**Goal**: Identify technical patterns and trends
**Tools**: yfinance, TA-Lib
**Output**: TechnicalAnalysis (score 0-100)

#### 3. Sentiment Analyst Agent
**Name**: `sentiment_analyst`
**Role**: Market sentiment analyst
**Goal**: Gauge sentiment from news and social media
**Tools**: Reddit API, News APIs, yfinance
**Output**: SentimentAnalysis (score 0-100)

#### 4. Options Strategist Agent
**Name**: `options_strategist`
**Role**: Options trader
**Goal**: Analyze options market and recommend strategies
**Tools**: yfinance options, mibian (Greeks)
**Output**: OptionsAnalysis + StrategyRecommendations

---

## Communication Protocol

### Input Format
```python
ResearchRequest(
    symbol: str,              # e.g., "AAPL"
    user_position: Optional[Position] = None,
    force_refresh: bool = False
)
```

### Output Format
```python
ResearchReport(
    symbol: str,
    timestamp: datetime,
    overall_rating: float,     # 1.0 - 5.0
    quick_summary: str,
    fundamental: FundamentalAnalysis,
    technical: TechnicalAnalysis,
    sentiment: SentimentAnalysis,
    options: OptionsAnalysis,
    recommendation: TradeRecommendation,
    metadata: AnalysisMetadata
)
```

---

## Integration Points

### Upstream Dependencies (Receives From)
- **Positions Feature** - User's current positions for context-aware analysis
- **User Settings** - Analysis preferences (risk tolerance, strategies)
- **Auth Service** - User authentication and rate limiting

### Downstream Dependencies (Sends To)
- **Positions UI** - Displays research modal/sidebar
- **Opportunities** - Powers AI-powered opportunity screening
- **Alerts** - Triggers notifications on significant changes

### External APIs
- **Alpha Vantage** - Fundamental data (500 calls/day free)
- **Reddit API** - Social sentiment (60/min free)
- **yfinance** - Price data, options chains (unlimited)
- **Groq/Ollama** - LLM inference

---

## State Management

### Stateless Components
- All specialist agents (no memory between requests)
- API endpoints (REST, no session)

### Stateful Components
- **Redis Cache** - 30-minute TTL, stores complete reports
- **API Rate Counters** - Daily counters per API
- **User Request History** - Last 10 researched symbols (for UI autocomplete)

---

## Error Handling

### Agent Failure Scenarios

#### Individual Agent Failure
**Scenario**: Fundamental agent fails (Alpha Vantage down)
**Handling**: Continue with other 3 agents, note missing data in report
**Fallback**: Use yfinance for basic fundamentals

#### Critical Agent Failure
**Scenario**: LLM synthesis fails (Groq unavailable)
**Handling**: Return raw agent data without synthesis
**Fallback**: Switch to Ollama if configured

#### Complete System Failure
**Scenario**: All external APIs unavailable
**Handling**: Return cached data with stale data warning
**Escalation**: Log incident, notify admin

### Error Response Format
```python
ErrorResponse(
    error_code: str,           # "AGENT_FAILURE"
    error_message: str,
    failed_components: List[str],
    fallback_used: bool,
    cached_data_available: bool,
    retry_after_seconds: Optional[int]
)
```

---

## Performance Monitoring

### Key Metrics
| Metric | Target | Alert Threshold |
|--------|--------|----------------|
| Cache Hit Rate | >80% | <60% |
| Avg Response Time (cached) | <100ms | >500ms |
| Avg Response Time (fresh) | <10s | >30s |
| API Error Rate | <1% | >5% |
| Agent Success Rate | >95% | <90% |

### Logging
```python
logger.info(
    "Research completed",
    extra={
        "symbol": symbol,
        "cache_hit": bool,
        "latency_ms": int,
        "agents_succeeded": int,
        "agents_failed": int,
        "api_calls_used": int
    }
)
```

---

## Security & Privacy

### API Key Management
- Keys stored in `.env` only
- Never logged or exposed
- Rotated quarterly (recommended)

### Rate Limiting
- Per-user: 10 req/min, 100 req/hour, 1000 req/day
- Per-IP: 30 req/min (abuse prevention)
- Global: Monitor API quotas, queue if approaching limit

### Data Privacy
- No PII stored
- Symbol research history anonymized after 30 days
- User positions never logged

---

## Testing Strategy

### Unit Tests
- Each agent independently testable
- Mock external APIs
- Verify output schema compliance

### Integration Tests
- Full orchestration flow
- Real API calls (sandbox mode)
- Cache behavior validation

### End-to-End Tests
- UI → API → Agents → Response
- Test error scenarios
- Load testing (100 concurrent users)

### Test Coverage Target
- Code coverage: >85%
- Critical paths: 100%
- Error paths: >90%

---

## Deployment Requirements

### Environment Variables
```env
# Required
ALPHA_VANTAGE_API_KEY=your_key
REDIS_HOST=localhost
REDIS_PORT=6379

# Optional (for cloud LLM)
GROQ_API_KEY=your_key

# Configuration
LLM_PROVIDER=groq  # or 'ollama'
CACHE_TTL=1800     # 30 minutes
MAX_API_CALLS_PER_DAY=500
```

### Infrastructure
- Redis server (caching)
- FastAPI application (endpoints)
- LLM service (Groq cloud or Ollama local)

### Dependencies
```txt
langchain>=0.1.0
crewai>=0.2.0
alpha-vantage>=2.3.0
yfinance>=0.2.0
redis>=4.0.0
fastapi>=0.100.0
groq>=0.4.0  # Optional
mibian>=0.1.3  # Greeks calculation
```

---

## Maintenance

### Regular Tasks
- **Daily**: Monitor API usage, check rate limits
- **Weekly**: Review error logs, optimize slow queries
- **Monthly**: Update agent prompts based on performance
- **Quarterly**: Rotate API keys, review agent accuracy

### Incident Response
1. Check logs: `logs/ai_research_YYYYMMDD.log`
2. Verify API status: Alpha Vantage, Groq, Reddit
3. Test individual agents: `python src/agents/test_agents.py`
4. Check Redis: `redis-cli ping`
5. Restart services if needed

---

## Versioning

### Current Version: 1.0.0

### Changelog
See [CHANGELOG.md](CHANGELOG.md)

### Upgrade Path
- 1.0.x → 1.1.x: Backward compatible, new features
- 1.x → 2.x: Breaking changes, migration required

---

## Communication with Main Agent

### Registration
```yaml
feature_id: ai_research
feature_name: AI Research Assistant
endpoints:
  - /api/research/{symbol}
  - /api/research/{symbol}/refresh
status: in_development
health_check: /api/research/health
```

### Health Check Response
```json
{
  "status": "healthy",
  "uptime_seconds": 86400,
  "cache_hit_rate": 0.82,
  "agents_operational": 4,
  "api_quotas": {
    "alpha_vantage": "234/500 (47%)",
    "reddit": "42/60 (70%)",
    "groq": "18/30 (60%)"
  }
}
```

### Emergency Shutdown Protocol
1. Return cached data only (no fresh analysis)
2. Display maintenance message in UI
3. Log all incoming requests for replay
4. Notify Main Agent of degraded state
5. Automatic recovery attempt every 5 minutes

---

## Related Agents

### Dependencies
- **Positions Agent** - Provides user position context
- **Opportunities Agent** - Uses research for screening
- **Alerts Agent** - Triggers on research score changes

### Data Sharing
- Research scores shared with Dashboard (portfolio health)
- Recommendations logged for backtesting
- Error metrics aggregated by Main Agent

---

**Version**: 1.0.0
**Last Updated**: 2025-11-01
**Status**: 🟡 In Development
**Maintained By**: AI Research Team
**Contact**: See MAIN_AGENT.md for routing
