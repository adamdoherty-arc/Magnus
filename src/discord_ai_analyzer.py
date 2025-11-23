"""
Discord AI Signal Analyzer
Uses local LLM (Qwen 32B via Ollama) for intelligent signal analysis
Falls back to rule-based analysis if local LLM unavailable
"""

import logging
import re
from typing import List, Dict, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

# Try to import local LLM
try:
    from src.magnus_local_llm import get_magnus_llm, TaskComplexity
    LOCAL_LLM_AVAILABLE = True
    logger.info("✓ Local LLM available for Discord signal analysis")
except ImportError:
    LOCAL_LLM_AVAILABLE = False
    logger.warning("Local LLM not available, using rule-based fallback")


class DiscordAIAnalyzer:
    """
    Intelligent Discord trading signal analyzer

    Features:
    - Local LLM analysis (Qwen 32B)
    - Ticker extraction and classification
    - Sentiment analysis
    - Trading setup identification
    - Risk assessment
    - Confidence scoring
    """

    def __init__(self, use_local_llm: bool = True):
        """
        Initialize Discord AI Analyzer

        Args:
            use_local_llm: Try to use local LLM if available
        """
        self.use_local_llm = use_local_llm and LOCAL_LLM_AVAILABLE
        self.llm = None

        if self.use_local_llm:
            try:
                self.llm = get_magnus_llm()
                logger.info("✓ Initialized local LLM for Discord analysis")
            except Exception as e:
                logger.warning(f"Failed to initialize local LLM: {e}")
                self.use_local_llm = False

        # Trading keywords for rule-based analysis
        self.bullish_keywords = [
            'buy', 'long', 'call', 'bullish', 'breakout', 'support', 'upside',
            'pump', 'moon', 'rocket', 'squeeze', 'rally', 'bull run'
        ]

        self.bearish_keywords = [
            'sell', 'short', 'put', 'bearish', 'breakdown', 'resistance', 'downside',
            'dump', 'crash', 'collapse', 'bear', 'decline', 'drop'
        ]

        self.high_confidence_keywords = [
            'strong', 'high confidence', 'lock', 'certain', 'guaranteed',
            'max confidence', 'best setup', 'perfect', 'ideal'
        ]

    def analyze_signal(self, message: Dict) -> Dict:
        """
        Analyze a Discord trading signal

        Args:
            message: Discord message with content, author, timestamp, etc.

        Returns:
            Analysis dict with:
            - tickers: List of tickers mentioned
            - sentiment: bullish/bearish/neutral
            - confidence: 0-100 score
            - setup: Trading setup description
            - risk_level: low/medium/high
            - analysis: AI-generated analysis
            - method: 'local_llm' or 'rule_based'
        """
        content = message.get('content', '')

        # Extract tickers
        tickers = self._extract_tickers(content)

        # Choose analysis method
        if self.use_local_llm and self.llm and len(content) > 50:
            return self._analyze_with_llm(message, tickers)
        else:
            return self._analyze_rule_based(message, tickers)

    def _extract_tickers(self, content: str) -> List[str]:
        """Extract stock tickers from message content"""
        tickers = []

        # Pattern 1: $SYMBOL format
        dollar_tickers = re.findall(r'\$([A-Z]{1,5})\b', content.upper())
        tickers.extend(dollar_tickers)

        # Pattern 2: Standalone capitalized 2-5 letter words (be conservative)
        word_tickers = re.findall(r'\b([A-Z]{2,5})\b', content.upper())
        # Filter out common words
        common_words = {'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'CAN', 'HER', 'WAS', 'ONE', 'OUR', 'OUT', 'DAY', 'GET', 'HAS', 'HIM', 'HIS', 'HOW', 'MAN', 'NEW', 'NOW', 'OLD', 'SEE', 'TWO', 'WAY', 'WHO', 'BOY', 'ITS', 'LET', 'PUT', 'SAY', 'SHE', 'TOO', 'USE'}
        word_tickers = [t for t in word_tickers if t not in common_words and t not in tickers]
        tickers.extend(word_tickers[:2])  # Max 2 from this method

        # Return unique tickers (max 5)
        return list(dict.fromkeys(tickers))[:5]

    def _analyze_with_llm(self, message: Dict, tickers: List[str]) -> Dict:
        """Analyze signal using local LLM (Qwen 32B)"""
        content = message.get('content', '')
        author = message.get('author_name', 'Unknown')
        channel = message.get('channel_name', 'Unknown')

        # Build analysis prompt
        prompt = f"""Analyze this Discord trading signal:

**Channel:** {channel}
**Author:** {author}
**Message:** {content}

Provide a comprehensive analysis in JSON format:

1. **Sentiment**: bullish, bearish, or neutral
2. **Confidence**: 0-100 score (how confident is this signal?)
3. **Trading Setup**: Describe the trading strategy (CSP, covered call, spread, swing trade, etc.)
4. **Key Levels**: Important price levels mentioned (entry, target, stop loss)
5. **Risk Assessment**: low, medium, or high risk
6. **Tickers**: Stock symbols mentioned
7. **Time Horizon**: short-term (< 1 week), medium-term (1-4 weeks), long-term (> 1 month)
8. **Summary**: 1-2 sentence summary of the signal

Respond ONLY with valid JSON. No markdown, no explanations."""

        try:
            # Query local LLM
            response = self.llm.query(
                prompt=prompt,
                complexity=TaskComplexity.BALANCED,  # Qwen 32B
                use_trading_context=True,
                max_tokens=500
            )

            # Parse LLM response
            import json
            # Clean response (remove markdown code blocks if present)
            response = response.strip()
            if response.startswith('```'):
                response = '\n'.join(response.split('\n')[1:-1])
            if response.startswith('json'):
                response = '\n'.join(response.split('\n')[1:])

            analysis_data = json.loads(response)

            return {
                'tickers': tickers or analysis_data.get('tickers', []),
                'sentiment': analysis_data.get('sentiment', 'neutral').lower(),
                'confidence': min(100, max(0, analysis_data.get('confidence', 50))),
                'setup': analysis_data.get('trading_setup', analysis_data.get('setup', 'Unknown')),
                'risk_level': analysis_data.get('risk_assessment', analysis_data.get('risk_level', 'medium')).lower(),
                'key_levels': analysis_data.get('key_levels', {}),
                'time_horizon': analysis_data.get('time_horizon', 'medium-term'),
                'analysis': analysis_data.get('summary', content[:200]),
                'method': 'local_llm',
                'model': 'qwen2.5:32b'
            }

        except Exception as e:
            logger.error(f"LLM analysis failed: {e}, falling back to rule-based")
            return self._analyze_rule_based(message, tickers)

    def _analyze_rule_based(self, message: Dict, tickers: List[str]) -> Dict:
        """Fallback rule-based analysis"""
        content = message.get('content', '').lower()

        # Sentiment analysis
        bullish_count = sum(1 for kw in self.bullish_keywords if kw in content)
        bearish_count = sum(1 for kw in self.bearish_keywords if kw in content)

        if bullish_count > bearish_count:
            sentiment = 'bullish'
        elif bearish_count > bullish_count:
            sentiment = 'bearish'
        else:
            sentiment = 'neutral'

        # Confidence scoring
        confidence = 50  # Base confidence

        if tickers:
            confidence += 20

        if any(kw in content for kw in self.high_confidence_keywords):
            confidence += 20

        # Price targets mentioned
        prices = re.findall(r'\$\d+\.?\d*', content)
        if len(prices) >= 2:
            confidence += 10

        # Options keywords
        if any(kw in content for kw in ['strike', 'expiry', 'expiration', 'dte']):
            confidence += 10

        confidence = min(100, confidence)

        # Detect setup type
        setup = 'Unknown'
        if 'csp' in content or 'cash-secured put' in content or 'cash secured put' in content:
            setup = 'Cash-Secured Put'
        elif 'covered call' in content or 'cc' in content:
            setup = 'Covered Call'
        elif 'spread' in content:
            setup = 'Options Spread'
        elif 'swing' in content:
            setup = 'Swing Trade'
        elif 'call' in content and ('buy' in content or 'long' in content):
            setup = 'Long Call'
        elif 'put' in content and ('buy' in content or 'long' in content):
            setup = 'Long Put'

        # Risk assessment
        if confidence >= 75:
            risk_level = 'low'
        elif confidence >= 50:
            risk_level = 'medium'
        else:
            risk_level = 'high'

        return {
            'tickers': tickers,
            'sentiment': sentiment,
            'confidence': confidence,
            'setup': setup,
            'risk_level': risk_level,
            'analysis': f"{sentiment.title()} signal for {', '.join(tickers) if tickers else 'multiple tickers'}. Setup: {setup}.",
            'method': 'rule_based'
        }

    def batch_analyze(self, messages: List[Dict], max_analyze: int = 100) -> List[Dict]:
        """
        Batch analyze multiple messages

        Args:
            messages: List of Discord messages
            max_analyze: Maximum messages to analyze

        Returns:
            List of analyzed signals with scores
        """
        results = []

        for i, msg in enumerate(messages[:max_analyze]):
            try:
                analysis = self.analyze_signal(msg)
                results.append({
                    **msg,
                    **analysis
                })
            except Exception as e:
                logger.error(f"Error analyzing message {i}: {e}")
                continue

        # Sort by confidence score
        results.sort(key=lambda x: x.get('confidence', 0), reverse=True)

        return results

    def get_top_signals(
        self,
        messages: List[Dict],
        min_confidence: int = 60,
        limit: int = 10
    ) -> List[Dict]:
        """
        Get top trading signals from messages

        Args:
            messages: List of Discord messages
            min_confidence: Minimum confidence score
            limit: Maximum signals to return

        Returns:
            Top signals sorted by confidence
        """
        analyzed = self.batch_analyze(messages)

        # Filter by confidence
        filtered = [s for s in analyzed if s.get('confidence', 0) >= min_confidence]

        return filtered[:limit]


# Singleton instance
_analyzer_instance: Optional[DiscordAIAnalyzer] = None


def get_discord_analyzer() -> DiscordAIAnalyzer:
    """Get singleton instance of Discord AI Analyzer"""
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = DiscordAIAnalyzer()
        logger.info("Initialized Discord AI Analyzer")
    return _analyzer_instance


if __name__ == "__main__":
    # Test the analyzer
    print("Discord AI Signal Analyzer")
    print("=" * 60)

    analyzer = get_discord_analyzer()

    # Test message
    test_msg = {
        'content': '$NVDA looks strong here. Looking to sell CSP at $480 strike, 30 DTE. High confidence setup with support at $475.',
        'author_name': 'TestTrader',
        'channel_name': 'options-alerts',
        'timestamp': datetime.now()
    }

    print("\nTest Message:")
    print(test_msg['content'])
    print("\nAnalysis:")

    result = analyzer.analyze_signal(test_msg)

    for key, value in result.items():
        print(f"  {key}: {value}")

    print(f"\nUsing: {result['method']}")
    if result['method'] == 'local_llm':
        print(f"Model: {result.get('model', 'unknown')}")
