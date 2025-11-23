"""
Options Flow Agent - Unusual Options Activity Tracking

Monitors and analyzes unusual options activity to identify potential trading opportunities.
Tracks large orders, high volume, and unusual premium flows.

Author: Magnus AVA System
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from ..base_agent import BaseAgent

logger = logging.getLogger(__name__)


class FlowType(Enum):
    """Types of options flow signals"""
    SWEEP = "sweep"  # Multi-exchange sweep order
    BLOCK = "block"  # Large single order
    UNUSUAL_VOLUME = "unusual_volume"  # Volume spike
    UNUSUAL_OI = "unusual_oi"  # Open interest spike
    PREMIUM_FLOW = "premium_flow"  # Large premium flow


class Sentiment(Enum):
    """Market sentiment from flow"""
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"


@dataclass
class OptionsFlow:
    """Single options flow alert"""
    symbol: str
    flow_type: FlowType
    sentiment: Sentiment
    option_type: str  # CALL or PUT
    strike: float
    expiration: datetime
    premium: float
    volume: int
    open_interest: int
    timestamp: datetime
    spot_price: float
    confidence: float  # 0-100
    details: str


@dataclass
class FlowAnalysis:
    """Analysis of options flow for a symbol"""
    symbol: str
    overall_sentiment: Sentiment
    bullish_flow_count: int
    bearish_flow_count: int
    total_premium: float
    net_premium: float  # Bullish premium - Bearish premium
    unusual_flows: List[OptionsFlow]
    recommendations: List[str]
    confidence: float


class OptionsFlowAgent(BaseAgent):
    """
    Agent for tracking and analyzing unusual options activity

    Features:
    - Real-time flow monitoring
    - Sweep and block detection
    - Sentiment analysis
    - Premium flow tracking
    - AI-powered insights
    """

    def __init__(self, llm_service=None, db_manager=None):
        """
        Initialize Options Flow Agent

        Args:
            llm_service: Local LLM service for AI insights
            db_manager: Database manager for options data
        """
        super().__init__(name="OptionsFlowAgent", llm_service=llm_service)
        self.db_manager = db_manager

        # Flow detection thresholds
        self.SWEEP_THRESHOLD = 1000  # Min contracts for sweep
        self.BLOCK_THRESHOLD = 500  # Min contracts for block
        self.VOLUME_SPIKE_RATIO = 3.0  # Volume vs avg volume
        self.OI_SPIKE_RATIO = 2.0  # OI vs avg OI
        self.PREMIUM_THRESHOLD = 100000  # Min $100k premium

        logger.info("OptionsFlowAgent initialized")

    async def analyze_symbol_flow(self, symbol: str, lookback_hours: int = 24) -> FlowAnalysis:
        """
        Analyze options flow for a symbol

        Args:
            symbol: Stock symbol to analyze
            lookback_hours: Hours to look back for flow data

        Returns:
            FlowAnalysis object with complete analysis
        """
        try:
            logger.info(f"Analyzing options flow for {symbol} (last {lookback_hours}h)")

            # Get unusual flows
            unusual_flows = await self._detect_unusual_flows(symbol, lookback_hours)

            if not unusual_flows:
                return FlowAnalysis(
                    symbol=symbol,
                    overall_sentiment=Sentiment.NEUTRAL,
                    bullish_flow_count=0,
                    bearish_flow_count=0,
                    total_premium=0.0,
                    net_premium=0.0,
                    unusual_flows=[],
                    recommendations=["No unusual flow detected"],
                    confidence=0.0
                )

            # Calculate sentiment metrics
            bullish_flows = [f for f in unusual_flows if f.sentiment == Sentiment.BULLISH]
            bearish_flows = [f for f in unusual_flows if f.sentiment == Sentiment.BEARISH]

            bullish_premium = sum(f.premium for f in bullish_flows)
            bearish_premium = sum(f.premium for f in bearish_flows)
            total_premium = bullish_premium + bearish_premium
            net_premium = bullish_premium - bearish_premium

            # Determine overall sentiment
            if net_premium > total_premium * 0.3:
                overall_sentiment = Sentiment.BULLISH
            elif net_premium < -total_premium * 0.3:
                overall_sentiment = Sentiment.BEARISH
            else:
                overall_sentiment = Sentiment.NEUTRAL

            # Calculate confidence based on flow strength
            confidence = min(100, (len(unusual_flows) * 10) + (total_premium / 10000))

            # Generate recommendations
            recommendations = await self._generate_recommendations(
                symbol, unusual_flows, overall_sentiment, net_premium
            )

            return FlowAnalysis(
                symbol=symbol,
                overall_sentiment=overall_sentiment,
                bullish_flow_count=len(bullish_flows),
                bearish_flow_count=len(bearish_flows),
                total_premium=total_premium,
                net_premium=net_premium,
                unusual_flows=unusual_flows,
                recommendations=recommendations,
                confidence=confidence
            )

        except Exception as e:
            logger.error(f"Error analyzing flow for {symbol}: {e}")
            raise

    async def _detect_unusual_flows(self, symbol: str, lookback_hours: int) -> List[OptionsFlow]:
        """Detect unusual options activity"""
        try:
            unusual_flows = []
            cutoff_time = datetime.now() - timedelta(hours=lookback_hours)

            # Get recent options data from database
            if self.db_manager:
                query = """
                    SELECT
                        o.symbol,
                        o.option_type,
                        o.strike,
                        o.expiration_date,
                        o.volume,
                        o.open_interest,
                        o.last_price,
                        o.bid,
                        o.ask,
                        o.implied_volatility,
                        s.current_price as spot_price
                    FROM options o
                    JOIN stocks s ON o.symbol = s.symbol
                    WHERE o.symbol = %s
                        AND o.last_trade_date >= %s
                        AND o.volume > 0
                    ORDER BY o.volume DESC
                    LIMIT 100
                """

                with self.db_manager.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(query, (symbol, cutoff_time))
                    options_data = cursor.fetchall()

                # Analyze each option for unusual activity
                for opt in options_data:
                    flow = self._analyze_option_flow(opt)
                    if flow:
                        unusual_flows.append(flow)

            return unusual_flows

        except Exception as e:
            logger.error(f"Error detecting unusual flows: {e}")
            return []

    def _analyze_option_flow(self, opt_data: tuple) -> Optional[OptionsFlow]:
        """Analyze a single option for unusual activity"""
        try:
            (symbol, option_type, strike, expiration, volume, oi,
             last_price, bid, ask, iv, spot_price) = opt_data

            # Skip if no data
            if not volume or not last_price:
                return None

            # Calculate premium
            premium = last_price * volume * 100  # 100 shares per contract

            # Detect flow type and sentiment
            flow_type = None
            sentiment = Sentiment.NEUTRAL
            confidence = 50.0

            # Check for sweep (high volume, tight spread)
            spread = ask - bid if ask and bid else 0
            if volume >= self.SWEEP_THRESHOLD and spread < last_price * 0.05:
                flow_type = FlowType.SWEEP
                confidence = 85.0

            # Check for block trade
            elif volume >= self.BLOCK_THRESHOLD:
                flow_type = FlowType.BLOCK
                confidence = 75.0

            # Check for unusual volume (would need historical avg)
            # For now, use simple threshold
            elif volume > 500:
                flow_type = FlowType.UNUSUAL_VOLUME
                confidence = 60.0

            # Check for large premium flow
            elif premium >= self.PREMIUM_THRESHOLD:
                flow_type = FlowType.PREMIUM_FLOW
                confidence = 70.0

            # If no unusual activity detected, skip
            if not flow_type:
                return None

            # Determine sentiment based on option type and strike
            if option_type == 'CALL':
                # Calls are bullish if ITM or near ATM
                if strike <= spot_price * 1.05:
                    sentiment = Sentiment.BULLISH
                    confidence += 10
            else:  # PUT
                # Puts are bearish if ITM or near ATM
                if strike >= spot_price * 0.95:
                    sentiment = Sentiment.BEARISH
                    confidence += 10

            # Create flow details
            details = f"{flow_type.value.upper()}: {volume:,} contracts @ ${last_price:.2f}"

            return OptionsFlow(
                symbol=symbol,
                flow_type=flow_type,
                sentiment=sentiment,
                option_type=option_type,
                strike=strike,
                expiration=expiration,
                premium=premium,
                volume=volume,
                open_interest=oi,
                timestamp=datetime.now(),
                spot_price=spot_price,
                confidence=min(100, confidence),
                details=details
            )

        except Exception as e:
            logger.error(f"Error analyzing option flow: {e}")
            return None

    async def _generate_recommendations(
        self,
        symbol: str,
        flows: List[OptionsFlow],
        sentiment: Sentiment,
        net_premium: float
    ) -> List[str]:
        """Generate trading recommendations based on flow analysis"""
        try:
            recommendations = []

            # Basic recommendations based on sentiment
            if sentiment == Sentiment.BULLISH and net_premium > 500000:
                recommendations.append(
                    f"Strong bullish flow detected (${net_premium:,.0f} net premium)"
                )
                recommendations.append("Consider bullish strategies: long calls, bull spreads")
            elif sentiment == Sentiment.BEARISH and net_premium < -500000:
                recommendations.append(
                    f"Strong bearish flow detected (${abs(net_premium):,.0f} net premium)"
                )
                recommendations.append("Consider bearish strategies: long puts, bear spreads")
            else:
                recommendations.append("Mixed or neutral flow - wait for clearer signal")

            # Specific flow-based recommendations
            sweeps = [f for f in flows if f.flow_type == FlowType.SWEEP]
            if sweeps:
                recommendations.append(
                    f"{len(sweeps)} sweep order(s) detected - indicates strong conviction"
                )

            blocks = [f for f in flows if f.flow_type == FlowType.BLOCK]
            if blocks:
                recommendations.append(
                    f"{len(blocks)} block trade(s) detected - institutional activity"
                )

            # Get LLM insights if available
            if self.llm and len(flows) > 0:
                prompt = f"""Analyze this options flow for {symbol}:

Sentiment: {sentiment.value}
Net Premium: ${net_premium:,.0f}
Flow Count: {len(flows)}
Top Flows:
{self._format_flows_for_llm(flows[:5])}

Provide:
1. Key takeaways from this flow
2. Potential strategies to capitalize
3. Risk factors to watch"""

                llm_insights = await self.llm.generate(prompt, model="qwen2.5:14b")
                if llm_insights:
                    recommendations.append(f"\n🤖 AI Insights:\n{llm_insights}")

            return recommendations

        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return ["Error generating recommendations"]

    def _format_flows_for_llm(self, flows: List[OptionsFlow]) -> str:
        """Format flows for LLM prompt"""
        formatted = []
        for f in flows:
            formatted.append(
                f"- {f.option_type} ${f.strike} exp {f.expiration.date()}: "
                f"{f.volume:,} contracts (${f.premium:,.0f} premium) - {f.sentiment.value}"
            )
        return "\n".join(formatted)

    async def get_hot_symbols(self, min_flows: int = 3) -> List[Dict[str, Any]]:
        """
        Get symbols with unusual options activity

        Args:
            min_flows: Minimum number of unusual flows to be considered "hot"

        Returns:
            List of hot symbols with flow counts and sentiment
        """
        try:
            if not self.db_manager:
                return []

            # Get all symbols with recent options activity
            query = """
                SELECT DISTINCT symbol, COUNT(*) as flow_count
                FROM options
                WHERE last_trade_date >= NOW() - INTERVAL '24 hours'
                    AND volume > 500
                GROUP BY symbol
                HAVING COUNT(*) >= %s
                ORDER BY flow_count DESC
                LIMIT 20
            """

            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (min_flows,))
                hot_symbols = cursor.fetchall()

            # Analyze each hot symbol
            results = []
            for symbol, flow_count in hot_symbols:
                analysis = await self.analyze_symbol_flow(symbol, lookback_hours=24)
                results.append({
                    'symbol': symbol,
                    'flow_count': flow_count,
                    'sentiment': analysis.overall_sentiment.value,
                    'net_premium': analysis.net_premium,
                    'confidence': analysis.confidence
                })

            return results

        except Exception as e:
            logger.error(f"Error getting hot symbols: {e}")
            return []

    async def track_flow_real_time(self, symbols: List[str], callback=None):
        """
        Track real-time options flow for given symbols

        Args:
            symbols: List of symbols to monitor
            callback: Optional callback function for new flow alerts
        """
        logger.info(f"Starting real-time flow tracking for {len(symbols)} symbols")
        # Implementation for real-time tracking would go here
        # This would integrate with a real-time options data feed
        pass
