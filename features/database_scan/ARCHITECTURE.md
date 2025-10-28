# Database Scan Architecture

## System Architecture Overview

The Database Scan feature implements a multi-layered architecture that separates concerns between data access, business logic, and presentation. The system is designed for scalability, handling thousands of stocks with millions of option contracts while maintaining sub-second query response times.

## Component Architecture

### Layer 1: Data Layer

#### PostgreSQL Database
The foundation of the system is a PostgreSQL database with the following schema:

```
┌─────────────────────────────────────────────────────────────┐
│                     PostgreSQL Database                      │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────┐    ┌──────────────────┐                   │
│  │   stocks    │───>│  stock_premiums   │                   │
│  └─────────────┘    └──────────────────┘                   │
│         │                    │                               │
│         ▼                    ▼                               │
│  ┌─────────────┐    ┌──────────────────┐                   │
│  │ stock_data  │    │  tv_watchlists    │                   │
│  └─────────────┘    └──────────────────┘                   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

**Table Relationships:**
- `stocks` (1) → (N) `stock_premiums`: One stock has multiple option contracts
- `stocks` (1) → (1) `stock_data`: One stock has one current data record
- `stocks` (N) → (M) `tv_watchlists`: Many-to-many via `tv_watchlist_symbols`

### Layer 2: Data Access Layer

#### DatabaseScanner Class
Primary interface for database operations:

```python
class DatabaseScanner:
    def __init__(self)
    def connect() -> bool
    def disconnect() -> None
    def create_tables() -> bool
    def add_stock(symbol: str, fetch_data: bool) -> bool
    def get_all_stocks() -> List[Dict]
    def get_stocks_by_criteria(...) -> List[Dict]
    def update_stock_prices() -> int
    def save_option_data(...) -> bool
    def get_stocks_with_best_premiums(...) -> List[Dict]
```

#### TradingViewDBManager Class
Specialized manager for watchlist and premium operations:

```python
class TradingViewDBManager:
    def __init__(self)
    def get_connection() -> psycopg2.connection
    def initialize_tables() -> None
    def sync_watchlist_premiums(...) -> dict
    def get_watchlist_symbols(...) -> List[str]
    def save_stock_premium(...) -> bool
```

### Layer 3: Business Logic Layer

#### Option Premium Calculations
The system implements sophisticated option pricing logic:

1. **Monthly Return Calculation**
   ```python
   monthly_return = (premium / (strike * 100)) * (30 / dte) * 100
   ```

2. **Delta Filtering**
   - Target range: 0.25 - 0.40
   - Ensures 60-75% probability of profit
   - Balances premium income with assignment risk

3. **Strike Selection**
   - Default: 5% out-of-the-money (OTM)
   - Adjustable based on market conditions
   - Considers liquidity via bid-ask spread

#### Data Synchronization Service
Background service for option chain updates:

```python
async def sync_all_database_stocks():
    stocks = get_all_stocks_from_database()

    for batch in chunk(stocks, size=50):
        tasks = [fetch_options(symbol) for symbol in batch]
        results = await asyncio.gather(*tasks)
        save_batch_to_database(results)

    return sync_statistics
```

### Layer 4: Presentation Layer

#### Streamlit Dashboard Integration
The Database Scan feature is integrated into the main dashboard at `dashboard.py`:

```python
elif page == "Database Scan":
    st.title("Database Stock Scanner")

    # Tab-based interface
    tabs = st.tabs(["Overview", "Add Stocks", "Scan Premiums", "Analytics"])

    with tabs[2]:  # Scan Premiums - Primary Interface
        render_premium_scanner()
```

## Data Flow Architecture

### 1. Initial Page Load
```
User Request → Streamlit Router → Database Scan Page
                                          │
                                          ▼
                              TradingViewDBManager.get_connection()
                                          │
                                          ▼
                                  Execute SQL Query
                                          │
                                          ▼
                              Format & Display Results
```

### 2. Sync Process Flow
```
User Clicks "Sync All" → Create AllStocks Watchlist
                                    │
                                    ▼
                         Launch Background Service
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
            Fetch Stock List              Fetch Options Data
            from Database                  from Yahoo Finance
                    │                               │
                    └───────────────┬───────────────┘
                                    ▼
                            Save to stock_premiums
                                    │
                                    ▼
                            Update UI Statistics
```

### 3. Query Execution Pipeline
```
Apply Filters → Build SQL Query → Execute Query → Process Results
       │              │                │              │
       ▼              ▼                ▼              ▼
   Price Range    Add WHERE      PostgreSQL      Format Data
   Premium Min    Clauses        Optimizer       Apply Styling
   DTE Range      Bind Params    Index Scan      Return to UI
```

## Database Schema Details

### stocks Table
```sql
CREATE TABLE stocks (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(255),
    sector VARCHAR(100),
    industry VARCHAR(100),
    market_cap BIGINT,
    current_price DECIMAL(10,2),
    avg_volume BIGINT,
    last_updated TIMESTAMP DEFAULT NOW()
);
```

### stock_premiums Table
```sql
CREATE TABLE stock_premiums (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    dte INTEGER,
    strike_price DECIMAL(10,2),
    premium DECIMAL(10,4),
    bid DECIMAL(10,2),
    ask DECIMAL(10,2),
    delta DECIMAL(6,4),
    implied_volatility DECIMAL(6,2),
    volume INTEGER,
    open_interest INTEGER,
    monthly_return DECIMAL(6,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_symbol_dte (symbol, dte),
    INDEX idx_delta (delta),
    INDEX idx_monthly_return (monthly_return DESC)
);
```

## Performance Optimization Strategies

### 1. Database Indexes
Strategic indexes for common query patterns:

```sql
-- Primary lookup patterns
CREATE INDEX idx_sp_symbol_dte ON stock_premiums(symbol, dte);
CREATE INDEX idx_sp_delta ON stock_premiums(ABS(delta));
CREATE INDEX idx_sp_monthly_return ON stock_premiums(monthly_return DESC);

-- Join optimization
CREATE INDEX idx_stocks_symbol ON stocks(symbol);
CREATE INDEX idx_sd_symbol ON stock_data(symbol);
```

### 2. Query Optimization

#### DISTINCT ON Pattern
```sql
SELECT DISTINCT ON (sp.symbol)
    sp.*, ...
FROM stock_premiums sp
ORDER BY sp.symbol, sp.monthly_return DESC
```
- Returns best option per symbol
- Reduces result set size
- Leverages PostgreSQL-specific optimization

#### LEFT JOIN Strategy
```sql
LEFT JOIN stock_data sd ON sp.symbol = sd.symbol
LEFT JOIN stocks s ON sp.symbol = s.ticker
```
- Graceful null handling
- Maintains result set even with missing data
- Allows partial data display

### 3. Caching Strategy

#### Session State Caching
```python
if 'premium_scan_cache' not in st.session_state:
    st.session_state.premium_scan_cache = {}

cache_key = f"{filters}_{datetime.now().hour}"
if cache_key in st.session_state.premium_scan_cache:
    return st.session_state.premium_scan_cache[cache_key]
```

#### Database Connection Pooling
```python
class ConnectionPool:
    def __init__(self, size=10):
        self.pool = []
        for _ in range(size):
            self.pool.append(create_connection())

    def get_connection(self):
        return self.pool.pop()

    def return_connection(self, conn):
        self.pool.append(conn)
```

## Scalability Considerations

### Horizontal Scaling
- **Read Replicas**: Distribute read queries across multiple database instances
- **Sharding**: Partition stocks table by symbol range (A-F, G-M, N-S, T-Z)
- **Caching Layer**: Redis/Memcached for frequently accessed data

### Vertical Scaling
- **Query Parallelization**: Process multiple symbols simultaneously
- **Batch Processing**: Group operations for efficiency
- **Async Operations**: Non-blocking I/O for external API calls

### Data Volume Projections
```
Current State:
- Stocks: 1,205
- Options per stock: ~10-20 strikes
- Total contracts: ~15,000-25,000
- Query time: <2 seconds

Scaled Projection (5,000 stocks):
- Stocks: 5,000
- Options per stock: ~10-20 strikes
- Total contracts: ~50,000-100,000
- Query time (with optimizations): <3 seconds
```

## Error Handling Architecture

### Graceful Degradation
```python
try:
    # Primary data fetch
    options_data = fetch_options_from_api(symbol)
except APIException:
    try:
        # Fallback to cached data
        options_data = get_cached_options(symbol)
    except CacheException:
        # Return last known good data
        options_data = get_last_known_options(symbol)
```

### Error Recovery Patterns
1. **Connection Retry**: Exponential backoff for database connections
2. **Partial Sync Recovery**: Resume from last successful symbol
3. **Data Validation**: Sanity checks before database writes
4. **User Notification**: Clear error messages with recovery actions

## Security Architecture

### Data Protection
- **SQL Injection Prevention**: Parameterized queries throughout
- **Connection Encryption**: SSL/TLS for database connections
- **Credential Management**: Environment variables, never hardcoded
- **Rate Limiting**: Prevent API abuse during sync operations

### Access Control
```python
# Future implementation
class AccessControl:
    ROLES = {
        'viewer': ['read'],
        'trader': ['read', 'sync'],
        'admin': ['read', 'sync', 'write', 'delete']
    }

    def check_permission(user_role, action):
        return action in ROLES.get(user_role, [])
```

## Monitoring & Observability

### Key Metrics
1. **Performance Metrics**
   - Query response time
   - Sync completion rate
   - Database connection pool utilization

2. **Business Metrics**
   - Stocks with available options
   - Average premium yield
   - Most active sectors

3. **System Health**
   - Database CPU/Memory usage
   - API call success rate
   - Error rate by component

### Logging Strategy
```python
import logging

logger = logging.getLogger(__name__)

# Structured logging
logger.info("sync_started", extra={
    'stocks_count': 1205,
    'timestamp': datetime.now(),
    'user_id': user_id
})
```

## Integration Architecture

### External Systems
1. **Yahoo Finance API**
   - Options chain data
   - Real-time stock prices
   - Company information

2. **PostgreSQL Database**
   - Primary data store
   - ACID compliance
   - Complex query support

3. **Streamlit Framework**
   - User interface
   - Session management
   - Real-time updates

### Internal Components
```
┌─────────────────────────────────────────┐
│          Streamlit Dashboard            │
├─────────────────────────────────────────┤
│                    │                     │
│     ┌──────────────┼──────────────┐     │
│     ▼              ▼              ▼     │
│ TradingView    Database      Settings   │
│ Watchlists      Scan          Page      │
│     │              │              │     │
├─────┼──────────────┼──────────────┼─────┤
│     ▼              ▼              ▼     │
│        Shared Service Layer              │
│   (DatabaseScanner, TVDBManager)        │
├─────────────────────────────────────────┤
│         PostgreSQL Database              │
└─────────────────────────────────────────┘
```

## Development & Deployment

### Development Environment
```yaml
# docker-compose.yml
version: '3.8'
services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: wheel_strategy
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres123!
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  app:
    build: .
    ports:
      - "8502:8502"
    environment:
      DB_HOST: postgres
      DB_PORT: 5432
    depends_on:
      - postgres
```

### Production Deployment
1. **Database**: Managed PostgreSQL (AWS RDS, Google Cloud SQL)
2. **Application**: Container orchestration (Kubernetes, ECS)
3. **Load Balancer**: Nginx/HAProxy for traffic distribution
4. **Monitoring**: Prometheus + Grafana stack
5. **Logging**: ELK stack (Elasticsearch, Logstash, Kibana)

## Future Architecture Considerations

### Microservices Migration
```
Current: Monolithic Dashboard
Future: Microservices Architecture

┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   UI Service │  │  Scan Service │  │  Sync Service │
└──────────────┘  └──────────────┘  └──────────────┘
       │                 │                   │
       └─────────────────┼───────────────────┘
                         ▼
                   Message Queue
                    (RabbitMQ)
                         │
                         ▼
                 Database Cluster
```

### Event-Driven Architecture
- **Event Sourcing**: Track all state changes
- **CQRS Pattern**: Separate read/write models
- **Real-time Updates**: WebSocket for live data
- **Async Processing**: Background job queue

This architecture provides a robust, scalable foundation for the Database Scan feature while maintaining flexibility for future enhancements and scaling requirements.