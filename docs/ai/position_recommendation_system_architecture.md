# AI-Powered Position Recommendation System Architecture

## System Overview

A comprehensive AI-driven recommendation engine that provides actionable insights for every options position in the portfolio, leveraging LLM reasoning combined with quantitative analysis.

## Architecture Components

### 1. Data Layer

#### Position Data Aggregator
**Location**: `src/ai/position_data_aggregator.py`

**Responsibilities**:
- Fetch position data from Robinhood API
- Enrich with market data (yfinance, Polygon)
- Calculate Greeks using mibian (delta, gamma, theta, vega)
- Compute position health metrics
- Cache aggregated data (5-minute TTL)

**Data Schema**:
```python
@dataclass
class EnrichedPosition:
    # Basic position data
    symbol: str
    position_type: str  # 'CSP', 'CC', 'Long Call', 'Long Put'
    strike: float
    expiration: date
    dte: int
    quantity: int

    # Financial metrics
    premium_collected: float
    current_value: float
    pnl_dollar: float
    pnl_percent: float

    # Market data
    stock_price: float
    stock_price_ah: Optional[float]
    stock_change_percent: float

    # Greeks (estimated or calculated)
    delta: float
    gamma: float
    theta: float
    vega: float
    implied_volatility: float

    # Moneyness metrics
    moneyness: str  # 'ITM', 'ATM', 'OTM'
    distance_to_strike: float  # percentage
    probability_itm: float  # 0-100

    # Volatility metrics
    iv_rank: Optional[float]
    iv_percentile: Optional[float]

    # Technical indicators
    stock_rsi: Optional[float]
    stock_trend: Optional[str]  # 'bullish', 'bearish', 'neutral'
    support_level: Optional[float]
    resistance_level: Optional[float]

    # News sentiment
    news_sentiment: Optional[float]  # -1 to 1
    news_count_24h: int

    # Timestamp
    analyzed_at: datetime
```

#### Market Context Provider
**Location**: `src/ai/market_context_provider.py`

**Responsibilities**:
- Fetch real-time market conditions (VIX, SPY, sector performance)
- Get stock-specific news and sentiment
- Calculate technical indicators
- Provide earnings calendar data
- Detect unusual options activity

**Key Functions**:
- `get_market_regime()` → 'bull', 'bear', 'volatile', 'range-bound'
- `get_stock_context(symbol)` → dict with news, sentiment, technicals
- `get_earnings_proximity(symbol)` → days until next earnings

---

### 2. Analysis Layer

#### Quantitative Analyzer
**Location**: `src/ai/position_quantitative_analyzer.py`

**Responsibilities**:
- Calculate position risk metrics
- Compute profit targets and stop losses
- Analyze probability of profit (POP)
- Evaluate theta decay efficiency
- Assess assignment risk

**Key Metrics**:
```python
@dataclass
class QuantitativeAnalysis:
    # Risk metrics
    max_loss: float
    max_profit: float
    risk_reward_ratio: float
    probability_profit: float
    expected_value: float

    # Greeks analysis
    theta_efficiency: float  # daily theta / capital at risk
    gamma_risk_level: str  # 'low', 'medium', 'high'
    vega_exposure: float  # sensitivity to IV changes

    # Position health
    breakeven_price: float
    breakeven_distance_pct: float
    days_to_profitable_decay: int

    # Actionability
    optimal_exit_price: float
    stop_loss_price: float
    roll_threshold_dte: int
```

**Rule-Based Triggers**:
- **Close Now**: P/L > 50% of max profit, DTE < 21, IV rank < 25
- **Roll Out**: DTE < 7, position ITM, theta decay slowing
- **Add Hedge**: Position ITM, high gamma risk, earnings within 7 days
- **Cut Loss**: P/L < -100%, DTE > 30, adverse technical setup

#### LLM Recommendation Engine
**Location**: `src/ai/position_llm_analyzer.py`

**Responsibilities**:
- Generate contextual recommendations using LLMs
- Provide natural language reasoning
- Consider qualitative factors (news, sentiment, market regime)
- Synthesize quantitative + qualitative analysis

**Model Selection Strategy**:
```python
ANALYSIS_TIERS = {
    'critical': {  # Losing positions, high risk
        'model': 'claude',  # Claude 3.5 Sonnet for reasoning
        'temperature': 0.3,
        'max_tokens': 800
    },
    'standard': {  # Routine analysis
        'model': 'gemini',  # Gemini for cost efficiency
        'temperature': 0.4,
        'max_tokens': 500
    },
    'bulk': {  # Batch processing
        'model': 'llama3',  # Local model for zero cost
        'temperature': 0.5,
        'max_tokens': 400
    }
}
```

**Prompt Engineering**:
```python
def build_position_analysis_prompt(
    position: EnrichedPosition,
    quant_analysis: QuantitativeAnalysis,
    market_context: dict
) -> str:
    """
    Build structured prompt for position analysis
    """

    prompt = f"""You are an expert options trading advisor analyzing a specific position.

=== POSITION DETAILS ===
Symbol: {position.symbol}
Type: {position.position_type}
Strike: ${position.strike}
Expiration: {position.expiration} ({position.dte} DTE)
Quantity: {position.quantity}

Current Stock Price: ${position.stock_price}
After-Hours Price: ${position.stock_price_ah or 'N/A'}

=== FINANCIAL PERFORMANCE ===
Premium Collected/Paid: ${position.premium_collected}
Current Value: ${position.current_value}
P/L: ${position.pnl_dollar} ({position.pnl_percent:+.1f}%)

=== GREEKS & RISK METRICS ===
Delta: {position.delta:.2f}
Theta: {position.theta:.2f} (Daily decay: ${abs(position.theta * position.quantity * 100):.2f})
IV: {position.implied_volatility:.1f}%
Moneyness: {position.moneyness}

Probability ITM: {position.probability_itm:.1f}%
Max Profit: ${quant_analysis.max_profit}
Max Loss: ${quant_analysis.max_loss}
Probability of Profit: {quant_analysis.probability_profit:.1f}%

=== MARKET CONTEXT ===
Market Regime: {market_context.get('regime', 'N/A')}
Stock Trend: {position.stock_trend or 'N/A'}
News Sentiment (24h): {position.news_sentiment or 'N/A'}
Key News: {market_context.get('top_headline', 'None')}

VIX Level: {market_context.get('vix', 'N/A')}
Earnings in {market_context.get('earnings_days', '?')} days

=== QUANTITATIVE RECOMMENDATION ===
Rule-Based Signal: {quant_analysis.recommended_action}
Reasoning: {quant_analysis.reasoning}

=== YOUR TASK ===
Analyze this position holistically and provide a recommendation. Consider:

1. **P/L Status**: Is this a winning or losing position? How does that affect strategy?
2. **Time Decay**: Is theta working for or against us? Is there enough time for our thesis to play out?
3. **Moneyness & Assignment Risk**: How close are we to the strike? What's the risk of early assignment?
4. **Market Environment**: Does the current market regime support this position?
5. **News & Catalysts**: Are there upcoming events that could impact this?
6. **Optimal Action**: Should we hold, close, roll, adjust, or hedge?

Respond in this EXACT JSON format:
{{
  "recommendation": "hold" | "close_now" | "roll_out" | "roll_strike" | "add_hedge" | "cut_loss",
  "confidence": 0-100,
  "rationale": "2-3 sentence explanation of your recommendation",
  "key_factors": [
    "Most important factor 1",
    "Most important factor 2",
    "Most important factor 3"
  ],
  "risk_level": "low" | "medium" | "high",
  "action_details": {{
    "target_exit_price": 123.45,  // if closing
    "roll_to_date": "2025-12-20",  // if rolling
    "hedge_suggestion": "Buy 1 protective put at $X strike"  // if hedging
  }},
  "urgency": "low" | "medium" | "high",
  "expected_outcome": "Brief description of what you expect to happen"
}}

IMPORTANT:
- Be specific and actionable
- Consider the trader's risk profile (moderate risk tolerance)
- Explain WHY this action is best RIGHT NOW
- Account for transaction costs (rolling/closing costs ~$0.65 per contract)
- Respond ONLY with valid JSON
"""

    return prompt
```

---

### 3. Recommendation Synthesis Layer

#### Recommendation Aggregator
**Location**: `src/ai/position_recommendation_aggregator.py`

**Responsibilities**:
- Combine quantitative + LLM analysis
- Apply portfolio-level constraints
- Rank recommendations by urgency
- Generate action plan

**Decision Logic**:
```python
def synthesize_recommendation(
    quant_rec: dict,
    llm_rec: dict,
    position: EnrichedPosition
) -> FinalRecommendation:
    """
    Combine rule-based and AI recommendations

    Strategy:
    - If both agree → high confidence
    - If disagree → favor quantitative for risk management
    - If LLM confidence < 60% → use quantitative only
    - If critical position (big loss) → always use LLM
    """

    # Resolve conflicts
    if quant_rec['action'] == llm_rec['recommendation']:
        final_action = quant_rec['action']
        confidence = min(95, (quant_rec['confidence'] + llm_rec['confidence']) / 2)
    else:
        # Conflict resolution rules
        if position.pnl_dollar < -500:  # Big loss
            final_action = llm_rec['recommendation']
            confidence = llm_rec['confidence'] * 0.9
        elif llm_rec['confidence'] < 60:
            final_action = quant_rec['action']
            confidence = quant_rec['confidence']
        else:
            final_action = llm_rec['recommendation']
            confidence = (quant_rec['confidence'] * 0.4 + llm_rec['confidence'] * 0.6)

    return FinalRecommendation(
        action=final_action,
        confidence=confidence,
        rationale=llm_rec.get('rationale', quant_rec['reasoning']),
        key_factors=llm_rec.get('key_factors', []),
        risk_level=max(quant_rec['risk_level'], llm_rec['risk_level']),
        urgency=determine_urgency(position, final_action),
        action_details=llm_rec.get('action_details', {}),
        quant_signal=quant_rec['action'],
        llm_signal=llm_rec['recommendation']
    )
```

---

### 4. Caching & Performance Layer

#### Redis Cache Strategy
**Location**: `src/ai/recommendation_cache.py`

**Cache Structure**:
```python
CACHE_KEYS = {
    'position_data': 'pos:{symbol}:{strike}:{exp}',  # TTL: 5 min
    'market_context': 'market:{symbol}',  # TTL: 10 min
    'llm_recommendation': 'llm:{position_id}:{hash}',  # TTL: 30 min
    'quant_analysis': 'quant:{position_id}',  # TTL: 5 min
}

# Intelligent invalidation
def invalidate_on_events(event_type: str, symbol: str):
    """
    Invalidate cache on significant events
    - Stock price move > 3%
    - News alert published
    - Market hours transition
    - VIX spike > 10%
    """
```

**Cost Optimization**:
- Cache LLM responses for 30 minutes (avoid re-analyzing same position)
- Use hash of (position_data + market_context) as cache key
- Implement tiered refresh: critical positions (5 min), stable positions (30 min)

---

### 5. API Integration Layer

#### Market Data Service
**Location**: `src/ai/market_data_service.py`

**APIs Used**:

1. **yfinance** (Primary - Free)
   - Stock prices (real-time, 15-min delay)
   - Historical data for technical indicators
   - Basic options data
   ```python
   import yfinance as yf

   def get_stock_data(symbol: str):
       ticker = yf.Ticker(symbol)
       info = ticker.info
       hist = ticker.history(period='1mo', interval='1d')
       return {
           'price': info.get('currentPrice'),
           'change_pct': info.get('regularMarketChangePercent'),
           'volume': info.get('volume'),
           'avg_volume': info.get('averageVolume'),
           'hist': hist
       }
   ```

2. **Polygon.io** (Options Greeks - Paid)
   - Real-time IV and Greeks
   - Unusual options activity
   ```python
   from polygon import RESTClient

   def get_options_greeks(symbol: str, strike: float, exp: str):
       client = RESTClient(api_key=os.getenv('POLYGON_API_KEY'))
       contract = f"O:{symbol}{exp}{strike}"
       snapshot = client.get_snapshot_option(contract)
       return {
           'delta': snapshot.greeks.delta,
           'theta': snapshot.greeks.theta,
           'iv': snapshot.implied_volatility
       }
   ```

3. **Finnhub** (News & Sentiment - Freemium)
   - Company news (last 24 hours)
   - Sentiment scores
   ```python
   import finnhub

   def get_news_sentiment(symbol: str):
       client = finnhub.Client(api_key=os.getenv('FINNHUB_API_KEY'))
       news = client.company_news(symbol,
                                   _from=(datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
                                   to=datetime.now().strftime('%Y-%m-%d'))
       sentiment = sum(article.get('sentiment', 0) for article in news) / len(news) if news else 0
       return {
           'articles': news[:5],
           'avg_sentiment': sentiment,
           'count': len(news)
       }
   ```

4. **Alpha Vantage** (Earnings Calendar - Free)
   - Upcoming earnings dates
   ```python
   import requests

   def get_earnings_date(symbol: str):
       url = f"https://www.alphavantage.co/query?function=EARNINGS_CALENDAR&symbol={symbol}&apikey={API_KEY}"
       response = requests.get(url)
       # Parse CSV response
       return next_earnings_date
   ```

5. **mibian** (Local Greeks Calculation - Free)
   - Fallback for when Polygon is unavailable
   ```python
   import mibian

   def calculate_greeks_mibian(
       stock_price: float,
       strike: float,
       dte: int,
       iv: float,
       option_type: str
   ):
       if option_type in ['call', 'CC', 'Long Call']:
           bs = mibian.BS([stock_price, strike, 0.5, dte], volatility=iv*100)
           return {
               'delta': bs.callDelta / 100,
               'theta': bs.callTheta,
               'gamma': bs.gamma,
               'vega': bs.vega
           }
       else:
           bs = mibian.BS([stock_price, strike, 0.5, dte], volatility=iv*100)
           return {
               'delta': bs.putDelta / 100,
               'theta': bs.putTheta,
               'gamma': bs.gamma,
               'vega': bs.vega
           }
   ```

---

## Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER OPENS POSITIONS PAGE                     │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│           Position Data Aggregator (src/ai/)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Robinhood API│  │   yfinance   │  │  Polygon.io  │         │
│  │  Positions   │  │ Stock Prices │  │    Greeks    │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
│         └───────────────┬──┴────────────────┘                   │
│                         │ Cache (Redis 5min)                    │
│                         ▼                                        │
│              EnrichedPosition Objects                            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                ┌────────────┴─────────────┐
                │                          │
                ▼                          ▼
┌───────────────────────────┐  ┌───────────────────────────┐
│  Market Context Provider  │  │ Quantitative Analyzer     │
│  - News (Finnhub)         │  │ - Risk metrics            │
│  - Sentiment              │  │ - Greeks analysis         │
│  - Technical indicators   │  │ - POP calculation         │
│  - VIX, Market regime     │  │ - Rule-based signals      │
└─────────────┬─────────────┘  └─────────────┬─────────────┘
              │                               │
              │         Cache 10min           │  Cache 5min
              └────────────┬──────────────────┘
                           │
                           ▼
              ┌────────────────────────────┐
              │   LLM Recommendation       │
              │   Engine                   │
              │  - Prompt builder          │
              │  - Model selection         │
              │  - Response parser         │
              │                            │
              │  Cache: 30min (hash-based) │
              └─────────────┬──────────────┘
                            │
                            ▼
              ┌────────────────────────────┐
              │ Recommendation Aggregator  │
              │ - Synthesize quant + LLM   │
              │ - Resolve conflicts        │
              │ - Rank by urgency          │
              └─────────────┬──────────────┘
                            │
                            ▼
              ┌────────────────────────────┐
              │   UI Renderer              │
              │   (Streamlit Components)   │
              │   - Badge indicators       │
              │   - Expandable cards       │
              │   - Action buttons         │
              └────────────────────────────┘
```

---

## UI Design Specifications

### Component Layout

**Position Card with AI Recommendations**:

```
┌─────────────────────────────────────────────────────────────┐
│ AAPL  $150 Put (CSP)  Exp: 2025-12-20  (40 DTE)        ⚡💡│
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Stock: $165.50 (+2.3%)     P/L: +$125 (+35%)    🟢         │
│  Strike: $150.00            Moneyness: OTM                   │
│  Delta: -0.15   Theta: +$2.50/day                          │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 🤖 AI RECOMMENDATION: HOLD                      85% │  │
│  │                                                      │  │
│  │ Rationale: Position is profitable with 40 DTE       │  │
│  │ remaining. Theta decay is working in your favor     │  │
│  │ ($2.50/day). Stock is 10% above strike with low     │  │
│  │ probability of assignment. Consider closing at 50%   │  │
│  │ profit target (~$178).                               │  │
│  │                                                      │  │
│  │ Key Factors:                                         │  │
│  │  • Strong bullish momentum (RSI: 62)                │  │
│  │  • Low IV environment (IV Rank: 18)                 │  │
│  │  • No earnings until 45 days out                    │  │
│  │                                                      │  │
│  │ Risk Level: LOW     Urgency: LOW                    │  │
│  │                                                      │  │
│  │ [View Details ▼]                                     │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  [📊 Chart] [📰 News] [🔄 Roll] [💰 Close]                  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Badge System

**Quick Visual Indicators**:
```python
BADGES = {
    'recommendation': {
        'hold': {'emoji': '✋', 'color': 'blue'},
        'close_now': {'emoji': '💰', 'color': 'green'},
        'roll_out': {'emoji': '🔄', 'color': 'orange'},
        'cut_loss': {'emoji': '✂️', 'color': 'red'},
        'add_hedge': {'emoji': '🛡️', 'color': 'yellow'},
    },
    'urgency': {
        'low': {'emoji': '🐢', 'color': 'gray'},
        'medium': {'emoji': '⚡', 'color': 'orange'},
        'high': {'emoji': '🚨', 'color': 'red'},
    },
    'confidence': {
        'high': {'emoji': '💎', 'color': 'green'},  # >80%
        'medium': {'emoji': '💡', 'color': 'blue'},  # 60-80%
        'low': {'emoji': '🤔', 'color': 'gray'},  # <60%
    }
}
```

### Streamlit Implementation

**File**: `src/components/ai_recommendation_card.py`

```python
import streamlit as st
from datetime import datetime

def render_ai_recommendation_card(
    position: dict,
    recommendation: dict,
    expanded: bool = False
):
    """
    Render AI recommendation card for a position
    """

    # Determine badge colors
    rec_action = recommendation['action']
    confidence = recommendation['confidence']
    urgency = recommendation['urgency']

    # Confidence badge
    if confidence >= 80:
        conf_badge = "💎 High"
        conf_color = "green"
    elif confidence >= 60:
        conf_badge = "💡 Medium"
        conf_color = "blue"
    else:
        conf_badge = "🤔 Low"
        conf_color = "gray"

    # Urgency badge
    urgency_badges = {
        'low': '🐢 Monitor',
        'medium': '⚡ Review Soon',
        'high': '🚨 Act Now'
    }

    # Action badge
    action_badges = {
        'hold': '✋ Hold',
        'close_now': '💰 Close',
        'roll_out': '🔄 Roll',
        'roll_strike': '↕️ Adjust',
        'add_hedge': '🛡️ Hedge',
        'cut_loss': '✂️ Cut Loss'
    }

    with st.container():
        col1, col2, col3 = st.columns([3, 1, 1])

        with col1:
            st.markdown(f"### 🤖 AI Recommendation: **{action_badges.get(rec_action, rec_action.upper())}**")

        with col2:
            st.metric("Confidence", f"{confidence}%")

        with col3:
            st.markdown(f"**{urgency_badges.get(urgency, urgency)}**")

        # Rationale
        st.markdown(f"**Rationale**: {recommendation['rationale']}")

        # Expandable details
        with st.expander("📊 View Full Analysis", expanded=expanded):
            st.markdown("**Key Factors:**")
            for factor in recommendation.get('key_factors', []):
                st.markdown(f"- {factor}")

            # Quantitative metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Risk Level", recommendation['risk_level'].upper())
            with col2:
                st.metric("Expected Return", f"{recommendation.get('expected_return', 0):.1f}%")
            with col3:
                st.metric("Days to Target", recommendation.get('days_to_target', 'N/A'))

            # Action details
            if recommendation.get('action_details'):
                st.markdown("**Action Details:**")
                details = recommendation['action_details']

                if 'target_exit_price' in details:
                    st.markdown(f"- Target Exit Price: ${details['target_exit_price']:.2f}")

                if 'roll_to_date' in details:
                    st.markdown(f"- Roll to Date: {details['roll_to_date']}")

                if 'hedge_suggestion' in details:
                    st.markdown(f"- Hedge: {details['hedge_suggestion']}")

            # Model transparency
            st.caption(
                f"Analysis by {recommendation.get('model_used', 'AI')} | "
                f"Quant Signal: {recommendation.get('quant_signal', 'N/A')} | "
                f"Generated: {recommendation.get('timestamp', datetime.now()).strftime('%Y-%m-%d %H:%M')}"
            )

        # Action buttons
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("📊 View Chart", key=f"chart_{position['symbol']}"):
                st.session_state[f'show_chart_{position["symbol"]}'] = True

        with col2:
            if st.button("📰 Latest News", key=f"news_{position['symbol']}"):
                st.session_state[f'show_news_{position["symbol"]}'] = True

        with col3:
            if rec_action in ['roll_out', 'roll_strike']:
                if st.button("🔄 Execute Roll", key=f"roll_{position['symbol']}", type="primary"):
                    # Execute roll logic
                    st.info("Roll functionality coming soon")

        with col4:
            if rec_action == 'close_now':
                if st.button("💰 Close Position", key=f"close_{position['symbol']}", type="primary"):
                    st.warning("Close order would be placed here")
```

---

## Implementation Priority & Phases

### Phase 1: Core Infrastructure (Week 1)
1. ✅ `position_data_aggregator.py` - Fetch and enrich position data
2. ✅ `market_context_provider.py` - Market data integration
3. ✅ `position_quantitative_analyzer.py` - Rule-based analysis
4. ✅ `recommendation_cache.py` - Redis caching layer

### Phase 2: AI Integration (Week 2)
5. ✅ `position_llm_analyzer.py` - LLM recommendation engine
6. ✅ `position_recommendation_aggregator.py` - Synthesis logic
7. ✅ Update `cost_tracker.py` to track position analysis costs

### Phase 3: UI Components (Week 3)
8. ✅ `ai_recommendation_card.py` - Streamlit component
9. ✅ Update `positions_page_improved.py` - Integrate recommendations
10. ✅ Add batch analysis mode for portfolio-wide recommendations

### Phase 4: Optimization & Features (Week 4)
11. ✅ Implement intelligent cache invalidation
12. ✅ Add "What-If" scenario analysis
13. ✅ Build recommendation history tracking
14. ✅ Add email/Telegram alerts for high-urgency recommendations

---

## Cost Analysis & Budget

### Estimated Costs (per position analysis):

| Model | Tokens (In/Out) | Cost per Analysis | Best Use Case |
|-------|----------------|-------------------|---------------|
| Claude 3.5 Sonnet | 2000/500 | $0.0135 | Critical positions, big losses |
| Gemini 2.5 Flash | 2000/500 | $0.0018 | Standard analysis |
| Llama3 (Local) | 2000/500 | $0.0000 | Bulk processing, stable positions |

### Daily Cost Projection (25 positions, 3 refreshes/day):

- **All Claude**: 25 × 3 × $0.0135 = **$1.01/day** → $30/month
- **Mixed Strategy**:
  - 5 critical (Claude) + 10 standard (Gemini) + 10 bulk (Llama3)
  - (5×3×$0.0135) + (10×3×$0.0018) + (10×3×$0) = **$0.25/day** → $7.50/month
- **Cache-Optimized** (30-min cache hit rate 70%):
  - $7.50 × 0.30 = **$2.25/month**

**Recommended**: Mixed strategy with aggressive caching = **<$5/month**

---

## Configuration

### Add to `config/services.yaml`:

```yaml
ai_recommendations:
  # Model selection strategy
  model_strategy: 'tiered'  # 'tiered', 'single', 'ensemble'

  models:
    critical: 'claude'  # For losing positions
    standard: 'gemini'  # For routine analysis
    bulk: 'llama3'     # For stable positions

  # Caching
  cache_ttl:
    position_data: 300      # 5 minutes
    market_context: 600     # 10 minutes
    llm_response: 1800      # 30 minutes
    quant_analysis: 300     # 5 minutes

  # Analysis triggers
  triggers:
    critical_loss_threshold: -500  # USD
    critical_dte_threshold: 7      # Days
    refresh_interval: 300          # 5 minutes

  # UI preferences
  ui:
    default_expanded: false
    show_model_name: true
    show_cost: false
    enable_action_buttons: true

  # Budget limits
  budget:
    daily_limit: 2.00    # USD
    monthly_limit: 50.00
    alert_threshold: 80  # Percent
```

---

## Testing Strategy

### Unit Tests
```python
# tests/test_position_recommendations.py

def test_quantitative_analyzer():
    """Test rule-based analysis logic"""
    position = EnrichedPosition(...)
    analyzer = QuantitativeAnalyzer()
    result = analyzer.analyze(position)

    assert result.recommended_action in VALID_ACTIONS
    assert 0 <= result.confidence <= 100

def test_llm_analyzer_prompt_generation():
    """Test prompt builder"""
    position = EnrichedPosition(...)
    prompt = build_position_analysis_prompt(position, {}, {})

    assert 'POSITION DETAILS' in prompt
    assert position.symbol in prompt

def test_recommendation_aggregator_conflict_resolution():
    """Test conflict resolution between quant and LLM"""
    quant_rec = {'action': 'hold', 'confidence': 80}
    llm_rec = {'recommendation': 'close_now', 'confidence': 85}

    final = synthesize_recommendation(quant_rec, llm_rec, position)

    # Should favor LLM for high confidence
    assert final.action == 'close_now'

def test_cache_invalidation():
    """Test cache invalidation logic"""
    cache = RecommendationCache()
    cache.set('pos:AAPL:150:2025-12-20', data)

    # Simulate price move
    cache.invalidate_on_price_move('AAPL', old=165, new=170)

    assert cache.get('pos:AAPL:150:2025-12-20') is None
```

### Integration Tests
```python
def test_end_to_end_recommendation_generation():
    """Test full pipeline"""
    # Mock Robinhood position data
    positions = get_mock_positions()

    # Run recommendation engine
    engine = PositionRecommendationEngine()
    recommendations = engine.analyze_portfolio(positions)

    assert len(recommendations) == len(positions)
    for rec in recommendations:
        assert rec.action is not None
        assert rec.confidence > 0
        assert rec.rationale
```

---

## Security & Safety Considerations

1. **API Key Management**:
   - Store all API keys in environment variables
   - Never log API keys or sensitive data
   - Use `.env` file (excluded from git)

2. **LLM Output Validation**:
   - Always validate JSON responses
   - Sanitize outputs before displaying
   - Implement fallbacks for malformed responses

3. **Trade Execution Safety**:
   - Never auto-execute trades without user confirmation
   - Require 2FA for trade execution (future feature)
   - Log all recommendation-driven trades

4. **Data Privacy**:
   - Never send user credentials to LLM APIs
   - Anonymize position data if using third-party APIs
   - Cache responses locally, not in external services

5. **Error Handling**:
   - Graceful degradation (if LLM fails, show quant-only)
   - Rate limit enforcement
   - Circuit breakers for API failures

---

## Success Metrics

### Technical Metrics
- **Cache Hit Rate**: Target 70%+
- **Response Time**: <2s for cached, <5s for fresh analysis
- **API Cost**: <$10/month per user
- **Uptime**: 99.5%+

### Business Metrics
- **Recommendation Accuracy**: Track P/L of followed recommendations
- **User Engagement**: % of users who expand AI cards
- **Action Conversion**: % of recommendations that lead to trades
- **User Satisfaction**: Feedback ratings on recommendation quality

### Quality Metrics
- **Confidence Calibration**: Does 80% confidence = 80% accuracy?
- **False Positive Rate**: Recommendations that led to losses
- **Miss Rate**: Positions that crashed without warning

---

## Future Enhancements

1. **Portfolio-Level Analysis**:
   - Analyze correlations between positions
   - Portfolio delta/theta optimization
   - Sector concentration warnings

2. **Backtesting Framework**:
   - Test recommendation strategies on historical data
   - Compare AI vs rule-based performance
   - Optimize confidence thresholds

3. **Reinforcement Learning**:
   - Learn from user actions (which recommendations were followed)
   - Personalize recommendations based on user risk profile
   - Adaptive confidence scoring

4. **Integration with Trading View**:
   - Overlay recommendation zones on charts
   - Technical pattern recognition
   - Support/resistance level detection

5. **Voice Interface**:
   - "Alexa, what should I do with my AAPL position?"
   - Audio summaries of daily recommendations
   - Voice-activated trade execution (with safeguards)

---

## Appendix: Package Requirements

**New packages to add to `requirements.txt`**:
```txt
# Options Greeks
mibian==0.1.3  # Already installed

# Financial calculations
py_vollib==1.0.1  # Implied volatility calculation

# Market data (some already installed)
yfinance==0.2.32  # Already installed
polygon-api-client==1.12.4  # NEW
finnhub-python==2.4.18  # NEW

# Technical indicators
ta-lib==0.4.28  # NEW (requires separate TA-Lib C library)

# Caching
redis==5.0.1  # Already installed

# AI/LLM clients (already have some)
anthropic==0.25.0  # NEW (update to latest)
google-generativeai==0.3.2  # NEW

# Async support
aiohttp==3.9.1  # Already installed

# Data validation
pydantic==2.5.0  # Already installed
```

---

**END OF ARCHITECTURE DOCUMENT**

This architecture provides a production-ready, cost-effective, and maintainable AI recommendation system that leverages your existing infrastructure while adding sophisticated position analysis capabilities.
