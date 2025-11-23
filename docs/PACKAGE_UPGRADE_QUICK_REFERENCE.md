# Package Upgrade Quick Reference - 2025

## Quick Decision Matrix

| Current Package | Recommendation | Priority | Effort | Impact |
|----------------|----------------|----------|--------|--------|
| yfinance | yahooquery | HIGH | Low | High |
| mibian | py-vollib-vectorized | HIGH | Medium | High |
| psycopg2 (no pool) | Add pooling | HIGH | Medium | High |
| No pagination | streamlit-pagination | HIGH | Medium | High |
| LLM (basic) | RunnableWithFallbacks | MEDIUM | Medium | Medium |
| psycopg2 | asyncpg | MEDIUM | High | Very High |
| pandas-ta | Keep (works great) | - | - | - |
| SQLAlchemy 2.0 | Add asyncpg driver | LOW | High | High |

---

## Critical Upgrades (Do First)

### 1. Replace yfinance with yahooquery

**Why:** yfinance is unreliable for production (rate limits, IP bans)

**Install:**
```bash
pip uninstall yfinance
pip install yahooquery
```

**Code Changes:**
```python
# OLD (yfinance)
import yfinance as yf
ticker = yf.Ticker("AAPL")
hist = ticker.history(period="1mo")

# NEW (yahooquery)
from yahooquery import Ticker
ticker = Ticker("AAPL")
hist = ticker.history(period="1mo")
```

**Files to Update:**
- All files importing `yfinance`
- Search: `grep -r "import yfinance" --include="*.py"`

---

### 2. Upgrade to py-vollib for Greeks

**Why:** Faster, more accurate than mibian

**Install:**
```bash
pip install py-vollib-vectorized
```

**Code Changes:**
```python
# OLD (mibian)
import mibian
c = mibian.BS([100, 105, 1, 0.25], volatility=25)
delta = c.callDelta

# NEW (py_vollib)
from py_vollib.black_scholes.greeks import analytical
delta = analytical.delta('c', S=100, K=105, t=0.25, r=0.01, sigma=0.25)
```

**Files to Update:**
- `src/ai_options_advisor.py`
- Search: `grep -r "mibian" --include="*.py"`

---

### 3. Add Database Connection Pooling

**Why:** Better performance, avoid connection exhaustion

**Install:** None needed (psycopg2 has built-in pooling)

**Code:**
```python
from psycopg2 import pool

connection_pool = pool.ThreadedConnectionPool(
    minconn=5,
    maxconn=20,
    user=..., password=..., host=..., database=...
)

# Use
conn = connection_pool.getconn()
# ... use connection ...
connection_pool.putconn(conn)
```

**Files to Create:**
- `src/database/connection_pool.py`

**Files to Update:**
- All files creating new psycopg2 connections

---

### 4. Add Pagination to Scanners

**Why:** Better UX for large datasets

**Install:**
```bash
pip install streamlit-pagination
```

**Code:**
```python
from streamlit_pagination import pagination_component

# Split data into chunks
chunks = [df[i:i+100] for i in range(0, len(df), 100)]

# Pagination UI
page = pagination_component(len(chunks), layout={...}, key="scanner")

# Display current page
st.dataframe(chunks[page-1])
```

**Files to Update:**
- `options_analysis_page.py`
- `premium_scanner_page.py`
- All scanner/results pages

---

## Performance Upgrades (Do Next)

### 5. Implement LLM Fallbacks

**Why:** Production resilience, zero-downtime provider switching

**Install:** Already have LangChain 0.3+

**Code:**
```python
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI

primary = ChatAnthropic(model="claude-3-7-sonnet-20250219")
fallback = ChatOpenAI(model="gpt-4o")

robust_llm = primary.with_fallbacks([fallback])
```

**Files to Update:**
- `src/ai_options_agent/llm_manager.py`

---

### 6. Add asyncpg for High-Volume Queries

**Why:** 5x faster than psycopg3

**Install:**
```bash
pip install asyncpg
```

**Code:**
```python
import asyncpg

pool = await asyncpg.create_pool(
    user=..., password=..., database=..., host=...
)

async with pool.acquire() as conn:
    rows = await conn.fetch('SELECT * FROM stock_premiums WHERE symbol = $1', 'AAPL')
```

**Files to Create:**
- `src/database/async_db.py`

**Files to Update (Priority):**
- Options scanner (high volume)
- Real-time sync modules

---

## Long-term Improvements

### 7. Migrate to Polygon.io (Production Data)

**Why:** Reliable, professional-grade options data

**Cost:** $199-$399/month

**Install:**
```bash
pip install polygon-api-client
```

**When:** Ready for production deployment

---

### 8. SQLAlchemy 2.0 + asyncpg

**Why:** Modern ORM with async performance

**Install:**
```bash
pip install sqlalchemy[asyncio] asyncpg
```

**Code:**
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

engine = create_async_engine("postgresql+asyncpg://...")
async_session = async_sessionmaker(engine, class_=AsyncSession)
```

**When:** Major refactoring cycle

---

## Optional Enhancements

### 9. TA-Lib (Only if needed)

**When to Install:**
- Processing 10,000+ rows regularly
- Need maximum performance for technical indicators

**Current:** pandas-ta works great for most use cases

---

### 10. OptionGreeksGPU

**When to Install:**
- Scanning 1000+ contracts simultaneously
- Need sub-second Greeks for entire option chains

**Current:** py-vollib-vectorized is fast enough for most use cases

---

## Installation Commands (All at Once)

```bash
# Critical upgrades
pip uninstall yfinance
pip install yahooquery py-vollib-vectorized streamlit-pagination

# Performance upgrades
pip install asyncpg

# Update existing packages
pip install --upgrade sqlalchemy langchain langchain-core langchain-anthropic langchain-openai

# Optional (production)
# pip install polygon-api-client
# conda install -c conda-forge ta-lib
```

---

## Migration Checklist

- [ ] Install yahooquery, remove yfinance
- [ ] Replace all yf.Ticker() calls
- [ ] Install py-vollib-vectorized
- [ ] Replace mibian Greeks calculations
- [ ] Create connection_pool.py
- [ ] Update all database access to use pool
- [ ] Install streamlit-pagination
- [ ] Add pagination to scanner pages
- [ ] Implement RunnableWithFallbacks in llm_manager.py
- [ ] Install asyncpg
- [ ] Create async_db.py for high-volume queries
- [ ] Update scanner modules to use async queries
- [ ] Test all changes thoroughly
- [ ] Update requirements.txt
- [ ] Deploy to production

---

## Performance Expected Gains

| Upgrade | Performance Gain | Use Case |
|---------|------------------|----------|
| yahooquery | Reliability +500% | All data fetching |
| py-vollib | Speed +200% | Greeks calculations |
| Connection pooling | Throughput +300% | All DB operations |
| Pagination | UX +infinite% | Large result sets |
| RunnableWithFallbacks | Uptime +99.9% | LLM operations |
| asyncpg | Speed +500% | Bulk DB operations |

---

## Code Search Commands

```bash
# Find yfinance usage
grep -r "import yfinance" --include="*.py"
grep -r "yf.Ticker" --include="*.py"

# Find mibian usage
grep -r "import mibian" --include="*.py"
grep -r "mibian.BS" --include="*.py"

# Find direct psycopg2 connections (no pooling)
grep -r "psycopg2.connect" --include="*.py"

# Find LangChain usage
grep -r "from langchain" --include="*.py"
```

---

## Testing Strategy

1. **Unit Tests:**
   - Greeks calculation accuracy
   - Database connection pooling
   - LLM fallback chains

2. **Integration Tests:**
   - yahooquery data fetching
   - asyncpg bulk operations
   - Pagination in Streamlit

3. **Performance Tests:**
   - Benchmark Greeks calculations (old vs new)
   - Benchmark database queries (pooled vs non-pooled)
   - Benchmark asyncpg vs psycopg2

4. **Stress Tests:**
   - 1000+ concurrent database connections
   - LLM provider failures
   - Large dataset pagination (100,000+ rows)

---

## Rollback Plan

If anything breaks:

1. **yahooquery → yfinance:**
   ```bash
   pip install yfinance
   git checkout -- <files>
   ```

2. **py-vollib → mibian:**
   ```bash
   pip install mibian
   git checkout -- src/ai_options_advisor.py
   ```

3. **Connection pooling:**
   ```bash
   git checkout -- src/database/connection_pool.py
   # Remove pool usage from files
   ```

4. **Keep backups:**
   ```bash
   git branch backup-before-upgrade
   git commit -am "Backup before package upgrades"
   ```

---

## Support Resources

- **LangChain:** https://python.langchain.com/docs/
- **py_vollib:** https://vollib.org/
- **asyncpg:** https://magicstack.github.io/asyncpg/
- **yahooquery:** https://yahooquery.dpguthrie.com/
- **Streamlit:** https://docs.streamlit.io/

---

**Last Updated:** 2025-01-21
**Version:** 1.0
