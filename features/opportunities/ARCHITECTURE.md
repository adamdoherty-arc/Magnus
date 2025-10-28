# Opportunities Feature - Technical Architecture

## Table of Contents
1. [System Overview](#system-overview)
2. [Component Architecture](#component-architecture)
3. [Data Flow](#data-flow)
4. [Core Algorithms](#core-algorithms)
5. [Integration Points](#integration-points)
6. [Performance Optimization](#performance-optimization)
7. [Error Handling](#error-handling)
8. [Security Considerations](#security-considerations)
9. [Scalability Design](#scalability-design)
10. [Future Architecture](#future-architecture)

## System Overview

### Architectural Philosophy

The Opportunities feature is designed as a modular, event-driven system that processes market data through a pipeline of analyzers to identify optimal trading opportunities. The architecture emphasizes:

1. **Separation of Concerns**: Clear boundaries between data fetching, analysis, and presentation
2. **Scalability**: Ability to process hundreds of symbols efficiently
3. **Reliability**: Graceful handling of API limits and failures
4. **Extensibility**: Easy addition of new opportunity types and analysis methods

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface Layer                     │
│                   (dashboard.py: 1122-1292)                 │
└─────────────────┬───────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────┐
│                    Orchestration Layer                       │
│                  Strategy Selection & Filters                │
└─────────────────┬───────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────┐
│                     Analysis Engine                          │
│               (src/premium_scanner.py: 9-203)               │
└─────┬───────────────────────────────────────────────┬───────┘
      │                                               │
┌─────▼──────────────┐                   ┌───────────▼────────┐
│  Data Providers    │                   │   Calculation      │
│  - Yahoo Finance   │                   │   - Greeks         │
│  - Robinhood       │                   │   - Returns        │
│  - TradingView     │                   │   - Risk Metrics   │
└────────────────────┘                   └────────────────────┘
```

### Component Responsibilities

1. **UI Layer**: User interaction, parameter collection, result display
2. **Orchestration**: Strategy routing, filter application, scan coordination
3. **Analysis Engine**: Core opportunity identification and ranking logic
4. **Data Providers**: Market data fetching and normalization
5. **Calculation Engine**: Mathematical computations for metrics

## Component Architecture

### 1. Premium Scanner (Core Engine)

**Location**: `src/premium_scanner.py`

**Class Structure**:
```python
class PremiumScanner:
    def __init__(self):
        self.min_volume = 100      # Liquidity threshold
        self.min_oi = 50           # Open interest threshold

    def scan_premiums(self, symbols, max_price, min_premium_pct, dte)
    def scan_all_stocks_under(self, max_price)
    def find_assignment_candidates(self, positions)
```

**Key Responsibilities**:
- Symbol iteration and parallel processing
- Options chain analysis
- Opportunity scoring and ranking
- Filter application

**Design Patterns**:
- **Iterator Pattern**: For processing symbol lists
- **Strategy Pattern**: For different scanning strategies
- **Pipeline Pattern**: For data transformation

### 2. TradingView Integration

**Location**: `src/tradingview_watchlist.py`

**Class Structure**:
```python
class TradingViewWatchlist:
    def __init__(self):
        self.username = os.getenv('TRADINGVIEW_USERNAME')
        self.password = os.getenv('TRADINGVIEW_PASSWORD')
        self.max_price = float(os.getenv('MAX_STOCK_PRICE', '50'))

    def get_watchlist_symbols_simple(self)
    def get_comprehensive_premiums(self, symbols, max_price)
    def get_best_premiums(self, symbols)
    def get_watchlist_analysis(self)
```

**Integration Points**:
- Environment variable configuration
- Web scraping capabilities (when credentials available)
- Fallback to curated lists

### 3. Enhanced Options Fetcher

**Location**: `src/enhanced_options_fetcher.py`

**Class Structure**:
```python
class EnhancedOptionsFetcher:
    def __init__(self):
        self.logged_in = False
        self.risk_free_rate = 0.045

    def login_robinhood(self)
    def calculate_delta(self, S, K, T, r, sigma, option_type)
    def get_all_expirations_data(self, symbol, target_dtes)
```

**Greek Calculations**:
- Black-Scholes delta computation
- Time decay analysis
- Volatility surface mapping

### 4. User Interface Components

**Location**: `dashboard.py` (lines 1122-1292)

**UI Structure**:
```python
# Page routing
if page == "Premium Scanner":
    # Configuration columns
    col1, col2 = st.columns([1, 2])

    # Scanner controls
    - Strategy selection
    - Parameter inputs
    - Scan button

    # Results display
    - Summary metrics
    - Sortable table
    - Detailed expandable views
```

**State Management**:
```python
st.session_state['scan_results'] = results
st.session_state['last_scan_time'] = datetime.now()
```

## Data Flow

### 1. Scan Initiation Flow

```
User Input → UI Validation → Parameter Assembly → Scanner Invocation
    ↓            ↓                ↓                      ↓
Strategy    Range Check    Config Object       scan_premiums()
Selection   Enforcement    Creation            Method Call
```

### 2. Symbol Processing Pipeline

```
Symbol List → Price Filter → Options Chain Fetch → Expiration Selection
     ↓             ↓                ↓                      ↓
Watchlist     Current Price    API Call           Find Nearest DTE
or Manual     Validation       to Provider        to Target
```

### 3. Opportunity Analysis Flow

```
Raw Options Data → Liquidity Filter → Premium Calculation → Return Metrics
        ↓                ↓                   ↓                    ↓
   Puts Only      Volume & OI Check    Bid/Ask Midpoint    Monthly/Annual
   Extraction     Thresholds           Computation          Extrapolation
```

### 4. Results Aggregation

```
Individual Opportunities → Sorting → Filtering → Presentation
           ↓                  ↓          ↓            ↓
    Dict Creation      By Return    By Strategy   DataFrame
    per Symbol         Metrics      Requirements   Display
```

## Core Algorithms

### 1. Premium Calculation Algorithm

```python
def calculate_premium_metrics(put_option, strike, dte):
    """
    Core algorithm for premium opportunity scoring
    """
    # 1. Extract market data
    bid = put_option['bid']
    ask = put_option['ask']

    # 2. Calculate mid-price premium
    premium = (bid + ask) / 2 if bid > 0 and ask > 0 else bid

    # 3. Calculate premium percentage
    premium_pct = (premium / strike) * 100

    # 4. Annualize returns
    if dte > 0:
        monthly_return = (premium_pct / dte) * 30
        annual_return = monthly_return * 12
    else:
        monthly_return = annual_return = 0

    return {
        'premium': premium * 100,  # Per contract
        'premium_pct': premium_pct,
        'monthly_return': monthly_return,
        'annual_return': annual_return
    }
```

**Time Complexity**: O(1) per option
**Space Complexity**: O(1) per option

### 2. Optimal Strike Selection

```python
def find_optimal_strike(puts_chain, current_price, target_otm=0.95):
    """
    Algorithm to find the optimal strike price
    Target: 5% out-of-the-money by default
    """
    # 1. Calculate target strike
    target_strike = current_price * target_otm

    # 2. Filter valid strikes
    valid_strikes = puts_chain[
        (puts_chain['strike'] <= target_strike) &
        (puts_chain['strike'] >= current_price * 0.85)  # Max 15% OTM
    ]

    # 3. Score each strike
    scores = []
    for strike in valid_strikes:
        premium_score = calculate_premium_score(strike)
        liquidity_score = calculate_liquidity_score(strike)
        risk_score = calculate_risk_score(strike, current_price)

        total_score = (
            premium_score * 0.5 +
            liquidity_score * 0.3 +
            risk_score * 0.2
        )
        scores.append((strike, total_score))

    # 4. Return highest scoring strike
    return max(scores, key=lambda x: x[1])
```

**Time Complexity**: O(n) where n = number of strikes
**Space Complexity**: O(n) for score storage

### 3. Delta Calculation (Black-Scholes)

```python
def calculate_delta(S, K, T, r, sigma, option_type='put'):
    """
    Black-Scholes delta calculation for option Greeks

    Parameters:
    S: Spot price
    K: Strike price
    T: Time to expiration (years)
    r: Risk-free rate
    sigma: Implied volatility
    """
    # 1. Validate inputs
    if T <= 0 or sigma <= 0 or S <= 0 or K <= 0:
        return 0.0

    # 2. Calculate d1
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))

    # 3. Calculate delta based on option type
    if option_type == 'put':
        delta = norm.cdf(d1) - 1  # Put delta is negative
    else:
        delta = norm.cdf(d1)      # Call delta is positive

    return round(delta, 4)
```

**Mathematical Foundation**:
- Uses cumulative normal distribution
- Assumes log-normal price distribution
- Risk-neutral valuation framework

### 4. Liquidity Scoring Algorithm

```python
def calculate_liquidity_score(option_data):
    """
    Multi-factor liquidity scoring
    """
    volume = option_data.get('volume', 0)
    open_interest = option_data.get('openInterest', 0)
    bid_ask_spread = option_data.get('ask', 0) - option_data.get('bid', 0)

    # Volume score (0-40 points)
    volume_score = min(40, volume / 10) if volume > 0 else 0

    # Open interest score (0-40 points)
    oi_score = min(40, open_interest / 5) if open_interest > 0 else 0

    # Spread score (0-20 points)
    if bid_ask_spread > 0 and option_data.get('ask', 0) > 0:
        spread_pct = bid_ask_spread / option_data['ask']
        spread_score = max(0, 20 - (spread_pct * 100))
    else:
        spread_score = 0

    return volume_score + oi_score + spread_score
```

**Score Interpretation**:
- 80-100: Excellent liquidity
- 60-79: Good liquidity
- 40-59: Acceptable liquidity
- <40: Poor liquidity (filter out)

### 5. Multi-Expiration Comparison

```python
def compare_expirations(symbol, target_dtes=[7, 14, 21, 30, 45]):
    """
    Algorithm to find best opportunity across multiple expirations
    """
    opportunities = []

    for target_dte in target_dtes:
        # 1. Find closest actual expiration
        actual_expiry = find_closest_expiration(symbol, target_dte)

        # 2. Get options chain
        chain = fetch_options_chain(symbol, actual_expiry)

        # 3. Calculate efficiency score
        for strike in chain:
            efficiency = calculate_capital_efficiency(strike, target_dte)
            opportunities.append({
                'dte': target_dte,
                'strike': strike,
                'efficiency': efficiency,
                'score': efficiency * time_decay_factor(target_dte)
            })

    # 4. Return sorted by score
    return sorted(opportunities, key=lambda x: x['score'], reverse=True)
```

## Integration Points

### 1. Market Data Integration

**Yahoo Finance API**:
```python
# Connection pattern
ticker = yf.Ticker(symbol)
info = ticker.info
options_chain = ticker.option_chain(expiry_date)
```

**Rate Limiting Strategy**:
- Batch requests where possible
- Implement exponential backoff
- Cache responses for 15 minutes

### 2. Robinhood Integration

**Authentication Flow**:
```python
# Singleton pattern for connection
if not self.logged_in:
    rh.authentication.login(
        username=username,
        password=password,
        expiresIn=86400,
        store_session=True
    )
    self.logged_in = True
```

**Data Fetching**:
- Options chains with Greeks
- Real-time quotes
- Position data for assignment analysis

### 3. Session State Management

**Streamlit Session State**:
```python
# Results caching
st.session_state['scan_results'] = results
st.session_state['last_scan_time'] = datetime.now()

# Connection status
st.session_state['rh_connected'] = login_status
```

### 4. Environment Configuration

**Required Variables**:
```bash
ROBINHOOD_USERNAME=your_username
ROBINHOOD_PASSWORD=your_password
TRADINGVIEW_USERNAME=tv_username  # Optional
TRADINGVIEW_PASSWORD=tv_password  # Optional
MAX_STOCK_PRICE=50                # Default max price
```

## Performance Optimization

### 1. Parallel Processing Strategy

**Current Implementation**:
- Sequential symbol processing
- Blocking I/O for API calls

**Optimization Opportunities**:
```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def parallel_scan(symbols, max_workers=10):
    opportunities = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_symbol = {
            executor.submit(scan_single_symbol, symbol): symbol
            for symbol in symbols
        }

        for future in as_completed(future_to_symbol):
            try:
                result = future.result(timeout=30)
                if result:
                    opportunities.extend(result)
            except Exception as e:
                logger.error(f"Error scanning {future_to_symbol[future]}: {e}")

    return opportunities
```

### 2. Caching Strategy

**Multi-Level Cache**:
```python
class OpportunityCache:
    def __init__(self):
        self.memory_cache = {}  # In-memory cache
        self.redis_client = redis.Redis()  # Distributed cache

    def get_cached_opportunity(self, symbol, expiry):
        cache_key = f"{symbol}:{expiry}"

        # Check memory cache first
        if cache_key in self.memory_cache:
            if not self.is_expired(self.memory_cache[cache_key]):
                return self.memory_cache[cache_key]

        # Check Redis cache
        cached = self.redis_client.get(cache_key)
        if cached:
            return json.loads(cached)

        return None
```

**Cache Invalidation**:
- Market hours: 5-minute TTL
- After hours: 1-hour TTL
- Earnings/events: Immediate invalidation

### 3. Query Optimization

**Batch Processing**:
```python
def batch_fetch_quotes(symbols, batch_size=50):
    """
    Fetch quotes in batches to reduce API calls
    """
    results = {}

    for i in range(0, len(symbols), batch_size):
        batch = symbols[i:i + batch_size]
        # Single API call for multiple symbols
        batch_quotes = yf.download(batch, period='1d', interval='1m')
        results.update(process_batch_quotes(batch_quotes))

    return results
```

### 4. Database Optimization

**Indexed Queries**:
```sql
-- Create indexes for frequent queries
CREATE INDEX idx_opportunities_return ON opportunities(monthly_return DESC);
CREATE INDEX idx_opportunities_symbol ON opportunities(symbol);
CREATE INDEX idx_opportunities_expiry ON opportunities(expiry_date);

-- Composite index for complex queries
CREATE INDEX idx_opp_symbol_expiry_return
ON opportunities(symbol, expiry_date, monthly_return DESC);
```

## Error Handling

### 1. API Failure Handling

```python
def resilient_api_call(func, max_retries=3, backoff_factor=2):
    """
    Resilient API calling with exponential backoff
    """
    for attempt in range(max_retries):
        try:
            return func()
        except RateLimitError as e:
            wait_time = backoff_factor ** attempt
            logger.warning(f"Rate limited, waiting {wait_time}s")
            time.sleep(wait_time)
        except NetworkError as e:
            if attempt == max_retries - 1:
                logger.error(f"API call failed after {max_retries} attempts")
                raise
            time.sleep(1)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise

    return None
```

### 2. Data Validation

```python
def validate_opportunity(opportunity):
    """
    Comprehensive opportunity validation
    """
    required_fields = ['symbol', 'strike', 'premium', 'dte']

    # Check required fields
    for field in required_fields:
        if field not in opportunity:
            raise ValueError(f"Missing required field: {field}")

    # Validate data ranges
    if opportunity['premium'] <= 0:
        raise ValueError("Premium must be positive")

    if opportunity['dte'] <= 0:
        raise ValueError("Days to expiry must be positive")

    if opportunity['strike'] <= 0:
        raise ValueError("Strike price must be positive")

    # Validate calculated metrics
    if opportunity.get('annual_return', 0) > 500:
        logger.warning(f"Suspicious return for {opportunity['symbol']}: {opportunity['annual_return']}%")

    return True
```

### 3. Graceful Degradation

```python
class OpportunityScanner:
    def scan_with_fallback(self, primary_source='robinhood'):
        """
        Fallback to alternative data sources
        """
        try:
            # Try primary source
            if primary_source == 'robinhood':
                return self.scan_robinhood()
        except Exception as e:
            logger.warning(f"Primary source failed: {e}")

        try:
            # Fallback to Yahoo Finance
            return self.scan_yahoo_finance()
        except Exception as e:
            logger.warning(f"Secondary source failed: {e}")

        # Final fallback to cached data
        return self.get_cached_opportunities()
```

## Security Considerations

### 1. Credential Management

**Secure Storage**:
```python
# Never hardcode credentials
# Use environment variables or secure vault
class SecureCredentials:
    def __init__(self):
        self.vault = hvac.Client()  # HashiCorp Vault

    def get_credential(self, key):
        # Retrieve from secure vault
        return self.vault.read(f'secret/trading/{key}')

    def rotate_credentials(self):
        # Automatic credential rotation
        pass
```

### 2. API Key Protection

**Rate Limiting**:
```python
class RateLimiter:
    def __init__(self, max_calls=100, window=60):
        self.max_calls = max_calls
        self.window = window
        self.calls = deque()

    def allow_request(self):
        now = time.time()
        # Remove old calls outside window
        while self.calls and self.calls[0] < now - self.window:
            self.calls.popleft()

        if len(self.calls) < self.max_calls:
            self.calls.append(now)
            return True
        return False
```

### 3. Data Sanitization

```python
def sanitize_user_input(input_data):
    """
    Sanitize user inputs to prevent injection attacks
    """
    # Remove special characters
    sanitized = re.sub(r'[^\w\s\-.]', '', str(input_data))

    # Validate against whitelist
    if not is_valid_symbol(sanitized):
        raise ValueError(f"Invalid symbol: {sanitized}")

    return sanitized.upper()
```

## Scalability Design

### 1. Horizontal Scaling

**Microservices Architecture**:
```yaml
# docker-compose.yml for scaling
version: '3.8'
services:
  scanner:
    image: opportunity-scanner
    deploy:
      replicas: 5
    environment:
      - REDIS_URL=redis://cache:6379

  cache:
    image: redis:alpine
    ports:
      - "6379:6379"

  load_balancer:
    image: nginx
    ports:
      - "80:80"
    depends_on:
      - scanner
```

### 2. Queue-Based Processing

```python
from celery import Celery

app = Celery('opportunity_scanner', broker='redis://localhost:6379')

@app.task
def scan_symbol_async(symbol, parameters):
    """
    Asynchronous symbol scanning
    """
    scanner = PremiumScanner()
    return scanner.scan_single_symbol(symbol, **parameters)

def distributed_scan(symbols, parameters):
    """
    Distribute scanning across workers
    """
    jobs = []
    for symbol in symbols:
        job = scan_symbol_async.delay(symbol, parameters)
        jobs.append(job)

    # Collect results
    results = []
    for job in jobs:
        results.extend(job.get(timeout=30))

    return results
```

### 3. Database Sharding

```python
class ShardedOpportunityDB:
    def __init__(self, num_shards=4):
        self.shards = [
            create_db_connection(f"shard_{i}")
            for i in range(num_shards)
        ]

    def get_shard(self, symbol):
        """
        Determine shard based on symbol hash
        """
        shard_id = hash(symbol) % len(self.shards)
        return self.shards[shard_id]

    def store_opportunity(self, opportunity):
        shard = self.get_shard(opportunity['symbol'])
        shard.insert(opportunity)
```

## Future Architecture

### 1. Machine Learning Pipeline

```python
class MLOpportunityScorer:
    def __init__(self):
        self.model = self.load_model('opportunity_scorer_v2.pkl')
        self.feature_pipeline = self.create_feature_pipeline()

    def score_opportunity(self, opportunity):
        # Extract features
        features = self.feature_pipeline.transform(opportunity)

        # Predict success probability
        success_prob = self.model.predict_proba(features)[0][1]

        # Adjust traditional score with ML insights
        traditional_score = calculate_traditional_score(opportunity)
        ml_adjusted_score = traditional_score * (0.7 + 0.3 * success_prob)

        return ml_adjusted_score
```

### 2. Real-Time Streaming

```python
class StreamingOpportunityScanner:
    def __init__(self):
        self.kafka_consumer = KafkaConsumer('market-data')
        self.opportunity_stream = []

    async def process_stream(self):
        async for message in self.kafka_consumer:
            market_data = json.loads(message.value)

            # Real-time opportunity detection
            if self.is_opportunity(market_data):
                opportunity = self.create_opportunity(market_data)
                await self.broadcast_opportunity(opportunity)
```

### 3. GraphQL API Layer

```graphql
type Query {
  opportunities(
    symbols: [String]
    maxPrice: Float
    minPremium: Float
    strategies: [Strategy]
    limit: Int
    offset: Int
  ): OpportunityConnection!

  opportunity(symbol: String!, expiry: String!): Opportunity
}

type Opportunity {
  symbol: String!
  currentPrice: Float!
  strike: Float!
  expiry: String!
  premium: Float!
  metrics: OpportunityMetrics!
  rankings: OpportunityRankings!
}

type OpportunityMetrics {
  premiumPercent: Float!
  monthlyReturn: Float!
  annualReturn: Float!
  impliedVolatility: Float!
  delta: Float
  gamma: Float
  theta: Float
  vega: Float
}
```

### 4. Event-Driven Architecture

```python
class OpportunityEventBus:
    def __init__(self):
        self.subscribers = defaultdict(list)

    def publish(self, event_type, opportunity):
        """
        Publish opportunity events
        """
        event = {
            'type': event_type,
            'timestamp': datetime.now(),
            'opportunity': opportunity
        }

        for subscriber in self.subscribers[event_type]:
            subscriber.handle_event(event)

    def subscribe(self, event_type, handler):
        self.subscribers[event_type].append(handler)

# Event handlers
class AlertHandler:
    def handle_event(self, event):
        if event['opportunity']['monthly_return'] > 3:
            send_alert(event['opportunity'])

class DatabaseHandler:
    def handle_event(self, event):
        store_opportunity(event['opportunity'])
```

## Performance Metrics

### Key Performance Indicators

1. **Scan Latency**: Time to complete full market scan
   - Target: <30 seconds for 100 symbols
   - Current: ~45 seconds

2. **Opportunity Quality**: Percentage of profitable recommendations
   - Target: >70% success rate
   - Measurement: Track actual vs predicted returns

3. **System Throughput**: Opportunities analyzed per second
   - Target: 10 symbols/second
   - Current: ~2 symbols/second

4. **Cache Hit Rate**: Percentage of requests served from cache
   - Target: >80% during market hours
   - Current: ~60%

### Monitoring Dashboard

```python
class OpportunityMetrics:
    def __init__(self):
        self.prometheus_client = PrometheusClient()

    def record_scan_latency(self, duration):
        self.prometheus_client.histogram(
            'opportunity_scan_duration_seconds',
            duration,
            labels={'scanner': 'premium'}
        )

    def record_opportunity_found(self, opportunity):
        self.prometheus_client.counter(
            'opportunities_found_total',
            labels={
                'symbol': opportunity['symbol'],
                'strategy': opportunity['strategy']
            }
        )
```

## Conclusion

The Opportunities feature architecture is designed to be robust, scalable, and maintainable. Key architectural principles:

1. **Modularity**: Clear component boundaries enable independent development
2. **Resilience**: Multiple fallback mechanisms ensure continuous operation
3. **Performance**: Optimization strategies for sub-second response times
4. **Extensibility**: Easy addition of new strategies and data sources
5. **Observability**: Comprehensive monitoring and logging

The system processes market data through a sophisticated pipeline that identifies, analyzes, and ranks trading opportunities, providing users with actionable insights for their wheel strategy implementation.