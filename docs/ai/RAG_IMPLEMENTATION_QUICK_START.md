# RAG Autonomous Learning System - Quick Start Guide

**Status:** Ready for Implementation
**Priority:** HIGH
**Estimated Time:** Phase 1 (Foundation) = 2 weeks

---

## Overview

This guide walks you through implementing the RAG Autonomous Learning System for the Magnus Financial Assistant. The system will continuously learn from trading outcomes and improve recommendation quality without human intervention.

### What You're Building

- Autonomous learning loop that updates itself from trade outcomes
- Multi-source knowledge integration (trades, market events, user preferences)
- Adaptive weighting based on historical accuracy
- Self-correcting recommendation engine

### Current State vs. Target State

**Current (Your existing RAG):**
- ✅ Qdrant vector database
- ✅ sentence-transformers embeddings
- ✅ Claude Sonnet 4.5 LLM
- ✅ Basic recommendation generation
- ❌ No autonomous learning
- ❌ Static success weights
- ❌ No pattern extraction

**Target (After this implementation):**
- ✅ Everything above PLUS:
- ✅ Autonomous learning from every trade
- ✅ Dynamic success weight updates
- ✅ Pattern extraction and insight generation
- ✅ Market regime awareness
- ✅ Confidence calibration
- ✅ Continuous self-improvement

---

## Phase 1: Foundation Setup (Week 1-2)

### Step 1: Install pgvector Extension

```bash
# Connect to PostgreSQL
psql -U postgres -d magnus

# Install pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

# Verify installation
SELECT * FROM pg_extension WHERE extname = 'vector';
```

### Step 2: Deploy Learning Schema

```bash
# Navigate to project directory
cd C:\Code\Heracles\repos\WheelStrategy

# Deploy learning schema
psql -U postgres -d magnus -f src/rag/learning_schema.sql
```

**Expected output:**
```
RAG Autonomous Learning Schema Installed
========================================
Tables created:
  - xtrades_learning_insights
  - xtrades_learning_config
  - xtrades_market_regimes
  - xtrades_learning_metrics
  - xtrades_confidence_calibration
...
```

### Step 3: Install Python Dependencies

```bash
# Activate your virtual environment
.\venv\Scripts\activate

# Install new dependencies (if not already installed)
pip install psycopg2-binary>=2.9.9
pip install numpy>=1.26.3

# Verify installation
python -c "import psycopg2; print('psycopg2 OK')"
```

### Step 4: Test Learning Pipeline

```bash
# Run learning pipeline test
python src/rag/autonomous_learning.py
```

**Expected output:**
```
================================================================================
STARTING LEARNING CYCLE
================================================================================
Found 0 trades ready for learning
No trades to process
================================================================================
LEARNING CYCLE COMPLETE (0.5s)
  Trades Processed: 0
  Weights Updated: 0
  Insights Extracted: 0
================================================================================

Learning Cycle Complete!
Trades Processed: 0
Weights Updated: 0
Insights Extracted: 0
```

> If you see this, the learning pipeline is configured correctly and waiting for trade outcomes.

---

## Step 5: Integrate with Existing RAG System

### Update `recommendation_tracker.py`

Add learning trigger after outcome is recorded:

```python
# In recommendation_tracker.py, update_outcome() method

def update_outcome(
    self,
    recommendation_id: int,
    trade: Dict[str, Any]
) -> bool:
    """
    Update recommendation with actual trade outcome
    """
    # ... existing code ...

    # NEW: Trigger learning cycle asynchronously
    from src.rag.autonomous_learning import ContinuousLearningPipeline

    try:
        learning_pipeline = ContinuousLearningPipeline()
        # Run in background (non-blocking)
        import threading
        thread = threading.Thread(target=learning_pipeline.run_learning_cycle)
        thread.daemon = True
        thread.start()
    except Exception as e:
        logger.warning(f"Could not trigger learning cycle: {e}")

    return True
```

### Update `embedding_pipeline.py`

Add success weights to trade payloads:

```python
# In embedding_pipeline.py, create_point() method

def create_point(self, trade: Dict[str, Any]) -> PointStruct:
    """
    Create Qdrant point from trade
    """
    # ... existing code ...

    payload = {
        # ... existing fields ...

        # NEW: Learning fields
        'success_weight': 1.0,  # Initial weight
        'times_referenced': 0,
        'avg_recommendation_accuracy': 0.0,
        'last_updated': datetime.now().isoformat()
    }

    # ... rest of existing code ...
```

---

## Step 6: Create Background Learning Service

Create `src/rag/learning_service.py`:

```python
"""
Background service for continuous learning

Runs learning cycles every 30 minutes
"""

import asyncio
import logging
from datetime import datetime
from src.rag.autonomous_learning import ContinuousLearningPipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def run_continuous_learning():
    """
    Run learning cycles continuously
    """
    pipeline = ContinuousLearningPipeline()

    logger.info("Starting continuous learning service...")

    while True:
        try:
            # Run learning cycle
            metrics = pipeline.run_learning_cycle()

            logger.info(
                f"Learning cycle complete: "
                f"{metrics.trades_processed} trades, "
                f"{metrics.insights_extracted} insights"
            )

            # Wait 30 minutes
            await asyncio.sleep(1800)  # 30 minutes

        except Exception as e:
            logger.error(f"Learning cycle error: {e}")
            # Wait 5 minutes before retry
            await asyncio.sleep(300)


if __name__ == "__main__":
    asyncio.run(run_continuous_learning())
```

### Run Learning Service

```bash
# Terminal 1: Run main application
streamlit run dashboard.py

# Terminal 2: Run learning service (background)
python src/rag/learning_service.py
```

---

## Step 7: Monitor Learning Performance

### Query Learning Dashboard

```sql
-- Check learning system status
SELECT * FROM v_learning_dashboard;

-- View recent insights
SELECT * FROM v_recent_insights;

-- Check learning performance trend
SELECT * FROM v_learning_performance_trend;

-- Get statistics
SELECT * FROM get_learning_statistics(7);  -- Last 7 days
```

### Create Streamlit Monitoring Page

Create `learning_monitor_page.py`:

```python
import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Learning System Monitor", layout="wide")

st.title("RAG Autonomous Learning System - Monitor")

# Database connection (use your existing connection method)
@st.cache_resource
def get_connection():
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME', 'magnus')
    )

conn = get_connection()

# Overall metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    pending = pd.read_sql("SELECT pending_trades FROM v_learning_dashboard", conn).iloc[0, 0]
    st.metric("Pending Trades", pending or 0)

with col2:
    insights = pd.read_sql("SELECT insights_today FROM v_learning_dashboard", conn).iloc[0, 0]
    st.metric("Insights Today", insights or 0)

with col3:
    processed = pd.read_sql("SELECT trades_processed_today FROM v_learning_dashboard", conn).iloc[0, 0]
    st.metric("Trades Processed Today", processed or 0)

with col4:
    improvement = pd.read_sql("SELECT avg_improvement_7d FROM v_learning_dashboard", conn).iloc[0, 0]
    st.metric("Avg Improvement (7d)", f"{improvement or 0:.2f}%")

# Recent insights
st.subheader("Recent Learning Insights")
insights_df = pd.read_sql("SELECT * FROM v_recent_insights", conn)
st.dataframe(insights_df, use_container_width=True)

# Performance trend
st.subheader("Learning Performance Trend")
trend_df = pd.read_sql("SELECT * FROM v_learning_performance_trend", conn)

if not trend_df.empty:
    fig = px.line(
        trend_df,
        x='date',
        y=['trades_processed', 'insights_extracted'],
        title='Daily Learning Activity'
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No learning metrics yet. System will populate as trades are processed.")
```

---

## Step 8: Verify End-to-End Flow

### Test Complete Learning Cycle

1. **Create a test trade with recommendation:**

```python
# test_learning_flow.py
import psycopg2
from datetime import datetime, timedelta
from src.rag.rag_query_engine import RAGQueryEngine
from src.rag.recommendation_tracker import RecommendationTracker
from src.rag.autonomous_learning import ContinuousLearningPipeline

# 1. Create test alert
test_alert = {
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
    'alert_text': 'Test trade for learning system'
}

# 2. Get RAG recommendation
engine = RAGQueryEngine()
recommendation = engine.get_recommendation(test_alert)

print("Recommendation:", recommendation['recommendation'])
print("Confidence:", recommendation['confidence'])

# 3. Store recommendation (simulate trade creation)
# (In real system, this happens when user takes the trade)
trade_id = 12345  # Mock trade ID

tracker = RecommendationTracker()
rec_id = tracker.store_recommendation(trade_id, recommendation)

print(f"Stored recommendation {rec_id} for trade {trade_id}")

# 4. Simulate trade completion
test_trade_outcome = {
    'id': trade_id,
    'ticker': 'AAPL',
    'strategy': 'CSP',
    'status': 'closed',
    'entry_date': datetime.now() - timedelta(days=21),
    'exit_date': datetime.now(),
    'pnl': 180.0,  # Win
    'pnl_percent': 72.0,
    'hold_days': 21,
    'vix_at_entry': 15.2,
    'vix_at_exit': 14.8
}

# 5. Update outcome
tracker.update_outcome(rec_id, test_trade_outcome)

print(f"Recorded outcome for trade {trade_id}")

# 6. Run learning cycle
pipeline = ContinuousLearningPipeline()
metrics = pipeline.run_learning_cycle()

print("\nLearning Cycle Results:")
print(f"  Trades Processed: {metrics.trades_processed}")
print(f"  Insights Extracted: {metrics.insights_extracted}")
print(f"  Weights Updated: {metrics.weights_updated}")

print("\n✅ End-to-end learning flow complete!")
```

Run the test:

```bash
python test_learning_flow.py
```

**Expected output:**
```
Recommendation: TAKE
Confidence: 80
Stored recommendation 1 for trade 12345
Recorded outcome for trade 12345

================================================================================
STARTING LEARNING CYCLE
================================================================================
Found 1 trades ready for learning
Processing trade 12345: AAPL CSP
Processed trade 12345: 1 insights extracted, 5 weights to update
================================================================================
LEARNING CYCLE COMPLETE (1.2s)
  Trades Processed: 1
  Weights Updated: 5
  Insights Extracted: 1
================================================================================

Learning Cycle Results:
  Trades Processed: 1
  Insights Extracted: 1
  Weights Updated: 5

✅ End-to-end learning flow complete!
```

---

## Troubleshooting

### Issue: "pgvector extension not found"

**Solution:**
```bash
# Install pgvector from source (Windows)
# 1. Install Visual Studio Build Tools
# 2. Install PostgreSQL development files
# 3. Clone and build pgvector
git clone https://github.com/pgvector/pgvector.git
cd pgvector
# Follow build instructions for Windows
```

### Issue: "No trades ready for learning"

**Cause:** No closed trades with recommendations yet

**Solution:**
1. Ensure trades have recommendations stored
2. Ensure trades are marked as 'closed'
3. Ensure outcome_recorded_at is set
4. Check: `SELECT COUNT(*) FROM xtrades_recommendations WHERE learning_processed_at IS NULL AND outcome_recorded_at IS NOT NULL;`

### Issue: "Connection to Qdrant failed"

**Solution:**
```python
# Check Qdrant connection
from qdrant_client import QdrantClient

client = QdrantClient(
    url=os.getenv('QDRANT_URL'),
    api_key=os.getenv('QDRANT_API_KEY')
)

# Test connection
collections = client.get_collections()
print(f"Connected! Collections: {collections}")
```

### Issue: "Learning cycle runs but no insights extracted"

**Cause:** Pattern extractor needs trade outcome details

**Solution:**
Ensure trade outcome includes:
- pnl
- vix_at_entry and vix_at_exit
- hold_days
- recommendation_correct (set by tracker.update_outcome)

---

## Next Steps

### Phase 2: Multi-Collection Architecture (Weeks 3-4)

Once Phase 1 is stable:

1. **Create 6 Qdrant collections:**
   - trades_closed (primary)
   - trades_active (realtime)
   - market_events
   - strategies
   - user_context (pgvector)
   - financial_docs

2. **Implement collection-specific processors**

3. **Build cross-collection search**

4. **Migrate existing data**

### Phase 3: Advanced Retrieval (Weeks 5-6)

1. **Implement hybrid retrieval:**
   - Semantic + filtered + re-ranked

2. **Add market regime detection:**
   - Track regime changes
   - Adjust strategy based on regime

3. **Implement diversity-aware selection:**
   - Avoid redundant results

### Phase 4: Full Autonomous System (Weeks 7-8)

1. **Aggregate learning analysis:**
   - Weekly performance reports
   - Confidence calibration
   - Bias detection

2. **Model adaptation:**
   - Auto-tune retrieval weights
   - Adjust embedding strategies

---

## Success Metrics

Track these metrics to measure learning system effectiveness:

| Metric | Target | Current |
|--------|--------|---------|
| Recommendation Accuracy | 85%+ | (baseline) |
| Confidence Calibration Error | <10% | (baseline) |
| False Positive Rate | <15% | (baseline) |
| Insights per Trade | 1-3 | 0 |
| Learning Cycle Frequency | 30 min | N/A |

### Query Current Metrics

```sql
-- Overall accuracy
SELECT
    COUNT(*) as total_recommendations,
    SUM(CASE WHEN recommendation_correct THEN 1 ELSE 0 END) as correct,
    (SUM(CASE WHEN recommendation_correct THEN 1 ELSE 0 END)::FLOAT /
     COUNT(*)::FLOAT * 100) as accuracy_pct
FROM xtrades_recommendations
WHERE recommendation_correct IS NOT NULL;

-- Accuracy by confidence band
SELECT
    CASE
        WHEN confidence < 50 THEN '0-50%'
        WHEN confidence < 70 THEN '50-70%'
        WHEN confidence < 85 THEN '70-85%'
        ELSE '85-100%'
    END as confidence_band,
    COUNT(*) as total,
    SUM(CASE WHEN recommendation_correct THEN 1 ELSE 0 END) as correct,
    (SUM(CASE WHEN recommendation_correct THEN 1 ELSE 0 END)::FLOAT /
     COUNT(*)::FLOAT * 100) as accuracy_pct
FROM xtrades_recommendations
WHERE recommendation_correct IS NOT NULL
GROUP BY confidence_band
ORDER BY confidence_band;
```

---

## Support & Resources

### Documentation

- **Full Design:** `docs/ai/RAG_AUTONOMOUS_LEARNING_SYSTEM_DESIGN.md`
- **Implementation Code:** `src/rag/autonomous_learning.py`
- **Database Schema:** `src/rag/learning_schema.sql`

### Key Files Modified

1. `src/rag/autonomous_learning.py` - NEW
2. `src/rag/learning_schema.sql` - NEW
3. `src/rag/learning_service.py` - NEW (to create)
4. `learning_monitor_page.py` - NEW (to create)
5. `src/rag/recommendation_tracker.py` - UPDATE (add learning trigger)
6. `src/rag/embedding_pipeline.py` - UPDATE (add success weights)

### Questions?

Common questions answered in full design document:
- Why hybrid vector databases? (Section 2)
- How does success weight algorithm work? (Section 4)
- What embedding strategy to use? (Section 6)
- How to optimize costs? (Section 12)

---

## Final Checklist

Before moving to production:

- [ ] pgvector extension installed
- [ ] Learning schema deployed successfully
- [ ] Python dependencies installed
- [ ] Learning pipeline runs without errors
- [ ] Test learning flow passes end-to-end
- [ ] Background learning service running
- [ ] Monitoring dashboard accessible
- [ ] Success metrics baseline captured
- [ ] Documentation reviewed and understood

---

**Status:** Ready to begin Phase 1 implementation
**Timeline:** 2 weeks for foundation, 10 weeks for complete system
**Next Action:** Install pgvector and deploy learning schema

*Generated by: AI Engineer Agent*
*Date: November 10, 2025*
