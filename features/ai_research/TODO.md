# AI Research Assistant - TODO

## Sprint 1: Foundation & Documentation ✅
**Status**: ✅ COMPLETED
**Timeline**: 2025-11-01

- [x] Create feature folder structure
- [x] Write README.md
- [x] Write ARCHITECTURE.md
- [x] Write SPEC.md
- [x] Write WISHLIST.md
- [x] Write AGENT.md
- [x] Write TODO.md
- [x] Write CHANGELOG.md
- [x] Register with MAIN_AGENT.md
- [x] Update features/INDEX.md

---

## Sprint 2: Core Infrastructure 🔵
**Status**: ⏳ IN PROGRESS
**Timeline**: 2025-11-02 to 2025-11-03
**Goal**: Build foundational agent system

### Phase 1: Setup & Dependencies
- [ ] Install required packages
  ```bash
  pip install langchain crewai alpha-vantage groq yfinance redis mibian praw fastapi uvicorn
  ```
- [ ] Setup Redis server (Docker or WSL)
- [ ] Get Alpha Vantage API key (free)
- [ ] Get Groq API key (optional, free)
- [ ] Add API keys to `.env`
- [ ] Test API connections

### Phase 2: Data Layer
- [ ] Create `src/agents/ai_research/` folder structure
- [ ] Implement `src/agents/ai_research/data_sources/alpha_vantage.py`
- [ ] Implement `src/agents/ai_research/data_sources/yfinance_wrapper.py`
- [ ] Implement `src/agents/ai_research/data_sources/reddit_sentiment.py`
- [ ] Implement `src/agents/ai_research/data_sources/news_aggregator.py`
- [ ] Create data models (`models.py`)
- [ ] Add unit tests for data sources

### Phase 3: Specialist Agents
- [ ] Implement `fundamental_agent.py`
  - [ ] Fetch financials from Alpha Vantage
  - [ ] Calculate valuation metrics
  - [ ] Generate fundamental score (0-100)
  - [ ] Return `FundamentalAnalysis` object
- [ ] Implement `technical_agent.py`
  - [ ] Fetch price history
  - [ ] Calculate RSI, MACD, Bollinger Bands
  - [ ] Identify support/resistance
  - [ ] Generate technical score (0-100)
- [ ] Implement `sentiment_agent.py`
  - [ ] Scrape Reddit mentions
  - [ ] Fetch news headlines
  - [ ] Analyze insider trades
  - [ ] Generate sentiment score (0-100)
- [ ] Implement `options_agent.py`
  - [ ] Fetch options chain
  - [ ] Calculate IV rank/percentile
  - [ ] Calculate Greeks (Black-Scholes)
  - [ ] Recommend strategies
- [ ] Add unit tests for each agent

### Phase 4: Orchestration
- [ ] Implement `orchestrator.py`
  - [ ] Initialize specialist agents
  - [ ] Define task execution flow
  - [ ] Handle agent failures
  - [ ] Synthesize with LLM
  - [ ] Return `ResearchReport`
- [ ] Add integration tests
- [ ] Optimize for parallel execution

---

## Sprint 3: API & Caching 🔵
**Status**: ⏳ PENDING
**Timeline**: 2025-11-04 to 2025-11-05
**Goal**: Expose research via FastAPI with caching

### Phase 1: FastAPI Endpoints
- [ ] Create `src/api/research_endpoints.py`
- [ ] Implement `GET /api/research/{symbol}`
- [ ] Implement `GET /api/research/{symbol}/refresh`
- [ ] Implement `GET /api/research/health`
- [ ] Add request validation
- [ ] Add error handling
- [ ] Add rate limiting middleware

### Phase 2: Redis Caching
- [ ] Implement cache lookup logic
- [ ] Implement cache storage logic
- [ ] Add TTL management (30 min default)
- [ ] Add cache invalidation
- [ ] Monitor cache hit rate
- [ ] Add cache warming for popular symbols

### Phase 3: API Testing
- [ ] Unit tests for endpoints
- [ ] Integration tests (with real APIs in sandbox)
- [ ] Load testing (100 concurrent users)
- [ ] API documentation (OpenAPI/Swagger)
- [ ] Postman collection for manual testing

---

## Sprint 4: UI Integration 🔵
**Status**: ⏳ PENDING
**Timeline**: 2025-11-06 to 2025-11-07
**Goal**: Add AI Research button to Positions page

### Phase 1: UI Components
- [ ] Add 🤖 icon column to positions tables
- [ ] Create research modal component
  - [ ] Overall rating display
  - [ ] Score cards (fundamental, technical, sentiment)
  - [ ] Detailed sections (collapsible)
  - [ ] Recommendation box
  - [ ] Refresh button
  - [ ] Export button (future)
- [ ] Add loading state (spinner)
- [ ] Add error state (graceful failure)

### Phase 2: API Client
- [ ] Create `src/api/research_client.py`
- [ ] Implement async API calls from Streamlit
- [ ] Handle caching on client side
- [ ] Handle errors and retries
- [ ] Show "Last updated" timestamp

### Phase 3: User Experience
- [ ] Add tooltips explaining scores
- [ ] Add color coding (green/yellow/red)
- [ ] Add keyboard shortcuts (ESC to close)
- [ ] Mobile-responsive design
- [ ] Accessibility (ARIA labels)

### Phase 4: UI Testing
- [ ] Manual testing on all position types
- [ ] Test with cached data
- [ ] Test with fresh data
- [ ] Test error scenarios
- [ ] Browser compatibility (Chrome, Firefox, Safari)

---

## Sprint 5: Monitoring & Polish 🔵
**Status**: ⏳ PENDING
**Timeline**: 2025-11-08 to 2025-11-09
**Goal**: Production-ready with monitoring

### Phase 1: Logging & Monitoring
- [ ] Setup structured logging
- [ ] Add performance metrics
- [ ] Add error tracking (Sentry optional)
- [ ] Create monitoring dashboard
- [ ] Setup alerts (API quota warnings)

### Phase 2: Optimization
- [ ] Profile slow queries
- [ ] Optimize API call patterns
- [ ] Implement request batching
- [ ] Add query result caching (DB level)
- [ ] Optimize LLM prompts (token reduction)

### Phase 3: Documentation
- [ ] Update README with setup instructions
- [ ] Create user guide (with screenshots)
- [ ] Create troubleshooting guide
- [ ] Document API endpoints (Swagger)
- [ ] Update CHANGELOG

### Phase 4: Production Deployment
- [ ] Docker container build
- [ ] Environment variable validation
- [ ] Health check implementation
- [ ] Graceful shutdown handling
- [ ] Backup/restore procedures
- [ ] Deploy to production
- [ ] Smoke test in production

---

## Future Sprints (Backlog)

### Enhanced Research Links
**Priority**: 🟡 MEDIUM
- [ ] Add News link (Google Finance)
- [ ] Add Options Chain link (Robinhood)
- [ ] Add Strategy Analyzer link
- [ ] Add Alert creation link
- [ ] Add Position Notes link

### Full Greeks Display
**Priority**: 🟡 MEDIUM
- [ ] Calculate all Greeks (Delta, Gamma, Theta, Vega, Rho)
- [ ] Display in positions table
- [ ] Add tooltips explaining each Greek
- [ ] Color code by risk level

### WebSocket Real-Time Updates
**Priority**: 🔴 HIGH
- [ ] Setup FastAPI WebSocket server
- [ ] Implement Streamlit WebSocket client
- [ ] Replace meta-refresh with WebSocket
- [ ] Add reconnection logic
- [ ] Test with multiple tabs open

### Portfolio-Level Analysis
**Priority**: 🟡 MEDIUM
- [ ] Aggregate research scores across portfolio
- [ ] Calculate portfolio Greeks
- [ ] Identify correlation risks
- [ ] Sector exposure visualization

### AI Model Improvements
**Priority**: 🟢 LOW
- [ ] Fine-tune LLM on financial data
- [ ] Add agent memory/context
- [ ] Implement reinforcement learning
- [ ] A/B test different models

---

## Bug Fixes

### Known Issues
- [ ] None yet (feature not deployed)

### Reported Bugs
*This section will be updated as bugs are discovered*

---

## Technical Debt

### Code Quality
- [ ] Add type hints to all functions
- [ ] Increase test coverage to >85%
- [ ] Refactor large functions (>50 lines)
- [ ] Add docstrings to all classes/methods

### Performance
- [ ] Profile agent execution times
- [ ] Optimize database queries
- [ ] Reduce API call redundancy
- [ ] Implement connection pooling

### Security
- [ ] Add input sanitization
- [ ] Implement API key rotation
- [ ] Add audit logging
- [ ] Security audit (penetration testing)

---

## Metrics & Goals

### Success Metrics
| Metric | Current | Goal |
|--------|---------|------|
| Cache Hit Rate | TBD | >80% |
| Avg Response Time (cached) | TBD | <100ms |
| Avg Response Time (fresh) | TBD | <10s |
| User Satisfaction | TBD | >4.5/5 |
| API Error Rate | TBD | <1% |

### Usage Goals
- Week 1: 10 unique users, 100 research requests
- Month 1: 50 unique users, 1000 research requests
- Month 3: 200 unique users, 10,000 research requests

---

## Notes

### Blockers
- None currently

### Dependencies
- Waiting on: None
- Blocked by: None

### Questions for User
1. Preferred LLM provider: Groq (cloud) or Ollama (local)?
2. Research caching duration: 30 minutes OK?
3. Should we pre-cache popular stocks (SPY, QQQ, etc.)?
4. Priority: Speed or comprehensiveness?

---

**Version**: 1.0.0
**Last Updated**: 2025-11-01
**Next Review**: 2025-11-02
