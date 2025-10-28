# Earnings Calendar Technical Specification

## Table of Contents

1. [API Specifications](#api-specifications)
2. [Database Specifications](#database-specifications)
3. [Interface Specifications](#interface-specifications)
4. [Data Format Specifications](#data-format-specifications)
5. [Business Logic Specifications](#business-logic-specifications)
6. [Integration Specifications](#integration-specifications)
7. [Performance Specifications](#performance-specifications)
8. [Error Handling Specifications](#error-handling-specifications)
9. [Security Specifications](#security-specifications)
10. [Testing Specifications](#testing-specifications)

## API Specifications

### 1. Internal API Methods

#### EarningsManager Class API

##### Constructor
```python
def __init__(self, db_config: Optional[Dict] = None)
```

**Parameters:**
- `db_config` (Optional[Dict]): Database configuration dictionary

**Configuration Schema:**
```python
{
    'host': str,      # Database host (default: 'localhost')
    'port': str,      # Database port (default: '5432')
    'user': str,      # Database user (default: 'postgres')
    'password': str,  # Database password
    'database': str   # Database name (default: 'magnus')
}
```

**Returns:** EarningsManager instance

**Raises:**
- `psycopg2.OperationalError`: Database connection failed
- `KeyError`: Missing required configuration

---

##### get_earnings_events
```python
def get_earnings_events(
    self,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    time_filter: str = "all",
    sector_filter: Optional[str] = None,
    symbols: Optional[List[str]] = None
) -> pd.DataFrame
```

**Parameters:**
- `start_date` (Optional[date]): Filter events >= this date
- `end_date` (Optional[date]): Filter events <= this date
- `time_filter` (str): One of ["all", "BMO", "AMC"]
- `sector_filter` (Optional[str]): Sector name or "All Sectors"
- `symbols` (Optional[List[str]]): List of stock symbols

**Returns:** pandas.DataFrame with columns:
```python
[
    'id',                  # int: Primary key
    'symbol',              # str: Stock ticker
    'earnings_date',       # datetime: Earnings announcement date
    'earnings_time',       # str: BMO/AMC/null
    'eps_estimate',        # float: Estimated EPS
    'eps_actual',          # float: Actual EPS
    'revenue_estimate',    # float: Estimated revenue
    'revenue_actual',      # float: Actual revenue
    'surprise_percent',    # float: EPS surprise %
    'status',              # str: beat/miss/inline/pending
    'surprise_pct',        # float: Calculated surprise
    'expected_move',       # float: Expected price move
    'company_name',        # str: Full company name
    'sector',              # str: Sector classification
    'industry',            # str: Industry classification
    'market_cap',          # float: Market capitalization
    'current_price'        # float: Current stock price
]
```

**Raises:**
- `psycopg2.DatabaseError`: Query execution failed
- `ValueError`: Invalid filter parameters

---

##### get_historical_earnings
```python
def get_historical_earnings(
    self,
    symbol: str,
    limit: int = 12
) -> pd.DataFrame
```

**Parameters:**
- `symbol` (str): Stock ticker symbol
- `limit` (int): Maximum records to return (default: 12)

**Returns:** pandas.DataFrame with columns:
```python
[
    'id',              # int: Primary key
    'symbol',          # str: Stock ticker
    'report_date',     # date: Earnings report date
    'quarter',         # int: Quarter number (1-4)
    'year',            # int: Fiscal year
    'eps_actual',      # float: Actual EPS
    'eps_estimate',    # float: Estimated EPS
    'call_datetime',   # datetime: Earnings call time
    'call_replay_url', # str: URL to call replay
    'surprise_pct'     # float: Calculated surprise %
]
```

---

##### sync_robinhood_earnings
```python
def sync_robinhood_earnings(
    self,
    symbols: List[str],
    progress_callback: Optional[callable] = None
) -> Dict[str, Any]
```

**Parameters:**
- `symbols` (List[str]): List of symbols to sync
- `progress_callback` (Optional[callable]): Callback function(current, total, symbol)

**Callback Signature:**
```python
def progress_callback(current: int, total: int, symbol: str) -> None
```

**Returns:**
```python
{
    'success': bool,           # Operation success status
    'synced': int,             # Number of symbols synced
    'errors': int,             # Number of errors
    'total': int,              # Total symbols processed
    'error_symbols': List[str] # Symbols that failed
}
```

**Raises:**
- `EnvironmentError`: Missing Robinhood credentials
- `AuthenticationError`: Login failed

---

##### add_earnings_event
```python
def add_earnings_event(
    self,
    symbol: str,
    earnings_date: datetime,
    earnings_time: Optional[str] = None,
    eps_estimate: Optional[float] = None,
    **kwargs
) -> bool
```

**Parameters:**
- `symbol` (str): Stock ticker symbol
- `earnings_date` (datetime): Earnings announcement datetime
- `earnings_time` (Optional[str]): "BMO" or "AMC"
- `eps_estimate` (Optional[float]): Estimated EPS
- `**kwargs`: Additional fields from earnings_events schema

**Valid kwargs:**
```python
{
    'eps_actual': float,
    'revenue_estimate': float,
    'revenue_actual': float,
    'surprise_percent': float,
    'pre_earnings_iv': float,
    'post_earnings_iv': float,
    'pre_earnings_price': float,
    'post_earnings_price': float,
    'price_move_percent': float,
    'volume_ratio': float,
    'options_volume': int,
    'whisper_number': float
}
```

**Returns:** bool - Success status

---

### 2. Robinhood API Integration

#### Authentication
```python
robin_stocks.robinhood.login(
    username: str,
    password: str,
    expiresIn: int = 86400,
    scope: str = 'internal',
    by_sms: bool = True
) -> Dict
```

**Response:**
```python
{
    'access_token': str,
    'token_type': 'Bearer',
    'expires_in': int,
    'refresh_token': str,
    'scope': str
}
```

#### Get Earnings
```python
robin_stocks.robinhood.get_earnings(
    symbol: str,
    info: Optional[str] = None
) -> List[Dict]
```

**Response Schema:**
```python
[
    {
        'symbol': str,
        'year': int,
        'quarter': int,
        'eps': {
            'actual': float,
            'estimate': float
        },
        'report': {
            'date': str,  # ISO format date
            'timing': str,  # 'bmo' or 'amc'
            'verified': bool
        },
        'call': {
            'datetime': str,  # ISO format datetime
            'broadcast_url': str,
            'replay_url': str
        }
    }
]
```

## Database Specifications

### 1. Table Schemas

#### earnings_events Table

```sql
CREATE TABLE earnings_events (
    -- Primary Key
    id SERIAL PRIMARY KEY,

    -- Core Fields
    symbol VARCHAR(10) NOT NULL,
    earnings_date TIMESTAMP WITH TIME ZONE,
    earnings_time VARCHAR(10) CHECK (earnings_time IN ('BMO', 'AMC', NULL)),

    -- EPS Data
    eps_estimate DECIMAL(10, 2),
    eps_actual DECIMAL(10, 2),

    -- Revenue Data
    revenue_estimate DECIMAL(15, 2),
    revenue_actual DECIMAL(15, 2),

    -- Calculated Fields
    surprise_percent DECIMAL(10, 2),

    -- Options Data
    pre_earnings_iv DECIMAL(10, 4) CHECK (pre_earnings_iv >= 0 AND pre_earnings_iv <= 10),
    post_earnings_iv DECIMAL(10, 4) CHECK (post_earnings_iv >= 0 AND post_earnings_iv <= 10),

    -- Price Data
    pre_earnings_price DECIMAL(10, 2) CHECK (pre_earnings_price > 0),
    post_earnings_price DECIMAL(10, 2) CHECK (post_earnings_price > 0),
    price_move_percent DECIMAL(10, 2),

    -- Volume Data
    volume_ratio DECIMAL(10, 2) CHECK (volume_ratio > 0),
    options_volume INTEGER CHECK (options_volume >= 0),

    -- Additional Data
    whisper_number DECIMAL(10, 2),

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    -- Constraints
    UNIQUE(symbol, earnings_date)
);
```

#### earnings_history Table

```sql
CREATE TABLE earnings_history (
    -- Primary Key
    id SERIAL PRIMARY KEY,

    -- Core Fields
    symbol VARCHAR(20) NOT NULL,
    report_date DATE NOT NULL,

    -- Period Data
    quarter INTEGER CHECK (quarter BETWEEN 1 AND 4),
    year INTEGER CHECK (year BETWEEN 1900 AND 2100),

    -- EPS Data
    eps_actual NUMERIC(10, 4),
    eps_estimate NUMERIC(10, 4),

    -- Call Information
    call_datetime TIMESTAMP WITH TIME ZONE,
    call_replay_url TEXT,

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Constraints
    UNIQUE(symbol, report_date)
);
```

### 2. Index Specifications

```sql
-- Performance Indexes
CREATE INDEX idx_earnings_date ON earnings_events(earnings_date DESC);
CREATE INDEX idx_earnings_events_symbol ON earnings_events(symbol);
CREATE INDEX idx_earnings_history_symbol ON earnings_history(symbol);

-- Composite Indexes
CREATE INDEX idx_symbol_date ON earnings_events(symbol, earnings_date);
CREATE INDEX idx_date_time ON earnings_events(earnings_date, earnings_time);

-- Partial Indexes
CREATE INDEX idx_pending_earnings ON earnings_events(earnings_date)
WHERE eps_actual IS NULL;

CREATE INDEX idx_recent_earnings ON earnings_events(earnings_date)
WHERE earnings_date >= NOW() - INTERVAL '30 days';
```

### 3. Triggers

```sql
-- Update timestamp trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_earnings_events_updated_at
BEFORE UPDATE ON earnings_events
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

## Interface Specifications

### 1. Streamlit UI Components

#### Page Layout
```python
# Page configuration
st.set_page_config(
    page_title="Earnings Calendar",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded"
)
```

#### Component Hierarchy
```
show_earnings_calendar()
├── Database Initialization Section
│   ├── st.warning() - Status message
│   ├── st.columns() - Layout columns
│   ├── st.info() - Instructions
│   └── st.button() - Initialize trigger
├── Main Interface Section
│   ├── Metrics Row
│   │   ├── st.metric() - Event count
│   │   ├── st.button() - Sync action
│   │   └── st.caption() - Auto-sync notice
│   ├── Filter Row
│   │   ├── st.selectbox() - Date range
│   │   ├── st.selectbox() - Time filter
│   │   └── st.selectbox() - Result filter
│   └── Data Display
│       ├── Summary Metrics
│       │   ├── st.metric() - Total
│       │   ├── st.metric() - Beats
│       │   ├── st.metric() - Misses
│       │   └── st.metric() - Pending
│       ├── st.dataframe() - Data table
│       └── st.download_button() - CSV export
└── Progress Indicators
    ├── st.spinner() - Loading states
    ├── st.progress() - Sync progress
    └── st.empty() - Status updates
```

### 2. User Interaction Flows

#### Initialization Flow
```python
if not table_exists:
    # Show initialization UI
    if st.button("🔧 Initialize Database"):
        with st.spinner("Creating tables..."):
            # Create tables
            # Show success
            st.rerun()
```

#### Sync Flow
```python
if st.button("🔄 Sync Earnings"):
    with st.spinner("Syncing..."):
        progress_bar = st.progress(0)
        status_text = st.empty()

        for i, symbol in enumerate(symbols):
            status_text.text(f"Syncing {symbol}...")
            progress_bar.progress((i + 1) / len(symbols))

        st.success("Sync complete!")
        st.rerun()
```

## Data Format Specifications

### 1. Date/Time Formats

```python
# Database storage
earnings_date: "2024-01-15 16:00:00-05:00"  # ISO 8601 with timezone

# Display format
display_date: "2024-01-15 16:00"  # Simplified for UI

# API format (Robinhood)
api_date: "2024-01-15"  # Date only

# Time indicators
earnings_time: "BMO" | "AMC" | None
```

### 2. Numeric Formats

```python
# EPS values
eps_estimate: Decimal('1.23')  # 2 decimal places
eps_actual: Decimal('1.45')    # 2 decimal places

# Revenue (in millions)
revenue_estimate: Decimal('1234567890.00')  # Full value
revenue_actual: Decimal('1234567890.00')

# Percentages
surprise_percent: Decimal('17.89')  # 2 decimal places
price_move_percent: Decimal('-3.45')  # Can be negative

# Implied Volatility
pre_earnings_iv: Decimal('0.3456')  # 4 decimal places (34.56%)
```

### 3. CSV Export Format

```csv
Symbol,Date,Time,EPS Est,EPS Act,Rev Est,Rev Act,Result,Company,Sector
AAPL,2024-01-15 16:00,AMC,1.23,1.45,123456.00,124567.00,Beat,Apple Inc.,Technology
MSFT,2024-01-16 07:30,BMO,2.34,2.35,234567.00,235678.00,Meet,Microsoft Corporation,Technology
```

## Business Logic Specifications

### 1. Status Calculation

```python
def calculate_status(eps_actual, eps_estimate):
    if eps_actual is None:
        return 'pending'
    elif eps_estimate is None:
        return 'reported'
    elif eps_actual > eps_estimate:
        return 'beat'
    elif eps_actual < eps_estimate:
        return 'miss'
    else:
        return 'inline'
```

### 2. Surprise Percentage

```python
def calculate_surprise_percent(eps_actual, eps_estimate):
    if eps_actual is None or eps_estimate is None:
        return 0.0
    if eps_estimate == 0:
        return 0.0
    return ((eps_actual - eps_estimate) / abs(eps_estimate)) * 100
```

### 3. Expected Move

```python
def calculate_expected_move(current_price, implied_volatility):
    """
    Calculate expected move using simplified Black-Scholes approximation
    Expected Move = Stock Price × IV × sqrt(DTE/365)
    For 1-day event: ≈ Stock Price × IV × 0.0523
    """
    if current_price is None or implied_volatility is None:
        return 0.0

    # Simplified for 1-day move
    time_factor = math.sqrt(1/365)  # ≈ 0.0523
    return current_price * implied_volatility * time_factor
```

### 4. Volume Ratio

```python
def calculate_volume_ratio(current_volume, average_volume):
    """
    Volume Ratio = Current Volume / Average Volume
    """
    if average_volume == 0 or average_volume is None:
        return 0.0
    return current_volume / average_volume
```

## Integration Specifications

### 1. Database Connection

```python
# Connection parameters
DB_CONFIG = {
    'host': str,           # Required
    'port': int,           # Default: 5432
    'database': str,       # Required
    'user': str,           # Required
    'password': str,       # Required
    'connect_timeout': int,  # Default: 10
    'options': str,        # Optional: '-c statement_timeout=30000'
}

# Connection string
DATABASE_URL = "postgresql://user:password@host:port/database"
```

### 2. Robinhood Authentication

```python
# Login parameters
LOGIN_CONFIG = {
    'username': str,       # Required
    'password': str,       # Required
    'expiresIn': int,      # Default: 86400 (24 hours)
    'scope': str,          # Default: 'internal'
    'by_sms': bool,        # Default: True
    'store_session': bool  # Default: True
}

# Session management
SESSION_LIFETIME = 86400  # 24 hours
REFRESH_THRESHOLD = 3600  # Refresh if < 1 hour remaining
```

### 3. Redis Cache

```python
# Cache configuration
CACHE_CONFIG = {
    'host': 'localhost',
    'port': 6379,
    'db': 0,
    'password': None,
    'decode_responses': True,
    'max_connections': 50
}

# Cache keys
CACHE_KEYS = {
    'earnings_list': 'earnings:list:{date_filter}:{time_filter}',
    'earnings_detail': 'earnings:detail:{symbol}',
    'sectors': 'earnings:sectors',
    'analytics': 'earnings:analytics:{date}'
}

# TTL values (seconds)
CACHE_TTL = {
    'earnings_list': 300,    # 5 minutes
    'earnings_detail': 3600,  # 1 hour
    'sectors': 86400,         # 24 hours
    'analytics': 1800         # 30 minutes
}
```

## Performance Specifications

### 1. Response Time Requirements

| Operation | Target | Maximum |
|-----------|--------|---------|
| Page Load | < 500ms | 2s |
| Filter Apply | < 200ms | 1s |
| Data Export | < 1s | 5s |
| Sync 100 Symbols | < 120s | 300s |
| Database Query | < 100ms | 500ms |

### 2. Throughput Requirements

| Metric | Requirement |
|--------|-------------|
| Concurrent Users | 50 |
| Requests/Second | 100 |
| Database Connections | 20 |
| Sync Operations/Hour | 10 |

### 3. Resource Limits

```python
# Memory limits
MAX_DATAFRAME_SIZE = 100_000  # rows
MAX_EXPORT_SIZE = 50_000      # rows
MAX_CACHE_SIZE = 100_000_000  # bytes (100MB)

# Query limits
MAX_QUERY_RESULTS = 10_000
DEFAULT_QUERY_LIMIT = 200
MAX_SYMBOLS_PER_SYNC = 100

# Timeout values
QUERY_TIMEOUT = 30  # seconds
API_TIMEOUT = 10    # seconds
SYNC_TIMEOUT = 300  # seconds
```

## Error Handling Specifications

### 1. Error Categories

```python
class EarningsError(Exception):
    """Base exception for earnings module"""
    pass

class DatabaseError(EarningsError):
    """Database operation failed"""
    pass

class APIError(EarningsError):
    """External API error"""
    pass

class ValidationError(EarningsError):
    """Data validation failed"""
    pass

class AuthenticationError(EarningsError):
    """Authentication failed"""
    pass
```

### 2. Error Responses

```python
# Standard error response
{
    'success': False,
    'error': str,          # User-friendly message
    'error_code': str,     # Internal error code
    'details': Dict,       # Additional context
    'timestamp': datetime
}

# Error codes
ERROR_CODES = {
    'DB_CONNECTION_FAILED': 'E001',
    'DB_QUERY_FAILED': 'E002',
    'API_AUTH_FAILED': 'E003',
    'API_RATE_LIMITED': 'E004',
    'VALIDATION_FAILED': 'E005',
    'SYNC_FAILED': 'E006'
}
```

### 3. Error Recovery

```python
# Retry configuration
RETRY_CONFIG = {
    'max_attempts': 3,
    'backoff_factor': 2,  # Exponential backoff
    'max_delay': 30,       # seconds
    'retryable_errors': [
        'CONNECTION_ERROR',
        'TIMEOUT_ERROR',
        'RATE_LIMIT_ERROR'
    ]
}

# Recovery strategies
def recover_from_error(error_type):
    strategies = {
        'DB_CONNECTION': reconnect_database,
        'API_AUTH': refresh_authentication,
        'RATE_LIMIT': wait_and_retry,
        'VALIDATION': sanitize_and_retry
    }
    return strategies.get(error_type, log_and_fail)
```

## Security Specifications

### 1. Authentication

```python
# Credential storage
CREDENTIAL_ENCRYPTION = {
    'algorithm': 'AES-256-GCM',
    'key_derivation': 'PBKDF2',
    'iterations': 100_000,
    'salt_length': 32
}

# Session management
SESSION_CONFIG = {
    'timeout': 3600,           # 1 hour
    'max_lifetime': 86400,     # 24 hours
    'refresh_threshold': 900,   # 15 minutes
    'secure_cookie': True
}
```

### 2. Authorization

```python
# Permission levels
PERMISSIONS = {
    'read': ['view_earnings', 'export_data'],
    'write': ['sync_earnings', 'add_event'],
    'admin': ['create_tables', 'delete_data', 'modify_schema']
}

# Role definitions
ROLES = {
    'viewer': ['read'],
    'user': ['read', 'write'],
    'admin': ['read', 'write', 'admin']
}
```

### 3. Data Protection

```python
# Input validation
VALIDATION_RULES = {
    'symbol': r'^[A-Z]{1,10}$',
    'date': r'^\d{4}-\d{2}-\d{2}$',
    'time_filter': ['all', 'BMO', 'AMC'],
    'eps': r'^-?\d+\.?\d{0,4}$'
}

# SQL injection prevention
def sanitize_input(value, type):
    sanitizers = {
        'string': lambda x: re.sub(r'[^\w\s-]', '', x),
        'number': lambda x: float(x) if x.replace('.','').isdigit() else None,
        'date': lambda x: datetime.strptime(x, '%Y-%m-%d').date()
    }
    return sanitizers.get(type, lambda x: None)(value)
```

## Testing Specifications

### 1. Unit Tests

```python
# Test structure
class TestEarningsManager:
    def test_initialization(self):
        """Test manager initialization"""

    def test_get_earnings_events(self):
        """Test earnings event retrieval"""

    def test_calculate_status(self):
        """Test status calculation logic"""

    def test_sync_earnings(self):
        """Test Robinhood sync"""

# Test data fixtures
FIXTURES = {
    'earnings_event': {
        'symbol': 'AAPL',
        'earnings_date': datetime(2024, 1, 15, 16, 0),
        'earnings_time': 'AMC',
        'eps_estimate': 1.23,
        'eps_actual': 1.45
    }
}
```

### 2. Integration Tests

```python
# Database integration tests
def test_database_operations():
    # Test connection
    # Test CRUD operations
    # Test transactions
    # Test constraints

# API integration tests
def test_robinhood_integration():
    # Test authentication
    # Test data fetching
    # Test error handling
    # Test rate limiting
```

### 3. Performance Tests

```python
# Load testing configuration
LOAD_TEST_CONFIG = {
    'concurrent_users': 50,
    'test_duration': 300,  # seconds
    'ramp_up_time': 60,    # seconds
    'scenarios': [
        {'name': 'view_earnings', 'weight': 70},
        {'name': 'filter_data', 'weight': 20},
        {'name': 'sync_earnings', 'weight': 10}
    ]
}

# Performance benchmarks
BENCHMARKS = {
    'page_load': 500,       # ms
    'filter_apply': 200,    # ms
    'sync_100_symbols': 120000  # ms (2 minutes)
}
```

### 4. End-to-End Tests

```python
# E2E test scenarios
SCENARIOS = [
    {
        'name': 'first_time_user',
        'steps': [
            'navigate_to_calendar',
            'initialize_database',
            'sync_earnings',
            'view_data'
        ]
    },
    {
        'name': 'daily_workflow',
        'steps': [
            'navigate_to_calendar',
            'apply_this_week_filter',
            'export_to_csv',
            'sync_new_data'
        ]
    }
]
```

## Conclusion

This specification provides comprehensive technical details for implementing and maintaining the Earnings Calendar feature. All components are designed to work together seamlessly while maintaining clear boundaries and interfaces. The specifications ensure consistent behavior, predictable performance, and reliable operation across the entire feature set.