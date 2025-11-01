# Prediction Markets Feature Specifications

## 1. Functional Requirements

### 1.1 Market Data Retrieval

#### Requirements
- **FR-1.1.1**: Fetch active markets from Kalshi API
- **FR-1.1.2**: Retrieve orderbook data for real-time pricing
- **FR-1.1.3**: Extract bid/ask spreads for liquidity analysis
- **FR-1.1.4**: Calculate days to market close
- **FR-1.1.5**: Enrich markets with volume and open interest data

#### Acceptance Criteria
- Successfully fetch 50+ markets per request
- Orderbook data includes best bid/ask for Yes and No
- Days to close calculated accurately from ISO timestamps
- All markets include category classification
- Rate limiting compliance (100 req/min)

### 1.2 Market Scoring

#### Requirements
- **FR-1.2.1**: Calculate liquidity score based on volume and open interest
- **FR-1.2.2**: Compute time value score based on days to close
- **FR-1.2.3**: Assess risk-reward ratio using potential returns
- **FR-1.2.4**: Evaluate bid-ask spread quality
- **FR-1.2.5**: Combine scores using weighted algorithm

#### Acceptance Criteria
- Scores range from 0-100 (integer or one decimal place)
- Liquidity score increases with volume
- Time score peaks at 7-30 day window
- Risk-reward favors asymmetric payoffs
- Spread score inversely proportional to spread width
- Final score = weighted sum of components

### 1.3 Recommendation Generation

#### Requirements
- **FR-1.3.1**: Determine position recommendation (Yes/No/Maybe/Skip)
- **FR-1.3.2**: Assess risk level (Low/Medium/High)
- **FR-1.3.3**: Calculate expected value
- **FR-1.3.4**: Generate human-readable reasoning

#### Acceptance Criteria
- Yes recommended when price <50% and score >75
- No recommended when price >50% and score >75
- Skip recommended when liquidity <40 or score <60
- Risk level based on score and liquidity
- Reasoning includes all scoring factors
- Expected value calculated from potential returns

### 1.4 User Interface Display

#### Requirements
- **FR-1.4.1**: Display summary metrics (total, high quality, avg score, showing)
- **FR-1.4.2**: Render expandable market cards with key data
- **FR-1.4.3**: Show pricing information (Yes/No prices, spread)
- **FR-1.4.4**: Display volume and liquidity metrics
- **FR-1.4.5**: Present AI analysis and recommendations
- **FR-1.4.6**: Provide action buttons (Robinhood, Kalshi links)

#### Acceptance Criteria
- Summary metrics update instantly with filters
- Cards display score with color-coded emoji
- Pricing shown as percentages (0-100%)
- Volume formatted with thousands separators
- Analysis text is clear and concise
- Links open correct market pages

### 1.5 Filtering and Search

#### Requirements
- **FR-1.5.1**: Filter by category (All, Politics, Sports, Economics, etc.)
- **FR-1.5.2**: Filter by minimum AI score (0-100)
- **FR-1.5.3**: Filter by maximum days to close (1-365)
- **FR-1.5.4**: Sort markets by score (descending)
- **FR-1.5.5**: Limit display to top 20 results

#### Acceptance Criteria
- Category filter includes all available categories
- Score filter updates results in real-time
- Days filter excludes markets beyond threshold
- Markets sorted highest score first
- Top 20 displayed (performance optimization)

### 1.6 Caching and Performance

#### Requirements
- **FR-1.6.1**: Cache market data for 1 hour
- **FR-1.6.2**: Manual refresh capability
- **FR-1.6.3**: Fast filter updates (use cached data)
- **FR-1.6.4**: Rate limit compliance
- **FR-1.6.5**: Graceful error handling

#### Acceptance Criteria
- Cache TTL = 3600 seconds (1 hour)
- Refresh button clears cache and refetches
- Filter changes don't trigger API calls
- API calls stay under 100/minute
- Errors display user-friendly messages

## 2. UI Components and Layout

### 2.1 Page Structure

```
┌─────────────────────────────────────────────────────────────┐
│                    Navigation Sidebar                       │
├─────────────────────────────────────────────────────────────┤
│                   Page Title & Caption                      │
│         "Prediction Markets - AI-powered opportunities"     │
├─────────────────────────────────────────────────────────────┤
│                    Filter Controls (4 cols)                 │
│  Category Dropdown | Min Score | Max Days | Refresh Button │
├─────────────────────────────────────────────────────────────┤
│                  Summary Metrics (4 cols)                   │
│  Total Markets | High Quality >75 | Avg Score | Showing    │
├─────────────────────────────────────────────────────────────┤
│                   Market Cards (expandable)                 │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ Score: 94 🔥 | Politics | 5d | Market Title         │  │
│  │  (Expanded Content)                                  │  │
│  │  - Pricing (3 cols)                                  │  │
│  │  - Volume & Liquidity (3 cols)                       │  │
│  │  - Recommendation (3 cols)                           │  │
│  │  - AI Analysis                                       │  │
│  │  - Expected Value                                    │  │
│  │  - Action Buttons                                    │  │
│  │  - Market Details                                    │  │
│  └─────────────────────────────────────────────────────┘  │
│  (Up to 20 cards displayed)                                │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Component Specifications

#### 2.2.1 Page Header
- **Title**: "🎲 Prediction Markets"
- **Caption**: "AI-powered event contract opportunities from Kalshi"
- **Styling**: Streamlit default title and caption styles

#### 2.2.2 Filter Controls
**Layout**: 4 columns (2:1:1:1 ratio)

**Column 1 - Category Filter:**
- Type: Selectbox
- Options: ["All", "Politics", "Sports", "Economics", "Crypto", "Companies", "Tech", "Climate", "World"]
- Default: "All"
- Index: 0

**Column 2 - Min Score Filter:**
- Type: Number input
- Range: 0-100
- Default: 60
- Step: 5
- Label: "Min Score"

**Column 3 - Max Days Filter:**
- Type: Number input
- Range: 1-365
- Default: 90
- Step: 1
- Label: "Max Days"

**Column 4 - Refresh Button:**
- Type: Button
- Label: "🔄 Refresh"
- Style: Primary
- Action: Clear cache and rerun

#### 2.2.3 Summary Metrics
**Layout**: 4 equal columns

**Metric 1 - Total Markets:**
- Label: "Total Markets"
- Value: Count of all fetched markets
- Format: Integer

**Metric 2 - High Quality:**
- Label: "High Quality (>75)"
- Value: Count of markets with score ≥75
- Format: Integer

**Metric 3 - Average Score:**
- Label: "Avg Score"
- Value: Mean score of filtered markets
- Format: "XX.X" or "N/A" if empty

**Metric 4 - Showing:**
- Label: "Showing"
- Value: Count of displayed markets (after filters)
- Format: Integer

#### 2.2.4 Market Card (Collapsed)
**Header Format:**
```
{emoji} Score: {score:.0f} {quality_emoji} | {category} | {days}d | {title}
```

**Emoji Mapping:**
- Score ≥85: 🔥 (Fire) + 🟢 (Green)
- Score ≥75: ⭐ (Star) + 🟢 (Green)
- Score ≥60: 👍 (Thumbs Up) + 🟡 (Yellow)
- Score <60: 👎 (Thumbs Down) + 🔴 (Red)

**Example:**
```
🟢 Score: 94 🔥 | Politics | 5d | Presidential Election 2024
```

#### 2.2.5 Market Card (Expanded)

**Section 1: Pricing (3 columns)**

*Column 1: Yes Price*
- Label: "📊 Pricing"
- Metric: "Yes Price"
- Value: "{yes_price:.1%}" (e.g., "65.0%")
- Format: Percentage with 1 decimal

*Column 2: No Price*
- Metric: "No Price"
- Value: "{no_price:.1%}"
- Format: Percentage with 1 decimal

*Column 3: (Empty)*

**Section 2: Volume & Liquidity (3 columns)**

*Column 1: 24h Volume*
- Label: "💹 Volume & Liquidity"
- Metric: "24h Volume"
- Value: "{volume_24h:,} contracts"
- Format: Thousands separator

*Column 2: Spread*
- Metric: "Spread"
- Value: "{bid_ask_spread:.1%}"
- Format: Percentage with 1 decimal

*Column 3: (Empty)*

**Section 3: Recommendation (3 columns)**

*Column 1: Position*
- Label: "🎯 Recommendation"
- Metric: "Position"
- Value: recommendation (Yes/No/Maybe/Skip)
- Format: String

*Column 2: Risk Level*
- Metric: "Risk Level"
- Value: risk_level (Low/Medium/High)
- Format: String

*Column 3: (Empty)*

**Section 4: AI Analysis**
- Label: "🤖 Analysis:"
- Content: ai_reasoning text
- Format: Paragraph

**Section 5: Expected Value**
- Type: Success alert (if EV >0) or Warning alert (if EV ≤0)
- Success: "💰 Expected Value: +{expected_value:.1f}%"
- Warning: "Expected value is near zero or negative"

**Section 6: Action Buttons (2 columns)**

*Column 1: Robinhood Link*
- Type: Link button
- Label: "📱 View on Robinhood"
- URL: "https://robinhood.com/markets/events/{ticker}"
- Width: Full container

*Column 2: Kalshi Link*
- Type: Link button
- Label: "📈 View on Kalshi"
- URL: "https://kalshi.com/markets/{ticker}"
- Width: Full container

**Section 7: Market Details (expandable)**
- Type: Nested expander
- Label: "📋 Market Details"
- Content:
  - Ticker (code block)
  - Category
  - Days to Close
  - Close Date (if available)
  - Description (if available)

#### 2.2.6 Empty State
**Displayed when no markets match filters:**
- Type: Info alert
- Message: "No markets found with score >= {min_score} and <= {max_days} days to close."

**Displayed when API fails:**
- Type: Warning alert
- Message: "No markets found. Kalshi API may be unavailable or rate-limited."
- Additional Info: "💡 Try again in a few moments. Kalshi allows 100 requests per minute."

## 3. Data Models

### 3.1 Raw Market Data (from Kalshi API)

```python
@dataclass
class KalshiMarket:
    ticker: str                    # e.g., "PRES-2024-DEM"
    title: str                     # Market title
    category: str                  # "Politics", "Sports", etc.
    subcategory: Optional[str]     # Subcategory classification
    status: str                    # "active", "closed", "settled"
    open_time: str                 # ISO timestamp
    close_time: str                # ISO timestamp
    volume_24h: int                # 24-hour volume
    open_interest: int             # Total open contracts
    subtitle: Optional[str]        # Market description
```

### 3.2 Enriched Market Data

```python
@dataclass
class EnrichedMarket:
    # Base fields
    ticker: str
    title: str
    category: str
    subcategory: str
    description: str
    market_status: str

    # Pricing
    yes_price: Optional[float]     # Mid price (0-1)
    no_price: Optional[float]      # 1 - yes_price
    yes_bid: Optional[float]       # Best Yes bid
    yes_ask: Optional[float]       # Best Yes ask
    no_bid: Optional[float]        # Best No bid
    no_ask: Optional[float]        # Best No ask
    bid_ask_spread: Optional[float] # abs(yes_ask - yes_bid)

    # Volume & Liquidity
    volume_24h: int                # Trading volume
    open_interest: int             # Open contracts

    # Timing
    open_date: str                 # ISO timestamp
    close_date: str                # ISO timestamp
    days_to_close: Optional[int]   # Calculated days

    # Metadata
    last_updated: str              # ISO timestamp
```

### 3.3 Analyzed Market Data

```python
@dataclass
class AnalyzedMarket:
    # Inherits all EnrichedMarket fields
    # Plus analysis results:

    ai_score: float                # 0-100 overall score
    ai_reasoning: str              # Human-readable explanation
    recommended_position: str      # Yes/No/Maybe/Skip
    risk_level: str                # Low/Medium/High
    expected_value: float          # Expected value percentage

    # Component scores (internal)
    _liquidity_score: float        # 0-100
    _time_score: float             # 0-100
    _risk_reward_score: float      # 0-100
    _spread_score: float           # 0-100
```

### 3.4 Orderbook Data

```python
@dataclass
class Orderbook:
    yes: List[Tuple[int, int]]     # [(price_cents, size), ...]
    no: List[Tuple[int, int]]      # [(price_cents, size), ...]

    # Example:
    # yes: [(65, 100), (64, 50)]  # $0.65 for 100, $0.64 for 50
    # no: [(35, 100), (36, 50)]   # $0.35 for 100, $0.36 for 50
```

## 4. Business Logic

### 4.1 Score Calculation Formulas

#### 4.1.1 Liquidity Score

```python
def calculate_liquidity_score(volume_24h: int, open_interest: int) -> float:
    """
    Score based on trading activity
    Formula: liquidity_metric = (volume_24h * 2) + open_interest
    """
    liquidity_metric = (volume_24h * 2) + open_interest

    if liquidity_metric <= 0:
        return 0
    elif liquidity_metric < 100:
        return 20
    elif liquidity_metric < 1000:
        return 40
    elif liquidity_metric < 10000:
        return 60
    elif liquidity_metric < 100000:
        return 80
    else:
        return 100
```

**Rationale:**
- Volume weighted 2x (more important than static OI)
- Logarithmic scale (each 10x increase = +20 points)
- Reflects difficulty of entering/exiting positions

#### 4.1.2 Time Score

```python
def calculate_time_score(days_to_close: int) -> float:
    """
    Score based on time until market closes
    Sweet spot: 7-30 days
    """
    if days_to_close <= 0:
        return 0
    elif days_to_close < 3:
        return 40   # Too soon - high risk
    elif days_to_close <= 7:
        return 80   # Good - near term clarity
    elif days_to_close <= 30:
        return 100  # Optimal - balance of time and certainty
    elif days_to_close <= 90:
        return 70   # Okay - longer uncertainty
    else:
        return 40   # Too far - low predictability
```

**Rationale:**
- Near-term events (7-30 days) most predictable
- Very short (<3 days) = high volatility risk
- Long-term (>90 days) = too much uncertainty
- Balances opportunity window and information availability

#### 4.1.3 Risk-Reward Score

```python
def calculate_risk_reward_score(yes_price: float, no_price: float) -> float:
    """
    Score based on potential return vs risk
    Formula: max_return = max((1-yes)/yes, (1-no)/no)
    """
    if not yes_price or not no_price:
        return 0

    yes_potential_return = (1 - yes_price) / yes_price if yes_price > 0 else 0
    no_potential_return = (1 - no_price) / no_price if no_price > 0 else 0

    max_return = max(yes_potential_return, no_potential_return)

    if max_return < 0.2:    # <20% return
        return 30
    elif max_return < 0.5:  # 20-50% return
        return 50
    elif max_return < 1.0:  # 50-100% return
        return 70
    elif max_return < 2.0:  # 100-200% return
        return 85
    else:                   # >200% return
        return 100
```

**Rationale:**
- Asymmetric payoffs score higher
- Favors underdog pricing (high return potential)
- Reflects risk-reward fundamental to prediction markets

#### 4.1.4 Spread Score

```python
def calculate_spread_score(bid_ask_spread: float) -> float:
    """
    Score based on bid-ask spread tightness
    Formula: tighter spread = higher score
    """
    if bid_ask_spread is None:
        return 50  # Neutral if unknown

    # Spread is in decimal (0.01 = 1%)
    if bid_ask_spread <= 0.01:    # ≤1%
        return 100
    elif bid_ask_spread <= 0.02:  # 1-2%
        return 85
    elif bid_ask_spread <= 0.05:  # 2-5%
        return 70
    elif bid_ask_spread <= 0.10:  # 5-10%
        return 50
    else:                         # >10%
        return 30
```

**Rationale:**
- Spread represents transaction cost
- Tighter spreads = more liquid markets
- High spreads erode profit potential

#### 4.1.5 Overall Score

```python
def calculate_overall_score(liquidity_score: float,
                           time_score: float,
                           risk_reward_score: float,
                           spread_score: float) -> float:
    """
    Weighted combination of component scores
    """
    weights = {
        'liquidity': 0.30,      # 30%
        'time_value': 0.25,     # 25%
        'risk_reward': 0.25,    # 25%
        'spread': 0.20          # 20%
    }

    total_score = (
        liquidity_score * weights['liquidity'] +
        time_score * weights['time_value'] +
        risk_reward_score * weights['risk_reward'] +
        spread_score * weights['spread']
    )

    return round(total_score, 1)  # One decimal place
```

**Weight Rationale:**
- Liquidity (30%): Most critical for trade execution
- Time Value (25%): Affects predictability and urgency
- Risk-Reward (25%): Core investment metric
- Spread (20%): Important but less than liquidity

### 4.2 Recommendation Logic

```python
def generate_recommendation(score: float,
                           yes_price: float,
                           liquidity_score: float) -> Tuple[str, str]:
    """
    Determine position and risk level
    Returns: (recommended_position, risk_level)
    """
    # Skip low liquidity markets (hard to trade)
    if liquidity_score < 40:
        return ('Skip', 'High')

    # High score markets
    if score >= 75:
        # Determine Yes or No based on pricing
        if yes_price and yes_price < 0.50:
            position = 'Yes'  # Underpriced Yes
        else:
            position = 'No'   # Overpriced Yes = buy No

        # Risk level based on score
        if score >= 85:
            risk = 'Low'      # Exceptional opportunity
        else:
            risk = 'Medium'   # Good opportunity

        return (position, risk)

    # Moderate score markets
    elif score >= 60:
        return ('Maybe', 'Medium')

    # Low score markets
    else:
        return ('Skip', 'High')
```

**Decision Tree:**
```
Is liquidity_score >= 40?
    No  → Skip (High risk)
    Yes → Continue

Is score >= 75?
    Yes → Is yes_price < 0.50?
              Yes → Buy Yes (Low/Medium risk)
              No  → Buy No (Low/Medium risk)
    No  → Is score >= 60?
              Yes → Maybe (Medium risk)
              No  → Skip (High risk)
```

### 4.3 Expected Value Calculation

```python
def calculate_expected_value(yes_price: float) -> float:
    """
    Simple EV calculation assuming efficient markets
    Returns: Expected value as percentage
    """
    if not yes_price:
        return 0

    # EV for buying Yes
    ev_yes = (1 * yes_price) - yes_price  # = 0 in efficient market

    # EV for buying No
    ev_no = (1 * (1 - yes_price)) - (1 - yes_price)  # = 0

    # Return better EV as percentage
    return round(max(ev_yes, ev_no) * 100, 2)
```

**Note:** In efficient markets, EV ≈ 0. Non-zero values suggest potential mispricing, but this is a simplified model that doesn't account for:
- Market inefficiencies
- Information asymmetry
- Transaction costs
- True probability vs market price

### 4.4 Reasoning Generation Logic

```python
def generate_reasoning(liquidity_score: float,
                      time_score: float,
                      risk_reward_score: float,
                      spread_score: float,
                      yes_price: float,
                      volume_24h: int,
                      days_to_close: int) -> str:
    """
    Generate human-readable explanation
    Returns: Concatenated reasoning string
    """
    reasons = []

    # Liquidity analysis
    if liquidity_score >= 80:
        reasons.append("Excellent liquidity with high volume")
    elif liquidity_score >= 60:
        reasons.append("Good liquidity")
    elif liquidity_score >= 40:
        reasons.append("Moderate liquidity")
    else:
        reasons.append("Low liquidity - difficult to trade")

    # Time analysis
    if time_score >= 80:
        reasons.append(f"Optimal {days_to_close}-day timeframe")
    elif time_score >= 60:
        reasons.append(f"Reasonable {days_to_close}-day window")
    else:
        reasons.append(f"Suboptimal {days_to_close}-day timeframe")

    # Risk-reward analysis
    if risk_reward_score >= 80:
        reasons.append("Strong risk-reward ratio")
    elif risk_reward_score >= 60:
        reasons.append("Acceptable risk-reward")
    else:
        reasons.append("Limited upside potential")

    # Spread analysis
    if spread_score >= 80:
        reasons.append("Tight bid-ask spread")
    elif spread_score < 50:
        reasons.append("Wide spread increases costs")

    # Price analysis
    if yes_price:
        if yes_price <= 0.30:
            reasons.append(f"Yes priced low at {yes_price:.0%} (high upside if correct)")
        elif yes_price >= 0.70:
            reasons.append(f"Yes priced high at {yes_price:.0%} (safer but lower return)")

    return ". ".join(reasons) + "."
```

**Example Output:**
```
"Excellent liquidity with high volume. Optimal 14-day timeframe. Strong risk-reward ratio. Tight bid-ask spread. Yes priced low at 35% (high upside if correct)."
```

## 5. Edge Cases and Error Handling

### 5.1 Data Validation

#### Missing Pricing Data
- **Scenario**: Orderbook is empty or invalid
- **Handling**: Set ai_score = 0, recommended_position = 'Skip'
- **Implementation**:
```python
if not yes_price or not yes_bid or not yes_ask:
    return {
        'ai_score': 0,
        'ai_reasoning': 'Insufficient pricing data',
        'recommended_position': 'Skip',
        'risk_level': 'Unknown',
        'expected_value': 0
    }
```

#### Invalid Date Format
- **Scenario**: close_date is malformed or missing
- **Handling**: Set days_to_close = None, skip time score
- **Implementation**:
```python
try:
    close_dt = datetime.fromisoformat(close_date.replace('Z', '+00:00'))
    days_to_close = max(0, (close_dt - datetime.now()).days)
except:
    days_to_close = None
```

#### Negative or Zero Prices
- **Scenario**: Price data is corrupted
- **Handling**: Treat as missing data, skip market
- **Implementation**:
```python
if yes_price <= 0 or yes_price >= 1:
    return None  # Invalid market
```

### 5.2 API Failures

#### Kalshi Connection Timeout
- **Scenario**: API request times out
- **Handling**: Return empty list, show warning to user
- **Implementation**:
```python
try:
    response = self.session.get(url, timeout=30)
    response.raise_for_status()
except requests.exceptions.RequestException as e:
    print(f"Error fetching markets: {e}")
    return []
```

#### Rate Limit Exceeded
- **Scenario**: Too many requests in short time
- **Handling**: Display rate limit message, suggest waiting
- **Implementation**:
```python
if not markets:
    st.warning("No markets found. Kalshi API may be unavailable or rate-limited.")
    st.info("💡 Try again in a few moments. Kalshi allows 100 requests per minute.")
```

#### HTTP Error Codes
- **Scenario**: 4xx or 5xx response
- **Handling**: Log error, return empty list
- **Implementation**:
```python
response.raise_for_status()  # Raises HTTPError for bad status
```

### 5.3 Calculation Edge Cases

#### Division by Zero
- **Scenario**: yes_price = 0 in return calculation
- **Handling**: Check before division, return 0
- **Implementation**:
```python
yes_potential_return = (1 - yes_price) / yes_price if yes_price > 0 else 0
```

#### Market Already Closed
- **Scenario**: days_to_close < 0
- **Handling**: Filter out negative days
- **Implementation**:
```python
filtered_markets = [
    m for m in markets
    if m.get('days_to_close', 0) > 0
]
```

#### Extremely Wide Spreads
- **Scenario**: spread > 1.0 (100%)
- **Handling**: Cap score at minimum (30)
- **Implementation**:
```python
else:  # >10% spread
    return 30
```

### 5.4 UI Edge Cases

#### No Markets Match Filters
- **Scenario**: All markets filtered out
- **Handling**: Display helpful message
- **Implementation**:
```python
if not filtered_markets:
    st.info(f"No markets found with score >= {min_score} and <= {max_days} days to close.")
    return
```

#### Empty Category
- **Scenario**: Category has no active markets
- **Handling**: Return empty list, show info message
- **Implementation**:
```python
filtered = [m for m in all_markets if m.get('category') == category]
if not filtered:
    st.info(f"No active markets in {category} category")
```

#### Very Long Market Titles
- **Scenario**: Title exceeds reasonable length
- **Handling**: Streamlit handles wrapping automatically
- **Implementation**: No special handling needed

## 6. Performance Requirements

### Response Times
- Initial page load: < 40 seconds (50 markets with enrichment)
- Cached page load: < 2 seconds
- Filter update: < 1 second
- Card expand/collapse: < 100ms
- Refresh action: < 40 seconds

### Scalability
- Support fetching 50-200 markets
- Handle 10+ categories
- Process 1000+ contracts volume
- Manage 1-hour cache window

### Resource Usage
- Memory: < 200MB per session
- CPU: < 30% during enrichment, <5% idle
- Network: ~50 API calls per refresh (markets + orderbooks)
- Cache storage: ~1MB per hour

## 7. Testing Specifications

### Unit Tests

#### Scoring Algorithms
```python
def test_liquidity_score():
    assert calculate_liquidity_score(50000, 10000) == 80
    assert calculate_liquidity_score(0, 0) == 0
    assert calculate_liquidity_score(500, 100) == 40

def test_time_score():
    assert calculate_time_score(14) == 100
    assert calculate_time_score(2) == 40
    assert calculate_time_score(100) == 70

def test_risk_reward_score():
    assert calculate_risk_reward_score(0.25, 0.75) == 100  # 300% return
    assert calculate_risk_reward_score(0.50, 0.50) == 70   # 100% return

def test_spread_score():
    assert calculate_spread_score(0.005) == 100
    assert calculate_spread_score(0.15) == 30
```

#### Recommendation Logic
```python
def test_recommendation():
    pos, risk = generate_recommendation(85, 0.40, 80)
    assert pos == 'Yes'
    assert risk == 'Low'

    pos, risk = generate_recommendation(50, 0.60, 80)
    assert pos == 'Skip'
    assert risk == 'High'
```

#### Edge Cases
```python
def test_missing_data():
    result = analyze_market({'ticker': 'TEST'})
    assert result['ai_score'] == 0
    assert result['recommended_position'] == 'Skip'

def test_negative_days():
    enriched = enrich_market({'close_date': '2020-01-01'})
    assert enriched['days_to_close'] == 0
```

### Integration Tests

#### Kalshi API Integration
```python
def test_fetch_markets():
    kalshi = KalshiIntegration()
    markets = kalshi.get_markets(limit=10)
    assert len(markets) > 0
    assert 'ticker' in markets[0]

def test_orderbook_fetch():
    kalshi = KalshiIntegration()
    orderbook = kalshi.get_orderbook('PRES-2024')
    assert 'yes' in orderbook
    assert 'no' in orderbook
```

#### Cache Functionality
```python
def test_cache_hit():
    # First call
    markets1 = fetch_and_score_markets(kalshi, analyzer, 'All', 50)
    # Second call (cached)
    markets2 = fetch_and_score_markets(kalshi, analyzer, 'All', 50)
    assert markets1 == markets2  # Same data

def test_cache_clear():
    st.cache_data.clear()
    # Should fetch fresh data
```

### E2E Tests

#### Full Page Load
```python
def test_page_load():
    # Navigate to prediction markets
    # Assert page title displayed
    # Assert filters rendered
    # Assert markets displayed
    # Assert no errors
```

#### Filter Interactions
```python
def test_category_filter():
    # Select "Politics"
    # Assert only politics markets shown
    # Assert summary metrics updated

def test_score_filter():
    # Set min score to 75
    # Assert all displayed markets >= 75
    # Assert filtered count correct
```

#### Refresh Functionality
```python
def test_refresh_button():
    # Click refresh
    # Assert cache cleared
    # Assert new data fetched
    # Assert UI updated
```

### Performance Tests

#### Load Testing
```python
def test_50_markets_load_time():
    start = time.time()
    markets = fetch_and_score_markets(kalshi, analyzer, 'All', 50)
    duration = time.time() - start
    assert duration < 45  # Should complete in <45 seconds

def test_cache_performance():
    # First call (cache miss)
    start1 = time.time()
    fetch_and_score_markets(kalshi, analyzer, 'All', 50)
    duration1 = time.time() - start1

    # Second call (cache hit)
    start2 = time.time()
    fetch_and_score_markets(kalshi, analyzer, 'All', 50)
    duration2 = time.time() - start2

    assert duration2 < 2  # Cached call <2 seconds
    assert duration2 < duration1 / 10  # 10x faster
```

#### Rate Limit Compliance
```python
def test_rate_limiting():
    kalshi = KalshiIntegration()
    start = time.time()
    kalshi.get_enriched_markets(limit=100)
    duration = time.time() - start

    # Should take >60 seconds for 100 markets (rate limit)
    assert duration > 60
```

## 8. Security and Compliance

### Data Privacy
- No personal user data stored
- No authentication required for public markets
- No trading credentials handled
- All data from public Kalshi API

### API Security
- HTTPS only (no HTTP)
- No API key exposure (public endpoints)
- Rate limiting compliance
- No sensitive data in logs

### Input Validation
- All user inputs via Streamlit widgets (built-in validation)
- No SQL injection risk (no database queries)
- No XSS risk (Streamlit sanitizes output)
- Type-safe conversions

### Regulatory Compliance
- Display-only feature (no trading execution)
- Markets regulated by CFTC
- Platform links to licensed exchanges
- No financial advice provided

## 9. Deployment Checklist

### Pre-Deployment
- [ ] All unit tests passing
- [ ] Integration tests passing
- [ ] E2E tests passing
- [ ] Performance tests meeting requirements
- [ ] Documentation complete
- [ ] Code reviewed

### Deployment
- [ ] Deploy to production environment
- [ ] Verify Kalshi API connectivity
- [ ] Test rate limiting compliance
- [ ] Validate caching working correctly
- [ ] Monitor error logs
- [ ] Check page load times

### Post-Deployment
- [ ] User acceptance testing
- [ ] Monitor API usage
- [ ] Track performance metrics
- [ ] Collect user feedback
- [ ] Plan iterative improvements

## 10. Success Metrics

### Performance Metrics
- Page load time < 40s (initial)
- Page load time < 2s (cached)
- API success rate > 99%
- Rate limit violations = 0

### User Engagement
- Markets viewed per session
- Filter usage frequency
- Category distribution
- Card expansion rate
- External link clicks

### Data Quality
- Markets with valid scores > 90%
- Average score accuracy (validated against outcomes)
- Recommendation effectiveness
- User satisfaction ratings
