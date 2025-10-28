# TradingView Watchlists - Detailed Requirements Specification

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Functional Requirements](#functional-requirements)
3. [Non-Functional Requirements](#non-functional-requirements)
4. [Data Requirements](#data-requirements)
5. [Integration Requirements](#integration-requirements)
6. [User Interface Requirements](#user-interface-requirements)
7. [Performance Requirements](#performance-requirements)
8. [Security Requirements](#security-requirements)
9. [Business Rules](#business-rules)
10. [Validation Rules](#validation-rules)
11. [Error Handling Requirements](#error-handling-requirements)
12. [Reporting Requirements](#reporting-requirements)

## Executive Summary

### Purpose
The TradingView Watchlists feature provides a comprehensive option trading management system that integrates real-time position monitoring, trade history tracking, and premium analysis capabilities. It serves as the central hub for wheel strategy execution, combining data from Robinhood, TradingView, and market data providers.

### Scope
This specification covers all aspects of the TradingView Watchlists feature including position monitoring, trade logging, watchlist management, premium analysis, and performance tracking. It defines the requirements for data processing, calculations, user interactions, and system integrations.

### Key Stakeholders
- **End Users**: Options traders using the wheel strategy
- **System Administrators**: Responsible for system maintenance
- **Data Providers**: Robinhood, Yahoo Finance, TradingView
- **Database Administrators**: PostgreSQL database management

## Functional Requirements

### FR-1: Position Monitoring

#### FR-1.1: Live Position Display
- **Description**: System shall display all open option positions from Robinhood
- **Priority**: Critical
- **Acceptance Criteria**:
  - Positions update within 60 seconds of changes
  - All position types displayed (CSP, CC, Long/Short)
  - Accurate P/L calculations
  - Real-time market prices

#### FR-1.2: Position Enrichment
- **Description**: Enrich basic position data with detailed information
- **Priority**: High
- **Acceptance Criteria**:
  - Symbol and company name displayed
  - Strike price formatted as currency
  - Expiration date in readable format
  - Days to expiration calculated
  - Strategy type determined automatically

#### FR-1.3: P/L Calculation
- **Description**: Calculate profit/loss for each position
- **Priority**: Critical
- **Acceptance Criteria**:
  - Accurate calculation based on position type
  - Both dollar amount and percentage shown
  - Real-time updates with market prices
  - Handles both realized and unrealized P/L

#### FR-1.4: Position Aggregation
- **Description**: Provide summary metrics across all positions
- **Priority**: High
- **Acceptance Criteria**:
  - Total number of positions
  - Total premium collected
  - Aggregate P/L
  - Strategy breakdown (CSP count, CC count)

### FR-2: Trade History Management

#### FR-2.1: Trade Logging
- **Description**: Log closed trades with complete details
- **Priority**: Critical
- **Acceptance Criteria**:
  - Capture all required trade details
  - Calculate profit/loss automatically
  - Store in persistent database
  - Support multiple close reasons

#### FR-2.2: Trade Form Interface
- **Description**: Provide forms for logging closed trades
- **Priority**: High
- **Acceptance Criteria**:
  - Expandable form for each position
  - Pre-filled with position data
  - Input validation
  - Confirmation feedback

#### FR-2.3: Historical Analysis
- **Description**: Analyze historical trade performance
- **Priority**: High
- **Acceptance Criteria**:
  - Calculate win rate
  - Average days held
  - Total P/L
  - Annualized returns

#### FR-2.4: Trade Filtering
- **Description**: Filter trade history by criteria
- **Priority**: Medium
- **Acceptance Criteria**:
  - Filter by symbol
  - Filter by date range
  - Limit number of results
  - Sort by any column

#### FR-2.5: Data Export
- **Description**: Export trade history to CSV
- **Priority**: Medium
- **Acceptance Criteria**:
  - Include all trade fields
  - Proper date formatting
  - UTF-8 encoding
  - Filename with timestamp

### FR-3: Watchlist Management

#### FR-3.1: Watchlist Import
- **Description**: Import watchlists from various sources
- **Priority**: High
- **Acceptance Criteria**:
  - Accept comma-separated input
  - Accept line-separated input
  - Parse TradingView exports
  - Validate symbols

#### FR-3.2: Watchlist Storage
- **Description**: Persist watchlists in database
- **Priority**: Critical
- **Acceptance Criteria**:
  - Store watchlist metadata
  - Store symbol associations
  - Support multiple watchlists
  - Handle duplicates

#### FR-3.3: Watchlist Synchronization
- **Description**: Sync watchlist data with market sources
- **Priority**: High
- **Acceptance Criteria**:
  - Background synchronization
  - Non-blocking UI
  - Progress indication
  - Error recovery

#### FR-3.4: Watchlist CRUD Operations
- **Description**: Create, Read, Update, Delete watchlists
- **Priority**: High
- **Acceptance Criteria**:
  - Create new watchlists
  - Load existing watchlists
  - Update watchlist contents
  - Delete unwanted watchlists

### FR-4: Premium Analysis

#### FR-4.1: Option Chain Analysis
- **Description**: Analyze option chains for opportunities
- **Priority**: Critical
- **Acceptance Criteria**:
  - Fetch option chains for symbols
  - Calculate premiums
  - Filter by delta range
  - Sort by return

#### FR-4.2: 30-Day Options Focus
- **Description**: Specialize in 30-day option analysis
- **Priority**: High
- **Acceptance Criteria**:
  - Default to 28-32 DTE range
  - Target 0.25-0.40 delta
  - Calculate monthly returns
  - Show best opportunities

#### FR-4.3: Greeks Display
- **Description**: Display option Greeks
- **Priority**: Medium
- **Acceptance Criteria**:
  - Show delta values
  - Show theta values
  - Show implied volatility
  - Format appropriately

#### FR-4.4: Liquidity Metrics
- **Description**: Display liquidity indicators
- **Priority**: Medium
- **Acceptance Criteria**:
  - Show bid/ask spread
  - Display volume
  - Display open interest
  - Flag low liquidity

### FR-5: Theta Decay Visualization

#### FR-5.1: Decay Projections
- **Description**: Project theta decay over time
- **Priority**: Medium
- **Acceptance Criteria**:
  - Calculate daily decay
  - Show decay curve
  - Project to expiration
  - Update with market changes

#### FR-5.2: Profit Milestones
- **Description**: Show profit at key timepoints
- **Priority**: Low
- **Acceptance Criteria**:
  - 7-day projection
  - 3-day projection
  - Expiration value
  - Current profit level

#### FR-5.3: Decay Recommendations
- **Description**: Provide theta-based recommendations
- **Priority**: Low
- **Acceptance Criteria**:
  - Alert when >50% captured
  - Highlight maximum decay period
  - Suggest hold/close decisions
  - Show daily earnings rate

### FR-6: Database Operations

#### FR-6.1: Database Scan
- **Description**: Scan entire database for opportunities
- **Priority**: Medium
- **Acceptance Criteria**:
  - Query all stocks with options
  - Apply filters efficiently
  - Display results quickly
  - Handle large datasets

#### FR-6.2: Stock Addition
- **Description**: Add new stocks to database
- **Priority**: Medium
- **Acceptance Criteria**:
  - Bulk import capability
  - Fetch data from Yahoo Finance
  - Validate symbols
  - Update existing records

#### FR-6.3: Analytics Display
- **Description**: Show database analytics
- **Priority**: Low
- **Acceptance Criteria**:
  - Sector distribution
  - Price distribution
  - Total stock count
  - Options availability

## Non-Functional Requirements

### NFR-1: Performance Requirements

#### NFR-1.1: Response Time
- **Description**: System response time requirements
- **Metrics**:
  - Page load: < 3 seconds
  - Position refresh: < 2 seconds
  - Database query: < 1 second
  - Premium calculation: < 5 seconds per symbol

#### NFR-1.2: Throughput
- **Description**: System throughput capabilities
- **Metrics**:
  - Concurrent users: 10
  - Symbols per watchlist: 100
  - Trades per query: 1000
  - API calls per minute: 100

#### NFR-1.3: Resource Usage
- **Description**: Resource consumption limits
- **Metrics**:
  - Memory usage: < 2GB
  - CPU usage: < 50% average
  - Database connections: < 20
  - Network bandwidth: < 10 Mbps

### NFR-2: Reliability Requirements

#### NFR-2.1: Availability
- **Description**: System availability requirements
- **Metrics**:
  - Uptime: 99% during market hours
  - Planned maintenance: < 2 hours/month
  - Recovery time: < 5 minutes

#### NFR-2.2: Data Integrity
- **Description**: Data accuracy and consistency
- **Metrics**:
  - P/L accuracy: 100%
  - Transaction atomicity: ACID compliant
  - Data validation: 100% inputs validated

#### NFR-2.3: Fault Tolerance
- **Description**: System resilience
- **Metrics**:
  - API failures: Graceful degradation
  - Database failures: Connection retry
  - Network issues: Offline capability

### NFR-3: Usability Requirements

#### NFR-3.1: User Interface
- **Description**: UI/UX requirements
- **Metrics**:
  - Load time perception: Progressive loading
  - Mobile responsiveness: Full functionality
  - Accessibility: WCAG 2.1 AA compliant

#### NFR-3.2: Learning Curve
- **Description**: Ease of use requirements
- **Metrics**:
  - New user onboarding: < 10 minutes
  - Feature discovery: Intuitive navigation
  - Help documentation: Comprehensive

### NFR-4: Scalability Requirements

#### NFR-4.1: Vertical Scaling
- **Description**: Single instance scaling
- **Metrics**:
  - Database rows: 1M+ trades
  - Watchlist size: 500+ symbols
  - Historical data: 5+ years

#### NFR-4.2: Horizontal Scaling
- **Description**: Multi-instance scaling
- **Metrics**:
  - Load balancing: Supported
  - Session management: Distributed
  - Cache sharing: Redis cluster

## Data Requirements

### DR-1: Position Data

#### DR-1.1: Required Fields
```python
position_data = {
    'symbol': str,              # Stock ticker (required)
    'option_id': str,           # Unique identifier (required)
    'strategy': str,            # CSP/CC/Long/Short (required)
    'strike_price': Decimal,    # Strike price (required)
    'expiration_date': date,    # Expiration (required)
    'contracts': int,           # Number of contracts (required)
    'position_type': str,       # long/short (required)
    'option_type': str,         # call/put (required)
    'average_price': Decimal,   # Entry price (required)
    'current_price': Decimal,   # Market price (optional)
    'dte': int,                 # Days to expiration (calculated)
    'profit_loss': Decimal,     # P/L amount (calculated)
    'profit_loss_pct': float,   # P/L percentage (calculated)
}
```

#### DR-1.2: Data Sources
- **Primary**: Robinhood API
- **Secondary**: Manual entry
- **Enrichment**: Market data APIs

#### DR-1.3: Update Frequency
- **Real-time**: During market hours
- **Batch**: After hours daily
- **On-demand**: User refresh

### DR-2: Trade History Data

#### DR-2.1: Required Fields
```python
trade_history = {
    'id': int,                      # Unique ID (auto)
    'symbol': str,                   # Stock ticker (required)
    'strike_price': Decimal,         # Strike (required)
    'expiration_date': date,         # Expiration (required)
    'premium_collected': Decimal,    # Premium (required)
    'contracts': int,                # Contracts (default 1)
    'open_date': date,              # Open date (required)
    'close_date': date,             # Close date (optional)
    'close_price': Decimal,         # Close price (optional)
    'close_reason': str,            # Reason (optional)
    'dte_at_open': int,             # Initial DTE (calculated)
    'days_held': int,               # Duration (calculated)
    'profit_loss': Decimal,         # P/L (calculated)
    'profit_loss_percent': float,   # P/L % (calculated)
    'annualized_return': float,     # Annual % (calculated)
    'strategy_type': str,           # Strategy (required)
    'status': str,                  # open/closed (required)
    'notes': str,                   # Notes (optional)
}
```

#### DR-2.2: Calculated Fields
- **profit_loss**: premium_collected - close_price
- **profit_loss_percent**: (profit_loss / premium_collected) * 100
- **days_held**: close_date - open_date
- **annualized_return**: (profit_loss_percent / days_held) * 365

### DR-3: Watchlist Data

#### DR-3.1: Watchlist Structure
```python
watchlist = {
    'id': int,                  # Unique ID
    'name': str,                # Watchlist name
    'description': str,         # Description
    'created_at': datetime,     # Creation time
    'updated_at': datetime,     # Last update
    'last_refresh': datetime,   # Last sync
    'is_active': bool,         # Active flag
    'symbol_count': int,       # Symbol count
}

watchlist_symbol = {
    'id': int,                 # Unique ID
    'watchlist_id': int,       # FK to watchlist
    'symbol': str,             # Stock ticker
    'company_name': str,       # Company name
    'sector': str,             # Sector
    'industry': str,           # Industry
    'market_cap': int,         # Market cap
    'last_price': Decimal,     # Last price
    'volume': int,             # Volume
    'added_at': datetime,      # Added time
    'updated_at': datetime,    # Updated time
}
```

### DR-4: Premium Data

#### DR-4.1: Premium Structure
```python
premium_data = {
    'symbol': str,              # Stock ticker
    'strike_price': Decimal,    # Strike
    'dte': int,                # Days to expiry
    'premium': Decimal,        # Premium amount
    'delta': float,            # Delta
    'theta': float,            # Theta
    'implied_volatility': float, # IV
    'bid': Decimal,            # Bid price
    'ask': Decimal,            # Ask price
    'volume': int,             # Volume
    'open_interest': int,      # Open interest
    'monthly_return': float,   # Monthly %
    'updated_at': datetime,    # Last update
}
```

## Integration Requirements

### IR-1: Robinhood Integration

#### IR-1.1: Authentication
- **Method**: Username/Password with MFA
- **Storage**: Environment variables
- **Session**: Persistent with refresh
- **Security**: Encrypted storage

#### IR-1.2: API Endpoints
```python
# Required Robinhood endpoints
endpoints = {
    'login': 'rh.login()',
    'positions': 'rh.get_open_option_positions()',
    'instrument': 'rh.get_option_instrument_data_by_id()',
    'market_data': 'rh.get_option_market_data_by_id()',
    'logout': 'rh.logout()'
}
```

#### IR-1.3: Rate Limiting
- **Requests per minute**: 60
- **Retry strategy**: Exponential backoff
- **Error handling**: Graceful degradation

### IR-2: Yahoo Finance Integration

#### IR-2.1: Data Points
```python
# Required Yahoo Finance data
yahoo_data = {
    'current_price': 'ticker.info["currentPrice"]',
    'options_chain': 'ticker.option_chain()',
    'company_info': 'ticker.info["longName"]',
    'market_cap': 'ticker.info["marketCap"]',
    'volume': 'ticker.info["volume"]'
}
```

#### IR-2.2: Update Frequency
- **Intraday**: 5-minute intervals
- **Daily**: After market close
- **On-demand**: User triggered

### IR-3: Database Integration

#### IR-3.1: Connection Management
```python
# Database connection configuration
db_config = {
    'host': 'localhost',
    'port': 5432,
    'database': 'magnus',
    'user': 'postgres',
    'password': 'encrypted',
    'pool_size': 20,
    'max_overflow': 0,
    'pool_pre_ping': True,
    'pool_recycle': 3600
}
```

#### IR-3.2: Query Optimization
- **Indexes**: On frequently queried columns
- **Batch operations**: For bulk updates
- **Connection pooling**: For concurrent access
- **Query timeout**: 30 seconds max

## User Interface Requirements

### UI-1: Layout Structure

#### UI-1.1: Page Organization
```
┌─────────────────────────────────────┐
│          Page Header                 │
├─────────────────────────────────────┤
│     Current Positions Section       │
├─────────────────────────────────────┤
│      Trade History Section          │
├─────────────────────────────────────┤
│         Tabbed Interface            │
│  ┌────┬────┬────┬────┬────┐       │
│  │Tab1│Tab2│Tab3│Tab4│Tab5│       │
│  └────┴────┴────┴────┴────┘       │
│         Tab Content Area            │
└─────────────────────────────────────┘
```

#### UI-1.2: Component Specifications

##### Position Display Table
- **Columns**: Symbol, Strategy, Strike, Expiration, DTE, Contracts, Premium, Current, P/L, P/L%
- **Sorting**: Clickable headers
- **Formatting**: Currency for prices, percentage for returns
- **Colors**: Green for profit, red for loss

##### Trade Log Forms
- **Layout**: Expandable accordions
- **Fields**: Close price, reason dropdown, date picker
- **Validation**: Real-time input validation
- **Feedback**: Success messages with balloons

##### Watchlist Tabs
- **Tab 1**: Auto-Sync - Refresh controls and status
- **Tab 2**: Import - Text area and file upload
- **Tab 3**: Analysis - Results table and metrics
- **Tab 4**: Saved - List management
- **Tab 5**: Quick Scan - Filters and results

### UI-2: Interactive Elements

#### UI-2.1: Buttons
```python
buttons = {
    'refresh': {
        'label': 'Refresh Watchlists',
        'icon': '🔄',
        'type': 'primary',
        'action': 'reload_data()'
    },
    'sync': {
        'label': 'Sync Prices & Premiums',
        'icon': '⚡',
        'type': 'primary',
        'action': 'background_sync()'
    },
    'log_trade': {
        'label': 'Log This Trade',
        'icon': '📝',
        'type': 'primary',
        'action': 'submit_trade_log()'
    },
    'export': {
        'label': 'Download CSV',
        'icon': '📥',
        'type': 'secondary',
        'action': 'export_to_csv()'
    }
}
```

#### UI-2.2: Forms
```python
forms = {
    'trade_log': {
        'fields': [
            'close_price (number)',
            'close_reason (select)',
            'open_date (date)'
        ],
        'validation': 'real-time',
        'submission': 'ajax'
    },
    'import_watchlist': {
        'fields': [
            'symbols (textarea)',
            'name (text)'
        ],
        'validation': 'on_submit',
        'submission': 'page_reload'
    }
}
```

#### UI-2.3: Filters
```python
filters = {
    'stock_price': {
        'type': 'range',
        'min': 0,
        'max': 10000,
        'step': 10
    },
    'premium': {
        'type': 'minimum',
        'min': 0,
        'step': 1
    },
    'dte': {
        'type': 'select',
        'options': [10, 17, 24, 31, 38, 52]
    },
    'symbol': {
        'type': 'text',
        'placeholder': 'AAPL'
    }
}
```

### UI-3: Visual Feedback

#### UI-3.1: Status Indicators
- **Loading**: Spinner with message
- **Success**: Green checkmark with message
- **Warning**: Yellow triangle with message
- **Error**: Red X with message and retry option

#### UI-3.2: Progress Indicators
- **Sync progress**: Progress bar with percentage
- **Background tasks**: Status text updates
- **Data loading**: Skeleton screens

#### UI-3.3: Data Visualization
- **Metrics cards**: Large numbers with trends
- **Tables**: Sortable, filterable, paginated
- **Charts**: Theta decay curves (future)

## Performance Requirements

### PR-1: Query Performance

#### PR-1.1: Database Queries
```sql
-- Optimized query example
EXPLAIN ANALYZE
SELECT DISTINCT ON (symbol)
    symbol, strike_price, premium, delta
FROM stock_premiums
WHERE
    symbol = ANY(ARRAY['AAPL','MSFT'])
    AND dte BETWEEN 28 AND 32
    AND ABS(delta) BETWEEN 0.25 AND 0.40
ORDER BY symbol, monthly_return DESC;

-- Expected performance
-- Planning time: < 1ms
-- Execution time: < 100ms
```

#### PR-1.2: Caching Strategy
```python
cache_config = {
    'position_data': {
        'ttl': 60,  # 1 minute
        'key': 'positions:{user_id}'
    },
    'premium_data': {
        'ttl': 300,  # 5 minutes
        'key': 'premiums:{symbol}:{dte}'
    },
    'watchlist_data': {
        'ttl': 600,  # 10 minutes
        'key': 'watchlist:{name}'
    }
}
```

### PR-2: Concurrent Operations

#### PR-2.1: Thread Pool Configuration
```python
thread_config = {
    'sync_workers': 10,      # Data sync threads
    'calc_workers': 5,       # Calculation threads
    'db_connections': 20,    # Max DB connections
    'api_connections': 10    # Max API connections
}
```

#### PR-2.2: Rate Limiting
```python
rate_limits = {
    'robinhood': {
        'requests_per_minute': 60,
        'burst_size': 10
    },
    'yahoo_finance': {
        'requests_per_minute': 100,
        'burst_size': 20
    },
    'database': {
        'queries_per_second': 100,
        'max_query_time': 30
    }
}
```

## Security Requirements

### SR-1: Authentication & Authorization

#### SR-1.1: Credential Management
```python
security_config = {
    'storage': 'environment_variables',
    'encryption': 'AES-256',
    'rotation': 'quarterly',
    'access_control': 'role_based'
}
```

#### SR-1.2: Session Management
```python
session_config = {
    'timeout': 3600,  # 1 hour
    'refresh': True,
    'secure_cookies': True,
    'csrf_protection': True
}
```

### SR-2: Data Protection

#### SR-2.1: Sensitive Data
```python
sensitive_fields = [
    'password',
    'api_key',
    'session_token',
    'account_number'
]

# Handling rules
for field in sensitive_fields:
    # Never log
    # Never display in UI
    # Encrypt in storage
    # Mask in errors
```

#### SR-2.2: Input Validation
```python
validation_rules = {
    'symbol': r'^[A-Z]{1,5}$',
    'price': r'^\d+\.?\d{0,2}$',
    'date': r'^\d{4}-\d{2}-\d{2}$',
    'reason': ['early_close', 'expiration', 'assignment']
}
```

### SR-3: Audit & Compliance

#### SR-3.1: Audit Logging
```python
audit_events = [
    'user_login',
    'trade_logged',
    'position_closed',
    'data_exported',
    'watchlist_modified'
]

audit_log = {
    'timestamp': datetime,
    'user_id': str,
    'action': str,
    'details': dict,
    'ip_address': str
}
```

## Business Rules

### BR-1: Position Management Rules

#### BR-1.1: Strategy Classification
```python
def classify_strategy(position):
    """
    Determine option strategy type
    """
    if position['type'] == 'short':
        if position['option_type'] == 'put':
            return 'CSP'  # Cash-Secured Put
        elif position['option_type'] == 'call':
            return 'CC'   # Covered Call
    elif position['type'] == 'long':
        if position['option_type'] == 'call':
            return 'Long Call'
        elif position['option_type'] == 'put':
            return 'Long Put'
    return 'Other'
```

#### BR-1.2: P/L Calculation Rules
```python
def calculate_pl(position):
    """
    Calculate profit/loss based on position type
    """
    premium = position['average_price'] * position['quantity'] * 100
    current = position['current_price'] * position['quantity'] * 100

    if position['type'] == 'short':
        # Profit when option value decreases
        pl = premium - current
    else:
        # Profit when option value increases
        pl = current - premium

    pl_percent = (pl / premium * 100) if premium > 0 else 0
    return pl, pl_percent
```

### BR-2: Premium Analysis Rules

#### BR-2.1: Delta Targeting
```python
delta_rules = {
    'conservative': (0.20, 0.30),  # 20-30% ITM probability
    'moderate': (0.25, 0.35),       # 25-35% ITM probability
    'aggressive': (0.30, 0.40)      # 30-40% ITM probability
}

def is_valid_delta(delta, risk_profile='moderate'):
    """
    Check if delta is within target range
    """
    min_delta, max_delta = delta_rules[risk_profile]
    return min_delta <= abs(delta) <= max_delta
```

#### BR-2.2: DTE Selection
```python
dte_rules = {
    'weekly': (7, 14),
    'monthly': (28, 35),
    'quarterly': (80, 100)
}

def optimal_dte(strategy='monthly'):
    """
    Get optimal days to expiration range
    """
    return dte_rules[strategy]
```

### BR-3: Trade Management Rules

#### BR-3.1: Close Conditions
```python
close_conditions = {
    'profit_target': 0.50,      # Close at 50% profit
    'loss_limit': -1.00,        # Close at 100% loss
    'dte_threshold': 7,         # Consider closing < 7 DTE
    'delta_breach': 0.50        # Close if delta > 0.50
}

def should_close(trade):
    """
    Determine if trade should be closed
    """
    profit_pct = trade['profit_loss_percent']

    if profit_pct >= close_conditions['profit_target'] * 100:
        return True, 'profit_target'

    if profit_pct <= close_conditions['loss_limit'] * 100:
        return True, 'loss_limit'

    if trade['dte'] <= close_conditions['dte_threshold']:
        if abs(trade['delta']) >= close_conditions['delta_breach']:
            return True, 'high_risk'

    return False, None
```

## Validation Rules

### VR-1: Input Validation

#### VR-1.1: Symbol Validation
```python
def validate_symbol(symbol):
    """
    Validate stock symbol format
    """
    # Clean input
    symbol = symbol.strip().upper()

    # Check format
    if not re.match(r'^[A-Z]{1,5}$', symbol):
        raise ValueError(f"Invalid symbol format: {symbol}")

    # Check blacklist
    blacklist = ['TEST', 'DUMMY', 'XXX']
    if symbol in blacklist:
        raise ValueError(f"Blacklisted symbol: {symbol}")

    # Check existence (optional)
    if not symbol_exists(symbol):
        raise ValueError(f"Symbol not found: {symbol}")

    return symbol
```

#### VR-1.2: Price Validation
```python
def validate_price(price, field_name="price"):
    """
    Validate price input
    """
    # Type check
    if not isinstance(price, (int, float, Decimal)):
        raise TypeError(f"{field_name} must be numeric")

    # Range check
    if price < 0:
        raise ValueError(f"{field_name} cannot be negative")

    if price > 1000000:
        raise ValueError(f"{field_name} exceeds maximum")

    # Precision check
    if isinstance(price, float):
        price = Decimal(str(price))

    return price.quantize(Decimal('0.01'))
```

#### VR-1.3: Date Validation
```python
def validate_date(date_str, field_name="date"):
    """
    Validate date input
    """
    # Parse date
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        raise ValueError(f"Invalid {field_name} format. Use YYYY-MM-DD")

    # Business logic checks
    if date_obj.date() > datetime.now().date():
        raise ValueError(f"{field_name} cannot be in future")

    if date_obj.year < 2020:
        raise ValueError(f"{field_name} too far in past")

    return date_obj.date()
```

### VR-2: Business Logic Validation

#### VR-2.1: Trade Validation
```python
def validate_trade(trade_data):
    """
    Validate complete trade record
    """
    errors = []

    # Required fields
    required = ['symbol', 'strike_price', 'premium_collected']
    for field in required:
        if not trade_data.get(field):
            errors.append(f"Missing required field: {field}")

    # Logical checks
    if trade_data.get('close_price', 0) < 0:
        errors.append("Close price cannot be negative")

    if trade_data.get('contracts', 0) <= 0:
        errors.append("Contracts must be positive")

    # Date logic
    open_date = trade_data.get('open_date')
    close_date = trade_data.get('close_date')
    if open_date and close_date:
        if close_date < open_date:
            errors.append("Close date cannot be before open date")

    if errors:
        raise ValidationError(errors)

    return True
```

## Error Handling Requirements

### EH-1: Error Types

#### EH-1.1: Error Classification
```python
error_types = {
    'API_ERROR': {
        'severity': 'HIGH',
        'retry': True,
        'user_message': 'Unable to fetch data. Retrying...'
    },
    'VALIDATION_ERROR': {
        'severity': 'LOW',
        'retry': False,
        'user_message': 'Please check your input and try again.'
    },
    'DATABASE_ERROR': {
        'severity': 'CRITICAL',
        'retry': True,
        'user_message': 'System error. Please try again later.'
    },
    'CALCULATION_ERROR': {
        'severity': 'MEDIUM',
        'retry': False,
        'user_message': 'Unable to calculate. Check data.'
    }
}
```

#### EH-1.2: Error Recovery
```python
def handle_error(error_type, error, context=None):
    """
    Centralized error handling
    """
    config = error_types.get(error_type, {})

    # Log error
    logger.error(f"{error_type}: {error}", extra=context)

    # User notification
    if config.get('severity') == 'CRITICAL':
        st.error(config.get('user_message'))
        # Send alert to admin
        notify_admin(error)

    elif config.get('severity') == 'HIGH':
        st.warning(config.get('user_message'))

    else:
        st.info(config.get('user_message'))

    # Retry logic
    if config.get('retry'):
        return retry_operation(context)

    return None
```

### EH-2: Error Logging

#### EH-2.1: Log Format
```python
log_format = {
    'timestamp': 'ISO 8601',
    'level': 'ERROR|WARNING|INFO|DEBUG',
    'component': 'module.function',
    'message': 'error description',
    'context': {
        'user_id': 'identifier',
        'action': 'what user was doing',
        'data': 'relevant data'
    },
    'traceback': 'full stack trace'
}
```

#### EH-2.2: Log Retention
```python
log_retention = {
    'ERROR': '90 days',
    'WARNING': '30 days',
    'INFO': '7 days',
    'DEBUG': '1 day'
}
```

## Reporting Requirements

### RR-1: Trade Reports

#### RR-1.1: Performance Report
```python
def generate_performance_report(start_date, end_date):
    """
    Generate comprehensive performance report
    """
    report = {
        'summary': {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'win_rate': 0.0,
            'total_profit': 0.0,
            'average_profit': 0.0,
            'best_trade': {},
            'worst_trade': {}
        },
        'by_strategy': {
            'CSP': {},
            'CC': {}
        },
        'by_symbol': {},
        'by_month': {},
        'metrics': {
            'sharpe_ratio': 0.0,
            'max_drawdown': 0.0,
            'profit_factor': 0.0
        }
    }
    return report
```

#### RR-1.2: Tax Report
```python
def generate_tax_report(year):
    """
    Generate tax reporting data
    """
    trades = get_closed_trades(year)

    report = {
        'short_term_gains': [],
        'long_term_gains': [],
        'total_proceeds': 0,
        'total_cost_basis': 0,
        'net_gain_loss': 0,
        'form_8949_data': []
    }

    for trade in trades:
        # Classify by holding period
        if trade['days_held'] <= 365:
            report['short_term_gains'].append(trade)
        else:
            report['long_term_gains'].append(trade)

    return report
```

### RR-2: Analytics Reports

#### RR-2.1: Risk Report
```python
def generate_risk_report():
    """
    Generate current risk assessment
    """
    report = {
        'portfolio_greeks': {
            'total_delta': 0,
            'total_theta': 0,
            'total_gamma': 0
        },
        'concentration_risk': {
            'by_symbol': {},
            'by_sector': {},
            'max_position_pct': 0
        },
        'assignment_risk': [],
        'recommendations': []
    }
    return report
```

## Testing Requirements

### TR-1: Test Coverage

#### TR-1.1: Unit Test Coverage
- **Target**: 80% code coverage
- **Critical paths**: 100% coverage
- **Edge cases**: Comprehensive testing

#### TR-1.2: Integration Tests
- **API integrations**: Mock and real tests
- **Database operations**: Transaction testing
- **End-to-end workflows**: User journey tests

### TR-2: Test Data

#### TR-2.1: Test Data Sets
```python
test_data = {
    'positions': [
        # Various position types
        {'symbol': 'AAPL', 'type': 'short', 'option_type': 'put'},
        {'symbol': 'MSFT', 'type': 'short', 'option_type': 'call'},
        {'symbol': 'GOOGL', 'type': 'long', 'option_type': 'call'}
    ],
    'trades': [
        # Various outcomes
        {'profit_loss': 100, 'close_reason': 'early_close'},
        {'profit_loss': -50, 'close_reason': 'assignment'},
        {'profit_loss': 200, 'close_reason': 'expiration'}
    ],
    'edge_cases': [
        # Boundary conditions
        {'price': 0.01},  # Minimum price
        {'dte': 0},       # Expiration day
        {'delta': 0.99}   # Deep ITM
    ]
}
```

## Acceptance Criteria

### AC-1: Feature Completion

#### AC-1.1: Core Features
- [ ] Display all open positions from Robinhood
- [ ] Calculate accurate P/L for each position
- [ ] Log closed trades with full details
- [ ] Import and manage watchlists
- [ ] Analyze 30-day option premiums
- [ ] Export trade history to CSV

#### AC-1.2: Performance Criteria
- [ ] Page loads in < 3 seconds
- [ ] Position refresh in < 2 seconds
- [ ] Handles 100+ symbols per watchlist
- [ ] Supports 1000+ trade history records

#### AC-1.3: Quality Criteria
- [ ] No critical bugs in production
- [ ] 99% uptime during market hours
- [ ] All calculations accurate to 2 decimal places
- [ ] Comprehensive error handling

## Summary

This specification defines the complete requirements for the TradingView Watchlists feature, covering functional capabilities, non-functional qualities, data structures, integrations, and business rules. Implementation should follow these requirements to ensure a robust, performant, and user-friendly option trading management system.