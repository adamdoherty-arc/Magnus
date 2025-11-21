# RAG System Code Structure

## Directory Structure

```
WheelStrategy/
├── src/
│   ├── rag/
│   │   ├── __init__.py                      # Package initialization
│   │   ├── embedding_pipeline.py            # Convert trades to vectors
│   │   ├── rag_query_engine.py              # Core RAG query logic
│   │   ├── recommendation_tracker.py        # Track outcomes & learning
│   │   ├── xtrades_rag_integration.py       # Integration with Xtrades scraper
│   │   ├── qdrant_schema.json               # Qdrant collection schema
│   │   └── recommendation_tracker.sql       # PostgreSQL schema
│   │
│   ├── xtrades_db_manager.py                # Database CRUD operations
│   ├── xtrades_scraper.py                   # Scrape Xtrades alerts
│   └── xtrades_schema.sql                   # Existing Xtrades schema
│
├── docs/
│   └── rag/
│       ├── RAG_ARCHITECTURE.md              # Full architecture document
│       ├── SETUP_GUIDE.md                   # Step-by-step setup instructions
│       ├── EXAMPLE_PROMPTS.md               # Example LLM prompts & responses
│       └── CODE_STRUCTURE.md                # This file
│
├── tests/
│   ├── test_embedding_pipeline.py           # Unit tests for embeddings
│   ├── test_rag_query_engine.py             # Unit tests for RAG queries
│   └── test_recommendation_tracker.py       # Unit tests for tracking
│
├── .env                                      # Environment variables (API keys)
├── requirements.txt                          # Python dependencies
└── README.md                                 # Project README
```

## Core Modules

### 1. embedding_pipeline.py

**Purpose**: Convert historical trades into vector embeddings for similarity search

**Key Classes**:
```python
class TradeEmbeddingPipeline:
    """Pipeline for converting trades to vector embeddings"""

    def __init__(self, embedding_model, qdrant_url, qdrant_api_key)
        # Initialize embedding model and Qdrant client

    def create_collection(self, recreate=False)
        # Create Qdrant collection with proper schema

    def load_trades_from_db(self, status, limit, min_date)
        # Load trades from PostgreSQL

    def enrich_trade_with_market_data(self, trade)
        # Add market data (VIX, sector, etc.)

    def format_trade_for_embedding(self, trade)
        # Format trade into text for embedding

    def generate_embedding(self, text)
        # Generate vector embedding using Hugging Face model

    def create_point(self, trade)
        # Create Qdrant point (vector + metadata)

    def index_trades(self, trades, batch_size)
        # Batch insert trades into Qdrant

    def backfill_from_database(self, recreate_collection, limit)
        # Complete backfill workflow
```

**Key Methods**:
- `backfill_from_database()`: Main entry point for populating Qdrant
- `enrich_trade_with_market_data()`: Fetch VIX, sector, price data
- `format_trade_for_embedding()`: Create composite text representation
- `generate_embedding()`: Call Hugging Face model

**Dependencies**:
- `sentence-transformers`: Embedding model
- `qdrant-client`: Vector database client
- `psycopg2`: PostgreSQL connection
- `yfinance`: Market data

**Usage**:
```python
from rag.embedding_pipeline import TradeEmbeddingPipeline

pipeline = TradeEmbeddingPipeline()
pipeline.backfill_from_database(recreate_collection=True)
```

---

### 2. rag_query_engine.py

**Purpose**: Query Qdrant for similar trades and generate LLM recommendations

**Key Classes**:
```python
class RAGQueryEngine:
    """RAG-powered query engine for options trading recommendations"""

    def __init__(self, embedding_model, qdrant_url, qdrant_api_key, anthropic_api_key)
        # Initialize all clients

    def format_alert_for_embedding(self, alert)
        # Format new alert for embedding

    def build_search_filters(self, alert)
        # Create Qdrant filters (ticker, strategy, DTE, VIX)

    def search_similar_trades(self, alert, limit, score_threshold)
        # Vector search in Qdrant

    def rerank_trades(self, trades, top_k)
        # Re-rank by similarity + recency + outcome

    def calculate_statistics(self, trades)
        # Compute win rate, avg P&L, etc.

    def format_trade_for_context(self, trade, index)
        # Format trade for LLM context

    def build_prompt(self, alert, similar_trades, stats)
        # Construct full prompt for Claude

    def parse_claude_response(self, response_text)
        # Parse JSON from Claude's response

    def get_recommendation(self, alert, temperature, max_tokens)
        # Complete RAG workflow → recommendation
```

**Key Methods**:
- `get_recommendation()`: Main entry point - returns recommendation dict
- `search_similar_trades()`: Query Qdrant with filters
- `rerank_trades()`: Apply weighted re-ranking
- `build_prompt()`: Assemble context for LLM

**Dependencies**:
- `qdrant-client`: Vector search
- `anthropic`: Claude API
- `sentence-transformers`: Embedding generation

**Usage**:
```python
from rag.rag_query_engine import RAGQueryEngine

engine = RAGQueryEngine()
recommendation = engine.get_recommendation(alert)
print(recommendation['recommendation'])  # TAKE/PASS/MONITOR
```

---

### 3. recommendation_tracker.py

**Purpose**: Store recommendations and track outcomes for learning

**Key Classes**:
```python
class RecommendationTracker:
    """Tracks RAG recommendations and learns from outcomes"""

    def __init__(self)
        # Initialize database connection

    def store_recommendation(self, trade_id, recommendation, query_latency_ms)
        # Insert recommendation into PostgreSQL

    def update_outcome(self, recommendation_id, trade)
        # Update with actual trade outcome

    def _is_recommendation_correct(self, recommendation, actual_outcome, pnl)
        # Determine if rec was correct

    def _update_learning_weights(self, recommendation_id, conn)
        # Call PostgreSQL function to update weights

    def get_recommendation_by_trade_id(self, trade_id)
        # Fetch recommendation for specific trade

    def get_performance_metrics(self, days)
        # Calculate system-wide performance

    def get_accuracy_by_recommendation(self)
        # Accuracy breakdown (TAKE/PASS/MONITOR)

    def get_confidence_calibration(self)
        # Confidence vs actual accuracy

    def get_top_learning_trades(self, limit)
        # Best trades for learning

    def print_performance_report(self, days)
        # Human-readable performance report
```

**Key Methods**:
- `store_recommendation()`: Save RAG output to database
- `update_outcome()`: Link recommendation to trade result
- `get_performance_metrics()`: System accuracy, P&L impact
- `print_performance_report()`: Dashboard-style output

**Dependencies**:
- `psycopg2`: PostgreSQL connection

**Usage**:
```python
from rag.recommendation_tracker import RecommendationTracker

tracker = RecommendationTracker()
rec_id = tracker.store_recommendation(trade_id, recommendation)
tracker.update_outcome(rec_id, trade)
tracker.print_performance_report(days=30)
```

---

### 4. xtrades_rag_integration.py

**Purpose**: Integrate RAG with Xtrades scraper for automated workflow

**Key Functions**:
```python
def enrich_alert_with_market_data(alert):
    """Add current market data (price, VIX, IV) to alert"""
    # Fetch from Yahoo Finance
    # Return enriched alert

def process_new_alerts():
    """
    Main workflow:
    1. Query database for new alerts (no recommendation yet)
    2. Enrich each alert with market data
    3. Get RAG recommendation
    4. Store recommendation in database
    """
    # Load unprocessed alerts
    # For each alert:
    #   - Enrich with market data
    #   - Get RAG recommendation
    #   - Store in database
    #   - Log results
```

**Usage**:
```python
# Run manually
python src/rag/xtrades_rag_integration.py

# Or schedule (Windows Task Scheduler)
# Task: Run daily at 9:00 AM
```

---

## Database Schema

### PostgreSQL Tables

#### xtrades_recommendations
Stores RAG recommendations for trades
```sql
CREATE TABLE xtrades_recommendations (
    id SERIAL PRIMARY KEY,
    trade_id INTEGER REFERENCES xtrades_trades(id),
    recommendation VARCHAR(20),  -- TAKE/PASS/MONITOR
    confidence INTEGER,
    reasoning TEXT,
    historical_evidence JSONB,
    risk_factors JSONB,
    suggested_adjustments TEXT,
    similar_trades_found INTEGER,
    statistics JSONB,
    created_at TIMESTAMP WITH TIME ZONE,

    -- Outcome tracking
    actual_outcome VARCHAR(20),  -- WIN/LOSS/BREAK_EVEN
    actual_pnl DECIMAL(10,2),
    recommendation_correct BOOLEAN,
    outcome_recorded_at TIMESTAMP WITH TIME ZONE
);
```

#### xtrades_rag_performance
Aggregated performance metrics
```sql
CREATE TABLE xtrades_rag_performance (
    id SERIAL PRIMARY KEY,
    calculated_at TIMESTAMP WITH TIME ZONE,
    overall_accuracy DECIMAL(5,2),
    take_accuracy DECIMAL(5,2),
    pass_accuracy DECIMAL(5,2),
    high_confidence_accuracy DECIMAL(5,2),
    avg_pnl_per_take DECIMAL(10,2),
    false_positives INTEGER,
    false_negatives INTEGER,
    period_start TIMESTAMP WITH TIME ZONE,
    period_end TIMESTAMP WITH TIME ZONE
);
```

#### xtrades_rag_learning_weights
Learning weights for individual trades
```sql
CREATE TABLE xtrades_rag_learning_weights (
    trade_id INTEGER PRIMARY KEY,
    success_weight DECIMAL(5,2),  -- 0.1 to 5.0
    times_referenced INTEGER,
    recommendations_correct INTEGER,
    accuracy_rate DECIMAL(5,2),
    updated_at TIMESTAMP WITH TIME ZONE
);
```

### PostgreSQL Views

```sql
-- Accuracy by recommendation type
CREATE VIEW v_rag_accuracy_by_recommendation AS
SELECT recommendation, COUNT(*) as total, accuracy_pct
FROM xtrades_recommendations
GROUP BY recommendation;

-- Confidence calibration
CREATE VIEW v_rag_confidence_calibration AS
SELECT confidence_band, actual_accuracy
FROM xtrades_recommendations
GROUP BY confidence_band;

-- Top learning trades
CREATE VIEW v_rag_top_learning_trades AS
SELECT trade_id, ticker, accuracy_rate, success_weight
FROM xtrades_rag_learning_weights
WHERE times_referenced >= 3
ORDER BY accuracy_rate DESC;
```

### PostgreSQL Functions

```sql
-- Update learning weights after outcome
CREATE FUNCTION update_rag_learning_weights(recommendation_id INTEGER)
RETURNS VOID;

-- Calculate performance metrics
CREATE FUNCTION calculate_rag_performance(days_back INTEGER)
RETURNS INTEGER;
```

---

## Qdrant Schema

### Collection: options_trades

**Vector Config**:
- Size: 768 dimensions
- Distance: Cosine similarity

**Payload Schema**:
```json
{
  "trade_id": 12345,
  "ticker": "AAPL",
  "strategy": "CSP",
  "strike_price": 170.0,
  "dte": 30,
  "vix_at_entry": 15.2,
  "pnl": 180.0,
  "pnl_percent": 75.0,
  "win": true,
  "entry_date": "2024-11-01T10:30:00Z",
  "sector": "Technology",
  "success_weight": 1.0,
  ...
}
```

**Indexes**:
- `ticker` (keyword)
- `strategy` (keyword)
- `status` (keyword)
- `dte` (integer, range)
- `vix_at_entry` (float, range)
- `win` (bool)
- `entry_date` (datetime)

---

## Data Flow

### 1. Backfill Historical Trades
```
PostgreSQL → Load trades → Enrich market data → Generate embeddings → Qdrant
   (xtrades_trades)                                                    (options_trades)
```

### 2. New Alert Processing
```
Xtrades Scraper → PostgreSQL → Enrich → Generate embedding → Qdrant search
                  (new trade)                                  ↓
                                                         Similar trades
                                                               ↓
                                                   Re-rank & select top-5
                                                               ↓
                                                    Build context prompt
                                                               ↓
                                                       Claude Sonnet 4.5
                                                               ↓
                                                        Recommendation
                                                               ↓
                                            PostgreSQL (xtrades_recommendations)
```

### 3. Outcome Tracking & Learning
```
Trade closes → Update PostgreSQL → Calculate outcome correctness
   (xtrades_trades)        ↓
                    Update recommendation
              (xtrades_recommendations.actual_outcome)
                           ↓
                 Call update_rag_learning_weights()
                           ↓
           Update weights for similar trades
      (xtrades_rag_learning_weights.success_weight)
                           ↓
              Future recommendations improved
```

---

## Key Algorithms

### 1. Re-ranking Algorithm
```python
combined_score = (
    similarity_score * 0.5 +        # How similar (cosine distance)
    recency_score * 0.25 +          # How recent (decay over 1 year)
    outcome_score * 0.25            # How profitable (P&L %)
)
```

### 2. Recommendation Correctness
```python
if recommendation == 'TAKE':
    correct = (actual_pnl > 0)
elif recommendation == 'PASS':
    correct = (actual_pnl <= 0)
else:  # MONITOR
    correct = True  # Neutral recommendation
```

### 3. Learning Weight Update
```python
if recommendation_correct:
    success_weight = min(success_weight + 0.1, 5.0)  # Boost
else:
    success_weight = max(success_weight - 0.1, 0.1)  # Reduce
```

---

## Configuration

### Environment Variables (.env)

```bash
# PostgreSQL
DB_HOST=localhost
DB_PORT=5432
DB_NAME=magnus
DB_USER=postgres
DB_PASSWORD=postgres123!

# Qdrant
QDRANT_URL=https://your-cluster.qdrant.io:6333
QDRANT_API_KEY=your_qdrant_key

# Anthropic Claude
ANTHROPIC_API_KEY=your_anthropic_key

# Hugging Face (optional for API-based embeddings)
HUGGINGFACE_API_KEY=your_hf_key
```

### Model Configuration

**Embedding Model**: `sentence-transformers/all-mpnet-base-v2`
- Dimensions: 768
- Context: 384 tokens
- Speed: ~50ms per embedding

**LLM**: `claude-sonnet-4-5-20250929`
- Max tokens: 4096 input, 2048 output
- Temperature: 0.3 (consistent reasoning)
- Cost: $3/M input tokens

### Search Parameters

```python
SEARCH_PARAMS = {
    'limit': 10,                    # Retrieve top-10 similar trades
    'score_threshold': 0.7,         # Minimum similarity (70%)
    'top_k_rerank': 5,              # Select top-5 after re-ranking
}

RERANK_WEIGHTS = {
    'similarity': 0.5,              # Vector similarity importance
    'recency': 0.25,                # Recent trades more relevant
    'outcome': 0.25,                # Profitable trades weighted higher
}

LLM_PARAMS = {
    'temperature': 0.3,             # Lower = more consistent
    'max_tokens': 2048,             # Output length
}
```

---

## Testing

### Unit Tests

```python
# tests/test_embedding_pipeline.py
def test_embedding_generation():
    assert len(embedding) == 768
    assert -1 <= min(embedding) <= 1

def test_trade_enrichment():
    enriched = pipeline.enrich_trade_with_market_data(trade)
    assert enriched['vix_at_entry'] is not None
    assert enriched['sector'] is not None

# tests/test_rag_query_engine.py
def test_similarity_search():
    results = engine.search_similar_trades(alert, limit=5)
    assert len(results) <= 5
    assert all(r['similarity_score'] >= 0.7 for r in results)

def test_recommendation_format():
    rec = engine.get_recommendation(alert)
    assert rec['recommendation'] in ['TAKE', 'PASS', 'MONITOR']
    assert 0 <= rec['confidence'] <= 100

# tests/test_recommendation_tracker.py
def test_store_recommendation():
    rec_id = tracker.store_recommendation(trade_id, recommendation)
    assert rec_id > 0

def test_outcome_update():
    success = tracker.update_outcome(rec_id, trade)
    assert success == True
```

### Integration Tests

```python
def test_end_to_end_workflow():
    """Test complete RAG workflow"""
    # 1. Backfill
    pipeline.backfill_from_database(limit=10)

    # 2. Query
    recommendation = engine.get_recommendation(test_alert)

    # 3. Store
    rec_id = tracker.store_recommendation(trade_id, recommendation)

    # 4. Update outcome
    tracker.update_outcome(rec_id, closed_trade)

    # 5. Check learning
    weights = tracker.get_top_learning_trades()
    assert len(weights) > 0
```

---

## Performance Metrics

### Query Performance
- Embedding generation: 50-100ms
- Qdrant search: 50-200ms
- LLM inference: 1-2s
- **Total latency**: < 2.5s (target)

### Accuracy Targets
- Overall accuracy: > 65%
- High confidence accuracy (80-100%): > 80%
- TAKE recommendation accuracy: > 70%
- PASS recommendation accuracy: > 65%

### Scalability
- Current: 10,000 trades in Qdrant
- Target: 100,000+ trades
- Query rate: 100 queries/day
- Batch size: 100 trades per insert

---

## Deployment Checklist

- [ ] Install dependencies (`pip install -r requirements.txt`)
- [ ] Set up PostgreSQL schema (`recommendation_tracker.sql`)
- [ ] Configure Qdrant Cloud account
- [ ] Set environment variables (`.env`)
- [ ] Backfill historical trades (`embedding_pipeline.py`)
- [ ] Test RAG query (`rag_query_engine.py`)
- [ ] Test recommendation storage (`recommendation_tracker.py`)
- [ ] Set up automated processing (Task Scheduler)
- [ ] Configure monitoring and alerts
- [ ] Review performance report weekly

---

## Maintenance

### Weekly Tasks
- Review performance report (`tracker.print_performance_report(7)`)
- Check for degraded accuracy (alert if < 60%)
- Review top/bottom learning trades
- Update search parameters if needed

### Monthly Tasks
- Calculate full performance metrics (30 days)
- Review false positives/negatives
- Adjust re-ranking weights based on performance
- Backup Qdrant collection
- Archive old recommendations

### Quarterly Tasks
- Re-backfill Qdrant with all historical data
- Audit learning weights for outliers
- Upgrade embedding model if better alternatives available
- Review and update LLM prompts
- Cost analysis and optimization

---

## Troubleshooting

### Issue: High latency (>5s)
- Check Qdrant query time (may need more indexes)
- Reduce `limit` parameter (10 → 5)
- Cache frequent embeddings
- Use local Qdrant for development

### Issue: Low accuracy (<60%)
- Review false positives/negatives
- Adjust score threshold (0.7 → 0.75)
- Modify re-ranking weights
- Improve prompt engineering
- Filter by more specific conditions

### Issue: "No similar trades found"
- Lower score threshold (0.7 → 0.6)
- Broaden search filters (remove VIX filter)
- Ensure backfill completed successfully
- Check Qdrant collection size

---

## Future Enhancements

### Phase 2
- Real-time market data integration
- Options Greeks calculation (delta, theta, vega)
- Historical IV rank tracking
- Earnings calendar integration

### Phase 3
- Multi-strategy portfolio optimization
- Risk-adjusted position sizing
- Backtesting framework
- A/B testing of prompt variants

### Phase 4
- Web dashboard (Streamlit)
- Telegram bot notifications
- Mobile app integration
- Real-time trade monitoring

---

## Resources

- Architecture: `docs/rag/RAG_ARCHITECTURE.md`
- Setup Guide: `docs/rag/SETUP_GUIDE.md`
- Example Prompts: `docs/rag/EXAMPLE_PROMPTS.md`
- Qdrant Docs: https://qdrant.tech/documentation/
- Claude API: https://docs.anthropic.com/
- Sentence Transformers: https://www.sbert.net/
