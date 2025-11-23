# RAG Architecture for Options Trading Recommendations

## Executive Summary

This document outlines a production-ready Retrieval-Augmented Generation (RAG) system that learns from historical Xtrades trade data to provide intelligent recommendations for new options alerts. The system uses Qdrant vector database for similarity search, Hugging Face embeddings for semantic understanding, and Claude Sonnet 4.5 for contextual analysis.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         RAG RECOMMENDATION SYSTEM                    │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────────┐
│  New Xtrades     │
│  Alert Arrives   │
└────────┬─────────┘
         │
         v
┌────────────────────────────────────────────────────────────────────┐
│                    1. INGESTION & EMBEDDING PIPELINE                │
├────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Alert Parser                                                 │  │
│  │  - Extract: ticker, strategy, strike, expiration, premium    │  │
│  │  - Enrich: Add market data (volatility, price, sector)       │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                              ↓                                       │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Feature Engineering                                          │  │
│  │  - Technical indicators                                       │  │
│  │  - Market conditions (VIX, sector performance)               │  │
│  │  - Trade context (DTE, delta, IV rank)                       │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                              ↓                                       │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Text Embedding (Hugging Face all-mpnet-base-v2)            │  │
│  │  - Create semantic vector (768 dimensions)                   │  │
│  │  - Capture: strategy intent, market sentiment, risk profile │  │
│  └──────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────┘
         │
         v
┌────────────────────────────────────────────────────────────────────┐
│                    2. VECTOR SIMILARITY SEARCH                      │
├────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Qdrant Query                                                 │  │
│  │  - Hybrid search: Dense vector + metadata filters            │  │
│  │  - Retrieve top-k=10 similar historical trades               │  │
│  │  - Filter by: ticker, strategy, market regime                │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                              ↓                                       │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Re-ranking                                                   │  │
│  │  - Weight by recency (recent trades more relevant)           │  │
│  │  - Weight by outcome quality (high win-rate trades)          │  │
│  │  - Weight by similarity score                                │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                              ↓                                       │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Select top-5 most relevant trades for context              │  │
│  └──────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────┘
         │
         v
┌────────────────────────────────────────────────────────────────────┐
│                    3. CONTEXT ASSEMBLY & AUGMENTATION               │
├────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Historical Trade Context                                     │  │
│  │  - Format retrieved trades with outcomes                     │  │
│  │  - Calculate aggregate statistics (win rate, avg P&L)        │  │
│  │  - Identify patterns (time of day, market conditions)        │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                              ↓                                       │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Real-time Market Data                                        │  │
│  │  - Current price, IV, volume                                 │  │
│  │  - VIX level, sector trends                                  │  │
│  │  - News sentiment (if available)                             │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                              ↓                                       │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Prompt Construction                                          │  │
│  │  - System context + Retrieved trades + New alert             │  │
│  │  - Structured output format (TAKE/PASS + reasoning)          │  │
│  └──────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────┘
         │
         v
┌────────────────────────────────────────────────────────────────────┐
│                    4. LLM REASONING (Claude Sonnet 4.5)             │
├────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Contextual Analysis                                          │  │
│  │  - Compare new alert to historical patterns                  │  │
│  │  - Evaluate risk/reward based on similar outcomes            │  │
│  │  - Consider current market conditions                        │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                              ↓                                       │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Recommendation Generation                                    │  │
│  │  - Decision: TAKE / PASS / MONITOR                           │  │
│  │  - Confidence: 0-100%                                        │  │
│  │  - Reasoning: Why this recommendation                        │  │
│  │  - Evidence: Which historical trades support this            │  │
│  └──────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────┘
         │
         v
┌────────────────────────────────────────────────────────────────────┐
│                    5. FEEDBACK LOOP & LEARNING                      │
├────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Store Recommendation                                         │  │
│  │  - Save to: recommendations table                            │  │
│  │  - Link to: alert_id, retrieved_trade_ids                    │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                              ↓                                       │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Track Trade Outcome                                          │  │
│  │  - Monitor: P&L, win/loss, time to close                     │  │
│  │  - Calculate: Recommendation accuracy                        │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                              ↓                                       │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Update Vector Database                                       │  │
│  │  - Add new trade with actual outcome                         │  │
│  │  - Re-weight successful patterns                             │  │
│  │  - Archive low-performing trades                             │  │
│  └──────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────┘
         │
         v
┌────────────────────────────────────────────────────────────────────┐
│                    OUTPUT: ACTIONABLE RECOMMENDATION                │
├────────────────────────────────────────────────────────────────────┤
│  {                                                                  │
│    "recommendation": "TAKE",                                        │
│    "confidence": 87,                                               │
│    "reasoning": "Similar AAPL CSPs have 85% win rate...",         │
│    "historical_evidence": [                                        │
│      "AAPL CSP $170 - Won $250 (+80%)",                           │
│      "AAPL CSP $175 - Won $180 (+75%)"                            │
│    ],                                                              │
│    "risk_factors": ["Elevated IV", "Earnings in 2 weeks"],       │
│    "suggested_adjustment": "Consider 2-week DTE instead of 1"     │
│  }                                                                  │
└────────────────────────────────────────────────────────────────────┘
```

## System Components

### 1. Data Sources

#### Primary: PostgreSQL (Magnus Database)
- **xtrades_trades**: Historical trade data with outcomes
- **xtrades_profiles**: Trader profiles and performance
- Query for closed trades with P&L for training data

#### Secondary: Real-time Market Data
- Yahoo Finance (current prices, IV)
- VIX data (market volatility regime)
- Sector ETFs (SPY, QQQ, IWM for market context)

### 2. Vector Database: Qdrant Cloud

#### Collection Schema
- **Collection Name**: `options_trades`
- **Vector Dimensions**: 768 (all-mpnet-base-v2)
- **Distance Metric**: Cosine Similarity
- **Sharding**: Single shard (10K+ trades supported)
- **Replication**: Enabled for production

### 3. Embedding Model: Hugging Face

#### Model: `sentence-transformers/all-mpnet-base-v2`
- **Dimensions**: 768
- **Context Length**: 384 tokens
- **Performance**: 50ms inference on HF API
- **Cost**: Free tier (30K chars/day)

**Alternative**: `ProsusAI/finbert` for financial sentiment
- Specialized for financial text
- Better at understanding options terminology
- Trade-off: Smaller context window

### 4. LLM: Claude Sonnet 4.5

#### Model Configuration
- **Model**: claude-sonnet-4-5-20250929
- **Max Tokens**: 4096 (input) + 2048 (output)
- **Temperature**: 0.3 (consistent reasoning)
- **Top P**: 0.9

#### Why Claude?
- Superior reasoning for financial analysis
- Large context window (200K tokens)
- Structured output support
- Cost-effective ($3/M input tokens)

## Detailed Design Specifications

### Component 1: Embedding Pipeline

**Purpose**: Convert trade alerts into semantic vectors that capture strategy intent, market conditions, and risk profile.

**What to Embed**:
```python
# Composite text representation
trade_text = f"""
Strategy: {strategy}
Ticker: {ticker} ({sector})
Action: {action}
Strike: ${strike} (Delta: {delta})
Expiration: {expiration} (DTE: {dte})
Premium: ${premium} (IV Rank: {iv_rank})
Market Conditions: VIX={vix}, Sector Trend={sector_trend}
Trade Thesis: {alert_text}
"""
```

**Metadata to Store** (for filtering):
```json
{
  "ticker": "AAPL",
  "strategy": "CSP",
  "strike": 170.0,
  "expiration_date": "2024-12-20",
  "dte": 30,
  "premium": 2.50,
  "action": "BTO",
  "sector": "Technology",
  "vix_at_entry": 15.2,
  "iv_rank": 45,
  "profile_username": "behappy",
  "pnl": 180.0,
  "pnl_percent": 75.0,
  "status": "closed",
  "win": true,
  "entry_date": "2024-11-01T10:30:00Z",
  "exit_date": "2024-11-15T16:00:00Z"
}
```

**Implementation**:
```python
import os
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

# Initialize
model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
qdrant_client = QdrantClient(
    url="https://your-cluster.qdrant.io",
    api_key=os.getenv('QDRANT_API_KEY')
)

# Create collection
qdrant_client.create_collection(
    collection_name="options_trades",
    vectors_config=VectorParams(size=768, distance=Distance.COSINE),
)
```

### Component 2: Similarity Search Algorithm

**Query Strategy**: Hybrid search combining dense vectors + metadata filters

**Step 1: Pre-filter** (reduce search space)
```python
from qdrant_client.models import Filter, FieldCondition, MatchValue, Range

filters = Filter(
    must=[
        # Same ticker or sector
        FieldCondition(
            key="ticker",
            match=MatchValue(value=new_alert.ticker)
        ),
        # Same strategy
        FieldCondition(
            key="strategy",
            match=MatchValue(value=new_alert.strategy)
        ),
        # Only closed trades (with outcomes)
        FieldCondition(
            key="status",
            match=MatchValue(value="closed")
        ),
        # Similar DTE (+/- 7 days)
        FieldCondition(
            key="dte",
            range=Range(
                gte=new_alert.dte - 7,
                lte=new_alert.dte + 7
            )
        ),
        # Similar market volatility regime
        FieldCondition(
            key="vix_at_entry",
            range=Range(
                gte=current_vix - 5,
                lte=current_vix + 5
            )
        )
    ]
)
```

**Step 2: Vector search**
```python
search_results = qdrant_client.search(
    collection_name="options_trades",
    query_vector=new_alert_embedding,
    query_filter=filters,
    limit=10,  # Retrieve top-10
    score_threshold=0.7  # Minimum similarity
)
```

**Step 3: Re-ranking**
```python
def rerank_results(results, weights):
    """
    Re-rank by multiple factors:
    - Similarity score (50%)
    - Recency (25% - recent trades more relevant)
    - Outcome quality (25% - high P&L trades weighted higher)
    """
    for result in results:
        days_old = (datetime.now() - result.payload['entry_date']).days
        recency_score = max(0, 1 - (days_old / 365))  # Decay over 1 year

        outcome_score = result.payload['pnl_percent'] / 100  # Normalize

        combined_score = (
            result.score * weights['similarity'] +
            recency_score * weights['recency'] +
            outcome_score * weights['outcome']
        )
        result.combined_score = combined_score

    return sorted(results, key=lambda x: x.combined_score, reverse=True)[:5]
```

**Top-k Selection**: 5 most relevant trades
- Provides diverse examples
- Fits within Claude's context window
- Balances quality vs quantity

### Component 3: Context Assembly

**Template Structure**:
```python
context_template = """
You are an expert options trading advisor analyzing a new trade alert.

## NEW ALERT
{new_alert_details}

## HISTORICAL SIMILAR TRADES
I found {num_similar} similar trades in your history:

{historical_trades_formatted}

## AGGREGATE STATISTICS
- Win Rate: {win_rate}%
- Average P&L: ${avg_pnl}
- Best Trade: ${best_trade} (+{best_pct}%)
- Worst Trade: ${worst_trade} ({worst_pct}%)
- Average Hold Time: {avg_hold_days} days

## CURRENT MARKET CONDITIONS
- {ticker} Price: ${current_price}
- VIX: {vix}
- Sector Performance: {sector_perf}
- IV Rank: {iv_rank}/100

## YOUR TASK
Based on the historical evidence and current market conditions, provide a recommendation.

Output Format (JSON):
{{
  "recommendation": "TAKE" | "PASS" | "MONITOR",
  "confidence": 0-100,
  "reasoning": "Why this recommendation based on historical patterns",
  "historical_evidence": ["Trade 1 outcome", "Trade 2 outcome", ...],
  "risk_factors": ["Factor 1", "Factor 2", ...],
  "suggested_adjustments": "Optional modifications to improve probability"
}}
"""
```

**Historical Trade Formatting**:
```python
def format_historical_trade(trade):
    return f"""
Trade #{trade.id} ({trade.entry_date.strftime('%Y-%m-%d')}):
  Ticker: {trade.ticker}
  Strategy: {trade.strategy}
  Strike: ${trade.strike} (DTE: {trade.dte})
  Premium: ${trade.premium}
  Market Conditions: VIX={trade.vix_at_entry}, IV Rank={trade.iv_rank}
  Outcome: {trade.status} - P&L: ${trade.pnl} ({trade.pnl_percent:+.1f}%)
  Hold Time: {(trade.exit_date - trade.entry_date).days} days
  Similarity: {trade.similarity_score:.2%}
"""
```

### Component 4: LLM Integration

**API Configuration**:
```python
import anthropic

client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

def get_recommendation(context):
    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=2048,
        temperature=0.3,
        system="""You are an expert options trading advisor.
        You analyze trade alerts by comparing them to historical outcomes.
        You always provide evidence-based recommendations with clear reasoning.
        You identify risks and suggest adjustments to improve probability of success.""",
        messages=[
            {"role": "user", "content": context}
        ]
    )

    return parse_recommendation(response.content[0].text)
```

**Structured Output Parsing**:
```python
import json
import re

def parse_recommendation(llm_output):
    """
    Parse LLM response into structured format.
    Handles both JSON and natural language responses.
    """
    # Try JSON parsing first
    try:
        json_match = re.search(r'\{.*\}', llm_output, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
    except:
        pass

    # Fallback: Extract key information with regex
    recommendation = {
        "recommendation": extract_decision(llm_output),
        "confidence": extract_confidence(llm_output),
        "reasoning": extract_reasoning(llm_output),
        "historical_evidence": extract_evidence(llm_output),
        "risk_factors": extract_risks(llm_output),
        "suggested_adjustments": extract_adjustments(llm_output)
    }

    return recommendation
```

### Component 5: Feedback Loop

**Trade Outcome Tracking**:
```sql
-- New table: xtrades_recommendations
CREATE TABLE xtrades_recommendations (
    id SERIAL PRIMARY KEY,
    trade_id INTEGER REFERENCES xtrades_trades(id),
    recommendation VARCHAR(20) NOT NULL,  -- 'TAKE', 'PASS', 'MONITOR'
    confidence INTEGER NOT NULL,  -- 0-100
    reasoning TEXT,
    historical_evidence JSONB,  -- Array of similar trade IDs
    risk_factors JSONB,
    suggested_adjustments TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Outcome tracking (filled after trade closes)
    actual_outcome VARCHAR(20),  -- 'WIN', 'LOSS', 'BREAK_EVEN'
    actual_pnl DECIMAL(10,2),
    actual_pnl_percent DECIMAL(10,2),
    recommendation_correct BOOLEAN,

    CONSTRAINT chk_recommendation CHECK (recommendation IN ('TAKE', 'PASS', 'MONITOR'))
);

-- Index for performance analysis
CREATE INDEX idx_recommendations_outcome ON xtrades_recommendations(recommendation, recommendation_correct);
```

**Learning Mechanism**:
```python
def update_learning_weights(recommendation_id):
    """
    After trade closes, analyze recommendation accuracy
    and adjust re-ranking weights accordingly.
    """
    rec = get_recommendation_by_id(recommendation_id)
    trade = get_trade_by_id(rec.trade_id)

    # Calculate accuracy
    was_correct = (
        (rec.recommendation == 'TAKE' and trade.pnl > 0) or
        (rec.recommendation == 'PASS' and trade.pnl <= 0)
    )

    # Update database
    update_recommendation_outcome(recommendation_id, {
        'actual_outcome': 'WIN' if trade.pnl > 0 else 'LOSS',
        'actual_pnl': trade.pnl,
        'actual_pnl_percent': trade.pnl_percent,
        'recommendation_correct': was_correct
    })

    # Analyze similar trades used for recommendation
    similar_trade_ids = rec.historical_evidence
    for similar_id in similar_trade_ids:
        if was_correct:
            # Boost this trade's weight in future searches
            increment_trade_success_weight(similar_id)
        else:
            # Reduce this trade's weight
            decrement_trade_success_weight(similar_id)
```

**Performance Metrics Dashboard**:
```python
def calculate_rag_performance():
    """
    Calculate RAG system performance metrics
    """
    query = """
    SELECT
        recommendation,
        COUNT(*) as total,
        SUM(CASE WHEN recommendation_correct THEN 1 ELSE 0 END) as correct,
        AVG(confidence) as avg_confidence,
        AVG(actual_pnl) as avg_pnl
    FROM xtrades_recommendations
    WHERE actual_outcome IS NOT NULL
    GROUP BY recommendation
    """

    return {
        'accuracy_by_decision': db.execute(query).fetchall(),
        'confidence_calibration': calculate_calibration(),
        'pnl_impact': calculate_pnl_impact(),
        'false_positives': calculate_false_positives(),
        'false_negatives': calculate_false_negatives()
    }
```

## Performance Optimization

### Query Latency Targets
- **Embedding Generation**: 50-100ms (HuggingFace API)
- **Vector Search**: 50-200ms (Qdrant)
- **LLM Inference**: 1-2s (Claude Sonnet 4.5)
- **Total Latency**: < 2.5 seconds

### Optimization Strategies

#### 1. Caching
```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=1000)
def get_embedding(text):
    """Cache embeddings for repeated queries"""
    return model.encode(text)

def cache_key(alert):
    """Generate cache key from alert parameters"""
    return hashlib.md5(
        f"{alert.ticker}_{alert.strategy}_{alert.strike}_{alert.dte}".encode()
    ).hexdigest()
```

#### 2. Batch Processing
```python
def process_alerts_batch(alerts):
    """Process multiple alerts in single batch"""
    # Batch embed
    texts = [format_trade_for_embedding(a) for a in alerts]
    embeddings = model.encode(texts, batch_size=32)

    # Batch search
    results = qdrant_client.search_batch(
        collection_name="options_trades",
        requests=[
            SearchRequest(query_vector=emb, limit=10)
            for emb in embeddings
        ]
    )

    return results
```

#### 3. Index Optimization
```python
# Create payload indexes in Qdrant for faster filtering
qdrant_client.create_payload_index(
    collection_name="options_trades",
    field_name="ticker",
    field_type="keyword"
)

qdrant_client.create_payload_index(
    collection_name="options_trades",
    field_name="strategy",
    field_type="keyword"
)

qdrant_client.create_payload_index(
    collection_name="options_trades",
    field_name="dte",
    field_type="integer"
)
```

### Scalability Considerations

**Current Scale**: 10,000+ trades
**Target Scale**: 100,000+ trades
**Query Rate**: 100 queries/day

**Scaling Strategy**:
1. Use Qdrant Cloud for horizontal scaling
2. Implement query result caching (Redis)
3. Batch similar queries
4. Async processing for non-critical recommendations

## Cost Analysis

### Monthly Costs (10K trades, 100 queries/day)

**Qdrant Cloud**:
- Free tier: 1GB storage, 1M API calls/month
- Current: FREE
- Scale-up: $25/month (Pro tier) at 50K trades

**Hugging Face API**:
- Free tier: 30K chars/day
- Current: FREE
- Scale-up: $9/month (Pro tier) at 1M chars/month

**Claude Sonnet 4.5**:
- Input: $3/M tokens
- Output: $15/M tokens
- Current: ~$15/month (100 queries/day x 5K tokens/query x 30 days)
- Scale-up: Linear with query volume

**Total Monthly Cost**: $15-40 depending on scale

### Cost Optimization

**Strategy 1**: Cache LLM responses for similar alerts
```python
def get_cached_recommendation(alert, similar_trades):
    cache_key = generate_cache_key(alert, similar_trades)
    cached = redis.get(f"rec:{cache_key}")
    if cached:
        return json.loads(cached)

    recommendation = get_llm_recommendation(alert, similar_trades)
    redis.setex(f"rec:{cache_key}", 3600, json.dumps(recommendation))
    return recommendation
```

**Strategy 2**: Use smaller LLM for simple cases
```python
def should_use_full_rag(alert):
    """
    Use full RAG for complex/new scenarios
    Use simple rules for obvious cases
    """
    # Use simple rules if:
    # - Ticker has 50+ historical trades with clear pattern
    # - Strategy is common (CSP, CC)
    # - Market conditions are normal

    if (
        get_ticker_trade_count(alert.ticker) > 50 and
        alert.strategy in ['CSP', 'CC'] and
        10 < current_vix < 25
    ):
        return False  # Use simple heuristic

    return True  # Use full RAG
```

## Deployment Strategy

### Phase 1: Initial Setup (Week 1)
1. Create Qdrant collection
2. Backfill historical trades from PostgreSQL
3. Test embedding pipeline
4. Validate vector search quality

### Phase 2: Integration (Week 2)
1. Build RAG query pipeline
2. Integrate with Claude API
3. Create recommendation storage
4. Test end-to-end flow

### Phase 3: Feedback Loop (Week 3)
1. Implement outcome tracking
2. Build performance dashboard
3. Add learning mechanism
4. Monitor accuracy

### Phase 4: Production (Week 4)
1. Deploy to production
2. Enable for live alerts
3. Monitor performance
4. Iterate based on feedback

## Monitoring & Observability

### Key Metrics

**System Health**:
- Query latency (p50, p95, p99)
- Embedding generation time
- Vector search time
- LLM inference time
- Error rate

**Business Metrics**:
- Recommendation accuracy
- Win rate by recommendation type
- Average P&L by recommendation
- False positive rate
- False negative rate

**Data Quality**:
- Vector search recall
- Embedding quality score
- Context relevance score
- LLM response quality

### Alerting Rules

```python
# Alert if accuracy drops below 65%
if accuracy < 0.65:
    send_alert("RAG accuracy below threshold")

# Alert if latency exceeds 5s
if p95_latency > 5000:
    send_alert("RAG latency degraded")

# Alert if error rate > 5%
if error_rate > 0.05:
    send_alert("RAG error rate elevated")
```

## Security & Privacy

### API Key Management
- Store all API keys in environment variables
- Rotate keys quarterly
- Use separate keys for dev/prod
- Monitor API usage for anomalies

### Data Privacy
- No PII in embeddings
- Anonymize trader usernames in logs
- Encrypt sensitive data at rest
- HTTPS for all API calls

### Access Control
- Require authentication for RAG API
- Rate limiting (100 queries/day/user)
- IP whitelisting for production
- Audit log all recommendations

## Testing Strategy

### Unit Tests
```python
def test_embedding_generation():
    alert = create_test_alert()
    embedding = generate_embedding(alert)
    assert len(embedding) == 768
    assert -1 <= min(embedding) <= 1

def test_similarity_search():
    results = search_similar_trades(test_alert, limit=5)
    assert len(results) <= 5
    assert all(r.score >= 0.7 for r in results)

def test_recommendation_parsing():
    llm_output = get_test_llm_response()
    rec = parse_recommendation(llm_output)
    assert rec['recommendation'] in ['TAKE', 'PASS', 'MONITOR']
    assert 0 <= rec['confidence'] <= 100
```

### Integration Tests
```python
def test_end_to_end_rag():
    # Create test alert
    alert = {
        'ticker': 'AAPL',
        'strategy': 'CSP',
        'strike': 170,
        'dte': 30,
        'premium': 2.50
    }

    # Get recommendation
    recommendation = rag_system.get_recommendation(alert)

    # Validate
    assert recommendation is not None
    assert 'reasoning' in recommendation
    assert len(recommendation['historical_evidence']) > 0
```

### Performance Tests
```python
def test_latency_sla():
    start = time.time()
    recommendation = rag_system.get_recommendation(test_alert)
    latency = time.time() - start

    assert latency < 2.5, f"Latency {latency}s exceeds SLA"
```

## Conclusion

This RAG architecture provides a production-ready system for learning from historical options trades and generating intelligent recommendations. The system is:

- **Scalable**: Supports 100K+ trades with sub-2s latency
- **Accurate**: Learns from actual outcomes to improve over time
- **Cost-effective**: $15-40/month at target scale
- **Observable**: Full metrics and alerting
- **Maintainable**: Clean separation of concerns, well-tested

The architecture leverages your existing infrastructure (PostgreSQL, Xtrades data) and integrates seamlessly with your current workflow. The feedback loop ensures continuous improvement as more trades are executed and outcomes are tracked.

**Next Steps**: See implementation files for code-level details.
