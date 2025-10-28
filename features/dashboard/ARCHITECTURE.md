# Dashboard Architecture Documentation

## System Overview

The Dashboard feature is built on a modern, scalable architecture that combines real-time data streaming, persistent storage, and intelligent analysis to provide comprehensive portfolio management capabilities for options traders using the wheel strategy.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                           │
│                    (Streamlit Web Application)                   │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Dashboard Controller                        │
│                        (dashboard.py)                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │   Portfolio  │  │    Trade     │  │     Forecasting      │ │
│  │   Metrics    │  │   History    │  │      Engine          │ │
│  └──────────────┘  └──────────────┘  └──────────────────────┘ │
└─────────────────────────┬───────────────────────────────────────┘
                          │
            ┌─────────────┼─────────────┬──────────────┐
            ▼             ▼             ▼              ▼
┌──────────────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐
│  Robinhood API   │ │   Trade  │ │    AI    │ │   Market     │
│   Integration    │ │  History │ │  Analyzer│ │   Data API   │
│(robinhood_fixed) │ │  Manager │ │          │ │  (yfinance)  │
└──────────────────┘ └──────────┘ └──────────┘ └──────────────┘
            │             │             │              │
            └─────────────┼─────────────┴──────────────┘
                          ▼
        ┌─────────────────────────────────────────┐
        │           Data Layer                     │
        │  ┌──────────────┐  ┌─────────────────┐ │
        │  │  PostgreSQL  │  │     Redis       │ │
        │  │   Database   │  │     Cache       │ │
        │  └──────────────┘  └─────────────────┘ │
        └───────────────────────────────────────┘
```

## Core Components

### 1. Dashboard Controller (`dashboard.py`)

The main orchestrator that manages the entire dashboard functionality.

**Key Responsibilities:**
- Page routing and navigation management
- Session state management
- Component initialization and lifecycle
- Data aggregation from multiple sources
- UI rendering and updates

**Code Location:** `c:/Code/WheelStrategy/dashboard.py` (Lines 92-1100+)

### 2. Trade History Manager (`TradeHistoryManager`)

Manages the complete lifecycle of options trades from opening to closing.

**Key Features:**
- CRUD operations for trade records
- P&L calculations with annualized returns
- Trade statistics aggregation
- Cumulative profit tracking

**Class Structure:**
```python
class TradeHistoryManager:
    def add_trade(symbol, strike_price, expiration_date, premium_collected, ...)
    def close_trade(trade_id, close_price, close_reason, ...)
    def get_open_trades()
    def get_closed_trades(limit, symbol, date_from, date_to)
    def get_trade_stats()
    def get_cumulative_pl()
    def get_trade_by_id(trade_id)
```

**Code Location:** `c:/Code/WheelStrategy/src/trade_history_manager.py`

### 3. AI Trade Analyzer (`AITradeAnalyzer`)

Provides intelligent analysis and recommendations for positions.

**Analysis Pipeline:**
1. Position metrics calculation
2. Risk assessment
3. Profit percentage evaluation
4. Recommendation generation
5. Portfolio-level aggregation

**Recommendation Thresholds:**
- 75%+ profit → BUY_BACK_IMMEDIATELY
- 50%+ profit (>7 DTE) → BUY_BACK_RECOMMENDED
- 25%+ profit (>14 DTE) → MONITOR_CLOSELY
- ITM (<7 DTE) → PREPARE_FOR_ASSIGNMENT
- ≤3 DTE → HOLD_TO_EXPIRY
- Default → HOLD_POSITION

**Code Location:** `c:/Code/WheelStrategy/src/ai_trade_analyzer.py`

### 4. Robinhood Integration (`robinhood_fixed.py`)

Handles real-time portfolio data retrieval from Robinhood.

**Functions:**
- `login_robinhood()`: Authentication with session caching
- `get_account_summary()`: Account balance and buying power
- `get_positions()`: Stock holdings
- `get_options()`: Options positions
- `identify_wheel_positions()`: CSP/CC identification

**Session Management:**
- Cached credentials in `.robinhood_token.pickle`
- Automatic session refresh
- MFA handling

## Data Flow

### 1. Real-Time Data Flow
```
Robinhood API → Dashboard → UI Components
     ↓              ↓            ↓
  Positions    Processing    Display
     ↓              ↓            ↓
   Cache        Analysis     Updates
```

### 2. Trade History Flow
```
User Input → TradeHistoryManager → PostgreSQL
                    ↓                   ↓
              Validation            Storage
                    ↓                   ↓
              Calculation          Retrieval
                    ↓                   ↓
               UI Update           Analytics
```

### 3. Forecast Generation Flow
```
Current Positions → Forecast Engine → Projections
        ↓                 ↓               ↓
    Theta Calc      Timeline Gen    Scenario Calc
        ↓                 ↓               ↓
    Daily Decay      Date Groups     Best/Worst
        ↓                 ↓               ↓
    UI Display       Visualization    Metrics
```

## Database Schema

### `trade_history` Table

Primary table for tracking all options trades.

```sql
CREATE TABLE trade_history (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    strategy_type VARCHAR(20) DEFAULT 'cash_secured_put',

    -- Opening trade details
    open_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    strike_price DECIMAL(10, 2) NOT NULL,
    expiration_date DATE NOT NULL,
    premium_collected DECIMAL(10, 2) NOT NULL,
    contracts INTEGER DEFAULT 1,
    dte_at_open INTEGER,

    -- Closing trade details
    close_date TIMESTAMP WITH TIME ZONE,
    close_price DECIMAL(10, 2),
    close_reason VARCHAR(20),

    -- Calculated P&L
    days_held INTEGER,
    profit_loss DECIMAL(10, 2),
    profit_loss_percent DECIMAL(10, 4),
    annualized_return DECIMAL(10, 4),

    -- Status and metadata
    status VARCHAR(20) DEFAULT 'open',
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**Indexes:**
- `idx_trade_history_symbol`: Symbol-based queries
- `idx_trade_history_status`: Open/closed filtering
- `idx_trade_history_close_date`: Historical analysis
- `idx_trade_history_open_date`: Chronological ordering

## Key Algorithms

### 1. P&L Calculation
```python
profit_loss = premium_collected - close_price
profit_loss_pct = (profit_loss / premium_collected) * 100
annualized_return = (profit_loss_pct / days_held) * 365
```

### 2. Theta Decay Approximation
```python
# Square root of time decay model
decay_factor = sqrt(days_remaining) / sqrt(initial_dte)
projected_value = current_value * decay_factor
daily_theta = premium - projected_value
```

### 3. Balance Forecasting
```python
# Three scenarios per expiration date
best_case = current_balance + premium_income
worst_case = current_balance - capital_deployed + premium_income
expected_case = current_balance + (premium_income * 0.7) - (capital_deployed * 0.3)
```

### 4. Assignment Probability
```python
if current_stock_price < strike:
    probability = min(90, 50 + ((strike - current_price) / strike * 100))
else:
    probability = max(10, 50 - ((current_price - strike) / strike * 100))
```

## Dependencies

### Core Dependencies
- **streamlit** (1.29.0): Web application framework
- **pandas** (2.1.3): Data manipulation and analysis
- **plotly** (5.18.0): Interactive visualizations
- **psycopg2-binary** (2.9.9): PostgreSQL database adapter
- **redis** (5.0.1): Caching layer
- **yfinance** (0.2.32): Market data provider

### Integration Dependencies
- **robin_stocks**: Robinhood API client (via robinhood_fixed.py)
- **python-dotenv** (1.0.0): Environment variable management

## Performance Optimizations

### 1. Caching Strategy
- Redis cache for market data (15-minute TTL)
- Session-based Robinhood authentication caching
- Streamlit's built-in caching for resource initialization

### 2. Database Optimizations
- Indexed columns for frequent queries
- Prepared statements for repetitive operations
- Connection pooling via TradingViewDBManager

### 3. UI Optimizations
- Lazy loading for position details
- Expandable sections to reduce initial render
- Selective rerun with `st.rerun()` for targeted updates

## Error Handling

### Graceful Degradation
1. **Database Connection Failure**: Show cached data if available
2. **Robinhood API Timeout**: Display last known values with timestamp
3. **Market Data Unavailable**: Use fallback calculations
4. **Invalid Trade Data**: Validation with user-friendly error messages

### Logging Strategy
```python
import logging
logger = logging.getLogger(__name__)

# Structured logging for trade operations
logger.info(f"Trade opened: {symbol} ${strike_price} Put, ID {trade_id}")
logger.error(f"Error closing trade: {e}")
```

## Security Considerations

### 1. Credential Management
- Environment variables for sensitive data
- Encrypted session storage for Robinhood tokens
- No hardcoded credentials in source code

### 2. Input Validation
- SQL injection prevention via parameterized queries
- Type checking with Pydantic models
- Sanitization of user inputs

### 3. Access Control
- Session-based authentication state
- Secure token refresh mechanism
- Automatic logout on inactivity

## Scalability Considerations

### Horizontal Scaling
- Stateless dashboard design
- Database connection pooling
- Redis cluster support ready

### Vertical Scaling
- Async operations for I/O-bound tasks
- Efficient data structures
- Optimized query patterns

## Monitoring and Observability

### Key Metrics
- Trade execution latency
- P&L calculation accuracy
- API response times
- Cache hit rates

### Health Checks
- Database connectivity
- Redis availability
- Robinhood API status
- Market data feed health

## Deployment Architecture

### Production Setup
```
Load Balancer
      ↓
Streamlit Instances (N)
      ↓
PostgreSQL (Primary/Replica)
      ↓
Redis Cluster
```

### Development Setup
```
Local Streamlit
      ↓
Local PostgreSQL
      ↓
Local Redis
```

## Future Architecture Improvements

1. **Event-Driven Architecture**: Implement message queue for trade events
2. **Microservices**: Separate trade history, analysis, and forecasting services
3. **WebSocket Integration**: Real-time position updates
4. **GraphQL API**: Flexible data fetching for mobile clients
5. **Time-Series Database**: Specialized storage for historical metrics