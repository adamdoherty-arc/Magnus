"""
Research Orchestrator
Coordinates 4 specialist agents using CrewAI and synthesizes results with LLM
"""

import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import asyncio
import time

from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from langchain_community.llms import Ollama

from src.agents.ai_research.models import (
    ResearchReport,
    ResearchRequest,
    FundamentalAnalysis,
    TechnicalAnalysis,
    SentimentAnalysis,
    OptionsAnalysis,
    TradeRecommendation,
    AnalysisMetadata,
    TradeAction
)
from src.agents.ai_research.agents.fundamental_agent import FundamentalAgent
from src.agents.ai_research.agents.technical_agent import TechnicalAgent
from src.agents.ai_research.agents.sentiment_agent import SentimentAgent
from src.agents.ai_research.agents.options_agent import OptionsAgent

logger = logging.getLogger(__name__)


class ResearchOrchestrator:
    """
    Orchestrates multi-agent stock analysis using CrewAI

    Coordinates 4 specialist agents:
    1. Fundamental Analyst - Company financials, earnings, valuation
    2. Technical Analyst - Price action, indicators, chart patterns
    3. Sentiment Analyst - News, social media, insider trades, analyst ratings
    4. Options Strategist - IV analysis, options flow, strategy recommendations

    Uses LLM to synthesize results into coherent research report
    """

    def __init__(
        self,
        llm_provider: str = "ollama",  # 'ollama' or 'openai'
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000
    ):
        """
        Initialize orchestrator

        Args:
            llm_provider: LLM provider ('ollama' or 'openai')
            model_name: Model name (defaults: 'llama3.2' for Ollama, 'gpt-4' for OpenAI)
            temperature: LLM temperature (0.0-1.0)
            max_tokens: Maximum tokens for LLM response
        """
        self.llm_provider = llm_provider
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Initialize LLM
        if llm_provider == "ollama":
            self.model_name = model_name or "llama3.2"
            self.llm = Ollama(
                model=self.model_name,
                temperature=temperature
            )
            logger.info(f"Initialized Ollama LLM: {self.model_name}")

        elif llm_provider == "openai":
            self.model_name = model_name or "gpt-4"
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable required for OpenAI")

            self.llm = ChatOpenAI(
                model=self.model_name,
                temperature=temperature,
                max_tokens=max_tokens,
                api_key=api_key
            )
            logger.info(f"Initialized OpenAI LLM: {self.model_name}")

        else:
            raise ValueError(f"Invalid LLM provider: {llm_provider}. Use 'ollama' or 'openai'")

        # Initialize specialist agents
        self.fundamental_agent = FundamentalAgent()
        self.technical_agent = TechnicalAgent()
        self.sentiment_agent = SentimentAgent()
        self.options_agent = OptionsAgent()

        # Track metrics
        self.total_api_calls = 0
        self.processing_start_time = 0

    async def analyze(self, request: ResearchRequest) -> ResearchReport:
        """
        Run multi-agent analysis and synthesize results

        Args:
            request: Research request with symbol and options

        Returns:
            Complete research report
        """
        self.processing_start_time = time.time()
        self.total_api_calls = 0

        symbol = request.symbol
        logger.info(f"Starting multi-agent analysis for {symbol}")

        # Determine which agents to run
        agents_to_run = request.include_sections or ['fundamental', 'technical', 'sentiment', 'options']

        # Run specialist agents in parallel
        tasks = []
        agent_results = {}
        failed_agents = []

        if 'fundamental' in agents_to_run:
            tasks.append(self._run_fundamental_analysis(symbol))
        if 'technical' in agents_to_run:
            tasks.append(self._run_technical_analysis(symbol))
        if 'sentiment' in agents_to_run:
            tasks.append(self._run_sentiment_analysis(symbol))
        if 'options' in agents_to_run:
            tasks.append(self._run_options_analysis(symbol))

        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        result_idx = 0
        if 'fundamental' in agents_to_run:
            if isinstance(results[result_idx], Exception):
                logger.error(f"Fundamental analysis failed: {results[result_idx]}")
                failed_agents.append('fundamental')
                agent_results['fundamental'] = self._get_fallback_fundamental()
            else:
                agent_results['fundamental'] = results[result_idx]
            result_idx += 1

        if 'technical' in agents_to_run:
            if isinstance(results[result_idx], Exception):
                logger.error(f"Technical analysis failed: {results[result_idx]}")
                failed_agents.append('technical')
                agent_results['technical'] = self._get_fallback_technical()
            else:
                agent_results['technical'] = results[result_idx]
            result_idx += 1

        if 'sentiment' in agents_to_run:
            if isinstance(results[result_idx], Exception):
                logger.error(f"Sentiment analysis failed: {results[result_idx]}")
                failed_agents.append('sentiment')
                agent_results['sentiment'] = self._get_fallback_sentiment()
            else:
                agent_results['sentiment'] = results[result_idx]
            result_idx += 1

        if 'options' in agents_to_run:
            if isinstance(results[result_idx], Exception):
                logger.error(f"Options analysis failed: {results[result_idx]}")
                failed_agents.append('options')
                agent_results['options'] = self._get_fallback_options()
            else:
                agent_results['options'] = results[result_idx]
            result_idx += 1

        # Use CrewAI to synthesize insights
        logger.info(f"Synthesizing results with {self.llm_provider}")
        synthesis = await self._synthesize_with_crew(symbol, agent_results, request.user_position)

        # Build final report
        processing_time_ms = int((time.time() - self.processing_start_time) * 1000)

        metadata = AnalysisMetadata(
            api_calls_used=self.total_api_calls,
            processing_time_ms=processing_time_ms,
            agents_executed=len(agents_to_run),
            agents_failed=failed_agents,
            cache_expires_at=datetime.now() + timedelta(minutes=30),
            llm_model=self.model_name,
            llm_tokens_used=synthesis.get('tokens_used', 0)
        )

        report = ResearchReport(
            symbol=symbol,
            timestamp=datetime.now(),
            cached=False,
            overall_rating=synthesis.get('overall_rating', 3.0),
            quick_summary=synthesis.get('quick_summary', ''),
            fundamental=agent_results.get('fundamental'),
            technical=agent_results.get('technical'),
            sentiment=agent_results.get('sentiment'),
            options=agent_results.get('options'),
            recommendation=synthesis.get('recommendation'),
            metadata=metadata
        )

        logger.info(f"Analysis complete for {symbol} in {processing_time_ms}ms")
        return report

    async def _run_fundamental_analysis(self, symbol: str) -> FundamentalAnalysis:
        """Run fundamental analysis"""
        logger.info(f"Running fundamental analysis for {symbol}")
        result = await self.fundamental_agent.analyze(symbol)
        self.total_api_calls += self.fundamental_agent.get_api_call_count()
        return result

    async def _run_technical_analysis(self, symbol: str) -> TechnicalAnalysis:
        """Run technical analysis"""
        logger.info(f"Running technical analysis for {symbol}")
        result = await self.technical_agent.analyze(symbol)
        self.total_api_calls += self.technical_agent.get_api_call_count()
        return result

    async def _run_sentiment_analysis(self, symbol: str) -> SentimentAnalysis:
        """Run sentiment analysis"""
        logger.info(f"Running sentiment analysis for {symbol}")
        result = await self.sentiment_agent.analyze(symbol)
        self.total_api_calls += self.sentiment_agent.get_api_call_count()
        return result

    async def _run_options_analysis(self, symbol: str) -> OptionsAnalysis:
        """Run options analysis"""
        logger.info(f"Running options analysis for {symbol}")
        result = await self.options_agent.analyze(symbol)
        self.total_api_calls += self.options_agent.get_api_call_count()
        return result

    async def _synthesize_with_crew(
        self,
        symbol: str,
        agent_results: Dict[str, Any],
        user_position: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Use CrewAI to synthesize multi-agent results

        Args:
            symbol: Stock symbol
            agent_results: Results from specialist agents
            user_position: User's current position (optional)

        Returns:
            Dict with synthesized insights
        """
        # Create synthesis agent
        synthesis_agent = Agent(
            role="Lead Investment Analyst",
            goal=f"Synthesize multi-agent analysis into actionable investment recommendation for {symbol}",
            backstory="""You are a senior investment analyst with 20+ years of experience.
            You excel at combining fundamental, technical, sentiment, and options data
            into clear, actionable investment recommendations. You understand risk management
            and always consider the full picture before making recommendations.""",
            llm=self.llm,
            verbose=False
        )

        # Build context from agent results
        context = self._build_synthesis_context(symbol, agent_results, user_position)

        # Create synthesis task
        synthesis_task = Task(
            description=f"""Analyze the comprehensive research data for {symbol} and provide:

1. Overall Rating (1.0-5.0 stars)
2. Quick Summary (2-3 sentences)
3. Trade Recommendation with specific action (STRONG_BUY, BUY, HOLD, SELL, STRONG_SELL)
4. Confidence level (0.0-1.0)
5. Detailed reasoning
6. Time-sensitive factors to consider
7. Specific position advice for wheel strategy traders

Context:
{context}

Provide output in JSON format with keys:
- overall_rating
- quick_summary
- recommendation (object with action, confidence, reasoning, time_sensitive_factors, specific_position_advice, suggested_adjustments)
""",
            agent=synthesis_agent,
            expected_output="JSON object with synthesis results"
        )

        # Create crew and execute
        crew = Crew(
            agents=[synthesis_agent],
            tasks=[synthesis_task],
            process=Process.sequential,
            verbose=False
        )

        # Run synthesis
        try:
            result = crew.kickoff()

            # Parse result (CrewAI returns string, parse as JSON)
            import json
            import re

            # Extract JSON from response
            result_str = str(result)
            json_match = re.search(r'\{.*\}', result_str, re.DOTALL)

            if json_match:
                synthesis_data = json.loads(json_match.group())
            else:
                # Fallback if no JSON found
                synthesis_data = self._create_fallback_synthesis(symbol, agent_results)

            # Convert recommendation dict to TradeRecommendation object
            rec_data = synthesis_data.get('recommendation', {})
            synthesis_data['recommendation'] = TradeRecommendation(
                action=TradeAction(rec_data.get('action', 'HOLD')),
                confidence=rec_data.get('confidence', 0.5),
                reasoning=rec_data.get('reasoning', 'Insufficient data for strong recommendation'),
                time_sensitive_factors=rec_data.get('time_sensitive_factors', []),
                specific_position_advice=rec_data.get('specific_position_advice', {}),
                suggested_adjustments=rec_data.get('suggested_adjustments', [])
            )

            synthesis_data['tokens_used'] = 0  # TODO: Track actual token usage
            return synthesis_data

        except Exception as e:
            logger.error(f"Synthesis failed: {str(e)}")
            return self._create_fallback_synthesis(symbol, agent_results)

    def _build_synthesis_context(
        self,
        symbol: str,
        agent_results: Dict[str, Any],
        user_position: Optional[Any]
    ) -> str:
        """Build context string for synthesis"""
        lines = [f"Symbol: {symbol}\n"]

        if 'fundamental' in agent_results:
            fund = agent_results['fundamental']
            lines.append(f"Fundamental Score: {fund.score}/100")
            lines.append(f"Valuation: {fund.valuation_assessment}")
            lines.append(f"Revenue Growth: {fund.revenue_growth_yoy:.1%}")
            lines.append(f"P/E Ratio: {fund.pe_ratio:.2f} (sector avg: {fund.sector_avg_pe:.2f})")

        if 'technical' in agent_results:
            tech = agent_results['technical']
            lines.append(f"\nTechnical Score: {tech.score}/100")
            lines.append(f"Trend: {tech.trend.value}")
            lines.append(f"RSI: {tech.rsi:.1f}")
            lines.append(f"MACD Signal: {tech.macd_signal.value}")

        if 'sentiment' in agent_results:
            sent = agent_results['sentiment']
            lines.append(f"\nSentiment Score: {sent.score}/100")
            lines.append(f"News Sentiment: {sent.news_sentiment.value}")
            lines.append(f"Institutional Flow: {sent.institutional_flow.value}")
            lines.append(f"Analyst Rating: {sent.analyst_rating.value}")

        if 'options' in agent_results:
            opts = agent_results['options']
            lines.append(f"\nIV Rank: {opts.iv_rank}/100")
            lines.append(f"Days to Earnings: {opts.days_to_earnings}")
            lines.append(f"Put/Call Ratio: {opts.put_call_ratio:.2f}")

        if user_position:
            lines.append(f"\nUser Position: {user_position.position_type} @ ${user_position.entry_price}")

        return "\n".join(lines)

    def _create_fallback_synthesis(self, symbol: str, agent_results: Dict[str, Any]) -> Dict[str, Any]:
        """Create fallback synthesis when LLM fails"""
        # Calculate average score
        scores = []
        if 'fundamental' in agent_results:
            scores.append(agent_results['fundamental'].score)
        if 'technical' in agent_results:
            scores.append(agent_results['technical'].score)
        if 'sentiment' in agent_results:
            scores.append(agent_results['sentiment'].score)

        avg_score = sum(scores) / len(scores) if scores else 50

        # Map score to rating (1-5 stars)
        rating = 1.0 + (avg_score / 100.0) * 4.0

        # Map score to action
        if avg_score >= 75:
            action = TradeAction.STRONG_BUY
        elif avg_score >= 60:
            action = TradeAction.BUY
        elif avg_score >= 40:
            action = TradeAction.HOLD
        elif avg_score >= 25:
            action = TradeAction.SELL
        else:
            action = TradeAction.STRONG_SELL

        return {
            'overall_rating': rating,
            'quick_summary': f"{symbol} analysis complete. Overall score: {avg_score:.0f}/100",
            'recommendation': TradeRecommendation(
                action=action,
                confidence=0.5,
                reasoning="Automated fallback recommendation based on aggregate scores",
                time_sensitive_factors=[],
                specific_position_advice={},
                suggested_adjustments=[]
            ),
            'tokens_used': 0
        }

    # Fallback data for failed agents
    def _get_fallback_fundamental(self) -> FundamentalAnalysis:
        """Return fallback fundamental analysis"""
        from src.agents.ai_research.models import FundamentalAnalysis
        return FundamentalAnalysis(
            score=50,
            revenue_growth_yoy=0.0,
            earnings_beat_streak=0,
            pe_ratio=0.0,
            sector_avg_pe=0.0,
            pb_ratio=0.0,
            debt_to_equity=0.0,
            roe=0.0,
            free_cash_flow=0.0,
            dividend_yield=0.0,
            valuation_assessment="Data unavailable",
            key_strengths=["Data unavailable"],
            key_risks=["Data unavailable"]
        )

    def _get_fallback_technical(self) -> TechnicalAnalysis:
        """Return fallback technical analysis"""
        from src.agents.ai_research.models import TechnicalAnalysis, TrendDirection, SignalType
        return TechnicalAnalysis(
            score=50,
            trend=TrendDirection.SIDEWAYS,
            rsi=50.0,
            macd_signal=SignalType.NEUTRAL,
            support_levels=[],
            resistance_levels=[],
            moving_averages={},
            bollinger_bands={},
            volume_analysis="Data unavailable",
            chart_patterns=[],
            recommendation="Data unavailable"
        )

    def _get_fallback_sentiment(self) -> SentimentAnalysis:
        """Return fallback sentiment analysis"""
        from src.agents.ai_research.models import (
            SentimentAnalysis, SentimentType, InstitutionalFlow,
            AnalystRating, AnalystConsensus
        )
        return SentimentAnalysis(
            score=50,
            news_sentiment=SentimentType.NEUTRAL,
            news_count_7d=0,
            social_sentiment=SentimentType.NEUTRAL,
            reddit_mentions_24h=0,
            stocktwits_sentiment=0.0,
            institutional_flow=InstitutionalFlow.NEUTRAL,
            insider_trades=[],
            analyst_rating=AnalystRating.HOLD,
            analyst_consensus=AnalystConsensus(
                strong_buy=0, buy=0, hold=0, sell=0, strong_sell=0
            )
        )

    def _get_fallback_options(self) -> OptionsAnalysis:
        """Return fallback options analysis"""
        from src.agents.ai_research.models import OptionsAnalysis
        return OptionsAnalysis(
            iv_rank=50,
            iv_percentile=50,
            current_iv=0.0,
            iv_mean_30d=0.0,
            iv_std_30d=0.0,
            next_earnings_date="Unknown",
            days_to_earnings=999,
            avg_earnings_move=0.0,
            put_call_ratio=1.0,
            max_pain=0.0,
            unusual_options_activity=[],
            recommended_strategies=[]
        )
