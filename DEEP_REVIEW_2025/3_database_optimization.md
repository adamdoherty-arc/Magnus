# 2. DATABASE QUERY OPTIMIZATION ANALYSIS

## 2.1 Connection Pooling Status

**IMPLEMENTED (Good Practice):**
- KalshiDBManager: ThreadedConnectionPool (2-50 connections)
- XtradesDBManager: Optional connection pool with fallback
- ava/rate_limiter.py: Thread-safe rate limiting

**MISSING (Critical Risk):**
- ai_flow_analyzer.py: Direct psycopg2.connect() calls
- auto_balance_recorder.py: No pooling
- database_scanner.py: No pooling
- delisted_symbols_manager.py: No pooling
- earnings_sync_service.py: No pooling

**Impact:** Connection exhaustion under concurrent load, resource leaks

## 2.2 Index Coverage Analysis

**Total SQL Schema:** 4,428 lines across 14 schema files

**Well-Indexed Tables:**
- kalshi_markets: 8 indexes (type, status, dates, teams, scores)
- kalshi_predictions: 4 indexes
- kalshi_price_history: 3 indexes
- discord_messages: 4 indexes including GIN full-text search
- prediction_performance: 7 indexes
- feature_store: 6 indexes including GIN
- backtest_results: 4 indexes
- xtrades_trades: Adequate indexes

**Under-Indexed Tables:**
- stocks: Missing sector, industry indexes
- options: Missing strike price range indexes
- stock_premiums: Could use ticker/expiration indexes

**Recommended New Indexes:**
```sql
CREATE INDEX idx_stocks_sector ON stocks(sector);
CREATE INDEX idx_stocks_industry ON stocks(industry);
CREATE INDEX idx_options_strike_price ON options(strike_price);
CREATE INDEX idx_options_expiration_date ON options(expiration_date);
CREATE INDEX idx_stock_premiums_ticker_exp ON stock_premiums(ticker, expiration_date);
```

## 2.3 Query Pattern Analysis

**29 SQL queries in kalshi_db_manager.py:**
- Most use parameterized queries (SQL injection protected)
- Good use of LIMIT clauses
- Mostly SELECT * but in specific contexts (acceptable)

**Safety Assessment:**
- HIGH: kalshi_db_manager.py, xtrades_db_manager.py
- MEDIUM: earnings_sync_service.py, espn_kalshi_matcher.py
- REVIEW NEEDED: odds_validator.py (25+ complex queries)

## 2.4 N+1 Query Pattern Risk

**Risk Level: MEDIUM**

Found safe patterns using fetchall() but potential issues in:
- odds_validator.py: May iterate markets and fetch per-market data
- earnings_sync_service.py: May loop tickers individually
- game_watchlist_manager.py: May need batching optimization

**Example Problem:**
```python
# AVOID:
for market in markets:
    cur.execute(f"SELECT ... WHERE market_id = {market['id']}")

# BETTER:
market_ids = [m['id'] for m in markets]
cur.execute(f"SELECT ... WHERE market_id IN {tuple(market_ids)}")
```

## 2.5 LIMIT Clause Coverage

**Status:** Good (85%+ coverage)
- Most queries have LIMIT clauses
- kalshi_db_manager.py: Consistent use (line 1009: LIMIT 1)
- Missing in some earnings_sync_service.py queries

## 2.6 Caching Layer Analysis

**Implemented:**
- Streamlit @st.cache_data with TTL (300-1800 seconds)
- Local LLM response caching
- Technical analysis caching (Fibonacci, volume profile)

**Missing:**
- No database query result caching layer
- Portfolio data refetched on every access
- Options data refetched unnecessarily

## 2.7 Query Performance Optimization Plan

**Phase 1 - Immediate (Week 1):**
1. Implement unified connection pool (2-3 hours)
2. Add missing indexes (1 hour)
3. Migrate 5 modules to use connection pool (2-3 hours)

**Phase 2 - Short-term (Weeks 2-3):**
1. Add query logging/monitoring
2. Identify slow queries with EXPLAIN ANALYZE
3. Batch optimize N+1 patterns
4. Implement query result caching

**Phase 3 - Medium-term (Weeks 4+):**
1. Create materialized views for complex aggregations
2. Implement automatic query optimization
3. Add performance monitoring dashboard

## 2.8 Connection Pool Implementation Example

```python
# src/database/connection_pool.py
import psycopg2.pool
import os
import logging

logger = logging.getLogger(__name__)

class DatabaseConnectionPool:
    _instance = None
    _pool = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize_pool()
        return cls._instance
    
    def _initialize_pool(self):
        """Initialize the connection pool"""
        try:
            self._pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=2,
                maxconn=20,
                host=os.getenv('DB_HOST', 'localhost'),
                port=os.getenv('DB_PORT', '5432'),
                user=os.getenv('DB_USER', 'postgres'),
                password=os.getenv('DB_PASSWORD'),
                database=os.getenv('DB_NAME', 'magnus')
            )
            logger.info("Connection pool initialized (2-20 connections)")
        except Exception as e:
            logger.error(f"Failed to initialize connection pool: {e}")
            self._pool = None
    
    def get_connection(self):
        """Get a connection from the pool"""
        if self._pool:
            return self._pool.getconn()
        else:
            raise Exception("Connection pool not available")
    
    def return_connection(self, conn):
        """Return a connection to the pool"""
        if self._pool and conn:
            try:
                self._pool.putconn(conn)
            except Exception as e:
                logger.error(f"Error returning connection: {e}")

# Usage in other modules:
# from src.database.connection_pool import DatabaseConnectionPool
# pool = DatabaseConnectionPool()
# conn = pool.get_connection()
# try:
#     # use connection
# finally:
#     pool.return_connection(conn)
```

## 2.9 Estimated Performance Improvements

| Optimization | Expected Improvement | Effort |
|--------------|----------------------|--------|
| Connection Pooling | 30-40% reduction in connection overhead | Low |
| Missing Indexes | 20-30% faster queries | Low |
| N+1 Query Batching | 50%+ for affected queries | Medium |
| Query Result Caching | 60-80% hit rate (saves DB calls) | Medium |
| Materialized Views | 90%+ faster complex aggregations | High |

**Total Potential Improvement:** 3-5x faster database operations with 40 hours effort
