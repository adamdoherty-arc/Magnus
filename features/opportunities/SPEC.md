# Opportunities Feature - Technical Specification

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Business Requirements](#business-requirements)
3. [Functional Requirements](#functional-requirements)
4. [Non-Functional Requirements](#non-functional-requirements)
5. [System Interfaces](#system-interfaces)
6. [Data Models](#data-models)
7. [Business Logic](#business-logic)
8. [Validation Rules](#validation-rules)
9. [User Stories](#user-stories)
10. [Acceptance Criteria](#acceptance-criteria)
11. [Performance Requirements](#performance-requirements)
12. [Security Requirements](#security-requirements)

## Executive Summary

### Purpose

The Opportunities feature is a critical component of the Wheel Strategy Trading System that automates the discovery and analysis of optimal cash-secured put (CSP) opportunities. It addresses the core challenge of manually scanning hundreds of stocks to find the best risk-adjusted returns for options traders implementing the wheel strategy.

### Scope

This specification covers:
- Automated market scanning for option opportunities
- Multi-criteria filtering and ranking algorithms
- Real-time premium calculation and return projections
- Risk assessment and liquidity validation
- User interface for opportunity discovery and analysis

### Success Metrics

1. **Efficiency**: Reduce opportunity discovery time from hours to seconds
2. **Quality**: Identify opportunities with >15% annual returns and adequate liquidity
3. **Accuracy**: Achieve >95% accuracy in premium calculations
4. **Reliability**: Maintain 99.9% uptime during market hours

## Business Requirements

### BR-001: Market Opportunity Discovery

**Requirement**: The system shall automatically identify cash-secured put opportunities across multiple stocks.

**Rationale**: Manual scanning is time-consuming and prone to missing opportunities.

**Priority**: Critical

**Stakeholders**: Active traders, portfolio managers

### BR-002: Risk-Adjusted Return Optimization

**Requirement**: Opportunities shall be ranked by risk-adjusted returns considering premium, time value, and assignment probability.

**Rationale**: Maximize income while managing assignment risk.

**Priority**: Critical

**Stakeholders**: Risk-conscious investors

### BR-003: Liquidity Assurance

**Requirement**: Only display opportunities with sufficient trading volume and open interest.

**Rationale**: Ensure traders can enter and exit positions without significant slippage.

**Priority**: High

**Stakeholders**: All users

### BR-004: Multi-Strategy Support

**Requirement**: Support different trading strategies (weekly, monthly, high IV, sector-specific).

**Rationale**: Different traders have different risk tolerances and time horizons.

**Priority**: Medium

**Stakeholders**: Diverse trading personas

### BR-005: Real-Time Market Data

**Requirement**: Use current market prices and option chains for calculations.

**Rationale**: Stale data leads to missed opportunities or poor trades.

**Priority**: Critical

**Stakeholders**: Day traders, active managers

## Functional Requirements

### FR-001: Symbol Universe Definition

**Description**: System shall maintain a universe of tradable symbols for scanning.

**Acceptance Criteria**:
- Support manual symbol lists
- Import from TradingView watchlists
- Filter by market cap, sector, or custom criteria
- Maximum 500 symbols per scan

### FR-002: Option Chain Retrieval

**Description**: Fetch complete option chains for selected symbols.

**Acceptance Criteria**:
- Retrieve puts for next 5 expiration dates
- Include bid, ask, volume, open interest, Greeks
- Handle missing data gracefully
- Cache results for 5 minutes during market hours

### FR-003: Premium Calculation Engine

**Description**: Calculate premium metrics for each opportunity.

**Inputs**:
- Current stock price
- Strike price
- Option premium (bid/ask midpoint)
- Days to expiration

**Outputs**:
- Premium in dollars
- Premium as percentage of strike
- Monthly return (normalized to 30 days)
- Annual return (extrapolated)

**Formula**:
```
premium_pct = (premium / strike) * 100
monthly_return = (premium_pct / days_to_expiry) * 30
annual_return = monthly_return * 12
```

### FR-004: Filtering System

**Description**: Apply user-defined filters to opportunities.

**Filter Parameters**:
- Maximum stock price
- Minimum premium percentage
- Target days to expiration
- Minimum volume/open interest
- Maximum implied volatility
- Strike distance from current price

### FR-005: Ranking Algorithm

**Description**: Score and rank opportunities by multiple factors.

**Ranking Factors**:
- Return metrics (40% weight)
- Liquidity score (30% weight)
- Risk assessment (20% weight)
- Time efficiency (10% weight)

### FR-006: Strategy Templates

**Description**: Provide pre-configured scanning strategies.

**Strategies**:

| Strategy | Max Price | Min Premium | DTE | Special Filters |
|----------|-----------|-------------|-----|-----------------|
| Best Overall | $50 | 1.0% | 30 | Balanced |
| High IV | $50 | 1.5% | 30 | IV > 40% |
| Weekly | $50 | 0.5% | 7-14 | Short-term |
| Monthly | $50 | 1.0% | 30-45 | Standard |
| Tech Focus | $50 | 1.0% | 30 | Tech sector |

### FR-007: Results Display

**Description**: Present opportunities in an organized, sortable interface.

**Display Requirements**:
- Tabular format with key metrics
- Sort by any column
- Expand for detailed view
- Color coding for opportunity quality
- Export to CSV functionality

### FR-008: Opportunity Details

**Description**: Provide comprehensive details for each opportunity.

**Details Include**:
- Complete option chain data
- Historical volatility chart
- Assignment probability estimate
- Risk metrics
- Similar opportunities
- Trade execution guidance

## Non-Functional Requirements

### NFR-001: Performance

**Requirement**: Complete market scan within acceptable time limits.

**Specifications**:
- 100 symbols: <30 seconds
- 250 symbols: <60 seconds
- 500 symbols: <120 seconds
- UI response: <100ms for user actions

### NFR-002: Scalability

**Requirement**: Handle increasing load without degradation.

**Specifications**:
- Support 1,000 concurrent users
- Process 10,000 symbols/minute system-wide
- Horizontal scaling capability
- Database sharding ready

### NFR-003: Reliability

**Requirement**: Maintain high availability during market hours.

**Specifications**:
- 99.9% uptime (8:30 AM - 4:00 PM ET)
- Graceful degradation on API failures
- Automatic failover to backup data sources
- Error recovery within 30 seconds

### NFR-004: Usability

**Requirement**: Intuitive interface requiring minimal training.

**Specifications**:
- Single-click scanning
- Clear visual hierarchy
- Responsive design for mobile
- Keyboard shortcuts for power users
- Tooltips for all metrics

### NFR-005: Data Accuracy

**Requirement**: Ensure calculation precision and data freshness.

**Specifications**:
- Price data: <1 minute delay
- Greeks calculation: 4 decimal precision
- Return calculations: 2 decimal precision
- Data validation on all inputs

## System Interfaces

### SI-001: Market Data APIs

**Yahoo Finance Integration**:
```python
class YahooFinanceInterface:
    endpoints = {
        'quote': '/v7/finance/quote',
        'options': '/v7/finance/options/{symbol}',
        'historical': '/v8/finance/chart/{symbol}'
    }

    rate_limits = {
        'requests_per_second': 2,
        'daily_limit': 10000
    }
```

**Robinhood Integration**:
```python
class RobinhoodInterface:
    endpoints = {
        'login': '/api-token-auth/',
        'quotes': '/quotes/{symbol}/',
        'options': '/options/chains/{chain_id}/',
        'positions': '/options/positions/'
    }

    authentication = 'OAuth2'
    session_timeout = 86400  # 24 hours
```

### SI-002: Database Schema

**Opportunities Table**:
```sql
CREATE TABLE opportunities (
    id UUID PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    scan_timestamp TIMESTAMP NOT NULL,
    current_price DECIMAL(10, 2),
    strike_price DECIMAL(10, 2),
    expiration_date DATE,
    days_to_expiry INTEGER,
    premium DECIMAL(10, 4),
    premium_pct DECIMAL(5, 2),
    monthly_return DECIMAL(5, 2),
    annual_return DECIMAL(6, 2),
    implied_volatility DECIMAL(5, 2),
    delta DECIMAL(5, 4),
    volume INTEGER,
    open_interest INTEGER,
    bid_ask_spread DECIMAL(10, 4),
    liquidity_score INTEGER,
    risk_score INTEGER,
    overall_score DECIMAL(5, 2),
    strategy_type VARCHAR(50),

    INDEX idx_symbol (symbol),
    INDEX idx_return (monthly_return DESC),
    INDEX idx_scan_time (scan_timestamp),
    INDEX idx_score (overall_score DESC)
);
```

### SI-003: Cache Layer

**Redis Cache Structure**:
```python
cache_schema = {
    'quote:{symbol}': {
        'ttl': 60,  # 1 minute for quotes
        'data': 'JSON serialized quote data'
    },
    'options:{symbol}:{expiry}': {
        'ttl': 300,  # 5 minutes for options
        'data': 'JSON serialized option chain'
    },
    'scan_results:{strategy}': {
        'ttl': 900,  # 15 minutes for scan results
        'data': 'JSON serialized opportunities list'
    }
}
```

## Data Models

### DM-001: Opportunity Model

```python
@dataclass
class Opportunity:
    # Identification
    symbol: str
    expiration_date: date
    strike_price: float

    # Market Data
    current_price: float
    bid: float
    ask: float
    last_price: float
    volume: int
    open_interest: int

    # Calculated Metrics
    premium: float  # Dollar amount per contract
    premium_pct: float  # As percentage of strike
    days_to_expiry: int
    monthly_return: float  # Normalized to 30 days
    annual_return: float  # Extrapolated annual

    # Greeks
    delta: float
    gamma: float
    theta: float
    vega: float
    implied_volatility: float

    # Risk Metrics
    probability_itm: float  # Probability of being in-the-money
    expected_value: float
    risk_score: int  # 1-100 scale

    # Liquidity Metrics
    bid_ask_spread: float
    liquidity_score: int  # 1-100 scale

    # Meta Information
    scan_timestamp: datetime
    data_source: str
    strategy_type: str
```

### DM-002: Scan Parameters Model

```python
@dataclass
class ScanParameters:
    # Symbol Selection
    symbols: List[str]
    symbol_source: str  # 'manual', 'watchlist', 'all'

    # Price Filters
    max_stock_price: float
    min_stock_price: float

    # Premium Filters
    min_premium_pct: float
    max_premium_pct: float

    # Time Filters
    target_dte: int
    dte_range: int  # +/- days from target

    # Risk Filters
    max_delta: float  # Absolute value
    min_delta: float
    max_iv: float
    min_iv: float

    # Liquidity Filters
    min_volume: int
    min_open_interest: int
    max_spread_pct: float

    # Strategy
    strategy_type: str
    sort_by: str  # 'monthly_return', 'annual_return', 'premium_pct'
    limit: int  # Maximum results to return
```

### DM-003: Market Data Model

```python
@dataclass
class MarketData:
    symbol: str
    timestamp: datetime

    # Stock Data
    last_price: float
    bid: float
    ask: float
    volume: int
    market_cap: float
    pe_ratio: float
    dividend_yield: float

    # Volatility Data
    historical_volatility: float
    implied_volatility_mean: float
    iv_rank: float  # 0-100 percentile
    iv_percentile: float

    # Technical Indicators
    rsi: float
    sma_20: float
    sma_50: float
    sma_200: float
    bollinger_upper: float
    bollinger_lower: float
```

## Business Logic

### BL-001: Opportunity Scoring Algorithm

```python
def calculate_opportunity_score(opportunity: Opportunity) -> float:
    """
    Multi-factor scoring algorithm for ranking opportunities

    Weights:
    - Return: 40%
    - Liquidity: 30%
    - Risk: 20%
    - Efficiency: 10%
    """

    # Return Score (0-40 points)
    return_score = min(40, opportunity.monthly_return * 10)

    # Liquidity Score (0-30 points)
    volume_score = min(15, opportunity.volume / 100)
    oi_score = min(15, opportunity.open_interest / 50)
    liquidity_score = volume_score + oi_score

    # Risk Score (0-20 points)
    # Lower delta = lower risk for CSP
    delta_score = max(0, 20 * (1 - abs(opportunity.delta)))

    # Efficiency Score (0-10 points)
    # Premium per day
    daily_return = opportunity.premium_pct / opportunity.days_to_expiry
    efficiency_score = min(10, daily_return * 100)

    total_score = (
        return_score +
        liquidity_score +
        delta_score +
        efficiency_score
    )

    return round(total_score, 2)
```

### BL-002: Strike Selection Logic

```python
def select_optimal_strike(
    current_price: float,
    put_chain: List[Dict],
    target_delta: float = -0.30
) -> float:
    """
    Select optimal strike price based on delta target

    Business Rules:
    1. Target 30 delta (30% probability of assignment)
    2. Must be OTM (strike < current_price)
    3. Minimum 3% OTM to avoid early assignment
    4. Maximum 15% OTM to maintain reasonable premium
    """

    # Filter valid strikes
    valid_strikes = []

    min_strike = current_price * 0.85  # Max 15% OTM
    max_strike = current_price * 0.97  # Min 3% OTM

    for put in put_chain:
        strike = put['strike']
        delta = put.get('delta', 0)

        if min_strike <= strike <= max_strike:
            delta_diff = abs(delta - target_delta)
            valid_strikes.append({
                'strike': strike,
                'delta': delta,
                'delta_diff': delta_diff,
                'premium': put['premium']
            })

    if not valid_strikes:
        return None

    # Sort by closest to target delta
    valid_strikes.sort(key=lambda x: x['delta_diff'])

    # Return best strike
    return valid_strikes[0]['strike']
```

### BL-003: Liquidity Validation

```python
def validate_liquidity(
    volume: int,
    open_interest: int,
    bid: float,
    ask: float
) -> Tuple[bool, str]:
    """
    Validate option liquidity meets minimum requirements

    Business Rules:
    1. Volume >= 100 OR Open Interest >= 50
    2. Bid-Ask spread < 20% of mid-price
    3. Both bid and ask must be > 0
    """

    # Check for valid quotes
    if bid <= 0 or ask <= 0:
        return False, "No valid bid/ask"

    # Check spread
    mid_price = (bid + ask) / 2
    spread = ask - bid
    spread_pct = (spread / mid_price) * 100

    if spread_pct > 20:
        return False, f"Spread too wide: {spread_pct:.1f}%"

    # Check volume/OI
    if volume < 100 and open_interest < 50:
        return False, f"Insufficient liquidity: Vol={volume}, OI={open_interest}"

    return True, "Liquidity acceptable"
```

### BL-004: Assignment Probability Estimation

```python
def estimate_assignment_probability(
    current_price: float,
    strike_price: float,
    days_to_expiry: int,
    implied_volatility: float
) -> float:
    """
    Estimate probability of option being assigned

    Uses simplified Black-Scholes probability model
    """

    # Calculate moneyness
    moneyness = strike_price / current_price

    # Time factor
    time_factor = days_to_expiry / 365

    # Volatility adjustment
    vol_factor = implied_volatility * math.sqrt(time_factor)

    # Calculate z-score
    z_score = (math.log(moneyness) + 0.5 * vol_factor ** 2) / vol_factor

    # Probability using normal CDF
    probability = norm.cdf(z_score)

    return round(probability * 100, 2)
```

### BL-005: Return Calculation Rules

```python
def calculate_returns(
    premium: float,
    strike: float,
    days_to_expiry: int,
    include_assignment: bool = False
) -> Dict[str, float]:
    """
    Calculate various return metrics

    Business Rules:
    1. Base return on premium only (not assignment)
    2. Normalize monthly to 30 days
    3. Annualize assuming continuous trading
    4. Account for capital requirements
    """

    # Capital required for CSP
    capital_required = strike * 100  # Per contract

    # Premium return
    premium_return = (premium / capital_required) * 100

    # Time-adjusted returns
    daily_return = premium_return / days_to_expiry
    monthly_return = daily_return * 30
    annual_return = monthly_return * 12

    # Risk-adjusted return (Sharpe-like)
    # Assuming 4.5% risk-free rate
    risk_free_daily = 0.045 / 365
    excess_return = daily_return - risk_free_daily

    returns = {
        'premium_pct': premium_return,
        'daily_return': daily_return,
        'monthly_return': monthly_return,
        'annual_return': annual_return,
        'risk_adjusted_return': excess_return * 365
    }

    if include_assignment:
        # Additional calculations if assigned
        # Assumes selling at strike price
        returns['break_even'] = strike - premium
        returns['max_profit'] = premium
        returns['max_loss'] = strike - premium  # If stock goes to 0

    return returns
```

## Validation Rules

### VR-001: Input Validation

```python
class InputValidator:
    """
    Validation rules for user inputs
    """

    @staticmethod
    def validate_symbol(symbol: str) -> bool:
        """Symbol must be 1-5 uppercase letters"""
        pattern = r'^[A-Z]{1,5}$'
        return bool(re.match(pattern, symbol.upper()))

    @staticmethod
    def validate_price(price: float, min_val: float = 1, max_val: float = 10000) -> bool:
        """Price must be positive and within reasonable range"""
        return min_val <= price <= max_val

    @staticmethod
    def validate_dte(dte: int) -> bool:
        """DTE must be between 1 and 365 days"""
        return 1 <= dte <= 365

    @staticmethod
    def validate_premium_pct(pct: float) -> bool:
        """Premium percentage must be between 0 and 50%"""
        return 0 < pct <= 50

    @staticmethod
    def validate_delta(delta: float) -> bool:
        """Delta must be between -1 and 0 for puts"""
        return -1 <= delta <= 0
```

### VR-002: Data Quality Rules

```python
def validate_opportunity_data(opportunity: Opportunity) -> List[str]:
    """
    Validate opportunity data quality

    Returns list of validation errors
    """
    errors = []

    # Price consistency
    if opportunity.strike_price >= opportunity.current_price:
        errors.append("Strike must be below current price for CSP")

    # Premium sanity checks
    if opportunity.premium <= 0:
        errors.append("Premium must be positive")

    if opportunity.premium > opportunity.strike_price * 0.2:
        errors.append("Premium suspiciously high (>20% of strike)")

    # Time validation
    if opportunity.days_to_expiry <= 0:
        errors.append("Option has expired")

    # Greeks validation
    if opportunity.delta > 0:
        errors.append("Put delta must be negative")

    if opportunity.implied_volatility <= 0:
        errors.append("IV must be positive")

    if opportunity.implied_volatility > 500:
        errors.append("IV unreasonably high (>500%)")

    # Liquidity validation
    if opportunity.bid > opportunity.ask:
        errors.append("Bid exceeds ask price")

    return errors
```

## User Stories

### US-001: Quick Opportunity Scan

**As a** busy trader
**I want to** quickly scan for the best CSP opportunities
**So that** I can make trading decisions efficiently

**Acceptance Criteria**:
- One-click scanning with default parameters
- Results displayed within 30 seconds
- Top 10 opportunities clearly highlighted
- Ability to sort and filter results

### US-002: Strategy-Based Scanning

**As a** trader with specific strategies
**I want to** scan using predefined strategy templates
**So that** I find opportunities matching my trading style

**Acceptance Criteria**:
- At least 5 strategy templates available
- Clear description of each strategy
- Ability to customize template parameters
- Save custom strategies for reuse

### US-003: Risk Assessment

**As a** risk-conscious investor
**I want to** see clear risk metrics for each opportunity
**So that** I can make informed decisions

**Acceptance Criteria**:
- Display delta for assignment probability
- Show implied volatility
- Calculate maximum loss scenarios
- Provide risk score (1-100)

### US-004: Liquidity Verification

**As a** trader
**I want to** only see liquid opportunities
**So that** I can enter and exit positions easily

**Acceptance Criteria**:
- Filter out illiquid options automatically
- Display volume and open interest
- Show bid-ask spread
- Provide liquidity score

### US-005: Historical Performance

**As a** systematic trader
**I want to** see historical performance of similar opportunities
**So that** I can validate the strategy

**Acceptance Criteria**:
- Track success rate of recommendations
- Show average returns achieved
- Display win/loss ratio
- Provide performance attribution

## Acceptance Criteria

### AC-001: Functional Completeness

- [ ] All strategy templates functional
- [ ] Filtering works correctly
- [ ] Sorting works on all columns
- [ ] Details view shows all metrics
- [ ] Export functionality works

### AC-002: Performance Benchmarks

- [ ] 100 symbol scan < 30 seconds
- [ ] UI responsive (< 100ms)
- [ ] No memory leaks after 1 hour usage
- [ ] Handles API failures gracefully

### AC-003: Data Accuracy

- [ ] Premium calculations match broker quotes ±1%
- [ ] Greeks calculations validated against Black-Scholes
- [ ] Return calculations mathematically verified
- [ ] All edge cases handled

### AC-004: User Experience

- [ ] Intuitive navigation
- [ ] Clear error messages
- [ ] Helpful tooltips
- [ ] Mobile responsive
- [ ] Keyboard accessible

## Performance Requirements

### Response Time Requirements

| Operation | Target | Maximum |
|-----------|--------|---------|
| Page Load | 500ms | 2s |
| Start Scan | 100ms | 500ms |
| Sort Table | 50ms | 200ms |
| Filter Apply | 100ms | 500ms |
| Export Data | 1s | 5s |

### Throughput Requirements

| Metric | Requirement |
|--------|------------|
| Concurrent Users | 1,000 |
| Scans per Minute | 100 |
| Symbols per Scan | 500 |
| API Calls per Second | 50 |

### Resource Utilization

| Resource | Limit |
|----------|-------|
| CPU Usage | < 70% |
| Memory Usage | < 2GB |
| Network Bandwidth | < 10 Mbps |
| Database Connections | < 100 |

## Security Requirements

### SR-001: Authentication

- Secure credential storage (encrypted)
- Session timeout after 24 hours
- Multi-factor authentication support
- API key rotation capability

### SR-002: Authorization

- Role-based access control
- Feature-level permissions
- Audit trail for all actions
- Data access logging

### SR-003: Data Protection

- TLS encryption for all API calls
- Encrypted storage for sensitive data
- PII data masking
- GDPR compliance

### SR-004: Rate Limiting

- Per-user rate limits
- API call quotas
- DDoS protection
- Automatic blacklisting for abuse

## Testing Requirements

### Unit Tests

```python
class TestOpportunityScoring:
    def test_high_return_opportunity(self):
        """Test scoring of high-return opportunity"""
        opp = create_test_opportunity(monthly_return=3.5)
        score = calculate_opportunity_score(opp)
        assert score >= 70  # Should score well

    def test_low_liquidity_penalty(self):
        """Test that low liquidity reduces score"""
        opp = create_test_opportunity(volume=10, open_interest=5)
        score = calculate_opportunity_score(opp)
        assert score < 50  # Should score poorly
```

### Integration Tests

```python
class TestMarketDataIntegration:
    def test_yahoo_finance_connection(self):
        """Test Yahoo Finance API integration"""
        data = fetch_yahoo_quote("AAPL")
        assert data is not None
        assert 'regularMarketPrice' in data

    def test_option_chain_retrieval(self):
        """Test complete option chain fetching"""
        chain = fetch_option_chain("SPY", "2024-12-20")
        assert len(chain) > 0
        assert 'puts' in chain
```

### Performance Tests

```python
class TestPerformance:
    def test_scan_performance(self):
        """Test scanning performance meets requirements"""
        symbols = get_test_symbols(100)
        start = time.time()
        results = scanner.scan_premiums(symbols)
        duration = time.time() - start
        assert duration < 30  # Must complete in 30 seconds
```

## Deployment Requirements

### Infrastructure

- Load balancer for high availability
- Redis cache cluster
- PostgreSQL database with replication
- CDN for static assets
- Monitoring and alerting system

### Deployment Process

1. Automated testing pipeline
2. Staging environment validation
3. Blue-green deployment
4. Rollback capability
5. Performance monitoring

## Documentation Requirements

### User Documentation

- Getting started guide
- Strategy explanations
- FAQ section
- Video tutorials
- API documentation

### Technical Documentation

- System architecture
- Database schema
- API specifications
- Deployment guide
- Troubleshooting guide

## Conclusion

This specification defines a comprehensive opportunity scanning system that automates the discovery of optimal options trading opportunities. The system balances sophistication with usability, providing powerful analytics while maintaining an intuitive interface. By implementing these requirements, the Opportunities feature will deliver significant value to wheel strategy traders, enabling them to identify and capitalize on the best risk-adjusted returns in the options market.