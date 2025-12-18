"""
Technical Analysis Agent - Unified LangGraph-based agent
Migrated from src/agents/ai_research/technical_agent.py

Provides comprehensive technical analysis using:
- Advanced Technical Indicators (RSI, MACD, Bollinger Bands, Volume Profile)
- Zone Analysis (Supply/Demand Zones, Support/Resistance)
- Smart Money Indicators (Order Blocks, Fair Value Gaps, BOS/CHoCH)
- Pattern Recognition (Chart patterns, harmonic patterns)
- Local LLM for intelligent analysis and insights
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import pandas as pd
import numpy as np
import yfinance as yf

from ...core.agent_base import BaseAgent, AgentState
from langchain_core.tools import tool

# Import technical analysis modules
try:
    from src.advanced_technical_indicators import (
        VolumeProfileCalculator,
        OrderFlowAnalyzer,
        HarmonicPatternDetector
    )
    from src.zone_analyzer import ZoneAnalyzer
    from src.smart_money_indicators import SmartMoneyIndicators
    from src.magnus_local_llm import get_magnus_llm, TaskComplexity
    TECH_MODULES_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Technical analysis modules not fully available: {e}")
    TECH_MODULES_AVAILABLE = False

logger = logging.getLogger(__name__)


@tool
def analyze_technical_tool(symbol: str) -> str:
    """Perform technical analysis on a stock"""
    try:
        # Fetch data
        ticker = yf.Ticker(symbol)
        df = ticker.history(period='3mo', interval='1d')

        if df.empty:
            return f"No data available for {symbol}"

        # Basic indicators
        close = df['Close'].iloc[-1]
        sma_20 = df['Close'].rolling(20).mean().iloc[-1]
        sma_50 = df['Close'].rolling(50).mean().iloc[-1]

        return f"{symbol} - Price: ${close:.2f}, SMA20: ${sma_20:.2f}, SMA50: ${sma_50:.2f}"
    except Exception as e:
        return f"Error analyzing {symbol}: {str(e)}"


class TechnicalAnalysisAgent(BaseAgent):
    """
    Technical Analysis Agent - Comprehensive price action and technical analysis

    Capabilities:
    - Technical indicators (RSI, MACD, Bollinger Bands, Volume Profile)
    - Chart pattern detection (Head & Shoulders, Triangles, Flags, etc.)
    - Support/resistance level identification
    - Supply/demand zone analysis
    - Volume analysis and order flow
    - Smart Money Concepts (Order Blocks, FVG, BOS/CHoCH)
    - Trend analysis and momentum
    - LLM-powered insights and pattern recognition
    """

    def __init__(self, use_huggingface: bool = False):
        """Initialize Technical Analysis Agent"""
        tools = [analyze_technical_tool]

        super().__init__(
            name="technical_analysis_agent",
            description="Analyzes price action, technical indicators, and chart patterns",
            tools=tools,
            use_huggingface=use_huggingface
        )

        self.metadata['capabilities'] = [
            'technical_indicators',
            'chart_patterns',
            'support_resistance',
            'volume_analysis',
            'trend_analysis',
            'rsi_macd_analysis',
            'supply_demand_zones',
            'smart_money_concepts',
            'order_flow_analysis',
            'llm_insights'
        ]

        # Initialize technical analysis modules
        if TECH_MODULES_AVAILABLE:
            self.volume_profile = VolumeProfileCalculator(value_area_pct=0.70)
            self.order_flow = OrderFlowAnalyzer()
            self.harmonic_detector = HarmonicPatternDetector()
            self.zone_analyzer = ZoneAnalyzer()
            self.smart_money = SmartMoneyIndicators()
            self.llm = get_magnus_llm()
        else:
            logger.warning("Technical analysis modules not available - running in limited mode")
            self.volume_profile = None
            self.order_flow = None
            self.harmonic_detector = None
            self.zone_analyzer = None
            self.smart_money = None
            self.llm = None

    async def execute(self, state: AgentState) -> AgentState:
        """Execute technical analysis agent"""
        try:
            input_text = state.get('input', '')
            context = state.get('context', {})

            symbol = context.get('symbol')
            if not symbol:
                # Try to extract symbol from input
                symbol = self._extract_symbol_from_input(input_text)

            if not symbol:
                state['error'] = "No symbol provided for technical analysis"
                return state

            logger.info(f"Performing technical analysis for {symbol}")

            # Fetch market data
            df = self._fetch_market_data(symbol, period='3mo', interval='1d')

            if df is None or df.empty:
                state['error'] = f"No market data available for {symbol}"
                return state

            # Perform comprehensive analysis
            result = await self._perform_comprehensive_analysis(symbol, df, context)

            state['result'] = result
            return state

        except Exception as e:
            logger.error(f"TechnicalAnalysisAgent error: {e}", exc_info=True)
            state['error'] = str(e)
            return state

    async def _perform_comprehensive_analysis(
        self,
        symbol: str,
        df: pd.DataFrame,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform comprehensive technical analysis"""

        # Get current price
        current_price = float(df['Close'].iloc[-1])

        # 1. Calculate Technical Indicators
        indicators = self._calculate_technical_indicators(df)

        # 2. Identify Support/Resistance and Zones
        zones = self._analyze_zones(df, current_price)

        # 3. Detect Chart Patterns
        patterns = self._detect_chart_patterns(df)

        # 4. Perform Volume and Order Flow Analysis
        volume_analysis = self._analyze_volume_and_flow(df, current_price)

        # 5. Smart Money Concepts
        smart_money_analysis = self._analyze_smart_money(df)

        # 6. Generate LLM-powered insights
        llm_insights = await self._generate_llm_insights(
            symbol=symbol,
            current_price=current_price,
            indicators=indicators,
            zones=zones,
            patterns=patterns,
            volume_analysis=volume_analysis,
            smart_money=smart_money_analysis
        )

        # 7. Determine trading signal
        signal = self._determine_trading_signal(
            indicators=indicators,
            zones=zones,
            patterns=patterns,
            volume_analysis=volume_analysis,
            smart_money=smart_money_analysis
        )

        return {
            'symbol': symbol,
            'current_price': current_price,
            'timestamp': datetime.now().isoformat(),
            'indicators': indicators,
            'zones': zones,
            'patterns': patterns,
            'volume_analysis': volume_analysis,
            'smart_money': smart_money_analysis,
            'llm_insights': llm_insights,
            'signal': signal,
            'analysis_period': '3 months',
            'data_points': len(df)
        }

    def _calculate_technical_indicators(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate comprehensive technical indicators"""
        try:
            close = df['Close']
            high = df['High']
            low = df['Low']
            volume = df['Volume']

            # Moving Averages
            sma_20 = close.rolling(20).mean().iloc[-1]
            sma_50 = close.rolling(50).mean().iloc[-1]
            sma_200 = close.rolling(200).mean().iloc[-1] if len(close) >= 200 else None
            ema_12 = close.ewm(span=12).mean().iloc[-1]
            ema_26 = close.ewm(span=26).mean().iloc[-1]

            # RSI
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            rsi_value = float(rsi.iloc[-1])

            # MACD
            macd_line = ema_12 - ema_26
            signal_line = close.ewm(span=9).mean().iloc[-1]
            macd_histogram = macd_line - signal_line

            # Bollinger Bands
            bb_period = 20
            bb_std = 2
            bb_middle = close.rolling(bb_period).mean()
            bb_std_dev = close.rolling(bb_period).std()
            bb_upper = bb_middle + (bb_std_dev * bb_std)
            bb_lower = bb_middle - (bb_std_dev * bb_std)

            bb_upper_value = float(bb_upper.iloc[-1])
            bb_lower_value = float(bb_lower.iloc[-1])
            bb_middle_value = float(bb_middle.iloc[-1])

            # ATR (Average True Range)
            high_low = high - low
            high_close = (high - close.shift()).abs()
            low_close = (low - close.shift()).abs()
            true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            atr = true_range.rolling(14).mean().iloc[-1]

            # Volume analysis
            avg_volume = volume.rolling(20).mean().iloc[-1]
            volume_ratio = volume.iloc[-1] / avg_volume if avg_volume > 0 else 1.0

            # Trend determination
            current_price = close.iloc[-1]
            trend = self._determine_trend(current_price, sma_20, sma_50, sma_200)

            return {
                'moving_averages': {
                    'sma_20': float(sma_20),
                    'sma_50': float(sma_50),
                    'sma_200': float(sma_200) if sma_200 is not None else None,
                    'ema_12': float(ema_12),
                    'ema_26': float(ema_26)
                },
                'rsi': {
                    'value': rsi_value,
                    'signal': self._interpret_rsi(rsi_value)
                },
                'macd': {
                    'macd_line': float(macd_line),
                    'signal_line': float(signal_line),
                    'histogram': float(macd_histogram),
                    'signal': 'BULLISH' if macd_histogram > 0 else 'BEARISH'
                },
                'bollinger_bands': {
                    'upper': bb_upper_value,
                    'middle': bb_middle_value,
                    'lower': bb_lower_value,
                    'position': self._bb_position(current_price, bb_upper_value, bb_lower_value)
                },
                'atr': float(atr),
                'volume': {
                    'current': int(volume.iloc[-1]),
                    'average': int(avg_volume),
                    'ratio': float(volume_ratio),
                    'signal': 'HIGH' if volume_ratio > 1.5 else 'NORMAL' if volume_ratio > 0.5 else 'LOW'
                },
                'trend': trend
            }
        except Exception as e:
            logger.error(f"Error calculating indicators: {e}")
            return {'error': str(e)}

    def _analyze_zones(self, df: pd.DataFrame, current_price: float) -> Dict[str, Any]:
        """Analyze supply/demand zones and support/resistance levels"""
        try:
            if not self.zone_analyzer or not self.smart_money:
                return self._basic_support_resistance(df, current_price)

            # Detect zones using Smart Money Indicators
            structure = self.smart_money.detect_market_structure(df)

            # Extract swing highs and lows as support/resistance
            swing_highs = structure.get('swing_highs', [])
            swing_lows = structure.get('swing_lows', [])

            # Get recent levels
            resistance_levels = [h['price'] for h in swing_highs[-5:]] if swing_highs else []
            support_levels = [l['price'] for l in swing_lows[-5:]] if swing_lows else []

            # Determine nearest levels
            nearest_support = max([s for s in support_levels if s < current_price], default=None)
            nearest_resistance = min([r for r in resistance_levels if r > current_price], default=None)

            return {
                'support_levels': support_levels,
                'resistance_levels': resistance_levels,
                'nearest_support': nearest_support,
                'nearest_resistance': nearest_resistance,
                'current_trend': structure.get('current_trend', 'NEUTRAL'),
                'swing_highs_count': len(swing_highs),
                'swing_lows_count': len(swing_lows)
            }
        except Exception as e:
            logger.error(f"Error analyzing zones: {e}")
            return self._basic_support_resistance(df, current_price)

    def _basic_support_resistance(self, df: pd.DataFrame, current_price: float) -> Dict[str, Any]:
        """Basic support/resistance calculation (fallback)"""
        high = df['High']
        low = df['Low']

        # Use recent highs/lows
        recent_high = high.tail(20).max()
        recent_low = low.tail(20).min()

        return {
            'support_levels': [float(recent_low)],
            'resistance_levels': [float(recent_high)],
            'nearest_support': float(recent_low) if recent_low < current_price else None,
            'nearest_resistance': float(recent_high) if recent_high > current_price else None,
            'current_trend': 'UNKNOWN',
            'swing_highs_count': 0,
            'swing_lows_count': 0
        }

    def _detect_chart_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect chart patterns"""
        try:
            patterns_detected = []

            # Simple pattern detection
            close = df['Close']

            # Higher highs, higher lows (uptrend)
            if len(close) >= 10:
                recent_highs = df['High'].tail(10)
                recent_lows = df['Low'].tail(10)

                if recent_highs.iloc[-1] > recent_highs.iloc[-5] and recent_lows.iloc[-1] > recent_lows.iloc[-5]:
                    patterns_detected.append({
                        'pattern': 'UPTREND',
                        'confidence': 'HIGH',
                        'description': 'Higher highs and higher lows detected'
                    })
                elif recent_highs.iloc[-1] < recent_highs.iloc[-5] and recent_lows.iloc[-1] < recent_lows.iloc[-5]:
                    patterns_detected.append({
                        'pattern': 'DOWNTREND',
                        'confidence': 'HIGH',
                        'description': 'Lower highs and lower lows detected'
                    })

            # Detect consolidation
            if len(close) >= 20:
                price_range = (close.tail(20).max() - close.tail(20).min()) / close.tail(20).mean()
                if price_range < 0.05:  # Less than 5% range
                    patterns_detected.append({
                        'pattern': 'CONSOLIDATION',
                        'confidence': 'MEDIUM',
                        'description': 'Price consolidating in tight range'
                    })

            return {
                'patterns_detected': patterns_detected,
                'count': len(patterns_detected)
            }
        except Exception as e:
            logger.error(f"Error detecting patterns: {e}")
            return {'patterns_detected': [], 'count': 0, 'error': str(e)}

    def _analyze_volume_and_flow(self, df: pd.DataFrame, current_price: float) -> Dict[str, Any]:
        """Analyze volume profile and order flow"""
        try:
            if not self.volume_profile or not self.order_flow:
                return self._basic_volume_analysis(df)

            # Volume Profile
            vp = self.volume_profile.calculate_volume_profile(df, price_bins=30)
            vp_signals = self.volume_profile.get_trading_signals(current_price, vp)

            # Order Flow (CVD)
            df_copy = df.copy()
            df_copy['cvd'] = self.order_flow.calculate_cvd(df_copy)

            cvd_latest = df_copy['cvd'].iloc[-1]
            cvd_prev = df_copy['cvd'].iloc[-6]
            cvd_trend = 'BULLISH' if cvd_latest > cvd_prev else 'BEARISH'

            # Divergences
            divergences = self.order_flow.find_cvd_divergences(df_copy, lookback=5)

            return {
                'volume_profile': {
                    'poc': vp['poc']['price'],
                    'vah': vp['vah'],
                    'val': vp['val'],
                    'position': vp_signals['position'],
                    'bias': vp_signals['bias'],
                    'setup_quality': vp_signals['setup_quality']
                },
                'order_flow': {
                    'cvd_latest': int(cvd_latest),
                    'cvd_trend': cvd_trend,
                    'divergences': len(divergences),
                    'divergence_signals': [d['signal'] for d in divergences[:3]]
                }
            }
        except Exception as e:
            logger.error(f"Error analyzing volume/flow: {e}")
            return self._basic_volume_analysis(df)

    def _basic_volume_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Basic volume analysis (fallback)"""
        volume = df['Volume']
        avg_volume = volume.rolling(20).mean().iloc[-1]
        current_volume = volume.iloc[-1]

        return {
            'volume_profile': {
                'current': int(current_volume),
                'average': int(avg_volume),
                'ratio': float(current_volume / avg_volume) if avg_volume > 0 else 1.0
            },
            'order_flow': {
                'trend': 'UNKNOWN'
            }
        }

    def _analyze_smart_money(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze Smart Money Concepts (ICT)"""
        try:
            if not self.smart_money:
                return {'order_blocks': [], 'fvg': [], 'liquidity_pools': []}

            # Get all SMC indicators
            smc_data = self.smart_money.get_all_smc_indicators(df)

            # Filter recent order blocks
            recent_obs = [ob for ob in smc_data['order_blocks']
                         if not ob['mitigated']][-5:]

            # Filter unfilled FVGs
            unfilled_fvgs = [fvg for fvg in smc_data['fair_value_gaps']
                            if not fvg['filled']][-5:]

            # Get market structure
            structure = smc_data['market_structure']

            return {
                'order_blocks': [{
                    'type': ob['type'],
                    'price_range': f"${ob['bottom']:.2f} - ${ob['top']:.2f}",
                    'strength': ob['strength']
                } for ob in recent_obs],
                'fair_value_gaps': [{
                    'type': fvg['type'],
                    'price_range': f"${fvg['bottom']:.2f} - ${fvg['top']:.2f}",
                    'gap_pct': fvg['gap_pct']
                } for fvg in unfilled_fvgs],
                'market_structure': {
                    'current_trend': structure['current_trend'],
                    'bos_count': len(structure['bos']),
                    'choch_count': len(structure['choch'])
                },
                'liquidity_pools': len(smc_data['liquidity_pools'])
            }
        except Exception as e:
            logger.error(f"Error analyzing smart money: {e}")
            return {'order_blocks': [], 'fair_value_gaps': [], 'market_structure': {}}

    async def _generate_llm_insights(
        self,
        symbol: str,
        current_price: float,
        indicators: Dict,
        zones: Dict,
        patterns: Dict,
        volume_analysis: Dict,
        smart_money: Dict
    ) -> Dict[str, Any]:
        """Generate LLM-powered insights and analysis"""
        try:
            if not self.llm:
                return {'summary': 'LLM not available', 'entry_points': [], 'risk_assessment': ''}

            # Build comprehensive context for LLM
            context = f"""
Symbol: {symbol}
Current Price: ${current_price:.2f}

TECHNICAL INDICATORS:
- RSI: {indicators.get('rsi', {}).get('value', 'N/A')} ({indicators.get('rsi', {}).get('signal', 'N/A')})
- MACD: {indicators.get('macd', {}).get('signal', 'N/A')}
- Trend: {indicators.get('trend', 'N/A')}
- Bollinger Bands Position: {indicators.get('bollinger_bands', {}).get('position', 'N/A')}

SUPPORT/RESISTANCE:
- Nearest Support: ${zones.get('nearest_support', 0):.2f}
- Nearest Resistance: ${zones.get('nearest_resistance', 0):.2f}
- Current Trend: {zones.get('current_trend', 'NEUTRAL')}

VOLUME ANALYSIS:
- Volume Signal: {indicators.get('volume', {}).get('signal', 'N/A')}
- Volume Profile Position: {volume_analysis.get('volume_profile', {}).get('position', 'N/A')}
- Order Flow Trend: {volume_analysis.get('order_flow', {}).get('cvd_trend', 'N/A')}

PATTERNS:
{patterns.get('patterns_detected', [])}

SMART MONEY:
- Order Blocks: {len(smart_money.get('order_blocks', []))}
- Fair Value Gaps: {len(smart_money.get('fair_value_gaps', []))}
- Market Structure Trend: {smart_money.get('market_structure', {}).get('current_trend', 'N/A')}
"""

            prompt = f"""Analyze the following technical data for {symbol} and provide:

{context}

Please provide:
1. A concise technical summary (2-3 sentences)
2. Potential entry points with specific price levels
3. Risk assessment and stop loss recommendations
4. Overall trading signal (BUY/SELL/HOLD) with confidence level

Format your response as structured analysis."""

            response = self.llm.query(
                prompt=prompt,
                complexity=TaskComplexity.BALANCED,
                use_trading_context=True
            )

            return {
                'summary': response,
                'analysis_timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error generating LLM insights: {e}")
            return {
                'summary': f"Error generating insights: {str(e)}",
                'analysis_timestamp': datetime.now().isoformat()
            }

    def _determine_trading_signal(
        self,
        indicators: Dict,
        zones: Dict,
        patterns: Dict,
        volume_analysis: Dict,
        smart_money: Dict
    ) -> Dict[str, Any]:
        """Determine overall trading signal with confidence"""
        try:
            bullish_signals = 0
            bearish_signals = 0
            total_weight = 0

            # RSI signal (weight: 15)
            rsi_value = indicators.get('rsi', {}).get('value', 50)
            if rsi_value < 30:
                bullish_signals += 15
            elif rsi_value > 70:
                bearish_signals += 15
            total_weight += 15

            # MACD signal (weight: 20)
            macd_signal = indicators.get('macd', {}).get('signal', 'NEUTRAL')
            if macd_signal == 'BULLISH':
                bullish_signals += 20
            elif macd_signal == 'BEARISH':
                bearish_signals += 20
            total_weight += 20

            # Trend signal (weight: 25)
            trend = indicators.get('trend', 'NEUTRAL')
            if trend == 'UPTREND':
                bullish_signals += 25
            elif trend == 'DOWNTREND':
                bearish_signals += 25
            total_weight += 25

            # Volume signal (weight: 15)
            volume_signal = indicators.get('volume', {}).get('signal', 'NORMAL')
            vp_bias = volume_analysis.get('volume_profile', {}).get('bias', 'NEUTRAL')
            if vp_bias == 'BULLISH':
                bullish_signals += 15
            elif vp_bias == 'BEARISH':
                bearish_signals += 15
            total_weight += 15

            # Smart Money signal (weight: 25)
            sm_trend = smart_money.get('market_structure', {}).get('current_trend', 'NEUTRAL')
            if sm_trend == 'BULLISH':
                bullish_signals += 25
            elif sm_trend == 'BEARISH':
                bearish_signals += 25
            total_weight += 25

            # Calculate confidence
            if bullish_signals > bearish_signals:
                signal = 'BUY'
                confidence = (bullish_signals / total_weight) * 100
            elif bearish_signals > bullish_signals:
                signal = 'SELL'
                confidence = (bearish_signals / total_weight) * 100
            else:
                signal = 'HOLD'
                confidence = 50.0

            # Determine strength
            if confidence >= 75:
                strength = 'STRONG'
            elif confidence >= 60:
                strength = 'MODERATE'
            else:
                strength = 'WEAK'

            return {
                'signal': signal,
                'confidence': round(confidence, 2),
                'strength': strength,
                'bullish_score': bullish_signals,
                'bearish_score': bearish_signals,
                'reasoning': self._generate_signal_reasoning(
                    signal, confidence, indicators, zones, volume_analysis, smart_money
                )
            }
        except Exception as e:
            logger.error(f"Error determining signal: {e}")
            return {
                'signal': 'HOLD',
                'confidence': 0,
                'strength': 'UNKNOWN',
                'reasoning': f"Error: {str(e)}"
            }

    def _generate_signal_reasoning(
        self,
        signal: str,
        confidence: float,
        indicators: Dict,
        zones: Dict,
        volume_analysis: Dict,
        smart_money: Dict
    ) -> str:
        """Generate human-readable reasoning for the signal"""
        reasons = []

        rsi_value = indicators.get('rsi', {}).get('value', 50)
        if rsi_value < 30:
            reasons.append(f"RSI oversold at {rsi_value:.1f}")
        elif rsi_value > 70:
            reasons.append(f"RSI overbought at {rsi_value:.1f}")

        trend = indicators.get('trend', 'NEUTRAL')
        if trend != 'NEUTRAL':
            reasons.append(f"Price in {trend.lower()}")

        macd_signal = indicators.get('macd', {}).get('signal', 'NEUTRAL')
        if macd_signal != 'NEUTRAL':
            reasons.append(f"MACD {macd_signal.lower()}")

        vp_bias = volume_analysis.get('volume_profile', {}).get('bias', 'NEUTRAL')
        if vp_bias != 'NEUTRAL':
            reasons.append(f"Volume profile {vp_bias.lower()}")

        if not reasons:
            reasons.append("Mixed signals detected")

        return f"{signal} signal with {confidence:.0f}% confidence: " + ", ".join(reasons)

    def _fetch_market_data(
        self,
        symbol: str,
        period: str = '3mo',
        interval: str = '1d'
    ) -> Optional[pd.DataFrame]:
        """Fetch market data using yfinance"""
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)

            if df.empty:
                logger.warning(f"No data returned for {symbol}")
                return None

            # Ensure consistent column names
            df.columns = [col.lower() if isinstance(col, str) else col for col in df.columns]
            df = df.rename(columns={
                'close': 'Close',
                'open': 'Open',
                'high': 'High',
                'low': 'Low',
                'volume': 'Volume'
            })

            return df
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return None

    def _extract_symbol_from_input(self, input_text: str) -> Optional[str]:
        """Extract stock symbol from input text"""
        import re

        # Look for patterns like "AAPL", "$AAPL", or "analyze AAPL"
        patterns = [
            r'\$([A-Z]{1,5})',  # $AAPL
            r'\b([A-Z]{1,5})\b',  # AAPL
        ]

        for pattern in patterns:
            match = re.search(pattern, input_text)
            if match:
                return match.group(1)

        return None

    def _determine_trend(
        self,
        current_price: float,
        sma_20: float,
        sma_50: float,
        sma_200: Optional[float]
    ) -> str:
        """Determine overall trend from moving averages"""
        if current_price > sma_20 > sma_50:
            if sma_200 is None or current_price > sma_200:
                return 'UPTREND'
        elif current_price < sma_20 < sma_50:
            if sma_200 is None or current_price < sma_200:
                return 'DOWNTREND'

        return 'NEUTRAL'

    def _interpret_rsi(self, rsi_value: float) -> str:
        """Interpret RSI value"""
        if rsi_value < 30:
            return 'OVERSOLD'
        elif rsi_value > 70:
            return 'OVERBOUGHT'
        elif rsi_value < 40:
            return 'BEARISH'
        elif rsi_value > 60:
            return 'BULLISH'
        else:
            return 'NEUTRAL'

    def _bb_position(
        self,
        current_price: float,
        upper: float,
        lower: float
    ) -> str:
        """Determine position relative to Bollinger Bands"""
        if current_price > upper:
            return 'ABOVE_UPPER'
        elif current_price < lower:
            return 'BELOW_LOWER'
        elif current_price > (upper + lower) / 2:
            return 'UPPER_HALF'
        else:
            return 'LOWER_HALF'
