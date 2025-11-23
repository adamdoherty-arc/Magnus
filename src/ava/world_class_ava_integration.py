"""
World-Class AVA Integration
============================

Integrates all premium features to make AVA the best financial advisor:
- World-class prompts with Chain-of-Thought reasoning
- Unified market data from 3 FREE sources
- AI-powered sentiment analysis
- Economic context and macro indicators
- Comprehensive stock analysis

This module provides easy integration with existing AVA code.

Author: Magnus Trading Platform
Created: 2025-11-21
"""

import logging
from typing import Dict, Optional, Any, List
from datetime import datetime
import os
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import new components
try:
    from src.ava.prompts.master_financial_advisor_prompt import FinancialAdvisorPrompt
    from src.services.unified_market_data import UnifiedMarketData, get_market_data
except ImportError as e:
    logging.warning(f"Could not import new AVA components: {e}")
    FinancialAdvisorPrompt = None
    UnifiedMarketData = None

logger = logging.getLogger(__name__)


class WorldClassAVA:
    """
    Enhanced AVA with world-class financial advisory capabilities.

    Use this class to upgrade any existing AVA implementation.
    """

    def __init__(
        self,
        alpha_vantage_key: Optional[str] = None,
        fred_key: Optional[str] = None,
        finnhub_key: Optional[str] = None
    ):
        """
        Initialize World-Class AVA.

        Args:
            alpha_vantage_key: Alpha Vantage API key (or uses env var)
            fred_key: FRED API key (or uses env var)
            finnhub_key: Finnhub API key (or uses env var)
        """
        # Initialize unified market data
        if UnifiedMarketData:
            self.market_data = UnifiedMarketData(
                alpha_vantage_key=alpha_vantage_key,
                fred_key=fred_key,
                finnhub_key=finnhub_key
            )
            logger.info("✅ World-Class AVA initialized with premium features")
        else:
            self.market_data = None
            logger.warning("⚠️ Market data unavailable - install required packages")

        # Track usage
        self.queries_processed = 0

    # ========================================================================
    # ENHANCED PROMPT GENERATION
    # ========================================================================

    def generate_world_class_prompt(
        self,
        user_query: str,
        user_profile: Optional[Dict] = None,
        portfolio_context: Optional[Dict] = None,
        rag_context: Optional[str] = None,
        conversation_history: Optional[str] = None,
        personality_mode: str = "professional"
    ) -> str:
        """
        Generate world-class financial advisor prompt.

        Args:
            user_query: User's question
            user_profile: User preferences and profile
            portfolio_context: Current portfolio state
            rag_context: Retrieved knowledge base context
            conversation_history: Previous conversation
            personality_mode: AVA's personality mode

        Returns:
            Complete prompt for LLM
        """
        if not FinancialAdvisorPrompt:
            logger.warning("Master prompt not available, using basic prompt")
            return f"You are AVA, a financial assistant. Answer: {user_query}"

        # Get real-time market context
        market_context = self._get_market_context()

        # Use default user profile if not provided
        if not user_profile:
            user_profile = self._get_default_user_profile()

        # Use default portfolio context if not provided
        if not portfolio_context:
            portfolio_context = self._get_default_portfolio_context()

        # Generate master prompt
        prompt = FinancialAdvisorPrompt.get_master_prompt(
            user_profile=user_profile,
            portfolio_context=portfolio_context,
            market_context=market_context,
            user_query=user_query,
            rag_context=rag_context,
            conversation_history=conversation_history,
            personality_mode=personality_mode
        )

        self.queries_processed += 1
        logger.info(f"✅ Generated world-class prompt #{self.queries_processed}")

        return prompt

    # ========================================================================
    # MARKET CONTEXT
    # ========================================================================

    def _get_market_context(self) -> Dict[str, Any]:
        """Get real-time market context"""
        if not self.market_data:
            return self._get_default_market_context()

        try:
            # Get comprehensive market context
            context = self.market_data.get_market_context_for_ava()

            # Extract key metrics
            return {
                'sp500_trend': 'neutral',  # TODO: Add trend detection
                'vix': context.get('vix_level', 20),
                'fed_rate': context.get('fed_funds_rate', 5.25),
                'recent_headlines': [],  # TODO: Add top market headlines
                'market_regime': context.get('market_regime', 'Transitional'),
                'recession_risk': context.get('recession_risk', 'Unknown'),
                'volatility_regime': context.get('volatility_regime', 'Moderate'),
                'policy_stance': context.get('policy_stance', 'Neutral')
            }

        except Exception as e:
            logger.warning(f"Failed to get live market context: {e}")
            return self._get_default_market_context()

    def _get_default_market_context(self) -> Dict:
        """Fallback market context"""
        return {
            'sp500_trend': 'neutral',
            'vix': 18,
            'fed_rate': 5.25,
            'recent_headlines': ['Market data temporarily unavailable'],
            'market_regime': 'Transitional',
            'recession_risk': 'Unknown',
            'volatility_regime': 'Moderate',
            'policy_stance': 'Neutral'
        }

    def _get_default_user_profile(self) -> Dict:
        """Default user profile"""
        return {
            'risk_tolerance': 'moderate',
            'experience_level': 'intermediate',
            'goals': ['income generation', 'capital preservation'],
            'favorite_tickers': [],
            'preferred_strategy': 'wheel strategy',
            'max_position_size': 10000
        }

    def _get_default_portfolio_context(self) -> Dict:
        """Default portfolio context"""
        return {
            'total_value': 0,
            'cash': 0,
            'num_positions': 0,
            'net_delta': 0,
            'ytd_return': 0,
            'sectors': {},
            'top_positions': []
        }

    # ========================================================================
    # STOCK ANALYSIS
    # ========================================================================

    def analyze_stock(self, symbol: str) -> Optional[Dict]:
        """
        Get comprehensive stock analysis.

        Args:
            symbol: Stock ticker

        Returns:
            Complete analysis including fundamentals, news, sentiment, etc.
        """
        if not self.market_data:
            logger.error("Market data not available")
            return None

        try:
            analysis = self.market_data.get_comprehensive_stock_analysis(symbol)
            logger.info(f"✅ Complete analysis for {symbol}")
            return analysis

        except Exception as e:
            logger.error(f"Stock analysis failed: {e}")
            return None

    def get_stock_sentiment(self, symbol: str) -> Optional[Dict]:
        """Get AI-powered sentiment for a stock"""
        if not self.market_data:
            return None

        try:
            result = self.market_data.get_news_and_sentiment(symbol, days_back=7)
            return result.get('sentiment') if result else None

        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return None

    def get_stock_quote(self, symbol: str) -> Optional[Dict]:
        """Get real-time quote"""
        if not self.market_data:
            return None

        try:
            return self.market_data.get_quote(symbol)
        except Exception as e:
            logger.error(f"Quote failed: {e}")
            return None

    # ========================================================================
    # ECONOMIC DATA
    # ========================================================================

    def get_economic_snapshot(self) -> Optional[Dict]:
        """Get current economic indicators"""
        if not self.market_data:
            return None

        try:
            return self.market_data.get_economic_dashboard()
        except Exception as e:
            logger.error(f"Economic snapshot failed: {e}")
            return None

    def get_recession_risk(self) -> Optional[str]:
        """Get current recession risk assessment"""
        if not self.market_data:
            return "Unknown"

        try:
            econ = self.market_data.get_economic_dashboard()
            recession = econ.get('recession_indicators', {})
            return recession.get('recession_risk', 'Unknown')
        except Exception as e:
            logger.error(f"Recession risk check failed: {e}")
            return "Unknown"

    # ========================================================================
    # HELPER METHODS
    # ========================================================================

    def format_stock_analysis_for_display(self, analysis: Dict) -> str:
        """
        Format stock analysis for display in UI.

        Args:
            analysis: Stock analysis dict

        Returns:
            Formatted markdown string
        """
        output = []

        # Header
        symbol = analysis.get('symbol', 'UNKNOWN')
        timestamp = analysis.get('timestamp', '')
        output.append(f"# 📊 Comprehensive Analysis: {symbol}")
        output.append(f"*Generated: {timestamp}*\n")

        # Quote
        if 'quote' in analysis:
            q = analysis['quote']
            change_emoji = "🟢" if q.get('change', 0) >= 0 else "🔴"
            output.append(f"## {change_emoji} Current Quote")
            output.append(f"**Price:** ${q.get('price', 0):.2f}")
            output.append(f"**Change:** {q.get('change', 0):+.2f} ({q.get('change_percent', 0):+.2f}%)")
            output.append(f"**Range:** ${q.get('low', 0):.2f} - ${q.get('high', 0):.2f}\n")

        # Sentiment
        if 'sentiment' in analysis:
            s = analysis['sentiment']
            if s:
                sentiment_emoji = "🐂" if s.get('label') == 'Bullish' else "🐻" if s.get('label') == 'Bearish' else "⚖️"
                output.append(f"## {sentiment_emoji} AI Sentiment Analysis")
                output.append(f"**Overall:** {s.get('label', 'Neutral')} (Score: {s.get('score', 0):.3f})")
                output.append(f"**Confidence:** {s.get('confidence', 'low').title()}")
                output.append(f"**Articles Analyzed:** {s.get('article_count', 0)}\n")

        # Fundamentals
        if 'fundamentals' in analysis:
            f = analysis['fundamentals']
            output.append(f"## 📈 Key Fundamentals")
            output.append(f"**Company:** {f.get('name', 'Unknown')}")
            output.append(f"**Sector:** {f.get('sector', 'Unknown')} | **Industry:** {f.get('industry', 'Unknown')}")
            if f.get('pe_ratio'):
                output.append(f"**P/E Ratio:** {f.get('pe_ratio')}")
            if f.get('market_cap'):
                output.append(f"**Market Cap:** {f.get('market_cap')}")
            if f.get('dividend_yield'):
                output.append(f"**Dividend Yield:** {f.get('dividend_yield')}%\n")

        # Recent news
        if 'news' in analysis and analysis['news']:
            output.append(f"## 📰 Recent News (Top 5)")
            for i, article in enumerate(analysis['news'][:5], 1):
                output.append(f"{i}. **{article.get('headline', 'No headline')}**")
                output.append(f"   *{article.get('source', 'Unknown source')} - {article.get('datetime', '')}*\n")

        # Insider activity
        if 'insider_transactions' in analysis and analysis['insider_transactions']:
            output.append(f"## 👔 Recent Insider Activity")
            output.append(f"Found {len(analysis['insider_transactions'])} transactions in last 3 months\n")

        # Analyst ratings
        if 'analyst_ratings' in analysis:
            ar = analysis['analyst_ratings']
            if ar and ar.get('price_target'):
                pt = ar['price_target']
                output.append(f"## 🎯 Analyst Price Target")
                output.append(f"**Consensus:** ${pt.get('target_mean', 0):.2f}")
                output.append(f"**Range:** ${pt.get('target_low', 0):.2f} - ${pt.get('target_high', 0):.2f}\n")

        return "\n".join(output)

    def get_usage_stats(self) -> Dict:
        """Get usage statistics"""
        stats = {
            'queries_processed': self.queries_processed,
            'world_class_features': 'Active',
            'data_sources': '3 FREE APIs'
        }

        if self.market_data:
            market_stats = self.market_data.get_usage_stats()
            stats.update(market_stats)

        return stats


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

# Global instance
_world_class_ava = None

def get_world_class_ava() -> WorldClassAVA:
    """Get singleton World-Class AVA instance"""
    global _world_class_ava
    if _world_class_ava is None:
        _world_class_ava = WorldClassAVA()
    return _world_class_ava


def generate_prompt(
    user_query: str,
    user_profile: Optional[Dict] = None,
    portfolio_context: Optional[Dict] = None,
    rag_context: Optional[str] = None,
    conversation_history: Optional[str] = None,
    personality_mode: str = "professional"
) -> str:
    """Quick function to generate world-class prompt"""
    return get_world_class_ava().generate_world_class_prompt(
        user_query=user_query,
        user_profile=user_profile,
        portfolio_context=portfolio_context,
        rag_context=rag_context,
        conversation_history=conversation_history,
        personality_mode=personality_mode
    )


def analyze_stock(symbol: str) -> Optional[Dict]:
    """Quick function to analyze a stock"""
    return get_world_class_ava().analyze_stock(symbol)


def get_sentiment(symbol: str) -> Optional[Dict]:
    """Quick function to get sentiment"""
    return get_world_class_ava().get_stock_sentiment(symbol)


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)

    print("\n=== World-Class AVA Integration Test ===\n")

    # Initialize
    ava = WorldClassAVA()

    # Test 1: Generate world-class prompt
    print("1. Generating world-class prompt...")
    prompt = ava.generate_world_class_prompt(
        user_query="Should I sell a cash-secured put on AAPL at $175 strike, 45 DTE?",
        personality_mode="professional"
    )
    print(f"   ✅ Prompt generated ({len(prompt)} characters)")
    print(f"   Preview: {prompt[:200]}...\n")

    # Test 2: Analyze stock
    print("2. Analyzing AAPL...")
    analysis = ava.analyze_stock('AAPL')
    if analysis:
        print(f"   ✅ Analysis complete")
        if 'quote' in analysis:
            print(f"   Price: ${analysis['quote']['price']}")
        if 'sentiment' in analysis:
            print(f"   Sentiment: {analysis['sentiment']['label']}")

    # Test 3: Get economic snapshot
    print("\n3. Getting economic snapshot...")
    econ = ava.get_economic_snapshot()
    if econ:
        print(f"   ✅ Economic data retrieved")
        recession = econ.get('recession_indicators', {})
        print(f"   Recession Risk: {recession.get('recession_risk', 'Unknown')}")

    # Test 4: Usage stats
    print("\n4. Usage statistics...")
    stats = ava.get_usage_stats()
    print(f"   ✅ Total queries: {stats['queries_processed']}")
    print(f"   Total cost: {stats.get('total_cost', '$0.00')} (FREE!)")
