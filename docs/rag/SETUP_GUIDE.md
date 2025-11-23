# RAG System Setup Guide

## Quick Start (5 Minutes)

This guide will get your RAG system up and running in 5 minutes.

## Prerequisites

- PostgreSQL database (`magnus`) with Xtrades data
- Python 3.8+ with pip
- API keys (already in `.env`):
  - `QDRANT_API_KEY`: Your Qdrant Cloud API key
  - `ANTHROPIC_API_KEY`: Your Claude API key
  - `HUGGINGFACE_API_KEY`: Your HuggingFace API key (optional for local models)

## Step 1: Install Dependencies

```bash
cd c:\Code\WheelStrategy

# Install required packages
pip install sentence-transformers qdrant-client anthropic psycopg2-binary yfinance python-dotenv
```

## Step 2: Set Up Database Schema

```bash
# Run the recommendation tracking schema
psql -U postgres -d magnus -f src\rag\recommendation_tracker.sql
```

Or from Python:
```python
import psycopg2
from pathlib import Path

# Connect to database
conn = psycopg2.connect(
    host='localhost',
    database='magnus',
    user='postgres',
    password='postgres123!'
)

# Run schema file
schema_path = Path('src/rag/recommendation_tracker.sql')
with open(schema_path) as f:
    sql = f.read()
    conn.cursor().execute(sql)
    conn.commit()

print("Schema created successfully!")
```

## Step 3: Set Up Qdrant Cloud

### Option A: Using Qdrant Cloud (Recommended)

1. Go to https://cloud.qdrant.io/
2. Sign up for free account (1GB storage, 1M API calls/month)
3. Create a new cluster:
   - Name: `options-trades`
   - Region: Closest to your location
   - Size: Free tier
4. Copy your API key (already in your `.env`)
5. Copy your cluster URL

Update `.env`:
```bash
QDRANT_URL=https://your-cluster-id.us-east.aws.cloud.qdrant.io:6333
QDRANT_API_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.GwGL6bGqMFnSqrRHeHXCDqsJtBxNlq2Bx1Ri2E42uAU
```

### Option B: Using Local Qdrant (Development)

```bash
# Run Qdrant in Docker
docker run -p 6333:6333 qdrant/qdrant

# Update .env
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=  # Leave empty for local instance
```

## Step 4: Backfill Historical Trades

This will load your existing Xtrades data into Qdrant:

```bash
cd c:\Code\WheelStrategy
python src\rag\embedding_pipeline.py
```

Expected output:
```
Loading embedding model: sentence-transformers/all-mpnet-base-v2
Embedding dimension: 768
Connecting to Qdrant...
Creating collection: options_trades
Loading trades from database (status=closed, limit=None)
Loaded 1234 trades
Indexing 1234 trades...
Indexed 100/1234 trades
Indexed 200/1234 trades
...
Indexed 1234/1234 trades
Backfill complete. Indexed 1234 trades.
```

**Time**: 5-10 minutes depending on number of trades

## Step 5: Test the System

Create a test file `test_rag.py`:

```python
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / 'src'))

from rag.rag_query_engine import RAGQueryEngine

# Initialize engine
engine = RAGQueryEngine()

# Test alert
alert = {
    'ticker': 'AAPL',
    'strategy': 'CSP',
    'action': 'BTO',
    'strike_price': 170.0,
    'expiration_date': '2024-12-20',
    'dte': 30,
    'premium': 2.50,
    'current_price': 178.50,
    'current_vix': 15.2,
    'iv_rank': 45,
    'alert_text': 'BTO 2x $AAPL 12/20 $170 CSP @ $2.50'
}

# Get recommendation
print("Getting recommendation...")
recommendation = engine.get_recommendation(alert)

# Print result
print("\nRECOMMENDATION:", recommendation['recommendation'])
print("CONFIDENCE:", f"{recommendation['confidence']}%")
print("REASONING:", recommendation['reasoning'])
print("\nHISTORICAL EVIDENCE:")
for evidence in recommendation['historical_evidence']:
    print(f"  - {evidence}")
```

Run:
```bash
python test_rag.py
```

Expected output:
```
Getting recommendation...
Searching for similar trades (limit=10, threshold=0.7)
Found 8 similar trades
Calling Claude Sonnet 4.5 for recommendation...
Recommendation: TAKE (Confidence: 85%)

RECOMMENDATION: TAKE
CONFIDENCE: 85%
REASONING: Historical data shows 7 out of 8 similar AAPL CSPs were profitable, with an average P&L of +$180 (72%). Current market conditions align with successful historical trades (VIX ~15, bullish trend).

HISTORICAL EVIDENCE:
  - AAPL CSP $170 - Won $250 (+80%) in 14 days
  - AAPL CSP $175 - Won $180 (+75%) in 18 days
  - AAPL CSP $165 - Won $200 (+85%) in 12 days
```

## Step 6: Integrate with Xtrades Scraper

Create `src/rag/xtrades_rag_integration.py`:

```python
"""
Integrate RAG with Xtrades scraper for automatic recommendations
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from xtrades_scraper import XtradesScraper
from xtrades_db_manager import XtradesDBManager
from rag.rag_query_engine import RAGQueryEngine
from rag.recommendation_tracker import RecommendationTracker
import yfinance as yf
from datetime import datetime


def enrich_alert_with_market_data(alert):
    """Add current market data to alert"""
    ticker = alert.get('ticker')

    if ticker:
        try:
            # Get current price and VIX
            stock = yf.Ticker(ticker)
            alert['current_price'] = stock.info.get('currentPrice')

            vix = yf.Ticker("^VIX")
            vix_hist = vix.history(period='1d')
            alert['current_vix'] = vix_hist['Close'].iloc[-1] if not vix_hist.empty else 15.0

            # Placeholder for IV rank (would need options data API)
            alert['iv_rank'] = 50

        except Exception as e:
            print(f"Could not enrich alert: {e}")

    return alert


def process_new_alerts():
    """
    Process new Xtrades alerts and generate RAG recommendations
    """
    # Initialize components
    db = XtradesDBManager()
    rag = RAGQueryEngine()
    tracker = RecommendationTracker()

    # Get recent unprocessed trades (last 24 hours, no recommendation yet)
    query_24h_ago = datetime.now() - timedelta(hours=24)

    conn = db.get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT t.*
        FROM xtrades_trades t
        LEFT JOIN xtrades_recommendations r ON t.id = r.trade_id
        WHERE t.alert_timestamp >= %s
          AND r.id IS NULL
          AND t.status = 'open'
        ORDER BY t.alert_timestamp DESC
    """, (query_24h_ago,))

    new_alerts = [dict(row) for row in cur.fetchall()]
    cur.close()
    conn.close()

    print(f"Found {len(new_alerts)} new alerts to process")

    for alert in new_alerts:
        try:
            print(f"\nProcessing: {alert['ticker']} {alert['strategy']}")

            # Enrich with market data
            enriched_alert = enrich_alert_with_market_data(alert)

            # Get RAG recommendation
            start_time = datetime.now()
            recommendation = rag.get_recommendation(enriched_alert)
            latency_ms = int((datetime.now() - start_time).total_seconds() * 1000)

            # Store recommendation
            rec_id = tracker.store_recommendation(
                trade_id=alert['id'],
                recommendation=recommendation,
                query_latency_ms=latency_ms
            )

            print(f"  Recommendation: {recommendation['recommendation']} ({recommendation['confidence']}%)")
            print(f"  Stored as ID: {rec_id}")

        except Exception as e:
            print(f"  Error processing alert {alert['id']}: {e}")

    print(f"\nProcessed {len(new_alerts)} alerts")


if __name__ == "__main__":
    process_new_alerts()
```

## Step 7: Set Up Automated Processing

### Option A: Windows Task Scheduler

1. Create `process_xtrades_rag.bat`:
```batch
@echo off
cd c:\Code\WheelStrategy
python src\rag\xtrades_rag_integration.py
```

2. Open Task Scheduler
3. Create Basic Task:
   - Name: "Process Xtrades RAG"
   - Trigger: Daily at 9:00 AM (market open)
   - Action: Start a program -> Browse to `process_xtrades_rag.bat`

### Option B: Manual Processing

Run whenever you scrape new alerts:
```bash
python src\xtrades_scraper.py  # Scrape new alerts
python src\rag\xtrades_rag_integration.py  # Get RAG recommendations
```

## Step 8: Monitor Performance

Check RAG system performance:

```python
from src.rag.recommendation_tracker import RecommendationTracker

tracker = RecommendationTracker()
tracker.print_performance_report(days=30)
```

Output:
```
================================================================================
RAG SYSTEM PERFORMANCE REPORT (Last 30 Days)
================================================================================

OVERALL METRICS
--------------------------------------------------------------------------------
Total Recommendations: 45
Recommendations with Outcomes: 32
Overall Accuracy: 78.1%
Total P&L Impact: $3,450.00

BY RECOMMENDATION TYPE
--------------------------------------------------------------------------------
TAKE    :  28 recs, 82.1% accurate, avg confidence: 75%, avg P&L: +$156.25
PASS    :  15 recs, 73.3% accurate, avg confidence: 68%, avg P&L: -$45.00
MONITOR :   2 recs, 100.0% accurate, avg confidence: 55%, avg P&L: $0.00

CONFIDENCE CALIBRATION
--------------------------------------------------------------------------------
High (80-100%)      :  12 recs, 91.7% accurate, avg conf: 87%
Medium (50-79%)     :  25 recs, 76.0% accurate, avg conf: 64%
Low (0-49%)         :   5 recs, 60.0% accurate, avg conf: 42%

TOP 10 LEARNING TRADES
--------------------------------------------------------------------------------
 1. AAPL  CSP             - P&L: +$250.00 (+80.0%) - Weight: 1.30, Accuracy: 92%, Used: 12x
 2. MSFT  CSP             - P&L: +$180.00 (+75.0%) - Weight: 1.25, Accuracy: 89%, Used: 9x
 3. TSLA  Put Credit Spread - P&L: +$320.00 (+85.0%) - Weight: 1.20, Accuracy: 86%, Used: 7x
```

## Architecture Overview

```
New Alert → Embedding → Vector Search → Re-ranking → LLM → Recommendation
    ↓                         ↓              ↓          ↓           ↓
  Qdrant               Similar Trades   Top-5 Trades  Claude   PostgreSQL
```

## Customization

### Adjust Re-ranking Weights

Edit `src/rag/rag_query_engine.py`:

```python
self.rerank_weights = {
    'similarity': 0.5,   # How similar to historical trades
    'recency': 0.25,     # How recent the trade was
    'outcome': 0.25      # How profitable the trade was
}
```

### Adjust Confidence Threshold

```python
# Only show high-confidence recommendations
if recommendation['confidence'] >= 75:
    print(f"HIGH CONFIDENCE: {recommendation['recommendation']}")
```

### Change LLM Model

```python
# Use different Claude model
response = self.claude.messages.create(
    model="claude-3-5-sonnet-20241022",  # Older, cheaper version
    # or
    model="claude-opus-4-20250514",      # More powerful, expensive
    ...
)
```

### Add Custom Filters

```python
# Only learn from winning trades
must_conditions.append(
    FieldCondition(
        key="win",
        match=MatchValue(value=True)
    )
)
```

## Troubleshooting

### Issue: "QDRANT_API_KEY not set"

**Solution**: Add to `.env`:
```
QDRANT_API_KEY=your_key_here
```

### Issue: "No similar trades found"

**Causes**:
1. Not enough historical data in Qdrant
2. Filters too restrictive
3. Score threshold too high

**Solutions**:
- Run backfill: `python src\rag\embedding_pipeline.py`
- Reduce score threshold: `search_similar_trades(alert, score_threshold=0.6)`
- Broaden filters: Remove VIX or DTE filters

### Issue: "Claude API rate limit exceeded"

**Solution**: Add rate limiting:
```python
import time

# Rate limit: 1 request per second
time.sleep(1)
recommendation = engine.get_recommendation(alert)
```

### Issue: "Embedding model download failed"

**Solution**: Download model manually:
```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
model.save('models/all-mpnet-base-v2')

# Then use local model
model = SentenceTransformer('models/all-mpnet-base-v2')
```

## Performance Optimization

### 1. Cache Embeddings

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_embedding(text):
    return model.encode(text)
```

### 2. Batch Process Alerts

```python
# Process multiple alerts at once
alerts = get_new_alerts()
embeddings = model.encode([format_alert(a) for a in alerts], batch_size=32)
```

### 3. Use GPU for Embeddings

```python
# Install CUDA-enabled PyTorch first
model = SentenceTransformer('all-mpnet-base-v2', device='cuda')
```

## Cost Estimation

Based on 100 queries per day:

| Service | Usage | Cost |
|---------|-------|------|
| Qdrant Cloud | 100 queries/day, 10K vectors | $0 (Free tier) |
| HuggingFace | 100 embeddings/day | $0 (Free tier) |
| Claude Sonnet 4.5 | 100 queries × 5K tokens | ~$15/month |
| **Total** | | **~$15/month** |

Scale to 1,000 queries/day: ~$40/month

## Next Steps

1. **Add Notifications**: Send RAG recommendations to Telegram
2. **Build Dashboard**: Visualize RAG performance in Streamlit
3. **Backtest**: Compare RAG recommendations vs actual outcomes
4. **Fine-tune**: Adjust weights based on performance data
5. **Expand**: Add support for more complex strategies (Iron Condors, etc.)

## Support

For issues or questions:
- Check logs in `rag_system.log`
- Review database: `SELECT * FROM xtrades_recommendations ORDER BY created_at DESC LIMIT 10;`
- Test components individually (embedding, search, LLM)

## Resources

- Qdrant Docs: https://qdrant.tech/documentation/
- Claude API Docs: https://docs.anthropic.com/
- Sentence Transformers: https://www.sbert.net/
- RAG Architecture: See `docs/rag/RAG_ARCHITECTURE.md`
