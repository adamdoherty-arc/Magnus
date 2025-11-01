# AI Research Assistant - Architecture

## System Overview

The AI Research Assistant is built as a multi-agent system using LangChain and CrewAI frameworks. It orchestrates four specialized agents to provide comprehensive stock analysis through a scalable, cached architecture.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit UI Layer                        │
│  (Positions Page → 🤖 Button → Research Modal/Sidebar)      │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                 FastAPI Endpoint Layer                       │
│         /api/research/{symbol}                               │
│         /api/research/{symbol}/refresh                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                  Cache Layer (Redis)                         │
│         TTL: 30 minutes │ Key: research:{symbol}             │
└─────────┬──────────────────────────────┬────────────────────┘
         Hit                             Miss
          │                               │
     ┌────▼─────┐                    ┌───▼──────────────────┐
     │  Return  │                    │  Research            │
     │  Cached  │                    │  Orchestrator Agent  │
     │  Result  │                    │                      │
     └──────────┘                    └──────┬───────────────┘
                                             │
                    ┌────────────────────────┼────────────────────────┐
                    │                        │                        │
         ┌──────────▼──────────┐  ┌─────────▼───────────┐  ┌─────────▼─────────┐
         │  Fundamental         │  │  Technical          │  │  Sentiment        │
         │  Analyst Agent       │  │  Analyst Agent      │  │  Analyst Agent    │
         │                      │  │                     │  │                   │
         │  • Alpha Vantage    │  │  • yfinance        │  │  • Reddit API     │
         │  • Company Info     │  │  • TA indicators   │  │  • News APIs      │
         │  • Financials       │  │  • Chart patterns  │  │  • Social media   │
         └──────────┬──────────┘  └─────────┬───────────┘  └─────────┬─────────┘
                    │                        │                        │
                    └────────────────────────┼────────────────────────┘
                                             │
                               ┌─────────────▼─────────────┐
                               │  Options Strategist       │
                               │  Agent                    │
                               │                           │
                               │  • Options chain data    │
                               │  • Greeks calculation    │
                               │  • IV analysis           │
                               │  • Probability calc      │
                               └──────────┬────────────────┘
                                          │
                               ┌──────────▼────────────┐
                               │  LLM Synthesis        │
                               │  (Groq/Ollama)        │
                               │                       │
                               │  • Combine insights   │
                               │  • Generate report    │
                               │  • Score & recommend  │
                               └──────────┬────────────┘
                                          │
                               ┌──────────▼────────────┐
                               │  Cache & Return       │
                               │  (Redis + FastAPI)    │
                               └───────────────────────┘
```

## Component Details

### 1. FastAPI Endpoint Layer

**File**: `src/api/research_endpoints.py`

```python
@app.get("/api/research/{symbol}")
async def get_research(symbol: str, force_refresh: bool = False):
    """
    Get AI research for a stock symbol
    Returns cached result if available and not expired
    """
    pass

@app.get("/api/research/{symbol}/refresh")
async def refresh_research(symbol: str):
    """Force refresh analysis (bypasses cache)"""
    pass
```

**Responsibilities**:
- Request validation and sanitization
- Cache lookup/invalidation
- Orchestrator agent invocation
- Response formatting (JSON)
- Error handling and rate limiting

---

### 2. Research Orchestrator Agent

**File**: `src/agents/ai_research/orchestrator.py`

**Class**: `ResearchOrchestrator`

```python
class ResearchOrchestrator:
    def __init__(self, llm_provider='groq'):
        self.crew = Crew(
            agents=[
                self.fundamental_analyst,
                self.technical_analyst,
                self.sentiment_analyst,
                self.options_strategist
            ],
            tasks=[...],
            process=Process.sequential
        )

    async def analyze(self, symbol: str) -> ResearchReport:
        """Coordinate all agents and synthesize results"""
        pass
```

**Responsibilities**:
- Initialize and coordinate all specialist agents
- Define task execution order
- Collect agent outputs
- Synthesize final research report
- Handle agent failures gracefully

---

### 3. Specialist Agents

#### Fundamental Analyst Agent

**File**: `src/agents/ai_research/fundamental_agent.py`

**Data Sources**:
- Alpha Vantage: Company overview, income statements, balance sheets
- yfinance: Basic financials, earnings dates

**Responsibilities**:
- Retrieve financial statements
- Calculate valuation ratios (P/E, P/B, PEG, DCF)
- Analyze earnings trends
- Assess competitive position
- Generate fundamental score (0-100)

**Output**:
```python
FundamentalAnalysis(
    score=85,
    revenue_growth=0.12,
    earnings_beat_count=4,
    pe_ratio=28.5,
    sector_avg_pe=25.0,
    recommendation="Strong fundamentals, slight premium valuation"
)
```

---

#### Technical Analyst Agent

**File**: `src/agents/ai_research/technical_agent.py`

**Data Sources**:
- yfinance: Price history, volume data
- TA-Lib: Technical indicators

**Responsibilities**:
- Calculate indicators (RSI, MACD, Bollinger Bands)
- Identify chart patterns
- Determine support/resistance levels
- Analyze trend strength
- Generate technical score (0-100)

**Output**:
```python
TechnicalAnalysis(
    score=60,
    trend="sideways",
    rsi=52,
    macd_signal="neutral",
    support_level=170,
    resistance_level=180,
    recommendation="Neutral technical setup"
)
```

---

#### Sentiment Analyst Agent

**File**: `src/agents/ai_research/sentiment_agent.py`

**Data Sources**:
- Reddit API: r/wallstreetbets, r/investing, r/stocks
- News APIs: Alpha Vantage news, Google News RSS
- yfinance: Analyst recommendations

**Responsibilities**:
- Scrape and analyze news headlines
- Calculate social media sentiment
- Track institutional activity
- Monitor insider trading
- Generate sentiment score (0-100)

**Output**:
```python
SentimentAnalysis(
    score=75,
    news_sentiment="positive",
    social_sentiment="neutral",
    institutional_activity="moderate_buying",
    insider_trades=[],
    recommendation="Positive overall sentiment"
)
```

---

#### Options Strategist Agent

**File**: `src/agents/ai_research/options_agent.py`

**Data Sources**:
- yfinance: Options chain, Greeks
- Black-Scholes: Greeks calculation (mibian library)

**Responsibilities**:
- Retrieve options chain
- Calculate IV rank and percentile
- Analyze historical earnings moves
- Detect unusual options flow
- Calculate probability of profit
- Recommend optimal strikes/expirations

**Output**:
```python
OptionsAnalysis(
    iv_rank=45,
    iv_percentile=62,
    next_earnings="2025-11-24",
    avg_earnings_move=0.04,
    unusual_activity=[],
    recommendation="Moderate IV suitable for selling premium"
)
```

---

### 4. LLM Synthesis Layer

**Providers**:
- **Groq** (default): Fast inference, free tier
- **Ollama**: Local LLMs (llama2, mistral)
- **OpenAI**: Highest quality (optional paid)

**Prompt Template**:
```python
SYNTHESIS_PROMPT = """
You are an expert options trader analyzing {symbol}.

Fundamental Analysis:
{fundamental_analysis}

Technical Analysis:
{technical_analysis}

Sentiment Analysis:
{sentiment_analysis}

Options Data:
{options_analysis}

User's Position:
{user_position}

Task: Provide a concise investment recommendation (4-5 sentences).
Include:
1. Overall rating (1-5 stars)
2. Key strengths and risks
3. Specific advice for this position
4. Any time-sensitive factors (earnings, ex-dividend)

Output as JSON:
{
  "rating": 4,
  "summary": "...",
  "strengths": [...],
  "risks": [...],
  "recommendation": "...",
  "time_sensitive": [...]
}
```

---

### 5. Caching Layer

**Technology**: Redis

**Configuration**:
```python
REDIS_CONFIG = {
    'host': 'localhost',
    'port': 6379,
    'db': 0,
    'decode_responses': True
}

CACHE_TTL = 1800  # 30 minutes
```

**Cache Keys**:
- `research:{symbol}` - Full research report
- `research:{symbol}:timestamp` - Last update time
- `research:{symbol}:api_calls` - API call counter

**Cache Invalidation**:
- TTL expiration (30 minutes)
- Manual refresh button
- Market close (store until next open)

---

## Data Flow

### Cache Hit (Fast Path)
```
User clicks 🤖
→ FastAPI checks Redis
→ Cache hit
→ Return cached JSON (<100ms)
→ Display in UI
```

### Cache Miss (Analysis Path)
```
User clicks 🤖
→ FastAPI checks Redis
→ Cache miss
→ Invoke Orchestrator
→ Agents fetch data in parallel
  ├── Fundamental (Alpha Vantage)
  ├── Technical (yfinance)
  ├── Sentiment (Reddit + News)
  └── Options (yfinance options chain)
→ LLM synthesizes results
→ Cache result in Redis (TTL=30min)
→ Return JSON (<30s)
→ Display in UI
```

---

## API Rate Limiting

### Request Rate Limiter
```python
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Limit to 10 requests/minute per user"""
    pass
```

### External API Limits
| API | Free Tier Limit | Our Usage | Daily Max Stocks |
|-----|----------------|-----------|------------------|
| Alpha Vantage | 500/day | 5/stock | 100 stocks |
| Reddit | 60/min | 2/stock | Unlimited |
| yfinance | Unlimited | 3/stock | Unlimited |
| Groq | 30/min | 1/stock | ~1800 stocks |

**Safety Measures**:
- API call counter per symbol
- Exponential backoff on rate limit
- Fallback to cached data
- User notification on limit exceeded

---

## Error Handling

### Error Types
1. **API Errors** (Alpha Vantage down)
   - Fallback: Use yfinance only
   - Cache stale data for 24 hours

2. **Rate Limit Errors**
   - Retry after 60 seconds
   - Use cached data if available
   - Notify user of delay

3. **LLM Errors** (Groq unavailable)
   - Fallback: Return raw data without synthesis
   - Switch to Ollama if configured

4. **Symbol Not Found**
   - Return error: "Symbol not supported"
   - Suggest similar symbols

### Retry Logic
```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def fetch_with_retry(url):
    pass
```

---

## Security

### API Key Management
- Stored in `.env` (never in code)
- Redacted in logs
- Encrypted in transit (HTTPS)

### Input Validation
- Symbol: Alphanumeric, max 5 chars
- Sanitize against SQL injection
- Rate limit per IP

### Data Privacy
- No PII stored
- Redis data encrypted at rest (optional)
- Logs anonymized

---

## Performance Optimization

### Parallel Data Fetching
```python
async def fetch_all_data(symbol):
    results = await asyncio.gather(
        fetch_fundamental(symbol),
        fetch_technical(symbol),
        fetch_sentiment(symbol),
        fetch_options(symbol),
        return_exceptions=True
    )
    return results
```

### Database Indexing
```sql
-- Cache lookup index
CREATE INDEX idx_research_cache_symbol ON research_cache(symbol);
CREATE INDEX idx_research_cache_expires_at ON research_cache(expires_at);
```

### CDN for Static Data
- Company logos: Cloudflare CDN
- Historical data: S3 + CloudFront

---

## Monitoring & Logging

### Metrics Tracked
- Request latency (p50, p95, p99)
- Cache hit rate
- API call counts
- Error rates by type
- Agent execution times

### Logging
```python
logger.info(
    "Research completed",
    extra={
        "symbol": symbol,
        "cache_hit": False,
        "latency_ms": 2847,
        "api_calls": 8,
        "agents_executed": 4
    }
)
```

### Alerts
- API rate limit approaching (80%)
- Error rate spike (>5%)
- Latency degradation (>10s p95)

---

## Deployment

### Development
```bash
# Start services
docker-compose up redis
uvicorn src.api.research_endpoints:app --reload

# Test endpoint
curl http://localhost:8000/api/research/AAPL
```

### Production
```bash
# Docker container
docker build -t magnus-ai-research .
docker run -p 8000:8000 magnus-ai-research

# Kubernetes (future)
kubectl apply -f k8s/ai-research-deployment.yaml
```

---

## Testing Strategy

### Unit Tests
- Each agent independently tested
- Mock external APIs
- Verify output schemas

### Integration Tests
- Full orchestration flow
- Real API calls (sandbox)
- Cache behavior validation

### Load Tests
- Simulate 100 concurrent users
- Verify rate limiting
- Check cache effectiveness

---

## Future Improvements

See [WISHLIST.md](WISHLIST.md):
- Agent memory/context between requests
- Real-time streaming results
- Fine-tuned LLM for financial analysis
- Agent collaboration (not just sequential)
- Portfolio-level analysis

---

**Version**: 1.0.0
**Last Updated**: 2025-11-01
**Status**: ✅ In Development
