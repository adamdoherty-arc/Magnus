# Calendar Spreads Feature - Technical Specifications

## Table of Contents
1. [Functional Requirements](#functional-requirements)
2. [Mathematical Formulas](#mathematical-formulas)
3. [Greeks Calculations](#greeks-calculations)
4. [Scoring Algorithm](#scoring-algorithm)
5. [Data Requirements](#data-requirements)
6. [Integration Specifications](#integration-specifications)
7. [Performance Requirements](#performance-requirements)
8. [Business Rules](#business-rules)
9. [Error Handling](#error-handling)
10. [Testing Requirements](#testing-requirements)

## Functional Requirements

### FR-1: Watchlist Integration
```yaml
requirement_id: FR-1
description: System shall integrate with TradingView watchlists
priority: HIGH
acceptance_criteria:
  - Connect to TradingView API with OAuth 2.0
  - Fetch all user watchlists
  - Support multiple watchlist selection
  - Refresh watchlists every 15 minutes
  - Handle up to 500 symbols per watchlist
  - Cache watchlist data for 5 minutes
```

### FR-2: Market Data Retrieval
```yaml
requirement_id: FR-2
description: System shall retrieve real-time options data
priority: HIGH
acceptance_criteria:
  - Fetch options chains for all watchlist symbols
  - Update prices every 30 seconds during market hours
  - Retrieve complete Greeks for all options
  - Support multiple data providers (IBKR, TD, Polygon)
  - Handle missing or stale data gracefully
  - Store 30 days of historical data
```

### FR-3: Calendar Spread Analysis
```yaml
requirement_id: FR-3
description: System shall analyze calendar spread opportunities
priority: HIGH
acceptance_criteria:
  - Identify valid calendar spread combinations
  - Calculate spread metrics for each combination
  - Filter based on user-defined criteria
  - Process minimum 100 symbols per minute
  - Support both call and put calendar spreads
  - Analyze ATM, OTM, and ITM strikes
```

### FR-4: AI Scoring System
```yaml
requirement_id: FR-4
description: System shall score spreads using AI/ML
priority: HIGH
acceptance_criteria:
  - Generate scores from 0-100
  - Update scores in real-time
  - Explain score components
  - Learn from historical outcomes
  - Maintain 85%+ prediction accuracy
  - Process scoring within 100ms per spread
```

### FR-5: P/L Calculations
```yaml
requirement_id: FR-5
description: System shall calculate profit/loss scenarios
priority: HIGH
acceptance_criteria:
  - Calculate max profit and max loss
  - Generate P/L matrix across price/time
  - Compute breakeven points
  - Calculate probability of profit
  - Support commission inclusion
  - Display expected value
```

## Mathematical Formulas

### Calendar Spread Pricing

#### Net Premium (Initial Cost)
```
Net Premium = Premium_back - Premium_front

Where:
- Premium_back = Price of long back-month option
- Premium_front = Price of short front-month option
```

#### Maximum Loss
```
Max Loss = Net Premium = Premium_back - Premium_front

This is the maximum amount that can be lost, occurring when:
- Both options expire worthless (OTM), OR
- Stock moves far from strike causing spread to lose all value
```

#### Maximum Profit Calculation
The maximum profit is complex and depends on several factors:

```
Max Profit ≈ Value_back_at_front_expiry - Net Premium

Where Value_back_at_front_expiry is calculated using Black-Scholes:

For Calls:
C = S₀ × N(d₁) - K × e^(-r×T) × N(d₂)

For Puts:
P = K × e^(-r×T) × N(-d₂) - S₀ × N(-d₁)

Where:
d₁ = [ln(S₀/K) + (r + σ²/2) × T] / (σ × √T)
d₂ = d₁ - σ × √T

Variables:
- S₀ = Current stock price (at front expiry, assumed = K for max profit)
- K = Strike price
- T = Time to back-month expiry from front-month expiry
- r = Risk-free rate
- σ = Implied volatility of back-month option
- N(x) = Cumulative standard normal distribution
```

#### Breakeven Calculation
Calendar spreads have two breakeven points that form a profit "tent":

```
Breakeven occurs when:
Current Spread Value = Initial Net Premium

This requires iterative calculation:
1. For each stock price P:
   Value_spread(P) = Value_back(P) - Value_front(P)
2. Find P where Value_spread(P) = Net Premium

Approximate breakeven range:
Lower_breakeven ≈ K × (1 - σ × √(T_front/252))
Upper_breakeven ≈ K × (1 + σ × √(T_front/252))

Where:
- K = Strike price
- σ = Average implied volatility
- T_front = Days to front-month expiry
```

### Time Decay Differential

#### Theta Ratio
```
Theta Ratio = |Theta_front| / |Theta_back|

Optimal Range: 1.5 to 2.5

Where:
Theta_front = -[S₀ × φ(d₁) × σ / (2√T_front) + r × K × e^(-r×T_front) × N(d₂)]
Theta_back = -[S₀ × φ(d₁) × σ / (2√T_back) + r × K × e^(-r×T_back) × N(d₂)]

φ(x) = Standard normal probability density function
```

#### Daily Decay Advantage
```
Daily_Decay_Advantage = |Theta_front| - |Theta_back|

This represents the daily profit from time decay differential
Target: $5-$20 per day per contract
```

### Volatility Impact

#### IV Differential
```
IV_Differential = IV_front - IV_back

Ideal: -5% to +5% (relatively flat volatility term structure)
```

#### Vega Exposure
```
Net_Vega = Vega_back - Vega_front

Where:
Vega = S₀ × φ(d₁) × √T / 100

Calendar spreads are typically:
- Long vega when IV is low (benefit from IV increase)
- Short vega when IV is high (benefit from IV decrease)
```

#### IV Percentile
```
IV_Percentile = Rank(Current_IV) / Count(Historical_IV_365d) × 100

Target: < 30th percentile for entry
```

### Probability Calculations

#### Probability of Profit (Monte Carlo)
```python
def calculate_pop_monte_carlo(spread, num_simulations=10000):
    """
    Monte Carlo simulation for Probability of Profit
    """
    profitable_outcomes = 0

    for _ in range(num_simulations):
        # Generate random price at front expiry
        # Using log-normal distribution
        Z = np.random.standard_normal()
        S_T = S_0 * exp((μ - σ²/2) * T + σ * √T * Z)

        # Calculate P/L at this price
        pl = calculate_pl_at_expiry(spread, S_T)

        if pl > 0:
            profitable_outcomes += 1

    return profitable_outcomes / num_simulations

Where:
- μ = Expected return (often set to 0 for risk-neutral)
- σ = Historical or implied volatility
- T = Time to front expiry (years)
```

#### Probability of Touch
```
Probability of touching breakeven during life of spread:

P(touch) ≈ 2 × N(|ln(Breakeven/S₀)| / (σ × √T))

This estimates chance of reaching breakeven at any point
```

#### Expected Value
```
Expected Value = Σ(P(outcome_i) × Payoff_i)

Calculated via Monte Carlo:
EV = (1/n) × Σ(PL_simulation_i)

Positive EV indicates favorable risk/reward
```

## Greeks Calculations

### Delta (Direction Risk)
```
Spread Delta = Delta_back - Delta_front

For Calls:
Delta = N(d₁)

For Puts:
Delta = N(d₁) - 1

Target for calendar spreads: -0.10 to +0.10 (near neutral)
```

### Gamma (Delta Change Rate)
```
Spread Gamma = Gamma_back - Gamma_front

Gamma = φ(d₁) / (S₀ × σ × √T)

Calendar spreads have near-zero gamma at initiation
Gamma risk increases as front expiry approaches
```

### Theta (Time Decay)
```
Spread Theta = Theta_back - Theta_front

For Calls:
Theta = -[S₀ × φ(d₁) × σ / (2√T) + r × K × e^(-r×T) × N(d₂)] / 365

For Puts:
Theta = -[S₀ × φ(d₁) × σ / (2√T) - r × K × e^(-r×T) × N(-d₂)] / 365

Calendar spreads have positive theta (collect time decay)
Target: +$0.05 to +$0.20 per day per share
```

### Vega (Volatility Sensitivity)
```
Spread Vega = Vega_back - Vega_front

Vega = S₀ × φ(d₁) × √T / 100

Sign depends on relative IVs:
- Positive if back IV < front IV (benefits from IV increase)
- Negative if back IV > front IV (benefits from IV decrease)
```

### Rho (Interest Rate Sensitivity)
```
Spread Rho = Rho_back - Rho_front

For Calls:
Rho = K × T × e^(-r×T) × N(d₂) / 100

For Puts:
Rho = -K × T × e^(-r×T) × N(-d₂) / 100

Generally minimal impact for short-dated calendar spreads
```

## Scoring Algorithm

### Composite Score Calculation
```python
def calculate_spread_score(spread: CalendarSpread) -> float:
    """
    Calculate composite score (0-100) for calendar spread
    """

    # Component scores with weights
    components = {
        'time_decay': {
            'weight': 0.30,
            'score': score_time_decay(spread)
        },
        'volatility': {
            'weight': 0.25,
            'score': score_volatility(spread)
        },
        'price_stability': {
            'weight': 0.25,
            'score': score_price_stability(spread)
        },
        'liquidity': {
            'weight': 0.10,
            'score': score_liquidity(spread)
        },
        'risk_reward': {
            'weight': 0.10,
            'score': score_risk_reward(spread)
        }
    }

    # Calculate weighted score
    total_score = sum(
        comp['weight'] * comp['score']
        for comp in components.values()
    )

    # Apply penalties and bonuses
    total_score = apply_adjustments(total_score, spread)

    return min(max(total_score, 0), 100)
```

### Time Decay Scoring
```python
def score_time_decay(spread: CalendarSpread) -> float:
    """
    Score based on theta differential (0-100)
    """
    theta_ratio = abs(spread.front_theta / spread.back_theta)

    if 1.8 <= theta_ratio <= 2.2:
        base_score = 100
    elif 1.5 <= theta_ratio <= 2.5:
        base_score = 80
    else:
        # Linear decay outside optimal range
        if theta_ratio < 1.5:
            base_score = max(0, 80 * (theta_ratio / 1.5))
        else:
            base_score = max(0, 80 * (3.0 - theta_ratio) / 0.5)

    # Adjust for absolute theta value
    daily_decay = abs(spread.front_theta - spread.back_theta)
    if daily_decay >= 0.15:
        theta_score = base_score
    elif daily_decay >= 0.10:
        theta_score = base_score * 0.9
    elif daily_decay >= 0.05:
        theta_score = base_score * 0.8
    else:
        theta_score = base_score * 0.6

    return theta_score
```

### Volatility Scoring
```python
def score_volatility(spread: CalendarSpread) -> float:
    """
    Score based on IV conditions (0-100)
    """
    iv_front = spread.front_iv
    iv_percentile = spread.iv_percentile

    # IV level scoring
    if iv_front <= 0.20:
        iv_score = 100
    elif iv_front <= 0.25:
        iv_score = 90
    elif iv_front <= 0.30:
        iv_score = 70
    elif iv_front <= 0.35:
        iv_score = 50
    else:
        iv_score = max(0, 50 - (iv_front - 0.35) * 200)

    # IV percentile adjustment
    if iv_percentile <= 20:
        percentile_multiplier = 1.1
    elif iv_percentile <= 30:
        percentile_multiplier = 1.0
    elif iv_percentile <= 50:
        percentile_multiplier = 0.9
    else:
        percentile_multiplier = 0.7

    # Term structure scoring
    iv_diff = spread.back_iv - spread.front_iv
    if -0.02 <= iv_diff <= 0.02:
        structure_score = 100
    elif -0.05 <= iv_diff <= 0.05:
        structure_score = 70
    else:
        structure_score = 40

    final_score = (
        iv_score * 0.5 +
        structure_score * 0.3 +
        (100 - iv_percentile) * 0.2
    ) * percentile_multiplier

    return min(max(final_score, 0), 100)
```

### Price Stability Scoring
```python
def score_price_stability(spread: CalendarSpread) -> float:
    """
    Score based on underlying price stability (0-100)
    """
    # Historical volatility (20-day)
    hv_20 = spread.historical_volatility_20d

    # Average True Range percentage
    atr_pct = spread.atr_14 / spread.underlying_price

    # Trend strength (0 = no trend, 1 = strong trend)
    trend_strength = spread.adx_14 / 100

    # Base score from historical volatility
    if hv_20 <= 0.15:
        hv_score = 100
    elif hv_20 <= 0.20:
        hv_score = 85
    elif hv_20 <= 0.25:
        hv_score = 70
    elif hv_20 <= 0.30:
        hv_score = 50
    else:
        hv_score = max(0, 50 - (hv_20 - 0.30) * 100)

    # ATR adjustment
    if atr_pct <= 0.01:
        atr_multiplier = 1.1
    elif atr_pct <= 0.02:
        atr_multiplier = 1.0
    elif atr_pct <= 0.03:
        atr_multiplier = 0.9
    else:
        atr_multiplier = 0.7

    # Trend penalty (calendar spreads prefer range-bound)
    trend_penalty = 1.0 - (trend_strength * 0.3)

    # Support/Resistance proximity bonus
    sr_distance = spread.distance_from_support_resistance
    if sr_distance <= 0.01:  # Within 1% of S/R
        sr_bonus = 1.1
    elif sr_distance <= 0.02:
        sr_bonus = 1.05
    else:
        sr_bonus = 1.0

    final_score = (
        hv_score *
        atr_multiplier *
        trend_penalty *
        sr_bonus
    )

    return min(max(final_score, 0), 100)
```

## Data Requirements

### Market Data Specifications
```yaml
data_requirements:
  real_time_data:
    - stock_price:
        frequency: 1_second
        fields: [bid, ask, last, volume]
    - options_chain:
        frequency: 30_seconds
        fields: [bid, ask, last, volume, open_interest, iv, greeks]
    - market_indices:
        frequency: 5_seconds
        fields: [SPX, VIX, sector_indices]

  historical_data:
    - price_history:
        period: 2_years
        granularity: daily
    - options_history:
        period: 90_days
        granularity: end_of_day
    - volatility_history:
        period: 1_year
        granularity: daily

  derived_metrics:
    - implied_volatility:
        calculation: Black-Scholes inversion
        precision: 4_decimal_places
    - historical_volatility:
        periods: [10, 20, 30, 60]
        method: close_to_close
    - correlation_matrix:
        update_frequency: daily
        lookback: 60_days
```

### Data Quality Requirements
```python
class DataQualityValidator:
    """
    Ensure data quality for calendar spread analysis
    """

    def validate_options_data(self, option: OptionData) -> ValidationResult:
        """
        Validate options data quality
        """
        checks = []

        # Bid-Ask spread check
        spread_pct = (option.ask - option.bid) / option.mid
        checks.append(
            ValidationCheck(
                name="bid_ask_spread",
                passed=spread_pct <= 0.10,  # Max 10% spread
                message=f"Bid-ask spread: {spread_pct:.2%}"
            )
        )

        # Volume check
        checks.append(
            ValidationCheck(
                name="volume",
                passed=option.volume >= 10,
                message=f"Volume: {option.volume}"
            )
        )

        # Open interest check
        checks.append(
            ValidationCheck(
                name="open_interest",
                passed=option.open_interest >= 100,
                message=f"Open interest: {option.open_interest}"
            )
        )

        # IV sanity check
        checks.append(
            ValidationCheck(
                name="implied_volatility",
                passed=0.05 <= option.iv <= 2.00,
                message=f"IV: {option.iv:.2%}"
            )
        )

        # Greeks sanity checks
        checks.extend([
            ValidationCheck(
                name="delta",
                passed=-1.0 <= option.delta <= 1.0,
                message=f"Delta: {option.delta}"
            ),
            ValidationCheck(
                name="theta",
                passed=option.theta <= 0,  # Should be negative
                message=f"Theta: {option.theta}"
            )
        ])

        return ValidationResult(
            is_valid=all(check.passed for check in checks),
            checks=checks
        )
```

## Integration Specifications

### TradingView Integration
```python
class TradingViewIntegration:
    """
    TradingView watchlist integration specifications
    """

    API_ENDPOINT = "https://api.tradingview.com/v1"
    AUTH_METHOD = "OAuth2"
    RATE_LIMIT = 100  # requests per minute

    async def authenticate(self) -> AuthToken:
        """
        OAuth2 authentication flow
        """
        return await oauth2_client.authorize(
            client_id=self.client_id,
            client_secret=self.client_secret,
            scope=["watchlist:read", "symbol:read"],
            redirect_uri=self.redirect_uri
        )

    async def fetch_watchlists(self) -> List[Watchlist]:
        """
        Fetch user watchlists
        """
        response = await self.client.get(
            "/watchlists",
            headers={"Authorization": f"Bearer {self.token}"}
        )

        return [
            Watchlist(
                id=wl["id"],
                name=wl["name"],
                symbols=[s["symbol"] for s in wl["symbols"]],
                updated_at=parse_datetime(wl["updated_at"])
            )
            for wl in response.json()
        ]

    async def sync_symbols(self, watchlist_id: str) -> List[Symbol]:
        """
        Sync symbols from specific watchlist
        """
        response = await self.client.get(
            f"/watchlists/{watchlist_id}/symbols",
            headers={"Authorization": f"Bearer {self.token}"}
        )

        symbols = []
        for item in response.json():
            symbols.append(
                Symbol(
                    ticker=item["symbol"],
                    exchange=item["exchange"],
                    name=item["description"],
                    sector=item.get("sector"),
                    market_cap=item.get("market_cap")
                )
            )

        return symbols
```

### Broker Integration Requirements
```yaml
broker_integrations:
  interactive_brokers:
    api: TWS API v9.81+
    connection: Gateway or TWS
    features:
      - real_time_options_chains
      - greeks_calculation
      - order_execution
      - position_monitoring
    rate_limits:
      market_data: 100_req_per_second
      historical: 60_req_per_10_minutes

  td_ameritrade:
    api: TD Ameritrade API v1
    auth: OAuth2
    features:
      - options_chains
      - market_hours
      - order_placement
    rate_limits:
      per_second: 120
      per_minute: 2000

  alpaca:
    api: Alpaca Data API v2
    auth: API_KEY
    features:
      - real_time_quotes
      - options_data_beta
    rate_limits:
      per_minute: 200

  polygon_io:
    api: Polygon.io REST v2
    auth: API_KEY
    features:
      - options_snapshots
      - aggregates
      - technical_indicators
    rate_limits:
      per_minute: unlimited_paid
```

## Performance Requirements

### Response Time Requirements
```yaml
performance_metrics:
  api_response_times:
    watchlist_fetch: < 500ms
    symbol_analysis: < 1000ms
    spread_scoring: < 100ms
    pl_calculation: < 200ms
    top_spreads_query: < 300ms

  throughput:
    symbols_per_minute: >= 100
    spreads_analyzed_per_second: >= 50
    concurrent_users: >= 1000

  data_processing:
    options_chain_parse: < 50ms
    greeks_calculation: < 10ms
    monte_carlo_simulation: < 500ms (10k iterations)

  ui_performance:
    initial_load: < 2s
    dashboard_refresh: < 1s
    chart_rendering: < 300ms
```

### Scalability Requirements
```python
# Horizontal scaling configuration
SCALING_CONFIG = {
    "min_instances": 2,
    "max_instances": 20,
    "target_cpu_utilization": 70,
    "scale_up_threshold": 80,
    "scale_down_threshold": 30,
    "cool_down_period": 300,  # seconds

    "services": {
        "analysis_service": {
            "min_instances": 2,
            "max_instances": 10,
            "memory": "2Gi",
            "cpu": "1000m"
        },
        "scoring_service": {
            "min_instances": 3,
            "max_instances": 15,
            "memory": "4Gi",
            "cpu": "2000m",
            "gpu": "optional"
        },
        "calculation_service": {
            "min_instances": 2,
            "max_instances": 8,
            "memory": "1Gi",
            "cpu": "500m"
        }
    }
}
```

## Business Rules

### Entry Criteria
```python
class CalendarSpreadEntryRules:
    """
    Business rules for calendar spread entry
    """

    # Volatility rules
    MAX_IMPLIED_VOLATILITY = 0.30  # 30%
    MIN_IMPLIED_VOLATILITY = 0.10  # 10%
    MAX_IV_PERCENTILE = 30  # 30th percentile

    # Time rules
    MIN_FRONT_DTE = 25  # days
    MAX_FRONT_DTE = 45  # days
    MIN_BACK_DTE = 55   # days
    MAX_BACK_DTE = 90   # days
    MIN_DTE_DIFFERENCE = 30  # days between expirations

    # Liquidity rules
    MIN_VOLUME = 100
    MIN_OPEN_INTEREST = 500
    MAX_BID_ASK_SPREAD_PCT = 0.10  # 10%

    # Price rules
    MAX_DISTANCE_FROM_STRIKE_PCT = 0.02  # 2% from ATM
    MIN_STRIKE_PRICE = 5.00
    MAX_STRIKE_PRICE = 5000.00

    # Greeks rules
    MAX_INITIAL_DELTA = 0.15  # Near neutral
    MIN_THETA_RATIO = 1.3
    MAX_THETA_RATIO = 3.0

    # Risk rules
    MAX_POSITION_SIZE_PCT_ACCOUNT = 0.05  # 5% of account
    MAX_TOTAL_CALENDAR_ALLOCATION = 0.20  # 20% of portfolio
    MAX_CORRELATED_POSITIONS = 3  # Same sector/correlation

    def validate_entry(self, spread: CalendarSpread) -> ValidationResult:
        """
        Validate spread meets all entry criteria
        """
        violations = []

        # Check IV
        if spread.front_iv > self.MAX_IMPLIED_VOLATILITY:
            violations.append(
                f"IV too high: {spread.front_iv:.1%} > {self.MAX_IMPLIED_VOLATILITY:.1%}"
            )

        # Check DTE
        if spread.front_dte < self.MIN_FRONT_DTE:
            violations.append(
                f"Front DTE too short: {spread.front_dte} < {self.MIN_FRONT_DTE}"
            )

        # Check liquidity
        if spread.front_option.volume < self.MIN_VOLUME:
            violations.append(
                f"Insufficient volume: {spread.front_option.volume} < {self.MIN_VOLUME}"
            )

        # Check delta
        if abs(spread.net_delta) > self.MAX_INITIAL_DELTA:
            violations.append(
                f"Delta not neutral: {spread.net_delta:.3f} > {self.MAX_INITIAL_DELTA}"
            )

        return ValidationResult(
            is_valid=len(violations) == 0,
            violations=violations
        )
```

### Exit Rules
```python
class CalendarSpreadExitRules:
    """
    Business rules for calendar spread exit
    """

    # Profit targets
    PROFIT_TARGET_1 = 0.25  # 25% of max profit
    PROFIT_TARGET_2 = 0.40  # 40% of max profit
    PROFIT_TARGET_3 = 0.60  # 60% of max profit

    # Stop loss
    MAX_LOSS_PCT = 0.50  # 50% of initial debit

    # Time-based exits
    DAYS_BEFORE_FRONT_EXPIRY = 7  # Exit 1 week before
    MAX_HOLDING_PERIOD = 30  # days

    # Greek-based exits
    MAX_DELTA_THRESHOLD = 0.30  # Exit if delta exceeds
    MIN_THETA_THRESHOLD = 0.01  # Exit if theta too low

    # Volatility exits
    IV_SPIKE_THRESHOLD = 0.10  # 10% IV increase
    IV_CRASH_THRESHOLD = 0.08  # 8% IV decrease

    def check_exit_signals(
        self,
        position: CalendarPosition
    ) -> List[ExitSignal]:
        """
        Check for exit signals
        """
        signals = []

        # Check profit target
        profit_pct = position.unrealized_pnl / position.max_profit
        if profit_pct >= self.PROFIT_TARGET_1:
            signals.append(
                ExitSignal(
                    type="PROFIT_TARGET",
                    urgency="MEDIUM",
                    reason=f"Profit target reached: {profit_pct:.1%}"
                )
            )

        # Check stop loss
        loss_pct = position.unrealized_pnl / position.initial_debit
        if loss_pct <= -self.MAX_LOSS_PCT:
            signals.append(
                ExitSignal(
                    type="STOP_LOSS",
                    urgency="HIGH",
                    reason=f"Stop loss triggered: {loss_pct:.1%}"
                )
            )

        # Check time decay
        if position.days_to_front_expiry <= self.DAYS_BEFORE_FRONT_EXPIRY:
            signals.append(
                ExitSignal(
                    type="TIME_EXIT",
                    urgency="HIGH",
                    reason=f"Approaching expiration: {position.days_to_front_expiry} days"
                )
            )

        # Check delta
        if abs(position.current_delta) > self.MAX_DELTA_THRESHOLD:
            signals.append(
                ExitSignal(
                    type="DELTA_BREACH",
                    urgency="MEDIUM",
                    reason=f"Delta threshold exceeded: {position.current_delta:.3f}"
                )
            )

        return signals
```

## Error Handling

### Error Classification
```python
class ErrorTypes:
    """
    Calendar spread error classifications
    """

    # Data errors
    MISSING_MARKET_DATA = "E001"
    STALE_OPTIONS_DATA = "E002"
    INVALID_GREEK_VALUES = "E003"
    CHAIN_INCOMPLETE = "E004"

    # Calculation errors
    PRICING_MODEL_FAILURE = "E101"
    GREEKS_CALCULATION_ERROR = "E102"
    PL_CALCULATION_ERROR = "E103"
    SCORE_GENERATION_FAILURE = "E104"

    # Integration errors
    BROKER_CONNECTION_LOST = "E201"
    TRADINGVIEW_API_ERROR = "E202"
    AUTHENTICATION_FAILED = "E203"
    RATE_LIMIT_EXCEEDED = "E204"

    # Business logic errors
    INVALID_SPREAD_CONFIGURATION = "E301"
    ENTRY_CRITERIA_NOT_MET = "E302"
    POSITION_SIZE_EXCEEDED = "E303"
    INSUFFICIENT_BUYING_POWER = "E304"
```

### Error Recovery Strategies
```python
class ErrorRecovery:
    """
    Error recovery mechanisms
    """

    async def handle_data_error(self, error: DataError):
        """
        Handle data-related errors
        """
        if error.code == ErrorTypes.MISSING_MARKET_DATA:
            # Try alternate data source
            return await self.fetch_from_backup_source(error.symbol)

        elif error.code == ErrorTypes.STALE_OPTIONS_DATA:
            # Use last known good data with warning
            return await self.get_cached_data(
                error.symbol,
                max_age_minutes=15
            )

        elif error.code == ErrorTypes.INVALID_GREEK_VALUES:
            # Recalculate Greeks using different model
            return await self.calculate_greeks_fallback(error.option)

    async def handle_integration_error(self, error: IntegrationError):
        """
        Handle integration errors
        """
        if error.code == ErrorTypes.BROKER_CONNECTION_LOST:
            # Implement exponential backoff retry
            return await self.retry_with_backoff(
                error.operation,
                max_retries=5,
                initial_delay=1.0
            )

        elif error.code == ErrorTypes.RATE_LIMIT_EXCEEDED:
            # Queue request for later
            await self.queue_for_retry(
                error.request,
                delay_seconds=60
            )
```

## Testing Requirements

### Unit Testing
```python
# Test coverage requirements
TEST_COVERAGE = {
    "minimum_coverage": 85,  # percent
    "critical_paths": 95,     # percent
    "modules": {
        "calculators": 90,
        "scoring": 90,
        "analyzers": 85,
        "integrations": 80,
        "api": 85
    }
}

# Example unit tests
class TestCalendarSpreadCalculations:
    """
    Unit tests for calendar spread calculations
    """

    def test_max_loss_calculation(self):
        """
        Test maximum loss equals net debit
        """
        spread = create_test_spread(
            front_price=3.00,
            back_price=5.00
        )

        max_loss = calculator.calculate_max_loss(spread)

        assert max_loss == -2.00  # Net debit
        assert max_loss == spread.back_price - spread.front_price

    def test_theta_ratio_calculation(self):
        """
        Test theta ratio calculation
        """
        spread = create_test_spread(
            front_theta=-0.10,
            back_theta=-0.04
        )

        theta_ratio = calculator.calculate_theta_ratio(spread)

        assert theta_ratio == 2.5
        assert 1.5 <= theta_ratio <= 3.0  # Optimal range

    def test_probability_of_profit(self):
        """
        Test POP calculation consistency
        """
        spread = create_test_spread()

        pop1 = calculator.calculate_pop(spread, simulations=10000)
        pop2 = calculator.calculate_pop(spread, simulations=10000)

        # Should be consistent within 2%
        assert abs(pop1 - pop2) < 0.02
```

### Integration Testing
```yaml
integration_tests:
  tradingview_integration:
    - test_oauth_flow
    - test_watchlist_fetch
    - test_symbol_sync
    - test_rate_limiting
    - test_error_handling

  broker_integration:
    - test_connection_establishment
    - test_options_chain_fetch
    - test_real_time_updates
    - test_order_placement
    - test_position_monitoring

  end_to_end:
    - test_complete_analysis_pipeline
    - test_scoring_workflow
    - test_alert_generation
    - test_dashboard_updates
```

### Performance Testing
```python
# Performance test specifications
PERFORMANCE_TESTS = {
    "load_testing": {
        "concurrent_users": 100,
        "duration_minutes": 30,
        "ramp_up_seconds": 60,
        "scenarios": [
            "watchlist_analysis",
            "spread_scoring",
            "pl_calculation",
            "dashboard_refresh"
        ]
    },

    "stress_testing": {
        "max_concurrent_users": 1000,
        "spike_duration_seconds": 300,
        "recovery_time_target": 60
    },

    "endurance_testing": {
        "duration_hours": 24,
        "steady_state_users": 50,
        "memory_leak_threshold": 10  # percent increase
    }
}
```

### Acceptance Testing
```gherkin
Feature: Calendar Spread Analysis

  Scenario: Analyze watchlist for calendar spreads
    Given I have a watchlist with 10 symbols
    And the market is open
    When I request calendar spread analysis
    Then I should receive scored opportunities within 5 seconds
    And each opportunity should have a score between 0 and 100
    And each opportunity should include P/L calculations

  Scenario: Filter spreads by criteria
    Given I have calendar spread opportunities
    When I filter by minimum score of 70
    And maximum IV of 25%
    And front month DTE between 30-45 days
    Then I should only see spreads matching all criteria
    And results should be sorted by score descending

  Scenario: Calculate real-time P/L
    Given I have an open calendar spread position
    When the underlying price changes by 2%
    Then the P/L should update within 1 second
    And the Greeks should be recalculated
    And breakeven points should be updated
```

---
*Technical Specifications Document v1.0.0*
*Last Updated: January 2025*