# Position-Specific Recommendations Engine Architecture

**Document Version:** 1.0
**Date:** 2025-11-10
**Status:** Design Specification
**Project:** WheelStrategy - Magnus Trading Dashboard

---

## 1. Executive Summary

This document outlines the architecture for a **Position-Specific Recommendations Engine** that provides actionable, real-time trading recommendations for each open option position (CSPs, Covered Calls, Long Calls/Puts) in the WheelStrategy platform.

The system will analyze 10-20 active positions in real-time, incorporating market data, Greeks, news sentiment, and recovery strategies to deliver personalized recommendations directly within the Positions Page UI. The design prioritizes **scalability**, **API efficiency**, and **cost-effectiveness** while maintaining sub-2-second recommendation delivery.

### Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Hybrid Caching (Redis + PostgreSQL)** | Balance real-time accuracy with API rate limit compliance |
| **Background Processing with Priority Queue** | Decouple expensive computations from UI rendering |
| **Service-Oriented Architecture** | Maintain clean separation of concerns; enable independent testing |
| **Graceful Degradation** | Display cached recommendations if real-time fetch fails |
| **LLM-powered Insights** | Leverage existing Groq/DeepSeek integration for cost-effective AI reasoning |

---

## 2. Architecture Overview

### 2.1 System Context Diagram (Text-Based)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    POSITIONS PAGE (Streamlit UI)                    │
│  ┌────────────────┐  ┌─────────────────┐  ┌────────────────────┐   │
│  │ Position Table │  │ Recommendation  │  │ Action Buttons     │   │
│  │ (Green/Red P/L)│  │ Cards/Badges    │  │ (Roll, Close, etc.)│   │
│  └────────┬───────┘  └────────┬────────┘  └──────────┬─────────┘   │
└───────────┼──────────────────┼─────────────────────┼──────────────┘
            │                  │                     │
            ▼                  ▼                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│              RECOMMENDATION SERVICE LAYER (src/services/)           │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  PositionRecommendationService (Main Orchestrator)          │   │
│  │  - Batch position analysis                                  │   │
│  │  - Priority-based processing (losing positions first)       │   │
│  │  - Cache management and fallback logic                      │   │
│  └────┬────────────────────────────────────────────────────┬───┘   │
│       │                                                    │       │
│  ┌────▼──────────────┐  ┌──────────────────┐  ┌──────────▼──────┐ │
│  │ GreeksAnalyzer    │  │ NewsAggregator   │  │ RecoveryAdvisor │ │
│  │ (Delta, Theta,    │  │ (Finnhub,Polygon)│  │ (Rolling,       │ │
│  │  IV analysis)     │  │                  │  │  Adjustments)   │ │
│  └────┬──────────────┘  └─────────┬────────┘  └──────────┬──────┘ │
└───────┼───────────────────────────┼───────────────────────┼────────┘
        │                           │                       │
        ▼                           ▼                       ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    DATA LAYER & INTEGRATIONS                        │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐  ┌──────────┐ │
│  │ PostgreSQL  │  │ Redis Cache  │  │ Robinhood   │  │ yfinance │ │
│  │ (Options    │  │ (TTL: 2-60m) │  │ API         │  │ (Greeks) │ │
│  │  History)   │  └──────────────┘  │ (Positions) │  │          │ │
│  └─────────────┘                    └─────────────┘  └──────────┘ │
│                                                                     │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐  ┌──────────┐ │
│  │ News APIs   │  │ LLM Service  │  │ Rate Limiter│  │ Config   │ │
│  │ (Finnhub,   │  │ (Groq/Deep-  │  │ (Token      │  │ Manager  │ │
│  │  Polygon)   │  │  Seek)       │  │  Bucket)    │  │          │ │
│  └─────────────┘  └──────────────┘  └─────────────┘  └──────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 Data Flow for Single Position Recommendation

1. **User Loads Positions Page** → Fetches all positions from Robinhood API
2. **UI Triggers Recommendation Request** → `get_recommendations_batch([positions])`
3. **Service Layer Checks Cache** → Redis lookup by `position_id + timestamp_bucket`
4. **Cache Miss → Background Job** → Enqueue position analysis task
5. **Greeks Fetcher** → yfinance API call (rate-limited: 60/min)
6. **News Aggregator** → Parallel API calls to Finnhub + Polygon
7. **Recovery Advisor** → Query historical options data from PostgreSQL
8. **LLM Reasoning** → Optional AI-generated insight (Groq free tier)
9. **Store in Cache** → Redis (TTL: 15 min for active, 60 min for stable)
10. **Return to UI** → Display recommendation card/badge

---

## 3. Service Definitions

### 3.1 **PositionRecommendationService** (Main Orchestrator)

**Responsibilities:**
- Batch-process 10-20 positions efficiently
- Manage cache lifecycle (Redis TTL + PostgreSQL backup)
- Coordinate data fetching from multiple sources
- Apply priority logic (losing positions analyzed first)
- Handle API failures with graceful degradation

**Key Methods:**
```python
class PositionRecommendationService:
    def get_recommendations_batch(
        self,
        positions: List[Position],
        force_refresh: bool = False
    ) -> Dict[str, PositionRecommendation]:
        """
        Get recommendations for multiple positions.

        Returns:
            Dict mapping position_id -> PositionRecommendation
        """

    def _get_single_recommendation(
        self,
        position: Position
    ) -> PositionRecommendation:
        """Generate recommendation for one position"""

    def _prioritize_positions(
        self,
        positions: List[Position]
    ) -> List[Position]:
        """Sort by urgency: losing positions, expiring soon, etc."""
```

**Rate Limit Strategy:**
- Redis cache check: No API calls for cached results
- Batch API calls: Fetch all needed data in 2-3 parallel requests
- Fallback: Use stale cache if APIs fail (with "Last Updated" warning)

---

### 3.2 **GreeksAnalyzer** (Options Greeks Analysis)

**Responsibilities:**
- Fetch real-time Greeks (Delta, Theta, Gamma, Vega) from yfinance
- Calculate position-specific metrics (theta decay, delta exposure)
- Identify moneyness (ITM/ATM/OTM) and assignment risk

**Data Sources:**
- **Primary:** yfinance (free, 60 calls/min limit)
- **Fallback:** TradingView database (historical Greeks estimates)

**Key Methods:**
```python
class GreeksAnalyzer:
    @rate_limit("yfinance", tokens=1, timeout=5)
    def fetch_greeks(
        self,
        symbol: str,
        strike: float,
        expiration: datetime,
        option_type: str
    ) -> OptionsGreeks:
        """Fetch live Greeks from yfinance"""

    def calculate_theta_decay_rate(
        self,
        greeks: OptionsGreeks,
        dte: int
    ) -> float:
        """Daily theta decay ($/day)"""

    def assess_assignment_risk(
        self,
        position: Position,
        stock_price: float,
        greeks: OptionsGreeks
    ) -> AssignmentRisk:
        """Risk level: LOW, MEDIUM, HIGH"""
```

**Greeks Calculation Logic:**
```python
# For CSPs (Short Puts):
- Delta: -0.3 to -0.1 = LOW assignment risk (OTM)
- Delta: -0.5 to -0.4 = MEDIUM risk (ATM)
- Delta: -0.7+ = HIGH risk (ITM)

# Theta Decay:
- Good: Theta > $5/day per contract
- Moderate: Theta $2-5/day
- Low: Theta < $2/day

# IV Rank:
- High IV (>60%) = Good for selling premium
- Low IV (<30%) = Poor for selling, good for buying
```

---

### 3.3 **NewsAggregator** (Market Sentiment Analysis)

**Responsibilities:**
- Fetch recent news for position symbols
- Extract sentiment signals (earnings, analyst upgrades, FDA news, etc.)
- Deduplicate and prioritize high-impact news

**Data Sources:**
- Finnhub API (free tier: 60 calls/min)
- Polygon API (free tier: 5 calls/min)
- Existing `NewsService` class (already implemented)

**Key Methods:**
```python
class NewsAggregator:
    def get_position_news_summary(
        self,
        symbol: str,
        days_back: int = 7
    ) -> NewsSummary:
        """
        Returns:
            NewsSummary(
                sentiment="bullish" | "bearish" | "neutral",
                key_events=["Earnings beat", "FDA approval"],
                impact_score=0.0 to 1.0
            )
        """

    def detect_high_impact_events(
        self,
        articles: List[NewsArticle]
    ) -> List[str]:
        """Identify keywords: earnings, merger, FDA, bankruptcy"""
```

**Sentiment Scoring:**
```python
# Impact Keywords:
HIGH_IMPACT = ["earnings", "FDA", "merger", "acquisition", "bankruptcy",
               "analyst upgrade", "analyst downgrade"]
MEDIUM_IMPACT = ["revenue", "guidance", "product launch", "CEO"]
LOW_IMPACT = ["partnership", "hiring", "event"]

# Sentiment Mapping to Action:
- Bullish news + Losing CSP → HOLD (stock may recover)
- Bearish news + Losing CSP → ROLL DOWN or CLOSE
- Bullish news + Profitable CC → ROLL UP (capture more upside)
```

---

### 3.4 **RecoveryAdvisor** (Strategy-Specific Recommendations)

**Responsibilities:**
- Analyze losing positions and suggest recovery strategies
- Calculate optimal roll targets (strike, expiration)
- Identify adjustment opportunities (spread conversions)

**Key Methods:**
```python
class RecoveryAdvisor:
    def get_recovery_strategy(
        self,
        position: Position,
        greeks: OptionsGreeks,
        news: NewsSummary
    ) -> RecoveryStrategy:
        """
        Returns:
            RecoveryStrategy(
                action="ROLL_DOWN" | "ROLL_OUT" | "CLOSE" | "HOLD",
                target_strike=155.0,
                target_expiration="2025-12-15",
                expected_credit=45.50,
                reasoning="Stock down 8%, IV elevated. Roll to $155 strike..."
            )
        """

    def find_optimal_roll_targets(
        self,
        symbol: str,
        current_strike: float,
        current_exp: datetime
    ) -> List[RollOpportunity]:
        """Query TradingView DB for best roll candidates"""
```

**Recovery Logic (CSPs):**
```python
# Losing CSP Decision Tree:
if pl_pct < -20% and dte < 7:
    if news.sentiment == "bullish":
        recommendation = "ROLL OUT (same strike, +30 days)"
    else:
        recommendation = "ROLL DOWN & OUT (lower strike, +30 days)"

elif pl_pct < -50% and greeks.delta > -0.8:
    recommendation = "CLOSE and re-evaluate (deep ITM, assignment likely)"

else:
    recommendation = "HOLD (theta decay working in your favor)"
```

---

### 3.5 **LLMReasoningService** (AI-Powered Insights)

**Responsibilities:**
- Generate human-readable explanations for recommendations
- Synthesize multi-factor analysis (Greeks + News + Technicals)
- Provide "Why this recommendation?" reasoning

**Provider Selection:**
- **Primary:** Groq (free tier, fast inference)
- **Fallback:** DeepSeek (very cheap: $0.14/$0.28 per 1M tokens)

**Key Methods:**
```python
class LLMReasoningService:
    @rate_limit("groq", tokens=1, timeout=10)
    def generate_recommendation_reasoning(
        self,
        position: Position,
        greeks: OptionsGreeks,
        news: NewsSummary,
        recovery: RecoveryStrategy
    ) -> str:
        """
        Generates 2-3 sentence explanation like:

        "Your NVDA $180 CSP is down 15% with 12 days to expiration.
        Delta is -0.65 (assignment risk increasing). Recent news shows
        strong earnings beat. Recommendation: Roll to $175 strike for
        +$45 credit to reduce assignment risk while IV is elevated."
        """
```

**Prompt Template:**
```python
RECOMMENDATION_PROMPT = """
You are a wheel strategy options advisor. Analyze this position:

Position: {symbol} ${strike} {option_type} expiring {expiration}
Current P/L: {pl_pct}%
Greeks: Delta={delta}, Theta={theta}, IV={iv}%
News Sentiment: {sentiment}
Stock Price: ${stock_price}

Provide a 2-3 sentence recommendation focusing on:
1. Current position status (winning/losing, assignment risk)
2. Key factor driving the recommendation (Greeks, news, or time decay)
3. Specific action (HOLD, ROLL, CLOSE) with target parameters

Recommendation:
"""
```

**Cost Mitigation:**
- Only generate LLM reasoning for losing positions (P/L < -10%)
- Cache LLM responses for 1 hour (same position state)
- Use Groq free tier first (30 calls/min), fallback to DeepSeek

---

## 4. API Contracts & Data Schemas

### 4.1 **PositionRecommendation** (Response Object)

```python
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
from enum import Enum

class RecommendationAction(Enum):
    HOLD = "HOLD"
    ROLL_OUT = "ROLL_OUT"          # Extend expiration, same strike
    ROLL_DOWN = "ROLL_DOWN"        # Lower strike, same expiration
    ROLL_DOWN_OUT = "ROLL_DOWN_OUT"  # Lower strike + extend expiration
    ROLL_UP = "ROLL_UP"            # Higher strike (for CCs)
    CLOSE = "CLOSE"                # Exit position
    ADD_HEDGE = "ADD_HEDGE"        # Buy protective option
    CONVERT_SPREAD = "CONVERT_SPREAD"  # Turn into spread

class RiskLevel(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

@dataclass
class OptionsGreeks:
    delta: float
    theta: float
    gamma: float
    vega: float
    iv: float  # Implied volatility %
    updated_at: datetime

@dataclass
class NewsSummary:
    sentiment: str  # "bullish", "bearish", "neutral"
    key_events: List[str]
    impact_score: float  # 0.0 to 1.0
    latest_headline: Optional[str] = None

@dataclass
class RecoveryStrategy:
    action: RecommendationAction
    target_strike: Optional[float] = None
    target_expiration: Optional[datetime] = None
    expected_credit: Optional[float] = None
    reasoning: str = ""

@dataclass
class PositionRecommendation:
    position_id: str
    symbol: str
    action: RecommendationAction
    risk_level: RiskLevel
    confidence: float  # 0.0 to 1.0

    # Primary recommendation
    short_summary: str  # e.g., "Roll Down & Out to $155 (+$45 credit)"
    detailed_reasoning: str

    # Supporting data
    greeks: Optional[OptionsGreeks] = None
    news: Optional[NewsSummary] = None
    recovery: Optional[RecoveryStrategy] = None

    # Metadata
    generated_at: datetime
    cache_expires_at: datetime
    data_freshness: str  # "real-time", "cached-2m", "stale"
```

### 4.2 **API Endpoints** (Internal Service Methods)

```python
# Main API
def get_recommendations_batch(
    positions: List[Position],
    force_refresh: bool = False
) -> Dict[str, PositionRecommendation]:
    """
    Batch-fetch recommendations for multiple positions.

    Args:
        positions: List of Position objects from Robinhood
        force_refresh: Bypass cache and fetch fresh data

    Returns:
        Dict mapping position_id -> PositionRecommendation

    Rate Limits:
        - Redis cache: unlimited
        - yfinance: 60 calls/min
        - Finnhub: 60 calls/min
        - Polygon: 5 calls/min
        - Groq: 30 calls/min (free tier)
    """

# Individual fetchers (for testing/debugging)
def fetch_greeks(symbol: str, strike: float, exp: datetime, opt_type: str) -> OptionsGreeks:
    """Fetch Greeks from yfinance"""

def fetch_news_summary(symbol: str, days_back: int = 7) -> NewsSummary:
    """Fetch aggregated news from Finnhub + Polygon"""

def generate_recovery_plan(position: Position, greeks: OptionsGreeks) -> RecoveryStrategy:
    """Calculate optimal recovery strategy"""
```

---

## 5. Data Schema Changes

### 5.1 **New Table: `position_recommendations`** (PostgreSQL)

```sql
-- Store recommendation history for backtesting and auditing
CREATE TABLE position_recommendations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    position_id VARCHAR(100) NOT NULL,  -- Robinhood position ID
    symbol VARCHAR(10) NOT NULL,

    -- Recommendation details
    action VARCHAR(30) NOT NULL,  -- HOLD, ROLL_DOWN, etc.
    risk_level VARCHAR(10) NOT NULL,
    confidence DECIMAL(3,2),  -- 0.00 to 1.00
    short_summary TEXT,
    detailed_reasoning TEXT,

    -- Supporting data (JSON)
    greeks_data JSONB,
    news_data JSONB,
    recovery_data JSONB,

    -- Metadata
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    cache_expires_at TIMESTAMP WITH TIME ZONE,
    data_freshness VARCHAR(20),  -- 'real-time', 'cached', 'stale'

    -- User action tracking (did they follow the recommendation?)
    user_action VARCHAR(30),  -- NULL if not acted upon
    user_action_timestamp TIMESTAMP WITH TIME ZONE,

    -- Outcome tracking (for ML training)
    position_closed_at TIMESTAMP WITH TIME ZONE,
    final_pnl DECIMAL(10,2),
    recommendation_accuracy DECIMAL(3,2),  -- Calculated post-close

    CONSTRAINT fk_symbol FOREIGN KEY (symbol) REFERENCES stocks(symbol)
);

-- Indexes for fast lookups
CREATE INDEX idx_position_recommendations_position_id ON position_recommendations(position_id);
CREATE INDEX idx_position_recommendations_symbol ON position_recommendations(symbol);
CREATE INDEX idx_position_recommendations_generated_at ON position_recommendations(generated_at DESC);

-- Time-series optimization
SELECT create_hypertable('position_recommendations', 'generated_at');
```

### 5.2 **Extend Table: `options_chains`** (Add Greeks if missing)

```sql
-- Ensure Greeks columns exist (already present in schema)
-- Delta, Gamma, Theta, Vega, Rho already defined

-- Add index for Greeks-based queries
CREATE INDEX idx_options_chains_greeks ON options_chains(
    stock_id,
    expiration_date,
    delta,
    implied_volatility
) WHERE delta IS NOT NULL;
```

### 5.3 **Redis Cache Schema**

```python
# Cache key format:
CACHE_KEY = f"rec:{position_id}:{timestamp_bucket}"

# Example:
# rec:NVDA-180P-2025-12-15:2025-11-10-14:00
#     └── position_id     └── 15-minute bucket

# TTL Strategy:
CACHE_TTL = {
    "winning_positions": 3600,     # 60 minutes (stable)
    "losing_positions": 900,       # 15 minutes (more volatile)
    "expiring_soon": 300,          # 5 minutes (high urgency)
}

# Cached Value (JSON):
{
    "position_id": "NVDA-180P-2025-12-15",
    "action": "ROLL_DOWN_OUT",
    "risk_level": "HIGH",
    "confidence": 0.85,
    "short_summary": "Roll to $175 strike, +30 days (+$45 credit)",
    "detailed_reasoning": "...",
    "greeks": {...},
    "news": {...},
    "generated_at": "2025-11-10T14:23:15Z",
    "expires_at": "2025-11-10T14:38:15Z"
}
```

---

## 6. Integration Points with Existing Code

### 6.1 **positions_page_improved.py** (UI Integration)

**Insertion Point:** After line 714 (inside `display_strategy_table`)

```python
# NEW: Fetch recommendations for current positions
from src.services.position_recommendation_service import get_recommendations_batch

# Inside display_strategy_table function:
def display_strategy_table(title, emoji, positions, section_key, expanded=False):
    if not positions:
        return

    with st.expander(f"{emoji} {title} ({len(positions)})", expanded=expanded):
        df = pd.DataFrame(positions)

        # === NEW: Fetch Recommendations ===
        with st.spinner("Analyzing positions..."):
            recommendations = get_recommendations_batch(positions)

        # Add recommendation column to DataFrame
        df['Recommendation'] = df.apply(
            lambda row: recommendations.get(
                row['symbol_raw'],
                PositionRecommendation(action="HOLD", short_summary="No recommendation")
            ).short_summary,
            axis=1
        )

        # Display table with new column
        display_df = df.copy()
        # ... existing formatting code ...

        # Add clickable recommendation badges
        st.dataframe(
            styled_df,
            hide_index=True,
            column_config={
                "Recommendation": st.column_config.TextColumn(
                    "💡 Action",
                    help="AI-powered recommendation",
                    width="medium"
                ),
                # ... existing column configs ...
            }
        )

        # === NEW: Expandable Recommendation Details ===
        st.markdown("#### 📋 Detailed Recommendations")
        for pos in positions:
            rec = recommendations.get(pos['symbol_raw'])
            if rec and rec.action != RecommendationAction.HOLD:
                with st.expander(
                    f"{pos['Symbol']} ${pos['Strike']} - {rec.action.value}",
                    expanded=False
                ):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.markdown(f"**{rec.detailed_reasoning}**")
                    with col2:
                        st.metric("Risk Level", rec.risk_level.value)
                    with col3:
                        st.metric("Confidence", f"{rec.confidence*100:.0f}%")

                    if rec.greeks:
                        st.markdown("**Greeks:**")
                        col1, col2, col3, col4 = st.columns(4)
                        col1.metric("Delta", f"{rec.greeks.delta:.2f}")
                        col2.metric("Theta", f"${rec.greeks.theta:.2f}/day")
                        col3.metric("IV", f"{rec.greeks.iv:.1f}%")
                        col4.metric("Updated", rec.greeks.updated_at.strftime("%H:%M"))

                    if rec.news and rec.news.key_events:
                        st.markdown("**Recent News:**")
                        for event in rec.news.key_events[:3]:
                            st.markdown(f"- {event}")

                    # Action button
                    if rec.recovery:
                        st.button(
                            f"Execute: {rec.recovery.action.value}",
                            key=f"action_{pos['symbol_raw']}",
                            type="primary"
                        )
```

### 6.2 **src/services/robinhood_client.py** (Data Source)

```python
# Extend existing RobinhoodClient to support recommendation data

class RobinhoodClient:
    # ... existing methods ...

    def get_positions_with_metadata(self) -> List[Position]:
        """
        Enhanced position fetcher for recommendation engine.

        Returns Position objects with:
        - Basic details (symbol, strike, expiration, P/L)
        - Current stock price
        - Days to expiration
        - Option type and position type
        """
        positions = rh.get_open_option_positions()

        enriched = []
        for pos in positions:
            # ... existing parsing logic ...

            enriched.append(Position(
                position_id=f"{symbol}-{strike}{opt_type[0]}-{exp_date}",
                symbol=symbol,
                strike=strike,
                expiration=exp_date,
                option_type=opt_type,
                position_type=position_type,
                quantity=quantity,
                avg_price=avg_price,
                current_price=current_price,
                pl=pl,
                pl_pct=(pl/total_premium*100) if total_premium > 0 else 0,
                dte=(exp_dt - datetime.now()).days
            ))

        return enriched
```

### 6.3 **src/services/rate_limiter.py** (Already Exists!)

The existing `RateLimiter` class will be used as-is:

```python
from src.services.rate_limiter import rate_limit

# In GreeksAnalyzer:
@rate_limit("yfinance", tokens=1, timeout=5)
def fetch_greeks(self, ...):
    # yfinance API call
```

### 6.4 **src/news_service.py** (Already Exists!)

The existing `NewsService` will be wrapped:

```python
from src.news_service import NewsService

class NewsAggregator:
    def __init__(self):
        self.news_service = NewsService()

    def get_position_news_summary(self, symbol: str) -> NewsSummary:
        articles = self.news_service.get_combined_news(symbol)

        # Add sentiment analysis
        sentiment = self._analyze_sentiment(articles)
        key_events = self._extract_key_events(articles)

        return NewsSummary(
            sentiment=sentiment,
            key_events=key_events,
            impact_score=self._calculate_impact(articles)
        )
```

---

## 7. Technology Stack & Dependencies

### 7.1 **New Python Packages** (Add to requirements.txt)

```txt
# Options Greeks calculation
yfinance>=0.2.40              # Free options data with Greeks

# Redis caching
redis>=5.0.1                  # Redis client
hiredis>=2.2.3               # Fast C parser for Redis

# Background job processing (optional)
rq>=1.15.1                    # Redis Queue for async tasks
rq-scheduler>=0.13.1         # Scheduled background jobs

# Sentiment analysis (optional)
textblob>=0.17.1             # Basic NLP for news sentiment
vaderSentiment>=3.3.2        # Financial sentiment analyzer

# Async HTTP (for parallel API calls)
aiohttp>=3.9.1               # Async HTTP client
asyncio>=3.4.3               # Async runtime (stdlib, but good to specify)
```

### 7.2 **Recommended GitHub Projects**

| Package | Purpose | GitHub Link |
|---------|---------|-------------|
| **mibian** | Black-Scholes Greeks calculator (pure Python) | [github.com/yassinemaaroufi/MibianLib](https://github.com/yassinemaaroufi/MibianLib) |
| **optlib** | Options pricing and Greeks (fast, NumPy-based) | [github.com/CarsonGSmith/optlib](https://github.com/CarsonGSmith/optlib) |
| **vollib** | Implied volatility calculations | [github.com/vollib/vollib](https://github.com/vollib/vollib) |

**Recommendation:** Use **yfinance** (already getting real-time Greeks from exchanges) and fallback to **mibian** for manual calculation if API fails.

### 7.3 **Infrastructure Requirements**

| Component | Spec | Cost | Notes |
|-----------|------|------|-------|
| **Redis** | 256MB RAM | Free (local) or $7/mo (Redis Cloud) | Use local Redis for dev, cloud for prod |
| **PostgreSQL** | 10GB storage | Free (local) or $15/mo (Supabase) | Existing DB, no extra cost |
| **LLM API** | Groq free tier → DeepSeek paid | Free → $0.10/day | ~500 recommendations/day |

---

## 8. Scalability Plan

### 8.1 **Handling 10-20 Positions Efficiently**

| Strategy | Implementation | Expected Gain |
|----------|----------------|---------------|
| **Batch API Calls** | Fetch all Greeks in 1-2 parallel `yfinance` calls | 10x faster vs sequential |
| **Redis Caching** | Cache recommendations for 15-60 minutes | 90% cache hit rate after warmup |
| **Priority Queue** | Process losing positions first, cache winners longer | Improve UX for urgent positions |
| **Async Processing** | Use `asyncio` for parallel news/Greeks fetching | Sub-2s total recommendation time |
| **Graceful Degradation** | Show cached recommendations if APIs fail | 100% uptime |

### 8.2 **Batch vs. Individual Position Analysis**

**Decision: Hybrid Approach**

```python
def get_recommendations_batch(positions: List[Position]) -> Dict[str, PositionRecommendation]:
    # Step 1: Check cache for all positions
    cached = _get_from_cache([p.position_id for p in positions])

    # Step 2: Identify positions needing fresh data
    needs_update = [p for p in positions if p.position_id not in cached]

    # Step 3: Batch-fetch Greeks for all uncached positions
    symbols = list(set([p.symbol for p in needs_update]))
    greeks_batch = _fetch_greeks_batch(symbols)  # Single yfinance call

    # Step 4: Parallel news fetching (async)
    news_batch = await _fetch_news_batch(symbols)  # Concurrent API calls

    # Step 5: Generate recommendations
    fresh = {}
    for pos in needs_update:
        fresh[pos.position_id] = _generate_recommendation(
            pos, greeks_batch[pos.symbol], news_batch[pos.symbol]
        )

    # Step 6: Store in cache
    _store_in_cache(fresh)

    # Step 7: Merge cached + fresh
    return {**cached, **fresh}
```

**Performance:**
- **10 positions:** 1.5 seconds (all uncached)
- **20 positions:** 2.5 seconds (all uncached)
- **10 positions (cached):** 0.2 seconds

### 8.3 **Background Processing vs. On-Demand**

**Decision: Hybrid with Smart Scheduling**

```python
# On-Demand (Default):
# - Fetch recommendations when user opens Positions Page
# - Use cache for repeat views within 15 minutes

# Background Processing (Optional):
# - Schedule background job to pre-fetch recommendations every 15 min
# - Only for users with auto-refresh enabled
# - Use RQ (Redis Queue) for scheduling

from rq import Queue
from redis import Redis

redis_conn = Redis(host='localhost', port=6379)
queue = Queue('recommendations', connection=redis_conn)

def schedule_background_refresh(user_id: str, positions: List[Position]):
    """Enqueue background job to refresh recommendations"""
    job = queue.enqueue(
        'src.services.position_recommendation_service.refresh_recommendations',
        user_id=user_id,
        positions=positions,
        job_timeout='5m'
    )
    return job.id
```

**Use Background Jobs For:**
- Auto-refresh enabled users (polling every 2-5 minutes)
- Pre-market warmup (7:00 AM ET)
- Post-earnings updates (scheduled events)

---

## 9. Recommendation Storage Strategy

### 9.1 **Cache Layer Design (Redis)**

**TTL Strategy:**

```python
def calculate_cache_ttl(position: Position) -> int:
    """Dynamic TTL based on position characteristics"""

    # Expiring soon = shorter TTL
    if position.dte <= 7:
        return 300  # 5 minutes

    # Losing positions = shorter TTL (more volatility)
    if position.pl_pct < -10:
        return 900  # 15 minutes

    # Winning positions = longer TTL (stable)
    if position.pl_pct > 5:
        return 3600  # 60 minutes

    # Default
    return 1800  # 30 minutes
```

**Cache Invalidation:**
- Automatic: TTL expiration
- Manual: User clicks "Refresh Now"
- Event-driven: Major news detected (earnings, FDA, etc.)

### 9.2 **Database Storage (PostgreSQL)**

**When to Store:**
1. User acts on recommendation (clicked "Execute")
2. Position closes (for accuracy tracking)
3. Daily snapshot (for backtesting)

**Why Store:**
- **Backtesting:** Evaluate recommendation accuracy over time
- **ML Training:** Build dataset for future AI model
- **Audit Trail:** Compliance and user trust
- **Analytics:** "Which recommendations are most profitable?"

### 9.3 **Update Frequency**

| Position State | Cache TTL | Update Trigger |
|---------------|-----------|----------------|
| **Winning (P/L > 5%)** | 60 min | Manual refresh only |
| **Breakeven (P/L ±5%)** | 30 min | Auto-refresh if enabled |
| **Losing (P/L -5% to -20%)** | 15 min | Auto-refresh + news events |
| **Critical (P/L < -20% or DTE < 7)** | 5 min | Real-time monitoring |

---

## 10. UI Integration Design

### 10.1 **Display Recommendation in Table**

**Option 1: Badge in Existing Table** (Recommended)

```python
# Add column to DataFrame
df['Action'] = df['symbol_raw'].map(
    lambda s: recommendations[s].action.value
)

# Color-coded badges
def style_recommendation(action: str):
    colors = {
        "HOLD": "🟢 HOLD",
        "ROLL_DOWN": "🟡 ROLL DOWN",
        "CLOSE": "🔴 CLOSE"
    }
    return colors.get(action, action)

df['Action'] = df['Action'].apply(style_recommendation)
```

**Display Result:**
```
Symbol | Stock Price | Strike | P/L    | Action
NVDA   | $182.50     | $180   | -$45   | 🟡 ROLL DOWN
AAPL   | $175.20     | $170   | +$120  | 🟢 HOLD
TSLA   | $195.00     | $200   | -$250  | 🔴 CLOSE
```

**Option 2: Expandable Details Below Each Position**

```python
# After main table, show detailed cards for losing positions
st.markdown("### 💡 Active Recommendations")

for pos in losing_positions:
    rec = recommendations[pos['symbol_raw']]

    with st.expander(f"{pos['Symbol']} - {rec.action.value}", expanded=True):
        col1, col2 = st.columns([3, 1])

        with col1:
            st.markdown(f"**{rec.detailed_reasoning}**")

            if rec.recovery:
                st.info(
                    f"💰 Target: ${rec.recovery.target_strike} strike, "
                    f"exp {rec.recovery.target_expiration.strftime('%Y-%m-%d')} "
                    f"for ${rec.recovery.expected_credit:.2f} credit"
                )

        with col2:
            st.metric("Risk", rec.risk_level.value)
            st.metric("Confidence", f"{rec.confidence*100:.0f}%")

            # Action button
            if st.button("Execute", key=f"exec_{pos['symbol_raw']}"):
                st.success("Opening Robinhood app...")
                # TODO: Deep link to Robinhood
```

### 10.2 **Action Buttons vs. Text Descriptions**

**Recommendation: Both**

1. **Text Badge** (always visible in table)
   - Quick scan: "HOLD", "ROLL DOWN", "CLOSE"
   - Color-coded: Green = HOLD, Yellow = Action needed, Red = Urgent

2. **Action Button** (in expandable section)
   - Opens Robinhood app (deep link)
   - Pre-fills order form with recommended parameters
   - Tracks user action in database

**Example Deep Link:**
```python
# Robinhood URL scheme (iOS/Android)
def generate_robinhood_link(symbol: str, action: str, strike: float, exp: datetime) -> str:
    if action == "ROLL_DOWN":
        # Deep link to options chain with pre-selected strike
        return f"robinhood://options/{symbol}?strike={strike}&expiration={exp.strftime('%Y-%m-%d')}"
    elif action == "CLOSE":
        return f"robinhood://positions/{symbol}"
    else:
        return f"robinhood://stocks/{symbol}"
```

### 10.3 **Expandable Details with Reasoning**

**Interactive Card Design:**

```python
with st.expander(f"📊 {symbol} ${strike}P - {action}", expanded=False):
    # Header: Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Current P/L", f"${pl:.2f}", delta=f"{pl_pct:.1f}%")
    col2.metric("Delta", f"{greeks.delta:.2f}")
    col3.metric("DTE", f"{dte} days")
    col4.metric("IV", f"{greeks.iv:.1f}%")

    # Reasoning
    st.markdown("### 💡 Why This Recommendation?")
    st.info(rec.detailed_reasoning)

    # Supporting Data
    tabs = st.tabs(["Greeks", "News", "Recovery Plan"])

    with tabs[0]:  # Greeks
        st.markdown("**Options Greeks:**")
        df_greeks = pd.DataFrame({
            'Metric': ['Delta', 'Theta', 'Gamma', 'Vega', 'IV'],
            'Value': [greeks.delta, greeks.theta, greeks.gamma, greeks.vega, greeks.iv],
            'Interpretation': [
                'Assignment probability',
                'Daily premium decay',
                'Delta sensitivity',
                'IV sensitivity',
                'Implied volatility'
            ]
        })
        st.dataframe(df_greeks, hide_index=True)

    with tabs[1]:  # News
        st.markdown(f"**Sentiment: {news.sentiment.upper()}**")
        for event in news.key_events:
            st.markdown(f"- {event}")

    with tabs[2]:  # Recovery Plan
        if rec.recovery:
            st.markdown(f"**Recommended Action: {rec.recovery.action.value}**")
            st.markdown(f"- Target Strike: ${rec.recovery.target_strike}")
            st.markdown(f"- Target Expiration: {rec.recovery.target_expiration}")
            st.markdown(f"- Expected Credit: ${rec.recovery.expected_credit}")

            st.button("Execute in Robinhood", type="primary")
```

---

## 11. Risk Mitigation Strategies

### 11.1 **API Failure Handling**

| Failure Type | Mitigation Strategy | User Experience |
|--------------|---------------------|-----------------|
| **yfinance timeout** | Fall back to cached Greeks (show "Last updated: 15m ago") | Warning badge: "⚠️ Using cached Greeks" |
| **Finnhub rate limit** | Use only Polygon news, skip sentiment analysis | No news section, show "News unavailable" |
| **Redis down** | Fall back to PostgreSQL `position_recommendations` table | Slower (2-3s delay), show loading spinner |
| **LLM API failure** | Use template-based reasoning (no AI) | Generic text: "Consider rolling based on Greeks" |
| **Total API failure** | Show only position data, no recommendations | Error banner: "Recommendations temporarily unavailable" |

### 11.2 **Graceful Degradation Hierarchy**

```python
def get_recommendation_with_fallbacks(position: Position) -> PositionRecommendation:
    """Multi-tier fallback system"""

    # Tier 1: Full recommendation (all data sources)
    try:
        return _generate_full_recommendation(position)
    except Exception as e:
        logger.warning(f"Tier 1 failed: {e}")

    # Tier 2: Partial recommendation (Greeks only, no news)
    try:
        greeks = fetch_greeks(position.symbol, position.strike, position.expiration)
        return _generate_greeks_only_recommendation(position, greeks)
    except Exception as e:
        logger.warning(f"Tier 2 failed: {e}")

    # Tier 3: Rule-based recommendation (no external APIs)
    try:
        return _generate_rule_based_recommendation(position)
    except Exception as e:
        logger.error(f"Tier 3 failed: {e}")

    # Tier 4: Fallback to cached recommendation (stale OK)
    cached = _get_stale_cache(position.position_id)
    if cached:
        cached.data_freshness = "stale"
        return cached

    # Tier 5: Default "HOLD" with error message
    return PositionRecommendation(
        position_id=position.position_id,
        symbol=position.symbol,
        action=RecommendationAction.HOLD,
        risk_level=RiskLevel.MEDIUM,
        confidence=0.0,
        short_summary="Unable to generate recommendation",
        detailed_reasoning="Please check data sources and try again later.",
        data_freshness="unavailable"
    )
```

### 11.3 **Rate Limit Management**

**Token Bucket Configuration:**

```python
# From existing src/services/config.py
RATE_LIMITS = {
    "yfinance": ServiceRateLimit(max_calls=60, time_window=60),
    "finnhub": ServiceRateLimit(max_calls=60, time_window=60),
    "polygon": ServiceRateLimit(max_calls=5, time_window=60),
    "groq": ServiceRateLimit(max_calls=30, time_window=60),
}

# Smart rate limiting for batch requests
def batch_api_call_with_rate_limit(symbols: List[str], api_func, rate_limiter):
    """
    Split batch into chunks to respect rate limits.

    Example:
        20 positions, 60 calls/min limit
        → Process 60 symbols/min (3 symbols/sec)
        → Total time: ~20 seconds for 20 positions
    """
    results = {}

    for symbol in symbols:
        if rate_limiter.wait_if_needed("yfinance", tokens=1, timeout=5):
            results[symbol] = api_func(symbol)
        else:
            # Timeout: use cached data
            results[symbol] = _get_cached_greeks(symbol)

    return results
```

### 11.4 **Data Validation & Error Handling**

```python
def validate_greeks(greeks: OptionsGreeks) -> bool:
    """Sanity check for Greeks data"""

    # Delta range checks
    if not -1.0 <= greeks.delta <= 1.0:
        logger.error(f"Invalid delta: {greeks.delta}")
        return False

    # Theta should be negative for option buyers, can be positive/negative for sellers
    if abs(greeks.theta) > 100:  # $100/day theta is unrealistic
        logger.warning(f"Suspicious theta: {greeks.theta}")
        return False

    # IV range check
    if not 0 < greeks.iv < 500:  # IV should be 0-500%
        logger.error(f"Invalid IV: {greeks.iv}")
        return False

    return True
```

---

## 12. Implementation Roadmap

### Phase 1: Core Infrastructure (Week 1)
- [ ] Create `PositionRecommendation` dataclasses
- [ ] Implement `PositionRecommendationService` orchestrator
- [ ] Set up Redis cache with TTL logic
- [ ] Create PostgreSQL `position_recommendations` table
- [ ] Write unit tests for data models

### Phase 2: Data Sources (Week 2)
- [ ] Implement `GreeksAnalyzer` with yfinance integration
- [ ] Add rate limiting decorators to all API calls
- [ ] Implement fallback logic (cached data when APIs fail)
- [ ] Test Greeks fetching for 20 positions (performance)
- [ ] Write integration tests for API calls

### Phase 3: Recommendation Logic (Week 3)
- [ ] Implement `RecoveryAdvisor` for CSPs
- [ ] Implement `RecoveryAdvisor` for Covered Calls
- [ ] Implement `RecoveryAdvisor` for Long Calls/Puts
- [ ] Integrate `NewsAggregator` with existing NewsService
- [ ] Add LLM reasoning generation (Groq/DeepSeek)
- [ ] Write recommendation accuracy tests

### Phase 4: UI Integration (Week 4)
- [ ] Add recommendation column to positions table
- [ ] Create expandable recommendation cards
- [ ] Add action buttons with Robinhood deep links
- [ ] Implement manual refresh button
- [ ] Add loading states and error messages
- [ ] User acceptance testing

### Phase 5: Background Jobs & Optimization (Week 5)
- [ ] Set up RQ (Redis Queue) for background processing
- [ ] Implement auto-refresh for positions (2-5 min)
- [ ] Add recommendation caching warmup (pre-market)
- [ ] Optimize batch API calls (reduce latency)
- [ ] Performance testing (100+ positions)

### Phase 6: Analytics & ML Prep (Week 6)
- [ ] Implement user action tracking (did they follow recommendation?)
- [ ] Add outcome tracking (was recommendation profitable?)
- [ ] Build analytics dashboard for recommendation accuracy
- [ ] Export training data for future ML model
- [ ] Documentation and knowledge transfer

---

## 13. File Structure

```
WheelStrategy/
├── src/
│   ├── services/
│   │   ├── position_recommendation_service.py  # Main orchestrator
│   │   ├── greeks_analyzer.py                  # Options Greeks fetcher
│   │   ├── news_aggregator.py                  # News + sentiment wrapper
│   │   ├── recovery_advisor.py                 # Strategy-specific recommendations
│   │   ├── llm_reasoning_service.py           # AI-powered insights
│   │   └── __init__.py
│   │
│   ├── models/
│   │   ├── position_recommendation.py          # Dataclasses
│   │   └── __init__.py
│   │
│   ├── cache/
│   │   ├── redis_cache_manager.py             # Redis wrapper
│   │   └── __init__.py
│   │
│   └── db/
│       ├── recommendation_db_manager.py        # PostgreSQL CRUD
│       └── __init__.py
│
├── database_schema.sql                          # Add new tables
├── positions_page_improved.py                  # UI integration
├── requirements.txt                            # Add new dependencies
└── docs/
    └── architecture/
        └── POSITION_RECOMMENDATIONS_ARCHITECTURE.md  # This document
```

---

## 14. Cost Analysis

### 14.1 **API Costs (Monthly)**

| Service | Tier | Calls/Day | Cost |
|---------|------|-----------|------|
| **yfinance** | Free | 1,000 | $0 |
| **Finnhub** | Free | 500 | $0 |
| **Polygon** | Free | 100 | $0 |
| **Groq (LLM)** | Free | 500 | $0 |
| **DeepSeek (LLM)** | Paid | 500 (if Groq exceeded) | ~$3/month |
| **Redis Cloud** | Free (50MB) | Unlimited | $0 (or $7/mo for 256MB) |

**Total: $0-10/month**

### 14.2 **Infrastructure Costs**

| Resource | Spec | Cost |
|----------|------|------|
| **Redis** | 256MB RAM | Free (local) or $7/mo (cloud) |
| **PostgreSQL** | 10GB | Free (existing DB) |
| **Background Worker** | 1 CPU, 512MB RAM | Free (local) or $5/mo (Heroku) |

**Total: $0-12/month**

### 14.3 **Performance Metrics**

| Metric | Target | Actual (Expected) |
|--------|--------|-------------------|
| **Recommendation Latency** | < 2 seconds | 1.5 seconds (uncached) |
| **Cache Hit Rate** | > 80% | 85% (after warmup) |
| **API Failure Rate** | < 1% | 0.5% (with fallbacks) |
| **Cost per Recommendation** | < $0.01 | $0.003 (cached) to $0.02 (full) |

---

## 15. Security & Compliance

### 15.1 **Data Privacy**

- **Position Data:** Never stored in logs or external services
- **User Actions:** Encrypted at rest in PostgreSQL
- **API Keys:** Stored in `.env`, never committed to Git
- **Redis:** Local-only or TLS-encrypted connection

### 15.2 **Robinhood API Terms**

- **Unofficial API:** robin_stocks uses undocumented endpoints
- **Risk:** Account suspension if rate limits abused
- **Mitigation:** Conservative rate limits (60 calls/min vs. Robinhood's ~120)
- **Disclaimer:** Show "Not affiliated with Robinhood" in UI

---

## 16. Future Enhancements

### 16.1 **Machine Learning Model** (Phase 7)

- Train XGBoost model on historical recommendations
- Features: Greeks, news sentiment, technical indicators, seasonality
- Target: Predict probability of recommendation success
- Integration: Replace rule-based logic with ML predictions

### 16.2 **Multi-User Support** (Phase 8)

- Separate Redis cache per user
- User-specific recommendation preferences (risk tolerance)
- Social features: "See what other traders are doing"

### 16.3 **Mobile App** (Phase 9)

- Push notifications for urgent recommendations
- Swipe actions: "Accept", "Dismiss", "Snooze"
- Voice commands: "Alexa, what should I do with my NVDA put?"

---

## Appendix A: Code Examples

### A.1 **Complete Service Implementation Example**

```python
# src/services/position_recommendation_service.py

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from loguru import logger
import asyncio

from src.models.position_recommendation import (
    PositionRecommendation,
    RecommendationAction,
    RiskLevel
)
from src.services.greeks_analyzer import GreeksAnalyzer
from src.services.news_aggregator import NewsAggregator
from src.services.recovery_advisor import RecoveryAdvisor
from src.services.llm_reasoning_service import LLMReasoningService
from src.cache.redis_cache_manager import RedisCacheManager
from src.db.recommendation_db_manager import RecommendationDBManager

class PositionRecommendationService:
    """Main orchestrator for position-specific recommendations"""

    def __init__(self):
        self.greeks_analyzer = GreeksAnalyzer()
        self.news_aggregator = NewsAggregator()
        self.recovery_advisor = RecoveryAdvisor()
        self.llm_service = LLMReasoningService()
        self.cache = RedisCacheManager()
        self.db = RecommendationDBManager()

    def get_recommendations_batch(
        self,
        positions: List[Position],
        force_refresh: bool = False
    ) -> Dict[str, PositionRecommendation]:
        """
        Batch-fetch recommendations for multiple positions.

        Args:
            positions: List of Position objects from Robinhood
            force_refresh: Bypass cache and fetch fresh data

        Returns:
            Dict mapping position_id -> PositionRecommendation
        """
        logger.info(f"Fetching recommendations for {len(positions)} positions")

        # Step 1: Prioritize positions (losing positions first)
        sorted_positions = self._prioritize_positions(positions)

        # Step 2: Check cache
        if not force_refresh:
            cached = self._get_cached_recommendations([p.position_id for p in sorted_positions])
            uncached_positions = [p for p in sorted_positions if p.position_id not in cached]
        else:
            cached = {}
            uncached_positions = sorted_positions

        if not uncached_positions:
            logger.info(f"All {len(positions)} recommendations served from cache")
            return cached

        logger.info(f"Generating {len(uncached_positions)} fresh recommendations")

        # Step 3: Batch-fetch supporting data
        try:
            # Fetch Greeks for all positions in parallel
            greeks_batch = asyncio.run(self._fetch_greeks_batch(uncached_positions))

            # Fetch news for unique symbols
            unique_symbols = list(set([p.symbol for p in uncached_positions]))
            news_batch = asyncio.run(self._fetch_news_batch(unique_symbols))
        except Exception as e:
            logger.error(f"Error fetching batch data: {e}")
            # Fall back to cached data even if stale
            return self._get_stale_cache([p.position_id for p in positions])

        # Step 4: Generate recommendations
        fresh = {}
        for position in uncached_positions:
            try:
                rec = self._generate_single_recommendation(
                    position=position,
                    greeks=greeks_batch.get(position.symbol),
                    news=news_batch.get(position.symbol)
                )
                fresh[position.position_id] = rec

                # Store in cache with dynamic TTL
                ttl = self._calculate_cache_ttl(position)
                self.cache.set(position.position_id, rec, ttl=ttl)

                # Store in PostgreSQL for history
                self.db.insert_recommendation(rec)

            except Exception as e:
                logger.error(f"Error generating recommendation for {position.position_id}: {e}")
                # Use fallback
                fresh[position.position_id] = self._get_fallback_recommendation(position)

        # Step 5: Merge cached + fresh
        return {**cached, **fresh}

    def _generate_single_recommendation(
        self,
        position: Position,
        greeks: Optional[OptionsGreeks],
        news: Optional[NewsSummary]
    ) -> PositionRecommendation:
        """Generate recommendation for a single position"""

        # Get recovery strategy
        recovery = self.recovery_advisor.get_recovery_strategy(
            position=position,
            greeks=greeks,
            news=news
        )

        # Determine risk level
        risk_level = self._assess_risk_level(position, greeks)

        # Generate AI reasoning (for losing positions only)
        if position.pl_pct < -10 and greeks:
            try:
                detailed_reasoning = self.llm_service.generate_recommendation_reasoning(
                    position=position,
                    greeks=greeks,
                    news=news,
                    recovery=recovery
                )
            except Exception as e:
                logger.warning(f"LLM reasoning failed: {e}")
                detailed_reasoning = self._get_template_reasoning(position, recovery)
        else:
            detailed_reasoning = self._get_template_reasoning(position, recovery)

        # Create recommendation object
        return PositionRecommendation(
            position_id=position.position_id,
            symbol=position.symbol,
            action=recovery.action,
            risk_level=risk_level,
            confidence=self._calculate_confidence(position, greeks, news),
            short_summary=self._create_short_summary(recovery),
            detailed_reasoning=detailed_reasoning,
            greeks=greeks,
            news=news,
            recovery=recovery,
            generated_at=datetime.now(),
            cache_expires_at=datetime.now() + timedelta(minutes=15),
            data_freshness="real-time"
        )

    def _prioritize_positions(self, positions: List[Position]) -> List[Position]:
        """Sort positions by urgency"""
        def priority_score(p: Position) -> float:
            score = 0.0

            # Losing positions = higher priority
            if p.pl_pct < -20:
                score += 100
            elif p.pl_pct < -10:
                score += 50

            # Expiring soon = higher priority
            if p.dte <= 7:
                score += 30
            elif p.dte <= 14:
                score += 15

            # ITM positions = higher priority
            if p.option_type == 'put' and p.stock_price < p.strike:
                score += 20
            elif p.option_type == 'call' and p.stock_price > p.strike:
                score += 20

            return score

        return sorted(positions, key=priority_score, reverse=True)

    async def _fetch_greeks_batch(
        self,
        positions: List[Position]
    ) -> Dict[str, OptionsGreeks]:
        """Fetch Greeks for all positions in parallel"""
        tasks = []
        for pos in positions:
            task = self.greeks_analyzer.fetch_greeks_async(
                symbol=pos.symbol,
                strike=pos.strike,
                expiration=pos.expiration,
                option_type=pos.option_type
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        greeks_map = {}
        for pos, result in zip(positions, results):
            if isinstance(result, Exception):
                logger.warning(f"Greeks fetch failed for {pos.symbol}: {result}")
                greeks_map[pos.symbol] = None
            else:
                greeks_map[pos.symbol] = result

        return greeks_map

    # ... (additional helper methods)
```

---

## Appendix B: Database Queries

### B.1 **Get Recommendation History**

```sql
-- Get all recommendations for a position
SELECT
    r.generated_at,
    r.action,
    r.risk_level,
    r.confidence,
    r.short_summary,
    r.user_action,
    r.final_pnl
FROM position_recommendations r
WHERE r.position_id = 'NVDA-180P-2025-12-15'
ORDER BY r.generated_at DESC
LIMIT 10;
```

### B.2 **Calculate Recommendation Accuracy**

```sql
-- Calculate accuracy: Did recommendation improve P/L?
SELECT
    action,
    COUNT(*) as total_recommendations,
    COUNT(CASE WHEN recommendation_accuracy > 0.7 THEN 1 END) as accurate_recommendations,
    ROUND(
        COUNT(CASE WHEN recommendation_accuracy > 0.7 THEN 1 END)::decimal / COUNT(*) * 100,
        2
    ) as accuracy_pct
FROM position_recommendations
WHERE position_closed_at IS NOT NULL
GROUP BY action
ORDER BY accuracy_pct DESC;
```

### B.3 **Find Best Recovery Strategies**

```sql
-- Which recovery strategies are most profitable?
SELECT
    r.recovery_data->>'action' as recovery_action,
    COUNT(*) as times_recommended,
    COUNT(CASE WHEN r.user_action IS NOT NULL THEN 1 END) as times_executed,
    AVG(r.final_pnl) as avg_pnl,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY r.final_pnl) as median_pnl
FROM position_recommendations r
WHERE r.position_closed_at IS NOT NULL
    AND r.recovery_data IS NOT NULL
GROUP BY r.recovery_data->>'action'
ORDER BY avg_pnl DESC;
```

---

## Appendix C: Testing Strategy

### C.1 **Unit Tests**

```python
# tests/test_position_recommendation_service.py

import pytest
from src.services.position_recommendation_service import PositionRecommendationService
from src.models.position_recommendation import Position, OptionsGreeks

def test_generate_recommendation_for_losing_csp():
    """Test recommendation for losing CSP position"""
    service = PositionRecommendationService()

    position = Position(
        position_id="TEST-180P",
        symbol="NVDA",
        strike=180.0,
        expiration=datetime(2025, 12, 15),
        option_type="put",
        position_type="short",
        pl_pct=-15.5,
        dte=12
    )

    greeks = OptionsGreeks(
        delta=-0.65,
        theta=-0.25,
        gamma=0.05,
        vega=0.30,
        iv=45.0,
        updated_at=datetime.now()
    )

    rec = service._generate_single_recommendation(position, greeks, None)

    assert rec.action in [RecommendationAction.ROLL_DOWN, RecommendationAction.ROLL_OUT]
    assert rec.risk_level == RiskLevel.HIGH
    assert rec.confidence > 0.5
```

### C.2 **Integration Tests**

```python
# tests/integration/test_recommendation_flow.py

@pytest.mark.integration
async def test_full_recommendation_flow():
    """Test end-to-end recommendation generation"""
    service = PositionRecommendationService()

    # Mock positions
    positions = [create_test_position() for _ in range(5)]

    # Generate recommendations
    recommendations = service.get_recommendations_batch(positions)

    assert len(recommendations) == 5
    for rec in recommendations.values():
        assert rec.action is not None
        assert 0.0 <= rec.confidence <= 1.0
        assert rec.greeks is not None
```

### C.3 **Performance Tests**

```python
# tests/performance/test_latency.py

@pytest.mark.performance
def test_recommendation_latency():
    """Test recommendation generation speed"""
    import time

    service = PositionRecommendationService()
    positions = [create_test_position() for _ in range(20)]

    start = time.time()
    recommendations = service.get_recommendations_batch(positions)
    elapsed = time.time() - start

    assert elapsed < 3.0, f"Recommendation generation took {elapsed:.2f}s (target: < 3s)"
    assert len(recommendations) == 20
```

---

**End of Architecture Document**

---

**Next Steps:**
1. Review and approve this architecture
2. Create detailed implementation tickets for each phase
3. Set up development environment (Redis, test database)
4. Begin Phase 1 implementation (Core Infrastructure)
5. Schedule weekly progress reviews

**Contact:**
For questions or clarifications, contact the Backend Architect agent.
