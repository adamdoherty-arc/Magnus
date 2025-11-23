"""
Vision Analyzer - Chart and Image Analysis
==========================================

Multi-modal capabilities for analyzing charts, screenshots, and images
using vision-enabled LLM models.

Features:
- Technical chart pattern recognition
- Earnings report screenshot analysis
- UI/dashboard screenshot understanding
- Stock chart analysis (candlesticks, indicators)
- Support/resistance level detection

Supported Models:
- GPT-4 Vision (OpenAI)
- Claude 3 Opus/Sonnet (Anthropic)
- Gemini Pro Vision (Google)
- LLaVA (Local, open-source)

Author: Magnus Trading Platform
Created: 2025-11-21
"""

import logging
import base64
import os
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from enum import Enum
import json

logger = logging.getLogger(__name__)


# ============================================================================
# Vision Model Configuration
# ============================================================================

class VisionModel(Enum):
    """Available vision models"""
    GPT4_VISION = "gpt-4-vision-preview"
    GPT4O = "gpt-4o"  # GPT-4 Omni (multimodal)
    CLAUDE_OPUS = "claude-3-opus-20240229"
    CLAUDE_SONNET = "claude-3-sonnet-20240229"
    GEMINI_PRO_VISION = "gemini-pro-vision"
    LLAVA = "llava"  # Local open-source


class AnalysisType(Enum):
    """Types of image analysis"""
    TECHNICAL_CHART = "technical_chart"
    EARNINGS_REPORT = "earnings_report"
    PORTFOLIO_SCREENSHOT = "portfolio_screenshot"
    GENERAL_IMAGE = "general_image"
    OPTION_CHAIN = "option_chain"
    NEWS_ARTICLE = "news_article"


# ============================================================================
# Vision Analyzer
# ============================================================================

class VisionAnalyzer:
    """
    Multi-modal vision analyzer for charts and images

    Supports multiple vision models with automatic fallback
    and intelligent routing based on image complexity.
    """

    def __init__(self, default_model: VisionModel = VisionModel.GPT4O):
        """
        Initialize vision analyzer

        Args:
            default_model: Default vision model to use
        """
        self.default_model = default_model
        self.models_available = self._check_available_models()

        logger.info(f"Vision analyzer initialized with {default_model.value}")
        logger.info(f"Available models: {list(self.models_available.keys())}")

    def _check_available_models(self) -> Dict[str, bool]:
        """Check which vision models are available based on API keys"""
        available = {}

        # Check OpenAI
        if os.getenv('OPENAI_API_KEY'):
            available[VisionModel.GPT4_VISION.value] = True
            available[VisionModel.GPT4O.value] = True

        # Check Anthropic
        if os.getenv('ANTHROPIC_API_KEY'):
            available[VisionModel.CLAUDE_OPUS.value] = True
            available[VisionModel.CLAUDE_SONNET.value] = True

        # Check Google
        if os.getenv('GOOGLE_API_KEY'):
            available[VisionModel.GEMINI_PRO_VISION.value] = True

        # LLaVA always available if Ollama is running
        available[VisionModel.LLAVA.value] = True

        return available

    def analyze_image(
        self,
        image_path: Union[str, Path],
        analysis_type: AnalysisType = AnalysisType.GENERAL_IMAGE,
        custom_prompt: Optional[str] = None,
        model: Optional[VisionModel] = None
    ) -> Dict[str, Any]:
        """
        Analyze image with vision model

        Args:
            image_path: Path to image file
            analysis_type: Type of analysis to perform
            custom_prompt: Custom analysis prompt (overrides default)
            model: Vision model to use (default: self.default_model)

        Returns:
            Dict with analysis results
        """
        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        # Select model
        selected_model = model or self.default_model

        # Generate prompt
        prompt = custom_prompt or self._get_analysis_prompt(analysis_type)

        # Encode image
        image_data = self._encode_image(image_path)

        # Perform analysis with selected model
        try:
            if selected_model in [VisionModel.GPT4_VISION, VisionModel.GPT4O]:
                result = self._analyze_with_openai(image_data, prompt, selected_model)
            elif selected_model in [VisionModel.CLAUDE_OPUS, VisionModel.CLAUDE_SONNET]:
                result = self._analyze_with_anthropic(image_data, prompt, selected_model)
            elif selected_model == VisionModel.GEMINI_PRO_VISION:
                result = self._analyze_with_gemini(image_data, prompt)
            elif selected_model == VisionModel.LLAVA:
                result = self._analyze_with_llava(image_data, prompt)
            else:
                raise ValueError(f"Unsupported model: {selected_model}")

            return {
                'status': 'success',
                'analysis': result,
                'model_used': selected_model.value,
                'analysis_type': analysis_type.value,
                'image_path': str(image_path)
            }

        except Exception as e:
            logger.error(f"Vision analysis failed: {e}")

            # Try fallback model
            return self._fallback_analysis(image_data, prompt, analysis_type, image_path)

    def analyze_chart(
        self,
        image_path: Union[str, Path],
        ticker: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Specialized chart analysis

        Args:
            image_path: Path to chart image
            ticker: Stock ticker (optional, for context)

        Returns:
            Dict with technical analysis from chart
        """
        custom_prompt = f"""
Analyze this stock chart{"for " + ticker if ticker else ""} and provide:

1. **Trend Analysis**:
   - Current trend direction (uptrend, downtrend, sideways)
   - Trend strength (weak, moderate, strong)
   - Potential trend reversal signals

2. **Support & Resistance Levels**:
   - Key support levels (price points)
   - Key resistance levels (price points)
   - Breakout or breakdown zones

3. **Technical Indicators** (if visible):
   - Moving averages (position and crossovers)
   - RSI level (overbought/oversold)
   - MACD signals
   - Volume analysis

4. **Chart Patterns**:
   - Identified patterns (head & shoulders, double top/bottom, triangles, flags, etc.)
   - Pattern completion status
   - Target price from pattern

5. **Trading Signals**:
   - Bullish or bearish signals
   - Entry points for long/short
   - Stop loss suggestions
   - Profit target levels

6. **Overall Assessment**:
   - Bullish, bearish, or neutral
   - Confidence level (1-10)
   - Time horizon (short-term, medium-term, long-term)

Provide specific price levels and quantitative analysis where possible.
        """

        result = self.analyze_image(
            image_path=image_path,
            analysis_type=AnalysisType.TECHNICAL_CHART,
            custom_prompt=custom_prompt
        )

        # Parse structured data from analysis
        analysis_text = result.get('analysis', '')
        parsed_data = self._parse_chart_analysis(analysis_text, ticker)

        result['structured_analysis'] = parsed_data

        return result

    def analyze_earnings_report(
        self,
        image_path: Union[str, Path],
        ticker: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze earnings report screenshot

        Args:
            image_path: Path to earnings report image
            ticker: Stock ticker

        Returns:
            Dict with earnings analysis
        """
        custom_prompt = f"""
Analyze this earnings report{"for " + ticker if ticker else ""} and extract:

1. **Key Metrics**:
   - Revenue (actual vs expected)
   - EPS (actual vs expected)
   - Guidance (raised, lowered, maintained)
   - Beat or miss on each metric

2. **Financial Highlights**:
   - Gross margin
   - Operating margin
   - Net income
   - Cash flow
   - Year-over-year growth rates

3. **Business Metrics** (if available):
   - User growth
   - Customer acquisition cost
   - Lifetime value
   - Churn rate
   - Other KPIs

4. **Forward Guidance**:
   - Next quarter expectations
   - Full year guidance
   - Management commentary

5. **Market Reaction**:
   - Analyst rating changes
   - Price target adjustments
   - Sentiment (positive, negative, neutral)

6. **Trading Implications**:
   - Likely stock reaction (up, down, flat)
   - Options IV crush impact
   - Support/resistance levels to watch

Extract specific numbers and percentages where visible.
        """

        return self.analyze_image(
            image_path=image_path,
            analysis_type=AnalysisType.EARNINGS_REPORT,
            custom_prompt=custom_prompt
        )

    def analyze_option_chain(
        self,
        image_path: Union[str, Path],
        ticker: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze option chain screenshot

        Args:
            image_path: Path to option chain image
            ticker: Stock ticker

        Returns:
            Dict with option chain analysis
        """
        custom_prompt = f"""
Analyze this options chain{"for " + ticker if ticker else ""} and identify:

1. **Unusual Activity**:
   - High volume strikes
   - Large open interest
   - Put/call ratio anomalies
   - Unusual bid-ask spreads

2. **Key Strike Prices**:
   - Max pain strike
   - Highest put OI
   - Highest call OI
   - Most liquid strikes

3. **Implied Volatility**:
   - IV levels across strikes
   - IV skew (put vs call)
   - Volatility smile/smirk

4. **Greeks Analysis**:
   - Delta concentration
   - Gamma exposure
   - Theta decay opportunities

5. **Trading Opportunities**:
   - Best strikes for cash-secured puts
   - Covered call candidates
   - Spread opportunities
   - Calendar spread potential

6. **Market Sentiment**:
   - Bullish or bearish bias
   - Expected move (from straddle prices)
   - Support/resistance from options

Extract specific numbers: strikes, premiums, volumes, OI.
        """

        return self.analyze_image(
            image_path=image_path,
            analysis_type=AnalysisType.OPTION_CHAIN,
            custom_prompt=custom_prompt
        )

    # ========================================================================
    # Model-Specific Analysis Methods
    # ========================================================================

    def _analyze_with_openai(
        self,
        image_data: str,
        prompt: str,
        model: VisionModel
    ) -> str:
        """Analyze with OpenAI GPT-4 Vision"""
        try:
            import openai

            client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

            response = client.chat.completions.create(
                model=model.value,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_data}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=2000
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"OpenAI vision analysis failed: {e}")
            raise

    def _analyze_with_anthropic(
        self,
        image_data: str,
        prompt: str,
        model: VisionModel
    ) -> str:
        """Analyze with Anthropic Claude Vision"""
        try:
            import anthropic

            client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

            # Detect image format
            import imghdr
            image_bytes = base64.b64decode(image_data)
            image_format = imghdr.what(None, h=image_bytes) or "jpeg"

            message = client.messages.create(
                model=model.value,
                max_tokens=2000,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": f"image/{image_format}",
                                    "data": image_data
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ]
            )

            return message.content[0].text

        except Exception as e:
            logger.error(f"Anthropic vision analysis failed: {e}")
            raise

    def _analyze_with_gemini(self, image_data: str, prompt: str) -> str:
        """Analyze with Google Gemini Pro Vision"""
        try:
            import google.generativeai as genai

            genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

            model = genai.GenerativeModel('gemini-pro-vision')

            # Decode base64 to bytes
            image_bytes = base64.b64decode(image_data)

            response = model.generate_content([prompt, image_bytes])

            return response.text

        except Exception as e:
            logger.error(f"Gemini vision analysis failed: {e}")
            raise

    def _analyze_with_llava(self, image_data: str, prompt: str) -> str:
        """Analyze with LLaVA (local Ollama)"""
        try:
            import requests

            # Save base64 to temp file for Ollama
            import tempfile
            image_bytes = base64.b64decode(image_data)

            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
                tmp.write(image_bytes)
                tmp_path = tmp.name

            # Ollama API request
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': 'llava',
                    'prompt': prompt,
                    'images': [base64.b64encode(open(tmp_path, 'rb').read()).decode()]
                }
            )

            # Clean up temp file
            os.unlink(tmp_path)

            if response.status_code == 200:
                result = response.json()
                return result.get('response', '')
            else:
                raise Exception(f"Ollama request failed: {response.status_code}")

        except Exception as e:
            logger.error(f"LLaVA vision analysis failed: {e}")
            raise

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _encode_image(self, image_path: Path) -> str:
        """Encode image to base64"""
        with open(image_path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')

    def _get_analysis_prompt(self, analysis_type: AnalysisType) -> str:
        """Get default prompt for analysis type"""
        prompts = {
            AnalysisType.TECHNICAL_CHART: """
            Analyze this stock chart and provide:
            1. Trend direction and strength
            2. Key support and resistance levels
            3. Technical indicators (if visible)
            4. Chart patterns identified
            5. Trading signals (bullish/bearish)
            6. Overall assessment with confidence level
            """,

            AnalysisType.EARNINGS_REPORT: """
            Analyze this earnings report and extract:
            1. Key metrics (revenue, EPS, beat/miss)
            2. Financial highlights and margins
            3. Forward guidance
            4. Year-over-year growth rates
            5. Trading implications
            """,

            AnalysisType.PORTFOLIO_SCREENSHOT: """
            Analyze this portfolio screenshot and provide:
            1. Total portfolio value
            2. Individual positions and sizes
            3. Gains/losses ($ and %)
            4. Asset allocation breakdown
            5. Portfolio risk assessment
            """,

            AnalysisType.OPTION_CHAIN: """
            Analyze this options chain and identify:
            1. Unusual volume or open interest
            2. Key strike prices
            3. IV levels and skew
            4. Trading opportunities
            5. Market sentiment signals
            """,

            AnalysisType.NEWS_ARTICLE: """
            Analyze this news article screenshot and summarize:
            1. Main headline and key points
            2. Companies or stocks mentioned
            3. Market impact (bullish/bearish)
            4. Trading implications
            5. Key dates or events mentioned
            """,

            AnalysisType.GENERAL_IMAGE: """
            Analyze this image in the context of trading and finance.
            Describe what you see and any relevant insights.
            """
        }

        return prompts.get(analysis_type, prompts[AnalysisType.GENERAL_IMAGE])

    def _fallback_analysis(
        self,
        image_data: str,
        prompt: str,
        analysis_type: AnalysisType,
        image_path: Path
    ) -> Dict[str, Any]:
        """Fallback to alternative models if primary fails"""
        fallback_order = [
            VisionModel.GPT4O,
            VisionModel.CLAUDE_SONNET,
            VisionModel.GEMINI_PRO_VISION,
            VisionModel.LLAVA
        ]

        for model in fallback_order:
            if model == self.default_model:
                continue  # Skip the one that just failed

            if self.models_available.get(model.value):
                try:
                    logger.info(f"Trying fallback model: {model.value}")

                    if model in [VisionModel.GPT4_VISION, VisionModel.GPT4O]:
                        result = self._analyze_with_openai(image_data, prompt, model)
                    elif model in [VisionModel.CLAUDE_OPUS, VisionModel.CLAUDE_SONNET]:
                        result = self._analyze_with_anthropic(image_data, prompt, model)
                    elif model == VisionModel.GEMINI_PRO_VISION:
                        result = self._analyze_with_gemini(image_data, prompt)
                    elif model == VisionModel.LLAVA:
                        result = self._analyze_with_llava(image_data, prompt)

                    return {
                        'status': 'success',
                        'analysis': result,
                        'model_used': model.value,
                        'analysis_type': analysis_type.value,
                        'image_path': str(image_path),
                        'fallback': True
                    }

                except Exception as e:
                    logger.error(f"Fallback model {model.value} also failed: {e}")
                    continue

        # All models failed
        return {
            'status': 'error',
            'error': 'All vision models failed',
            'analysis_type': analysis_type.value,
            'image_path': str(image_path)
        }

    def _parse_chart_analysis(self, analysis_text: str, ticker: Optional[str] = None) -> Dict[str, Any]:
        """Parse chart analysis into structured data"""
        # This is a simple implementation - could be enhanced with regex or LLM parsing
        return {
            'ticker': ticker,
            'analysis_text': analysis_text,
            'trend': self._extract_trend(analysis_text),
            'sentiment': self._extract_sentiment(analysis_text),
            'confidence': self._extract_confidence(analysis_text)
        }

    def _extract_trend(self, text: str) -> str:
        """Extract trend from analysis text"""
        text_lower = text.lower()
        if 'uptrend' in text_lower or 'bullish trend' in text_lower:
            return 'uptrend'
        elif 'downtrend' in text_lower or 'bearish trend' in text_lower:
            return 'downtrend'
        else:
            return 'sideways'

    def _extract_sentiment(self, text: str) -> str:
        """Extract sentiment from analysis text"""
        text_lower = text.lower()
        if 'bullish' in text_lower:
            return 'bullish'
        elif 'bearish' in text_lower:
            return 'bearish'
        else:
            return 'neutral'

    def _extract_confidence(self, text: str) -> Optional[int]:
        """Extract confidence level from analysis text"""
        import re
        match = re.search(r'confidence.*?(\d+)', text.lower())
        if match:
            return int(match.group(1))
        return None


# ============================================================================
# Convenience Functions
# ============================================================================

def analyze_chart_image(
    image_path: Union[str, Path],
    ticker: Optional[str] = None
) -> Dict[str, Any]:
    """
    Quick function to analyze a chart image

    Args:
        image_path: Path to chart image
        ticker: Stock ticker (optional)

    Returns:
        Analysis results
    """
    analyzer = VisionAnalyzer()
    return analyzer.analyze_chart(image_path, ticker)


def analyze_earnings_screenshot(
    image_path: Union[str, Path],
    ticker: Optional[str] = None
) -> Dict[str, Any]:
    """
    Quick function to analyze earnings report

    Args:
        image_path: Path to earnings report image
        ticker: Stock ticker (optional)

    Returns:
        Analysis results
    """
    analyzer = VisionAnalyzer()
    return analyzer.analyze_earnings_report(image_path, ticker)


# ============================================================================
# Testing
# ============================================================================

if __name__ == "__main__":
    # Test vision analyzer
    analyzer = VisionAnalyzer()

    print("Available models:")
    print(json.dumps(analyzer.models_available, indent=2))

    # Test with a sample chart (replace with actual path)
    # result = analyzer.analyze_chart("path/to/chart.png", ticker="AAPL")
    # print(json.dumps(result, indent=2))
