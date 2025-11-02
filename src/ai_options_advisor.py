"""
AI Options Advisor - Intelligent recommendations using LangChain and advanced analysis

This module provides AI-powered recommendations for option strategies using:
- Fundamental analysis (earnings, growth, sentiment)
- Technical analysis (support/resistance, trends, indicators)
- Options Greeks analysis (delta, theta, vega impact)
- Market conditions analysis (VIX, sector rotation)
- Probability modeling (Monte Carlo simulations)
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import yfinance as yf
import logging
from dataclasses import dataclass
import json
import asyncio

# Technical indicators
import talib

# For AI integration
from langchain_community.chat_models import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.messages import BaseMessage
from langchain_core.callbacks import StreamingStdOutCallbackHandler

logger = logging.getLogger(__name__)


@dataclass
class MarketConditions:
    """Current market conditions data"""
    vix_level: float
    vix_percentile: float
    market_trend: str  # 'bullish', 'bearish', 'neutral'
    sector_rotation: Dict[str, float]
    risk_appetite: str  # 'risk-on', 'risk-off'


@dataclass
class StockAnalysis:
    """Complete stock analysis data"""
    symbol: str
    fundamentals: Dict
    technicals: Dict
    sentiment: Dict
    options_flow: Dict


class AIOptionsAdvisor:
    """AI-powered options strategy advisor"""

    def __init__(self, openai_api_key: Optional[str] = None):
        """Initialize AI Options Advisor

        Args:
            openai_api_key: OpenAI API key for GPT-4 integration
        """
        self.api_key = openai_api_key
        if self.api_key:
            self.llm = ChatOpenAI(
                api_key=self.api_key,
                model="gpt-4-turbo-preview",
                temperature=0.2,
                streaming=False
            )
        else:
            self.llm = None
            logger.warning("No OpenAI API key provided. AI recommendations will be limited.")

        # Initialize analysis components
        self.fundamental_analyzer = FundamentalAnalyzer()
        self.technical_analyzer = TechnicalAnalyzer()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.monte_carlo_simulator = MonteCarloSimulator()

    async def analyze_fundamentals(self, symbol: str) -> str:
        """
        Analyze company fundamentals

        Args:
            symbol: Stock ticker symbol

        Returns:
            Fundamental analysis summary
        """
        analysis = await self.fundamental_analyzer.analyze(symbol)

        summary = f"**Fundamental Analysis for {symbol}:**\n"
        summary += f"- P/E Ratio: {analysis.get('pe_ratio', 'N/A')}\n"
        summary += f"- Revenue Growth: {analysis.get('revenue_growth', 'N/A')}%\n"
        summary += f"- Profit Margin: {analysis.get('profit_margin', 'N/A')}%\n"
        summary += f"- Debt/Equity: {analysis.get('debt_to_equity', 'N/A')}\n"
        summary += f"- Earnings Date: {analysis.get('next_earnings', 'N/A')}\n"
        summary += f"- Analyst Rating: {analysis.get('analyst_rating', 'N/A')}\n"

        return summary

    async def analyze_technicals(self, symbol: str) -> str:
        """
        Analyze technical indicators

        Args:
            symbol: Stock ticker symbol

        Returns:
            Technical analysis summary
        """
        analysis = await self.technical_analyzer.analyze(symbol)

        summary = f"**Technical Analysis for {symbol}:**\n"
        summary += f"- Trend: {analysis.get('trend', 'N/A')}\n"
        summary += f"- RSI: {analysis.get('rsi', 'N/A')} ({analysis.get('rsi_signal', '')})\n"
        summary += f"- MACD: {analysis.get('macd_signal', 'N/A')}\n"
        summary += f"- Support: ${analysis.get('support', 'N/A')}\n"
        summary += f"- Resistance: ${analysis.get('resistance', 'N/A')}\n"
        summary += f"- 50-Day MA: ${analysis.get('ma_50', 'N/A')}\n"
        summary += f"- 200-Day MA: ${analysis.get('ma_200', 'N/A')}\n"

        return summary

    def recommend_strategy(self, position: Dict, opportunities: List[Dict]) -> str:
        """
        Generate AI recommendation for best strategy

        Args:
            position: Current position details
            opportunities: List of available opportunities

        Returns:
            Detailed recommendation with reasoning
        """
        symbol = position.get('symbol', 'Unknown')

        # Gather all analysis data
        fundamentals = self.fundamental_analyzer.analyze_sync(symbol)
        technicals = self.technical_analyzer.analyze_sync(symbol)
        market_conditions = self._get_market_conditions()

        # Use LLM if available
        if self.llm:
            recommendation = self._generate_llm_recommendation(
                position, opportunities, fundamentals, technicals, market_conditions
            )
        else:
            # Fallback to rule-based recommendation
            recommendation = self._generate_rule_based_recommendation(
                position, opportunities, fundamentals, technicals, market_conditions
            )

        return recommendation

    def analyze_option_greeks(self, symbol: str, strike: float,
                            expiration: str, option_type: str = 'put') -> Dict:
        """
        Analyze option Greeks and their implications

        Args:
            symbol: Stock ticker
            strike: Strike price
            expiration: Expiration date
            option_type: 'put' or 'call'

        Returns:
            Greeks analysis with interpretations
        """
        try:
            # Calculate Greeks
            greeks = self._calculate_greeks(symbol, strike, expiration, option_type)

            # Interpret Greeks
            interpretation = {
                'delta': self._interpret_delta(greeks['delta'], option_type),
                'gamma': self._interpret_gamma(greeks['gamma']),
                'theta': self._interpret_theta(greeks['theta']),
                'vega': self._interpret_vega(greeks['vega']),
                'rho': self._interpret_rho(greeks['rho'])
            }

            return {
                'values': greeks,
                'interpretations': interpretation,
                'overall_assessment': self._assess_greeks_overall(greeks, option_type)
            }

        except Exception as e:
            logger.error(f"Error analyzing Greeks for {symbol}: {e}")
            return {'error': str(e)}

    def run_monte_carlo_simulation(self, symbol: str, strike: float,
                                  days_to_expiry: int, num_simulations: int = 10000) -> Dict:
        """
        Run Monte Carlo simulation for probability analysis

        Args:
            symbol: Stock ticker
            strike: Strike price
            days_to_expiry: Days until expiration
            num_simulations: Number of simulation paths

        Returns:
            Simulation results with probabilities
        """
        return self.monte_carlo_simulator.simulate(
            symbol, strike, days_to_expiry, num_simulations
        )

    def _generate_llm_recommendation(self, position: Dict, opportunities: List[Dict],
                                    fundamentals: Dict, technicals: Dict,
                                    market_conditions: MarketConditions) -> str:
        """Generate recommendation using LLM"""

        # Prepare context for LLM
        system_prompt = """You are an expert options trading advisor specializing in
        cash-secured puts and wheel strategies. Analyze the provided position and market data
        to recommend the best recovery strategy. Consider risk management, probability of success,
        and capital efficiency. Be specific and actionable in your recommendations."""

        human_prompt = f"""
        Current Losing Position:
        - Symbol: {position.get('symbol')}
        - Strike: ${position.get('current_strike')}
        - Current Price: ${position.get('current_price')}
        - Loss: ${position.get('current_loss')}
        - Days to Expiry: {position.get('days_to_expiry')}

        Fundamental Analysis:
        {json.dumps(fundamentals, indent=2)}

        Technical Analysis:
        {json.dumps(technicals, indent=2)}

        Market Conditions:
        - VIX: {market_conditions.vix_level} (Percentile: {market_conditions.vix_percentile}%)
        - Market Trend: {market_conditions.market_trend}
        - Risk Appetite: {market_conditions.risk_appetite}

        Top 3 Recovery Opportunities:
        {json.dumps(opportunities[:3], indent=2, default=str)}

        Please provide:
        1. Best recovery strategy (buy new CSPs, roll, or accept assignment)
        2. Specific strike and expiration recommendations
        3. Risk assessment
        4. Expected outcome with probabilities
        5. Alternative strategies if the primary recommendation doesn't work
        """

        try:
            messages = [
                SystemMessagePromptTemplate.from_template(system_prompt).format(),
                HumanMessagePromptTemplate.from_template(human_prompt).format()
            ]

            response = self.llm.predict_messages(messages)
            return response.content

        except Exception as e:
            logger.error(f"Error generating LLM recommendation: {e}")
            return self._generate_rule_based_recommendation(
                position, opportunities, fundamentals, technicals, market_conditions
            )

    def _generate_rule_based_recommendation(self, position: Dict, opportunities: List[Dict],
                                           fundamentals: Dict, technicals: Dict,
                                           market_conditions: MarketConditions) -> str:
        """Generate recommendation using rule-based logic"""

        recommendation = f"**Recovery Strategy Recommendation for {position.get('symbol')}**\n\n"

        # Analyze current situation
        loss_percentage = abs(position.get('loss_percentage', 0))
        days_to_expiry = position.get('days_to_expiry', 0)

        # Decision tree for recommendations
        if loss_percentage < 5 and days_to_expiry > 14:
            recommendation += "**Primary Strategy: Hold and Monitor**\n"
            recommendation += "- Position has minimal loss with time remaining\n"
            recommendation += "- Monitor for recovery above strike\n"
            recommendation += "- Set alert at breakeven price\n\n"

        elif loss_percentage < 10 and market_conditions.market_trend == 'bullish':
            recommendation += "**Primary Strategy: Roll Out**\n"
            recommendation += "- Market conditions favor recovery\n"
            recommendation += "- Roll to next monthly expiration\n"
            recommendation += "- Maintain same strike to maximize recovery potential\n\n"

        elif loss_percentage > 15 or market_conditions.risk_appetite == 'risk-off':
            recommendation += "**Primary Strategy: Roll Down and Out**\n"
            recommendation += "- Significant loss requires risk reduction\n"
            recommendation += "- Target 5-10% below current price\n"
            recommendation += "- Extend expiration by 30-45 days\n\n"

        else:
            recommendation += "**Primary Strategy: Buy Recovery CSPs**\n"
            recommendation += "- Add new positions at better strikes\n"

            if opportunities:
                best_opp = opportunities[0]
                recommendation += f"- Recommended: ${best_opp.get('strike', 0):.2f} strike\n"
                recommendation += f"- Premium: ${best_opp.get('premium', 0):.2f}\n"
                recommendation += f"- Probability of Profit: {best_opp.get('probability_profit', 0)*100:.1f}%\n\n"

        # Add risk assessment
        recommendation += "**Risk Assessment:**\n"

        if market_conditions.vix_level > 25:
            recommendation += "- High VIX indicates elevated volatility risk\n"

        if technicals.get('rsi', 50) < 30:
            recommendation += "- Oversold conditions may present opportunity\n"
        elif technicals.get('rsi', 50) > 70:
            recommendation += "- Overbought conditions increase assignment risk\n"

        if fundamentals.get('next_earnings_days', 999) < 30:
            recommendation += f"- Earnings in {fundamentals.get('next_earnings_days')} days - expect volatility\n"

        # Add alternative strategies
        recommendation += "\n**Alternative Strategies:**\n"
        recommendation += "1. Accept assignment and sell covered calls (wheel strategy)\n"
        recommendation += "2. Close position and redeploy capital to higher probability trades\n"
        recommendation += "3. Hedge with protective calls if expecting continued decline\n"

        return recommendation

    def _get_market_conditions(self) -> MarketConditions:
        """Get current market conditions"""
        try:
            # Get VIX data
            vix = yf.Ticker('^VIX')
            vix_current = float(vix.history(period='1d')['Close'].iloc[-1])

            # Calculate VIX percentile
            vix_history = vix.history(period='1y')['Close']
            vix_percentile = (vix_history < vix_current).mean() * 100

            # Determine market trend (simplified)
            spy = yf.Ticker('SPY')
            spy_history = spy.history(period='50d')['Close']
            spy_sma_20 = spy_history.tail(20).mean()
            spy_sma_50 = spy_history.mean()
            spy_current = spy_history.iloc[-1]

            if spy_current > spy_sma_20 > spy_sma_50:
                market_trend = 'bullish'
            elif spy_current < spy_sma_20 < spy_sma_50:
                market_trend = 'bearish'
            else:
                market_trend = 'neutral'

            # Risk appetite based on VIX
            if vix_current < 15:
                risk_appetite = 'risk-on'
            elif vix_current > 25:
                risk_appetite = 'risk-off'
            else:
                risk_appetite = 'neutral'

            return MarketConditions(
                vix_level=vix_current,
                vix_percentile=vix_percentile,
                market_trend=market_trend,
                sector_rotation={},  # Could be expanded
                risk_appetite=risk_appetite
            )

        except Exception as e:
            logger.error(f"Error getting market conditions: {e}")
            return MarketConditions(
                vix_level=20,
                vix_percentile=50,
                market_trend='neutral',
                sector_rotation={},
                risk_appetite='neutral'
            )

    def _calculate_greeks(self, symbol: str, strike: float,
                         expiration: str, option_type: str) -> Dict:
        """Calculate option Greeks"""
        # Simplified Greeks calculation
        # In production, use proper Black-Scholes or binomial models

        current_price = self._get_current_price(symbol)
        days_to_expiry = self._days_to_expiry(expiration)
        time_to_expiry = days_to_expiry / 365
        volatility = self._get_implied_volatility(symbol)
        risk_free_rate = 0.045

        # Simplified calculations (replace with proper Greeks library)
        if option_type == 'put':
            delta = -0.5 * (1 - (current_price - strike) / current_price)
            delta = max(-1, min(0, delta))
        else:
            delta = 0.5 * (1 + (current_price - strike) / current_price)
            delta = max(0, min(1, delta))

        gamma = 0.05 / (current_price * volatility * np.sqrt(time_to_expiry))
        theta = -0.05 * current_price * volatility / (2 * np.sqrt(time_to_expiry))
        vega = 0.01 * current_price * np.sqrt(time_to_expiry)
        rho = 0.01 * strike * time_to_expiry * abs(delta)

        return {
            'delta': delta,
            'gamma': gamma,
            'theta': theta,
            'vega': vega,
            'rho': rho
        }

    def _interpret_delta(self, delta: float, option_type: str) -> str:
        """Interpret delta value"""
        if option_type == 'put':
            probability_itm = abs(delta) * 100
            if abs(delta) < 0.3:
                return f"Low probability ({probability_itm:.1f}%) of assignment"
            elif abs(delta) < 0.5:
                return f"Moderate probability ({probability_itm:.1f}%) of assignment"
            else:
                return f"High probability ({probability_itm:.1f}%) of assignment"
        else:
            return f"Option price moves ${delta:.2f} per $1 stock move"

    def _interpret_gamma(self, gamma: float) -> str:
        """Interpret gamma value"""
        if gamma > 0.05:
            return "High gamma - delta changes rapidly with stock moves"
        elif gamma > 0.02:
            return "Moderate gamma - steady delta changes"
        else:
            return "Low gamma - stable delta"

    def _interpret_theta(self, theta: float) -> str:
        """Interpret theta value"""
        daily_decay = abs(theta)
        if daily_decay > 0.05:
            return f"High time decay - losing ${daily_decay:.2f}/day"
        elif daily_decay > 0.02:
            return f"Moderate time decay - losing ${daily_decay:.2f}/day"
        else:
            return f"Low time decay - losing ${daily_decay:.2f}/day"

    def _interpret_vega(self, vega: float) -> str:
        """Interpret vega value"""
        if vega > 0.5:
            return "High sensitivity to volatility changes"
        elif vega > 0.2:
            return "Moderate volatility sensitivity"
        else:
            return "Low volatility sensitivity"

    def _interpret_rho(self, rho: float) -> str:
        """Interpret rho value"""
        if abs(rho) > 0.1:
            return "Significant interest rate sensitivity"
        else:
            return "Minimal interest rate sensitivity"

    def _assess_greeks_overall(self, greeks: Dict, option_type: str) -> str:
        """Overall assessment of Greeks"""
        assessments = []

        if option_type == 'put' and abs(greeks['delta']) < 0.3:
            assessments.append("Low assignment risk")

        if abs(greeks['theta']) > 0.03:
            assessments.append("Favorable time decay for sellers")

        if greeks['vega'] > 0.3:
            assessments.append("Consider IV environment before entering")

        if not assessments:
            assessments.append("Balanced Greek profile")

        return "; ".join(assessments)

    def _get_current_price(self, symbol: str) -> float:
        """Get current stock price"""
        try:
            ticker = yf.Ticker(symbol)
            return float(ticker.history(period='1d')['Close'].iloc[-1])
        except:
            return 0

    def _days_to_expiry(self, expiration: str) -> int:
        """Calculate days to expiry"""
        try:
            exp_date = datetime.strptime(expiration, '%Y-%m-%d')
            return max(0, (exp_date - datetime.now()).days)
        except:
            return 0

    def _get_implied_volatility(self, symbol: str) -> float:
        """Get implied volatility"""
        try:
            ticker = yf.Ticker(symbol)
            options = ticker.options
            if options:
                chain = ticker.option_chain(options[0])
                ivs = chain.puts['impliedVolatility'].dropna()
                if len(ivs) > 0:
                    return float(ivs.mean())
        except:
            pass
        return 0.3  # Default 30% volatility


class FundamentalAnalyzer:
    """Analyze company fundamentals"""

    def analyze_sync(self, symbol: str) -> Dict:
        """Synchronous fundamental analysis"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            # Extract key metrics
            analysis = {
                'pe_ratio': info.get('trailingPE', info.get('forwardPE')),
                'peg_ratio': info.get('pegRatio'),
                'price_to_book': info.get('priceToBook'),
                'profit_margin': info.get('profitMargins', 0) * 100 if info.get('profitMargins') else None,
                'revenue_growth': info.get('revenueGrowth', 0) * 100 if info.get('revenueGrowth') else None,
                'debt_to_equity': info.get('debtToEquity'),
                'current_ratio': info.get('currentRatio'),
                'analyst_rating': self._get_analyst_rating(ticker),
                'next_earnings': self._get_next_earnings(ticker),
                'next_earnings_days': self._days_to_earnings(ticker)
            }

            return analysis

        except Exception as e:
            logger.error(f"Error in fundamental analysis for {symbol}: {e}")
            return {}

    async def analyze(self, symbol: str) -> Dict:
        """Async wrapper for fundamental analysis"""
        return self.analyze_sync(symbol)

    def _get_analyst_rating(self, ticker) -> str:
        """Get analyst consensus rating"""
        try:
            recommendations = ticker.recommendations
            if recommendations is not None and not recommendations.empty:
                recent = recommendations.tail(10)
                if 'strongBuy' in recent.columns:
                    avg_score = (
                        recent['strongBuy'].sum() * 5 +
                        recent['buy'].sum() * 4 +
                        recent['hold'].sum() * 3 +
                        recent['sell'].sum() * 2 +
                        recent['strongSell'].sum() * 1
                    ) / len(recent)

                    if avg_score >= 4.5:
                        return "Strong Buy"
                    elif avg_score >= 3.5:
                        return "Buy"
                    elif avg_score >= 2.5:
                        return "Hold"
                    elif avg_score >= 1.5:
                        return "Sell"
                    else:
                        return "Strong Sell"
        except:
            pass
        return "N/A"

    def _get_next_earnings(self, ticker) -> str:
        """Get next earnings date"""
        try:
            calendar = ticker.calendar
            if calendar is not None and not calendar.empty:
                if 'Earnings Date' in calendar.index:
                    earnings_dates = calendar.loc['Earnings Date']
                    if hasattr(earnings_dates, 'iloc') and len(earnings_dates) > 0:
                        next_date = earnings_dates.iloc[0]
                        if pd.notna(next_date):
                            return next_date.strftime('%Y-%m-%d')
        except:
            pass
        return "N/A"

    def _days_to_earnings(self, ticker) -> int:
        """Calculate days to next earnings"""
        try:
            earnings_date_str = self._get_next_earnings(ticker)
            if earnings_date_str != "N/A":
                earnings_date = datetime.strptime(earnings_date_str, '%Y-%m-%d')
                return (earnings_date - datetime.now()).days
        except:
            pass
        return 999


class TechnicalAnalyzer:
    """Analyze technical indicators"""

    def analyze_sync(self, symbol: str) -> Dict:
        """Synchronous technical analysis"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period='6mo')

            if hist.empty:
                return {}

            close_prices = hist['Close'].values
            high_prices = hist['High'].values
            low_prices = hist['Low'].values
            volume = hist['Volume'].values

            # Calculate indicators
            analysis = {
                'current_price': float(close_prices[-1]),
                'trend': self._determine_trend(close_prices),
                'rsi': float(talib.RSI(close_prices, timeperiod=14)[-1]),
                'rsi_signal': self._interpret_rsi(talib.RSI(close_prices, timeperiod=14)[-1]),
                'macd_signal': self._get_macd_signal(close_prices),
                'support': self._find_support(low_prices[-50:]),
                'resistance': self._find_resistance(high_prices[-50:]),
                'ma_50': float(talib.SMA(close_prices, timeperiod=50)[-1]),
                'ma_200': float(talib.SMA(close_prices, timeperiod=200)[-1]) if len(close_prices) >= 200 else None,
                'volume_trend': self._analyze_volume(volume)
            }

            return analysis

        except Exception as e:
            logger.error(f"Error in technical analysis for {symbol}: {e}")
            return {}

    async def analyze(self, symbol: str) -> Dict:
        """Async wrapper for technical analysis"""
        return self.analyze_sync(symbol)

    def _determine_trend(self, prices: np.ndarray) -> str:
        """Determine price trend"""
        if len(prices) < 20:
            return "Unknown"

        sma_20 = talib.SMA(prices, timeperiod=20)[-1]
        sma_50 = talib.SMA(prices, timeperiod=50)[-1] if len(prices) >= 50 else sma_20

        current = prices[-1]

        if current > sma_20 > sma_50:
            return "Strong Uptrend"
        elif current > sma_20:
            return "Uptrend"
        elif current < sma_20 < sma_50:
            return "Strong Downtrend"
        elif current < sma_20:
            return "Downtrend"
        else:
            return "Sideways"

    def _interpret_rsi(self, rsi: float) -> str:
        """Interpret RSI value"""
        if rsi < 30:
            return "Oversold"
        elif rsi > 70:
            return "Overbought"
        else:
            return "Neutral"

    def _get_macd_signal(self, prices: np.ndarray) -> str:
        """Get MACD signal"""
        try:
            macd, signal, hist = talib.MACD(prices)
            if hist[-1] > 0 and hist[-2] <= 0:
                return "Bullish Crossover"
            elif hist[-1] < 0 and hist[-2] >= 0:
                return "Bearish Crossover"
            elif hist[-1] > 0:
                return "Bullish"
            else:
                return "Bearish"
        except:
            return "N/A"

    def _find_support(self, lows: np.ndarray) -> float:
        """Find nearest support level"""
        if len(lows) < 3:
            return float(np.min(lows))

        # Simple method: find recent local minima
        support_levels = []
        for i in range(1, len(lows) - 1):
            if lows[i] < lows[i-1] and lows[i] < lows[i+1]:
                support_levels.append(lows[i])

        if support_levels:
            return float(np.mean(support_levels[-3:]))  # Average of last 3 supports
        return float(np.min(lows))

    def _find_resistance(self, highs: np.ndarray) -> float:
        """Find nearest resistance level"""
        if len(highs) < 3:
            return float(np.max(highs))

        # Simple method: find recent local maxima
        resistance_levels = []
        for i in range(1, len(highs) - 1):
            if highs[i] > highs[i-1] and highs[i] > highs[i+1]:
                resistance_levels.append(highs[i])

        if resistance_levels:
            return float(np.mean(resistance_levels[-3:]))  # Average of last 3 resistances
        return float(np.max(highs))

    def _analyze_volume(self, volume: np.ndarray) -> str:
        """Analyze volume trend"""
        if len(volume) < 20:
            return "Insufficient data"

        recent_avg = np.mean(volume[-5:])
        historical_avg = np.mean(volume[-20:])

        if recent_avg > historical_avg * 1.5:
            return "High volume (bullish)"
        elif recent_avg < historical_avg * 0.7:
            return "Low volume (bearish)"
        else:
            return "Normal volume"


class SentimentAnalyzer:
    """Analyze market sentiment"""

    def analyze_sync(self, symbol: str) -> Dict:
        """Synchronous sentiment analysis"""
        # This would integrate with news APIs, social media APIs, etc.
        # For now, return placeholder data
        return {
            'news_sentiment': 'neutral',
            'social_sentiment': 'neutral',
            'analyst_sentiment': 'neutral',
            'insider_trading': 'neutral'
        }

    async def analyze(self, symbol: str) -> Dict:
        """Async wrapper for sentiment analysis"""
        return self.analyze_sync(symbol)


class MonteCarloSimulator:
    """Monte Carlo simulation for options probability"""

    def simulate(self, symbol: str, strike: float,
                days_to_expiry: int, num_simulations: int = 10000) -> Dict:
        """
        Run Monte Carlo simulation

        Args:
            symbol: Stock ticker
            strike: Strike price
            days_to_expiry: Days until expiration
            num_simulations: Number of simulation paths

        Returns:
            Simulation results
        """
        try:
            # Get historical data for volatility calculation
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period='1y')

            if hist.empty:
                return {'error': 'No historical data available'}

            # Calculate parameters
            current_price = float(hist['Close'].iloc[-1])
            returns = hist['Close'].pct_change().dropna()
            volatility = returns.std() * np.sqrt(252)
            drift = returns.mean() * 252

            # Run simulation
            dt = 1/252  # Daily steps
            num_steps = days_to_expiry

            # Generate random paths
            np.random.seed(42)  # For reproducibility
            price_paths = np.zeros((num_simulations, num_steps + 1))
            price_paths[:, 0] = current_price

            for t in range(1, num_steps + 1):
                z = np.random.standard_normal(num_simulations)
                price_paths[:, t] = price_paths[:, t-1] * np.exp(
                    (drift - 0.5 * volatility**2) * dt + volatility * np.sqrt(dt) * z
                )

            # Calculate probabilities
            final_prices = price_paths[:, -1]
            prob_above_strike = (final_prices > strike).mean()
            prob_profit = prob_above_strike  # For CSP

            # Calculate expected value
            itm_payoffs = np.maximum(strike - final_prices, 0)
            expected_loss = itm_payoffs.mean()

            # Percentile outcomes
            percentiles = np.percentile(final_prices, [5, 25, 50, 75, 95])

            return {
                'current_price': current_price,
                'strike': strike,
                'probability_profit': prob_profit,
                'probability_assignment': 1 - prob_profit,
                'expected_loss': expected_loss,
                'percentile_5': percentiles[0],
                'percentile_25': percentiles[1],
                'percentile_50': percentiles[2],
                'percentile_75': percentiles[3],
                'percentile_95': percentiles[4],
                'volatility_annual': volatility,
                'num_simulations': num_simulations
            }

        except Exception as e:
            logger.error(f"Error in Monte Carlo simulation: {e}")
            return {'error': str(e)}


# Example usage
if __name__ == "__main__":
    # Initialize advisor (provide API key for full functionality)
    advisor = AIOptionsAdvisor()

    # Example position
    position = {
        'symbol': 'AAPL',
        'current_strike': 180,
        'current_price': 175,
        'current_loss': 500,
        'loss_percentage': 2.78,
        'days_to_expiry': 15
    }

    # Example opportunities
    opportunities = [
        {
            'strike': 170,
            'premium': 2.50,
            'probability_profit': 0.75,
            'ai_score': 82
        }
    ]

    # Get recommendation
    recommendation = advisor.recommend_strategy(position, opportunities)
    print(recommendation)

    # Analyze Greeks
    greeks = advisor.analyze_option_greeks('AAPL', 170, '2024-01-19', 'put')
    print(f"\nGreeks Analysis:")
    print(f"Values: {greeks.get('values')}")
    print(f"Assessment: {greeks.get('overall_assessment')}")

    # Run Monte Carlo
    simulation = advisor.run_monte_carlo_simulation('AAPL', 170, 15)
    print(f"\nMonte Carlo Results:")
    print(f"Probability of Profit: {simulation.get('probability_profit', 0)*100:.1f}%")
    print(f"Expected Loss if Assigned: ${simulation.get('expected_loss', 0):.2f}")