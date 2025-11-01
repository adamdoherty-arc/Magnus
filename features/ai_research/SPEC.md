# AI Research Assistant - Specifications

## API Specifications

### Endpoints

#### GET /api/research/{symbol}
**Description**: Retrieve AI-powered research analysis for a stock symbol

**Parameters**:
- `symbol` (path, required): Stock ticker symbol (e.g., "AAPL")
- `force_refresh` (query, optional): Boolean, bypass cache (default: false)
- `user_position` (query, optional): JSON string describing user's position

**Response** (200 OK):
```json
{
  "symbol": "AAPL",
  "timestamp": "2025-11-01T14:30:00Z",
  "cached": false,
  "analysis": {
    "overall_rating": 4.0,
    "quick_summary": "Strong fundamentals with neutral technical setup. Good for premium selling strategies.",
    "fundamental": {
      "score": 85,
      "revenue_growth_yoy": 0.12,
      "earnings_beat_streak": 4,
      "pe_ratio": 28.5,
      "sector_avg_pe": 25.0,
      "valuation_assessment": "Slight premium to sector",
      "key_strengths": [
        "Consistent revenue growth",
        "Strong brand moat",
        "Healthy cash flow"
      ],
      "key_risks": [
        "Premium valuation",
        "Regulatory scrutiny"
      ]
    },
    "technical": {
      "score": 60,
      "trend": "sideways",
      "rsi": 52,
      "macd_signal": "neutral",
      "support_levels": [170, 165],
      "resistance_levels": [180, 185],
      "chart_patterns": [],
      "recommendation": "Neutral technical setup, range-bound"
    },
    "sentiment": {
      "score": 75,
      "news_sentiment": "positive",
      "news_count_7d": 15,
      "social_sentiment": "neutral",
      "reddit_mentions_24h": 234,
      "institutional_flow": "moderate_buying",
      "insider_trades": [],
      "analyst_rating": "buy",
      "analyst_consensus": {
        "strong_buy": 8,
        "buy": 12,
        "hold": 5,
        "sell": 1,
        "strong_sell": 0
      }
    },
    "options": {
      "iv_rank": 45,
      "iv_percentile": 62,
      "current_iv": 0.28,
      "iv_mean_30d": 0.26,
      "next_earnings_date": "2025-11-24",
      "days_to_earnings": 23,
      "avg_earnings_move": 0.04,
      "unusual_options_activity": [],
      "recommended_strategies": [
        {
          "strategy": "cash_secured_put",
          "strike": 170,
          "expiration": "2025-11-15",
          "premium": 2.50,
          "pop": 68,
          "rationale": "Moderate IV, strong support at $170"
        }
      ]
    },
    "recommendation": {
      "action": "HOLD",
      "confidence": 0.78,
      "reasoning": "Strong fundamentals support current price levels. IV is moderate, suitable for premium selling. No immediate catalysts.",
      "time_sensitive_factors": [
        "Earnings announcement in 23 days may increase volatility"
      ],
      "specific_position_advice": {
        "cash_secured_put": "Good position. Stock trading above strike with solid support. Consider rolling up/out for more premium if desired.",
        "covered_call": "Moderate assignment risk. Consider rolling out if you want to keep shares.",
        "long_stock": "Fair entry point. Set stops at $165 support."
      }
    }
  },
  "metadata": {
    "api_calls_used": 8,
    "processing_time_ms": 2847,
    "agents_executed": 4,
    "cache_expires_at": "2025-11-01T15:00:00Z"
  }
}
```

**Error Responses**:
```json
// 400 Bad Request
{
  "error": "Invalid symbol format",
  "detail": "Symbol must be 1-5 alphanumeric characters"
}

// 404 Not Found
{
  "error": "Symbol not found",
  "detail": "No data available for symbol XYZ",
  "suggestions": ["XYZA", "XYZ.TO"]
}

// 429 Too Many Requests
{
  "error": "Rate limit exceeded",
  "detail": "Maximum 10 requests per minute",
  "retry_after_seconds": 45
}

// 503 Service Unavailable
{
  "error": "External API unavailable",
  "detail": "Alpha Vantage API temporarily unavailable",
  "cached_data_available": true,
  "cached_data_age_hours": 2
}
```

---

#### GET /api/research/{symbol}/refresh
**Description**: Force refresh analysis, bypassing cache

**Parameters**:
- `symbol` (path, required): Stock ticker symbol

**Response**: Same as GET /api/research/{symbol} with `cached: false`

---

## Data Models

### ResearchReport
```python
@dataclass
class ResearchReport:
    symbol: str
    timestamp: datetime
    overall_rating: float  # 1.0 - 5.0
    quick_summary: str
    fundamental: FundamentalAnalysis
    technical: TechnicalAnalysis
    sentiment: SentimentAnalysis
    options: OptionsAnalysis
    recommendation: TradeRecommendation
    metadata: AnalysisMetadata
```

### FundamentalAnalysis
```python
@dataclass
class FundamentalAnalysis:
    score: int  # 0-100
    revenue_growth_yoy: float
    earnings_beat_streak: int
    pe_ratio: float
    sector_avg_pe: float
    pb_ratio: float
    debt_to_equity: float
    roe: float
    free_cash_flow: float
    dividend_yield: float
    valuation_assessment: str
    key_strengths: List[str]
    key_risks: List[str]
```

### TechnicalAnalysis
```python
@dataclass
class TechnicalAnalysis:
    score: int  # 0-100
    trend: Literal['uptrend', 'downtrend', 'sideways']
    rsi: float  # 0-100
    macd_signal: Literal['bullish', 'bearish', 'neutral']
    support_levels: List[float]
    resistance_levels: List[float]
    moving_averages: Dict[str, float]  # {'MA50': 172.5, 'MA200': 165.0}
    bollinger_bands: Dict[str, float]
    volume_analysis: str
    chart_patterns: List[str]
    recommendation: str
```

### SentimentAnalysis
```python
@dataclass
class SentimentAnalysis:
    score: int  # 0-100
    news_sentiment: Literal['positive', 'negative', 'neutral']
    news_count_7d: int
    social_sentiment: Literal['positive', 'negative', 'neutral']
    reddit_mentions_24h: int
    stocktwits_sentiment: float  # -1.0 to 1.0
    institutional_flow: Literal['heavy_buying', 'moderate_buying', 'neutral', 'moderate_selling', 'heavy_selling']
    insider_trades: List[InsiderTrade]
    analyst_rating: Literal['strong_buy', 'buy', 'hold', 'sell', 'strong_sell']
    analyst_consensus: AnalystConsensus
```

### OptionsAnalysis
```python
@dataclass
class OptionsAnalysis:
    iv_rank: int  # 0-100
    iv_percentile: int  # 0-100
    current_iv: float
    iv_mean_30d: float
    iv_std_30d: float
    next_earnings_date: str
    days_to_earnings: int
    avg_earnings_move: float  # 0.0-1.0 (percentage)
    put_call_ratio: float
    max_pain: float
    unusual_options_activity: List[UnusualActivity]
    recommended_strategies: List[StrategyRecommendation]
```

### TradeRecommendation
```python
@dataclass
class TradeRecommendation:
    action: Literal['STRONG_BUY', 'BUY', 'HOLD', 'SELL', 'STRONG_SELL']
    confidence: float  # 0.0-1.0
    reasoning: str
    time_sensitive_factors: List[str]
    specific_position_advice: Dict[str, str]
    suggested_adjustments: List[str]
```

---

## Agent Specifications

### Fundamental Analyst Agent

**Name**: `fundamental_analyst`
**Role**: Financial analyst specializing in fundamental analysis
**Goal**: Assess company financial health and valuation
**Backstory**: Expert in reading financial statements, calculating valuation metrics, and analyzing competitive positioning

**Tools**:
- `AlphaVantageFinancialsTool`
- `YFinanceFinancialsTool`
- `CompanyOverviewTool`

**Output Schema**: `FundamentalAnalysis`

---

### Technical Analyst Agent

**Name**: `technical_analyst`
**Role**: Chart analyst and technical trader
**Goal**: Identify technical patterns, trends, and key price levels
**Backstory**: 20 years experience in technical analysis, specializes in momentum and mean reversion strategies

**Tools**:
- `YFinancePriceTool`
- `TechnicalIndicatorsTool`
- `ChartPatternRecognitionTool`

**Output Schema**: `TechnicalAnalysis`

---

### Sentiment Analyst Agent

**Name**: `sentiment_analyst`
**Role**: Market sentiment and news analyst
**Goal**: Gauge market sentiment from news, social media, and institutional activity
**Backstory**: Former hedge fund analyst specializing in alternative data and sentiment analysis

**Tools**:
- `RedditSentimentTool`
- `NewsAPITool`
- `InsiderTradingTool`
- `AnalystRatingsTool`

**Output Schema**: `SentimentAnalysis`

---

### Options Strategist Agent

**Name**: `options_strategist`
**Role**: Options trader and strategist
**Goal**: Analyze options market and recommend optimal strategies
**Backstory**: Professional options trader with expertise in volatility trading and Greeks

**Tools**:
- `YFinanceOptionsChainTool`
- `IVCalculatorTool`
- `GreeksCalculatorTool`
- `ProbabilityCalculatorTool`

**Output Schema**: `OptionsAnalysis`

---

## Scoring Rubrics

### Fundamental Score (0-100)

| Metric | Weight | Scoring |
|--------|--------|---------|
| Revenue Growth | 20% | YoY >15% = 20, 10-15% = 15, 5-10% = 10, <5% = 5 |
| Earnings Growth | 20% | Beat streak >4 = 20, 3-4 = 15, 1-2 = 10, miss = 0 |
| Valuation | 20% | P/E vs sector: below = 20, inline = 15, 10% premium = 10, >20% premium = 5 |
| Profitability | 15% | ROE >20% = 15, 15-20% = 10, 10-15% = 7, <10% = 3 |
| Balance Sheet | 15% | D/E <0.5 = 15, 0.5-1.0 = 10, 1.0-2.0 = 5, >2.0 = 0 |
| Dividend | 10% | Yield >3% = 10, 2-3% = 7, 1-2% = 5, <1% = 3, none = 0 |

---

### Technical Score (0-100)

| Metric | Weight | Scoring |
|--------|--------|---------|
| Trend Strength | 25% | Strong up = 25, moderate up = 20, sideways = 15, moderate down = 10, strong down = 5 |
| RSI | 20% | 50-60 = 20, 40-50 or 60-70 = 15, 30-40 or 70-80 = 10, <30 or >80 = 5 |
| MACD | 20% | Bullish cross = 20, above signal = 15, neutral = 10, below signal = 5, bearish cross = 0 |
| Moving Averages | 15% | Above all MAs = 15, above 50 = 10, below 50 above 200 = 5, below all = 0 |
| Bollinger Bands | 10% | Middle = 10, upper half = 7, lower half = 7, at bands = 5 |
| Volume | 10% | Above avg with trend = 10, above avg against = 5, below avg = 3 |

---

### Sentiment Score (0-100)

| Metric | Weight | Scoring |
|--------|--------|---------|
| News Sentiment | 30% | Strongly positive = 30, positive = 25, neutral = 15, negative = 10, strongly negative = 0 |
| Social Media | 25% | Bullish >70% = 25, bullish 60-70% = 20, neutral = 15, bearish 60-70% = 10, bearish >70% = 5 |
| Institutional Flow | 20% | Heavy buying = 20, moderate buying = 17, neutral = 10, moderate selling = 7, heavy selling = 0 |
| Analyst Ratings | 15% | Strong buy consensus = 15, buy = 12, hold = 8, sell = 4, strong sell = 0 |
| Insider Trading | 10% | Significant buying = 10, minor buying = 7, none = 5, minor selling = 3, significant selling = 0 |

---

## Caching Rules

### Cache Key Structure
```
research:{symbol}:{version}
```

### TTL Rules
| Market Status | TTL | Reason |
|--------------|-----|--------|
| Pre-market (4:00-9:30 AM ET) | 15 min | Prices changing, moderate refresh |
| Market hours (9:30 AM-4:00 PM ET) | 30 min | Active trading, regular refresh |
| After-hours (4:00-8:00 PM ET) | 1 hour | Less volatility, slower refresh |
| Closed (8:00 PM-4:00 AM ET) | 24 hours | Static data, minimal refresh |

### Cache Invalidation Triggers
1. Manual refresh request
2. TTL expiration
3. Earnings announcement detected
4. Major news event (>10 articles in 1 hour)

---

## Rate Limiting

### Internal Rate Limits
- 10 requests/minute per user
- 100 requests/hour per user
- 1000 requests/day per user

### External API Limits
| API | Limit | Handling |
|-----|-------|----------|
| Alpha Vantage | 500/day | Queue requests, spread over 24 hours |
| Reddit | 60/minute | Batch requests, use praw library |
| yfinance | Unlimited | No special handling |
| Groq | 30/minute | Use queue, fallback to Ollama |

---

## Performance Requirements

| Metric | Target | Maximum |
|--------|--------|---------|
| Cache Hit Response Time | <100ms | <500ms |
| Cache Miss Response Time | <5s | <30s |
| Concurrent Users | 50 | 100 |
| Cache Hit Rate | >80% | >60% |
| API Error Rate | <1% | <5% |

---

## Security Requirements

- API keys stored in environment variables only
- Input validation on all endpoints
- Rate limiting per IP and user
- SQL injection prevention (parameterized queries)
- XSS prevention (sanitize outputs)
- HTTPS only in production
- Audit logging of all research requests

---

**Version**: 1.0.0
**Last Updated**: 2025-11-01
