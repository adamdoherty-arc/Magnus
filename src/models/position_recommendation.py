"""
Position Recommendation Data Models
====================================

Core dataclasses for the position-specific recommendation engine.

Usage:
    from src.models.position_recommendation import PositionRecommendation, Position

    rec = PositionRecommendation(
        position_id="NVDA-180P-2025-12-15",
        symbol="NVDA",
        action=RecommendationAction.ROLL_DOWN,
        risk_level=RiskLevel.HIGH,
        confidence=0.85,
        short_summary="Roll to $175 strike (+$45 credit)",
        detailed_reasoning="Position is down 15% with 12 DTE..."
    )
"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
from enum import Enum


# =============================================================================
# Enums
# =============================================================================

class RecommendationAction(Enum):
    """Available recommendation actions"""
    HOLD = "HOLD"
    ROLL_OUT = "ROLL_OUT"                    # Extend expiration, same strike
    ROLL_DOWN = "ROLL_DOWN"                  # Lower strike, same expiration
    ROLL_DOWN_OUT = "ROLL_DOWN_OUT"          # Lower strike + extend expiration
    ROLL_UP = "ROLL_UP"                      # Higher strike (for covered calls)
    ROLL_UP_OUT = "ROLL_UP_OUT"              # Higher strike + extend expiration
    CLOSE = "CLOSE"                          # Exit position immediately
    ADD_HEDGE = "ADD_HEDGE"                  # Buy protective option
    CONVERT_SPREAD = "CONVERT_SPREAD"        # Turn single leg into spread
    TAKE_ASSIGNMENT = "TAKE_ASSIGNMENT"      # Let position be assigned (CSPs)
    WAIT_EXPIRATION = "WAIT_EXPIRATION"      # Hold through expiration (OTM)


class RiskLevel(Enum):
    """Position risk assessment"""
    LOW = "LOW"           # P/L healthy, low assignment risk
    MEDIUM = "MEDIUM"     # Breakeven or slight loss
    HIGH = "HIGH"         # Significant loss or near assignment
    CRITICAL = "CRITICAL" # Deep ITM, assignment imminent


class PositionStatus(Enum):
    """Position state"""
    WINNING = "WINNING"   # P/L > 5%
    BREAKEVEN = "BREAKEVEN"  # P/L between -5% and +5%
    LOSING = "LOSING"     # P/L < -5%
    CRITICAL = "CRITICAL" # P/L < -20% or DTE < 7


class SentimentType(Enum):
    """News sentiment classification"""
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"


# =============================================================================
# Core Data Models
# =============================================================================

@dataclass
class Position:
    """
    Represents a single options position from Robinhood.

    Attributes:
        position_id: Unique identifier (symbol-strike-type-expiration)
        symbol: Stock ticker symbol
        strike: Option strike price
        expiration: Expiration date
        option_type: 'put' or 'call'
        position_type: 'short' or 'long'
        quantity: Number of contracts
        avg_price: Average entry price (per contract, in dollars)
        current_price: Current market price (per contract, in dollars)
        pl: Profit/Loss in dollars
        pl_pct: Profit/Loss percentage
        dte: Days to expiration
        stock_price: Current underlying stock price
    """
    position_id: str
    symbol: str
    strike: float
    expiration: datetime
    option_type: str  # 'put' or 'call'
    position_type: str  # 'short' or 'long'
    quantity: int
    avg_price: float
    current_price: float
    pl: float
    pl_pct: float
    dte: int
    stock_price: float = 0.0

    @property
    def status(self) -> PositionStatus:
        """Calculate position status based on P/L"""
        if self.pl_pct < -20 or self.dte < 7:
            return PositionStatus.CRITICAL
        elif self.pl_pct < -5:
            return PositionStatus.LOSING
        elif self.pl_pct > 5:
            return PositionStatus.WINNING
        else:
            return PositionStatus.BREAKEVEN

    @property
    def is_itm(self) -> bool:
        """Check if option is in-the-money"""
        if self.option_type == 'put':
            return self.stock_price < self.strike
        else:  # call
            return self.stock_price > self.strike

    @property
    def moneyness(self) -> str:
        """Return moneyness: ITM, ATM, or OTM"""
        if self.option_type == 'put':
            if self.stock_price < self.strike * 0.95:
                return "ITM"
            elif self.stock_price < self.strike * 1.05:
                return "ATM"
            else:
                return "OTM"
        else:  # call
            if self.stock_price > self.strike * 1.05:
                return "ITM"
            elif self.stock_price > self.strike * 0.95:
                return "ATM"
            else:
                return "OTM"


@dataclass
class OptionsGreeks:
    """
    Options Greeks and implied volatility.

    Attributes:
        delta: Sensitivity to stock price change (-1 to 1)
        theta: Daily time decay ($/day, usually negative for buyers)
        gamma: Rate of change of delta
        vega: Sensitivity to IV changes
        iv: Implied volatility (percentage, e.g., 45.0 for 45%)
        updated_at: Timestamp of data fetch
    """
    delta: float
    theta: float
    gamma: float
    vega: float
    iv: float
    updated_at: datetime

    @property
    def assignment_risk(self) -> str:
        """Estimate assignment risk based on delta"""
        abs_delta = abs(self.delta)

        if abs_delta < 0.30:
            return "LOW"
        elif abs_delta < 0.50:
            return "MEDIUM"
        elif abs_delta < 0.70:
            return "HIGH"
        else:
            return "CRITICAL"

    @property
    def theta_decay_quality(self) -> str:
        """Rate theta decay (for premium sellers)"""
        abs_theta = abs(self.theta)

        if abs_theta > 5.0:
            return "EXCELLENT"
        elif abs_theta > 2.0:
            return "GOOD"
        elif abs_theta > 0.5:
            return "MODERATE"
        else:
            return "POOR"


@dataclass
class NewsArticle:
    """Individual news article"""
    headline: str
    source: str
    url: str
    published_at: datetime
    summary: str
    sentiment_score: float = 0.0  # -1.0 (bearish) to +1.0 (bullish)


@dataclass
class NewsSummary:
    """
    Aggregated news analysis for a symbol.

    Attributes:
        sentiment: Overall sentiment (BULLISH, BEARISH, NEUTRAL)
        key_events: List of important events extracted from headlines
        impact_score: 0.0 to 1.0, higher = more significant news
        latest_headline: Most recent headline
        articles: Full list of articles (optional)
    """
    sentiment: SentimentType
    key_events: List[str]
    impact_score: float  # 0.0 to 1.0
    latest_headline: Optional[str] = None
    articles: List[NewsArticle] = field(default_factory=list)

    @property
    def has_high_impact_news(self) -> bool:
        """Check if there's high-impact news"""
        return self.impact_score > 0.7

    @property
    def is_bullish(self) -> bool:
        """Check if sentiment is bullish"""
        return self.sentiment == SentimentType.BULLISH

    @property
    def is_bearish(self) -> bool:
        """Check if sentiment is bearish"""
        return self.sentiment == SentimentType.BEARISH


@dataclass
class RollOpportunity:
    """
    Potential roll target for an option position.

    Attributes:
        target_strike: New strike price
        target_expiration: New expiration date
        expected_credit: Net credit/debit from roll (positive = credit)
        dte: Days to expiration of new option
        delta: Delta of new option
        premium: Premium of new option
        probability_profit: Estimated probability of profit
    """
    target_strike: float
    target_expiration: datetime
    expected_credit: float
    dte: int
    delta: float
    premium: float
    probability_profit: float = 0.0

    @property
    def is_credit_roll(self) -> bool:
        """Check if this is a credit roll (positive expected credit)"""
        return self.expected_credit > 0

    @property
    def strike_adjustment_pct(self) -> float:
        """Calculate percentage change in strike"""
        # This will be set by RecoveryAdvisor based on current strike
        return 0.0


@dataclass
class RecoveryStrategy:
    """
    Recommended recovery action for a position.

    Attributes:
        action: Recommended action (HOLD, ROLL_DOWN, etc.)
        target_strike: New strike price (if rolling)
        target_expiration: New expiration (if rolling)
        expected_credit: Expected credit from action
        reasoning: Explanation of why this action is recommended
        alternatives: List of alternative roll opportunities
    """
    action: RecommendationAction
    reasoning: str
    target_strike: Optional[float] = None
    target_expiration: Optional[datetime] = None
    expected_credit: Optional[float] = None
    alternatives: List[RollOpportunity] = field(default_factory=list)

    @property
    def is_action_required(self) -> bool:
        """Check if action is needed (not HOLD or WAIT)"""
        return self.action not in [
            RecommendationAction.HOLD,
            RecommendationAction.WAIT_EXPIRATION
        ]


@dataclass
class PositionRecommendation:
    """
    Complete recommendation for a single position.

    This is the primary output of the recommendation engine.

    Attributes:
        position_id: Unique position identifier
        symbol: Stock ticker symbol
        action: Recommended action
        risk_level: Current risk assessment
        confidence: Confidence score (0.0 to 1.0)
        short_summary: Brief recommendation (e.g., "Roll to $175 (+$45 credit)")
        detailed_reasoning: Full explanation (2-3 sentences)
        greeks: Options Greeks data (if available)
        news: News summary (if available)
        recovery: Recovery strategy details (if applicable)
        generated_at: Timestamp of recommendation generation
        cache_expires_at: When cached recommendation expires
        data_freshness: Data quality indicator
    """
    position_id: str
    symbol: str
    action: RecommendationAction
    risk_level: RiskLevel
    confidence: float  # 0.0 to 1.0
    short_summary: str
    detailed_reasoning: str

    # Supporting data
    greeks: Optional[OptionsGreeks] = None
    news: Optional[NewsSummary] = None
    recovery: Optional[RecoveryStrategy] = None

    # Metadata
    generated_at: datetime = field(default_factory=datetime.now)
    cache_expires_at: Optional[datetime] = None
    data_freshness: str = "real-time"  # 'real-time', 'cached-Xm', 'stale'

    # User tracking (populated after user acts)
    user_action: Optional[str] = None
    user_action_timestamp: Optional[datetime] = None

    # Outcome tracking (populated after position closes)
    position_closed_at: Optional[datetime] = None
    final_pnl: Optional[float] = None
    recommendation_accuracy: Optional[float] = None

    def __post_init__(self):
        """Validate recommendation data"""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {self.confidence}")

        if self.cache_expires_at is None:
            # Default to 15 minutes cache
            from datetime import timedelta
            self.cache_expires_at = self.generated_at + timedelta(minutes=15)

    @property
    def is_urgent(self) -> bool:
        """Check if recommendation requires immediate attention"""
        return self.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]

    @property
    def cache_ttl_seconds(self) -> int:
        """Calculate remaining cache TTL in seconds"""
        if self.cache_expires_at is None:
            return 0

        remaining = (self.cache_expires_at - datetime.now()).total_seconds()
        return max(0, int(remaining))

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'position_id': self.position_id,
            'symbol': self.symbol,
            'action': self.action.value,
            'risk_level': self.risk_level.value,
            'confidence': self.confidence,
            'short_summary': self.short_summary,
            'detailed_reasoning': self.detailed_reasoning,
            'greeks': {
                'delta': self.greeks.delta,
                'theta': self.greeks.theta,
                'gamma': self.greeks.gamma,
                'vega': self.greeks.vega,
                'iv': self.greeks.iv,
                'updated_at': self.greeks.updated_at.isoformat()
            } if self.greeks else None,
            'news': {
                'sentiment': self.news.sentiment.value,
                'key_events': self.news.key_events,
                'impact_score': self.news.impact_score,
                'latest_headline': self.news.latest_headline
            } if self.news else None,
            'recovery': {
                'action': self.recovery.action.value,
                'target_strike': self.recovery.target_strike,
                'target_expiration': self.recovery.target_expiration.isoformat() if self.recovery.target_expiration else None,
                'expected_credit': self.recovery.expected_credit,
                'reasoning': self.recovery.reasoning
            } if self.recovery else None,
            'generated_at': self.generated_at.isoformat(),
            'cache_expires_at': self.cache_expires_at.isoformat() if self.cache_expires_at else None,
            'data_freshness': self.data_freshness
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'PositionRecommendation':
        """Create PositionRecommendation from dictionary"""
        # Parse nested objects
        greeks = None
        if data.get('greeks'):
            greeks = OptionsGreeks(
                delta=data['greeks']['delta'],
                theta=data['greeks']['theta'],
                gamma=data['greeks']['gamma'],
                vega=data['greeks']['vega'],
                iv=data['greeks']['iv'],
                updated_at=datetime.fromisoformat(data['greeks']['updated_at'])
            )

        news = None
        if data.get('news'):
            news = NewsSummary(
                sentiment=SentimentType(data['news']['sentiment']),
                key_events=data['news']['key_events'],
                impact_score=data['news']['impact_score'],
                latest_headline=data['news'].get('latest_headline')
            )

        recovery = None
        if data.get('recovery'):
            recovery = RecoveryStrategy(
                action=RecommendationAction(data['recovery']['action']),
                target_strike=data['recovery'].get('target_strike'),
                target_expiration=datetime.fromisoformat(data['recovery']['target_expiration']) if data['recovery'].get('target_expiration') else None,
                expected_credit=data['recovery'].get('expected_credit'),
                reasoning=data['recovery']['reasoning']
            )

        return cls(
            position_id=data['position_id'],
            symbol=data['symbol'],
            action=RecommendationAction(data['action']),
            risk_level=RiskLevel(data['risk_level']),
            confidence=data['confidence'],
            short_summary=data['short_summary'],
            detailed_reasoning=data['detailed_reasoning'],
            greeks=greeks,
            news=news,
            recovery=recovery,
            generated_at=datetime.fromisoformat(data['generated_at']),
            cache_expires_at=datetime.fromisoformat(data['cache_expires_at']) if data.get('cache_expires_at') else None,
            data_freshness=data.get('data_freshness', 'real-time')
        )


# =============================================================================
# Example Usage
# =============================================================================

if __name__ == "__main__":
    # Example: Create a position
    position = Position(
        position_id="NVDA-180P-2025-12-15",
        symbol="NVDA",
        strike=180.0,
        expiration=datetime(2025, 12, 15),
        option_type="put",
        position_type="short",
        quantity=2,
        avg_price=3.50,
        current_price=5.20,
        pl=-340.0,
        pl_pct=-15.5,
        dte=12,
        stock_price=175.30
    )

    print("Position Status:", position.status.value)
    print("Is ITM:", position.is_itm)
    print("Moneyness:", position.moneyness)

    # Example: Create Greeks
    greeks = OptionsGreeks(
        delta=-0.65,
        theta=-0.25,
        gamma=0.05,
        vega=0.30,
        iv=45.0,
        updated_at=datetime.now()
    )

    print("\nGreeks:")
    print("Assignment Risk:", greeks.assignment_risk)
    print("Theta Decay Quality:", greeks.theta_decay_quality)

    # Example: Create recommendation
    rec = PositionRecommendation(
        position_id=position.position_id,
        symbol=position.symbol,
        action=RecommendationAction.ROLL_DOWN_OUT,
        risk_level=RiskLevel.HIGH,
        confidence=0.85,
        short_summary="Roll to $175 strike, +30 days (+$45 credit)",
        detailed_reasoning="Your NVDA $180 CSP is down 15% with 12 days to expiration. "
                          "Delta is -0.65 (assignment risk increasing). Recent earnings beat shows strong fundamentals. "
                          "Recommendation: Roll to $175 strike for +$45 credit to reduce assignment risk.",
        greeks=greeks
    )

    print("\nRecommendation:")
    print("Action:", rec.action.value)
    print("Risk Level:", rec.risk_level.value)
    print("Confidence:", f"{rec.confidence*100:.0f}%")
    print("Summary:", rec.short_summary)
    print("Is Urgent:", rec.is_urgent)

    # Test serialization
    rec_dict = rec.to_dict()
    print("\nSerialized to dict:", len(rec_dict), "keys")

    # Test deserialization
    rec_restored = PositionRecommendation.from_dict(rec_dict)
    print("Restored from dict:", rec_restored.action.value)
