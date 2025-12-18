"""
LLM Options Strategist - AI-Powered Options Strategy Generator

Uses local LLM to generate custom options strategies based on market outlook,
risk tolerance, and current market conditions.

Expected Impact: Personalized strategy recommendations with detailed analysis
Cost Savings: 80% reduction vs cloud LLMs

Author: Magnus Enhancement Team
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json

from src.magnus_local_llm import get_local_llm

logger = logging.getLogger(__name__)


class MarketOutlook(Enum):
    """Market outlook for a symbol"""
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"
    VOLATILE = "volatile"


class RiskTolerance(Enum):
    """Risk tolerance levels"""
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


@dataclass
class OptionsStrategy:
    """Single options strategy recommendation"""
    name: str
    outlook: MarketOutlook
    risk_level: RiskTolerance
    setup: str  # Step-by-step setup instructions
    max_profit: str
    max_loss: str
    breakeven: List[str]
    probability_of_profit: float
    expected_return: float
    holding_period: str
    greeks_summary: str
    ideal_entry: str
    exit_strategy: str
    risk_factors: List[str]
    why_this_strategy: str


@dataclass
class StrategyRecommendation:
    """Complete strategy recommendation for a symbol"""
    symbol: str
    current_price: float
    outlook: MarketOutlook
    risk_tolerance: RiskTolerance

    # Strategies (3 levels)
    conservative_strategy: OptionsStrategy
    moderate_strategy: OptionsStrategy
    aggressive_strategy: OptionsStrategy

    # Market context
    implied_volatility: float
    iv_rank: float
    earnings_date: Optional[datetime]
    technical_summary: str

    # Overall analysis
    overall_recommendation: str
    generated_at: datetime


class LLMOptionsStrategist:
    """
    AI-powered options strategy generator

    Features:
    - Custom strategy generation based on outlook and risk
    - Three-tier recommendations (conservative, moderate, aggressive)
    - Detailed setup instructions with Greeks
    - Risk/reward analysis
    - Entry/exit strategy guidance
    """

    def __init__(self, db_manager=None):
        """
        Initialize LLM Options Strategist

        Args:
            db_manager: Database manager for options data
        """
        self.db_manager = db_manager
        self.llm = get_local_llm()

        # LLM model for strategy generation
        self.STRATEGY_MODEL = "qwen2.5:32b"  # Best quality for complex analysis

        logger.info("LLMOptionsStrategist initialized")

    async def generate_strategies(
        self,
        symbol: str,
        outlook: MarketOutlook,
        risk_tolerance: RiskTolerance,
        current_price: Optional[float] = None,
        options_chain: Optional[List[Dict]] = None
    ) -> StrategyRecommendation:
        """
        Generate three-tier options strategies for a symbol

        Args:
            symbol: Stock symbol
            outlook: Market outlook (bullish, bearish, neutral, volatile)
            risk_tolerance: Risk tolerance (conservative, moderate, aggressive)
            current_price: Current stock price (fetched if not provided)
            options_chain: Options chain data (fetched if not provided)

        Returns:
            StrategyRecommendation with three strategies
        """
        try:
            logger.info(f"Generating strategies for {symbol} - {outlook.value} outlook, {risk_tolerance.value} risk")

            # Get current market data
            if not current_price or not options_chain:
                market_data = await self._get_market_data(symbol)
                current_price = market_data['current_price']
                options_chain = market_data['options_chain']
            else:
                market_data = {'current_price': current_price}

            # Get market context
            context = await self._get_market_context(symbol, current_price)

            # Build comprehensive prompt
            strategy_prompt = self._build_strategy_prompt(
                symbol, outlook, risk_tolerance, current_price, options_chain, context
            )

            # Get LLM strategy recommendations
            llm_response = await self.llm.generate(
                strategy_prompt,
                model=self.STRATEGY_MODEL,
                temperature=0.4  # Balanced creativity and consistency
            )

            # Parse response
            strategies = self._parse_strategy_response(llm_response)

            return StrategyRecommendation(
                symbol=symbol,
                current_price=current_price,
                outlook=outlook,
                risk_tolerance=risk_tolerance,
                conservative_strategy=strategies['conservative'],
                moderate_strategy=strategies['moderate'],
                aggressive_strategy=strategies['aggressive'],
                implied_volatility=context.get('iv', 0.0),
                iv_rank=context.get('iv_rank', 50.0),
                earnings_date=context.get('earnings_date'),
                technical_summary=context.get('technical_summary', ''),
                overall_recommendation=strategies.get('overall_recommendation', ''),
                generated_at=datetime.now()
            )

        except Exception as e:
            logger.error(f"Error generating strategies for {symbol}: {e}")
            raise

    async def _get_market_data(self, symbol: str) -> Dict:
        """Fetch current market data and options chain"""
        try:
            if not self.db_manager:
                return {'current_price': 0.0, 'options_chain': []}

            # Get current stock price
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()

                # Stock price
                cursor.execute(
                    "SELECT current_price FROM stocks WHERE symbol = %s",
                    (symbol,)
                )
                price_result = cursor.fetchone()
                current_price = price_result[0] if price_result else 0.0

                # Options chain (next 60 days, top 20 by volume)
                cursor.execute("""
                    SELECT
                        option_type, strike, expiration_date,
                        bid, ask, last_price, volume, open_interest,
                        implied_volatility, delta, gamma, theta, vega
                    FROM options
                    WHERE symbol = %s
                        AND expiration_date > NOW()
                        AND expiration_date <= NOW() + INTERVAL '60 days'
                        AND volume > 0
                    ORDER BY volume DESC
                    LIMIT 20
                """, (symbol,))

                options_chain = []
                for row in cursor.fetchall():
                    options_chain.append({
                        'type': row[0],
                        'strike': row[1],
                        'expiration': row[2],
                        'bid': row[3],
                        'ask': row[4],
                        'last': row[5],
                        'volume': row[6],
                        'oi': row[7],
                        'iv': row[8],
                        'delta': row[9],
                        'gamma': row[10],
                        'theta': row[11],
                        'vega': row[12]
                    })

                return {
                    'current_price': current_price,
                    'options_chain': options_chain
                }

        except Exception as e:
            logger.error(f"Error fetching market data: {e}")
            return {'current_price': 0.0, 'options_chain': []}

    async def _get_market_context(self, symbol: str, current_price: float) -> Dict:
        """Get market context (IV, earnings, technicals)"""
        try:
            context = {
                'iv': 0.0,
                'iv_rank': 50.0,
                'earnings_date': None,
                'technical_summary': ''
            }

            if not self.db_manager:
                return context

            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()

                # Get IV metrics
                cursor.execute("""
                    SELECT AVG(implied_volatility) as avg_iv
                    FROM options
                    WHERE symbol = %s AND implied_volatility IS NOT NULL
                """, (symbol,))
                iv_result = cursor.fetchone()
                if iv_result and iv_result[0]:
                    context['iv'] = float(iv_result[0])

                # Get earnings date
                cursor.execute("""
                    SELECT earnings_date
                    FROM stocks
                    WHERE symbol = %s AND earnings_date IS NOT NULL
                """, (symbol,))
                earnings_result = cursor.fetchone()
                if earnings_result and earnings_result[0]:
                    context['earnings_date'] = earnings_result[0]

            # Add technical summary (simplified)
            if current_price:
                context['technical_summary'] = f"Current price: ${current_price:.2f}"

            return context

        except Exception as e:
            logger.error(f"Error getting market context: {e}")
            return {'iv': 0.0, 'iv_rank': 50.0, 'earnings_date': None, 'technical_summary': ''}

    def _build_strategy_prompt(
        self,
        symbol: str,
        outlook: MarketOutlook,
        risk_tolerance: RiskTolerance,
        current_price: float,
        options_chain: List[Dict],
        context: Dict
    ) -> str:
        """Build comprehensive strategy generation prompt"""

        # Format options chain
        options_str = self._format_options_chain(options_chain[:10])  # Top 10

        # Earnings warning
        earnings_warning = ""
        if context.get('earnings_date'):
            days_to_earnings = (context['earnings_date'] - datetime.now()).days
            if 0 < days_to_earnings <= 30:
                earnings_warning = f"⚠️ EARNINGS in {days_to_earnings} days - consider IV crush risk"

        prompt = f"""You are a professional options trader and strategist. Generate THREE options strategies for this setup:

**SYMBOL**: {symbol}
**CURRENT PRICE**: ${current_price:.2f}
**MARKET OUTLOOK**: {outlook.value.upper()}
**RISK TOLERANCE**: {risk_tolerance.value.upper()}
**IMPLIED VOLATILITY**: {context.get('iv', 0)*100:.1f}% (IV Rank: {context.get('iv_rank', 50):.0f})
{earnings_warning}

**AVAILABLE OPTIONS (Top 10 by volume)**:
{options_str}

**GENERATE 3 STRATEGIES**:
Provide a JSON response with three strategies: conservative, moderate, and aggressive.

Each strategy should include:
- name: Strategy name (e.g., "Bull Put Spread", "Long Call", "Iron Condor")
- setup: Exact strikes and expirations to trade
- max_profit: Maximum profit potential
- max_loss: Maximum loss (risk)
- breakeven: Breakeven price(s)
- pop: Probability of profit (0-100)
- expected_return: Expected return in %
- holding_period: Recommended holding period
- greeks: Summary of Greeks exposure
- entry: Ideal entry conditions
- exit: Exit strategy
- risks: Key risk factors (list of 2-3)
- why: Why this strategy fits the outlook (2-3 sentences)

**STRATEGY GUIDELINES**:
- **Conservative**: Defined risk, lower profit potential, high probability of profit (>60%)
- **Moderate**: Balanced risk/reward, medium probability of profit (40-60%)
- **Aggressive**: Higher risk, higher profit potential, lower probability of profit (<40%)

Match strategies to the {outlook.value} outlook:
- Bullish: Long calls, bull spreads, covered calls, poor man's covered call
- Bearish: Long puts, bear spreads, credit call spreads
- Neutral: Iron condors, strangles, butterflies, calendars
- Volatile: Straddles, strangles, long volatility plays

**JSON FORMAT**:
{{
    "conservative": {{
        "name": "Strategy name",
        "setup": "Detailed setup instructions",
        "max_profit": "$X or X%",
        "max_loss": "$X or X%",
        "breakeven": ["$X", "$Y"],
        "pop": 70.0,
        "expected_return": 15.0,
        "holding_period": "X days/weeks",
        "greeks": "Delta: X, Theta: Y, Vega: Z",
        "entry": "Entry criteria",
        "exit": "Exit criteria",
        "risks": ["Risk 1", "Risk 2"],
        "why": "Explanation..."
    }},
    "moderate": {{ ... }},
    "aggressive": {{ ... }},
    "overall_recommendation": "2-3 sentence summary of which strategy to use and why"
}}

Be specific with strikes and expirations. Use real data from the options chain above."""

        return prompt

    def _format_options_chain(self, options: List[Dict]) -> str:
        """Format options chain for prompt"""
        if not options:
            return "No options data available"

        formatted = []
        for opt in options:
            exp_date = opt['expiration'].strftime('%m/%d/%y') if isinstance(opt['expiration'], datetime) else str(opt['expiration'])
            formatted.append(
                f"{opt['type']} ${opt['strike']:.0f} exp {exp_date} | "
                f"Bid/Ask: ${opt['bid']:.2f}/${opt['ask']:.2f} | "
                f"Vol: {opt['volume']:,} | IV: {opt.get('iv', 0)*100:.1f}% | "
                f"Delta: {opt.get('delta', 0):.2f}"
            )

        return "\n".join(formatted)

    def _parse_strategy_response(self, response: str) -> Dict:
        """Parse LLM strategy response"""
        try:
            # Extract JSON from response
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            elif "```" in response:
                json_start = response.find("```") + 3
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            elif "{" in response:
                json_start = response.find("{")
                json_end = response.rfind("}") + 1
                json_str = response[json_start:json_end]
            else:
                raise ValueError("No JSON found in response")

            data = json.loads(json_str)

            # Convert to OptionsStrategy objects
            return {
                'conservative': self._dict_to_strategy(data['conservative'], RiskTolerance.CONSERVATIVE),
                'moderate': self._dict_to_strategy(data['moderate'], RiskTolerance.MODERATE),
                'aggressive': self._dict_to_strategy(data['aggressive'], RiskTolerance.AGGRESSIVE),
                'overall_recommendation': data.get('overall_recommendation', '')
            }

        except Exception as e:
            logger.error(f"Failed to parse strategy response: {e}")
            # Return fallback strategies
            return self._create_fallback_strategies()

    def _dict_to_strategy(self, data: Dict, risk_level: RiskTolerance) -> OptionsStrategy:
        """Convert dictionary to OptionsStrategy object"""
        return OptionsStrategy(
            name=data.get('name', 'Unknown Strategy'),
            outlook=MarketOutlook.NEUTRAL,  # Set by caller
            risk_level=risk_level,
            setup=data.get('setup', 'No setup provided'),
            max_profit=data.get('max_profit', 'Unknown'),
            max_loss=data.get('max_loss', 'Unknown'),
            breakeven=data.get('breakeven', []),
            probability_of_profit=data.get('pop', 50.0),
            expected_return=data.get('expected_return', 0.0),
            holding_period=data.get('holding_period', 'Unknown'),
            greeks_summary=data.get('greeks', 'N/A'),
            ideal_entry=data.get('entry', 'No entry criteria'),
            exit_strategy=data.get('exit', 'No exit strategy'),
            risk_factors=data.get('risks', []),
            why_this_strategy=data.get('why', 'No explanation')
        )

    def _create_fallback_strategies(self) -> Dict:
        """Create fallback strategies if parsing fails"""
        fallback = OptionsStrategy(
            name="Analysis Unavailable",
            outlook=MarketOutlook.NEUTRAL,
            risk_level=RiskTolerance.MODERATE,
            setup="Strategy generation failed",
            max_profit="Unknown",
            max_loss="Unknown",
            breakeven=[],
            probability_of_profit=50.0,
            expected_return=0.0,
            holding_period="Unknown",
            greeks_summary="N/A",
            ideal_entry="N/A",
            exit_strategy="N/A",
            risk_factors=["Strategy generation failed"],
            why_this_strategy="Failed to generate strategy"
        )

        return {
            'conservative': fallback,
            'moderate': fallback,
            'aggressive': fallback,
            'overall_recommendation': 'Strategy generation failed'
        }

    async def compare_strategies(
        self,
        symbol: str,
        strategies: List[str],
        outlook: MarketOutlook
    ) -> str:
        """
        Compare multiple strategies for a given outlook

        Args:
            symbol: Stock symbol
            strategies: List of strategy names to compare
            outlook: Market outlook

        Returns:
            Detailed comparison analysis
        """
        prompt = f"""Compare these {len(strategies)} options strategies for {symbol} with a {outlook.value} outlook:

Strategies: {', '.join(strategies)}

Provide a detailed comparison covering:
1. Risk/reward profile of each
2. Capital requirements
3. Best market conditions for each
4. Complexity level
5. Which one is best for this {outlook.value} outlook and why

Be specific and provide actionable insights."""

        response = await self.llm.generate(prompt, model=self.STRATEGY_MODEL)
        return response
