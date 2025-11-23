"""
AI Options Analysis Agent
Single unified agent that analyzes options opportunities using the scoring engine

For Phase 1-2: Simple rule-based agent with scoring
For Phase 3-4: Will be upgraded to LLM-powered multi-agent system
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import time

from .scoring_engine import MultiCriteriaScorer
from .ai_options_db_manager import AIOptionsDBManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OptionsAnalysisAgent:
    """
    Main agent for analyzing options opportunities

    Current Implementation (Phase 1-2):
    - Uses rule-based scoring engine
    - Analyzes opportunities from database
    - Saves results to database
    - No LLM required (works offline)

    Future Enhancement (Phase 3-4):
    - LLM-powered reasoning with Claude/GPT-4
    - Multi-agent orchestration (6 specialized agents)
    - RAG knowledge base
    - Real-time market data integration
    """

    def __init__(self, db_manager: Optional[AIOptionsDBManager] = None,
                 scorer: Optional[MultiCriteriaScorer] = None,
                 llm_manager: Optional[Any] = None):
        """
        Initialize the Options Analysis Agent

        Args:
            db_manager: Database manager instance (creates new if None)
            scorer: Multi-criteria scorer instance (creates new if None)
            llm_manager: LLM manager for AI reasoning (optional)
        """
        self.db_manager = db_manager or AIOptionsDBManager()
        self.scorer = scorer or MultiCriteriaScorer()
        self.llm_manager = llm_manager

        logger.info("OptionsAnalysisAgent initialized" +
                   (" with LLM support" if llm_manager else ""))

    def analyze_opportunity(self, opportunity: Dict[str, Any],
                          save_to_db: bool = True,
                          use_llm: bool = False,
                          llm_provider: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze a single options opportunity

        Args:
            opportunity: Dict with opportunity data
            save_to_db: Whether to save analysis to database
            use_llm: Whether to use LLM for enhanced reasoning (requires llm_manager)
            llm_provider: Specific LLM provider to use (None for auto-select)

        Returns:
            Dict with analysis results including scores and reasoning
        """
        start_time = time.time()

        try:
            # Score the opportunity using multi-criteria engine
            analysis = self.scorer.score_opportunity(opportunity)

            # Generate reasoning based on mode
            if use_llm and self.llm_manager:
                # LLM-powered reasoning
                llm_result = self._generate_llm_reasoning(opportunity, analysis, llm_provider)
                reasoning = llm_result['reasoning']
                key_risks = llm_result['risks']
                key_opportunities = llm_result['opportunities']
                llm_model = llm_result['model']
                llm_tokens = llm_result['tokens']
            else:
                # Rule-based reasoning (default)
                reasoning = self._generate_reasoning(opportunity, analysis)
                key_risks = self._identify_risks(opportunity, analysis)
                key_opportunities = self._identify_opportunities(opportunity, analysis)
                llm_model = 'rule_based_v1'
                llm_tokens = 0

            # Add reasoning to analysis
            analysis['reasoning'] = reasoning
            analysis['key_risks'] = key_risks
            analysis['key_opportunities'] = key_opportunities

            # Add strategy recommendation
            analysis['strategy'] = self._recommend_strategy(opportunity, analysis)

            # Add metadata
            processing_time_ms = int((time.time() - start_time) * 1000)
            analysis['llm_model'] = llm_model
            analysis['llm_tokens_used'] = llm_tokens
            analysis['processing_time_ms'] = processing_time_ms

            # Save to database if requested
            if save_to_db:
                analysis_id = self.db_manager.save_analysis(analysis)
                analysis['id'] = analysis_id

            logger.info(f"Analyzed {opportunity.get('symbol')}: "
                       f"{analysis['final_score']}/100 ({analysis['recommendation']}) "
                       f"in {processing_time_ms}ms" +
                       (f" using {llm_model}" if use_llm else ""))

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing opportunity: {e}")
            return {
                'symbol': opportunity.get('symbol', 'ERROR'),
                'final_score': 0,
                'recommendation': 'ERROR',
                'reasoning': f'Analysis failed: {str(e)}'
            }

    def analyze_watchlist(self, watchlist_name: str,
                         dte_range: tuple = (20, 40),
                         delta_range: tuple = (-0.45, -0.15),
                         min_premium: float = 0,
                         limit: int = 50,
                         use_llm: bool = False,
                         llm_provider: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Analyze all opportunities from a specific watchlist

        Args:
            watchlist_name: Name of TradingView watchlist
            dte_range: (min_dte, max_dte) tuple
            delta_range: (min_delta, max_delta) tuple
            min_premium: Minimum premium in dollars
            limit: Maximum opportunities to analyze
            use_llm: Whether to use LLM for enhanced reasoning
            llm_provider: Specific LLM provider to use (None for auto-select)

        Returns:
            List of analysis results, sorted by final_score
        """
        logger.info(f"Analyzing watchlist: {watchlist_name}")

        # Get watchlist symbols
        symbols = self.db_manager.get_watchlist_symbols(watchlist_name)
        if not symbols:
            logger.warning(f"No symbols found in watchlist: {watchlist_name}")
            return []

        logger.info(f"Found {len(symbols)} symbols in watchlist")

        # Get opportunities for these symbols
        opportunities = self.db_manager.get_opportunities(
            symbols=symbols,
            dte_range=dte_range,
            delta_range=delta_range,
            min_premium=min_premium,
            limit=limit
        )

        # Analyze each opportunity
        analyses = []
        for opp in opportunities:
            analysis = self.analyze_opportunity(opp, save_to_db=True,
                                              use_llm=use_llm,
                                              llm_provider=llm_provider)
            analyses.append(analysis)

        # Sort by final score
        analyses.sort(key=lambda x: x['final_score'], reverse=True)

        logger.info(f"Analyzed {len(analyses)} opportunities from watchlist")
        return analyses

    def analyze_all_stocks(self,
                          dte_range: tuple = (20, 40),
                          delta_range: tuple = (-0.45, -0.15),
                          min_premium: float = 0,
                          limit: int = 100,
                          use_llm: bool = False,
                          llm_provider: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Analyze all stocks in database with options

        Args:
            dte_range: (min_dte, max_dte) tuple
            delta_range: (min_delta, max_delta) tuple
            min_premium: Minimum premium in dollars
            limit: Maximum opportunities to analyze
            use_llm: Whether to use LLM for enhanced reasoning
            llm_provider: Specific LLM provider to use (None for auto-select)

        Returns:
            List of analysis results, sorted by final_score
        """
        logger.info("Analyzing all stocks with options")

        # Get all opportunities (no symbol filter)
        opportunities = self.db_manager.get_opportunities(
            symbols=None,
            dte_range=dte_range,
            delta_range=delta_range,
            min_premium=min_premium,
            limit=limit
        )

        logger.info(f"Found {len(opportunities)} opportunities to analyze")

        # Analyze each opportunity
        analyses = []
        for opp in opportunities:
            analysis = self.analyze_opportunity(opp, save_to_db=True,
                                              use_llm=use_llm,
                                              llm_provider=llm_provider)
            analyses.append(analysis)

        # Sort by final score
        analyses.sort(key=lambda x: x['final_score'], reverse=True)

        logger.info(f"Analyzed {len(analyses)} total opportunities")
        return analyses

    def get_top_recommendations(self, days: int = 7,
                               min_score: int = 75) -> List[Dict[str, Any]]:
        """
        Get top recommendations from recent analyses

        Args:
            days: Look back this many days
            min_score: Minimum final score to include

        Returns:
            List of top recommendations
        """
        analyses = self.db_manager.get_recent_analyses(days=days, limit=100)

        # Filter by score
        top_picks = [a for a in analyses if a.get('final_score', 0) >= min_score]

        return top_picks

    def _generate_llm_reasoning(self, opportunity: Dict[str, Any],
                                analysis: Dict[str, Any],
                                provider_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate AI-powered reasoning using LLM

        Args:
            opportunity: Opportunity data
            analysis: Analysis results with scores
            provider_id: Specific provider to use (None for auto-select)

        Returns:
            Dict with reasoning, risks, opportunities, model name, and token count
        """
        if not self.llm_manager:
            # Fallback to rule-based
            return {
                'reasoning': self._generate_reasoning(opportunity, analysis),
                'risks': self._identify_risks(opportunity, analysis),
                'opportunities': self._identify_opportunities(opportunity, analysis),
                'model': 'rule_based_v1',
                'tokens': 0
            }

        # Build comprehensive prompt for LLM
        symbol = opportunity.get('symbol', 'UNKNOWN')
        strike = opportunity.get('strike_price', 0)
        current_price = opportunity.get('current_price', 0)
        dte = opportunity.get('dte', 0)
        delta = opportunity.get('delta', 0)
        iv = opportunity.get('iv', 0)
        premium = opportunity.get('premium', 0) / 100  # Convert cents to dollars
        monthly_return = opportunity.get('monthly_return', 0)
        annual_return = opportunity.get('annual_return', 0)

        # Scores
        fundamental_score = analysis.get('fundamental_score', 0)
        technical_score = analysis.get('technical_score', 0)
        greeks_score = analysis.get('greeks_score', 0)
        risk_score = analysis.get('risk_score', 0)
        sentiment_score = analysis.get('sentiment_score', 0)
        final_score = analysis.get('final_score', 0)
        recommendation = analysis.get('recommendation', 'UNKNOWN')

        # Company data
        sector = opportunity.get('sector', 'Unknown')
        pe_ratio = opportunity.get('pe_ratio')
        market_cap = opportunity.get('market_cap', 0)

        prompt = f"""Analyze this cash-secured put (CSP) opportunity for {symbol}:

OPPORTUNITY DETAILS:
- Current Price: ${current_price:.2f}
- Strike Price: ${strike:.2f}
- Days to Expiration (DTE): {dte}
- Premium: ${premium:.2f}
- Delta: {delta:.3f}
- Implied Volatility (IV): {iv*100:.1f}%
- Monthly Return: {monthly_return:.2f}%
- Annual Return: {annual_return:.1f}%

COMPANY FUNDAMENTALS:
- Sector: {sector}
- Market Cap: ${market_cap/1e9:.2f}B
{f'- P/E Ratio: {pe_ratio:.1f}' if pe_ratio else '- P/E Ratio: N/A'}

AI SCORING SYSTEM RESULTS:
- Fundamental Score: {fundamental_score}/100
- Technical Score: {technical_score}/100
- Greeks Score: {greeks_score}/100
- Risk Score: {risk_score}/100
- Sentiment Score: {sentiment_score}/100
- FINAL SCORE: {final_score}/100
- RECOMMENDATION: {recommendation}

Provide a concise analysis (3-4 sentences) addressing:
1. Overall assessment based on the {final_score}/100 score
2. Key strengths (what makes this a good/bad opportunity)
3. Main risk factors to consider
4. Whether this aligns with conservative CSP strategy

Then list:
- Top 3 Key Risks (bullet points, brief)
- Top 3 Key Opportunities (bullet points, brief)

Format your response as:
ANALYSIS: [your 3-4 sentence analysis]

RISKS:
- [risk 1]
- [risk 2]
- [risk 3]

OPPORTUNITIES:
- [opportunity 1]
- [opportunity 2]
- [opportunity 3]"""

        try:
            # Generate with LLM
            result = self.llm_manager.generate(
                prompt=prompt,
                provider_id=provider_id,
                max_tokens=500,
                temperature=0.7
            )

            llm_text = result.get('text', '')
            llm_model = f"{result.get('provider', 'unknown')}:{result.get('model', 'unknown')}"
            llm_tokens = result.get('tokens_used', 0)

            # Parse LLM response
            reasoning = ''
            risks = ''
            opportunities = ''

            if 'ANALYSIS:' in llm_text:
                parts = llm_text.split('ANALYSIS:')[1]
                if 'RISKS:' in parts:
                    reasoning = parts.split('RISKS:')[0].strip()
                    risks_part = parts.split('RISKS:')[1]
                    if 'OPPORTUNITIES:' in risks_part:
                        risks = risks_part.split('OPPORTUNITIES:')[0].strip()
                        opportunities = risks_part.split('OPPORTUNITIES:')[1].strip()
                    else:
                        risks = risks_part.strip()
                else:
                    reasoning = parts.strip()
            else:
                # Fallback: use entire response as reasoning
                reasoning = llm_text[:500]  # Truncate if needed

            # Fallback to rule-based if parsing failed
            if not reasoning:
                reasoning = self._generate_reasoning(opportunity, analysis)
            if not risks:
                risks = self._identify_risks(opportunity, analysis)
            if not opportunities:
                opportunities = self._identify_opportunities(opportunity, analysis)

            return {
                'reasoning': reasoning,
                'risks': risks,
                'opportunities': opportunities,
                'model': llm_model,
                'tokens': llm_tokens
            }

        except Exception as e:
            logger.error(f"LLM reasoning failed: {e}, falling back to rule-based")
            # Fallback to rule-based on error
            return {
                'reasoning': self._generate_reasoning(opportunity, analysis),
                'risks': self._identify_risks(opportunity, analysis),
                'opportunities': self._identify_opportunities(opportunity, analysis),
                'model': 'rule_based_v1',
                'tokens': 0
            }

    def _generate_reasoning(self, opportunity: Dict[str, Any],
                           analysis: Dict[str, Any]) -> str:
        """Generate human-readable reasoning for the recommendation"""
        symbol = opportunity.get('symbol', 'UNKNOWN')
        final_score = analysis.get('final_score', 0)
        recommendation = analysis.get('recommendation', 'UNKNOWN')

        # Get individual scores
        fundamental = analysis.get('fundamental_score', 0)
        technical = analysis.get('technical_score', 0)
        greeks = analysis.get('greeks_score', 0)
        risk = analysis.get('risk_score', 0)

        # Build reasoning
        reasoning_parts = []

        # Overall assessment
        if final_score >= 85:
            reasoning_parts.append(f"{symbol} is an excellent CSP opportunity with strong fundamentals and favorable Greeks.")
        elif final_score >= 75:
            reasoning_parts.append(f"{symbol} is a good CSP opportunity with solid metrics across key criteria.")
        elif final_score >= 60:
            reasoning_parts.append(f"{symbol} is a moderate opportunity with some positive factors to consider.")
        else:
            reasoning_parts.append(f"{symbol} shows weaknesses in key criteria and requires caution.")

        # Fundamental insights
        if fundamental >= 80:
            pe_ratio = opportunity.get('pe_ratio')
            sector = opportunity.get('sector')
            reasoning_parts.append(f"Strong fundamentals with {sector} sector positioning" +
                                 (f" and P/E of {pe_ratio:.1f}" if pe_ratio else ""))
        elif fundamental < 50:
            reasoning_parts.append("Weak fundamental metrics suggest potential business headwinds.")

        # Greeks insights
        delta = opportunity.get('delta')
        iv = opportunity.get('iv')
        if greeks >= 80:
            reasoning_parts.append(f"Excellent Greeks profile with delta of {delta:.2f}" +
                                 (f" and IV of {iv*100:.1f}%" if iv else ""))
        elif greeks < 50:
            reasoning_parts.append("Greeks profile indicates suboptimal risk/reward characteristics.")

        # Risk insights
        monthly_return = opportunity.get('monthly_return')
        annual_return = opportunity.get('annual_return')
        if risk >= 80:
            reasoning_parts.append(f"Low risk profile with attractive returns" +
                                 (f" ({monthly_return:.2f}% monthly, {annual_return:.1f}% annualized)"
                                  if monthly_return else ""))
        elif risk < 50:
            reasoning_parts.append("Elevated risk factors require careful consideration.")

        return " ".join(reasoning_parts)

    def _identify_risks(self, opportunity: Dict[str, Any],
                       analysis: Dict[str, Any]) -> str:
        """Identify key risks for this opportunity"""
        risks = []

        # Check fundamental risks
        pe_ratio = opportunity.get('pe_ratio')
        if pe_ratio and pe_ratio > 40:
            risks.append(f"High P/E ratio ({pe_ratio:.1f}) suggests overvaluation")

        eps = opportunity.get('eps')
        if eps and eps < 0:
            risks.append("Negative EPS indicates unprofitability")

        # Check Greeks risks
        delta = opportunity.get('delta')
        if delta and abs(delta) > 0.4:
            risks.append(f"High delta ({delta:.2f}) increases assignment probability")

        iv = opportunity.get('iv')
        if iv and iv < 0.2:
            risks.append(f"Low IV ({iv*100:.1f}%) limits premium collection")

        # Check technical risks
        volume = opportunity.get('volume')
        if volume and volume < 100:
            risks.append(f"Low volume ({volume}) may cause liquidity issues")

        # Check risk score
        risk_score = analysis.get('risk_score', 0)
        if risk_score < 50:
            risks.append("Overall risk profile exceeds recommended thresholds")

        if not risks:
            return "No significant risks identified"

        return "; ".join(risks)

    def _identify_opportunities(self, opportunity: Dict[str, Any],
                               analysis: Dict[str, Any]) -> str:
        """Identify key opportunities/strengths"""
        opps = []

        # Check premium
        premium = opportunity.get('premium')
        monthly_return = opportunity.get('monthly_return')
        if premium and monthly_return and monthly_return > 2.0:
            opps.append(f"Excellent premium of ${premium/100:.2f} ({monthly_return:.2f}% monthly)")

        # Check sector strength
        sector = opportunity.get('sector')
        if sector in ['Technology', 'Healthcare']:
            opps.append(f"Strong {sector} sector positioning")

        # Check fundamentals
        fundamental_score = analysis.get('fundamental_score', 0)
        if fundamental_score >= 85:
            opps.append("Excellent fundamental strength provides downside protection")

        # Check Greeks
        greeks_score = analysis.get('greeks_score', 0)
        if greeks_score >= 85:
            opps.append("Optimal Greeks configuration for CSP strategy")

        # Check market cap (stability)
        market_cap = opportunity.get('market_cap')
        if market_cap and market_cap >= 50_000_000_000:
            opps.append("Large-cap stability reduces volatility risk")

        if not opps:
            return "Standard opportunity with moderate upside potential"

        return "; ".join(opps)

    def _recommend_strategy(self, opportunity: Dict[str, Any],
                           analysis: Dict[str, Any]) -> str:
        """Recommend specific options strategy"""
        final_score = analysis.get('final_score', 0)
        delta = opportunity.get('delta')
        dte = opportunity.get('dte')

        # For Phase 1, we only support CSP
        # Future phases will add: credit spreads, iron condors, calendars, etc.

        if final_score >= 85:
            return "Cash-Secured Put (CSP) - Aggressive"
        elif final_score >= 75:
            return "Cash-Secured Put (CSP) - Standard"
        elif final_score >= 60:
            return "Cash-Secured Put (CSP) - Conservative"
        else:
            return "Not Recommended"


# Standalone test
if __name__ == "__main__":
    # Test the agent
    agent = OptionsAnalysisAgent()

    # Test analyzing a single opportunity from database
    print("\n=== Testing AI Options Agent ===\n")

    # Get some opportunities
    opportunities = agent.db_manager.get_opportunities(
        symbols=None,
        dte_range=(20, 40),
        delta_range=(-0.45, -0.15),
        min_premium=100,
        limit=5
    )

    if opportunities:
        print(f"Found {len(opportunities)} opportunities to analyze\n")

        for opp in opportunities[:3]:  # Analyze top 3
            analysis = agent.analyze_opportunity(opp, save_to_db=False)

            print(f"--- {analysis['symbol']} ---")
            print(f"Strike: ${analysis['strike_price']:.2f}, DTE: {analysis['dte']}")
            print(f"Scores: F:{analysis['fundamental_score']} T:{analysis['technical_score']} "
                  f"G:{analysis['greeks_score']} R:{analysis['risk_score']} S:{analysis['sentiment_score']}")
            print(f"Final Score: {analysis['final_score']}/100")
            print(f"Recommendation: {analysis['recommendation']} ({analysis['confidence']}% confidence)")
            print(f"Strategy: {analysis['strategy']}")
            print(f"Reasoning: {analysis['reasoning']}")
            print(f"Risks: {analysis['key_risks']}")
            print(f"Opportunities: {analysis['key_opportunities']}")
            print(f"Processing Time: {analysis['processing_time_ms']}ms\n")
    else:
        print("No opportunities found in database. Run database sync first.")
