"""
Data Models for AI Research Assistant
Defines all data structures used by specialist agents and orchestrator
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Literal
from enum import Enum


# Enums
class TrendDirection(str, Enum):
    UPTREND = "uptrend"
    DOWNTREND = "downtrend"
    SIDEWAYS = "sideways"


class SignalType(str, Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"


class SentimentType(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class InstitutionalFlow(str, Enum):
    HEAVY_BUYING = "heavy_buying"
    MODERATE_BUYING = "moderate_buying"
    NEUTRAL = "neutral"
    MODERATE_SELLING = "moderate_selling"
    HEAVY_SELLING = "heavy_selling"


class AnalystRating(str, Enum):
    STRONG_BUY = "strong_buy"
    BUY = "buy"
    HOLD = "hold"
    SELL = "sell"
    STRONG_SELL = "strong_sell"


class TradeAction(str, Enum):
    STRONG_BUY = "STRONG_BUY"
    BUY = "BUY"
    HOLD = "HOLD"
    SELL = "SELL"
    STRONG_SELL = "STRONG_SELL"


# Fundamental Analysis
@dataclass
class FundamentalAnalysis:
    """Fundamental analysis results from Fundamental Analyst Agent"""
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
    next_earnings_date: Optional[str] = None
    analyst_estimates: Optional[Dict[str, float]] = None


# Technical Analysis
@dataclass
class TechnicalAnalysis:
    """Technical analysis results from Technical Analyst Agent"""
    score: int  # 0-100
    trend: TrendDirection
    rsi: float  # 0-100
    macd_signal: SignalType
    support_levels: List[float]
    resistance_levels: List[float]
    moving_averages: Dict[str, float]  # {'MA50': 172.5, 'MA200': 165.0}
    bollinger_bands: Dict[str, float]  # {'upper': 180, 'middle': 175, 'lower': 170}
    volume_analysis: str
    chart_patterns: List[str]
    recommendation: str


# Sentiment Analysis
@dataclass
class InsiderTrade:
    """Individual insider trading transaction"""
    date: str
    insider_name: str
    transaction_type: Literal['buy', 'sell']
    shares: int
    price: float
    value: float


@dataclass
class AnalystConsensus:
    """Analyst rating consensus"""
    strong_buy: int
    buy: int
    hold: int
    sell: int
    strong_sell: int

    @property
    def total(self) -> int:
        return self.strong_buy + self.buy + self.hold + self.sell + self.strong_sell

    @property
    def average_rating(self) -> float:
        """Calculate average rating (1=Strong Buy, 5=Strong Sell)"""
        if self.total == 0:
            return 3.0  # Neutral
        weighted = (
            self.strong_buy * 1 +
            self.buy * 2 +
            self.hold * 3 +
            self.sell * 4 +
            self.strong_sell * 5
        )
        return weighted / self.total


@dataclass
class SentimentAnalysis:
    """Sentiment analysis results from Sentiment Analyst Agent"""
    score: int  # 0-100
    news_sentiment: SentimentType
    news_count_7d: int
    social_sentiment: SentimentType
    reddit_mentions_24h: int
    stocktwits_sentiment: float  # -1.0 to 1.0
    institutional_flow: InstitutionalFlow
    insider_trades: List[InsiderTrade]
    analyst_rating: AnalystRating
    analyst_consensus: AnalystConsensus


# Options Analysis
@dataclass
class UnusualActivity:
    """Unusual options activity detection"""
    date: str
    option_type: Literal['call', 'put']
    strike: float
    expiration: str
    volume: int
    open_interest: int
    volume_oi_ratio: float
    premium: float
    description: str


@dataclass
class StrategyRecommendation:
    """Recommended options strategy"""
    strategy: str  # 'cash_secured_put', 'covered_call', 'iron_condor', etc.
    strike: float
    expiration: str
    premium: float
    probability_of_profit: float  # 0.0-1.0
    max_profit: float
    max_loss: float
    rationale: str


@dataclass
class OptionsAnalysis:
    """Options analysis results from Options Strategist Agent"""
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


# Trade Recommendation
@dataclass
class TradeRecommendation:
    """Final trade recommendation from orchestrator"""
    action: TradeAction
    confidence: float  # 0.0-1.0
    reasoning: str
    time_sensitive_factors: List[str]
    specific_position_advice: Dict[str, str]  # {'cash_secured_put': 'advice...'}
    suggested_adjustments: List[str]


# Analysis Metadata
@dataclass
class AnalysisMetadata:
    """Metadata about the analysis process"""
    api_calls_used: int
    processing_time_ms: int
    agents_executed: int
    agents_failed: List[str]
    cache_expires_at: datetime
    llm_model: str
    llm_tokens_used: int


# Main Research Report
@dataclass
class ResearchReport:
    """Complete AI research report combining all agent outputs"""
    symbol: str
    timestamp: datetime
    cached: bool
    overall_rating: float  # 1.0 - 5.0 stars
    quick_summary: str

    fundamental: FundamentalAnalysis
    technical: TechnicalAnalysis
    sentiment: SentimentAnalysis
    options: OptionsAnalysis
    recommendation: TradeRecommendation
    metadata: AnalysisMetadata

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'symbol': self.symbol,
            'timestamp': self.timestamp.isoformat(),
            'cached': self.cached,
            'overall_rating': self.overall_rating,
            'quick_summary': self.quick_summary,
            'analysis': {
                'fundamental': self.fundamental.__dict__,
                'technical': {
                    **self.technical.__dict__,
                    'trend': self.technical.trend.value,
                    'macd_signal': self.technical.macd_signal.value
                },
                'sentiment': {
                    **self.sentiment.__dict__,
                    'news_sentiment': self.sentiment.news_sentiment.value,
                    'social_sentiment': self.sentiment.social_sentiment.value,
                    'institutional_flow': self.sentiment.institutional_flow.value,
                    'analyst_rating': self.sentiment.analyst_rating.value,
                    'insider_trades': [t.__dict__ for t in self.sentiment.insider_trades],
                    'analyst_consensus': self.sentiment.analyst_consensus.__dict__
                },
                'options': {
                    **self.options.__dict__,
                    'unusual_options_activity': [u.__dict__ for u in self.options.unusual_options_activity],
                    'recommended_strategies': [s.__dict__ for s in self.options.recommended_strategies]
                },
                'recommendation': {
                    **self.recommendation.__dict__,
                    'action': self.recommendation.action.value
                }
            },
            'metadata': {
                **self.metadata.__dict__,
                'cache_expires_at': self.metadata.cache_expires_at.isoformat()
            }
        }


# Request Models
@dataclass
class Position:
    """User's current position for context-aware analysis"""
    symbol: str
    position_type: Literal['stock', 'cash_secured_put', 'covered_call', 'long_call', 'long_put']
    quantity: int
    entry_price: float
    current_price: float
    strike: Optional[float] = None
    expiration: Optional[str] = None


@dataclass
class ResearchRequest:
    """Request for AI research"""
    symbol: str
    user_position: Optional[Position] = None
    force_refresh: bool = False
    include_sections: List[str] = field(default_factory=lambda: ['fundamental', 'technical', 'sentiment', 'options'])


# Error Models
@dataclass
class ErrorResponse:
    """Error response from API"""
    error_code: str
    error_message: str
    failed_components: List[str]
    fallback_used: bool
    cached_data_available: bool
    retry_after_seconds: Optional[int] = None
