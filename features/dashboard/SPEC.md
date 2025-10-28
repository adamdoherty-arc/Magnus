# Dashboard Feature Specifications

## 1. Functional Requirements

### 1.1 Portfolio Status Display

#### Requirements
- **FR-1.1.1**: Display current account balance from Robinhood API
- **FR-1.1.2**: Show available buying power in real-time
- **FR-1.1.3**: Calculate and display total premium collected across all positions
- **FR-1.1.4**: Compute capital at risk (sum of strike prices × 100 × contracts)
- **FR-1.1.5**: Count and display active cash-secured puts

#### Acceptance Criteria
- Balance updates within 2 seconds of page refresh
- Calculations accurate to 2 decimal places
- Graceful fallback to $0 when Robinhood not connected

### 1.2 Trade History Management

#### Requirements
- **FR-1.2.1**: Manual trade entry with validation
- **FR-1.2.2**: Trade closing with P&L calculation
- **FR-1.2.3**: Historical trade display with sorting
- **FR-1.2.4**: Cumulative P&L visualization
- **FR-1.2.5**: Trade statistics aggregation

#### Acceptance Criteria
- Form validation prevents invalid data entry
- P&L calculations match formula: `premium_collected - close_price`
- Chart updates immediately after trade changes
- Statistics refresh within 1 second of database update

### 1.3 Balance Forecasting

#### Requirements
- **FR-1.3.1**: Group positions by expiration date
- **FR-1.3.2**: Calculate three scenarios per date (best/expected/worst)
- **FR-1.3.3**: Project monthly returns
- **FR-1.3.4**: Display maximum capital at risk

#### Acceptance Criteria
- Expected case uses 70% probability of expiring OTM
- Forecasts update when positions change
- Monthly return calculation: `(final_balance / current_balance - 1) × 100 / months`

### 1.4 Position-Specific Analysis

#### Requirements
- **FR-1.4.1**: Individual P&L tracking per position
- **FR-1.4.2**: Real-time theta calculation
- **FR-1.4.3**: Assignment probability estimation
- **FR-1.4.4**: Breakeven price calculation

#### Acceptance Criteria
- Theta updates daily
- Assignment probability based on moneyness
- Breakeven = `strike_price - (premium / 100)`

### 1.5 Theta Decay Forecasting

#### Requirements
- **FR-1.5.1**: Daily profit projection tables
- **FR-1.5.2**: Accelerating theta visualization
- **FR-1.5.3**: Milestone profit calculations (3-day, 7-day)
- **FR-1.5.4**: Average daily theta computation

#### Acceptance Criteria
- Uses square root of time model for decay
- Projections extend to expiration or 60 days maximum
- Recommendations based on days to expiry

### 1.6 AI Trade Analysis

#### Requirements
- **FR-1.6.1**: Position-specific recommendations
- **FR-1.6.2**: Portfolio-level action suggestions
- **FR-1.6.3**: Profit-taking alerts at thresholds
- **FR-1.6.4**: Risk level assessment

#### Acceptance Criteria
- Recommendations update with market changes
- Alert triggers at 20%, 50%, 75% profit levels
- Risk levels: HIGH, MEDIUM, LOW
- Clear action items with urgency indicators

## 2. UI Components and Layout

### 2.1 Page Structure

```
┌─────────────────────────────────────────────────────────────┐
│                    Navigation Sidebar                       │
├─────────────────────────────────────────────────────────────┤
│                    Page Title Header                        │
├─────────────────────────────────────────────────────────────┤
│                Portfolio Status Metrics (5 cols)            │
├─────────────────────────────────────────────────────────────┤
│                    Trade History Section                    │
│  ├── Metrics Row (5 cols)                                  │
│  ├── Add Trade Button                                      │
│  ├── Trade Entry Form (conditional)                        │
│  ├── Trade History Table                                   │
│  └── Cumulative P/L Chart                                  │
├─────────────────────────────────────────────────────────────┤
│                 Balance Forecast Timeline                   │
│  ├── Expiration Date Projections (expandable)              │
│  └── Forecast Summary (4 cols)                             │
├─────────────────────────────────────────────────────────────┤
│              Individual Position Forecasts                  │
│  └── Position Cards (expandable, 4 cols each)              │
├─────────────────────────────────────────────────────────────┤
│               Theta Decay Profit Forecast                   │
│  └── Position Theta Tables (expandable)                    │
├─────────────────────────────────────────────────────────────┤
│                AI Trade Analysis Section                    │
│  ├── Portfolio Recommendation                              │
│  ├── High-Profit Alerts                                    │
│  └── Individual Position Analysis (expandable)             │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Component Specifications

#### 2.2.1 Navigation Sidebar
- **Width**: 250px fixed
- **Buttons**: Full width, primary color for active page
- **Pages**: Dashboard, Opportunities, Positions, Premium Scanner, etc.

#### 2.2.2 Portfolio Status Metrics
- **Layout**: 5 equal columns
- **Components**: `st.metric()` with label, value, delta
- **Update**: Real-time when Robinhood connected

#### 2.2.3 Trade Entry Form
- **Trigger**: "+ Add Trade" button
- **Fields**:
  - Symbol (text, uppercase transform)
  - Strike Price (number, $0.50 steps)
  - Premium Collected (number, $10 steps)
  - Expiration Date (date picker)
  - Contracts (integer, min 1)
  - Open Date (date picker, default today)
  - Notes (textarea, optional)
- **Actions**: Save Trade (primary), Cancel

#### 2.2.4 Trade History Table
- **Columns**: Symbol, Open Date, Close Date, Strike, Premium, Days, P/L, P/L %, Ann. Return, Reason
- **Sorting**: By close date descending
- **Limit**: 50 most recent trades
- **Styling**: Green for profits, red for losses

#### 2.2.5 Cumulative P/L Chart
- **Type**: Line chart with area fill
- **X-axis**: Date
- **Y-axis**: Cumulative P/L ($)
- **Features**: Hover tooltips, zoom capability

#### 2.2.6 Position Forecast Cards
- **Layout**: Expandable accordions
- **Content**: 4 columns per card
  - Position Details
  - Current Status
  - Forecast (If Expires OTM)
  - Risk (If Assigned)

#### 2.2.7 Theta Decay Tables
- **Columns**: Day, Date, Days Left, Option Value, Profit, Daily Gain
- **Rows**: Today through expiration (max 60)
- **Styling**: Color-coded profit changes

#### 2.2.8 AI Recommendation Cards
- **Components**:
  - Emoji indicator (urgency/action type)
  - Action headline
  - Detailed reasoning
  - Metrics display
- **Colors**: Success (green), Warning (yellow), Danger (red)

## 3. Data Models

### 3.1 Trade Model

```python
@dataclass
class Trade:
    id: int
    symbol: str
    strategy_type: str = 'cash_secured_put'

    # Opening details
    open_date: datetime
    strike_price: Decimal
    expiration_date: date
    premium_collected: Decimal
    contracts: int = 1
    dte_at_open: int

    # Closing details (nullable)
    close_date: Optional[datetime] = None
    close_price: Optional[Decimal] = None
    close_reason: Optional[str] = None  # 'early_close', 'expiration', 'assignment'

    # Calculated fields
    days_held: Optional[int] = None
    profit_loss: Optional[Decimal] = None
    profit_loss_percent: Optional[Decimal] = None
    annualized_return: Optional[Decimal] = None

    # Metadata
    status: str = 'open'  # 'open', 'closed', 'assigned'
    notes: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
```

### 3.2 Position Model

```python
@dataclass
class Position:
    symbol: str
    type: str  # 'CSP', 'CC', 'Stock'
    strike: float
    expiration: str
    premium: float
    current_value: float
    option_price: float
    pnl: float
    pnl_percent: float
    days_to_expiry: int
    chart_url: str
```

### 3.3 Forecast Model

```python
@dataclass
class Forecast:
    date: str
    positions: int
    premium_income: float
    capital_at_risk: float
    best_case_balance: float
    expected_balance: float
    worst_case_balance: float
```

### 3.4 AI Recommendation Model

```python
@dataclass
class Recommendation:
    action: str  # 'BUY_BACK_IMMEDIATELY', 'HOLD_POSITION', etc.
    reason: str
    detail: str
    urgency: str  # 'HIGH', 'MEDIUM', 'LOW'
    emoji: str
    metrics: Dict[str, Any]
```

## 4. Business Logic

### 4.1 P&L Calculation Logic

```python
def calculate_pnl(trade: Trade) -> Dict[str, float]:
    """Calculate profit/loss metrics for a trade"""

    # Basic P&L
    profit_loss = trade.premium_collected - (trade.close_price or 0)

    # Percentage return
    profit_loss_percent = (profit_loss / trade.premium_collected * 100)
                         if trade.premium_collected > 0 else 0

    # Days held (minimum 1 for calculation)
    days_held = max(1, (trade.close_date - trade.open_date).days)

    # Annualized return
    annualized_return = (profit_loss_percent / days_held) * 365

    return {
        'profit_loss': profit_loss,
        'profit_loss_percent': profit_loss_percent,
        'days_held': days_held,
        'annualized_return': annualized_return
    }
```

### 4.2 Theta Decay Calculation

```python
def calculate_theta_decay(current_value: float,
                         days_remaining: int,
                         initial_dte: int) -> float:
    """Calculate projected option value using square root of time model"""

    if days_remaining <= 0 or initial_dte <= 0:
        return 0

    # Square root of time decay approximation
    decay_factor = math.sqrt(days_remaining) / math.sqrt(initial_dte)
    projected_value = current_value * decay_factor

    return projected_value
```

### 4.3 Assignment Probability Estimation

```python
def estimate_assignment_probability(current_price: float,
                                   strike_price: float) -> float:
    """Estimate probability of assignment based on moneyness"""

    # Simple linear model based on how far ITM/OTM
    moneyness_percent = ((current_price - strike_price) / strike_price) * 100

    if current_price < strike_price:  # ITM
        # Higher probability as we go deeper ITM
        probability = min(90, 50 + abs(moneyness_percent))
    else:  # OTM
        # Lower probability as we go deeper OTM
        probability = max(10, 50 - moneyness_percent)

    return probability
```

### 4.4 Balance Forecast Scenarios

```python
def calculate_forecast_scenarios(current_balance: float,
                                premium_income: float,
                                capital_deployed: float) -> Dict[str, float]:
    """Calculate three scenarios for balance forecasting"""

    # Best case: All CSPs expire worthless, keep all premium
    best_case = current_balance + premium_income

    # Worst case: All CSPs assigned, deploy capital but keep premium
    worst_case = current_balance - capital_deployed + premium_income

    # Expected case: 70% expire worthless (statistical average for OTM options)
    expected_case = current_balance + (premium_income * 0.7) - (capital_deployed * 0.3)

    return {
        'best_case': best_case,
        'expected_case': expected_case,
        'worst_case': worst_case
    }
```

### 4.5 AI Recommendation Logic

```python
def generate_recommendation(profit_pct: float,
                           days_to_expiry: int,
                           is_itm: bool) -> Recommendation:
    """Generate AI recommendation based on position metrics"""

    # Profit-taking thresholds
    if profit_pct >= 75:
        return Recommendation(
            action='BUY_BACK_IMMEDIATELY',
            reason=f'Captured {profit_pct:.1f}% of max profit',
            detail='Close position and redeploy capital for higher returns',
            urgency='HIGH',
            emoji='🎯'
        )

    elif profit_pct >= 50 and days_to_expiry > 7:
        return Recommendation(
            action='BUY_BACK_RECOMMENDED',
            reason=f'{profit_pct:.1f}% profit with {days_to_expiry} days remaining',
            detail='Strong profit captured. Consider closing for new trades',
            urgency='MEDIUM',
            emoji='✅'
        )

    # Risk management
    elif is_itm and days_to_expiry < 7:
        return Recommendation(
            action='PREPARE_FOR_ASSIGNMENT',
            reason=f'ITM with {days_to_expiry} days left',
            detail='High probability of assignment. Prepare to take shares',
            urgency='HIGH',
            emoji='⚠️'
        )

    # Default holding strategy
    else:
        return Recommendation(
            action='HOLD_POSITION',
            reason=f'{profit_pct:.1f}% profit captured so far',
            detail='Continue collecting theta decay',
            urgency='LOW',
            emoji='💎'
        )
```

## 5. Edge Cases and Error Handling

### 5.1 Data Validation

#### Invalid Trade Data
- **Scenario**: User enters negative premium or strike price
- **Handling**: Form validation prevents submission, shows error message
- **Implementation**:
```python
if premium <= 0:
    st.error("Premium must be greater than zero")
    return
```

#### Date Inconsistencies
- **Scenario**: Close date before open date
- **Handling**: Validation error, prompt for correction
- **Implementation**:
```python
if close_date < open_date:
    raise ValueError("Close date cannot be before open date")
```

### 5.2 API Failures

#### Robinhood Connection Loss
- **Scenario**: API timeout or authentication failure
- **Handling**: Graceful degradation to manual mode
- **Implementation**:
```python
try:
    account_data = get_account()
except Exception as e:
    st.warning("Robinhood connection lost. Showing cached data.")
    account_data = get_cached_account_data()
```

#### Market Data Unavailable
- **Scenario**: yfinance API failure
- **Handling**: Use last known prices or strike price as fallback
- **Implementation**:
```python
try:
    current_price = ticker.info.get('currentPrice')
except:
    current_price = position.strike_price  # Fallback
    st.caption("Using strike price as estimate")
```

### 5.3 Database Errors

#### Connection Failure
- **Scenario**: PostgreSQL unavailable
- **Handling**: Queue operations for retry, show warning
- **Implementation**:
```python
@retry(max_attempts=3, backoff=2)
def save_trade(trade_data):
    try:
        return db.insert_trade(trade_data)
    except psycopg2.OperationalError:
        queue_for_later(trade_data)
        raise
```

#### Data Corruption
- **Scenario**: Invalid data in database
- **Handling**: Skip corrupted records, log for investigation
- **Implementation**:
```python
def get_trades():
    trades = []
    for row in db.fetch_all():
        try:
            trades.append(validate_trade(row))
        except ValidationError as e:
            logger.error(f"Corrupted trade {row['id']}: {e}")
            continue
    return trades
```

### 5.4 Calculation Edge Cases

#### Division by Zero
- **Scenario**: Premium is zero in P&L percentage calculation
- **Handling**: Return 0% instead of error
- **Implementation**:
```python
profit_pct = (profit / premium * 100) if premium > 0 else 0
```

#### Negative Days to Expiry
- **Scenario**: Option already expired
- **Handling**: Show as expired, disable certain features
- **Implementation**:
```python
if days_to_expiry < 0:
    st.warning("Position has expired")
    show_expired_position_ui(position)
```

### 5.5 UI Edge Cases

#### Empty Portfolio
- **Scenario**: No positions to display
- **Handling**: Show helpful onboarding message
- **Implementation**:
```python
if not positions:
    st.info("No active positions. Click '+ Add Trade' to start tracking")
```

#### Concurrent Updates
- **Scenario**: Multiple users/tabs updating same trade
- **Handling**: Optimistic locking with version checking
- **Implementation**:
```python
def update_trade(trade_id, updates, version):
    current = db.get_trade(trade_id)
    if current.version != version:
        raise ConcurrentUpdateError("Trade was modified")
    db.update_with_version(trade_id, updates, version + 1)
```

## 6. Performance Requirements

### Response Times
- Page load: < 2 seconds
- Trade submission: < 1 second
- Position refresh: < 3 seconds
- Chart rendering: < 1 second

### Scalability
- Support 1000+ trades in history
- Handle 100+ concurrent positions
- Process 50+ expiration dates in forecast

### Resource Usage
- Memory: < 500MB per session
- CPU: < 20% average utilization
- Database connections: Max 10 concurrent

## 7. Testing Specifications

### Unit Tests
- P&L calculation accuracy
- Theta decay formulas
- Date handling edge cases
- Validation logic

### Integration Tests
- Database CRUD operations
- API integration resilience
- Cache synchronization
- Session management

### E2E Tests
- Complete trade lifecycle
- Portfolio refresh flow
- Forecast generation
- AI recommendation triggers

### Performance Tests
- Load testing with 1000 trades
- Concurrent user simulation
- Database query optimization
- Cache effectiveness