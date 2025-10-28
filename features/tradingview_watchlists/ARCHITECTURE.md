# TradingView Watchlists - Technical Architecture

## Table of Contents
1. [System Overview](#system-overview)
2. [Component Architecture](#component-architecture)
3. [Data Flow Architecture](#data-flow-architecture)
4. [Database Design](#database-design)
5. [API Integration Layer](#api-integration-layer)
6. [Frontend Architecture](#frontend-architecture)
7. [Backend Services](#backend-services)
8. [State Management](#state-management)
9. [Security Architecture](#security-architecture)
10. [Performance Optimization](#performance-optimization)
11. [Error Handling](#error-handling)
12. [Deployment Architecture](#deployment-architecture)

## System Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Streamlit Frontend                       │
│  ┌─────────────┬──────────────┬───────────┬──────────────┐ │
│  │  Position   │  Trade       │ Watchlist │   Premium    │ │
│  │  Monitor    │  History     │ Manager   │   Analyzer   │ │
│  └─────────────┴──────────────┴───────────┴──────────────┘ │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    Service Layer                             │
│  ┌──────────────┬────────────────┬────────────────────────┐│
│  │  Robinhood   │  TradingView   │   Market Data         ││
│  │  Integration │  DB Manager     │   Agent              ││
│  └──────────────┴────────────────┴────────────────────────┘│
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                  Data Persistence Layer                      │
│  ┌──────────────┬────────────────┬────────────────────────┐│
│  │  PostgreSQL  │  Redis Cache    │  Session Storage      ││
│  │  Database    │  (Optional)     │  (Streamlit)         ││
│  └──────────────┴────────────────┴────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

### Core Design Principles

1. **Separation of Concerns**: Each component has a single, well-defined responsibility
2. **Data Integrity**: All financial calculations are validated and audited
3. **Real-time Updates**: Live synchronization with external data sources
4. **Fault Tolerance**: Graceful degradation when services are unavailable
5. **Performance First**: Optimized queries and caching strategies

## Component Architecture

### 1. Frontend Components (dashboard.py: lines 1293-1937)

#### Position Monitor Component
```python
class PositionMonitor:
    """
    Responsible for displaying live option positions from Robinhood
    Location: dashboard.py lines 1306-1473
    """

    def __init__(self):
        self.rh_client = RobinhoodClient()
        self.position_calculator = PositionCalculator()

    def fetch_positions(self):
        # Lines 1315-1389
        # 1. Get open positions from Robinhood
        # 2. Enrich with option details
        # 3. Calculate P/L metrics
        # 4. Determine strategy type
        return formatted_positions

    def display_metrics(self, positions):
        # Lines 1390-1409
        # Show aggregated metrics in columns
        # Total positions, premium, P/L, CSPs count
```

#### Trade Logger Component
```python
class TradeLogger:
    """
    Handles closed trade logging with forms
    Location: dashboard.py lines 1412-1463
    """

    def render_log_forms(self, positions):
        # Create expandable forms for each position
        # Capture close price, reason, date
        # Calculate P/L on submission

    def log_trade(self, trade_data):
        # Add to trade_history table
        # Calculate profit metrics
        # Return success confirmation
```

#### Watchlist Manager Component
```python
class WatchlistManager:
    """
    Manages watchlist CRUD operations
    Location: dashboard.py lines 1554-1724
    """

    def __init__(self):
        self.tv_manager = TradingViewDBManager()
        self.sync_service = WatchlistSyncService()

    def auto_sync(self):
        # Lines 1541-1553
        # Check last sync time
        # Load from database if stale
        # Update session state

    def import_watchlist(self, text_input, name):
        # Lines 1726-1772
        # Parse input text
        # Validate symbols
        # Store in database
```

### 2. Service Layer Components

#### TradingViewDBManager (src/tradingview_db_manager.py)
```python
class TradingViewDBManager:
    """
    Database interface for watchlist operations
    """

    def __init__(self):
        self.db_config = self._load_config()
        self.initialize_tables()

    def get_all_symbols_dict(self) -> Dict[str, List[str]]:
        # Returns watchlist_name -> [symbols] mapping

    def import_from_text(self, text: str, name: str) -> List[str]:
        # Parse and store new watchlist

    def get_premiums_for_symbols(self, symbols: List[str], dte: int):
        # Query stock_premiums table with filters
```

#### TradeHistoryManager (src/trade_history_manager.py)
```python
class TradeHistoryManager:
    """
    Manages trade lifecycle and P&L calculations
    """

    def add_trade(self, symbol, strike, expiration, premium, **kwargs):
        # Create new trade record
        # Calculate initial metrics

    def close_trade(self, trade_id, close_price, reason):
        # Update trade status
        # Calculate final P/L
        # Compute performance metrics

    def get_trade_stats(self):
        # Aggregate statistics
        # Win rate, avg days, total P/L
```

#### MarketDataAgent (src/agents/runtime/market_data_agent.py)
```python
class MarketDataAgent:
    """
    Fetches and processes market data
    """

    def get_stock_data(self, symbol):
        # Fetch from yfinance
        # Calculate option premiums
        # Add technical indicators

    async def scan_opportunities(self, symbols):
        # Parallel data fetching
        # Filter by criteria
        # Rank by score
```

### 3. Integration Services

#### Robinhood API Integration
```python
class RobinhoodService:
    """
    Wrapper for robin_stocks library
    """

    def login(self):
        rh.login(username, password)

    def get_option_positions(self):
        positions = rh.get_open_option_positions()
        # Enrich with instrument data
        # Add market prices
        return enriched_positions

    def get_option_details(self, option_id):
        # Get instrument data
        # Get market data
        # Combine and return
```

## Data Flow Architecture

### 1. Position Data Flow

```
Robinhood API
     │
     ▼
get_open_option_positions()
     │
     ▼
Enrich with instrument_data
     │
     ▼
Calculate current values
     │
     ▼
Determine P/L metrics
     │
     ▼
Format for display
     │
     ▼
Streamlit UI
```

### 2. Watchlist Sync Flow

```
TradingView Export / Manual Input
            │
            ▼
    Parse & Validate Symbols
            │
            ▼
    Store in tv_watchlists
            │
            ▼
    Background Sync Service
            │
            ├──► Yahoo Finance API
            │         │
            │         ▼
            │    Stock Prices
            │
            └──► Options Chain API
                      │
                      ▼
                Premium Calculations
                      │
                      ▼
                stock_premiums table
```

### 3. Trade Lifecycle Flow

```
Open Position (Robinhood)
          │
          ▼
    Monitor in UI
          │
          ▼
    User Closes Trade
          │
          ▼
    Log via Form
          │
          ▼
    add_trade()
          │
          ▼
    close_trade()
          │
          ▼
    Calculate P/L
          │
          ▼
    Update Statistics
```

## Database Design

### Entity Relationship Diagram

```
┌──────────────────┐        ┌─────────────────────┐
│  tv_watchlists   │───1:N──│ tv_watchlist_symbols│
└──────────────────┘        └─────────────────────┘
         │                            │
         │                            │
         1:N                          │
         │                            ▼
         ▼                    ┌──────────────┐
┌──────────────────┐          │  stock_data  │
│ tv_refresh_history│         └──────────────┘
└──────────────────┘                  │
                                     1:N
                                      ▼
                              ┌──────────────────┐
                              │ stock_premiums   │
                              └──────────────────┘

┌──────────────────┐
│  trade_history   │
└──────────────────┘
```

### Table Schemas

#### tv_watchlists
```sql
CREATE TABLE tv_watchlists (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_refresh TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    symbol_count INTEGER DEFAULT 0
);
```

#### tv_watchlist_symbols
```sql
CREATE TABLE tv_watchlist_symbols (
    id SERIAL PRIMARY KEY,
    watchlist_id INTEGER REFERENCES tv_watchlists(id) ON DELETE CASCADE,
    symbol VARCHAR(20) NOT NULL,
    company_name VARCHAR(255),
    sector VARCHAR(100),
    industry VARCHAR(100),
    market_cap BIGINT,
    last_price DECIMAL(10,2),
    volume BIGINT,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(watchlist_id, symbol)
);
```

#### stock_premiums
```sql
CREATE TABLE stock_premiums (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    strike_price DECIMAL(10,2),
    dte INTEGER,
    premium DECIMAL(10,2),
    delta DECIMAL(5,4),
    theta DECIMAL(10,4),
    implied_volatility DECIMAL(5,2),
    bid DECIMAL(10,2),
    ask DECIMAL(10,2),
    volume INTEGER,
    open_interest INTEGER,
    monthly_return DECIMAL(5,2),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_symbol_dte (symbol, dte),
    INDEX idx_delta (delta)
);
```

#### trade_history
```sql
CREATE TABLE trade_history (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    strike_price DECIMAL(10,2),
    expiration_date DATE,
    premium_collected DECIMAL(10,2),
    contracts INTEGER DEFAULT 1,
    open_date DATE,
    close_date DATE,
    close_price DECIMAL(10,2),
    close_reason VARCHAR(50),
    dte_at_open INTEGER,
    days_held INTEGER,
    profit_loss DECIMAL(10,2),
    profit_loss_percent DECIMAL(5,2),
    annualized_return DECIMAL(5,2),
    strategy_type VARCHAR(50),
    status VARCHAR(20) DEFAULT 'open',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_symbol (symbol),
    INDEX idx_status (status),
    INDEX idx_dates (open_date, close_date)
);
```

### Database Indexes

```sql
-- Performance critical indexes
CREATE INDEX idx_watchlist_symbols_symbol ON tv_watchlist_symbols(symbol);
CREATE INDEX idx_watchlist_symbols_watchlist ON tv_watchlist_symbols(watchlist_id);
CREATE INDEX idx_premiums_symbol_dte ON stock_premiums(symbol, dte);
CREATE INDEX idx_premiums_delta_range ON stock_premiums(delta) WHERE delta BETWEEN -0.4 AND -0.25;
CREATE INDEX idx_trade_history_symbol ON trade_history(symbol);
CREATE INDEX idx_trade_history_status ON trade_history(status);
```

## API Integration Layer

### 1. Robinhood API

#### Authentication
```python
def authenticate():
    """
    Handles Robinhood login with MFA support
    """
    return rh.login(
        username=os.getenv('ROBINHOOD_USERNAME'),
        password=os.getenv('ROBINHOOD_PASSWORD'),
        store_session=True
    )
```

#### Position Fetching
```python
def fetch_positions():
    """
    Gets all open option positions with enriched data
    """
    positions = rh.get_open_option_positions()

    for position in positions:
        # Get option instrument details
        instrument = rh.get_option_instrument_data_by_id(
            position['option_id']
        )

        # Get current market data
        market_data = rh.get_option_market_data_by_id(
            position['option_id']
        )

        # Merge data
        position.update(instrument)
        position.update(market_data[0] if market_data else {})

    return positions
```

### 2. Yahoo Finance Integration

#### Stock Data Fetching
```python
def get_stock_data(symbol):
    """
    Fetches current stock data from yfinance
    """
    ticker = yf.Ticker(symbol)

    # Get current price
    info = ticker.info
    current_price = info.get('currentPrice', 0)

    # Get options chain
    options = ticker.options  # Available expiration dates

    # Get specific expiration
    target_date = find_30_day_expiration(options)
    opt_chain = ticker.option_chain(target_date)

    return {
        'price': current_price,
        'options': process_option_chain(opt_chain.puts)
    }
```

### 3. Background Sync Service

#### Watchlist Sync Process
```python
class WatchlistSyncService:
    """
    Handles background synchronization of watchlist data
    """

    def sync_watchlist(self, watchlist_name):
        """
        Launched as subprocess for non-blocking sync
        """
        # Get symbols from database
        symbols = self.get_watchlist_symbols(watchlist_name)

        # Parallel fetch stock data
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = executor.map(self.fetch_symbol_data, symbols)

        # Bulk update database
        self.bulk_update_premiums(results)

        # Update refresh timestamp
        self.update_watchlist_timestamp(watchlist_name)
```

## Frontend Architecture

### Streamlit Component Structure

#### Page Layout
```python
# Main page structure (lines 1293-1937)
def render_tradingview_watchlists():
    st.title("TradingView Watchlists")

    # Section 1: Current Positions
    render_current_positions()

    # Section 2: Trade History
    render_trade_history()

    # Section 3: Watchlist Tabs
    tabs = st.tabs([
        "Auto-Sync",
        "Import Watchlist",
        "My Watchlist Analysis",
        "Saved Watchlists",
        "Quick Scan"
    ])

    with tabs[0]:
        render_auto_sync()
    # ... other tabs
```

#### State Management
```python
# Session state usage
if 'watchlists_db' not in st.session_state:
    st.session_state['watchlists_db'] = tv_manager.get_all_symbols_dict()

if 'last_sync' not in st.session_state:
    st.session_state['last_sync'] = datetime.min

# Update on user action
if st.button("Refresh"):
    st.session_state['watchlists_db'] = fetch_new_data()
    st.session_state['last_sync'] = datetime.now()
    st.rerun()
```

#### Data Display Components
```python
def render_positions_table(positions):
    """
    Displays positions with formatting and metrics
    """
    # Create DataFrame
    df = pd.DataFrame(positions)

    # Format columns
    df['P/L'] = df['P/L'].apply(lambda x: f"${x:.2f}")
    df['P/L %'] = df['P/L %'].apply(lambda x: f"{x:.1f}%")

    # Display with column config
    st.dataframe(
        df,
        column_config={
            "Symbol": st.column_config.TextColumn("Symbol"),
            "Strike": st.column_config.NumberColumn("Strike", format="$%.2f"),
            "P/L": st.column_config.NumberColumn("P/L", format="$%.2f"),
            # ... other columns
        }
    )
```

## Backend Services

### 1. Database Connection Pool

```python
class DatabasePool:
    """
    Manages PostgreSQL connection pooling
    """

    def __init__(self):
        self.pool = psycopg2.pool.SimpleConnectionPool(
            1, 20,  # min, max connections
            host=os.getenv('DB_HOST'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )

    def get_connection(self):
        return self.pool.getconn()

    def return_connection(self, conn):
        self.pool.putconn(conn)
```

### 2. Cache Layer (Optional)

```python
class RedisCache:
    """
    Caches frequently accessed data
    """

    def __init__(self):
        self.redis = redis.Redis(
            host='localhost',
            port=6379,
            decode_responses=True
        )

    def cache_premiums(self, symbol, data, ttl=300):
        """
        Cache premium data for 5 minutes
        """
        key = f"premiums:{symbol}"
        self.redis.setex(
            key,
            ttl,
            json.dumps(data)
        )
```

### 3. Background Task Queue

```python
class BackgroundTaskQueue:
    """
    Manages async task execution
    """

    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=5)
        self.tasks = []

    def submit_sync_task(self, watchlist_name):
        """
        Submit watchlist sync as background task
        """
        future = self.executor.submit(
            sync_watchlist_data,
            watchlist_name
        )
        self.tasks.append(future)
        return future
```

## State Management

### Session State Architecture

```python
# Global state management
class SessionStateManager:
    """
    Centralized session state management
    """

    KEYS = {
        'watchlists_db': dict,          # Watchlist data
        'last_sync': datetime,           # Last sync time
        'current_watchlist': list,       # Active symbols
        'watchlist_analysis': list,      # Analysis results
        'rh_connected': bool,            # Robinhood status
        'trade_history_cache': dict,     # Cached trades
    }

    @classmethod
    def initialize(cls):
        """
        Initialize all session state keys
        """
        for key, dtype in cls.KEYS.items():
            if key not in st.session_state:
                st.session_state[key] = dtype()

    @classmethod
    def get(cls, key, default=None):
        """
        Safe getter with default
        """
        return st.session_state.get(key, default)
```

### Data Flow States

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Initial   │─────▶│   Loading    │─────▶│   Loaded    │
└─────────────┘      └──────────────┘      └─────────────┘
                            │                      │
                            ▼                      ▼
                     ┌──────────────┐      ┌─────────────┐
                     │    Error     │      │   Syncing   │
                     └──────────────┘      └─────────────┘
                                                   │
                                                   ▼
                                            ┌─────────────┐
                                            │   Updated   │
                                            └─────────────┘
```

## Security Architecture

### 1. Credential Management

```python
class CredentialManager:
    """
    Secure credential handling
    """

    def __init__(self):
        load_dotenv()
        self.credentials = {
            'robinhood': {
                'username': os.getenv('ROBINHOOD_USERNAME'),
                'password': os.getenv('ROBINHOOD_PASSWORD')
            },
            'database': {
                'host': os.getenv('DB_HOST'),
                'password': os.getenv('DB_PASSWORD')
            }
        }

    def get_credential(self, service, key):
        """
        Retrieve credential with validation
        """
        if service not in self.credentials:
            raise ValueError(f"Unknown service: {service}")

        value = self.credentials[service].get(key)
        if not value:
            raise ValueError(f"Missing credential: {service}.{key}")

        return value
```

### 2. Input Validation

```python
class InputValidator:
    """
    Validates and sanitizes user input
    """

    @staticmethod
    def validate_symbol(symbol: str) -> str:
        """
        Validate stock symbol
        """
        # Remove whitespace
        symbol = symbol.strip().upper()

        # Check format (letters only, max 5 chars)
        if not re.match(r'^[A-Z]{1,5}$', symbol):
            raise ValueError(f"Invalid symbol: {symbol}")

        # Check against blacklist
        if symbol in BLACKLISTED_SYMBOLS:
            raise ValueError(f"Blacklisted symbol: {symbol}")

        return symbol

    @staticmethod
    def validate_price(price: float) -> float:
        """
        Validate price input
        """
        if price < 0:
            raise ValueError("Price cannot be negative")

        if price > 1000000:
            raise ValueError("Price exceeds maximum")

        return round(price, 2)
```

### 3. SQL Injection Prevention

```python
class SafeQueryBuilder:
    """
    Builds parameterized queries
    """

    @staticmethod
    def build_premium_query(symbols, filters):
        """
        Build safe parameterized query
        """
        query = """
            SELECT * FROM stock_premiums
            WHERE symbol = ANY(%s)
        """
        params = [symbols]

        if filters.get('min_premium'):
            query += " AND premium >= %s"
            params.append(filters['min_premium'])

        if filters.get('dte_range'):
            query += " AND dte BETWEEN %s AND %s"
            params.extend(filters['dte_range'])

        return query, params
```

## Performance Optimization

### 1. Query Optimization

```python
# Optimized query with proper indexing
def get_watchlist_premiums_optimized(symbols, dte_target=30):
    """
    Fetches premiums with optimized query
    """
    query = """
        WITH latest_premiums AS (
            SELECT DISTINCT ON (symbol)
                symbol, strike_price, premium, delta, monthly_return
            FROM stock_premiums
            WHERE
                symbol = ANY(%s)
                AND dte BETWEEN %s AND %s
                AND ABS(delta) BETWEEN 0.25 AND 0.40
            ORDER BY symbol, monthly_return DESC
        )
        SELECT * FROM latest_premiums
        ORDER BY monthly_return DESC
    """

    return execute_query(query, [symbols, dte_target-2, dte_target+2])
```

### 2. Caching Strategy

```python
class CacheStrategy:
    """
    Multi-level caching implementation
    """

    def __init__(self):
        self.memory_cache = {}  # In-memory cache
        self.redis_cache = RedisCache()  # Redis cache

    def get_cached_data(self, key, fetcher, ttl=300):
        """
        Try memory -> Redis -> Database
        """
        # Check memory cache
        if key in self.memory_cache:
            if self.memory_cache[key]['expires'] > time.time():
                return self.memory_cache[key]['data']

        # Check Redis
        redis_data = self.redis_cache.get(key)
        if redis_data:
            self.memory_cache[key] = {
                'data': redis_data,
                'expires': time.time() + 60
            }
            return redis_data

        # Fetch from source
        data = fetcher()

        # Cache in both layers
        self.redis_cache.setex(key, ttl, data)
        self.memory_cache[key] = {
            'data': data,
            'expires': time.time() + 60
        }

        return data
```

### 3. Batch Processing

```python
class BatchProcessor:
    """
    Processes data in optimized batches
    """

    def update_premiums_batch(self, symbol_data_pairs):
        """
        Bulk update premiums in database
        """
        conn = get_connection()
        cur = conn.cursor()

        try:
            # Use COPY for bulk insert
            with tempfile.NamedTemporaryFile(mode='w') as f:
                writer = csv.writer(f)

                for symbol, data in symbol_data_pairs:
                    for option in data['options']:
                        writer.writerow([
                            symbol,
                            option['strike'],
                            option['premium'],
                            option['delta'],
                            # ... other fields
                        ])

                f.flush()
                f.seek(0)

                cur.copy_from(
                    f,
                    'stock_premiums',
                    columns=['symbol', 'strike', 'premium', 'delta']
                )

            conn.commit()

        finally:
            cur.close()
            conn.close()
```

## Error Handling

### 1. Exception Hierarchy

```python
class TradingViewWatchlistError(Exception):
    """Base exception for all watchlist errors"""
    pass

class RobinhoodConnectionError(TradingViewWatchlistError):
    """Raised when Robinhood API fails"""
    pass

class DatabaseError(TradingViewWatchlistError):
    """Raised for database operations"""
    pass

class ValidationError(TradingViewWatchlistError):
    """Raised for invalid input"""
    pass

class SyncError(TradingViewWatchlistError):
    """Raised during sync operations"""
    pass
```

### 2. Error Recovery

```python
class ErrorRecovery:
    """
    Implements retry and fallback strategies
    """

    @staticmethod
    def with_retry(func, max_attempts=3, delay=1):
        """
        Retry failed operations
        """
        for attempt in range(max_attempts):
            try:
                return func()
            except Exception as e:
                if attempt == max_attempts - 1:
                    raise

                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                time.sleep(delay * (2 ** attempt))  # Exponential backoff

    @staticmethod
    def with_fallback(primary_func, fallback_func):
        """
        Use fallback on primary failure
        """
        try:
            return primary_func()
        except Exception as e:
            logger.error(f"Primary failed: {e}, using fallback")
            return fallback_func()
```

### 3. User Error Feedback

```python
def display_error(error_type, message, recovery_action=None):
    """
    Display user-friendly error messages
    """
    if error_type == "connection":
        st.error(f"Connection Error: {message}")
        if recovery_action:
            if st.button("Retry"):
                recovery_action()

    elif error_type == "validation":
        st.warning(f"Invalid Input: {message}")

    elif error_type == "sync":
        st.info(f"Sync Issue: {message}")
        st.caption("Data may be stale. Try refreshing.")

    else:
        st.error(f"Error: {message}")
        st.caption("Please contact support if this persists.")
```

## Deployment Architecture

### 1. Container Structure

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_SERVER_PORT=8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run application
CMD ["streamlit", "run", "dashboard.py"]
```

### 2. Docker Compose Configuration

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8501:8501"
    environment:
      - DB_HOST=postgres
      - DB_PORT=5432
      - DB_NAME=magnus
      - DB_USER=postgres
      - DB_PASSWORD=${DB_PASSWORD}
      - ROBINHOOD_USERNAME=${ROBINHOOD_USERNAME}
      - ROBINHOOD_PASSWORD=${ROBINHOOD_PASSWORD}
    depends_on:
      - postgres
      - redis
    volumes:
      - ./data:/app/data
    restart: unless-stopped

  postgres:
    image: postgres:14
    environment:
      - POSTGRES_DB=magnus
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./sql/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  sync_service:
    build: .
    command: python src/watchlist_sync_service.py
    environment:
      - DB_HOST=postgres
      - DB_PORT=5432
      - DB_NAME=magnus
      - DB_USER=postgres
      - DB_PASSWORD=${DB_PASSWORD}
    depends_on:
      - postgres
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

### 3. Production Considerations

#### Scaling Strategy
```python
# Horizontal scaling configuration
class ScalingConfig:
    """
    Production scaling parameters
    """

    # Database connections
    DB_POOL_MIN = 5
    DB_POOL_MAX = 20

    # Background workers
    SYNC_WORKERS = 10
    CALC_WORKERS = 5

    # Cache settings
    CACHE_TTL = 300  # 5 minutes
    CACHE_SIZE = 1000  # Max entries

    # Rate limiting
    API_RATE_LIMIT = 100  # per minute
    DB_QUERY_TIMEOUT = 30  # seconds
```

#### Monitoring and Logging
```python
class MonitoringService:
    """
    Application monitoring and metrics
    """

    def __init__(self):
        self.metrics = {
            'api_calls': 0,
            'db_queries': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'errors': 0
        }

    def track_api_call(self, endpoint, duration):
        """
        Track API performance
        """
        self.metrics['api_calls'] += 1

        # Log slow calls
        if duration > 1.0:
            logger.warning(f"Slow API call: {endpoint} took {duration:.2f}s")

    def export_metrics(self):
        """
        Export to monitoring service (Prometheus, DataDog, etc.)
        """
        return self.metrics
```

## Testing Architecture

### 1. Unit Testing

```python
# tests/test_trade_history.py
class TestTradeHistory(unittest.TestCase):
    """
    Test trade history calculations
    """

    def test_profit_calculation(self):
        """
        Test P/L calculation accuracy
        """
        manager = TradeHistoryManager()

        trade_id = manager.add_trade(
            symbol="AAPL",
            strike_price=150.00,
            premium_collected=200.00,
            contracts=1
        )

        result = manager.close_trade(
            trade_id=trade_id,
            close_price=50.00,
            close_reason="early_close"
        )

        self.assertEqual(result['profit_loss'], 150.00)
        self.assertEqual(result['profit_loss_percent'], 75.0)
```

### 2. Integration Testing

```python
# tests/test_integration.py
class TestRobinhoodIntegration(unittest.TestCase):
    """
    Test Robinhood API integration
    """

    @mock.patch('robin_stocks.robinhood.get_open_option_positions')
    def test_position_fetching(self, mock_positions):
        """
        Test position data processing
        """
        mock_positions.return_value = [
            {
                'option_id': '123',
                'quantity': '1',
                'average_price': '2.50',
                'type': 'short'
            }
        ]

        positions = fetch_positions()

        self.assertEqual(len(positions), 1)
        self.assertEqual(positions[0]['total_premium'], 250.00)
```

### 3. Performance Testing

```python
# tests/test_performance.py
class TestPerformance(unittest.TestCase):
    """
    Performance and load testing
    """

    def test_bulk_premium_query(self):
        """
        Test query performance with large dataset
        """
        symbols = ['AAPL', 'MSFT', 'GOOGL'] * 100  # 300 symbols

        start = time.time()
        results = get_premiums_for_symbols(symbols)
        duration = time.time() - start

        self.assertLess(duration, 2.0)  # Should complete in < 2 seconds
        self.assertEqual(len(results), 300)
```

## Code Quality Standards

### 1. Type Hints

```python
from typing import Dict, List, Optional, Any, Tuple
from decimal import Decimal
from datetime import datetime

def calculate_profit_loss(
    premium_collected: Decimal,
    close_price: Decimal,
    contracts: int = 1,
    position_type: str = 'short'
) -> Tuple[Decimal, float]:
    """
    Calculate P/L for option position

    Returns:
        Tuple of (profit_loss, profit_loss_percent)
    """
    if position_type == 'short':
        profit_loss = premium_collected - close_price
    else:
        profit_loss = close_price - premium_collected

    profit_loss_percent = float(
        (profit_loss / premium_collected) * 100
    )

    return profit_loss, profit_loss_percent
```

### 2. Documentation Standards

```python
class WatchlistManager:
    """
    Manages TradingView watchlist operations.

    This class provides methods for importing, syncing, and analyzing
    watchlists stored in the PostgreSQL database. It integrates with
    multiple data sources including TradingView exports and Yahoo Finance.

    Attributes:
        db_manager: Database interface for watchlist operations
        sync_service: Background synchronization service
        cache: Optional caching layer for performance

    Example:
        manager = WatchlistManager()
        symbols = manager.import_watchlist("AAPL,MSFT,GOOGL", "Tech Stocks")
        analysis = manager.analyze_watchlist("Tech Stocks")
    """
```

### 3. Error Handling Standards

```python
def safe_operation(func):
    """
    Decorator for safe operation execution with logging
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationError as e:
            logger.warning(f"Validation error in {func.__name__}: {e}")
            st.warning(str(e))
        except DatabaseError as e:
            logger.error(f"Database error in {func.__name__}: {e}")
            st.error("Database error. Please try again.")
        except Exception as e:
            logger.exception(f"Unexpected error in {func.__name__}")
            st.error("An unexpected error occurred.")
        return None
    return wrapper
```

## Future Architecture Considerations

### Microservices Migration Path

```
Current Monolith                    Future Microservices
┌──────────────┐                   ┌─────────────────┐
│              │                   │   API Gateway   │
│   Streamlit  │                   └────────┬────────┘
│   Dashboard  │                            │
│              │         ┌──────────────────┼──────────────────┐
│              │         │                  │                  │
└──────────────┘         ▼                  ▼                  ▼
                   ┌──────────┐      ┌──────────┐      ┌──────────┐
                   │ Position │      │Watchlist │      │  Trade   │
                   │ Service  │      │ Service  │      │ History  │
                   └──────────┘      └──────────┘      └──────────┘
```

### Event-Driven Architecture

```python
class EventBus:
    """
    Future event-driven architecture foundation
    """

    events = {
        'position.opened': [],
        'position.closed': [],
        'watchlist.updated': [],
        'premium.calculated': [],
        'trade.logged': []
    }

    @classmethod
    def publish(cls, event_type: str, data: Dict[str, Any]):
        """
        Publish event to subscribers
        """
        for handler in cls.events.get(event_type, []):
            handler(data)

    @classmethod
    def subscribe(cls, event_type: str, handler):
        """
        Subscribe to event type
        """
        cls.events[event_type].append(handler)
```

### API Layer Addition

```python
# Future REST API layer
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class PositionResponse(BaseModel):
    symbol: str
    strategy: str
    strike: float
    expiration: str
    profit_loss: float

@app.get("/api/v1/positions")
async def get_positions():
    """
    REST endpoint for position data
    """
    positions = fetch_positions()
    return [PositionResponse(**pos) for pos in positions]

@app.post("/api/v1/trades/log")
async def log_trade(trade: TradeLog):
    """
    REST endpoint for trade logging
    """
    manager = TradeHistoryManager()
    trade_id = manager.add_trade(**trade.dict())
    return {"trade_id": trade_id}
```

## Summary

The TradingView Watchlists architecture implements a robust, scalable system for option trading management. Key architectural achievements include:

1. **Clean Separation**: Service layer abstraction between UI and data
2. **Performance Optimization**: Caching, batch processing, and query optimization
3. **Reliability**: Error recovery, validation, and monitoring
4. **Extensibility**: Modular design supporting future enhancements
5. **Security**: Credential management and input validation

The architecture supports both current monolithic deployment and future microservices migration, ensuring long-term maintainability and scalability.